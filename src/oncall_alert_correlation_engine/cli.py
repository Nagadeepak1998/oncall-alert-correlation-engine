"""Command line interface for alert correlation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .engine import PAGE_SEVERITIES, correlate_alerts, render_markdown
from .metrics import render_metrics
from .models import Alert, ServiceCatalogEntry


def main() -> int:
    parser = argparse.ArgumentParser(description="Correlate on-call alerts into incidents.")
    subcommands = parser.add_subparsers(dest="command", required=True)
    correlate = subcommands.add_parser("correlate", help="Review alert payloads.")
    correlate.add_argument("alerts", type=Path)
    correlate.add_argument("--catalog", type=Path, required=True)
    correlate.add_argument("--json-out", type=Path)
    correlate.add_argument("--markdown-out", type=Path)
    correlate.add_argument("--metrics-out", type=Path)
    correlate.add_argument("--fail-on-page", action="store_true")
    args = parser.parse_args()

    if args.command == "correlate":
        report = correlate_alerts(_load_alerts(args.alerts), _load_catalog(args.catalog))
        print(report.summary)
        if args.json_out:
            _write(args.json_out, report.model_dump_json(indent=2) + "\n")
        if args.markdown_out:
            _write(args.markdown_out, render_markdown(report))
        if args.metrics_out:
            _write(args.metrics_out, render_metrics(report))
        if args.fail_on_page and any(i.severity in PAGE_SEVERITIES for i in report.incidents):
            return 2
    return 0


def _load_alerts(path: Path) -> list[Alert]:
    payload = json.loads(path.read_text())
    return [Alert.model_validate(item) for item in payload["alerts"]]


def _load_catalog(path: Path) -> dict[str, ServiceCatalogEntry]:
    payload = json.loads(path.read_text())
    return {
        service: ServiceCatalogEntry.model_validate(entry)
        for service, entry in payload["services"].items()
    }


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


if __name__ == "__main__":
    raise SystemExit(main())


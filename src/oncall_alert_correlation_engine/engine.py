"""Deterministic alert correlation logic."""

from __future__ import annotations

from collections import defaultdict
from datetime import timedelta
from hashlib import sha1

from .models import Alert, CorrelationReport, Incident, ServiceCatalogEntry

PAGE_SEVERITIES = {"P1", "P2"}
SEVERITY_RANK = {"info": 0, "warning": 1, "critical": 2}
CORRELATION_WINDOW = timedelta(minutes=15)


def correlate_alerts(
    alerts: list[Alert], catalog: dict[str, ServiceCatalogEntry]
) -> CorrelationReport:
    ordered = sorted(alerts, key=lambda alert: (alert.started_at, alert.id))
    grouped: dict[tuple[str, str], list[Alert]] = defaultdict(list)
    for alert in ordered:
        grouped[(alert.service, alert.fingerprint or alert.signal.lower().strip())].append(alert)

    incidents: list[Incident] = []
    suppressed: set[str] = set()

    for (service, fingerprint), group in grouped.items():
        window: list[Alert] = []
        for alert in group:
            if window and alert.started_at - window[0].started_at > CORRELATION_WINDOW:
                incidents.extend(_incident_for_window(service, fingerprint, window, catalog))
                suppressed.update(alert_id for alert_id in _suppressed_ids(window))
                window = []
            window.append(alert)
        if window:
            incidents.extend(_incident_for_window(service, fingerprint, window, catalog))
            suppressed.update(alert_id for alert_id in _suppressed_ids(window))

    incidents.sort(key=lambda incident: (incident.window_start, incident.service, incident.key))
    page_count = sum(1 for incident in incidents if incident.severity in PAGE_SEVERITIES)
    return CorrelationReport(
        reviewed_alerts=len(alerts),
        incident_count=len(incidents),
        page_worthy_incidents=page_count,
        incidents=incidents,
        suppressed_alert_ids=sorted(suppressed),
        summary=(
            f"Reviewed {len(alerts)} alerts, correlated {len(incidents)} incidents, "
            f"and found {page_count} page-worthy incidents."
        ),
    )


def _incident_for_window(
    service: str,
    fingerprint: str,
    alerts: list[Alert],
    catalog: dict[str, ServiceCatalogEntry],
) -> list[Incident]:
    if not alerts:
        return []
    max_rank = max(SEVERITY_RANK[alert.severity] for alert in alerts)
    if max_rank == 0 and len(alerts) < 3:
        return []

    entry = catalog.get(service, ServiceCatalogEntry())
    missing = []
    if not entry.owner:
        missing.append("owner")
    if not entry.escalation_policy:
        missing.append("escalation_policy")
    if any(not alert.runbook_url for alert in alerts):
        missing.append("runbook_url")

    severity = _incident_severity(alerts, missing)
    key_hash = sha1(f"{service}:{fingerprint}:{alerts[0].started_at.isoformat()}".encode()).hexdigest()[:10]
    signals = sorted({alert.signal for alert in alerts})
    action = _recommended_action(service, severity, signals, entry)
    return [
        Incident(
            key=f"inc-{key_hash}",
            service=service,
            severity=severity,
            alert_count=len(alerts),
            window_start=alerts[0].started_at,
            window_end=alerts[-1].started_at,
            owner=entry.owner,
            escalation_policy=entry.escalation_policy,
            signals=signals,
            contributing_alert_ids=[alert.id for alert in alerts],
            recommended_action=action,
            missing_readiness=sorted(set(missing)),
        )
    ]


def _incident_severity(alerts: list[Alert], missing: list[str]) -> str:
    critical_count = sum(1 for alert in alerts if alert.severity == "critical")
    warning_count = sum(1 for alert in alerts if alert.severity == "warning")
    if critical_count >= 2 or (critical_count >= 1 and "escalation_policy" in missing):
        return "P1"
    if critical_count == 1 or warning_count >= 3:
        return "P2"
    if warning_count >= 1:
        return "P3"
    return "P4"


def _recommended_action(
    service: str, severity: str, signals: list[str], entry: ServiceCatalogEntry
) -> str:
    owner = entry.owner or "the owning team"
    signal_text = ", ".join(signals)
    if severity in PAGE_SEVERITIES:
        return (
            f"Page {owner} for {service}; correlate {signal_text}; verify dependencies "
            f"{', '.join(entry.dependencies) or 'none listed'} before mitigation."
        )
    return f"Open a ticket for {owner} to review {service} signals: {signal_text}."


def _suppressed_ids(alerts: list[Alert]) -> list[str]:
    return [alert.id for alert in alerts[1:]]


def render_markdown(report: CorrelationReport) -> str:
    lines = [
        "# On-Call Alert Correlation Report",
        "",
        report.summary,
        "",
        "| Incident | Service | Severity | Alerts | Owner | Missing readiness |",
        "| --- | --- | --- | ---: | --- | --- |",
    ]
    for incident in report.incidents:
        missing = ", ".join(incident.missing_readiness) or "none"
        owner = incident.owner or "unassigned"
        lines.append(
            f"| {incident.key} | {incident.service} | {incident.severity} | "
            f"{incident.alert_count} | {owner} | {missing} |"
        )
    lines.extend(["", "## Recommended Actions", ""])
    for incident in report.incidents:
        lines.append(f"- **{incident.key}**: {incident.recommended_action}")
    return "\n".join(lines) + "\n"


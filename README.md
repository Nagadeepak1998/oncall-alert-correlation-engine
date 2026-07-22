# On-call Alert Correlation Engine

Deterministic SRE project that turns noisy monitoring alerts into incident-ready evidence. It groups duplicate pages, checks service catalog readiness, emits Prometheus metrics, and exposes the same logic through a CLI and FastAPI service.

## Architecture

```text
examples/noisy_alerts.json       examples/service_catalog.json
          |                                  |
          +---------------+------------------+
                          |
                Correlation Engine
                          |
       +------------------+------------------+
       |                  |                  |
Markdown/JSON report   Prometheus metrics   FastAPI /correlate
```

The engine groups alerts by service and fingerprint inside a 15-minute window. It promotes correlated windows to P1/P2/P3/P4 incidents based on severity mix and missing readiness metadata. Duplicate alerts inside the same incident are captured as suppressed alert IDs so an on-call engineer sees one incident instead of several disconnected pages.

## What It Demonstrates

- SRE alert correlation and paging-readiness review.
- Service catalog ownership checks for owner, escalation policy, and runbook metadata.
- CI-friendly exit codes for page-worthy incidents.
- Prometheus exposition from the latest API correlation run.
- Docker, Kubernetes, and Terraform-shaped assets that can be validated locally.

## Setup

```bash
make install
```

The Makefile defaults to `python3.13` because macOS `python3` may be older than the project requirement. Override with `SYSTEM_PYTHON=/path/to/python make install` if needed.

## Run

Generate reports from the noisy example:

```bash
make report
```

Run the smoke gate. The included noisy example intentionally returns exit code `2` because it contains a page-worthy checkout incident:

```bash
make smoke
```

Run the API:

```bash
make api
```

Then post alerts and services to `POST /correlate`. After a request, `/metrics` exposes the latest reviewed alert and incident counts in Prometheus format.

## Verification

```bash
make lint
make test
make report
make smoke
make k8s-validate
make terraform-fmt
```

Optional when Docker is available:

```bash
make docker-build
```

## Example Output

The sample noisy payload reviews five alerts and produces:

- One P1 `checkout-api` incident from three correlated alerts.
- One P3 `search-api` incident with missing escalation readiness.
- Three suppressed duplicate alerts across the grouped incidents.

Reports are written to:

- `reports/latest/correlation_report.json`
- `reports/latest/correlation_report.md`
- `reports/latest/metrics.prom`

## Repository Layout

```text
src/oncall_alert_correlation_engine/  CLI, API, engine, models, metrics
examples/                            Synthetic alert and service catalog fixtures
tests/                               Engine, CLI, API, and metrics tests
infra/docker/                        Local container image definition
infra/k8s/                           Kustomize-compatible deployment and service
infra/terraform/                     Local metadata example, no cloud provider
docs/CASE_STUDY.md                   Design note and operational rationale
docs/github-actions/ci.yml           CI example stored outside root workflow path
```

## Limitations

- The fixtures are synthetic and contain no employer or production data.
- The correlation algorithm is rule-based, not a trained model.
- Kubernetes and Terraform assets are local validation examples, not proof of cloud deployment.
- No root `.github/workflows` file is included because GitHub auth currently lacks `workflow` scope. To publish workflows, run:

```bash
gh auth refresh -h github.com -s workflow
```


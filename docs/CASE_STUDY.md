# Case Study: On-Call Alert Correlation Engine

## Scenario

An on-call rotation receives several alerts during a checkout degradation: 5xx rate, payment authorization failures, and latency. A separate search latency issue arrives in the same review window. A weak process pages multiple people, loses the root signal, and leaves missing readiness until the incident is already hot.

This project models the review I would want before routing those alerts to responders. It correlates alerts into incident candidates, keeps deterministic output for CI/reviewer artifacts, and flags readiness gaps such as missing owners, escalation policies, and runbooks.

## Architecture

- `engine.py` owns deterministic grouping, severity scoring, suppression, and readiness findings.
- `cli.py` turns saved alert payloads into JSON, Markdown, and Prometheus-style metrics artifacts.
- `api.py` exposes the same review through `POST /correlate`, `GET /health`, and `GET /metrics`.
- `examples/` contains safe and noisy fixtures for repeatable demos.
- `infra/k8s/` and `infra/terraform/` show deploy-shaped assets without requiring cloud credentials.

## Operational Behavior

The noisy fixture produces one P1 checkout incident because two critical alerts share a correlation window and fingerprint. The search alerts become a lower-severity readiness finding because the service has an owner but lacks complete escalation/runbook metadata. The engine suppresses duplicate alert IDs after the first alert in each incident group so reviewers can see what would be deduplicated.

## What This Demonstrates

- Incident-response thinking beyond single-alert threshold checks.
- Shared CLI/API implementation for consistent automation behavior.
- Reviewer artifacts that can be attached to a release, incident review, or CI job.
- Practical Kubernetes, metrics, and Terraform-shaped service registration assets.

## Limitations

- This is a static review engine for saved alert payloads; it does not connect to PagerDuty, Datadog, Prometheus, Slack, or Kubernetes.
- The correlation rules are intentionally deterministic for portfolio review. A production system would add service topology, alert histories, and incident feedback loops.
- The Terraform example uses `terraform_data` only, so it is safe to validate locally and does not create cloud resources.

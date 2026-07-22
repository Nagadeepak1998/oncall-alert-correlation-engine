SYSTEM_PYTHON ?= python3.13
PYTHON ?= .venv/bin/python
PIP ?= .venv/bin/pip

.PHONY: install test lint smoke report api k8s-validate terraform-fmt docker-build

install:
	$(SYSTEM_PYTHON) -m venv .venv
	$(PIP) install --upgrade pip
	$(PIP) install -e '.[dev]'

test:
	PYTHONPATH=src $(PYTHON) -m pytest -q

lint:
	PYTHONPATH=src $(PYTHON) -m ruff check src tests

smoke:
	PYTHONPATH=src $(PYTHON) -m oncall_alert_correlation_engine.cli correlate examples/noisy_alerts.json --catalog examples/service_catalog.json --fail-on-page

report:
	PYTHONPATH=src $(PYTHON) -m oncall_alert_correlation_engine.cli correlate examples/noisy_alerts.json --catalog examples/service_catalog.json --json-out reports/latest/correlation_report.json --markdown-out reports/latest/correlation_report.md --metrics-out reports/latest/metrics.prom

api:
	PYTHONPATH=src $(PYTHON) -m uvicorn oncall_alert_correlation_engine.api:app --host 127.0.0.1 --port 8088

k8s-validate:
	kubectl kustomize infra/k8s

terraform-fmt:
	terraform -chdir=infra/terraform fmt -check -recursive

docker-build:
	docker build -f infra/docker/Dockerfile -t oncall-alert-correlation-engine:local .

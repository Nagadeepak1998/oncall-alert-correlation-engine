# On-Call Alert Correlation Report

Reviewed 5 alerts, correlated 2 incidents, and found 1 page-worthy incidents.

| Incident | Service | Severity | Alerts | Owner | Missing readiness |
| --- | --- | --- | ---: | --- | --- |
| inc-7863ec05e3 | checkout-api | P1 | 3 | Revenue Platform | none |
| inc-0d19f6e6c3 | search-api | P3 | 2 | Search Platform | escalation_policy, runbook_url |

## Recommended Actions

- **inc-7863ec05e3**: Page Revenue Platform for checkout-api; correlate 5xx_error_rate, latency_p95; verify dependencies payment-gateway, orders-db before mitigation.
- **inc-0d19f6e6c3**: Open a ticket for Search Platform to review search-api signals: latency_p95.

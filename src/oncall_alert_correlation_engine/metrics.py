"""Prometheus exposition helpers."""

from prometheus_client import CollectorRegistry, Counter, Gauge, generate_latest

from .models import CorrelationReport


def render_metrics(report: CorrelationReport) -> str:
    registry = CollectorRegistry()
    reviewed = Counter(
        "oncall_correlation_alerts_reviewed_total",
        "Total alerts reviewed by the correlation engine.",
        registry=registry,
    )
    incidents = Gauge(
        "oncall_correlation_incidents",
        "Current correlated incident count.",
        registry=registry,
    )
    pages = Gauge(
        "oncall_correlation_page_worthy_incidents",
        "Current page-worthy incident count.",
        registry=registry,
    )
    reviewed.inc(report.reviewed_alerts)
    incidents.set(report.incident_count)
    pages.set(report.page_worthy_incidents)
    return generate_latest(registry).decode("utf-8")


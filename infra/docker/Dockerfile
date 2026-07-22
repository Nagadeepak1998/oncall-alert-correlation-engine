FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir .

EXPOSE 8088
CMD ["uvicorn", "oncall_alert_correlation_engine.api:app", "--host", "0.0.0.0", "--port", "8088"]

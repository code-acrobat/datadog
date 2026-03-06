# Datadog APM Python Auto-Instrumentation Demo

This demo app shows Datadog APM traces for a Python service using **auto-instrumentation** with `ddtrace-run`.

## What this demo includes

- Flask web server
- SQLite query spans
- Outbound HTTP request spans (`requests`)
- Error trace endpoint

## Prerequisites

- Python 3.10+
- A Datadog Agent reachable from this machine

## 1) Install dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 2) Set Datadog config

Set these environment variables before running:

```bash
export DD_SERVICE=python-apm-demo
export DD_ENV=demo
export DD_VERSION=1.0.0
export DD_TRACE_ENABLED=true
export DD_LOGS_INJECTION=true

# Use this when Datadog Agent is local (default):
export DD_AGENT_HOST=127.0.0.1
export DD_TRACE_AGENT_PORT=8126
```

If your agent is remote, set `DD_AGENT_HOST` accordingly.

## 3) Run with auto-instrumentation

```bash
ddtrace-run python app.py
```

App listens on `http://localhost:8000`.

## 4) Generate traces

In another terminal:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/work
curl http://localhost:8000/work
curl http://localhost:8000/error
```

Then open Datadog APM and filter by service: `python-apm-demo`.

## Notes

- `/work` creates DB and HTTP spans under one request trace.
- `/error` intentionally returns a 500 to demonstrate error tracing.
- Auto-instrumentation is provided by `ddtrace-run`; app code does not call `patch_all()`.

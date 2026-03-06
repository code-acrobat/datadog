# Datadog APM Python Auto-Instrumentation Demo

This demo app shows Datadog APM traces for a Python service using **auto-instrumentation** with `ddtrace-run`.

## What this demo includes

- Flask web server
- SQLite query spans
- Outbound HTTP request spans (`requests`)
- Error trace endpoint
- **Custom metrics** sent via StatsD (works with free tier)
- **Demo client** for automated traffic generation

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
# Activate virtual environment (if not already activated)
source .venv/bin/activate

# Set Datadog config
export DD_SERVICE=python-apm-demo
export DD_ENV=demo
export DD_VERSION=1.0.0
export DD_TRACE_ENABLED=true
export DD_LOGS_INJECTION=true

# Use this when Datadog Agent is local (default):
export DD_AGENT_HOST=127.0.0.1
export DD_TRACE_AGENT_PORT=8126

# Run with auto-instrumentation
ddtrace-run python app.py
```

**Or use the convenience script:**
```bash
./run_demo.sh
```

**Or run with automated traffic generation:**
```bash
./run_demo_with_traffic.sh
```
This starts both the server and client, generating continuous traffic with distributed traces across two services.

App listens on `http://localhost:8000`.

## 4) Generate traces

In another terminal:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/work
curl http://localhost:8000/work
curl http://localhost:8000/error
```

**Or use the automated demo client:**
```bash
# Run for 60 seconds (default)
python demo_client.py

# Run for custom duration (in seconds)
python demo_client.py 120
```

The demo client runs as a separate service (`demo-client`) and creates distributed traces that span both the client and server services. It logs progress every 10 requests.

## 5) View metrics in Datadog

The app sends custom metrics via StatsD to your Datadog agent:

- `endpoint.*.hits` - Counter for each endpoint access
- `database.insert.success/error` - Database operation counters
- `database.hits.total` - Gauge showing total database records
- `http.request.success/error` - HTTP request counters

In Datadog Metrics Explorer, search for these metrics filtered by:
- `service:python-apm-demo`
- `env:demo`

## 6) View distributed traces

When using the demo client, you'll see **distributed traces** that span across services:
- **demo-client** service: Client-side request spans
- **python-apm-demo** service: Server-side processing spans

In Datadog APM → Traces, you can see the full request flow from client to server, including database and HTTP operations within the server spans.

## Notes

- `/work` creates DB and HTTP spans under one request trace.
- `/error` intentionally returns a 500 to demonstrate error tracing.
- Auto-instrumentation is provided by `ddtrace-run`; app code does not call `patch_all()`.
- Custom metrics work with Datadog's free tier (metrics enabled).

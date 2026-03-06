# Docker Setup for Datadog APM Demo

This Docker Compose setup runs the Python APM demo with a local Datadog Agent, configured for the EU instance by default.

## Prerequisites

- Docker and Docker Compose installed
- A Datadog API key from your EU account (https://datadoghq.eu)

## Quick Start

1. **Set your Datadog API key:**
   ```bash
   export DD_API_KEY=your_api_key_here
   ```

2. **Start the services:**
   ```bash
   docker-compose up --build
   ```

3. **Generate traces and logs:**
   In another terminal:
   ```bash
   # Health check
   curl http://localhost:8000/health
   
   # Generate traces with database and HTTP spans
   curl http://localhost:8000/work
   curl http://localhost:8000/work  # Run multiple times
   
   # Generate an error trace
   curl http://localhost:8000/error
   ```

4. **View in Datadog:**
   - Go to https://datadoghq.eu (you'll sign into your EU instance)
   - Navigate to APM → Traces
   - Filter by service: `python-apm-demo`

## What's Included

### Services

- **datadog-agent**: Datadog Agent container (EU instance by default)
  - APM/Trace collection on port 8126
  - Statsd metrics on port 8125
  - Container and system monitoring enabled

- **python-app**: Flask application with auto-instrumented traces
  - Exposes on port 8000
  - Auto-instrumentation via `ddtrace-run`

### Logging

The app includes structured logging at various levels:
- **INFO**: Endpoint calls, database operations, HTTP requests
- **DEBUG**: Health checks
- **ERROR**: Database/HTTP errors and intentional exceptions

These logs are automatically collected by the Datadog Agent and will appear in Datadog Logs with the tag `service:python-apm-demo`.

### Configuration

Key environment variables (EU instance by default):
- `DD_SITE: datadoghq.eu` - Routes to EU Datadog endpoint
- `DD_SERVICE: python-apm-demo` - Service name for traces
- `DD_ENV: demo` - Environment tag
- `DD_LOGS_INJECTION: true` - Adds trace IDs to logs

## Stopping

```bash
docker-compose down
```

## Troubleshooting

- **Agent not starting**: Check that `DD_API_KEY` is set correctly
- **No traces appearing**: Ensure the Flask app can reach the agent at `datadog-agent:8126`
- **Missing logs**: Verify `DD_LOGS_ENABLED=true` on the agent

#!/bin/bash
# Run Datadog APM Demo with Virtual Environment

echo "Starting Datadog APM Python Demo..."
echo "===================================="

# Activate virtual environment
source .venv/bin/activate

# Set Datadog environment variables for EU instance
export DD_SITE=datadoghq.eu
export DD_SERVICE=python-apm-demo
export DD_ENV=demo
export DD_VERSION=1.0.0
export DD_TRACE_ENABLED=true
export DD_PROFILING_ENABLED=true
export DD_LOGS_INJECTION=true

echo "Datadog configuration:"
echo "  Site: $DD_SITE"
echo "  Service: $DD_SERVICE"
echo "  Environment: $DD_ENV"
echo "  Version: $DD_VERSION"
echo ""

# Run the Flask app with auto-instrumentation
echo "Starting Flask app with ddtrace-run..."
ddtrace-run python app.py
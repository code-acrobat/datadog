#!/bin/bash
# Run Datadog APM Demo with automated client traffic generation

echo "Starting Datadog APM Python Demo with automated traffic..."
echo "=========================================================="

# Activate virtual environment
source .venv/bin/activate

# Set Datadog environment variables for EU instance
export DD_SITE=datadoghq.eu
export DD_SERVICE=python-apm-demo
export DD_ENV=demo
export DD_VERSION=1.0.0
export DD_TRACE_ENABLED=true
export DD_LOGS_INJECTION=true

echo "Datadog configuration:"
echo "  Site: $DD_SITE"
echo "  Service: $DD_SERVICE"
echo "  Environment: $DD_ENV"
echo "  Version: $DD_VERSION"
echo ""

# Function to cleanup background processes
cleanup() {
    echo ""
    echo "Stopping demo..."
    kill $SERVER_PID 2>/dev/null
    kill $CLIENT_PID 2>/dev/null
    wait $SERVER_PID 2>/dev/null
    wait $CLIENT_PID 2>/dev/null
    echo "Demo stopped."
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup EXIT INT TERM

echo "Starting Flask server in background..."
# Start the server in background
/home/coder/datadog/.venv/bin/ddtrace-run python app.py &
SERVER_PID=$!

# Wait for server to be ready
echo "Waiting for server to start..."
sleep 5

# Test if server is responding
if curl -s http://localhost:8000/health > /dev/null; then
    echo "Server is ready!"
else
    echo "Warning: Server may not be ready yet"
fi

echo "Starting automated client (will run for 60 seconds)..."
echo "Press Ctrl+C to stop"
# Start the client with ddtrace instrumentation
DD_SERVICE=demo-client DD_ENV=demo DD_VERSION=1.0.0 /home/coder/datadog/.venv/bin/ddtrace-run python demo_client.py &
CLIENT_PID=$!

# Wait for client to finish
wait $CLIENT_PID

echo "Client finished. Server still running on http://localhost:8000"
echo "Press Ctrl+C to stop the server"
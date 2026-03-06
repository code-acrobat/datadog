# Datadog Agent Ubuntu Installation

The Datadog Agent has been installed directly on Ubuntu 24.04. This setup is configured for the **EU instance** by default.

## Quick Setup

1. **Set your Datadog API key:**
   ```bash
   sudo /etc/datadog-agent/setup_agent.sh YOUR_API_KEY_HERE
   ```

   Replace `YOUR_API_KEY_HERE` with your actual Datadog API key from https://datadoghq.eu

2. **Install Python dependencies:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Verify agent is running:**
   ```bash
   sudo service datadog-agent status
   ```

4. **Run your Python app with APM:**
   ```bash
   # Activate virtual environment
   source .venv/bin/activate
   
   # Set environment variables
   export DD_SITE=datadoghq.eu
   export DD_SERVICE=python-apm-demo
   export DD_ENV=demo
   export DD_VERSION=1.0.0
   export DD_TRACE_ENABLED=true
   export DD_LOGS_INJECTION=true

   # Run with auto-instrumentation
   ddtrace-run python app.py
   ```

   **Or use the convenience script:**
   ```bash
   ./run_demo.sh
   ```

4. **Generate traces:**
   In another terminal:
   ```bash
   curl http://localhost:8000/health
   curl http://localhost:8000/work
   curl http://localhost:8000/error
   ```

## Agent Configuration

- **EU Instance**: `datadoghq.eu`
- **APM Port**: 8126
- **StatsD Port**: 8125
- **Logs**: Enabled with injection
- **Process Monitoring**: Enabled
- **System Monitoring**: Enabled

## Agent Management

```bash
# Check status
sudo /opt/datadog-agent/bin/supervisorctl status

# Stop agent
sudo /opt/datadog-agent/bin/supervisorctl stop all

# Start agent
sudo /opt/datadog-agent/bin/start_agent.sh

# Restart agent
sudo /opt/datadog-agent/bin/supervisorctl restart all
```

## View Data in Datadog

Go to https://datadoghq.eu and check:
- **APM → Traces**: Filter by service `python-apm-demo`
- **Logs**: Filter by service `python-apm-demo`
- **Infrastructure**: See your Ubuntu host
- **Processes**: Monitor running processes

## Troubleshooting

- **Agent not starting**: Check API key is correct
- **No traces**: Verify environment variables are set
- **Permission issues**: Run commands with `sudo`
- **Port conflicts**: Check if ports 8126/8125 are available

## Configuration Files

- **Agent config**: `/etc/datadog-agent/datadog.yaml`
- **Setup script**: `/etc/datadog-agent/setup_agent.sh`
- **Logs**: `/var/log/datadog/` (if exists)</content>
<parameter name="filePath">/home/coder/datadog/UBUNTU_SETUP.md
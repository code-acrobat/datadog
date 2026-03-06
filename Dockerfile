FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY app.py .

# Install ddtrace and other monitoring tools
RUN pip install --no-cache-dir ddtrace

# Expose port
EXPOSE 8000

# Run with ddtrace auto-instrumentation
CMD ["ddtrace-run", "python", "app.py"]

import logging
import sqlite3
import time
from pathlib import Path

import requests
from flask import Flask, jsonify
from datadog import statsd

# Configure structured logging for Datadog
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
DB_PATH = Path(__file__).with_name("demo.db")

# Initialize StatsD client for custom metrics (connects to local agent on port 8125)
# This works with Datadog free tier (metrics enabled)
statsd.constant_tags = ["env:demo", "service:python-apm-demo"]


def init_db() -> None:
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS hits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                endpoint TEXT NOT NULL,
                created_at REAL NOT NULL
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


@app.get("/")
def index():
    logger.info("Index endpoint accessed")
    statsd.increment("endpoint.index.hits", tags=["endpoint:index"])
    return jsonify(
        {
            "message": "Datadog APM Python demo",
            "endpoints": ["/", "/work", "/error", "/health"],
        }
    )


@app.get("/health")
def health():
    logger.debug("Health check endpoint accessed")
    statsd.increment("endpoint.health.hits", tags=["endpoint:health"])
    return {"status": "ok"}


@app.get("/work")
def work():
    # Simulate mixed work so APM shows multiple spans.
    logger.info("Work endpoint called - starting database operation")
    statsd.increment("endpoint.work.hits", tags=["endpoint:work"])
    
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute(
            "INSERT INTO hits (endpoint, created_at) VALUES (?, ?)",
            ("/work", time.time()),
        )
        conn.commit()
        statsd.increment("database.insert.success", tags=["operation:insert"])
        logger.info("Database insert successful")
        rows = conn.execute("SELECT COUNT(*) FROM hits").fetchone()
        statsd.gauge("database.hits.total", rows[0], tags=["operation:count"])
        logger.info(f"Total hits in database: {rows[0]}")
    except Exception as e:
        statsd.increment("database.insert.error", tags=["operation:insert"])
        logger.error(f"Database error: {str(e)}", exc_info=True)
        raise
    finally:
        conn.close()

    try:
        logger.info("Making HTTP request to httpbin.org")
        response = requests.get("https://httpbin.org/delay/0.1", timeout=2)
        response.raise_for_status()
        statsd.increment("http.request.success", tags=["status:200"])
        logger.info(f"HTTP request successful: {response.status_code} from {response.url}")
    except requests.RequestException as e:
        statsd.increment("http.request.error", tags=["status:error"])
        logger.warning(f"HTTP request failed: {str(e)}")
        raise

    return jsonify(
        {
            "db_row_count": rows[0],
            "http_status": response.status_code,
            "http_url": response.url,
        }
    )


@app.get("/error")
def error():
    logger.error("Error endpoint triggered - about to raise exception", extra={"user": "demo"})
    statsd.increment("endpoint.error.triggers", tags=["endpoint:error"])
    raise RuntimeError("Intentional demo exception to show error traces")


if __name__ == "__main__":
    logger.info("Initializing database")
    init_db()
    logger.info("Database initialized successfully")
    logger.info("Starting Flask application on 0.0.0.0:8000")
    app.run(host="0.0.0.0", port=8000, debug=False)

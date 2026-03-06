import logging
import sqlite3
import time
from pathlib import Path

import requests
from flask import Flask, jsonify

# Configure structured logging for Datadog
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
DB_PATH = Path(__file__).with_name("demo.db")


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
    return jsonify(
        {
            "message": "Datadog APM Python demo",
            "endpoints": ["/", "/work", "/error", "/health"],
        }
    )


@app.get("/health")
def health():
    logger.debug("Health check endpoint accessed")
    return {"status": "ok"}


@app.get("/work")
def work():
    # Simulate mixed work so APM shows multiple spans.
    logger.info("Work endpoint called - starting database operation")
    
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute(
            "INSERT INTO hits (endpoint, created_at) VALUES (?, ?)",
            ("/work", time.time()),
        )
        conn.commit()
        logger.info("Database insert successful")
        rows = conn.execute("SELECT COUNT(*) FROM hits").fetchone()
        logger.info(f"Total hits in database: {rows[0]}")
    except Exception as e:
        logger.error(f"Database error: {str(e)}", exc_info=True)
        raise
    finally:
        conn.close()

    try:
        logger.info("Making HTTP request to httpbin.org")
        response = requests.get("https://httpbin.org/delay/0.1", timeout=2)
        response.raise_for_status()
        logger.info(f"HTTP request successful: {response.status_code} from {response.url}")
    except requests.RequestException as e:
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
    raise RuntimeError("Intentional demo exception to show error traces")


if __name__ == "__main__":
    logger.info("Initializing database")
    init_db()
    logger.info("Database initialized successfully")
    logger.info("Starting Flask application on 0.0.0.0:8000")
    app.run(host="0.0.0.0", port=8000, debug=False)

import sqlite3
import time
from pathlib import Path

import requests
from flask import Flask, jsonify

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
    return jsonify(
        {
            "message": "Datadog APM Python demo",
            "endpoints": ["/", "/work", "/error", "/health"],
        }
    )


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/work")
def work():
    # Simulate mixed work so APM shows multiple spans.
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute(
            "INSERT INTO hits (endpoint, created_at) VALUES (?, ?)",
            ("/work", time.time()),
        )
        conn.commit()
        rows = conn.execute("SELECT COUNT(*) FROM hits").fetchone()
    finally:
        conn.close()

    response = requests.get("https://httpbin.org/delay/0.1", timeout=2)
    response.raise_for_status()

    return jsonify(
        {
            "db_row_count": rows[0],
            "http_status": response.status_code,
            "http_url": response.url,
        }
    )


@app.get("/error")
def error():
    raise RuntimeError("Intentional demo exception to show error traces")


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=8000, debug=False)

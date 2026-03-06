#!/usr/bin/env python3
"""
Demo client that randomly calls endpoints to generate metrics and traces.
This simulates real traffic to the Datadog APM demo app.
"""

import random
import time
import requests
import logging
from typing import List

# Import ddtrace for instrumentation and trace propagation
from ddtrace import tracer, patch_all

# Enable auto-instrumentation for requests
patch_all()

# Note: Service name, env, and version are set via environment variables
# when running with ddtrace-run

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Base URL for the demo app
BASE_URL = "http://localhost:8000"

# Available endpoints to call
ENDPOINTS = ["/", "/health", "/work", "/error"]

# Weights for random selection (error endpoint less frequent)
WEIGHTS = [0.3, 0.4, 0.25, 0.05]  # /, /health, /work, /error


def make_request(endpoint: str) -> None:
    """Make a request to the specified endpoint."""
    url = f"{BASE_URL}{endpoint}"

    # Create a span for the client request
    with tracer.trace("client.request", resource=f"GET {endpoint}") as span:
        span.set_tags({
            'http.method': 'GET',
            'http.url': url,
            'endpoint': endpoint
        })

        try:
            logger.info(f"Making request to {url}")
            response = requests.get(url, timeout=5)

            # Add response information to the span
            span.set_tags({
                'http.status_code': response.status_code,
                'http.status_msg': response.reason
            })

            if endpoint == "/error":
                # Error endpoint is expected to return 500
                logger.info(f"Error endpoint returned {response.status_code} (expected)")
            else:
                response.raise_for_status()
                logger.info(f"Request to {endpoint} successful: {response.status_code}")

        except requests.RequestException as e:
            # Record the error in the span
            span.set_tags({
                'error': True,
                'error.msg': str(e)
            })
            logger.error(f"Request to {endpoint} failed: {str(e)}")
            # Don't re-raise the exception - continue with the demo


def run_demo(duration_seconds: int = 60) -> None:
    """Run the demo for the specified duration."""
    logger.info(f"Starting demo client for {duration_seconds} seconds")
    logger.info(f"Will randomly call endpoints: {ENDPOINTS}")
    logger.info("Press Ctrl+C to stop early")

    # Create a span for the entire demo run
    with tracer.trace("demo.run", resource=f"run_demo_{duration_seconds}s") as demo_span:
        demo_span.set_tags({
            'demo.duration': duration_seconds,
            'demo.endpoints': ','.join(ENDPOINTS)
        })

        start_time = time.time()
        request_count = 0

        try:
            while time.time() - start_time < duration_seconds:
                # Randomly select an endpoint based on weights
                endpoint = random.choices(ENDPOINTS, weights=WEIGHTS, k=1)[0]

                # Make the request
                make_request(endpoint)
                request_count += 1

                # Log progress every 10 requests
                if request_count % 10 == 0:
                    elapsed = time.time() - start_time
                    logger.info(f"Progress: {request_count} requests in {elapsed:.1f}s")

                # Wait 1 second before next request
                time.sleep(1)

        except KeyboardInterrupt:
            logger.info("Demo interrupted by user")

        # Update demo span with final stats
        demo_span.set_tags({
            'demo.requests_made': request_count,
            'demo.actual_duration': time.time() - start_time
        })

        logger.info(f"Demo completed. Made {request_count} requests in {time.time() - start_time:.1f} seconds")


if __name__ == "__main__":
    import sys

    # Allow custom duration via command line argument
    duration = int(sys.argv[1]) if len(sys.argv) > 1 else 60

    run_demo(duration)
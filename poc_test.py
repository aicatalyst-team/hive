#!/usr/bin/env python3
"""PoC validation tests for Hive agent memory API.

Uses only Python stdlib (urllib.request). Outputs structured JSON results.

Usage:
    python poc_test.py [BASE_URL]
    python poc_test.py http://hive.poc-hive.svc.cluster.local:8080
"""
from __future__ import annotations

import json
import sys
import time
import urllib.request
import urllib.error

DEFAULT_BASE_URL = "http://hive.poc-hive.svc.cluster.local:8080"


def _request(
    url: str,
    method: str = "GET",
    data: dict | None = None,
    timeout: int = 30,
    retries: int = 3,
    backoff: float = 2.0,
) -> tuple[int, dict | str]:
    """Make an HTTP request with retry logic."""
    headers = {"Content-Type": "application/json"} if data else {}
    body = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)

    last_error = None
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                raw = resp.read().decode("utf-8")
                try:
                    return resp.status, json.loads(raw)
                except json.JSONDecodeError:
                    return resp.status, raw
        except urllib.error.HTTPError as e:
            raw = e.read().decode("utf-8", errors="replace")
            try:
                return e.code, json.loads(raw)
            except json.JSONDecodeError:
                return e.code, raw
        except (urllib.error.URLError, OSError, TimeoutError) as e:
            last_error = str(e)
            if attempt < retries - 1:
                wait = backoff * (attempt + 1)
                print(f"  Retry {attempt + 1}/{retries} after {wait}s: {last_error}", file=sys.stderr)
                time.sleep(wait)
    return -1, f"Connection failed after {retries} attempts: {last_error}"


def test_health_check(base_url: str) -> dict:
    """Scenario 1: GET /health -> 200."""
    t0 = time.time()
    status, body = _request(f"{base_url}/health")
    duration = time.time() - t0

    passed = status == 200 and isinstance(body, dict) and body.get("status") == "alive"
    return {
        "scenario_name": "health-check",
        "status": "pass" if passed else "fail",
        "output": json.dumps(body) if isinstance(body, dict) else str(body),
        "error_message": None if passed else f"HTTP {status}: {body}",
        "duration_seconds": round(duration, 3),
    }


def test_ready_check(base_url: str) -> dict:
    """Scenario 2: GET /ready -> 200."""
    t0 = time.time()
    status, body = _request(f"{base_url}/ready")
    duration = time.time() - t0

    passed = status == 200 and isinstance(body, dict) and body.get("status") == "ready"
    return {
        "scenario_name": "ready-check",
        "status": "pass" if passed else "fail",
        "output": json.dumps(body) if isinstance(body, dict) else str(body),
        "error_message": None if passed else f"HTTP {status}: {body}",
        "duration_seconds": round(duration, 3),
    }


def test_route_request(base_url: str) -> dict:
    """Scenario 3: POST /route with routing request."""
    t0 = time.time()
    payload = {
        "goal": "What is the weather today?",
        "available_tools": ["search", "calculator"],
        "step": 0,
    }
    status, body = _request(f"{base_url}/route", method="POST", data=payload)
    duration = time.time() - t0

    passed = (
        status == 200
        and isinstance(body, dict)
        and "tool" in body
        and "confidence" in body
        and "escalated" in body
        and "source" in body
    )
    return {
        "scenario_name": "route-request",
        "status": "pass" if passed else "fail",
        "output": json.dumps(body) if isinstance(body, dict) else str(body),
        "error_message": None if passed else f"HTTP {status}: {body}",
        "duration_seconds": round(duration, 3),
    }


def test_compress_request(base_url: str) -> dict:
    """Scenario 4: POST /compress with compression request."""
    t0 = time.time()
    payload = {
        "role": "user",
        "content": "Hello world, this is a test message for compression",
    }
    status, body = _request(f"{base_url}/compress", method="POST", data=payload)
    duration = time.time() - t0

    passed = (
        status == 200
        and isinstance(body, dict)
        and "role" in body
        and "content" in body
        and "label" in body
    )
    return {
        "scenario_name": "compress-request",
        "status": "pass" if passed else "fail",
        "output": json.dumps(body) if isinstance(body, dict) else str(body),
        "error_message": None if passed else f"HTTP {status}: {body}",
        "duration_seconds": round(duration, 3),
    }


def test_remember_recall(base_url: str) -> dict:
    """Scenario 5: POST /remember then GET /recall."""
    t0 = time.time()

    # Step 1: Remember
    remember_payload = {
        "key": "test-endpoint",
        "value": "/v1/api",
        "trust": 1.0,
    }
    status1, body1 = _request(f"{base_url}/remember", method="POST", data=remember_payload)
    remember_ok = status1 == 200 and isinstance(body1, dict) and body1.get("status") == "ok"

    # Step 2: Recall
    status2, body2 = _request(f"{base_url}/recall?key=test-endpoint")
    recall_ok = (
        status2 == 200
        and isinstance(body2, dict)
        and body2.get("key") == "test-endpoint"
        and body2.get("value") == "/v1/api"
    )
    duration = time.time() - t0

    passed = remember_ok and recall_ok
    output_parts = []
    if remember_ok:
        output_parts.append(f"remember: {json.dumps(body1)}")
    else:
        output_parts.append(f"remember FAILED: HTTP {status1} {body1}")
    if recall_ok:
        output_parts.append(f"recall: {json.dumps(body2)}")
    else:
        output_parts.append(f"recall FAILED: HTTP {status2} {body2}")

    return {
        "scenario_name": "remember-recall",
        "status": "pass" if passed else "fail",
        "output": "; ".join(output_parts),
        "error_message": None if passed else "; ".join(output_parts),
        "duration_seconds": round(duration, 3),
    }


def main() -> int:
    base_url = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_BASE_URL
    base_url = base_url.rstrip("/")

    print(f"Running PoC tests against: {base_url}", file=sys.stderr)
    print(f"Timestamp: {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}", file=sys.stderr)

    tests = [
        test_health_check,
        test_ready_check,
        test_route_request,
        test_compress_request,
        test_remember_recall,
    ]

    results = []
    for test_fn in tests:
        print(f"  Running: {test_fn.__doc__}", file=sys.stderr)
        result = test_fn(base_url)
        results.append(result)
        status_icon = "PASS" if result["status"] == "pass" else "FAIL"
        print(f"  [{status_icon}] {result['scenario_name']} ({result['duration_seconds']}s)", file=sys.stderr)

    passed = sum(1 for r in results if r["status"] == "pass")
    failed = sum(1 for r in results if r["status"] == "fail")
    print(f"\nResults: {passed} passed, {failed} failed out of {len(results)}", file=sys.stderr)

    # Output structured JSON to stdout
    print(json.dumps({"results": results, "passed": passed, "failed": failed}, indent=2))

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())

import os
from typing import List, Union

import requests
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)

DEFAULT_BACKEND_URL = (
    "http://ocp-dog-backend-api.guscontre-dev.svc.cluster.local:5002/dog"
)
DEFAULT_ALLOWED_ORIGINS = "*"


def parse_allowed_origins(raw_value: str) -> Union[str, List[str]]:
    """Return '*' or a list of allowed origins understood by Flask-CORS."""
    if not raw_value or raw_value.strip() == "*":
        return "*"

    origins = [origin.strip() for origin in raw_value.split(",")]
    return [origin for origin in origins if origin]


def get_backend_url() -> str:
    return os.environ.get("BACKEND_URL", DEFAULT_BACKEND_URL)


def get_backend_base() -> str:
    url = get_backend_url().rstrip("/")
    # If points to /dog, strip it to build other endpoints
    if url.endswith("/dog"):
        return url[: -len("/dog")]
    return url


def get_allowed_origins() -> Union[str, List[str]]:
    raw_value = os.environ.get("ALLOWED_ORIGINS", DEFAULT_ALLOWED_ORIGINS)
    return parse_allowed_origins(raw_value)


CORS(app, resources={r"/*": {"origins": get_allowed_origins()}})


@app.get("/healthz")
def healthz():
    return jsonify({"status": "ok"})


@app.get("/dog")
def dog():
    backend_url = get_backend_url()
    try:
        response = requests.get(backend_url, timeout=5)
        response.raise_for_status()
        payload = response.json()
    except Exception as exc:
        return jsonify({"status": "error", "message": str(exc)}), 502

    return jsonify(payload)


@app.post("/save")
def save():
    base = get_backend_base()
    try:
        payload = request.get_json(force=True, silent=True) or {}
        resp = requests.post(f"{base}/save", json=payload, timeout=5)
        resp.raise_for_status()
        return jsonify(resp.json())
    except Exception as exc:
        return jsonify({"status": "error", "message": str(exc)}), 502


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5001)))

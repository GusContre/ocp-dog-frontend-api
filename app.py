import os

from flask import Flask, jsonify
import requests

app = Flask(__name__)

DEFAULT_BACKEND_URL = "http://ocp-dog-backend-api:5002/dog"


def get_backend_url() -> str:
    return os.environ.get("BACKEND_URL", DEFAULT_BACKEND_URL)


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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5001)))

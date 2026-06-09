from flask import Flask, jsonify
import os
import redis
from datetime import datetime

app = Flask(__name__)

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)


def get_redis_client():
    return redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        password=REDIS_PASSWORD if REDIS_PASSWORD else None,
        decode_responses=True
    )


@app.route("/api/ping")
def ping():
    print(f"[{datetime.now()}] Received request: /api/ping")

    try:
        r = get_redis_client()
        r.set("last_ping", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        redis_status = "connected"
    except Exception as e:
        redis_status = f"error: {str(e)}"

    return jsonify({
        "status": "ok",
        "redis": redis_status
    })


@app.route("/")
def index():
    return jsonify({
        "message": "Cloud Computing Course Project Backend",
        "status": "running"
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

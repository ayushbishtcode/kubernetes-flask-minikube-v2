from flask import Flask
import socket

app = Flask(__name__)


@app.route("/")
def home():
    return {
        "application": "Kubernetes Flask Demo",
        "version": "v2",
        "pod": socket.gethostname(),
        "status": "running"
    }


@app.route("/health")
def health():
    return {
        "status": "healthy"
    }


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5006)
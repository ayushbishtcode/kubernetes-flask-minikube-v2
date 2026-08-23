from flask import Flask

app = Flask(__name__)


@app.route("/admin")
def admin():
    return {
        "application": "Admin Application",
        "message": "Admin API",
        "status": "working"
    }


@app.route("/health")
def health():
    return {
        "status": "healthy"
    }


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5007)
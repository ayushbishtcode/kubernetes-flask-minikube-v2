from flask import Flask
import os
import psycopg2

app = Flask(__name__)


def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )


@app.route("/")
def home():
    return {
        "application": "Kubernetes Flask + PostgreSQL",
        "status": "running",
        "version": "v3"
    }


@app.route("/health")
def health():
    return {
        "status": "healthy"
    }

@app.route("/api")
def api():
    return {
        "message": "Flask API",
        "status": "working"
    }


@app.route("/db-test")
def db_test():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT version();")
    result = cursor.fetchone()

    cursor.close()
    conn.close()

    return {
        "database": "connected",
        "postgresql_version": result[0]
    }


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5006)
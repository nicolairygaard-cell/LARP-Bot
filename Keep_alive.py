from flask import Flask
from datetime import datetime

app = Flask(__name__)

@app.route("/")
def keep_alive():
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "message": "Server is running"
    }

@app.route("/health")
def health():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

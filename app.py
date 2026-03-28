from __future__ import annotations

from datetime import datetime

from flask import Flask, jsonify, render_template, request

app = Flask(__name__)


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/chat")
def chat():
    payload = request.get_json(silent=True) or {}
    user_message = (payload.get("message") or "").strip()

    if not user_message:
        return jsonify({"error": "Message is required."}), 400

    reply = (
        "meow"
    )

    return jsonify(
        {
            "reply": reply,
            "timestamp": datetime.now().strftime("%I:%M %p"),
        }
    )


if __name__ == "__main__":
    app.run(debug=True)
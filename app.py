from datetime import datetime
import atexit
import threading
import uuid
from flask import Flask, jsonify, render_template, request

from dotenv import load_dotenv

from query_chat_service import QueryChatService

app = Flask(__name__)

load_dotenv()

_service_lock = threading.Lock()
_chat_service = None


def _get_chat_service():
    global _chat_service
    if _chat_service is not None:
        return _chat_service

    with _service_lock:
        if _chat_service is None:
            _chat_service = QueryChatService()
            atexit.register(_chat_service.close)
    return _chat_service


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/chat")
def chat():
    payload = request.get_json(silent=True) or {}
    user_message = (payload.get("message") or "").strip()
    chat_id = (payload.get("chat_id") or "").strip() or str(uuid.uuid4())
    reset = bool(payload.get("reset"))

    if not user_message:
        return jsonify({"error": "Message is required."}), 400

    try:
        service = _get_chat_service()
        reply = service.ask(chat_id=chat_id, message=user_message, reset=reset)
    except Exception as exc:
        return (
            jsonify(
                {
                    "error": "Query Agent request failed.",
                    "details": str(exc),
                    "chat_id": chat_id,
                }
            ),
            500,
        )

    return jsonify(
        {
            "reply": reply,
            "timestamp": datetime.now().strftime("%I:%M %p"),
            "chat_id": chat_id,
        }
    )


if __name__ == "__main__":
    app.run(debug=True)
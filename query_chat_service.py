import os
import threading
import time

import weaviate
from weaviate.agents.query import QueryAgent


class QueryChatService:
    def __init__(self, collections=None, system_prompt=None, timeout=60, chat_ttl_seconds=21600):
        self._collections = collections or ["Recipes", "Ingredients"]
        self._system_prompt = system_prompt or (
            "You are a helpful cooking assistant. Answer in clear, practical English. "
            "Use the Weaviate collections Recipes and Ingredients when relevant. "
            "If the user asks a follow-up question, use the conversation context. "
            "If information is missing, say what is missing and provide the closest helpful alternative."
        )
        self._timeout = timeout
        self._chat_ttl_seconds = chat_ttl_seconds

        self._lock = threading.Lock()
        self._histories = {}

        self._client = self._connect_client()
        self._agent = QueryAgent(
            client=self._client,
            collections=self._collections,
            system_prompt=self._system_prompt,
            timeout=self._timeout,
        )

    def _connect_client(self):
        weaviate_url = os.getenv("WEAVIATE_URL")
        weaviate_api_key = os.getenv("WEAVIATE_API_KEY")
        openai_api_key = os.getenv("OPENAI_API_KEY")

        if not weaviate_url or not weaviate_api_key:
            raise RuntimeError("Missing WEAVIATE_URL / WEAVIATE_API_KEY environment variables.")

        headers = {}
        if openai_api_key:
            headers["X-OpenAI-Api-Key"] = openai_api_key

        return weaviate.connect_to_weaviate_cloud(
            cluster_url=weaviate_url,
            auth_credentials=weaviate.auth.AuthApiKey(weaviate_api_key),
            headers=headers,
        )

    def close(self):
        try:
            self._client.close()
        except Exception:
            return

    def _purge_old_chats(self):
        cutoff = time.time() - self._chat_ttl_seconds
        with self._lock:
            expired = [chat_id for chat_id, (_, ts) in self._histories.items() if ts < cutoff]
            for chat_id in expired:
                self._histories.pop(chat_id, None)

    def ask(self, chat_id, message, reset=False):
        self._purge_old_chats()

        with self._lock:
            cached = self._histories.get(chat_id) if (chat_id and not reset) else None

        history = []
        if cached is not None:
            history = cached[0]

        history = list(history)
        history.append({"role": "user", "content": (message or "").strip()})

        response = self._agent.ask(history)
        reply = (response.final_answer or "").strip() or "I don't have an answer right now."

        history.append({"role": "assistant", "content": reply})

        with self._lock:
            self._histories[chat_id] = (history, time.time())

        return reply

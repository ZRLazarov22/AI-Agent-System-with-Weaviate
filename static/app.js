(() => {
  const composer = document.getElementById("composer");
  const input = document.getElementById("messageInput");
  const sendBtn = document.getElementById("sendBtn");
  const messages = document.getElementById("messages");

  if (!composer || !input || !sendBtn || !messages) return;

  const pad2 = (n) => String(n).padStart(2, "0");
  const formatTime = (date) => {
    let hours = date.getHours();
    const minutes = date.getMinutes();
    const ampm = hours >= 12 ? "PM" : "AM";
    hours = hours % 12;
    hours = hours ? hours : 12;
    return `${pad2(hours)}:${pad2(minutes)} ${ampm}`;
  };

  const appendMessage = ({ role, text, time }) => {
    const article = document.createElement("article");
    article.className = `msg msg--${role}`;

    const bubble = document.createElement("div");
    bubble.className = "msg__bubble";

    const t = document.createElement("div");
    t.className = "msg__text";
    t.textContent = text;

    const meta = document.createElement("div");
    meta.className = "msg__meta";
    meta.textContent = time;

    bubble.appendChild(t);
    bubble.appendChild(meta);
    article.appendChild(bubble);
    messages.appendChild(article);

    article.scrollIntoView({ block: "end", behavior: "smooth" });
  };

  composer.addEventListener("submit", async (e) => {
    e.preventDefault();

    const message = (input.value || "").trim();
    if (!message) return;

    const now = new Date();
    appendMessage({ role: "user", text: message, time: formatTime(now) });

    input.value = "";
    input.focus();

    try {
      sendBtn.disabled = true;

      const res = await fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message }),
      });

      if (!res.ok) return;
      const data = await res.json();
      if (!data || !data.reply) return;

      appendMessage({
        role: "assistant",
        text: data.reply,
        time: data.timestamp || formatTime(new Date()),
      });
    } finally {
      sendBtn.disabled = false;
    }
  });
})();

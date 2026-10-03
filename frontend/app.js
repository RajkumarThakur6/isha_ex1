const messagesElement = document.querySelector("#messages");
const form = document.querySelector("#chat-form");
const input = document.querySelector("#message-input");
const sendButton = document.querySelector("#send-button");
const clearButton = document.querySelector("#clear-chat");
const statusMessage = document.querySelector("#status-message");
const welcomeMessage = document.querySelector("#welcome-message");

function addMessage(role, content, isError = false) {
  welcomeMessage?.remove();
  const message = document.createElement("div");
  message.className = `message ${role}${isError ? " error" : ""}`;
  message.textContent = content;
  messagesElement.append(message);
  messagesElement.scrollTop = messagesElement.scrollHeight;
}

async function requestJson(url, options = {}) {
  const response = await fetch(url, {
    ...options,
    headers: { "Content-Type": "application/json", ...options.headers },
    credentials: "same-origin",
  });
  const payload = await response.json();
  if (!response.ok) {
    const detail = payload.detail;
    const message = Array.isArray(detail)
      ? detail.map((item) => item.msg || "Invalid request.").join(" ")
      : detail;
    throw new Error(message || `Request failed (${response.status}).`);
  }
  return payload;
}

async function loadHistory() {
  try {
    const [health, history] = await Promise.all([
      requestJson("/api/health"),
      requestJson("/api/history"),
    ]);
    document.querySelector("#model-name").textContent = health.model;
    document.querySelector("#mode-label").textContent = health.demo_mode
      ? "DEMO · no API calls"
      : `${health.provider.toUpperCase()} · live`;
    document.querySelector("#demo-notice").hidden = !health.demo_mode;
    document.querySelector("#provider-notice").hidden =
      health.demo_mode || !["ollama", "lmstudio"].includes(health.provider);
    if (health.provider === "lmstudio") {
      document.querySelector("#provider-instructions").textContent =
        "In LM Studio, load a model and start the Local Server. Set LLM_MODEL to the loaded model ID.";
      const providerLink = document.querySelector("#provider-link");
      providerLink.href = "https://lmstudio.ai/";
      providerLink.textContent = "Get LM Studio ↗";
    } else {
      document.querySelector("#provider-instructions").textContent =
        "If Ollama is not running, install it and run ollama pull llama3.2:3b, then restart this chat server.";
    }
    for (const message of history.messages) {
      addMessage(message.role, message.content);
    }
  } catch (error) {
    statusMessage.textContent = `Could not load chat: ${error.message}`;
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const message = input.value.trim();
  if (!message || sendButton.disabled) return;

  addMessage("user", message);
  input.value = "";
  sendButton.disabled = true;
  statusMessage.textContent = "Thinking…";

  try {
    const result = await requestJson("/api/chat", {
      method: "POST",
      body: JSON.stringify({ message }),
    });
    addMessage("assistant", result.reply);
    statusMessage.textContent = "AI can make mistakes. Do not share secrets or sensitive information.";
  } catch (error) {
    addMessage("assistant", error.message, true);
    statusMessage.textContent = "The request did not complete. Your conversation was not saved.";
  } finally {
    sendButton.disabled = false;
    input.focus();
  }
});

clearButton.addEventListener("click", async () => {
  clearButton.disabled = true;
  try {
    await requestJson("/api/clear", { method: "POST" });
    messagesElement.replaceChildren();
    const welcome = document.createElement("div");
    const icon = document.createElement("span");
    const heading = document.createElement("h2");
    const description = document.createElement("p");
    welcome.className = "welcome-message";
    icon.className = "welcome-icon";
    icon.setAttribute("aria-hidden", "true");
    icon.textContent = "✳";
    heading.textContent = "What would you like to learn?";
    description.textContent = "Ask a question, then ask a follow-up.";
    welcome.append(icon, heading, description);
    messagesElement.append(welcome);
    statusMessage.textContent = "New conversation started.";
  } catch (error) {
    statusMessage.textContent = `Could not clear chat: ${error.message}`;
  } finally {
    clearButton.disabled = false;
  }
});

loadHistory();

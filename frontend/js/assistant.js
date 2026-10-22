const chatLog = document.getElementById("chat-log");
const chatForm = document.getElementById("chat-form");
const chatInput = document.getElementById("chat-input");
const sendButton = document.getElementById("send-btn");

// The conversation so far. It is sent to the server with every message.
const messages = [];

function textElement(tag, className, text) {
  const element = document.createElement(tag);
  if (className) element.className = className;
  element.textContent = text; // text only, never runs HTML
  return element;
}

function scrollToEnd() {
  chatLog.scrollTop = chatLog.scrollHeight;
}

function addBubble(kind, text) {
  const bubble = textElement("div", `bubble ${kind}`, text);
  chatLog.append(bubble);
  scrollToEnd();
  return bubble;
}

function addBooks(books) {
  if (books.length === 0) return;

  const grid = document.createElement("div");
  grid.className = "rec-grid";
  for (const book of books) {
    const card = document.createElement("div");
    card.className = "rec-card";

    const available = book.available_copies > 0;
    card.append(
      textElement("h3", "", book.title),
      textElement("p", "meta", [book.author, book.category].filter(Boolean).join(" · ")),
      textElement(
        "span",
        "badge " + (available ? "badge-ok" : "badge-out"),
        available ? `${book.available_copies} available` : "All copies borrowed"
      )
    );
    grid.append(card);
  }
  chatLog.append(grid);
  scrollToEnd();
}

// The greeting is fixed text, so it costs no AI request and is not sent to the server.
addBubble(
  "assistant",
  "Hi! I'm the library assistant. Tell me what you feel like reading, " +
    "or ask me anything about our books."
);

chatForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const text = chatInput.value.trim();
  if (!text) return;

  chatInput.value = "";
  sendButton.disabled = true;
  messages.push({ role: "user", content: text });
  addBubble("user", text);
  const typing = addBubble("assistant", "Thinking...");

  try {
    const data = await aiApi.chat(messages);
    typing.remove();
    messages.push({ role: "assistant", content: data.reply });
    addBubble("assistant", data.reply);
    addBooks(data.books);
  } catch (error) {
    typing.remove();
    messages.pop(); // forget the failed message, so the history stays in order
    chatInput.value = text; // and put it back so the reader can resend it
    addBubble("error", error.message);
  } finally {
    sendButton.disabled = false;
    chatInput.focus();
  }
});
const recForm = document.getElementById("rec-form");
const recButton = document.getElementById("rec-btn");
const results = document.getElementById("results");
const messageBox = document.getElementById("message");

function showMessage(text, type = "") {
  messageBox.textContent = text;
  messageBox.className = type;
}

function textElement(tag, className, text) {
  const element = document.createElement(tag);
  if (className) element.className = className;
  element.textContent = text; // text only, never runs HTML
  return element;
}

function renderResults(recommendations) {
  results.replaceChildren();

  for (const { book, reason } of recommendations) {
    const card = document.createElement("div");
    card.className = "rec-card";

    const meta = [book.author, book.category].filter(Boolean).join(" · ");
    const available = book.available_copies > 0;
    const badge = textElement(
      "span",
      "badge " + (available ? "badge-ok" : "badge-out"),
      available ? `${book.available_copies} available` : "All copies borrowed"
    );

    card.append(
      textElement("h3", "", book.title),
      textElement("p", "meta", meta),
      badge,
      textElement("p", "reason", reason)
    );
    results.append(card);
  }
}

recForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  recButton.disabled = true; // one request at a time
  results.replaceChildren();
  showMessage("Finding books for you...");

  try {
    const data = await aiApi.recommend({
      mood: document.getElementById("mood").value,
      interests: document.getElementById("interests").value,
      length: document.getElementById("length").value,
    });
    renderResults(data.recommendations);
    showMessage(
      data.recommendations.length ? "" : "No matching books found. Try different interests."
    );
  } catch (error) {
    showMessage(error.message, "error");
  } finally {
    recButton.disabled = false;
  }
});
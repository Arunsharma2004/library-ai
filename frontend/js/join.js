const joinForm = document.getElementById("join-form");
const joinButton = document.getElementById("join-submit");
const joinMessage = document.getElementById("join-message");

function showJoinMessage(text, isError) {
  joinMessage.textContent = text;  // textContent, never innerHTML, so nothing typed can run as code
  joinMessage.className = isError ? "join-error" : "join-success";
}

joinForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  joinButton.disabled = true;
  showJoinMessage("Sending...", false);

  try {
    const response = await fetch("/api/public/join", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name: document.getElementById("join-name").value,
        email: document.getElementById("join-email").value,
        phone: document.getElementById("join-phone").value || null,
      }),
    });
    const data = await response.json().catch(() => ({}));

    if (response.ok) {
      joinForm.reset();
      showJoinMessage(data.message + " Taking you to the library...", false);
      setTimeout(() => { window.location.href = "/account.html"; }, 1800);
      return;  // keep the button disabled while we leave the page
    } else if (typeof data.detail === "string") {
      showJoinMessage(data.detail, true);  // for example the "too many requests" message
    } else {
      showJoinMessage("Please check your details. A name and a valid email are required.", true);
    }
  } catch (error) {
    showJoinMessage("Could not reach the server. Please try again.", true);
  }
  joinButton.disabled = false;
});
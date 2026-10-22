// Runs on every page except the login page. It shows who is signed in
// and adds the Log out button to the header.
(async function () {
  const header = document.querySelector(".app-header");
  if (!header) return;

  try {
    const user = await authApi.me();

    const box = document.createElement("div");
    box.className = "user-box";

    const name = document.createElement("span");
    name.textContent = user.username;

    const logoutButton = document.createElement("button");
    logoutButton.type = "button";
    logoutButton.className = "btn-secondary btn-small";
    logoutButton.textContent = "Log out";
    logoutButton.addEventListener("click", async () => {
      try {
        await authApi.logout();
      } finally {
        window.location.href = "/login.html";
      }
    });

    box.append(name, logoutButton);
    header.append(box);
  } catch (error) {
    // Not signed in: request() has already sent the browser to the login page.
  }
})();
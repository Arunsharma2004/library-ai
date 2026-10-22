// Runs on every page except the login page. It builds the navigation bar,
// shows who is signed in, and adds the Log out button.
const NAV_LINKS = [
  { href: "/", label: "Books" },
  { href: "/members.html", label: "Members" },
  { href: "/borrowing.html", label: "Borrowing" },
  { href: "/recommend.html", label: "Find a book" },
  { href: "/assistant.html", label: "Assistant" },
];

(async function () {
  const header = document.querySelector(".app-header");
  if (!header) return;

  // Rebuild the navigation from the list above.
  const oldNav = header.querySelector("nav");
  if (oldNav) oldNav.remove();

  const nav = document.createElement("nav");
  for (const link of NAV_LINKS) {
    const anchor = document.createElement("a");
    anchor.href = link.href;
    anchor.textContent = link.label;
    const isHere =
      location.pathname === link.href ||
      (link.href === "/" && location.pathname === "/index.html");
    if (isHere) anchor.className = "active";
    nav.append(anchor);
  }
  header.append(nav);

  // Who is signed in, and the Log out button.
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
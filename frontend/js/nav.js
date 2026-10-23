// Runs on every page except the login page. It builds the navigation bar for the
// current role (staff or visitor), shows who is here, and adds the Log out button.
const NAV_LINKS = [
  { href: "/", label: "Books", roles: ["staff", "visitor"] },
  { href: "/members.html", label: "Members", roles: ["staff"] },
  { href: "/borrowing.html", label: "Borrowing", roles: ["staff"] },
  { href: "/recommend.html", label: "Find a book", roles: ["staff", "visitor"] },
  { href: "/assistant.html", label: "Assistant", roles: ["staff", "visitor"] },
  { href: "/account.html", label: "My account", roles: ["visitor"] },
];

(async function () {
  const header = document.querySelector(".app-header");
  if (!header) return;

  const oldNav = header.querySelector("nav");
  if (oldNav) oldNav.remove();

  // Ask the server who is using the app.
  let session;
  try {
    const response = await fetch("/api/auth/session");
    if (!response.ok) {
      window.location.href = signInPage();  // nobody is signed in
      return;
    }
    session = await response.json();
  } catch (error) {
    return;
  }
  const role = session.role;
  document.body.classList.add("role-" + role);

  // A person who opens a page they may not use by typing its address goes back to the books.
  const here = NAV_LINKS.find(
    (link) => location.pathname === link.href ||
      (link.href === "/" && location.pathname === "/index.html")
  );
  if (here && !here.roles.includes(role)) {
    window.location.href = "/";
    return;
  }

  // The navigation: only the links this role may use.
  const nav = document.createElement("nav");
  for (const link of NAV_LINKS) {
    if (!link.roles.includes(role)) continue;
    const anchor = document.createElement("a");
    anchor.href = link.href;
    anchor.textContent = link.label;
    if (link === here) anchor.className = "active";
    nav.append(anchor);
  }
  header.append(nav);

  // Who is here: the staff username, or the visitor's name if they joined in this browser.
  let label = role === "staff" ? session.username : "Visitor";
  if (role === "visitor") {
    try {
      const response = await fetch("/api/my/account");
      if (response.ok) label = (await response.json()).name;
    } catch (error) {
      // keep "Visitor"
    }
  }

  const box = document.createElement("div");
  box.className = "user-box";

  const name = document.createElement("span");
  name.textContent = label;

  const logoutButton = document.createElement("button");
  logoutButton.type = "button";
  logoutButton.className = "btn-secondary btn-small";
  logoutButton.textContent = role === "staff" ? "Log out" : "Leave";
  logoutButton.addEventListener("click", async () => {
    try {
      await authApi.logout();
    } finally {
      window.location.href = role === "staff" ? "/login.html" : "/join.html";
    }
  });

  box.append(name, logoutButton);
  header.append(box);
})();
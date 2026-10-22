// Page behavior for "My account". It shows the member linked to this browser:
// their status (pending or member) and their own loans.

const nameEl = document.getElementById("account-name");
const emailEl = document.getElementById("account-email");
const statusEl = document.getElementById("account-status");
const noteEl = document.getElementById("account-note");
const messageEl = document.getElementById("account-message");
const loansSection = document.getElementById("loans-section");
const loansBody = document.getElementById("loans-body");
const loansEmpty = document.getElementById("loans-empty");

function textCell(text) {
  const td = document.createElement("td");
  td.textContent = text; // textContent shows text only and never runs HTML
  return td;
}

function loanStatusCell(loan) {
  const td = document.createElement("td");
  const badge = document.createElement("span");
  if (loan.returned_on) {
    badge.className = "badge badge-muted";
    badge.textContent = "Returned";
  } else if (loan.is_overdue) {
    badge.className = "badge badge-out";
    badge.textContent = "Overdue";
  } else {
    badge.className = "badge badge-ok";
    badge.textContent = "Borrowed";
  }
  td.append(badge);
  return td;
}

function showAccount(account) {
  nameEl.textContent = account.name;
  emailEl.textContent = account.email;

  statusEl.hidden = false;
  if (account.status === "member") {
    statusEl.className = "badge badge-ok";
    statusEl.textContent = "Member";
    noteEl.textContent = "You can borrow books at the library desk.";
  } else {
    statusEl.className = "badge badge-muted";
    statusEl.textContent = "Pending approval";
    noteEl.textContent = "Library staff will review your request. You can borrow once you are approved.";
  }

  loansSection.hidden = false;
  loansBody.replaceChildren();
  loansEmpty.hidden = account.loans.length > 0;
  for (const loan of account.loans) {
    const row = document.createElement("tr");
    row.append(
      textCell(loan.book_title),
      textCell(loan.issued_on),
      textCell(loan.due_on),
      loanStatusCell(loan)
    );
    loansBody.append(row);
  }
}

async function loadAccount() {
  try {
    const response = await fetch("/api/my/account");
    if (response.status === 401) {
      window.location.href = "/login.html";
      return;
    }
    if (response.status === 404) {
      messageEl.textContent =
        "No membership is linked to this browser. If you joined on another device or " +
        "browser, ask at the library desk. Otherwise you can join the library first.";
      return;
    }
    if (!response.ok) throw new Error("request failed");
    showAccount(await response.json());
  } catch (error) {
    messageEl.textContent = "Could not load your account. Please try again.";
  }
}

loadAccount();
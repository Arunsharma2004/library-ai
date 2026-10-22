// Page behavior for the borrowing screen.
// Uses booksApi, membersApi and borrowsApi from api.js.

const issueForm = document.getElementById("issue-form");
const bookSelect = document.getElementById("book-select");
const memberSelect = document.getElementById("member-select");
const statusFilter = document.getElementById("status-filter");
const loansBody = document.getElementById("loans-body");
const emptyState = document.getElementById("empty-state");
const messageBox = document.getElementById("message");

function showMessage(text, type = "") {
  messageBox.textContent = text;
  messageBox.className = type;
}

// ---------- The two drop-down lists ----------
function fillSelect(select, placeholder, items, labelOf) {
  select.replaceChildren();
  const first = document.createElement("option");
  first.value = "";
  first.textContent = placeholder;
  select.append(first);

  for (const item of items) {
    const option = document.createElement("option");
    option.value = item.id;
    option.textContent = labelOf(item);
    select.append(option);
  }
}

// Only books with copies left and active members can be chosen.
async function loadChoices() {
  const [books, members] = await Promise.all([
    booksApi.list({ availableOnly: true }),
    membersApi.list({ activeOnly: true }),
  ]);
  fillSelect(bookSelect, "Choose a book...", books,
    (b) => `${b.title} (${b.available_copies} available)`);
  fillSelect(memberSelect, "Choose a member...", members, (m) => m.name);
}

// ---------- The loans table ----------
async function loadLoans() {
  const loans = await borrowsApi.list({ status: statusFilter.value });
  renderLoans(loans);
}

function renderLoans(loans) {
  loansBody.replaceChildren();
  emptyState.hidden = loans.length > 0;

  for (const loan of loans) {
    const row = document.createElement("tr");
    row.append(
      cell(loan.book_title),
      cell(loan.member_name),
      cell(loan.issued_on),
      cell(loan.due_on),
      cell(loan.returned_on || "-"),
      statusCell(loan),
      actionsCell(loan)
    );
    loansBody.append(row);
  }
}

function cell(text) {
  const td = document.createElement("td");
  td.textContent = text; // text only, never runs HTML
  return td;
}

function statusCell(loan) {
  let label = "Borrowed";
  let style = "badge-ok";
  if (loan.returned_on) {
    label = "Returned";
    style = "badge-muted";
  } else if (loan.is_overdue) {
    label = "Overdue";
    style = "badge-out";
  }

  const td = document.createElement("td");
  const badge = document.createElement("span");
  badge.className = "badge " + style;
  badge.textContent = label;
  td.append(badge);
  return td;
}

function actionsCell(loan) {
  const td = document.createElement("td");
  td.className = "actions";
  if (loan.returned_on) {
    return td; // nothing to do for a returned book
  }

  const button = document.createElement("button");
  button.type = "button";
  button.className = "btn-secondary btn-small";
  button.textContent = "Return";
  button.addEventListener("click", () => returnLoan(loan));
  td.append(button);
  return td;
}

// ---------- Actions ----------
async function refresh() {
  await Promise.all([loadChoices(), loadLoans()]);
}

async function returnLoan(loan) {
  try {
    await borrowsApi.returnBook(loan.id);
    await refresh();
    showMessage(`"${loan.book_title}" returned.`, "success");
  } catch (error) {
    showMessage(error.message, "error");
  }
}

issueForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    const loan = await borrowsApi.issue(
      Number(bookSelect.value),
      Number(memberSelect.value)
    );
    await refresh();
    showMessage(`"${loan.book_title}" issued to ${loan.member_name}. Due ${loan.due_on}.`, "success");
  } catch (error) {
    showMessage(error.message, "error");
  }
});

statusFilter.addEventListener("change", async () => {
  try {
    await loadLoans();
  } catch (error) {
    showMessage(error.message, "error");
  }
});

refresh().catch((error) => showMessage(error.message, "error"));
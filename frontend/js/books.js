// Page behavior for the books screen.
// It never calls fetch directly. It uses booksApi from api.js.

const searchInput = document.getElementById("search-input");
const categoryInput = document.getElementById("category-input");
const availableOnly = document.getElementById("available-only");
const booksBody = document.getElementById("books-body");
const emptyState = document.getElementById("empty-state");
const messageBox = document.getElementById("message");

function showMessage(text, type = "") {
  messageBox.textContent = text;
  messageBox.className = type; // "error" or "success" (styled in the CSS)
}

// Reads the current values of the search box, category box and checkbox.
function currentFilters() {
  return {
    search: searchInput.value.trim(),
    category: categoryInput.value.trim(),
    availableOnly: availableOnly.checked,
  };
}

async function loadBooks() {
  try {
    const books = await booksApi.list(currentFilters());
    renderBooks(books);
    showMessage("");
  } catch (error) {
    showMessage(error.message, "error");
  }
}

function renderBooks(books) {
    booksBody.replaceChildren(); // remove the old rows
  emptyState.hidden = books.length > 0;

  for (const book of books) {
    const row = document.createElement("tr");
    row.append(
      cell(book.title),
      cell(book.author),
      cell(book.isbn || "-"),
      cell(book.category || "-"),
      availabilityCell(book),
      actionsCell(book)
    );
    booksBody.append(row);
  }
}
function cell(text) {
  const td = document.createElement("td");
  td.textContent = text; // textContent shows text only and never runs HTML
  return td;
}

function availabilityCell(book) {
  const td = document.createElement("td");
  const badge = document.createElement("span");
  badge.className = "badge " + (book.available_copies > 0 ? "badge-ok" : "badge-out");
  badge.textContent = `${book.available_copies} / ${book.total_copies}`;
  td.append(badge);
  return td;
}

function availabilityCell(book) {
  const td = document.createElement("td");
  const badge = document.createElement("span");
  badge.className = "badge " + (book.available_copies > 0 ? "badge-ok" : "badge-out");
  badge.textContent = `${book.available_copies} / ${book.total_copies}`;
  td.append(badge);
  return td;
}

function actionsCell(book) {
  const td = document.createElement("td");
  td.className = "actions";

  const editButton = document.createElement("button");
  editButton.type = "button";
  editButton.className = "btn-secondary btn-small";
  editButton.textContent = "Edit";
  editButton.addEventListener("click", () => openDialog(book));

  const deleteButton = document.createElement("button");
  deleteButton.type = "button";
  deleteButton.className = "btn-danger btn-small";
  deleteButton.textContent = "Delete";
  deleteButton.addEventListener("click", () => deleteBook(book));

  td.append(editButton, deleteButton);
  return td;
}

async function deleteBook(book) {
  if (!confirm(`Delete "${book.title}"? This cannot be undone.`)) {
    return;
  }
  try {
    await booksApi.remove(book.id);
    await loadBooks();
    showMessage("Book deleted.", "success");
  } catch (error) {
    showMessage(error.message, "error");
  }
}
// Reload the list when a filter changes. For typing we wait 300 ms after the
// last keystroke, so we don't send a request for every single letter.
let filterTimer;
function onFilterChange() {
  clearTimeout(filterTimer);
  filterTimer = setTimeout(loadBooks, 300);
}
searchInput.addEventListener("input", onFilterChange);
categoryInput.addEventListener("input", onFilterChange);
availableOnly.addEventListener("change", loadBooks);

// ---------- Add / edit form ----------
const dialog = document.getElementById("book-dialog");
const form = document.getElementById("book-form");
const dialogTitle = document.getElementById("dialog-title");
const formError = document.getElementById("form-error");

let editingId = null; // null = adding a new book, a number = editing that book

function openDialog(book = null) {
  editingId = book ? book.id : null;
  dialogTitle.textContent = book ? "Edit book" : "Add book";
  form.reset();
  formError.textContent = "";

  if (book) {
    // Used by the Edit button, which we add in the next step.
    document.getElementById("title").value = book.title;
    document.getElementById("author").value = book.author;
    document.getElementById("isbn").value = book.isbn || "";
    document.getElementById("category").value = book.category || "";
    document.getElementById("published-year").value = book.published_year || "";
    document.getElementById("total-copies").value = book.total_copies;
    document.getElementById("description").value = book.description || "";
  }
  dialog.showModal();
}

// The API wants null for an empty optional field, not an empty string.
function emptyToNull(value) {
  const trimmed = value.trim();
  return trimmed === "" ? null : trimmed;
}

function readForm() {
  const year = document.getElementById("published-year").value;
  return {
    title: document.getElementById("title").value,
    author: document.getElementById("author").value,
    isbn: emptyToNull(document.getElementById("isbn").value),
    category: emptyToNull(document.getElementById("category").value),
    published_year: year === "" ? null : Number(year),
    total_copies: Number(document.getElementById("total-copies").value),
    description: emptyToNull(document.getElementById("description").value),
  };
}

form.addEventListener("submit", async (event) => {
  event.preventDefault(); // stop the browser from reloading the page
  const wasAdding = editingId === null;
  try {
    if (wasAdding) {
      await booksApi.create(readForm());
    } else {
      await booksApi.update(editingId, readForm());
    }
    dialog.close();
    await loadBooks();
    showMessage(wasAdding ? "Book added." : "Book updated.", "success");
  } catch (error) {
    formError.textContent = error.message; // shown inside the form
  }
});

document.getElementById("add-book-btn").addEventListener("click", () => openDialog());
document.getElementById("cancel-btn").addEventListener("click", () => dialog.close());

loadBooks(); // load the books when the page opens
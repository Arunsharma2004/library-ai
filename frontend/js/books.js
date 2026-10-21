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
      cell("") // the Edit / Delete buttons will go here later
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

loadBooks(); // load the books when the page opens
// All communication with the backend lives in this file.
const API_BASE = "/api";

// Sends one request and returns the parsed JSON (or null for "204 No Content").
// If anything goes wrong it throws an Error with a readable message.
async function request(path, options = {}) {
  let response;
  try {
    response = await fetch(API_BASE + path, {
      headers: { "Content-Type": "application/json" },
      ...options,
    });
  } catch (networkError) {
    throw new Error("Cannot reach the server. Is it running?");
  }

  if (response.status === 204) {
    return null;
  }

  let data = null;
  try {
    data = await response.json();
  } catch (parseError) {
    // the response had no JSON body
  }

  if (!response.ok) {
    throw new Error(errorMessage(data, response.status));
  }
  return data;
}

// Turns the backend's error format into one readable sentence.
function errorMessage(data, status) {
  if (data && typeof data.detail === "string") {
    return data.detail;                      // 404 and 409 errors
  }
  if (data && Array.isArray(data.detail)) {  // 422 validation errors
    return data.detail
      .map((e) => `${e.loc.slice(1).join(".")}: ${e.msg}`)
      .join("; ");
  }
  return `Request failed (${status})`;
}

// One function per endpoint of the books API.
const booksApi = {
  list(filters = {}) {
    const params = new URLSearchParams();
    if (filters.search) params.set("search", filters.search);
    if (filters.category) params.set("category", filters.category);
    if (filters.availableOnly) params.set("available_only", "true");
    const query = params.toString();
    return request("/books" + (query ? "?" + query : ""));
  },

  create(book) {
    return request("/books", { method: "POST", body: JSON.stringify(book) });
  },

  update(id, changes) {
    return request(`/books/${id}`, { method: "PATCH", body: JSON.stringify(changes) });
  },

  remove(id) {
    return request(`/books/${id}`, { method: "DELETE" });
  },
};

const membersApi = {
  list(filters = {}) {
    const params = new URLSearchParams();
    if (filters.search) params.set("search", filters.search);
    if (filters.activeOnly) params.set("active_only", "true");
    const query = params.toString();
    return request("/members" + (query ? "?" + query : ""));
  },

  create(member) {
    return request("/members", { method: "POST", body: JSON.stringify(member) });
  },

  update(id, changes) {
    return request(`/members/${id}`, { method: "PATCH", body: JSON.stringify(changes) });
  },

  remove(id) {
    return request(`/members/${id}`, { method: "DELETE" });
  },
};

const borrowsApi = {
  list(filters = {}) {
    const params = new URLSearchParams();
    if (filters.status) params.set("status", filters.status);
    const query = params.toString();
    return request("/borrows" + (query ? "?" + query : ""));
  },

  issue(bookId, memberId) {
    return request("/borrows/issue", {
      method: "POST",
      body: JSON.stringify({ book_id: bookId, member_id: memberId }),
    });
  },

  returnBook(recordId) {
    return request(`/borrows/${recordId}/return`, { method: "POST" });
  },
};
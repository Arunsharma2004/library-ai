// Page behavior for the members screen. Uses membersApi from api.js.

const searchInput = document.getElementById("search-input");
const activeOnly = document.getElementById("active-only");
const membersBody = document.getElementById("members-body");
const emptyState = document.getElementById("empty-state");
const messageBox = document.getElementById("message");

const dialog = document.getElementById("member-dialog");
const form = document.getElementById("member-form");
const dialogTitle = document.getElementById("dialog-title");
const formError = document.getElementById("form-error");

let editingId = null; // null = adding, a number = editing that member

function showMessage(text, type = "") {
  messageBox.textContent = text;
  messageBox.className = type;
}

// ---------- List ----------
async function loadMembers() {
  try {
    const members = await membersApi.list({
      search: searchInput.value.trim(),
      activeOnly: activeOnly.checked,
    });
    renderMembers(members);
    showMessage("");
  } catch (error) {
    showMessage(error.message, "error");
  }
}

function renderMembers(members) {
  membersBody.replaceChildren();
  emptyState.hidden = members.length > 0;

  for (const member of members) {
    const row = document.createElement("tr");
    row.append(
      cell(member.name),
      cell(member.email),
      cell(member.phone || "-"),
      statusCell(member),
      actionsCell(member)
    );
    membersBody.append(row);
  }
}

function cell(text) {
  const td = document.createElement("td");
  td.textContent = text; // text only, never runs HTML
  return td;
}

function statusCell(member) {
  const td = document.createElement("td");
  const badge = document.createElement("span");
  badge.className = "badge " + (member.is_active ? "badge-ok" : "badge-out");
  badge.textContent = member.is_active ? "Active" : "Inactive";
  td.append(badge);
  return td;
}

function actionsCell(member) {
  const td = document.createElement("td");
  td.className = "actions";

  const editButton = document.createElement("button");
  editButton.type = "button";
  editButton.className = "btn-secondary btn-small";
  editButton.textContent = "Edit";
  editButton.addEventListener("click", () => openDialog(member));

  const deleteButton = document.createElement("button");
  deleteButton.type = "button";
  deleteButton.className = "btn-danger btn-small";
  deleteButton.textContent = "Delete";
  deleteButton.addEventListener("click", () => deleteMember(member));

  td.append(editButton, deleteButton);
  return td;
}

async function deleteMember(member) {
  if (!confirm(`Delete "${member.name}"? This cannot be undone.`)) {
    return;
  }
  try {
    await membersApi.remove(member.id);
    await loadMembers();
    showMessage("Member deleted.", "success");
  } catch (error) {
    showMessage(error.message, "error");
  }
}

// ---------- Add / edit form ----------
function openDialog(member = null) {
  editingId = member ? member.id : null;
  dialogTitle.textContent = member ? "Edit member" : "Add member";
  form.reset();
  formError.textContent = "";

  if (member) {
    document.getElementById("name").value = member.name;
    document.getElementById("email").value = member.email;
    document.getElementById("phone").value = member.phone || "";
    document.getElementById("is-active").checked = member.is_active;
  }
  dialog.showModal();
}

function readForm() {
  const phone = document.getElementById("phone").value.trim();
  return {
    name: document.getElementById("name").value,
    email: document.getElementById("email").value,
    phone: phone === "" ? null : phone, // the API wants null, not ""
    is_active: document.getElementById("is-active").checked,
  };
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const wasAdding = editingId === null;
  try {
    if (wasAdding) {
      // New members are always active, so the API doesn't take is_active here.
      const { is_active, ...newMember } = readForm();
      await membersApi.create(newMember);
    } else {
      await membersApi.update(editingId, readForm());
    }
    dialog.close();
    await loadMembers();
    showMessage(wasAdding ? "Member added." : "Member updated.", "success");
  } catch (error) {
    formError.textContent = error.message;
  }
});

document.getElementById("add-member-btn").addEventListener("click", () => openDialog());
document.getElementById("cancel-btn").addEventListener("click", () => dialog.close());

// ---------- Filters ----------
let filterTimer;
searchInput.addEventListener("input", () => {
  clearTimeout(filterTimer);
  filterTimer = setTimeout(loadMembers, 300);
});
activeOnly.addEventListener("change", loadMembers);

loadMembers(); // load the members when the page opens
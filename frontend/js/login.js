const loginForm = document.getElementById("login-form");
const formError = document.getElementById("form-error");
const loginButton = document.getElementById("login-btn");

loginForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  formError.textContent = "";
  loginButton.disabled = true; // stops double clicks while we wait

  try {
    await authApi.login(
      document.getElementById("username").value,
      document.getElementById("password").value
    );
    window.location.href = "/"; // signed in: go to the books page
  } catch (error) {
    formError.textContent = error.message;
    loginButton.disabled = false;
  }
});
import { AUTH_URL } from "./config.js";

// =============================
// AUTH HELPER FUNCTIONS
// =============================
export function getToken() {
  return localStorage.getItem("token");
}

export function setToken(token) {
  localStorage.setItem("token", token);
}

export function logout() {
  localStorage.removeItem("token");
  alert("Logged out!");
  window.location.reload();
}

export function isLoggedIn() {
  return !!localStorage.getItem("token");
}

// A reusable authorized fetch helper
export async function authRequest(endpoint, method = "GET", body = null) {
  const token = getToken();

  if (!token) throw new Error("No token found. Please login first.");

  const res = await fetch(`${AUTH_URL}${endpoint}`, {
    method,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: body ? JSON.stringify(body) : null,
  });

  if (res.status === 401) {
    logout();
    throw new Error("Session expired. Please login again.");
  }

  return res.json();
}

// =============================
// UI + LOGIN/SIGNUP HANDLERS
// =============================
document.addEventListener("DOMContentLoaded", () => {
  const modalOverlay = document.getElementById("modalOverlay");
  const emailInput = document.getElementById("emailInput");
  const passwordInput = document.getElementById("passwordInput");
  const nameInput = document.getElementById("nameInput");
  const primaryBtn = document.getElementById("primaryAuthBtn");
  const switchBtn = document.getElementById("switchBtn");
  const googleAuthBtn = document.getElementById("googleAuthBtn");

  let isLogin = true;

  // Show modal if not logged in
  if (!isLoggedIn()) {
    modalOverlay.classList.remove("hidden");
    disableChatUi();
  }

  // Switch between login/signup UI
  switchBtn.addEventListener("click", () => {
    isLogin = !isLogin;
    document.querySelector(".modal-title").textContent = isLogin
      ? "Sign In"
      : "Create Account";
    document.querySelector(".modal-subtitle").textContent = isLogin
      ? "Enter your credentials"
      : "Create an account";
    primaryBtn.textContent = isLogin ? "Login" : "Sign Up";
    nameInput.classList.toggle("hidden", isLogin);
    switchBtn.textContent = isLogin ? "Create Account" : "Login";
    document.getElementById("switchText").textContent = isLogin
      ? "Don't have an account?"
      : "Already have an account?";
  });

  // MAIN ACTION (LOGIN OR SIGNUP)
  primaryBtn.addEventListener("click", async () => {
    const email = emailInput.value.trim();
    const password = passwordInput.value.trim();
    const username = nameInput.value.trim();

    if (!email || !password || (!isLogin && !username)) {
      alert("Please fill out all fields");
      return;
    }

    const endpoint = isLogin ? "/login" : "/signup";
    const payload = isLogin
      ? { email, password }
      : { username, email, password };

    try {
      const res = await fetch(`${AUTH_URL}${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Authentication failed");

      if (isLogin) {
        setToken(data.access_token);
        alert("Logged in successfully!");
        modalOverlay.classList.add("hidden");
        enableChatUi();
      } else {
        alert("Signup successful! Please login.");
        switchBtn.click();
      }

      emailInput.value = "";
      passwordInput.value = "";
      nameInput.value = "";
    } catch (err) {
      alert(err.message);
    }
  });

  googleAuthBtn.addEventListener("click", () => {
    window.location.href = `${AUTH_URL}/google`;
  });
});

// =============================
// CHAT LOCK / UNLOCK
// =============================
function disableChatUi() {
  const userInput = document.getElementById("userInput");
  const sendBtn = document.getElementById("sendBtn");
  const recBtn = document.getElementById("recordBtn");

  if (userInput) userInput.disabled = true;
  if (sendBtn) sendBtn.disabled = true;
  if (recBtn) recBtn.disabled = true;
}

function enableChatUi() {
  const userInput = document.getElementById("userInput");
  const sendBtn = document.getElementById("sendBtn");
  const recBtn = document.getElementById("recordBtn");

  if (userInput) userInput.disabled = false;
  if (sendBtn) sendBtn.disabled = false;
  if (recBtn) recBtn.disabled = false;
}

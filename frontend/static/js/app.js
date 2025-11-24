import { BACKEND_URL } from "./config.js";
import { getToken, isLoggedIn } from "./auth.js";

// =============================
// DOM ELEMENTS
// =============================
const sendBtn = document.getElementById("sendBtn");
const resetBtn = document.getElementById("resetBtn");
const recordBtn = document.getElementById("recordBtn");
const userInput = document.getElementById("userInput");
const chatArea = document.getElementById("chatArea");
const personaSelect = document.getElementById("personaselect");

let selectedPersona = "default";
let recognition = null;

// =============================
// API ENDPOINT
// =============================
const API_URL = `${BACKEND_URL}/speak`;

// =============================
// CHECK IF LOGGED IN
// =============================
if (!isLoggedIn()) {
  disableChat();
} else {
  enableChat();
}

// =============================
// EVENT LISTENERS
// =============================
sendBtn?.addEventListener("click", () => sendMessage());

userInput?.addEventListener("keypress", (e) => {
  if (e.key === "Enter") sendMessage();
});

resetBtn?.addEventListener("click", () => {
  chatArea.innerHTML = "";
});

personaSelect?.addEventListener("change", (e) => {
  selectedPersona = e.target.value;
});

// =============================
// SPEECH RECOGNITION (Optional)
// =============================
if ("webkitSpeechRecognition" in window || "SpeechRecognition" in window) {
  const SpeechRecognition =
    window.SpeechRecognition || window.webkitSpeechRecognition;

  recognition = new SpeechRecognition();
  recognition.lang = "en-US";
  recognition.interimResults = false;
  recognition.maxAlternatives = 1;

  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    appendMessage(transcript, "user");
    sendMessage(transcript);
  };

  recognition.onerror = (event) => console.error("Voice error:", event.error);

  recognition.onend = () => {
    if (recordBtn) recordBtn.textContent = "Start Recording";
  };
}

recordBtn?.addEventListener("click", () => {
  if (!recognition) return;
  recognition.start();
  recordBtn.textContent = "Listening...";
});

// =============================
// SEND CHAT MESSAGE TO BACKEND
// =============================
async function sendMessage(textOverride = null) {
  if (!isLoggedIn()) {
    alert("Please login first.");
    return;
  }

  const text = textOverride || userInput.value.trim();
  if (!text) return;

  if (!textOverride) appendMessage(text, "user");
  userInput.value = "";

  const thinkingMsg = appendMessage("Thinking...", "bot");

  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${getToken()}`,
      },
      body: JSON.stringify({ text, persona: selectedPersona }),
    });

    if (!response.ok) {
      updateBotMessage(thinkingMsg, "Error: Could not process request.");
      return;
    }

    const data = await response.json();

    if (data.audio_url) {
      updateBotMessage(thinkingMsg, "Yuna says:");
      appendAudio(data.audio_url);
    } else if (data.reply) {
      updateBotMessage(thinkingMsg, data.reply);
    } else {
      updateBotMessage(thinkingMsg, "No response from backend.");
    }
  } catch (error) {
    console.error("Chat error:", error);
    updateBotMessage(thinkingMsg, "⚠ Backend error. Try again.");
  }
}

// =============================
// UI HELPERS
// =============================
function appendMessage(text, sender) {
  const msg = document.createElement("div");
  msg.className = `message ${sender === "user" ? "user-msg" : "bot-msg"}`;
  msg.textContent = text;
  chatArea.appendChild(msg);
  chatArea.scrollTop = chatArea.scrollHeight;
  return msg;
}

function updateBotMessage(msgElement, newText) {
  if (msgElement) msgElement.textContent = newText;
  chatArea.scrollTop = chatArea.scrollHeight;
}

function appendAudio(audioPath) {
  const audioContainer = document.createElement("div");
  audioContainer.className = "message bot-msg";

  const audio = document.createElement("audio");
  audio.controls = true;
  audio.src = `${BACKEND_URL}${audioPath}`;

  audioContainer.appendChild(audio);
  chatArea.appendChild(audioContainer);
  chatArea.scrollTop = chatArea.scrollHeight;
}

// =============================
// CHAT DISABLE/ENABLE (Used by auth.js)
// =============================
export function disableChat() {
  if (userInput) userInput.disabled = true;
  if (sendBtn) sendBtn.disabled = true;
  if (recordBtn) recordBtn.disabled = true;
}

export function enableChat() {
  if (userInput) userInput.disabled = false;
  if (sendBtn) sendBtn.disabled = false;
  if (recordBtn) recordBtn.disabled = false;
}

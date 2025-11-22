const sendBtn = document.getElementById("sendBtn");
const resetBtn = document.getElementById("resetBtn");
const recordBtn = document.getElementById("recordBtn");
const userInput = document.getElementById("userInput");
const chatArea = document.getElementById("chatArea");

const API_URL = "http://localhost:8000/speak";

// ---- Button events ----
sendBtn.addEventListener("click", () => sendMessage());
userInput.addEventListener("keypress", (e) => {
  if (e.key === "Enter") sendMessage();
});
resetBtn.addEventListener("click", () => (chatArea.innerHTML = ""));


// ---- Speech Recognition ----
let recognition;
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

  recognition.onerror = (event) => {
    console.error("Speech recognition error:", event.error);
  };

  recognition.onend = () => {
    recordBtn.textContent = "Start Recording";
  };
} else {
  alert("Speech Recognition not supported in this browser.");
}

// ---- Start/Stop Recording ----
recordBtn.addEventListener("click", () => {
  if (!recognition) return;
  recognition.start();
  recordBtn.textContent = "Listening...";
});

// ---- Send message ----
async function sendMessage(textOverride) {
  const text = textOverride || userInput.value.trim();
  if (!text) return;

  if (!textOverride) appendMessage(text, "user");
  userInput.value = "";

  const thinkingMsg = appendMessage("Thinking...", "bot");

  try {
    const res = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    });

    if (!res.ok) {
      const errText = await res.text();
      throw new Error(`Server returned ${res.status}: ${errText}`);
    }

    const data = await res.json();

    if (data.audio_url) {
      updateLastBotMessage("Yuna says:");
      appendBotMessage("Yuna says:", data.audio_url);
    } else {
      updateLastBotMessage("⚠ No audio returned from backend.");
    }
  } catch (err) {
    updateLastBotMessage("❌ Error communicating with backend");
    console.error("Fetch error:", err);
  }
}

// ---- Helpers ----
function appendMessage(text, sender) {
  const msg = document.createElement("div");
  msg.className = `message ${sender === "user" ? "user-msg" : "bot-msg"}`;
  msg.textContent = text;
  chatArea.appendChild(msg);
  chatArea.scrollTop = chatArea.scrollHeight;
  return msg;
}

function updateLastBotMessage(text) {
  const msgs = chatArea.getElementsByClassName("bot-msg");
  if (msgs.length) msgs[msgs.length - 1].textContent = text;
  else appendMessage(text, "bot");
}

// Append bot message with inline audio
function appendBotMessage(text, audioFile) {
  const msg = document.createElement("div");
  msg.className = "message bot-msg";

  const textEl = document.createElement("span");
  textEl.textContent = text;
  msg.appendChild(textEl);

  if (audioFile) {
    const audio = document.createElement("audio");
    audio.controls = true;
    audio.src = `http://localhost:8000${audioFile}`;
    audio.style.marginTop = "4px";
    msg.appendChild(audio);
  }

  chatArea.appendChild(msg);
  chatArea.scrollTop = chatArea.scrollHeight;
}

const moodLabels = {
  1: "Very low",
  2: "Low",
  3: "Neutral",
  4: "Good",
  5: "Very good",
};

const suggestions = [
  "Take a short break from your current task.",
  "Write down one small task you can finish next.",
  "Listen to a song you enjoy.",
  "Pause for a few comfortable, slow breaths.",
  "Consider checking in with someone you trust.",
];

let suggestionIndex = 0;
let messages = [];

function localToday() {
  const now = new Date();
  return new Date(now.getTime() - now.getTimezoneOffset() * 60000)
    .toISOString()
    .slice(0, 10);
}

async function api(path, options = {}) {
  const response = await fetch(path, options);
  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || "The request failed.");
  }

  return data;
}

function setMoodFormDefaults() {
  document.getElementById("entry-date").value = localToday();
}

function renderMoods(moods) {
  const container = document.getElementById("mood-report");
  const recent = moods.slice(-7);

  if (recent.length === 0) {
    container.innerHTML = "<p>No entries yet.</p>";
    return;
  }

  container.innerHTML = recent
    .map((entry) => {
      return (
        '<div class="chart-row">' +
        `<span>${entry.entry_date}</span>` +
        '<div class="track"><div class="bar" ' +
        `style="width: ${entry.mood_score * 20}%"></div></div>` +
        `<span>${entry.mood_score}/5 — ${moodLabels[entry.mood_score]}</span>` +
        "</div>"
      );
    })
    .join("");
}

async function loadMoods() {
  try {
    const data = await api("/api/moods");
    renderMoods(data.moods);
  } catch (error) {
    document.getElementById("mood-status").textContent = error.message;
  }
}

async function saveMood() {
  const status = document.getElementById("mood-status");
  status.textContent = "";

  try {
    await api("/api/moods", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        entry_date: document.getElementById("entry-date").value,
        mood_score: Number(document.getElementById("mood-score").value),
        note: document.getElementById("mood-note").value,
      }),
    });

    document.getElementById("mood-note").value = "";
    status.textContent = "Mood saved successfully.";
    await loadMoods();
  } catch (error) {
    status.textContent = error.message;
  }
}

async function clearMoods() {
  if (!window.confirm("Delete all mood entries in this demo?")) return;

  try {
    await api("/api/moods", { method: "DELETE" });
    await loadMoods();
  } catch (error) {
    document.getElementById("mood-status").textContent = error.message;
  }
}

function renderMessages() {
  const container = document.getElementById("chat-log");

  if (messages.length === 0) {
    container.innerHTML =
      "<p>Try: “I feel overwhelmed by my assignments.”</p>";
    return;
  }

  container.innerHTML = messages
    .map((message) => {
      const speaker = message.role === "user" ? "You" : "CampusWell";

      return (
        `<div class="message ${message.role}">` +
        `<span class="speaker">${speaker}</span>` +
        `<p>${message.content.replace(/</g, "&lt;")}</p>` +
        "</div>"
      );
    })
    .join("");
}

async function sendMessage() {
  const input = document.getElementById("chat-message");
  const status = document.getElementById("chat-status");
  const text = input.value.trim();

  if (!text) return;

  const next = [...messages, { role: "user", content: text }];
  messages = next;
  input.value = "";
  status.textContent = "Sending...";
  renderMessages();

  try {
    const data = await api("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ messages: next.slice(-11) }),
    });

    messages = [...next, { role: "assistant", content: data.reply }];
    status.textContent = "";
  } catch (error) {
    messages = next.slice(0, -1);
    status.textContent = error.message;
  }

  renderMessages();
}

function showSuggestion() {
  document.getElementById("suggestion").textContent =
    suggestions[suggestionIndex];
}

document.addEventListener("DOMContentLoaded", () => {
  setMoodFormDefaults();
  showSuggestion();
  loadMoods();

  document.getElementById("save-mood").addEventListener("click", saveMood);
  document.getElementById("clear-moods").addEventListener("click", clearMoods);
  document.getElementById("send-chat").addEventListener("click", sendMessage);
  document
    .getElementById("new-suggestion")
    .addEventListener("click", () => {
      suggestionIndex = (suggestionIndex + 1) % suggestions.length;
      showSuggestion();
    });

  document
    .getElementById("chat-message")
    .addEventListener("keydown", (event) => {
      if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
      }
    });
});

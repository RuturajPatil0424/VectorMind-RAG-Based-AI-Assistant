const chat = document.getElementById("chat");
const queryInput = document.getElementById("query");

// function addMessage(text, type) {
//   const div = document.createElement("div");
//   div.className = `message ${type}`;
//   div.textContent = text;
//   chat.appendChild(div);
//   chat.scrollTop = chat.scrollHeight;
// }



/* Auto-grow textarea */
queryInput.addEventListener("input", () => {
  queryInput.style.height = "52px"; // reset
  const newHeight = Math.min(queryInput.scrollHeight, 50);
  queryInput.style.height = newHeight + "px";
});
function toggleTheme() {
  document.body.classList.toggle("light-theme");

  // Save preference
  localStorage.setItem(
    "theme",
    document.body.classList.contains("light-theme") ? "light" : "dark"
  );
}

// Load theme on refresh
window.onload = () => {
  if (localStorage.getItem("theme") === "light") {
    document.body.classList.add("light-theme");
  }
};
async function ask() {
  const query = queryInput.value.trim();
  if (!query) return;

  // UI: show user message
  addMessage(query, "user");
  queryInput.value = "";
  queryInput.style.height = "52px";

  // Read sidebar values
  const model = document.getElementById("model").value;
  const rag = document.getElementById("rag").checked;
  const streaming = document.getElementById("stream").checked;

  try {
    const res = await fetch("/ask", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        query: query,
        model: model,
        rag: rag,
        streaming: streaming
      })
    });

    const data = await res.json();
    
    // ✅ UPDATE MODEL NAME FROM BACKEND RESPONSE
    if (data.ai_name) {
      document.getElementById("ai-name").textContent = data.ai_name;
    }

    // UI: show AI message
    addMessage(data.answer, "ai");

  } catch (err) {
    addMessage("❌ Error connecting to server", "ai");
    console.error(err);
  }
}

queryInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    ask();
  }
});

function addMessage(text, type) {
  const message = document.createElement("div");
  message.className = `message ${type}`;

  const content = document.createElement("div");
  content.className = "message-content";
  content.textContent = text;

  const copyBtn = document.createElement("button");
  copyBtn.className = "copy-btn";
  copyBtn.innerHTML = "📋";

  copyBtn.onclick = () => {
    navigator.clipboard.writeText(text);
    copyBtn.innerHTML = "✓";
    setTimeout(() => (copyBtn.innerHTML = "📋"), 1200);
  };

  message.appendChild(content);
  message.appendChild(copyBtn);

  chat.appendChild(message);
  chat.scrollTop = chat.scrollHeight;
}

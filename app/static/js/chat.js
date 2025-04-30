document.addEventListener("DOMContentLoaded", () => {
  const chatWindow = document.getElementById("chat-window");
  const chatInput = document.getElementById("chat-input");
  const sendBtn = document.getElementById("send-btn");
  const suggestionsDiv = document.getElementById("suggestions");
  const sourcesDiv = document.getElementById("sources");
  const toolsBox = document.getElementById("tools-box");
  const toolsJson = document.getElementById("tools-json");
  const toolCardsDiv = document.getElementById("tool-cards");
  const preloadDiv = document.getElementById("preloaded-questions");

  const settingsBtn = document.getElementById("settings-btn");
  const toolboxPanel = document.getElementById("toolbox-panel");
  const backdrop = document.getElementById("backdrop");
  const closeToolboxBtn = document.getElementById("close-toolbox");
  const mainContent = document.getElementById("main-content");

  const markdown = window.marked;

  settingsBtn.onclick = () => {
    toolboxPanel.classList.add("open");
    backdrop.classList.remove("hidden");
    mainContent.classList.add("blur");
  };

  closeToolboxBtn.onclick = () => {
    toolboxPanel.classList.remove("open");
    backdrop.classList.add("hidden");
    mainContent.classList.remove("blur");
  };

  backdrop.onclick = () => {
    toolboxPanel.classList.remove("open");
    backdrop.classList.add("hidden");
    mainContent.classList.remove("blur");
  };

  function showToast(message) {
    let toast = document.getElementById("toast");
    if (!toast) {
      toast = document.createElement("div");
      toast.id = "toast";
      toast.className = "toast";
      document.body.appendChild(toast);
    }
    toast.textContent = message;
    toast.classList.add("show");
    setTimeout(() => {
      toast.classList.remove("show");
    }, 2500);
  }

  function saveSettings() {
    const settings = {
      return_sources: document.getElementById("return_sources").checked,
      return_follow_up_questions: document.getElementById("return_follow_ups").checked,
      embed_sources_in_llm_response: document.getElementById("embed_sources").checked,
      text_chunk_size: document.getElementById("text_chunk_size").value,
      text_chunk_overlap: document.getElementById("text_chunk_overlap").value,
      number_of_similarity_results: document.getElementById("number_of_similarity_results").value,
      number_of_pages_to_scan: document.getElementById("number_of_pages_to_scan").value,
      stream_mode: document.getElementById("stream_mode").checked,
    };
    localStorage.setItem("chat_settings", JSON.stringify(settings));
    showToast("Settings saved ✅");
  }

  function loadSettings() {
    const saved = JSON.parse(localStorage.getItem("chat_settings"));
    if (saved) {
      document.getElementById("return_sources").checked = saved.return_sources;
      document.getElementById("return_follow_ups").checked = saved.return_follow_up_questions;
      document.getElementById("embed_sources").checked = saved.embed_sources_in_llm_response;
      document.getElementById("text_chunk_size").value = saved.text_chunk_size;
      document.getElementById("text_chunk_overlap").value = saved.text_chunk_overlap;
      document.getElementById("number_of_similarity_results").value = saved.number_of_similarity_results;
      document.getElementById("number_of_pages_to_scan").value = saved.number_of_pages_to_scan;
      document.getElementById("stream_mode").checked = saved.stream_mode;
    }
  }

  function resetSettings() {
    document.getElementById("return_sources").checked = true;
    document.getElementById("return_follow_ups").checked = true;
    document.getElementById("embed_sources").checked = false;
    document.getElementById("text_chunk_size").value = 1000;
    document.getElementById("text_chunk_overlap").value = 200;
    document.getElementById("number_of_similarity_results").value = 2;
    document.getElementById("number_of_pages_to_scan").value = 4;
    document.getElementById("stream_mode").checked = true;
    localStorage.removeItem("chat_settings");
    showToast("Settings reset 🔄");
  }

  document.getElementById("save-settings").onclick = saveSettings;
  document.getElementById("reset-settings").onclick = resetSettings;

  loadSettings();

  const PRELOADED = [
    "Where is Disneyland located and what is the latest news about it?",
    "Where is Apple headquarters?",
    "What is the price of iPhone 16 Pro Max?",
    "Show me latest news about OpenAI",
    "What's the weather in New York today?",
    "How do I reset my password?"
  ];

  function loadPreloaded() {
    preloadDiv.innerHTML = "";
    PRELOADED.forEach(q => {
      const btn = document.createElement("button");
      btn.className = "preloaded-btn";
      btn.textContent = q;
      btn.onclick = () => {
        sendMessage(q);
      };
      preloadDiv.appendChild(btn);
    });
  }

  loadPreloaded();

  function escapeHTML(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  function appendMessage(text, role, isHTML = false) {
    const div = document.createElement("div");
    div.className = `message ${role}`;
    const now = new Date();
    const time = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    div.innerHTML = `
      <div>${isHTML ? text : escapeHTML(text)}</div>
      <div class="timestamp">${time}</div>
    `;
    chatWindow.appendChild(div);
    scrollChatToBottom();
  }

  function showActivity(msg) {
    const el = document.getElementById("activity-log");
    el.classList.remove("hidden");
    el.textContent = msg;
  }
  

  async function sendMessage(text) {
    appendMessage(text, "user");
  
    chatInput.value = "";
    chatInput.disabled = sendBtn.disabled = true;
  
    sourcesDiv.innerHTML = "";
    toolCardsDiv.innerHTML = "";
    toolsJson.textContent = "";
    toolsBox.hidden = true;
    document.getElementById("activity-log").classList.add("hidden");
  
    // Create bot message shell
    const botDiv = document.createElement("div");
    botDiv.className = "message bot";
    const inner = document.createElement("div");
    botDiv.appendChild(inner);
    chatWindow.appendChild(botDiv);
    scrollChatToBottom();
  
    const payload = {
      message: text,
      return_sources: document.getElementById("return_sources").checked,
      return_follow_up_questions: document.getElementById("return_follow_ups").checked,
      embed_sources_in_llm_response: document.getElementById("embed_sources").checked,
      text_chunk_size: parseInt(document.getElementById("text_chunk_size").value),
      text_chunk_overlap: parseInt(document.getElementById("text_chunk_overlap").value),
      number_of_similarity_results: parseInt(document.getElementById("number_of_similarity_results").value),
      number_of_pages_to_scan: parseInt(document.getElementById("number_of_pages_to_scan").value),
      stream: true
    };
  
    const response = await fetch(window.CHAT_ENDPOINT, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
  
    const reader = response.body.getReader();
    const decoder = new TextDecoder("utf-8");
  
    let fullAnswer = "";
    let buffer = "";
    let toolOutput = null;
  
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
  
      const chunk = decoder.decode(value, { stream: true });
      buffer += chunk;
  
      while (buffer.includes("###")) {
        const markerIndex = buffer.indexOf("###");
        const nextNewline = buffer.indexOf("\n", markerIndex);
        const line = buffer.slice(markerIndex, nextNewline).trim();
  
        if (line.startsWith("###ACTIVITY###")) {
          const msg = line.replace("###ACTIVITY###", "").trim();
          showActivity(msg);
          buffer = buffer.slice(nextNewline + 1);
        } else if (line.startsWith("###TOOL_OUTPUT###")) {
          try {
            const json = buffer.slice(nextNewline).replace("###TOOL_OUTPUT###", "").trim();
            toolOutput = JSON.parse(json);
          } catch (e) {
            console.error("Failed to parse tool output");
          }
          buffer = ""; // Done processing
          break;
        } else {
          break;
        }
      }
  
      const cleanChunk = chunk
        .replace(/###ACTIVITY###.*/g, "")
        .replace(/###TOOL_OUTPUT###.*/g, "");
  
      fullAnswer += cleanChunk;
      inner.innerHTML = markdown.parse(fullAnswer);
      scrollChatToBottom();
    }
  
    // Final tool rendering
    if (toolOutput) {
      renderToolCards(toolOutput);
      renderToolsRaw(toolOutput);
    }
  
    // Load sources and follow-ups after full stream ends
    chatInput.disabled = sendBtn.disabled = false;
    chatInput.focus();
  }

  function scrollChatToBottom() {
    setTimeout(() => {
      chatWindow.scrollTo({
        top: chatWindow.scrollHeight,
        behavior: 'smooth'
      });
    }, 100);
  }

  function renderSources(sources) {
    sourcesDiv.innerHTML = "";
    if (!sources?.length) return;

    const container = document.createElement("div");
    container.className = "sources-container";
    const heading = document.createElement("div");
    heading.className = "sources-heading";
    heading.textContent = "Sources:";
    container.appendChild(heading);

    const ul = document.createElement("ul");
    ul.className = "sources-list";

    sources.forEach(s => {
      const li = document.createElement("li");
      li.innerHTML = `<a href="${s.link}" target="_blank" class="source-link">${s.title}</a>`;
      ul.appendChild(li);
    });

    container.appendChild(ul);
    sourcesDiv.appendChild(container);
  }

  function renderToolCards(tools) {
    toolCardsDiv.innerHTML = "";
    if (!tools?.length) return;

    tools.forEach(tool => {
      const card = document.createElement("div");
      const typeClass = {
        search_location: "map",
        search_shopping: "shopping",
        search_news: "news"
      }[tool.function_name] || "";

      card.className = `tool-card ${typeClass}`;

      const labelData = {
        search_location: { icon: "📍", text: "Location (Google Maps)" },
        search_shopping: { icon: "🛒", text: "Shopping Result" },
        search_news: { icon: "📰", text: "News Articles" }
      }[tool.function_name] || { icon: "🔧", text: tool.function_name };

      const header = `<div class="tool-title">
        <span>${labelData.icon}</span>${labelData.text}
      </div>`;

      let content = "";

      if (tool.function_name === "search_location") {
        content = `<a href="${tool.response.maps_url}" target="_blank" class="map-link">🌍 View on Google Maps</a>`;
      } else if (tool.function_name === "search_shopping") {
        content = `
          <div>
            <img src="${tool.response.image_url}" alt="Product" class="shopping-img" onerror="this.style.display='none';">
            <div>
              <a href="${tool.response.link}" target="_blank" class="font-bold">${tool.response.title}</a>
              <p>${tool.response.price}</p>
            </div>
          </div>
        `;
      } else if (tool.function_name === "search_news") {
        content = '<ul>';
        tool.response.articles.forEach(article => {
          content += `<li><a href="${article.link}" target="_blank">${article.title}</a> • ${article.source}</li>`;
        });
        content += '</ul>';
      } else {
        content = `<pre>${JSON.stringify(tool.response, null, 2)}</pre>`;
      }

      card.innerHTML = header + content;
      toolCardsDiv.appendChild(card);
    });
  }

  function renderFollowUps(followUps) {
    preloadDiv.innerHTML = "";
    if (!followUps?.length) return;

    followUps.forEach(fu => {
      const btn = document.createElement("button");
      btn.className = "preloaded-btn";
      btn.textContent = fu;
      btn.onclick = () => {
        sendMessage(fu);
      };
      preloadDiv.appendChild(btn);
    });
  }

  function renderToolsRaw(tools) {
    if (tools?.length) {
      toolsJson.textContent = JSON.stringify(tools, null, 2);
      toolsBox.hidden = false;
    } else {
      toolsBox.hidden = true;
    }
  }

  sendBtn.onclick = () => {
    if (chatInput.value.trim()) sendMessage(chatInput.value.trim());
  };
  chatInput.onkeydown = e => {
    if (e.key === "Enter" && chatInput.value.trim()) sendMessage(chatInput.value.trim());
  };

  document.getElementById("darkmode-toggle").onclick = () => {
    document.body.classList.toggle("dark");
  };
});

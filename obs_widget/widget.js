(() => {
  "use strict";

  const fields = ["hack", "creator", "exits", "deaths", "timer", "achievements"];
  const controls = ["search", "random"];
  const fieldStorageKey = "smw-stream-tracker-obs-widget-fields-v1";
  const controlStorageKey = "smw-stream-tracker-obs-widget-controls-v1";
  const filterStorageKey = "smw-stream-tracker-obs-widget-random-filters-v1";
  const cardElements = [...document.querySelectorAll("[data-field]")];
  const settingsButton = document.getElementById("settingsButton");
  const settingsPanel = document.getElementById("settingsPanel");
  const pickerInputs = [...document.querySelectorAll("#fieldPicker input")];
  const controlInputs = [...document.querySelectorAll("#controlPicker input")];
  const randomFilterInputs = [...document.querySelectorAll("[data-random-filter]")];
  const emptySelection = document.getElementById("emptySelection");
  const dockControls = document.getElementById("dockControls");
  const searchControl = document.getElementById("searchControl");
  const randomControl = document.getElementById("randomControl");
  const searchForm = document.getElementById("hackSearchForm");
  const searchInput = document.getElementById("hackSearchInput");
  const searchButton = document.getElementById("hackSearchButton");
  const searchResults = document.getElementById("searchResults");
  const playRandomButton = document.getElementById("playRandomButton");
  const commandStatus = document.getElementById("commandStatus");
  let selectedFields = loadSet(fieldStorageKey, fields, fields);
  let selectedControls = loadSet(controlStorageKey, controls, controls);
  let randomFilters = loadFilters();
  let liveSocket = null;
  let reconnectTimer = null;
  let reconnectDelay = 500;
  let closing = false;
  let activeSearchRequest = "";
  const pendingRequestIds = new Set();

  function loadSet(key, allowed, defaults) {
    try {
      const stored = JSON.parse(localStorage.getItem(key) || "null");
      if (Array.isArray(stored)) {
        return new Set(stored.filter((value) => allowed.includes(value)));
      }
    } catch (_error) {
      // A corrupt preference should never prevent the live panel from loading.
    }
    return new Set(defaults);
  }

  function loadFilters() {
    const defaults = { rating: "Any", difficulty: "Any", type: "Any", released: "Any", hall_of_fame: "Any" };
    try {
      const stored = JSON.parse(localStorage.getItem(filterStorageKey) || "null");
      if (stored && typeof stored === "object" && !Array.isArray(stored)) {
        Object.keys(defaults).forEach((key) => {
          if (typeof stored[key] === "string") defaults[key] = stored[key];
        });
      }
    } catch (_error) {
      // Fall back to unrestricted filters.
    }
    return defaults;
  }

  function saveSelections() {
    localStorage.setItem(fieldStorageKey, JSON.stringify([...selectedFields]));
    localStorage.setItem(controlStorageKey, JSON.stringify([...selectedControls]));
  }

  function saveFilters() {
    localStorage.setItem(filterStorageKey, JSON.stringify(randomFilters));
  }

  function applyVisibility() {
    cardElements.forEach((card) => {
      card.hidden = !selectedFields.has(card.dataset.field);
    });
    pickerInputs.forEach((input) => {
      input.checked = selectedFields.has(input.value);
    });
    controlInputs.forEach((input) => {
      input.checked = selectedControls.has(input.value);
    });
    searchControl.hidden = !selectedControls.has("search");
    randomControl.hidden = !selectedControls.has("random");
    dockControls.hidden = selectedControls.size === 0;
    document.getElementById("randomFilterSettings").classList.toggle(
      "disabled",
      !selectedControls.has("random")
    );
    emptySelection.hidden = selectedFields.size !== 0 || selectedControls.size !== 0;
  }

  function setSettingsOpen(open) {
    settingsPanel.hidden = !open;
    settingsButton.setAttribute("aria-expanded", String(open));
  }

  settingsButton.addEventListener("click", () => setSettingsOpen(settingsPanel.hidden));
  document.getElementById("doneButton").addEventListener("click", () => setSettingsOpen(false));
  document.getElementById("selectAllButton").addEventListener("click", () => {
    selectedFields = new Set(fields);
    saveSelections();
    applyVisibility();
  });
  document.getElementById("clearButton").addEventListener("click", () => {
    selectedFields = new Set();
    saveSelections();
    applyVisibility();
  });
  pickerInputs.forEach((input) => {
    input.addEventListener("change", () => {
      if (input.checked) selectedFields.add(input.value);
      else selectedFields.delete(input.value);
      saveSelections();
      applyVisibility();
    });
  });
  controlInputs.forEach((input) => {
    input.addEventListener("change", () => {
      if (input.checked) selectedControls.add(input.value);
      else selectedControls.delete(input.value);
      saveSelections();
      applyVisibility();
    });
  });

  function setText(id, value) {
    document.getElementById(id).textContent = String(value ?? "");
  }

  function setProgress(elementId, fillId, percentage) {
    const clamped = Math.max(0, Math.min(100, Number(percentage) || 0));
    const progress = document.getElementById(elementId);
    progress.setAttribute("aria-valuenow", String(Math.round(clamped)));
    document.getElementById(fillId).style.width = `${clamped}%`;
  }

  function safeBadgeUrl(value) {
    const url = String(value || "");
    if (/^\/obs-widget\/badges\/[A-Za-z0-9_-]{1,80}\.png$/.test(url)) return url;
    if (/^https:\/\/(?:media\.)?retroachievements\.org\/Badge\/[A-Za-z0-9_-]{1,80}\.png$/i.test(url)) return url;
    return "";
  }

  function achievementRow(item, className) {
    const row = document.createElement("div");
    row.className = className;
    const image = document.createElement("img");
    image.className = "achievement-badge";
    image.alt = "";
    const badgeUrl = safeBadgeUrl(item.badge_url);
    if (badgeUrl) image.src = badgeUrl;
    image.addEventListener("error", () => { image.style.visibility = "hidden"; });
    const copy = document.createElement("div");
    copy.className = "achievement-copy";
    const title = document.createElement("strong");
    title.textContent = item.title || "Achievement";
    const description = document.createElement("span");
    description.textContent = item.description || item.date || "";
    copy.append(title, description);
    const points = document.createElement("span");
    points.className = "achievement-points";
    points.textContent = `${Number(item.points) || 0} pts`;
    row.append(image, copy, points);
    return row;
  }

  function renderAchievements(achievements) {
    const summary = achievements || {};
    const ready = summary.status === "ready" && Number(summary.total) > 0;
    const readyPanel = document.getElementById("achievementReady");
    const message = document.getElementById("achievementMessage");
    const hardcore = document.getElementById("hardcorePill");
    setText("achievementGame", summary.game_title || "Waiting for a supported game");
    hardcore.hidden = !summary.hardcore;
    readyPanel.hidden = !ready;
    message.hidden = ready;
    if (!ready) {
      message.textContent = summary.message || "Play a RetroAchievements-supported game to show progress and badges.";
      return;
    }

    const unlocked = Math.max(0, Number(summary.unlocked) || 0);
    const total = Math.max(unlocked, Number(summary.total) || 0);
    const percentage = total ? (unlocked / total) * 100 : 0;
    setText("achievementProgressText", `${unlocked} / ${total} unlocked`);
    setText("achievementPercent", `${Math.round(percentage)}%`);
    setProgress("achievementProgress", "achievementProgressFill", percentage);

    const nextHost = document.getElementById("nextAchievement");
    nextHost.replaceChildren();
    nextHost.hidden = !summary.next;
    if (summary.next) {
      const row = achievementRow(summary.next, "next-achievement-row");
      nextHost.append(...row.childNodes);
    }

    const recent = Array.isArray(summary.recent) ? summary.recent.slice(0, 4) : [];
    const recentHost = document.getElementById("recentAchievements");
    const recentHeading = document.getElementById("recentHeading");
    recentHost.replaceChildren();
    recentHeading.hidden = recent.length === 0;
    recent.forEach((item) => recentHost.append(achievementRow(item, "recent-achievement")));
  }

  function render(data) {
    setText("hackValue", data.hack || "No game detected");
    setText("creatorValue", data.creator || "Unknown");
    const exits = data.exits || {};
    setText("exitsValue", exits.label || "0 / Unknown");
    const exitPercent = Number.isFinite(exits.total) && exits.total > 0
      ? (Number(exits.completed) / exits.total) * 100
      : 0;
    setProgress("exitProgress", "exitProgressFill", exitPercent);
    const deaths = data.deaths || {};
    setText("gameDeathsValue", Number(deaths.total) || 0);
    setText("levelDeathsValue", Number(deaths.level) || 0);
    const timers = data.timers || {};
    setText("gameTimerValue", timers.game || "00:00");
    setText("levelTimerValue", timers.level || "00:00");
    renderAchievements(data.achievements);

    const connection = document.getElementById("connectionState");
    connection.classList.remove("offline");
    connection.classList.add("connected");
    setText("connectionText", data.connected ? "Live from app" : "Connected to app");
    setText("lastUpdate", `Updated ${new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" })}`);
  }

  function filterSummary() {
    const hall = randomFilters.hall_of_fame === "Any"
      ? "Any Hall of Fame status"
      : `Hall of Fame: ${randomFilters.hall_of_fame}`;
    setText(
      "filterSummary",
      `${randomFilters.rating} rating · ${randomFilters.difficulty} difficulty · ${randomFilters.type} type · ${randomFilters.released} · ${hall}`
    );
  }

  function populateFilter(name, values) {
    const selectElement = document.querySelector(`[data-random-filter="${name}"]`);
    const options = Array.isArray(values) && values.length ? values : ["Any"];
    selectElement.replaceChildren();
    options.forEach((value) => {
      const option = document.createElement("option");
      option.value = String(value);
      option.textContent = String(value);
      selectElement.append(option);
    });
    const wanted = String(randomFilters[name] || "Any");
    selectElement.value = options.map(String).includes(wanted) ? wanted : "Any";
    randomFilters[name] = selectElement.value;
  }

  function applyConfiguration(message) {
    const options = message.filters || {};
    ["rating", "difficulty", "type", "released", "hall_of_fame"].forEach((name) => {
      populateFilter(name, options[name]);
    });
    saveFilters();
    filterSummary();
  }

  randomFilterInputs.forEach((input) => {
    input.addEventListener("change", () => {
      randomFilters[input.dataset.randomFilter] = input.value;
      saveFilters();
      filterSummary();
    });
  });
  document.getElementById("resetFiltersButton").addEventListener("click", () => {
    randomFilterInputs.forEach((input) => {
      input.value = "Any";
      randomFilters[input.dataset.randomFilter] = "Any";
    });
    saveFilters();
    filterSummary();
  });

  function showCommandStatus(message, status = "") {
    commandStatus.hidden = !message;
    commandStatus.classList.toggle("success", status === "success");
    commandStatus.classList.toggle("error", status === "error");
    commandStatus.textContent = String(message || "");
  }

  function requestId() {
    return `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 10)}`;
  }

  function sendCommand(command, details = {}) {
    if (!liveSocket || liveSocket.readyState !== WebSocket.OPEN) {
      showCommandStatus("The tracker is reconnecting. Try again in a moment.", "error");
      return "";
    }
    const id = requestId();
    pendingRequestIds.add(id);
    liveSocket.send(JSON.stringify({ command, request_id: id, ...details }));
    return id;
  }

  searchForm.addEventListener("submit", (event) => {
    event.preventDefault();
    const query = searchInput.value.trim();
    if (!query) {
      showCommandStatus("Enter part of a hack title, creator, tag, or difficulty.", "error");
      searchInput.focus();
      return;
    }
    activeSearchRequest = sendCommand("search_hacks", { query });
    if (activeSearchRequest) {
      searchButton.disabled = true;
      searchButton.textContent = "Searching…";
      showCommandStatus("Searching downloaded hacks…");
    }
  });

  function renderSearchResults(message) {
    if (activeSearchRequest && message.request_id !== activeSearchRequest) return;
    activeSearchRequest = "";
    searchButton.disabled = false;
    searchButton.textContent = "Search";
    searchResults.replaceChildren();
    const results = Array.isArray(message.results) ? message.results : [];
    searchResults.hidden = results.length === 0;
    results.forEach((game) => {
      const row = document.createElement("div");
      row.className = "search-result";
      const copy = document.createElement("div");
      copy.className = "search-result-copy";
      const title = document.createElement("strong");
      title.textContent = game.title || "Unknown";
      const details = document.createElement("span");
      const rating = Number(game.rating) > 0 ? ` · ★ ${Number(game.rating).toFixed(1)}` : "";
      details.textContent = `${game.creator || "Unknown"} · ${game.difficulty || "Unknown"}${rating}`;
      copy.append(title, details);
      const playButton = document.createElement("button");
      playButton.className = "primary-control-button";
      playButton.type = "button";
      playButton.textContent = "Play";
      playButton.addEventListener("click", () => {
        const id = sendCommand("play_hack", { game_id: game.id });
        if (id) {
          playButton.disabled = true;
          showCommandStatus(`Sending “${game.title || "hack"}” to the tracker…`);
        }
      });
      row.append(copy, playButton);
      searchResults.append(row);
    });
    showCommandStatus(message.message || "Search complete.", results.length ? "success" : "error");
  }

  playRandomButton.addEventListener("click", () => {
    const id = sendCommand("play_random_hack", { filters: { ...randomFilters } });
    if (id) {
      playRandomButton.disabled = true;
      playRandomButton.textContent = "Choosing…";
      showCommandStatus("Choosing a downloaded hack with your filters…");
    }
  });

  function handleSocketMessage(message) {
    if (message.event === "configuration") {
      if (!pendingRequestIds.has(message.request_id)) return;
      pendingRequestIds.delete(message.request_id);
      applyConfiguration(message);
      return;
    }
    if (message.event === "search_results") {
      if (!pendingRequestIds.has(message.request_id)) return;
      pendingRequestIds.delete(message.request_id);
      renderSearchResults(message);
      return;
    }
    if (message.event === "command_result") {
      if (!pendingRequestIds.has(message.request_id)) return;
      pendingRequestIds.delete(message.request_id);
      playRandomButton.disabled = false;
      playRandomButton.textContent = "Play Random Hack";
      showCommandStatus(message.message || "The tracker handled the request.", message.ok ? "success" : "error");
      return;
    }
    if (message && message.schema === 1) render(message);
  }

  function showSocketStatus(text, connected) {
    const connection = document.getElementById("connectionState");
    connection.classList.toggle("connected", connected);
    connection.classList.toggle("offline", !connected);
    setText("connectionText", text);
  }

  function scheduleReconnect() {
    if (closing || reconnectTimer !== null) return;
    reconnectTimer = window.setTimeout(() => {
      reconnectTimer = null;
      connectToTracker();
    }, reconnectDelay);
    reconnectDelay = Math.min(5000, Math.round(reconnectDelay * 1.7));
  }

  function connectToTracker() {
    if (liveSocket && (liveSocket.readyState === WebSocket.OPEN || liveSocket.readyState === WebSocket.CONNECTING)) return;
    const socketProtocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const token = new URLSearchParams(window.location.search).get("token") || "";
    const socketUrl = `${socketProtocol}//${window.location.host}/obs-widget/socket?token=${encodeURIComponent(token)}`;
    liveSocket = new WebSocket(socketUrl);
    showSocketStatus("Connecting to app", false);
    liveSocket.addEventListener("open", () => {
      reconnectDelay = 500;
      showSocketStatus("Connected to app", true);
      sendCommand("get_configuration");
    });
    liveSocket.addEventListener("message", (event) => {
      try {
        handleSocketMessage(JSON.parse(event.data));
      } catch (_error) {
        // Ignore malformed frames and keep the direct connection alive.
      }
    });
    liveSocket.addEventListener("close", () => {
      liveSocket = null;
      pendingRequestIds.clear();
      searchButton.disabled = false;
      playRandomButton.disabled = false;
      showSocketStatus("Reconnecting to app", false);
      setText("lastUpdate", "Waiting for the desktop tracker…");
      scheduleReconnect();
    });
    liveSocket.addEventListener("error", () => {
      if (liveSocket) liveSocket.close();
    });
  }

  randomFilterInputs.forEach((input) => {
    input.value = randomFilters[input.dataset.randomFilter] || "Any";
  });
  filterSummary();
  applyVisibility();
  connectToTracker();
  window.addEventListener("beforeunload", () => {
    closing = true;
    if (reconnectTimer !== null) window.clearTimeout(reconnectTimer);
    if (liveSocket) liveSocket.close();
  });
})();

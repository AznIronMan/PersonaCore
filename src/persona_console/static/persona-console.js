(function () {
  function closeOpenNav(except) {
    document.querySelectorAll(".admin-nav-group[open]").forEach(function (group) {
      if (group !== except) group.open = false;
    });
  }

  document.querySelectorAll(".admin-nav-group").forEach(function (group) {
    group.addEventListener("toggle", function () {
      if (group.open) closeOpenNav(group);
    });
  });
  document.addEventListener("click", function (event) {
    if (!event.target.closest(".admin-nav-group")) closeOpenNav(null);
  });
  document.addEventListener("keydown", function (event) {
    if (event.key !== "Escape") return;
    closeOpenNav(null);
    const mobile = document.querySelector(".admin-mobile-nav");
    if (mobile) mobile.open = false;
  });

  const flashParams = new URLSearchParams(window.location.search);
  const flashText = flashParams.get("flash");
  if (flashText) {
      const stack = document.getElementById("flash-stack");
      if (stack) {
        const level = flashParams.get("flash_level") || "good";
        const safeLevel = ["good", "warn", "bad", "info", "neutral"].includes(level) ? level : "good";
        const banner = document.createElement("div");
        banner.className = "flash-banner pc-flash-banner flash-" + safeLevel + " pc-flash-" + safeLevel;
        const message = document.createElement("span");
        message.className = "flash-message pc-flash-message";
        message.textContent = flashText;
        const close = document.createElement("button");
        close.type = "button";
        close.className = "flash-dismiss pc-flash-dismiss";
        close.setAttribute("data-dismiss-flash", "");
        close.textContent = "Dismiss";
        close.addEventListener("click", function () { banner.remove(); });
        banner.append(message, close);
      stack.appendChild(banner);
    }
    flashParams.delete("flash");
    flashParams.delete("flash_level");
    flashParams.delete("flash_ts");
    const cleanQuery = flashParams.toString();
    window.history.replaceState(null, "", window.location.pathname + (cleanQuery ? "?" + cleanQuery : "") + window.location.hash);
  }
  document.addEventListener("click", function (event) {
    const button = event.target.closest("[data-dismiss-flash]");
    if (!button) return;
    const banner = button.closest(".flash-banner");
    if (banner) banner.remove();
  });

  function setRefreshStatus(message, state) {
    const status = document.getElementById("page-refresh-status");
    if (!status) return;
    status.textContent = message;
    status.dataset.state = state || "";
    status.title = new Date().toLocaleString();
  }
  function markPageUpdated(message) {
    setRefreshStatus(message || "Updated now", "ok");
  }
  window.__personaConsoleSetRefreshStatus = setRefreshStatus;
  window.__personaConsoleMarkUpdated = markPageUpdated;

  const liveTarget = document.getElementById("live-target");
  const livePill = document.getElementById("live-pill");
  let liveInflight = false;
  let liveTimer = null;
  let liveState = null;

  async function refreshLiveTarget(options) {
    const manual = Boolean(options && options.manual);
    if (!liveTarget || !liveTarget.dataset.liveUrl || liveInflight) return false;
    const holdSelector = liveTarget.dataset.liveHoldWhen || "";
    if (!manual && holdSelector && liveTarget.querySelector(holdSelector)) return false;
    liveInflight = true;
    try {
      const response = await fetch(liveTarget.dataset.liveUrl, {
        credentials: "same-origin",
        headers: {"X-Live-Refresh": "1"},
      });
      if (!response.ok) throw new Error(String(response.status));
      liveTarget.innerHTML = await response.text();
      markPageUpdated();
      return true;
    } catch (error) {
      if (manual) setRefreshStatus("Refresh failed", "error");
      return false;
    } finally {
      liveInflight = false;
    }
  }
  window.__personaConsoleRefreshLiveTarget = refreshLiveTarget;

  function scheduleLiveRefresh() {
    if (liveTimer) {
      clearInterval(liveTimer);
      liveTimer = null;
    }
    if (!liveState || !liveState.on || document.hidden) return;
    liveTimer = setInterval(function () { refreshLiveTarget(); }, liveState.interval * 1000);
  }

  if (livePill && liveTarget) {
    const toggle = livePill.querySelector("#live-toggle");
    const label = livePill.querySelector(".live-pill-label");
    const select = livePill.querySelector("#live-interval");
    const storeKey = livePill.dataset.storageKey || ("live:" + window.location.pathname);
    const defaultInterval = parseInt(livePill.dataset.defaultInterval || "15", 10) || 15;
    liveState = {on: true, interval: defaultInterval};
    try {
      const saved = window.localStorage.getItem(storeKey);
      if (saved) liveState = Object.assign(liveState, JSON.parse(saved));
    } catch (error) {}

    function persistLiveState() {
      try { window.localStorage.setItem(storeKey, JSON.stringify(liveState)); } catch (error) {}
    }
    function renderLiveState() {
      if (label) label.textContent = liveState.on ? "Live" : "Paused";
      if (toggle) {
        toggle.classList.toggle("live-on", Boolean(liveState.on));
        toggle.setAttribute("aria-pressed", liveState.on ? "true" : "false");
      }
      if (select) select.value = String(liveState.interval);
    }
    if (toggle) {
      toggle.addEventListener("click", function () {
        liveState.on = !liveState.on;
        persistLiveState();
        renderLiveState();
        scheduleLiveRefresh();
        if (liveState.on) refreshLiveTarget({manual: true});
      });
    }
    if (select) {
      select.addEventListener("change", function () {
        liveState.interval = parseInt(select.value || String(defaultInterval), 10) || defaultInterval;
        persistLiveState();
        renderLiveState();
        scheduleLiveRefresh();
      });
    }
    document.addEventListener("visibilitychange", function () {
      scheduleLiveRefresh();
      if (!document.hidden && liveState.on) refreshLiveTarget();
    });
    renderLiveState();
    scheduleLiveRefresh();
  }

  const pageRefreshButton = document.getElementById("page-refresh-button");
  if (pageRefreshButton) {
    pageRefreshButton.addEventListener("click", async function () {
      if (pageRefreshButton.disabled) return;
      pageRefreshButton.disabled = true;
      pageRefreshButton.classList.add("is-loading");
      setRefreshStatus(liveTarget ? "Refreshing..." : "Reloading...", "busy");
      try {
        if (liveTarget) {
          const updated = await refreshLiveTarget({manual: true});
          if (updated) markPageUpdated();
        } else {
          window.location.reload();
        }
      } finally {
        pageRefreshButton.disabled = false;
        pageRefreshButton.classList.remove("is-loading");
      }
    });
  }
})();

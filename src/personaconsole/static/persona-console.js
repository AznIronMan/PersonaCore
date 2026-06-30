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

  function setRefreshStatus(message, state, statusId) {
    const status = document.getElementById(statusId || "page-refresh-status");
    if (!status) return;
    status.textContent = message;
    status.dataset.state = state || "";
    status.title = new Date().toLocaleString();
  }
  function markPageUpdated(message, statusId) {
    setRefreshStatus(message || "Updated now", "ok", statusId);
  }
  window.__personaConsoleSetRefreshStatus = setRefreshStatus;
  window.__personaConsoleMarkUpdated = markPageUpdated;

  const liveControllers = [];

  function liveKey(target) {
    return target.dataset.pcLiveKey || target.id || "live-target";
  }

  function liveUrl(target) {
    return target.dataset.pcLiveUrl || target.dataset.liveUrl || "";
  }

  function liveStatusId(target, controls) {
    return (controls && controls.dataset.pcLiveStatus) || target.dataset.pcLiveStatus || "page-refresh-status";
  }

  function liveLabel(target, controls, name, fallback) {
    const dataName = "pcLive" + name.charAt(0).toUpperCase() + name.slice(1) + "Label";
    return (controls && controls.dataset[dataName]) || target.dataset[dataName] || fallback;
  }

  function selectorMatchesTarget(selector, target) {
    if (!selector) return false;
    if (target.id && (selector === "#" + target.id || selector === target.id)) return true;
    return selector === liveKey(target);
  }

  function controlsForTarget(target) {
    const controls = Array.from(document.querySelectorAll("[data-pc-live-controls], #live-pill"));
    const key = liveKey(target);
    return controls.find(function (control) {
      return selectorMatchesTarget(control.dataset.pcLiveFor || control.dataset.pcLiveTarget || "", target)
        || control.dataset.pcLiveKey === key
        || (target.id === "live-target" && control.id === "live-pill");
    }) || null;
  }

  function parseSeconds(value, fallback) {
    const parsed = parseInt(value || String(fallback || 0), 10);
    return Number.isFinite(parsed) && parsed > 0 ? parsed : fallback;
  }

  function setLiveTargetState(target, state, statusId, message) {
    target.dataset.pcLiveState = state || "";
    target.classList.toggle("is-refreshing", state === "busy");
    target.classList.toggle("is-stale", state === "stale");
    target.classList.toggle("has-refresh-error", state === "error");
    if (message) setRefreshStatus(message, state, statusId);
  }

  function installLiveRefresh(target) {
    const controls = controlsForTarget(target);
    const url = liveUrl(target);
    if (!url) return null;

    const toggle = controls ? controls.querySelector("[data-pc-live-toggle], #live-toggle") : null;
    const label = controls ? controls.querySelector(".live-pill-label, .pc-live-label") : null;
    const select = controls ? controls.querySelector("[data-pc-live-interval], #live-interval") : null;
    const manualButtons = Array.from(document.querySelectorAll("[data-pc-live-manual]:not(#page-refresh-button)")).filter(function (button) {
      const selector = button.dataset.pcLiveTarget || "";
      return !selector || selectorMatchesTarget(selector, target);
    });
    const statusId = liveStatusId(target, controls);
    const defaultInterval = parseSeconds(
      (controls && controls.dataset.defaultInterval) || target.dataset.pcLiveInterval,
      15
    );
    const storeKey = (controls && controls.dataset.storageKey) || ("live:" + liveKey(target));
    const pausedDefault = (controls && controls.dataset.pcLivePaused === "true") || target.dataset.pcLivePaused === "true";
    const state = {on: !pausedDefault, interval: defaultInterval};
    let inflight = false;
    let liveTimer = null;
    let staleTimer = null;

    try {
      const saved = window.localStorage.getItem(storeKey);
      if (saved) Object.assign(state, JSON.parse(saved));
    } catch (error) {}

    function persistLiveState() {
      try { window.localStorage.setItem(storeKey, JSON.stringify(state)); } catch (error) {}
    }

    function renderLiveState() {
      if (label) label.textContent = state.on
        ? liveLabel(target, controls, "label", "Live")
        : liveLabel(target, controls, "paused", "Paused");
      if (toggle) {
        toggle.classList.toggle("live-on", Boolean(state.on));
        toggle.setAttribute("aria-pressed", state.on ? "true" : "false");
      }
      if (select) select.value = String(state.interval);
      if (controls) controls.dataset.pcLiveState = state.on ? "live" : "paused";
    }

    function scheduleStaleCheck() {
      if (staleTimer) {
        clearTimeout(staleTimer);
        staleTimer = null;
      }
      const staleAfter = parseSeconds(target.dataset.pcLiveStaleAfter, 0);
      if (!staleAfter) return;
      staleTimer = setTimeout(function () {
        if (inflight) return;
        setLiveTargetState(target, "stale", statusId, liveLabel(target, controls, "stale", "Stale"));
      }, staleAfter * 1000);
    }

    async function refresh(options) {
      const manual = Boolean(options && options.manual);
      const holdSelector = target.dataset.pcLiveHoldWhen || target.dataset.liveHoldWhen || "";
      if (inflight) return false;
      if (!manual && holdSelector && target.querySelector(holdSelector)) return false;
      inflight = true;
      setLiveTargetState(target, "busy", statusId, liveLabel(target, controls, "refreshing", "Refreshing..."));
      try {
        const response = await fetch(url, {
          credentials: "same-origin",
          headers: {"X-Live-Refresh": "1", "X-PersonaConsole-Partial": "1"},
        });
        if (!response.ok) throw new Error(String(response.status));
        target.innerHTML = await response.text();
        target.dataset.pcLiveUpdatedAt = new Date().toISOString();
        target.classList.remove("has-refresh-error", "is-stale");
        markPageUpdated(liveLabel(target, controls, "updated", "Updated now"), statusId);
        scheduleStaleCheck();
        return true;
      } catch (error) {
        setLiveTargetState(target, "error", statusId, liveLabel(target, controls, "error", "Refresh failed"));
        return false;
      } finally {
        inflight = false;
        target.classList.remove("is-refreshing");
      }
    }

    function scheduleLiveRefresh() {
      if (liveTimer) {
        clearInterval(liveTimer);
        liveTimer = null;
      }
      if (!state.on || document.hidden) return;
      liveTimer = setInterval(function () { refresh(); }, state.interval * 1000);
    }

    if (toggle) {
      toggle.addEventListener("click", function () {
        state.on = !state.on;
        persistLiveState();
        renderLiveState();
        scheduleLiveRefresh();
        if (state.on) refresh({manual: true});
      });
    }
    if (select) {
      select.addEventListener("change", function () {
        state.interval = parseSeconds(select.value, defaultInterval);
        persistLiveState();
        renderLiveState();
        scheduleLiveRefresh();
      });
    }
    manualButtons.forEach(function (button) {
      button.addEventListener("click", async function () {
        if (button.disabled) return;
        button.disabled = true;
        button.classList.add("is-loading");
        await refresh({manual: true});
        button.disabled = false;
        button.classList.remove("is-loading");
      });
    });
    document.addEventListener("visibilitychange", function () {
      scheduleLiveRefresh();
      if (!document.hidden && state.on) refresh();
    });

    renderLiveState();
    scheduleStaleCheck();
    scheduleLiveRefresh();
    return {target: target, refresh: refresh, schedule: scheduleLiveRefresh};
  }

  Array.from(document.querySelectorAll("[data-pc-live-target], #live-target")).forEach(function (target) {
    if (liveControllers.some(function (controller) { return controller.target === target; })) return;
    const controller = installLiveRefresh(target);
    if (controller) liveControllers.push(controller);
  });

  async function refreshLiveTarget(options) {
    if (!liveControllers.length) return false;
    return liveControllers[0].refresh(options);
  }
  window.__personaConsoleRefreshLiveTarget = refreshLiveTarget;
  window.__personaConsoleRefreshPartial = function (selector, options) {
    const target = typeof selector === "string" ? document.querySelector(selector) : selector;
    const controller = liveControllers.find(function (item) { return item.target === target; });
    return controller ? controller.refresh(options || {manual: true}) : Promise.resolve(false);
  };

  const pageRefreshButton = document.getElementById("page-refresh-button");
  if (pageRefreshButton) {
    pageRefreshButton.addEventListener("click", async function () {
      if (pageRefreshButton.disabled) return;
      pageRefreshButton.disabled = true;
      pageRefreshButton.classList.add("is-loading");
      setRefreshStatus(liveControllers.length ? "Refreshing..." : "Reloading...", "busy");
      try {
        if (liveControllers.length) {
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

  function terminalRole(value) {
    const raw = String(value || "").toLowerCase().replace("-", "_");
    if (["command", "cmd", "human", "input", "operator", "prompt", "user"].includes(raw)) return "input";
    if (["err", "error", "failed", "stderr"].includes(raw)) return "error";
    if (["note", "status", "system"].includes(raw)) return "system";
    if (["tool", "tool_call", "tool_result"].includes(raw)) return "tool";
    return "output";
  }

  function terminalTone(value) {
    const raw = String(value || "").toLowerCase();
    if (["bad", "blocked", "critical", "danger", "down", "error", "failed"].includes(raw)) return "bad";
    if (["warn", "warning", "held", "pending", "queued", "review"].includes(raw)) return "warn";
    if (["good", "healthy", "ok", "ready", "success"].includes(raw)) return "good";
    if (["info"].includes(raw)) return "info";
    return "neutral";
  }

  function terminalText(parent, tag, className, value) {
    if (value === undefined || value === null || value === "") return null;
    const node = document.createElement(tag);
    if (className) node.className = className;
    node.textContent = String(value);
    parent.appendChild(node);
    return node;
  }

  function terminalEventNode(event) {
    const role = terminalRole(event.role || event.kind || event.type);
    const tone = terminalTone(event.tone || event.status);
    const article = document.createElement("article");
    article.className = "pc-terminal-event pc-terminal-role-" + role + " pc-dashboard-tone-" + tone;
    if (event.key || event.id) article.dataset.eventKey = String(event.key || event.id);
    article.dataset.eventRole = role;

    const gutter = document.createElement("div");
    gutter.className = "pc-terminal-event-gutter";
    terminalText(gutter, "span", "pc-terminal-role-label", event.label || role);

    const main = document.createElement("div");
    main.className = "pc-terminal-event-main";
    const meta = document.createElement("div");
    meta.className = "pc-terminal-event-meta";
    terminalText(meta, "span", "pc-terminal-sequence", event.sequence);
    terminalText(meta, "time", "", event.timestamp);
    terminalText(meta, "span", "", event.source);
    if (event.truncated) terminalText(meta, "span", "pc-terminal-truncated", "truncated");
    if (meta.childNodes.length) main.appendChild(meta);
    terminalText(main, "span", "pc-terminal-text", event.text || event.message || "");

    article.append(gutter, main);
    return article;
  }

  function terminalUrl(base, cursorName, cursorValue, limit) {
    const url = new URL(base, window.location.href);
    if (cursorValue) url.searchParams.set(cursorName, cursorValue);
    if (limit) url.searchParams.set("limit", String(limit));
    return url.toString();
  }

  async function terminalFetchJson(url) {
    const response = await fetch(url, {
      credentials: "same-origin",
      headers: {"X-PersonaConsole-Terminal": "1"},
    });
    if (!response.ok) throw new Error(String(response.status));
    return await response.json();
  }

  function terminalTrim(events, maxEvents, fromStart) {
    while (events.children.length > maxEvents) {
      if (fromStart) events.removeChild(events.firstElementChild);
      else events.removeChild(events.lastElementChild);
    }
  }

  function terminalAtBottom(viewport) {
    return viewport.scrollHeight - viewport.scrollTop - viewport.clientHeight < 48;
  }

  document.querySelectorAll("[data-pc-terminal-stream]").forEach(function (stream) {
    const events = stream.querySelector("[data-pc-terminal-events]");
    const viewport = stream.querySelector(".pc-terminal-viewport");
    if (!events || !viewport) return;
    const maxEvents = parseInt(stream.dataset.maxEvents || "200", 10) || 200;
    const autoscroll = stream.dataset.autoscroll !== "false";
    const historyButton = stream.querySelector("[data-pc-terminal-history]");
    let beforeCursor = stream.dataset.beforeCursor || "";
    let afterCursor = stream.dataset.afterCursor || "";
    let liveTimer = null;

    function scrollToBottom() {
      if (autoscroll) viewport.scrollTop = viewport.scrollHeight;
    }
    if ((stream.dataset.initialPosition || "current") === "current") scrollToBottom();

    async function loadEarlier() {
      const url = stream.dataset.historyUrl;
      if (!url || !historyButton || historyButton.disabled) return;
      historyButton.disabled = true;
      try {
        const payload = await terminalFetchJson(terminalUrl(url, "before", beforeCursor, maxEvents));
        const chunk = Array.isArray(payload.events) ? payload.events : [];
        const fragment = document.createDocumentFragment();
        chunk.forEach(function (event) { fragment.appendChild(terminalEventNode(event)); });
        events.insertBefore(fragment, events.firstChild);
        beforeCursor = payload.before_cursor || payload.beforeCursor || beforeCursor;
        stream.dataset.beforeCursor = beforeCursor;
        terminalTrim(events, maxEvents, false);
        historyButton.disabled = payload.has_more_before === false || payload.hasMoreBefore === false;
      } catch (error) {
        historyButton.disabled = false;
      }
    }

    async function loadNewer() {
      const url = stream.dataset.streamUrl;
      if (!url) return;
      const shouldStick = autoscroll && terminalAtBottom(viewport);
      try {
        const payload = await terminalFetchJson(terminalUrl(url, "after", afterCursor, maxEvents));
        const chunk = Array.isArray(payload.events) ? payload.events : [];
        chunk.forEach(function (event) { events.appendChild(terminalEventNode(event)); });
        afterCursor = payload.after_cursor || payload.afterCursor || payload.cursor || afterCursor;
        stream.dataset.afterCursor = afterCursor;
        terminalTrim(events, maxEvents, true);
        if (shouldStick && chunk.length) scrollToBottom();
      } catch (error) {}
    }

    if (historyButton) historyButton.addEventListener("click", loadEarlier);
    if (stream.dataset.streamUrl) {
      const interval = Math.max(parseInt(stream.dataset.pollInterval || "4000", 10) || 4000, 1000);
      liveTimer = setInterval(loadNewer, interval);
      document.addEventListener("visibilitychange", function () {
        if (document.hidden && liveTimer) {
          clearInterval(liveTimer);
          liveTimer = null;
        } else if (!document.hidden && !liveTimer) {
          loadNewer();
          liveTimer = setInterval(loadNewer, interval);
        }
      });
    }
  });

  document.querySelectorAll("[data-pc-settings-editor]").forEach(function (editor) {
    const changedCount = editor.querySelector("[data-pc-settings-changed-count]");

    function inputValue(input) {
      if (input.type === "checkbox") return input.checked ? "true" : "false";
      return input.value || "";
    }

    function updateDirtyState() {
      let count = 0;
      editor.querySelectorAll("[data-pc-settings-field]").forEach(function (field) {
        let dirty = false;
        field.querySelectorAll("input, select, textarea").forEach(function (input) {
          if (input.dataset.secret === "true") {
            if (input.value) dirty = true;
            return;
          }
          const original = input.dataset.originalValue || "";
          if (inputValue(input) !== original) dirty = true;
        });
        field.classList.toggle("is-client-changed", dirty);
        if (dirty) count += 1;
      });
      if (changedCount) changedCount.textContent = String(count || changedCount.dataset.initialCount || changedCount.textContent || "0");
    }

    editor.querySelectorAll("input, select, textarea").forEach(function (input) {
      input.addEventListener("input", updateDirtyState);
      input.addEventListener("change", updateDirtyState);
    });
    editor.querySelectorAll("[data-pc-settings-dismiss]").forEach(function (button) {
      button.addEventListener("click", function () {
        const banner = button.closest(".pc-settings-banner");
        if (banner) banner.remove();
      });
    });
  });
})();

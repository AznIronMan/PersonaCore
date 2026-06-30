(function () {
  "use strict";

  function text(node, value) {
    if (node) {
      node.textContent = value;
    }
  }

  function setHidden(node, hidden) {
    if (node) {
      node.hidden = hidden;
    }
  }

  function initSlideshows(root) {
    root.querySelectorAll("[data-pc-slideshow]").forEach(function (slideshow) {
      var image = slideshow.querySelector("[data-pc-slide-image]");
      if (!image) {
        return;
      }
      var slides = [];
      try {
        slides = JSON.parse(slideshow.getAttribute("data-pc-slide-srcs") || "[]");
      } catch (_error) {
        slides = [];
      }
      if (!Array.isArray(slides) || slides.length < 2) {
        return;
      }
      var dots = Array.prototype.slice.call(slideshow.querySelectorAll(".pc-public-slide-dot"));
      var index = 0;
      var interval = Number(slideshow.getAttribute("data-pc-slide-interval") || 7000);
      window.setInterval(function () {
        index = (index + 1) % slides.length;
        var slide = slides[index] || {};
        if (slide.src) {
          image.src = slide.src;
        }
        if (slide.alt) {
          image.alt = slide.alt;
        }
        dots.forEach(function (dot, dotIndex) {
          dot.classList.toggle("is-active", dotIndex === index);
        });
      }, Math.max(2500, interval));
    });
  }

  function initSoundControls(root) {
    root.querySelectorAll("[data-pc-public-media]").forEach(function (media) {
      var video = media.querySelector("[data-pc-public-video]");
      var audio = media.querySelector("[data-pc-public-audio]");
      var button = media.querySelector("[data-pc-sound-toggle]");
      if (!button || (!video && !audio)) {
        return;
      }
      function soundOn() {
        return button.getAttribute("aria-pressed") === "true";
      }
      function applyState(on) {
        if (video) {
          video.muted = !on;
          if (on && video.paused) {
            video.play().catch(function () {});
          }
        }
        if (audio) {
          audio.muted = !on;
          if (on) {
            audio.play().catch(function () {});
          } else {
            audio.pause();
          }
        }
        button.setAttribute("aria-pressed", on ? "true" : "false");
        text(button.querySelector("[data-pc-sound-label]"), on ? "Sound on" : "Sound off");
      }
      applyState(soundOn());
      button.addEventListener("click", function () {
        applyState(!soundOn());
      });
    });
  }

  function initModals(root) {
    root.querySelectorAll("[data-pc-legal-open]").forEach(function (trigger) {
      trigger.addEventListener("click", function () {
        var key = trigger.getAttribute("data-pc-legal-open");
        setHidden(root.querySelector('[data-pc-legal-modal="' + CSS.escape(key) + '"]'), false);
      });
    });
    root.querySelectorAll("[data-pc-settings-modal-open]").forEach(function (trigger) {
      trigger.addEventListener("click", function () {
        setHidden(root.querySelector("[data-pc-settings-modal]"), false);
      });
    });
    root.querySelectorAll("[data-pc-modal-close]").forEach(function (trigger) {
      trigger.addEventListener("click", function () {
        var modal = trigger.closest(".pc-public-modal");
        setHidden(modal, true);
      });
    });
    root.querySelectorAll(".pc-public-modal").forEach(function (modal) {
      modal.addEventListener("click", function (event) {
        if (event.target === modal) {
          setHidden(modal, true);
        }
      });
    });
  }

  function initSignupHooks(root) {
    root.querySelectorAll("[data-pc-signup-form]").forEach(function (form) {
      form.addEventListener("submit", function (event) {
        var hook = new CustomEvent("persona:signup", {
          bubbles: true,
          cancelable: true,
          detail: { form: form }
        });
        if (!form.dispatchEvent(hook)) {
          event.preventDefault();
          return;
        }
        if (form.getAttribute("data-pc-async") !== "true") {
          return;
        }
        event.preventDefault();
        var status = form.querySelector("[data-pc-form-status]");
        text(status, "Sending...");
        window.fetch(form.action, {
          method: form.method || "POST",
          body: new FormData(form),
          headers: { "Accept": "application/json" }
        }).then(function (response) {
          text(status, response.ok ? "Saved." : "Unable to save.");
        }).catch(function () {
          text(status, "Unable to save.");
        });
      });
    });
  }

  function appendChatMessage(container, body, outgoing) {
    var article = document.createElement("article");
    article.className = "pc-public-chat-message " + (outgoing ? "pc-public-chat-message-outgoing" : "pc-public-chat-message-system");
    var paragraph = document.createElement("p");
    paragraph.textContent = body;
    article.appendChild(paragraph);
    container.appendChild(article);
    container.scrollTop = container.scrollHeight;
  }

  function initChatHooks(root) {
    root.querySelectorAll("[data-pc-chat-form]").forEach(function (form) {
      var shell = form.closest("[data-pc-chat]");
      var messages = shell ? shell.querySelector("[data-pc-chat-messages]") : null;
      var status = form.querySelector("[data-pc-chat-status]");
      form.addEventListener("submit", function (event) {
        event.preventDefault();
        var field = form.querySelector("textarea[name='message']");
        var value = field ? field.value.trim() : "";
        if (!value || !messages) {
          return;
        }
        var payload = new FormData(form);
        appendChatMessage(messages, value, true);
        if (field) {
          field.value = "";
        }
        text(status, "Sending...");
        var endpoint = form.getAttribute("data-pc-chat-endpoint") || form.action;
        if (!endpoint) {
          text(status, "Queued locally.");
          return;
        }
        window.fetch(endpoint, {
          method: "POST",
          body: payload,
          headers: { "Accept": "application/json" }
        }).then(function (response) {
          text(status, response.ok ? "Sent." : "Queued.");
          return response.headers.get("content-type") && response.headers.get("content-type").indexOf("application/json") >= 0
            ? response.json()
            : null;
        }).then(function (payload) {
          if (payload && payload.reply) {
            appendChatMessage(messages, String(payload.reply), false);
          }
        }).catch(function () {
          text(status, "Queued.");
        });
      });
    });
  }

  function initPublicPresence(root) {
    initSlideshows(root);
    initSoundControls(root);
    initModals(root);
    initSignupHooks(root);
    initChatHooks(root);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function () {
      initPublicPresence(document);
    });
  } else {
    initPublicPresence(document);
  }

  window.PersonaPublicPresence = {
    init: initPublicPresence
  };
})();

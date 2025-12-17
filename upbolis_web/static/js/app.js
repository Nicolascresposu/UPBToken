document.addEventListener("DOMContentLoaded", () => {
  // ========= 1) TILT 3D =========
  const tiltContainer = document.querySelector("[data-tilt-container]");
  if (tiltContainer) {
    const strength = 8;

    tiltContainer.addEventListener("mousemove", (e) => {
      const rect = tiltContainer.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;

      const centerX = rect.width / 2;
      const centerY = rect.height / 2;

      const rotateX = ((y - centerY) / centerY) * -strength;
      const rotateY = ((x - centerX) / centerX) * strength;

      tiltContainer.style.transform =
        `perspective(1100px) rotateX(${rotateX}deg) rotateY(${rotateY}deg)`;
    });

    tiltContainer.addEventListener("mouseleave", () => {
      tiltContainer.style.transform =
        "perspective(1100px) rotateX(0deg) rotateY(0deg)";
    });
  }

  // ========= 2) FOCUS EN INPUTS =========
  const inputs = document.querySelectorAll("[data-field] input, .field input");
  inputs.forEach((input) => {
    const field = input.closest("[data-field]") || input.closest(".field");
    if (!field) return;

    if (input.value && input.value.trim() !== "") field.classList.add("field--focused");

    input.addEventListener("focus", () => field.classList.add("field--focused"));
    input.addEventListener("blur", () => {
      if (!input.value || input.value.trim() === "") field.classList.remove("field--focused");
    });
  });

  // ========= 3) RIPPLE =========
  const rippleButtons = document.querySelectorAll("[data-ripple], .btn-primary");
  rippleButtons.forEach((btn) => {
    btn.addEventListener("click", (e) => {
      const rect = btn.getBoundingClientRect();
      const ripple = document.createElement("span");
      ripple.classList.add("ripple");

      ripple.style.left = `${e.clientX - rect.left}px`;
      ripple.style.top = `${e.clientY - rect.top}px`;

      const previous = btn.querySelector(".ripple");
      if (previous) previous.remove();

      const computed = window.getComputedStyle(btn);
      if (computed.position === "static") btn.style.position = "relative";
      btn.style.overflow = "hidden";

      btn.appendChild(ripple);
      setTimeout(() => ripple.remove(), 500);
    });
  });

  // ========= 4) TOGGLE LOGIN/REGISTER (MISMA URL) =========
  const tabs = document.querySelectorAll("[data-auth-tab]");
  const panels = document.querySelectorAll("[data-auth-panel]");
  const switchers = document.querySelectorAll("[data-switch-auth]");

  function setActiveAuth(target) {
    // tabs
    tabs.forEach((t) => {
      const isOn = t.getAttribute("data-auth-tab") === target;
      t.classList.toggle("is-active", isOn);
      t.setAttribute("aria-selected", isOn ? "true" : "false");
    });

    // panels (animación por clases: tú la defines en CSS)
    panels.forEach((p) => {
      const isOn = p.getAttribute("data-auth-panel") === target;
      p.classList.toggle("is-active", isOn);
      p.setAttribute("aria-hidden", isOn ? "false" : "true");

      // reinicio “suave” de focus visual si cambias
      if (!isOn) {
        const inputs = p.querySelectorAll("input");
        inputs.forEach((inp) => {
          const field = inp.closest("[data-field]") || inp.closest(".field");
          if (field && (!inp.value || inp.value.trim() === "")) {
            field.classList.remove("field--focused");
          }
        });
      }
    });

    // foco en primer input del panel activo
    const activePanel = document.querySelector(`[data-auth-panel="${target}"]`);
    if (activePanel) {
      const first = activePanel.querySelector("input");
      if (first) setTimeout(() => first.focus(), 80);
    }
  }

  tabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      const target = tab.getAttribute("data-auth-tab");
      if (target) setActiveAuth(target);
    });
  });

  switchers.forEach((btn) => {
    btn.addEventListener("click", () => {
      const target = btn.getAttribute("data-switch-auth");
      if (target) setActiveAuth(target);
    });
  });

  // Por defecto: login
  setActiveAuth("login");
});

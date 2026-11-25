/* Date-only event management: the conference day belongs to Africa/Lagos. */
(function (root) {
  "use strict";
  const formatter = new Intl.DateTimeFormat("en-CA", {
    timeZone: "Africa/Lagos", year: "numeric", month: "2-digit", day: "2-digit"
  });
  function lagosDate(now = new Date()) {
    const parts = Object.fromEntries(formatter.formatToParts(now).map(p => [p.type, p.value]));
    return `${parts.year}-${parts.month}-${parts.day}`;
  }
  function phase(event, now = new Date()) {
    if (event.archived) return "past";
    const today = lagosDate(now);
    if (today > (event.endDate || event.date)) return "past";
    return today >= event.date ? "live" : "upcoming";
  }
  function countdown(event, now = new Date()) {
    // No session time is supplied: count down to the date, and show Event day on that date.
    const total = Math.max(0, Math.floor((Date.parse(event.date + "T00:00:00+01:00") - now.getTime()) / 1000));
    return {
      days: Math.floor(total / 86400), hours: Math.floor(total / 3600) % 24,
      minutes: Math.floor(total / 60) % 60, seconds: total % 60
    };
  }
  if (typeof module !== "undefined" && module.exports) module.exports = { lagosDate, phase, countdown };
  if (!root.document) return;
  const data = root.SPEAKING_EVENTS_DATA;
  if (!data) return;
  const events = data.events;
  const byId = new Map(events.map(event => [event.id, event]));
  let lastDate = "";

  function sync(now) {
    const today = lagosDate(now);
    if (today !== lastDate) {
      lastDate = today;
      const upcoming = events.filter(e => phase(e, now) !== "past").sort((a, b) => a.date.localeCompare(b.date));
      const past = events.filter(e => phase(e, now) === "past").sort((a, b) => (b.date || String(b.year)).localeCompare(a.date || String(a.year)));
      document.querySelectorAll("[data-event-list]").forEach(list => {
        const kind = list.dataset.eventList;
        if (kind === "featured") list.innerHTML = upcoming[0]?.upcomingHtml || data.emptyHtml;
        if (kind === "upcoming") list.innerHTML = upcoming.map(e => e.upcomingHtml).join("") || data.emptyHtml;
        if (kind === "past") list.innerHTML = past.map(e => e.pastHtml).join("");
      });
      const current = byId.get(document.body.dataset.eventId);
      if (current) {
        const state = phase(current, now);
        document.body.dataset.eventPhase = state;
        document.querySelectorAll("[data-event-status]").forEach(el => {
          el.textContent = state === "past" ? "Past engagement" : state === "live" ? "Event day" : "Upcoming engagement";
        });
        // Remove archived registration actions from keyboard and accessibility navigation too.
        document.querySelectorAll("[data-upcoming-only]").forEach(el => { el.hidden = state === "past"; });
        document.querySelectorAll("[data-past-only]").forEach(el => { el.hidden = state !== "past"; });
        current.gallery?.forEach(image => {
          if (image.expiresOn && today > image.expiresOn) {
            document.querySelectorAll(".flyer-gallery figure").forEach(figure => {
              if (figure.querySelector("[data-flyer]")?.getAttribute("href") === image.original) {
                const date = new Date(image.expiresOn + "T12:00:00+01:00").toLocaleDateString("en-GB", {timeZone: "Africa/Lagos", day: "numeric", month: "long", year: "numeric"});
                const caption = "Original registration flyer · offers ended " + date;
                figure.querySelector("figcaption").textContent = caption;
                figure.querySelector("[data-flyer]").dataset.caption = caption;
              }
            });
          }
        });
      }
      // Keep event offers out of archived structured data, including when a page stays open overnight.
      document.querySelectorAll('script[type="application/ld+json"]').forEach(script => {
        try {
          const graph = JSON.parse(script.textContent);
          let changed = false;
          (graph["@graph"] || [graph]).forEach(node => {
            const event = events.find(e => node["@id"] === location.origin + e.url + "#event");
            if (event && phase(event, now) === "past" && node.offers) { delete node.offers; changed = true; }
          });
          if (changed) script.textContent = JSON.stringify(graph).replace(/</g, "\\u003c");
        } catch (_) { /* Preserve unrelated structured data. */ }
      });
    }
    document.querySelectorAll("[data-event-countdown]").forEach(el => {
      const event = byId.get(el.dataset.eventCountdown);
      if (!event) return;
      const state = phase(event, now);
      if (state === "past") { el.hidden = true; return; }
      if (state === "live") {
        if (!el.querySelector(".event-day-message")) el.innerHTML = '<p class="event-day-message">Event day · ' + (event.endDate && event.endDate !== event.date ? 'under way in Lagos' : 'today in Lagos') + '</p>';
        return;
      }
      const units = countdown(event, now);
      Object.entries(units).forEach(([unit, value]) => {
        const number = el.querySelector(`[data-unit="${unit}"]`);
        if (number) number.textContent = unit === "days" ? String(value) : String(value).padStart(2, "0");
      });
    });
  }

  sync(new Date());
  root.setInterval(() => sync(new Date()), 1000);
  document.addEventListener("visibilitychange", () => { if (!document.hidden) sync(new Date()); });
  root.addEventListener("pageshow", () => sync(new Date()));

  const dialog = document.getElementById("flyer-dialog");
  if (!dialog || typeof dialog.showModal !== "function") return; // Full-size image links still work.
  const enlarged = document.getElementById("flyer-enlarged");
  const caption = document.getElementById("flyer-caption");
  const original = document.getElementById("flyer-original");
  const previous = dialog.querySelector("[data-previous-flyer]");
  const next = dialog.querySelector("[data-next-flyer]");
  let opener = null;
  let links = [];
  let index = 0;

  function showImage() {
    const link = links[index];
    enlarged.src = link.href;
    enlarged.alt = link.querySelector("img")?.alt || "Event flyer";
    caption.textContent = link.dataset.caption || "Event flyer";
    original.href = link.href;
    previous.hidden = next.hidden = links.length < 2;
  }
  document.addEventListener("click", e => {
    const link = e.target.closest("[data-flyer]");
    if (!link || e.button !== 0 || e.ctrlKey || e.metaKey || e.shiftKey || e.altKey) return;
    e.preventDefault();
    opener = link;
    links = Array.from(document.querySelectorAll("[data-flyer]"));
    index = links.indexOf(link);
    showImage();
    dialog.showModal();
    document.body.style.overflow = "hidden";
  });
  dialog.querySelector("[data-close-flyer]").addEventListener("click", () => dialog.close());
  previous.addEventListener("click", () => { index = (index - 1 + links.length) % links.length; showImage(); });
  next.addEventListener("click", () => { index = (index + 1) % links.length; showImage(); });
  dialog.addEventListener("keydown", e => {
    if (e.key === "ArrowLeft") { e.preventDefault(); previous.click(); }
    if (e.key === "ArrowRight") { e.preventDefault(); next.click(); }
  });
  dialog.addEventListener("click", e => {
    if (e.target === dialog) {
      const rect = dialog.getBoundingClientRect();
      if (e.clientX < rect.left || e.clientX > rect.right || e.clientY < rect.top || e.clientY > rect.bottom) dialog.close();
    }
  });
  dialog.addEventListener("close", () => {
    document.body.style.overflow = "";
    if (opener?.isConnected) opener.focus();
  });
})(typeof window !== "undefined" ? window : globalThis);

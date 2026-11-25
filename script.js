"use strict";
const year = document.getElementById("year");
if (year) year.textContent = new Date().getFullYear();
const menu = document.querySelector(".menu");
const nav = document.querySelector("#nav");
if (menu && nav) {
  const closeMenu = () => {
    nav.classList.remove("open");
    menu.setAttribute("aria-expanded", "false");
  };
  menu.setAttribute("aria-controls", "nav");
  menu.addEventListener("click", () => {
    const open = nav.classList.toggle("open");
    menu.setAttribute("aria-expanded", String(open));
  });
  nav.querySelectorAll("a").forEach(a => a.addEventListener("click", closeMenu));
  document.addEventListener("keydown", e => {
    if (e.key === "Escape" && nav.classList.contains("open")) {
      closeMenu();
      menu.focus();
    }
  });
}
const photoUpload = document.getElementById("photoUpload");
if (photoUpload) photoUpload.addEventListener("change", e => {
  const grid = document.getElementById("previewGrid");
  if (!grid) return;
  grid.querySelectorAll("img").forEach(img => URL.revokeObjectURL(img.src));
  grid.replaceChildren();
  Array.from(e.target.files).forEach(file => {
    if (!file.type.startsWith("image/")) return;
    const fig = document.createElement("figure");
    const img = document.createElement("img");
    const cap = document.createElement("figcaption");
    img.src = URL.createObjectURL(file);
    img.alt = file.name;
    cap.textContent = file.name + " — preview only";
    fig.append(img, cap);
    grid.append(fig);
  });
});
const galleryGrid = document.getElementById("galleryGrid");
if (galleryGrid) fetch("/gallery.json").then(r => r.ok ? r.json() : []).then(items => {
  items.forEach(item => {
    const fig = document.createElement("figure");
    const img = document.createElement("img");
    const cap = document.createElement("figcaption");
    img.src = item.file;
    img.alt = item.caption || "Professional photograph";
    cap.textContent = item.caption || "";
    fig.append(img, cap);
    galleryGrid.append(fig);
  });
}).catch(() => {});

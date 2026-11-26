"use strict";
(() => {
  const form = document.getElementById("archive-filters");
  if (form) {
    const search = document.getElementById("article-search");
    const category = document.getElementById("article-category");
    const year = document.getElementById("article-year");
    const sort = document.getElementById("article-sort");
    const list = document.getElementById("article-archive");
    const count = document.getElementById("archive-count");
    const empty = document.getElementById("archive-empty");
    const normal = text => text.normalize("NFKD").replace(/\p{Diacritic}/gu, "").toLowerCase();
    const rows = [...list.querySelectorAll("[data-article]")].map(node => ({node, date:node.dataset.date, id:node.dataset.article, categories:node.dataset.categories.split(" "), search:normal(node.textContent)}));
    let fullText = true;
    const fromUrl = () => {
      const params = new URLSearchParams(location.search);
      search.value = params.get("q") || "";
      category.value = [...category.options].some(o => o.value === params.get("category")) ? params.get("category") : "";
      year.value = [...year.options].some(o => o.value === params.get("year")) ? params.get("year") : "";
      sort.value = params.get("sort") === "oldest" ? "oldest" : "newest";
    };
    const update = (writeUrl=true) => {
      const tokens = normal(search.value.trim()).split(/\s+/).filter(Boolean);
      const ordered = [...rows].sort((a,b) => (sort.value === "oldest" ? 1 : -1) * (a.date.localeCompare(b.date) || a.id.localeCompare(b.id)));
      let visible = 0;
      for (const row of ordered) {
        const show = (!category.value || row.categories.includes(category.value)) && (!year.value || row.date.startsWith(year.value)) && tokens.every(word => row.search.includes(word));
        row.node.hidden = !show;
        if (show) visible++;
        list.append(row.node);
      }
      count.textContent = `${visible} ${visible === 1 ? "article" : "articles"} of ${rows.length}${!fullText && tokens.length ? " · Search is limited to titles and topics." : ""}`;
      empty.hidden = visible > 0;
      if (writeUrl) {
        const params = new URLSearchParams();
        if (search.value.trim()) params.set("q",search.value.trim());
        if (category.value) params.set("category",category.value);
        if (year.value) params.set("year",year.value);
        if (sort.value === "oldest") params.set("sort","oldest");
        history.replaceState(null,"",location.pathname+(params.size ? "?"+params.toString() : "")+location.hash);
      }
    };
    const reset = () => {search.value="";category.value="";year.value="";sort.value="newest";update();};
    form.hidden = false;
    fromUrl();
    // Wait for the local index before applying a bookmarked full-text query.
    fetch("/data/procure2save-search.json").then(response => {
      if (!response.ok) throw new Error("Search index unavailable");
      return response.json();
    }).then(index => {
      const byId = new Map(index.map(a => [a.id,a]));
      for (const row of rows) {
        const a = byId.get(row.id);
        if (a) row.search = normal(a.title+" "+a.text+" "+row.node.textContent);
      }
      update(false);
    }).catch(() => {fullText=false;update(false);});
    let timer;
    search.addEventListener("input",() => {clearTimeout(timer);timer=setTimeout(update,120);});
    for (const control of [category,year,sort]) control.addEventListener("change",() => update());
    form.addEventListener("submit",event => {event.preventDefault();clearTimeout(timer);update();});
    form.addEventListener("reset",event => {event.preventDefault();clearTimeout(timer);reset();search.focus();});
    document.getElementById("clear-empty").addEventListener("click",() => {reset();search.focus();});
    addEventListener("popstate",() => {fromUrl();update(false);});
  }
  const copy = document.querySelector(".p2-copy-link");
  if (copy && navigator.clipboard) {
    copy.hidden = false;
    copy.addEventListener("click",async () => {
      const status = document.querySelector(".p2-copy-status");
      try {await navigator.clipboard.writeText(document.querySelector('link[rel="canonical"]').href);status.textContent="Link copied.";}
      catch {status.textContent="Copy the page address from your browser.";}
    });
  }
})();

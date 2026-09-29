/* Seekter Web UI. Vanilla JS, hash routed, talks only to /api on 127.0.0.1.
   Same constraint as the kit: no framework, no build step, no packages. */
"use strict";

const appRoot = document.getElementById("app");

/* ---------- micro helpers ---------- */
const $1 = (sel, scope = document) => scope.querySelector(sel);
const $$s = (sel, scope = document) => [...scope.querySelectorAll(sel)];
const $ = $1;
const esc = (s) => String(s == null ? "" : s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const toast = (msg, isErr = false) => {
  const t = document.getElementById("toast");
  t.hidden = false;
  t.className = "toast" + (isErr ? " err" : "");
  t.textContent = msg;
  clearTimeout(t._h);
  t._h = setTimeout(() => { t.hidden = true; }, isErr ? 5000 : 3000);
};
const modalBox = (content) => {
  const overlay = el("div", { class: "overlay" });
  const panel = el("div", { class: "drawer" }, content);
  const escClose = (e) => {
    if (e.key === "Escape") {
      overlay.remove();
      document.removeEventListener("keydown", escClose);
    }
  };
  document.addEventListener("keydown", escClose);
  panel.prepend(el("div", { style: "display:flex;justify-content:flex-end" }, btn("Close", () => overlay.remove())));
  overlay.append(panel);
  document.body.append(overlay);
  return overlay;
};
const el = (tag, attrs = {}, ...kids) => {
  const node = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === "html") node.innerHTML = v;
    else if (k === "class") node.className = v;
    else if (k === "style") node.style.cssText = v;
    else if (k.startsWith("on")) node.addEventListener(k.slice(2), v);
    else node.setAttribute(k, v);
  }
  for (const kid of kids.flat()) {
    if (kid == null) continue;
    node.append(kid instanceof Node ? kid : document.createTextNode(kid));
  }
  return node;
};
const btn = (label, onClick, cls = "") => el("button", { class: cls, onclick: onClick }, label);
const primary = (label, onClick) => btn(label, onClick, "primary");
const field = (labelText, control) => el("label", { class: "f" }, labelText, control);
const statusChip = (status) => `<span class="chip st-${esc(String(status || "pending"))}">${esc(status || "pending")}</span>`;
const stateChip = (label) => `<span class="chip ${String(label).toLowerCase()}-line">${esc(label)}</span>`;

const debounce = (fn, ms) => (...a) => {
  clearTimeout(fn._t);
  fn._t = setTimeout(() => fn(...a), ms);
};
const fmtDate = (rec) => (rec ? (rec.applied || rec.updated || "").slice(0, 10) : "");

const api = async (path, opts = {}) => {
  if (opts.json) {
    opts.method = opts.method || "POST";
    opts.body = JSON.stringify(opts.json);
    opts.headers = { "Content-Type": "application/json", ...(opts.headers || {}) };
    delete opts.json;
  }
  try {
    const res = await fetch(path, opts);
    const payload = await res.json();
    if (payload && payload.ok === undefined && res.ok) payload.ok = true;
    return payload;
  } catch (e) {
    return { ok: false, error: e.message || "server not reachable" };
  }
};

const skeleton = (n) => {
  const box = el("div");
  for (let i = 0; i < (n || 3); i++) box.append(el("div", { class: "skel", style: "margin-bottom:14px" }));
  return box;
};

/* ---------- panels ---------- */
const ST_COLOR = {
  pending: "#9a6700", applied: "#0b62d6", interviewing: "#8250df", offer: "#1a7f37",
  rejected: "#c93c37", closed: "#5d6a7c", skipped: "#8b9199",
};
const funnelPanel = (stats) => {
  const max = Math.max(stats.sent, 1);
  const panel = el("div", { class: "panel" }, el("h3", {}, "Funnel (tracked status)"));
  const rows = [["applied", stats.applied], ["interviewing", stats.interviewing], ["offer", stats.offer],
    ["rejected", stats.rejected], ["closed", stats.closed], ["pending", stats.pending], ["skipped", stats.skipped]];
  for (const [label, value] of rows) {
    panel.append(el("div", { class: "barline" },
      el("span", {}, label),
      el("div", { class: "bar" }, el("i", { style: `width:${Math.round(value / max * 100)}%;background:${ST_COLOR[label]}` })),
      el("em", {}, String(value))));
  }
  panel.append(el("p", { class: "sub", style: "margin-top:10px" },
    `response rate: ${stats.response_rate == null ? "n/a" : Math.round(stats.response_rate * 100) + "%"} (${stats.sent} sent)`));
  return panel;
};
const monthsPanel = (months) => {
  const table = el("table", {}, el("thead", {}, el("tr", {},
    el("th", {}, "Month"), el("th", {}, "Sent"), el("th", {}, "Replies"),
    el("th", {}, "Interviewing / offers"), el("th", {}, "Pending"), el("th", {}, "Skipped"))));
  const body = el("tbody");
  for (const m of months) {
    body.append(el("tr", {}, el("td", {}, m.month), el("td", {}, String(m.sent)),
      el("td", {}, String(m.replies)), el("td", {}, String(m.live)),
      el("td", {}, String(m.pending)), el("td", {}, String(m.skipped))));
  }
  table.append(body);
  return el("div", { class: "panel" }, el("h3", {}, "By month"), table);
};
const recentTable = (rows) => {
  if (!rows.length) return el("div", { class: "empty" }, "Nothing in the last 30 days yet.");
  const table = el("table", {}, el("thead", {}, el("tr", {},
    el("th", {}, "Date"), el("th", {}, "Status"), el("th", {}, "Company"), el("th", {}, "Role"))));
  const body = el("tbody");
  for (const row of rows.slice(0, 8)) {
    body.append(el("tr", {}, el("td", {}, (row.applied || row.updated || "").slice(0, 10)),
      el("td", { html: statusChip(row.status) }),
      el("td", {}, esc(row.company)), el("td", {}, esc(row.role))));
  }
  table.append(body);
  return table;
};

/* ============================================================ dashboard */
const renderDashboard = async () => {
  document.title = "Seekter Web UI - dashboard";
  appRoot.replaceChildren(
    el("h1", { class: "page" }, "Dashboard"),
    el("p", { class: "sub" }, "Live funnel, what is waiting on you, and one click runs of the mechanical steps."),
    skeleton(3));
  const data = await api("/api/overview");
  if (!data.ok) {
    appRoot.replaceChildren(el("div", { class: "empty" }, esc(data.error || "server not reachable")));
    return;
  }
  const s = data.stats;

  const kpis = el("div", { class: "kpis" });
  for (const [label, value, tone] of [
    ["Sent", s.sent, "var(--ink)"],
    ["Response rate", s.response_rate == null ? "n/a" : Math.round(s.response_rate * 100) + "%", "var(--ink)"],
    ["Interviewing", s.interviewing, ST_COLOR.interviewing],
    ["Offers", s.offer, ST_COLOR.offer],
    ["Needs you", data.needs_you.length, ST_COLOR.pending],
    ["Skipped", s.skipped, ST_COLOR.skipped]]) {
    kpis.append(el("div", { class: "kpi" },
      el("b", { style: `color:${tone}` }, String(value)), el("span", {}, label)));
  }

  const needs = el("div", { class: "panel" },
    el("h3", {}, data.needs_you.length ? `Needs you (${data.needs_you.length})` : "Needs you"));
  if (!data.needs_you.length) needs.append(el("div", { class: "empty" }, "Nothing waiting on you right now."));
  for (const row of data.needs_you) {
    needs.append(el("div", { class: "mini" },
      el("div", { class: "lft" },
        el("div", { style: "display:flex;gap:8px;align-items:center;flex-wrap:wrap" },
          el("a", { href: row.url || "#", target: "_blank", rel: "noreferrer", style: "font-weight:600" },
            esc(row.company) + " : " + esc(row.role)),
          el("span", { html: statusChip(row.status) })),
        row.next_step ? el("div", { class: "next" }, `Next step: ${row.next_step}`) : null),
      el("button", { onclick: openDetail.bind(null, row.path) }, "Open")));
  }

  const quick = el("div", { class: "panel" }, el("h3", {}, "One click runs"),
    el("div", { class: "row-list" },
      miniAction("Rebuild index pages", "Rewrites applications/README.md and the monthly pages, the same writes the tracker does after every add and move.",
        async () => { const r = await api("/api/index", { json: {} }); toast(r.ok ? (r.report || "index rebuilt") : r.error, !r.ok); }),
      miniAction("Normalize dry run", "Lower cased enums and ATS values derived from urls; reports before it writes.",
        async () => { const r = await api("/api/normalize", { json: { dry_run: true } }); toast(r.ok ? (r.report || "nothing would change") : r.error, !r.ok); }),
      miniAction("Open sweep and add", "Search today's candidates and track them.", () => { location.hash = "#/sweep"; })));

  const cols = el("div", { class: "cols" },
    el("div", { class: "grid" }, funnelPanel(s),
      el("div", { class: "panel" }, el("h3", {}, "Last 30 days"), recentTable(data.recent))),
    el("div", { class: "grid" }, needs, quick, monthsPanel(data.months)));
  appRoot.replaceChildren(kpis, cols);
};

const miniAction = (title, note, action) =>
  el("div", { class: "mini" },
    el("div", { class: "lft" },
      el("b", {}, title), el("div", { class: "next" }, note)),
    btn("Run", action));

/* ============================================================ applications list */
const FILTERS = ["", "pending", "applied", "interviewing", "offer", "rejected", "closed", "skipped"];
let appFilter = { status: "", q: "" };

const renderApps = async (query) => {
  if (query && query.get("status") != null) appFilter.status = query.get("status");
  const chips = el("div", { style: "display:flex;gap:6px;flex-wrap:wrap" });
  for (const s of FILTERS) {
    chips.append(el("button", {
      class: "chip" + (s === appFilter.status ? (s ? " st-" + s : " on-line") : " chip-ghost"),
      style: "cursor:pointer",
      onclick: () => { appFilter.status = s; location.hash = "#/apps" + (s ? "?status=" + s : ""); },
    }, s || "all"));
  }
  const search = el("input", {
    type: "search", placeholder: "Filter by company, role, url, source...",
    style: "max-width:300px", value: appFilter.q,
    oninput: debounce((e) => { appFilter.q = e.target.value; refreshRows(); }, 250),
  });
  appRoot.replaceChildren(
    el("h1", { class: "page" }, "Applications"),
    el("p", { class: "sub" }, "One file per posting, one table row per skip. Click a row for the record and the status moves."),
    chips, search,
    el("div", { class: "panel", style: "padding:0 14px" }, el("div", { id: "rows" }, skeleton(2))));
  await refreshRows();
};

const refreshRows = async () => {
  const box = document.getElementById("rows");
  if (!box) return;
  box.replaceChildren(skeleton(2));
  const q = new URLSearchParams();
  if (appFilter.status) q.set("status", appFilter.status);
  if (appFilter.q) q.set("q", appFilter.q);
  const data = await api("/api/apps?" + q.toString());
  if (!data.ok) { box.replaceChildren(el("div", { class: "empty" }, esc(data.error))); return; }
  if (!data.rows.length) {
    box.replaceChildren(el("div", { class: "empty" }, "No records match. Track one from Sweep & add, or clear the filters."));
    return;
  }
  const table = el("table", {}, el("thead", {}, el("tr", {},
    el("th", {}, "Date"), el("th", {}, "Status"), el("th", {}, "Company"), el("th", {}, "Role"),
    el("th", {}, "Fit"), el("th", {}, "ATS / source"), el("th", {}, "Next step"), el("th", {}, ""))));
  const body = el("tbody");
  for (const row of data.rows) {
    body.append(el("tr", {},
      el("td", { style: "white-space:nowrap" }, (row.applied || row.updated || "").slice(0, 10)),
      el("td", { html: statusChip(row.status) }),
      el("td", {}, esc(row.company)),
      el("td", {}, esc(row.role)),
      el("td", {}, esc(row.location_fit)),
      el("td", {}, esc([row.ats, row.source].filter(Boolean).join(" / ") || "")),
      el("td", { class: "next", style: "max-width:340px" }, esc((row.sections && row.sections.Notes).slice(0, 120))),
      el("td", {}, el("div", { class: "acts" },
        row.url ? el("a", { href: row.url, target: "_blank", rel: "noreferrer" }, "posting") : null,
        el("button", { onclick: openDetail.bind(null, row.path) }, "Open")))));
  }
  table.append(body);
  box.replaceChildren(table);
};

const nextStepOf = (row) => {
  const notes = (row.sections && row.sections.Notes) || row.notes || "";
  return notes.length > 140 ? notes.slice(0, 140) + "..." : notes;
};

/* detail + move form */
let lastOverlay;
const openDetail = async (path) => {
  const data = await api("/api/app?path=" + encodeURIComponent(path));
  if (!data.ok) { toast(data.error, true); return; }
  const meta = el("div", { class: "dmeta" });
  for (const key of ["company", "role", "source", "ats", "applied", "updated"]) {
    const value = data[key];
    if (value !== "" && value != null) meta.append(el("div", {}, el("span", {}, key), el("b", {}, esc(value))));
  }
  if (data.url) meta.append(el("div", {}, el("span", {}, "posting"),
    el("b", {}, el("a", { href: data.url, target: "_blank", rel: "noreferrer" }, "open posting"))));
  const note = el("textarea", { placeholder: "Optional. Lands in the Log section stamped with today's date." });
  const moveRow = el("div", { style: "display:flex;gap:7px;flex-wrap:wrap;margin-top:8px" });
  for (const status of ["applied", "interviewing", "offer", "rejected", "closed", "skipped"]) {
    moveRow.append(el("button", {
      onclick: async () => {
        const res = await api("/api/move", { json: { target: data.path, status, note: note.value } });
        if (!res.ok) return toast(res.error, true);
        toast("Moved to " + status);
        if (lastOverlay) lastOverlay.remove();
        refreshRows();
      },
    }, status));
  }
  lastOverlay = modalBox(el("div", {},
    el("h2", {}, `${data.company || "(unknown)"} : ${data.role || "(no role)"}`),
    el("div", { style: "display:flex;gap:8px;align-items:center;margin:6px 0" },
      el("span", { html: statusChip(data.status) }),
      el("span", { class: "chip chip-ghost" }, data.kind === "row" ? "skip row" : "application file"),
      data.url ? el("a", { href: data.url, target: "_blank", rel: "noreferrer" }, "posting") : null),
    meta,
    ...Object.entries(data.sections).map(([name, text]) => text ? el("div", { class: "sec" }, el("h4", {}, name), el("pre", {}, esc(text))) : null),
    el("div", { class: "sec" }, el("h4", {}, "Move to status"),
      field("Log note", note), el("div", { style: "height:6px" }), moveRow)));
};

/* sweep + add */
const openDay = (date) => loadCandidates(date);
const loadHistory = async () => {
  const boxEl = document.getElementById("hist");
  const data = await api("/api/runs");
  boxEl.replaceChildren();
  if (!data.days.length) {
    boxEl.append(el("div", { class: "empty" }, "No sweeps yet. Run the sweep above; profile/search.json needs freehire.queries, freehire.categories and title_keep."));
    return;
  }
  for (const day of data.days) {
    boxEl.append(el("div", { class: "mini" },
      el("div", { class: "lft" }, el("b", {}, day.date), el("div", { class: "next" }, day.candidates + " candidates")),
      btn("Open candidates", () => openDay(day.date))));
  }
};

const pollSweep = (jobId) => {
  const timer = async () => {
    const data = await api("/api/jobs/" + jobId);
    const box = document.getElementById("live-run");
    if (!box || box.hidden) return;
    box.textContent = (data.lines || []).join("\n") || "running...";
    if (data.status === "running") {
      setTimeout(timer, 1100);
    } else {
      await loadHistory();
      await loadCandidates();
    }
  };
  setTimeout(timer, 900);
};

const renderSweep = async (query) => {
  document.title = "Seekter Web UI - sweep";
  const prefillUrl = query ? (query.get("url") || "") : "";
  const prefillCompany = query ? (query.get("company") || "") : "";
  const log = el("pre", { class: "console", id: "live-run", style: "display:none;margin-top:10px" }, "running...");
  appRoot.replaceChildren(
    el("h1", { class: "page" }, "Sweep & add"),
    el("p", { class: "sub" }, "Step 1: run the freehire sweep. Step 2: check the candidates. Step 3: add with the form, all logs on screen."),
    el("div", { class: "panel" },
      el("h3", {}, "Step 1: run the freehire sweep"),
      el("div", { class: "too" },
        primary("Run sweep", async () => {
          const r = await api("/api/jobs/sweep", { json: {} });
          if (!r.ok) return toast(r.error, true);
          log.style.display = "block";
          pollSweep(r.job);
        }),
        el("span", { class: "who" }, "needs profile/search.json (freehire.queries, freehire.categories, title_keep); writes runs/<today>/freehire.json")),
      log),
    el("div", { class: "panel" }, el("h3", {}, "Step 2: candidates"),
      el("div", { id: "cands" }, el("div", { class: "empty" }, "loading"))),
    el("div", { style: "height:16px" }),
    addFormPanel(prefillUrl, prefillCompany),
    el("div", { style: "height:16px" }),
    el("div", { class: "panel" }, el("h3", {}, "History"),
      el("div", { id: "hist" }, el("div", { class: "empty" }, "loading"))));
  await loadHistory();
  await loadCandidates();
};

const addFormPanel = (prefillUrl, prefillCompany) => {
  const url = el("input", { type: "text", placeholder: "Posting URL, or a bare LinkedIn id", value: prefillUrl, id: "track-url" });
  const company = el("input", { type: "text", placeholder: "Company", value: prefillCompany, id: "track-company" });
  const role = el("input", { type: "text", placeholder: "Role", id: "track-role" });
  const status = el("select", {}, ["pending", "applied", "rejected"].map((o) => el("option", { value: o }, o)));
  const source = el("select", {}, ["freehire", "linkedin", "board", "manual"].map((o) => el("option", { value: o }, o)));
  const ats = el("input", { type: "text", placeholder: "optional; derived from the url when left empty" });
  const why = el("textarea", { placeholder: "why it fits the rules; written into the file as the record's reasoning" });
  const note = el("textarea", { placeholder: "notes; a pending posting with a CAPTCHA becomes a needs-you row with this line" });
  const force = el("input", { type: "checkbox" });
  const result = el("div");
  const doCheck = async () => {
    const data = await api("/api/check?url=" + encodeURIComponent(url.value) + "&company=" + encodeURIComponent(company.value));
    result.replaceChildren();
    const list = data.state === "DUP" ? data.matches : data.same_co;
    if (data.state !== "NEW") {
      result.append(el("div", {}, stateChip(data.state)));
      for (const m of list) {
        result.append(el("div", { class: "mini" }, el("div", { class: "lft" },
          el("b", {}, `${m.company} : ${m.role}`),
          el("div", { class: "next" }, `${m.status}${m.applied ? " | " + m.applied : ""} | ${m.path}`))));
      }
      result.append(el("div", { class: "sub" }, "Add anyway? Tick force below."));
    } else {
      result.append(el("div", { class: "empty" }, "NEW: safe to add."));
    }
  };
  const doAdd = async () => {
    const data = await api("/api/add", { json: {
      company: company.value, role: role.value, url: url.value, status: status.value,
      source: source.value, ats: ats.value, why: why.value, notes: note.value,
      force: force.checked } });
    if (!data.ok) return toast(data.error, true);
    toast("Tracked at " + data.path);
    route();
  };
  return el("div", { class: "panel" }, el("h3", {}, "Step 3: track a posting"),
    field("URL", url), field("Company", company), field("Role", role),
    el("div", { class: "grid", style: "grid-template-columns:1fr 1fr" },
      field("Status", status), field("Source", source)),
    field("ATS (optional)", ats),
    field("Why it fits", why), field("Note", note),
    el("label", { class: "check" }, force, "Add anyway, skipping the duplicate guard"),
    el("div", { class: "too" }, btn("Check first", doCheck), primary("Add to tracker", doAdd)), result);
};

const loadCandidates = async (date = null) => {
  const boxEl = document.getElementById("cands");
  if (!boxEl) return;
  boxEl.replaceChildren(el("div", { class: "empty" }, "loading"));
  const day = date || new Date().toISOString().slice(0, 10);
  const data = await api("/api/run/day?date=" + day);
  boxEl.replaceChildren();
  if (!data || !data.ok) {
    boxEl.append(el("div", { class: "empty" }, "No sweep output for today. Run the sweep above."));
    return;
  }
  boxEl.append(el("p", { class: "sub" }, day + " : " + data.candidates.length + " candidates"));
  if (!data.candidates.length) {
    boxEl.append(el("div", { class: "empty" }, "Zero candidates. Loosen the filters or widen the window."));
    return;
  }
  for (const c of data.candidates.slice(0, 40)) {
    boxEl.append(el("div", { class: "mini" },
      el("div", { class: "lft" },
        el("div", { style: "display:flex;gap:8px;align-items:center;flex-wrap:wrap" },
          el("a", { href: c.url, target: "_blank", rel: "noreferrer", style: "font-weight:600" }, esc(c.title || "(no title)")),
          el("span", { class: "chip chip-ghost" }, c.age + "d"),
          c.reality ? el("span", { class: "chip chip-ghost" }, esc(c.reality)) : null),
        el("div", { class: "next" }, [c.company, c.location].filter(Boolean).map(esc).join(" | "))),
      el("div", { class: "acts" },
        btn("Check", async () => {
          const r = await api("/api/check?url=" + encodeURIComponent(c.url) + "&company=" + encodeURIComponent(c.company || ""));
          toast(r.state === "NEW" ? "NEW: safe to add" : r.state, r.state !== "NEW");
        }),
        btn("Track form", () => {
          const u = document.getElementById("track-url");
          const cEl = document.getElementById("track-company");
          const rEl = document.getElementById("track-role");
          if (u) u.value = c.url || "";
          if (cEl) cEl.value = c.company || "";
          if (rEl) rEl.value = c.title || "";
        }))));
  }
};

/* report */
const renderReport = async () => {
  document.title = "Seekter Web UI - report";
  appRoot.replaceChildren(el("h1", { class: "page" }, "Report"),
    el("p", { class: "sub" }, "Numbers read from applications/ and runs/ only."),
    skeleton(3));
  const data = await api("/api/overview");
  if (!data.ok) return;
  const s = data.stats;
  const kpis = el("div", { class: "kpis" });
  for (const [label, value, tone] of [["Total tracked", s.total, "var(--ink)"],
    ["Sent", s.sent, "var(--ink)"],
    ["Response rate", s.response_rate == null ? "n/a" : Math.round(s.response_rate * 100) + "%", "var(--ink)"]]) {
    kpis.append(el("div", { class: "kpi" },
      el("b", { style: `color:${tone}` }, String(value)), el("span", {}, label)));
  }
  const hygiene = el("div", { class: "panel" }, el("h3", {}, "Hygiene"),
    el("div", { class: "too" },
      btn("Normalize dry run", async () => { const r = await api("/api/normalize", { json: { dry_run: true } }); toast(r.ok ? (r.report || "nothing would change") : r.error, !r.ok); }),
      btn("Normalize apply", async () => { const r = await api("/api/normalize", { json: { dry_run: false } }); toast(r.ok ? r.report : r.error, !r.ok); }),
      btn("Rebuild index", async () => { const r = await api("/api/index", { json: {} }); toast(r.ok ? (r.report || "rebuilt") : r.error, !r.ok); })));
  appRoot.replaceChildren(kpis, funnelPanel(s),
    el("div", { style: "height:16px" }), monthsPanel(data.months),
    el("div", { style: "height:16px" }), hygiene);
};

/* profile (read-only) */
const renderProfile = async () => {
  document.title = "Seekter Web UI - profile";
  appRoot.replaceChildren(el("h1", { class: "page" }, "Profile"),
    el("p", { class: "sub" }, "Read-only. profile/ is git-ignored; edit profile.md by hand or tell Seekter in chat."),
    skeleton(2));
  const data = await api("/api/profile");
  const box = el("div", { class: "grid" });
  if (!data.ok) { box.append(el("div", { class: "empty" }, esc(data.error))); return; }
  if (!data.has_profile) {
    box.append(el("div", { class: "empty" }, "No profile on this checkout. Run /seekter-init in Claude Code once, then refresh this page."));
  }
  if (data.missing_values.length) {
    box.append(el("div", { class: "panel" }, el("h3", {}, "Config missing"),
      el("div", { class: "row-list" }, data.missing_values.map((m) => el("div", { class: "mini" },
        el("div", { class: "lft" }, el("b", {}, m),
          el("div", { class: "next" }, "Fill it in profile/search.json; templates/search.example.json shows the shape.")))))));
  }
  const docs = el("div", { class: "panel" }, el("h3", {}, "Document files"));
  docs.append(data.documents.length
    ? el("div", { class: "row-list" }, data.documents.map((x) => el("div", { class: "mini" }, el("b", {}, x))))
    : el("div", { class: "empty" }, "No CVs under profile/documents/. Forms are filled from these files only."));
  box.append(docs,
    data.search && Object.keys(data.search).length
      ? el("div", { class: "panel" }, el("h3", {}, "profile/search.json"),
          el("pre", { class: "console", style: "max-height:260px;white-space:pre-wrap" },
            esc(JSON.stringify(data.search, null, 2)))) : null,
    data.profile_head ? el("div", { class: "panel" }, el("h3", {}, "profile/profile.md"),
      el("div", { class: "console", style: "max-height:420px;white-space:pre-wrap" }, esc(data.profile_head))) : null);
  appRoot.append(box);
};

/* ============================================================ router */
const NAV = {
  dashboard: renderDashboard,
  apps: renderApps,
  sweep: renderSweep,
  report: renderReport,
  profile: renderProfile,
};
const navigate = (route, params) => {
  location.hash = "#/" + route + (params ? "?" + params : "");
};
const route = () => {
  const hash = location.hash.replace(/^#\/?/, "");
  const [name, qs] = hash.split("?");
  const target = NAV[name] ? name : "dashboard";
  $$s(".nav a").forEach((a) => a.classList.toggle("on", a.dataset.nav === target));
  appRoot.replaceChildren();
  NAV[target](new URLSearchParams(qs || ""));
};
window.addEventListener("hashchange", route);
route();
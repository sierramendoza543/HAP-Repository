/* Scenario-Aware Comparative Residential Regulation Index — V1.0 pilot
   Static, local, offline app. Reads only data/data.json (a frozen export of release_v1 artifacts).
   No external network calls, no secrets, no server-side logic. */

const DOMAIN_LABELS = {
  land: "Land threshold & density (25%)",
  placement: "Building placement (15%)",
  parking: "Vehicle-parking burden (10%)",
  housing_entitlement: "Housing-form entitlement (35%)",
  process: "Discretionary-review burden (15%)",
};
const STATUS_CLASS = (status) => {
  if (!status) return "na";
  if (status.startsWith("confirmed")) return "confirmed";
  if (status.includes("caveat")) return "caveat";
  if (status.includes("not_applicable")) return "na";
  if (status.includes("pending") || status.includes("unresolved") || status.includes("review")) return "unresolved";
  return "excluded";
};

let DATA = null;
let state = { tab: "start", scenarioKey: null, variant: "1_baseline" };

async function boot() {
  try {
    const res = await fetch("data/data.json");
    if (!res.ok) throw new Error("fetch failed: " + res.status);
    DATA = await res.json();
  } catch (e) {
    document.getElementById("main").innerHTML =
      `<div class="panel"><strong>Could not load data/data.json.</strong><br/>` +
      `This app must be served over a local HTTP server (opening the file directly triggers browser ` +
      `CORS restrictions on local fetch). From this folder run:<br/><br/>` +
      `<code>python3 -m http.server 8787</code><br/><br/>then open ` +
      `<code>http://localhost:8787/</code> in your browser.<br/><br/><span class="muted">Technical detail: ${e}</span></div>`;
    return;
  }
  state.scenarioKey = DATA.bridgeport_scenarios[0].key;
  document.getElementById("app-title").textContent = DATA.meta.title;
  document.getElementById("app-subtitle").textContent = DATA.meta.subtitle;
  document.getElementById("app-version").textContent = DATA.meta.version;
  document.getElementById("app-warning").textContent = DATA.meta.warning;
  document.querySelectorAll("#tabs button").forEach(btn => {
    btn.addEventListener("click", () => { state.tab = btn.dataset.tab; render(); });
  });
  render();
}

function render() {
  document.querySelectorAll("#tabs button").forEach(b => b.classList.toggle("active", b.dataset.tab === state.tab));
  const main = document.getElementById("main");
  const renderers = { start: renderStart, compare: renderCompare, distribution: renderDistribution,
    sensitivity: renderSensitivity, evidence: renderEvidence, excluded: renderExcluded,
    methods: renderMethods, download: renderDownload };
  main.innerHTML = "";
  main.appendChild(renderers[state.tab]());
}

function el(tag, attrs = {}, children = []) {
  const n = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === "html") n.innerHTML = v; else if (k === "class") n.className = v; else n.setAttribute(k, v);
  }
  (Array.isArray(children) ? children : [children]).forEach(c => { if (c) n.appendChild(typeof c === "string" ? document.createTextNode(c) : c); });
  return n;
}

function bar(label, value, color, max = 100) {
  const row = el("div", { class: "bar-row" });
  row.appendChild(el("div", { class: "label" }, label));
  const track = el("div", { class: "bar-track" });
  if (value === null || value === undefined) {
    track.appendChild(el("div", { class: "small muted", style: "padding-left:6px;line-height:16px" }, "not applicable / excluded"));
  } else {
    track.appendChild(el("div", { class: "bar-fill", style: `width:${Math.max(2,(value/max)*100)}%;background:${color}` }));
  }
  row.appendChild(track);
  row.appendChild(el("div", { class: "bar-value" }, value === null || value === undefined ? "—" : value.toFixed(0)));
  return row;
}

function renderStart() {
  const gre = DATA.greenwich_benchmark;
  const bptVals = DATA.bridgeport_scenarios.map(s => s.R_s_baseline).filter(v => v !== null);
  const frag = el("div");
  frag.appendChild(el("div", { class: "panel" }, [
    el("h3", {}, "What this index measures"),
    el("p", {}, "A scenario-level pilot comparison across nine source-linked residential-regulation " +
      "variables (lot size, lot width, placement/setbacks, parking, 3+-unit entitlement, ADU entitlement, " +
      "density/unit cap, missing-middle entitlement, and discretionary-review burden), each scored 0 " +
      "(least restrictive) to 100 (most restrictive) against predeclared policy bands."),
    el("h3", {}, "What it does not measure"),
    el("p", {}, "Vertical capacity (height), site-intensity/coverage, and floor-area capacity are " +
      "excluded from this version's numeric aggregate (see Excluded Context tab) because no common, " +
      "source-backed cross-town scoring rubric was established for them. This is not a complete zoning " +
      "code, not a legal opinion, and not a causal estimate of housing production."),
  ]));
  const stats = el("div", { class: "grid2" });
  stats.appendChild(el("div", { class: "panel" }, [
    el("div", { class: "stat" }, [el("div", { class: "num" }, gre.R_s_baseline.toFixed(1)), el("div", { class: "lbl" }, "Greenwich RA-4 benchmark (0–100)")]),
    el("div", { class: "caption" }, `Domain coverage: ${(gre.coverage_fraction*100).toFixed(0)}%`),
  ]));
  stats.appendChild(el("div", { class: "panel" }, [
    el("div", { class: "stat" }, [el("div", { class: "num" }, `${bptVals.length}`), el("div", { class: "lbl" }, "Score-eligible Bridgeport scenarios")]),
    el("div", { class: "caption" }, `Median ${median(bptVals).toFixed(1)} · range ${Math.min(...bptVals).toFixed(1)}–${Math.max(...bptVals).toFixed(1)}`),
  ]));
  frag.appendChild(stats);
  frag.appendChild(el("div", { class: "panel" }, [
    el("h3", {}, "Release & evidence coverage"),
    el("p", { class: "small" }, `Release version ${DATA.meta.release_version}, generated ${DATA.meta.generated_at}. ` +
      `Frozen scoring-input hash: `, ),
    el("p", {}, el("code", {}, DATA.meta.freeze_file_hash)),
    el("p", { class: "small" }, `Bridgeport candidate scenarios: ${DATA.release_manifest.coverage_statistics.bridgeport_candidate_scenarios} · ` +
      `eligible: ${DATA.release_manifest.coverage_statistics.bridgeport_eligible_scenarios} · ` +
      `excluded (reason retained): ${DATA.release_manifest.coverage_statistics.bridgeport_excluded_scenarios}.`),
  ]));
  return frag;
}

function renderCompare() {
  const frag = el("div");
  const gre = DATA.greenwich_benchmark;
  const sel = el("select", { id: "scenario-select" });
  DATA.bridgeport_scenarios.forEach(s => sel.appendChild(el("option", { value: s.key, ...(s.key === state.scenarioKey ? { selected: "selected" } : {}) }, s.label)));
  sel.addEventListener("change", () => { state.scenarioKey = sel.value; render(); });
  const bpt = DATA.bridgeport_scenarios.find(s => s.key === state.scenarioKey);

  const header = el("div", { class: "panel" }, [
    el("div", { class: "flex-between" }, [el("h3", { style: "margin:0" }, "Select a Bridgeport scenario"), sel]),
    el("p", { class: "small muted" }, "District, building form, and site/frontage condition define each scenario (r_d,b,f,k model)."),
  ]);
  frag.appendChild(header);

  const cols = el("div", { class: "grid2" });
  cols.appendChild(scenarioCard("Greenwich RA-4 (benchmark)", gre, "var(--greenwich)"));
  cols.appendChild(scenarioCard(bpt.label, bpt, "var(--bridgeport)"));
  frag.appendChild(cols);

  const diff = bpt.R_s_baseline - gre.R_s_baseline;
  frag.appendChild(el("div", { class: "panel" }, [
    el("p", {}, [
      el("strong", {}, `${bpt.label}`), ` has a V1.0 index value of ${bpt.R_s_baseline.toFixed(1)}, which is `,
      el("strong", {}, `${Math.abs(diff).toFixed(1)} points ${diff < 0 ? "lower" : diff > 0 ? "higher" : "equal"}`),
      ` than the Greenwich RA-4 benchmark (${gre.R_s_baseline.toFixed(1)}) under the V1.0 protocol. `,
    ]),
    el("p", { class: "small muted" }, "This describes relative position on the V1.0 index only — it is not a claim that one town is " +
      "\"more\" or \"less\" restrictive overall, and it compares one Bridgeport scenario to Greenwich's single documented district."),
  ]));
  return frag;
}

function scenarioCard(title, s, color) {
  const panel = el("div", { class: "panel" });
  panel.appendChild(el("h3", {}, title));
  panel.appendChild(el("div", { class: "stat" }, [el("div", { class: "num", style: `color:${color}` }, s.R_s_baseline.toFixed(1)), el("div", { class: "lbl" }, "V1.0 index (0–100)")]));
  panel.appendChild(el("p", { class: "caption" }, `Coverage: ${(s.coverage_fraction*100).toFixed(0)}% of domain weight applied`));
  const domains = el("div", {});
  for (const [k, v] of Object.entries(s.domains)) domains.appendChild(bar(DOMAIN_LABELS[k], v, color));
  panel.appendChild(domains);
  if (s.excluded_variables.length) {
    const d = el("details", {});
    d.appendChild(el("summary", {}, `${s.excluded_variables.length} variable(s) not scored for this scenario`));
    const ul = el("ul", { class: "small" });
    s.excluded_variables.forEach(e => ul.appendChild(el("li", {}, `${e.variable}: ${e.reason}`)));
    d.appendChild(ul);
    panel.appendChild(d);
  }
  if (s.shared_underlying_rule_v7_v11) {
    panel.appendChild(el("p", { class: "small" }, el("span", { class: "pill caveat" }, "dependency flag"), " V7 and V11 share the same underlying citation here — V11's weight was halved to avoid double-counting."));
  }
  return panel;
}

function renderDistribution() {
  const frag = el("div");
  const vals = DATA.bridgeport_scenarios.map(s => s.R_s_baseline).filter(v => v !== null);
  const gre = DATA.greenwich_benchmark.R_s_baseline;
  frag.appendChild(el("div", { class: "panel" }, [
    el("h3", {}, "Distribution of eligible Bridgeport scenario scores"),
    el("p", { class: "small muted" }, `n = ${vals.length} scenarios. This is a distribution, not a citywide average or ranking.`),
    histogramSVG(vals, gre),
  ]));

  const byDistrict = {};
  DATA.bridgeport_scenarios.forEach(s => { (byDistrict[s.district] ??= []).push(s.R_s_baseline); });
  const table1 = el("table");
  table1.appendChild(el("tr", {}, [el("th", {}, "District"), el("th", {}, "n"), el("th", {}, "Min"), el("th", {}, "Median"), el("th", {}, "Max")]));
  Object.entries(byDistrict).sort().forEach(([d, v]) => {
    table1.appendChild(el("tr", {}, [el("td", {}, d), el("td", {}, `${v.length}`), el("td", {}, Math.min(...v).toFixed(1)), el("td", {}, median(v).toFixed(1)), el("td", {}, Math.max(...v).toFixed(1))]));
  });
  frag.appendChild(el("div", { class: "panel" }, [el("h3", {}, "By district"), table1]));

  const byType = {};
  DATA.bridgeport_scenarios.forEach(s => { (byType[s.building_form] ??= []).push(s.R_s_baseline); });
  const table2 = el("table");
  table2.appendChild(el("tr", {}, [el("th", {}, "Building form"), el("th", {}, "n"), el("th", {}, "Min"), el("th", {}, "Median"), el("th", {}, "Max")]));
  Object.entries(byType).sort().forEach(([t, v]) => {
    table2.appendChild(el("tr", {}, [el("td", {}, t), el("td", {}, `${v.length}`), el("td", {}, Math.min(...v).toFixed(1)), el("td", {}, median(v).toFixed(1)), el("td", {}, Math.max(...v).toFixed(1))]));
  });
  frag.appendChild(el("div", { class: "panel" }, [el("h3", {}, "By building type"), table2]));
  frag.appendChild(el("div", { class: "panel small muted" }, "Note: this view shows how eligible Bridgeport scenarios are distributed. It is explicitly not a citywide average or ranking."));
  return frag;
}

function histogramSVG(values, markerValue) {
  const W = 760, H = 220, pad = 30;
  const bins = 10, max = 100;
  const counts = new Array(bins).fill(0);
  values.forEach(v => { let b = Math.min(bins - 1, Math.floor(v / (max / bins))); counts[b]++; });
  const maxCount = Math.max(...counts, 1);
  const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svg.setAttribute("viewBox", `0 0 ${W} ${H}`);
  svg.setAttribute("width", "100%");
  svg.style.maxWidth = "760px";
  const bw = (W - 2*pad) / bins;
  counts.forEach((c, i) => {
    const h = (c / maxCount) * (H - 2*pad);
    const rect = document.createElementNS("http://www.w3.org/2000/svg", "rect");
    rect.setAttribute("x", pad + i*bw + 2); rect.setAttribute("y", H - pad - h);
    rect.setAttribute("width", bw - 4); rect.setAttribute("height", h);
    rect.setAttribute("class", "hist-bar");
    svg.appendChild(rect);
    const txt = document.createElementNS("http://www.w3.org/2000/svg", "text");
    txt.setAttribute("x", pad + i*bw + bw/2); txt.setAttribute("y", H - pad + 14);
    txt.setAttribute("text-anchor", "middle"); txt.setAttribute("font-size", "9"); txt.setAttribute("fill", "var(--muted)");
    txt.textContent = `${i*10}`;
    svg.appendChild(txt);
  });
  const mx = pad + (markerValue / max) * (W - 2*pad);
  const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
  line.setAttribute("x1", mx); line.setAttribute("x2", mx); line.setAttribute("y1", pad); line.setAttribute("y2", H - pad);
  line.setAttribute("stroke", "var(--greenwich)"); line.setAttribute("stroke-width", "2"); line.setAttribute("stroke-dasharray", "5,3");
  svg.appendChild(line);
  const label = document.createElementNS("http://www.w3.org/2000/svg", "text");
  label.setAttribute("x", mx + 4); label.setAttribute("y", pad); label.setAttribute("font-size", "11"); label.setAttribute("fill", "var(--greenwich)"); label.setAttribute("font-weight", "700");
  label.textContent = "Greenwich RA-4";
  svg.appendChild(label);
  return svg;
}

function median(arr) {
  const s = [...arr].sort((a,b) => a-b);
  const m = Math.floor(s.length/2);
  return s.length % 2 ? s[m] : (s[m-1]+s[m])/2;
}

function renderSensitivity() {
  const frag = el("div");
  const sel = el("select", { id: "variant-scenario-select" });
  DATA.bridgeport_scenarios.forEach(s => sel.appendChild(el("option", { value: s.key, ...(s.key === state.scenarioKey ? { selected: "selected" } : {}) }, s.label)));
  sel.addEventListener("change", () => { state.scenarioKey = sel.value; render(); });
  const bpt = DATA.bridgeport_scenarios.find(s => s.key === state.scenarioKey);

  frag.appendChild(el("div", { class: "panel" }, [
    el("div", { class: "flex-between" }, [el("h3", { style: "margin:0" }, "Selected scenario across all 6 required variants"), sel]),
    ...Object.entries(bpt.variants).map(([k, v]) => bar(k.replace(/_/g, " "), v, "var(--bridgeport)")),
  ]));

  const table = el("table");
  table.appendChild(el("tr", {}, ["Variant","Greenwich","Bpt min","Bpt median","Bpt max","% Bpt below Greenwich"].map(h => el("th", {}, h))));
  DATA.sensitivity_summary.forEach(r => {
    table.appendChild(el("tr", {}, [
      el("td", {}, r.variant.replace(/_/g, " ")), el("td", {}, Number(r.greenwich_benchmark).toFixed(1)),
      el("td", {}, Number(r.bridgeport_min).toFixed(1)), el("td", {}, Number(r.bridgeport_median).toFixed(1)),
      el("td", {}, Number(r.bridgeport_max).toFixed(1)), el("td", {}, `${Number(r.pct_bridgeport_below_benchmark).toFixed(0)}%`),
    ]));
  });
  const pctVals = DATA.sensitivity_summary.map(r => Number(r.pct_bridgeport_below_benchmark));
  const stable = Math.max(...pctVals) - Math.min(...pctVals) < 25;
  frag.appendChild(el("div", { class: "panel" }, [
    el("h3", {}, "All 6 required variants"), table,
    el("p", { class: stable ? "small" : "small", html: stable
        ? `<strong>Stable:</strong> the share of Bridgeport scenarios below the Greenwich benchmark stays within ${Math.min(...pctVals).toFixed(0)}%–${Math.max(...pctVals).toFixed(0)}% across every required variant.`
        : `<strong>Unstable:</strong> the comparison shifts materially across variants (range ${Math.min(...pctVals).toFixed(0)}%–${Math.max(...pctVals).toFixed(0)}%) — treat the headline comparison with caution.` }),
  ]));
  return frag;
}

function renderEvidence() {
  const frag = el("div");
  const allScenarios = [DATA.greenwich_benchmark, ...DATA.bridgeport_scenarios];
  const sel = el("select", { id: "evidence-scenario-select" });
  allScenarios.forEach(s => sel.appendChild(el("option", { value: s.key, ...(s.key === state.scenarioKey ? { selected: "selected" } : {}) }, s.label)));
  sel.addEventListener("change", () => { state.scenarioKey = sel.value; render(); });
  const s = allScenarios.find(x => x.key === state.scenarioKey) || allScenarios[0];

  frag.appendChild(el("div", { class: "panel" }, [
    el("div", { class: "flex-between" }, [el("h3", { style: "margin:0" }, "Evidence Explorer"), sel]),
    el("p", { class: "small muted" }, "Shows the full 12-variable framework for this scenario, not only the 9 scored variables."),
  ]));

  const table = el("table");
  table.appendChild(el("tr", {}, ["Variable","Score (0–100)","Value","Source page","Section","Status"].map(h => el("th", {}, h))));
  const ALL_VARS = ["V1","V2","V3","V4","V5","V6","V7","V8","V9","V10","V11","V12"];
  ALL_VARS.forEach(v => {
    const data = s.variables[v];
    const excl = s.excluded_variables.find(e => e.variable === v);
    if (data) {
      table.appendChild(el("tr", {}, [
        el("td", {}, v), el("td", {}, data.score === null ? "—" : data.score.toFixed(0)),
        el("td", {}, data.value_categorical || (data.value_numeric ?? "—").toString()),
        el("td", {}, data.source_page || "—"), el("td", {}, data.section || "—"),
        el("td", {}, el("span", { class: "pill confirmed" }, "scored")),
      ]));
    } else {
      const reason = excl ? excl.reason : "not part of V1.0 score core (excluded context variable)";
      table.appendChild(el("tr", {}, [
        el("td", {}, v), el("td", {}, "—"), el("td", { class: "small muted" }, reason),
        el("td", {}, "—"), el("td", {}, "—"),
        el("td", {}, el("span", { class: `pill ${["V3","V4","V10"].includes(v) ? "na" : "excluded"}` }, ["V3","V4","V10"].includes(v) ? "context only" : "excluded")),
      ]));
    }
  });
  frag.appendChild(el("div", { class: "panel" }, [el("h3", {}, `${s.label} — all 12 variables`), table]));
  return frag;
}

function renderExcluded() {
  const frag = el("div");
  frag.appendChild(el("div", { class: "panel" }, [
    el("h3", {}, "Not included in the V1.0 numeric score"),
    ...DATA.excluded_constructs.map(c => el("div", { class: "panel", style: "margin-bottom:8px" }, [
      el("div", { class: "flex-between" }, [el("strong", {}, `${c.variable} — ${c.label}`), el("span", { class: "pill na" }, "context only")]),
      el("p", { class: "small" }, c.reason),
    ])),
    el("p", { class: "small muted" }, "These remain visible in the Evidence Explorer for every scenario — they are never silently dropped or scored as zero."),
  ]));
  return frag;
}

function renderMethods() {
  const frag = el("div");
  const m = DATA.methodology;
  frag.appendChild(el("div", { class: "panel" }, [
    el("h3", {}, "Formula"),
    el("pre", { class: "small", style: "white-space:pre-wrap" }, JSON.stringify(m.domain_formula, null, 2)),
    el("p", { class: "small muted" }, "Weights are theory-driven design parameters, not empirically estimated."),
  ]));
  frag.appendChild(el("div", { class: "panel" }, [
    el("h3", {}, "Frozen rubrics (V1.0 score core)"),
    el("table", {}, [
      el("tr", {}, ["Variable","Direction","No-minimum treatment","Source gate"].map(h => el("th", {}, h))),
      ...DATA.rubrics.map(r => el("tr", {}, [el("td", {}, r.variable_id), el("td", { class: "small" }, r.direction), el("td", { class: "small" }, r.no_minimum_treatment), el("td", { class: "small" }, r.source_gate)])),
    ]),
  ]));
  frag.appendChild(el("div", { class: "panel" }, [
    el("h3", {}, "Limitations"),
    el("ul", {}, DATA.score_manifest.limitations.map(l => el("li", { class: "small" }, l))),
    el("p", {}, el("strong", {}, DATA.score_manifest.no_townwide_ranking_statement)),
  ]));
  return frag;
}

function renderDownload() {
  const frag = el("div");
  const files = [
    ["Frozen scoring input (CSV)", "downloads/comparative_scoring_input_freeze_v1.csv"],
    ["Scenario scores, all variants (CSV)", "downloads/comparative_scenario_scores_v1.csv"],
    ["Sensitivity results, long format (CSV)", "downloads/comparative_score_sensitivity_results_v1.csv"],
    ["Variable-level scores (CSV)", "downloads/comparative_scenario_variable_scores_v1.csv"],
    ["Exclusion log (CSV)", "downloads/comparative_score_exclusion_log_v1.csv"],
    ["Scoring rubrics (CSV)", "downloads/comparative_scoring_rubrics_v1.csv"],
    ["Methodology (JSON)", "downloads/comparative_score_methodology_v1.json"],
    ["Full release manifest (JSON)", "downloads/comparative_residential_regulation_index_v1_manifest.json"],
  ];
  const list = el("div", { class: "dl-list" });
  files.forEach(([label, href]) => list.appendChild(el("a", { href, download: "" }, `⬇ ${label}`)));
  frag.appendChild(el("div", { class: "panel" }, [
    el("h3", {}, "Download the actual release-v1 artifacts"),
    el("p", { class: "small muted" }, "These are copies of the real files produced by Notebooks 14–15, not re-derived for this app."),
    list,
  ]));
  frag.appendChild(el("div", { class: "panel" }, [
    el("h3", {}, "Version metadata"),
    el("p", { class: "small" }, `Release: ${DATA.meta.release_version}`),
    el("p", { class: "small" }, "Frozen input hash: ", el("code", {}, DATA.meta.freeze_file_hash)),
    el("p", { class: "small" }, `Generated: ${DATA.meta.generated_at}`),
  ]));
  return frag;
}

boot();

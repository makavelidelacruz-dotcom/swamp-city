import WebSocket from "ws";
const KEY = process.argv[2], PORT = process.env.PORT || 7071;
const sleep = ms => new Promise(r => setTimeout(r, ms));
function client() {
  const c = { nodes: new Map(), ids: {} };
  c.ready = new Promise(res => {
    c.ws = new WebSocket("ws://localhost:" + PORT, ["networked-dom-v0.1"]);
    c.ws.on("message", raw => { let msgs = JSON.parse(raw.toString()); if (!Array.isArray(msgs)) msgs = [msgs];
      for (const m of msgs) {
        if (m.type === "snapshot") { add(c, m.snapshot, null); res(); }
        else if (m.type === "childrenChanged") { const par = c.nodes.get(m.nodeId); (m.removedNodes || []).forEach(id => { drop(c, id); if (par) par.children = par.children.filter(x => x !== id); }); (m.addedNodes || []).forEach(n => { add(c, n, m.nodeId); if (par && n) par.children.push(n.nodeId); }); }
        else if (m.type === "attributeChange") { const n = c.nodes.get(m.nodeId); if (!n) continue; const list = m.attributes || [{ attribute: m.attribute, newValue: m.newValue }]; for (const a of list) { if (a.newValue === null) delete n.attributes[a.attribute]; else n.attributes[a.attribute] = a.newValue; } }
        else if (m.type === "ping") c.ws.send(JSON.stringify({ type: "pong", pong: m.ping }));
      } });
  });
  return c;
}
function drop(c, id) { const n = c.nodes.get(id); if (!n) return; n.children.forEach(ch => drop(c, ch)); c.nodes.delete(id); }
function add(c, n, parent) { if (!n) return; c.nodes.set(n.nodeId, { nodeId: n.nodeId, tag: String(n.tag || "").toLowerCase(), attributes: Object.assign({}, n.attributes || {}), parent, children: (n.children || []).map(x => x.nodeId) }); if (n.attributes && n.attributes.id) c.ids[n.attributes.id] = n.nodeId; (n.children || []).forEach(ch => add(c, ch, n.nodeId)); }
const send = (c, nodeId, name, params) => c.ws.send(JSON.stringify({ type: "event", nodeId, name, bubbles: true, params: params || {} }));
const all = c => [...c.nodes.values()];
const labels = (c, re) => all(c).filter(n => n.tag === "m-label" && re.test(n.attributes.content || ""));
const state = c => JSON.parse(c.nodes.get(c.ids["hb-state"]).attributes["data-state"]);
let fails = 0; const check = (ok, m) => { console.log((ok ? "PASS " : "FAIL ") + m); if (!ok) fails++; };
const A = client(); await A.ready;
const pulls = labels(A, /^PULL$/), dice = labels(A, /^GATOR DICE$/), megas = labels(A, /^JACKPOT/);
check(pulls.length >= 16, "slot machines: " + pulls.length);
check(megas.length === 2, "two Mega Gator machines with a jackpot display");
check(dice.length === 4, "two Gator Dice tables (titles front and back)");
const models = all(A).filter(n => n.tag === "m-model").map(n => n.attributes.src || "");
check(models.some(s => /wheel-spin|b4ac4ffa01d4d5c79937f40672d5c43b849214cfe8d9ddc6a11bdf02ecf64afa/.test(s)) && models.some(s => /wheel-frame|219a129e86ee1dc14afcbdc9b5cd28669848fc68fbc24c4fa777a75779d74e50/.test(s)), "modeled wheel and frame");
// free play: pull a lever -> each reel gets a time-synced spin of several turns, ending on a reel symbol, staggered left to right
const kids = n => n.children.map(id => A.nodes.get(id)).filter(Boolean);
const animsOf = (n, attr) => kids(n).filter(c => c.tag === "m-attr-anim" && c.attributes.attr === attr);
const reelsOf = p => kids(A.nodes.get(p.parent)).filter(n => n.tag === "m-model" && animsOf(n, "rx").length + (/slot-reel/.test(n.attributes.src) ? 1 : 0) > 0 && !/slot-(purple|teal|red|mega|lever)/.test(n.attributes.src));
send(A, pulls[0].nodeId, "click"); await sleep(400);
const reels = reelsOf(pulls[0]).filter(n => animsOf(n, "rx").length === 1 && animsOf(n, "rx")[0].attributes["ping-pong"] !== "true");
check(reels.length === 3, "pulling the lever starts a spin animation on all 3 reels (" + reels.length + ")");
const ra = reels.map(n => animsOf(n, "rx")[0].attributes);
check(ra.every(a => +a["start-time"] > 0 && +a.start - +a.end >= 1800), "each reel spins at least 5 full turns from a synced start time");
check(ra.every(a => (((90 - +a.end) / 45 - 0.5) % 1 + 1) % 1 < 1e-6), "each reel stops exactly on a symbol");
check(+ra[0].duration < +ra[1].duration && +ra[1].duration < +ra[2].duration, "reels stop one after another, left to right");
const lever = kids(A.nodes.get(pulls[0].parent)).find(n => animsOf(n, "rx").some(a => a.attributes["ping-pong"] === "true"));
check(!!lever, "the lever pulls down and springs back");
await sleep(3000);
check(labels(A, /free play|No match/).length >= 1, "free play result shown");
// dice: thrown from the rim, bounce, tumble, and land showing the faces on the screen
await sleep(2000); send(A, dice[0].nodeId, "click"); await sleep(400);
const diceNodes = all(A).filter(n => n.tag === "m-model" && animsOf(n, "rx").length && animsOf(n, "rz").length && !animsOf(n, "ry").length);
const tossed = diceNodes.filter(n => { const hop = A.nodes.get(n.parent); const pos = hop && A.nodes.get(hop.parent); return hop && pos && animsOf(hop, "y").length && animsOf(pos, "x").length; });
check(tossed.length === 2, "both dice fly in, bounce and tumble (" + tossed.length + ")");
const hopA = A.nodes.get(tossed[0].parent), posA = A.nodes.get(hopA.parent);
check(animsOf(hopA, "y")[0].attributes.easing === "easeOutBounce" && +animsOf(hopA, "y")[0].attributes.start > 0.5, "dice drop onto the felt and bounce");
const tableCentre = [68, null];
await sleep(2400);
const shown = labels(A, /^\d \+ \d/)[0];
const want = shown ? shown.attributes.content.match(/^(\d) \+ (\d)/).slice(1).map(Number) : [];
const faceUp = (rx, rz) => { // which face points up for R = Rx * Rz (model has no yaw)
  const r = d => d * Math.PI / 180, cx = Math.cos(r(rx)), sx = Math.sin(r(rx)), cz = Math.cos(r(rz)), sz = Math.sin(r(rz));
  const N = { 1: [0, 1, 0], 2: [0, 0, 1], 3: [1, 0, 0], 4: [-1, 0, 0], 5: [0, 0, -1], 6: [0, -1, 0] };
  for (const [v, [x, y, z]] of Object.entries(N)) { const x1 = cz * x - sz * y, y1 = sz * x + cz * y, z1 = z; const y2 = cx * y1 - sx * z1; if (y2 > 0.99) return +v; }
  return 0; };
const got = tossed.map(n => faceUp(+animsOf(n, "rx")[0].attributes.end, +animsOf(n, "rz")[0].attributes.end)).sort();
check(want.length === 2 && JSON.stringify(got) === JSON.stringify([...want].sort()), "dice land showing exactly the rolled faces " + JSON.stringify(want) + " vs " + JSON.stringify(got));
const ends = tossed.map(n => { const p = A.nodes.get(A.nodes.get(n.parent).parent); return [+animsOf(p, "x")[0].attributes.end, +animsOf(p, "z")[0].attributes.end]; });
check(ends.every(([x, z]) => Math.hypot(x - 68, Math.min(Math.abs(z - (-30)), Math.abs(z - (-10)))) < 1.3) && Math.hypot(ends[0][0] - ends[1][0], ends[0][1] - ends[1][1]) > 0.3, "dice land on the felt, apart from each other");
await sleep(2500);
// bet kiosks
const kioskCounts = labels(A, /BETS OPEN DURING LUCKY WHEEL/);
check(kioskCounts.length === 4, "4 bet kiosks with a bet counter");
// check in, start LUCKY WHEEL, then play until a win pays the team
send(A, A.ids["signup"], "prompt", { value: "Tester" }); await sleep(400);
send(A, A.ids["hb-casino"], "click", { key: KEY }); await sleep(400);
check(state(A).active === "casino", "host starts LUCKY WHEEL");
send(A, kioskCounts[1].nodeId, "click"); await sleep(400);
check(labels(A, /^1 BET ON /).length === 1 && labels(A, /^NO BETS YET$/).length === 3, "placing a bet updates that kiosk's counter");
let wins = 0, rolls = 0;
for (let i = 0; i < 26 && state(A).round[0] === 0; i++) {
  const p = pulls[i % pulls.length]; send(A, p.nodeId, "click"); await sleep(5200);
  if (state(A).round[0] > 0) wins++;
  if (i % 2 === 0) { send(A, dice[0].nodeId, "click"); rolls++; await sleep(5200); }
}
check(state(A).round[0] > 0, "floor games pay the player's crew (GATORS) during the round: " + JSON.stringify(state(A).round));
await sleep(Math.max(0, state(A).phaseEnd ? 0 : 0)); for (let w = 0; w < 30 && !/SPINNING|LANDED/.test(state(A).games.casino); w++) await sleep(1000); await sleep(1500);
const wheelSpin = all(A).find(n => n.tag === "m-group" && n.children.some(id => { const m = A.nodes.get(id); return m && /wheel-spin|b4ac4ffa01d4d5c79937f40672d5c43b849214cfe8d9ddc6a11bdf02ecf64afa/.test(m.attributes.src || ""); }));
check(+wheelSpin.attributes.rz < 0, "the wheel has spun (rz " + wheelSpin.attributes.rz + ")");
send(A, A.ids["hb-stop"], "click", { key: KEY }); await sleep(300);
console.log(fails ? fails + " FAILED" : "ALL PASSED"); process.exit(0);

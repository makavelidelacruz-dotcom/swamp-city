// Game checks against a running server (port 7071 or PORT): lights budget, gator walk-over pickup and throne
// delivery, Stop -> winner + celebration, Bank Job grab and drop at the centred board, countdown in 10 s steps.
//   HOST_KEY=<code used by the server> node gametest.mjs
import WebSocket from "ws";
const KEY = process.env.HOST_KEY, sleep = ms => new Promise(r => setTimeout(r, ms));
function client() {
  const c = { nodes: new Map(), ids: {} };
  c.ready = new Promise(res => {
    c.ws = new WebSocket("ws://127.0.0.1:" + (process.env.PORT || 7071), ["networked-dom-v0.1"]);
    c.ws.on("message", raw => { let m = JSON.parse(raw.toString()); if (!Array.isArray(m)) m = [m]; for (const x of m) {
      if (x.type === "snapshot") { c.nodes.clear(); add(c, x.snapshot, null); res(); }
      else if (x.type === "childrenChanged") { (x.removedNodes || []).forEach(id => drop(c, id)); (x.addedNodes || []).forEach(n => add(c, n, x.nodeId)); }
      else if (x.type === "attributeChange") { const n = c.nodes.get(x.nodeId); if (n) for (const a of (x.attributes || [{ attribute: x.attribute, newValue: x.newValue }])) { if (a.newValue === null) delete n.attributes[a.attribute]; else n.attributes[a.attribute] = a.newValue; } }
      else if (x.type === "ping") c.ws.send(JSON.stringify({ type: "pong", pong: x.ping })); } });
  });
  return c;
}
function add(c, n, parent) { if (!n) return; c.nodes.set(n.nodeId, { nodeId: n.nodeId, tag: String(n.tag || "").toLowerCase(), attributes: Object.assign({}, n.attributes || {}), parent, kids: (n.children || []).map(k => k.nodeId) }); if (n.attributes && n.attributes.id) c.ids[n.attributes.id] = n.nodeId; (n.children || []).forEach(ch => add(c, ch, n.nodeId)); }
function drop(c, id) { const n = c.nodes.get(id); if (!n) return; (n.kids || []).forEach(k => drop(c, k)); c.nodes.delete(id); }
const send = (c, id, name, p) => c.ws.send(JSON.stringify({ type: "event", nodeId: id, name, bubbles: true, params: p || {} }));
const find = (c, f) => [...c.nodes.values()].filter(f);
const A = (n, k) => +n.attributes[k] || 0;
const state = c => JSON.parse(c.nodes.get(c.ids["hb-state"]).attributes["data-state"]);
const host = (c, cmd) => send(c, c.ids["hb-" + cmd], "click", { key: KEY });
let fails = 0; const check = (ok, m) => { console.log((ok ? "PASS " : "FAIL ") + m); if (!ok) fails++; };

const o = client(); await o.ready;
check(find(o, n => n.tag === "m-light").length <= 8, "8-light budget: " + find(o, n => n.tag === "m-light").length + " lights");
check(find(o, n => n.tag === "m-cylinder" && n.attributes.radius === "0.85").length === 0, "no see-through gator rings");
const grass = find(o, n => /ground-grass/.test(n.attributes.src || "") && n.attributes["collision-interval"])[0];
const throne = find(o, n => n.tag === "m-cylinder" && n.attributes.radius === "4.5")[0];
const toL = (m, x, z) => { const a = A(m, "ry") * Math.PI / 180, c = Math.cos(a), s = Math.sin(a), dx = x - A(m, "x"), dz = z - A(m, "z"); return { x: c * dx - s * dz, z: s * dx + c * dz }; };
const stand = (p, x, z) => { const l = toL(grass, x, z); send(p, grass.nodeId, "collisionmove", { position: { x: l.x, y: 0.1, z: l.z } }); };

// GATOR ROUND-UP: walk onto a loose gator, carry it to the throne
const p = client(); await p.ready;
send(p, p.ids.signup, "prompt", { value: "Tester" }); await sleep(400);
host(o, "arena"); await sleep(800);
check(state(o).active === "arena", "host starts the Gator Round-Up");
const wild = find(o, n => n.tag === "m-group" && n.attributes["data-game"] === "arena" && n.attributes.y === "0.17");
check(wild.length === 56, "56 loose gators: " + wild.length);
const gx = A(wild[0], "x"), gz = A(wild[0], "z");
stand(p, gx + 0.8, gz); await sleep(500);
check(/1 CARRIED/.test(state(o).games.arena), "walk-over pickup: " + state(o).games.arena.split("|")[3]);
send(p, throne.nodeId, "collisionmove", { position: { x: 0.5, y: 0.18, z: 0.3 } }); await sleep(500);
check(state(o).round[0] + state(o).round[1] + state(o).round[2] + state(o).round[3] === 1, "throne delivery scores: " + JSON.stringify(state(o).round));
const clock = state(o).games.arena.match(/(\d+):(\d\d) LEFT/);
check(clock && +clock[2] % 10 === 0, "countdown in 10 s steps: " + (clock && clock[0]));
// Stop -> winner on the big screen + celebration (6 spots x 5 stars x 5 bars, 6 x 4 mascots)
host(o, "stop"); await sleep(5000);
check(/WIN GATOR PIT/.test(state(o).note), "Stop announces the winner: " + state(o).note);
check(find(o, n => n.tag === "m-cube" && n.attributes.color === "#ffd23f").length === 150, "celebration: 150 gold star bars lit");
check(find(o, n => n.tag === "m-model" && n.attributes.sx === "14").length === 24, "celebration: 24 giant mascots");

// BANK JOB: click the vault, click your own crew's centred drop board
host(o, "heist"); await sleep(800);
check(find(o, n => n.tag === "m-cube" && n.attributes.color === "#ffd23f").length === 0, "starting a game clears the celebration");
const strobes = () => find(o, n => n.tag === "m-attr-anim" && n.attributes.attr === "emissive");
check(strobes().length === 14, "Bank Job: police scene up, 14 flashing light bars/strobes (5 cruisers, 2 helicopters): " + strobes().length);
check(strobes().every(n => +n.attributes.end <= 1 && +n.attributes.start <= 1), "flashing stays at level 1 or lower");
check(find(o, n => n.tag === "m-light").length <= 8, "still 8 lights at most during the Bank Job");
const vault = o.ids.vault != null ? o.ids.vault : find(o, n => /CLICK THE VAULT/.test(n.attributes.content || ""))[0].nodeId;
send(p, vault, "click", {}); await sleep(500);
check(/1 ON THE RUN/.test(state(o).games.heist), "vault grab: " + state(o).games.heist);
const crew = JSON.parse(o.nodes.get(o.ids["hb-state"]).attributes["data-roster"]).findIndex(l => l.includes("Tester"));
const boards = find(o, n => n.attributes.content === "DROP LOOT");
// the label sits on the hideout group; pick the board whose hideout is this crew's (team order: NE, SW, SE, NW)
const H = [[125, -145], [-125, 105], [125, 105], [-125, -145]][crew];
const board = boards.find(b => { const g = o.nodes.get(b.parent); return A(g, "x") === H[0] && A(g, "z") === H[1]; });
check(board && A(board, "x") === 0, "drop board centred on the door");
send(p, board.nodeId, "click", {}); await sleep(500);
check(/1 BAGS BANKED/.test(state(o).games.heist), "bag banked at the hideout: " + state(o).games.heist);
host(o, "stop"); await sleep(600);
check(strobes().length === 0, "police scene removed when the Bank Job ends");
host(o, "reset"); await sleep(300);
console.log(fails ? fails + " FAILED" : "ALL PASS"); process.exit(fails ? 1 : 0);

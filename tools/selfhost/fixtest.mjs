// Tests for the two patches: floor beats probe, and a reconnect keeps the crew.
import WebSocket from "ws";
const sleep = ms => new Promise(r => setTimeout(r, ms));
function client() {
  const c = { nodes: new Map(), ids: {} };
  c.ready = new Promise(res => {
    c.ws = new WebSocket("ws://127.0.0.1:" + (process.env.PORT || 7071), ["networked-dom-v0.1"]);
    c.ws.on("message", raw => { let m = JSON.parse(raw.toString()); if (!Array.isArray(m)) m = [m]; for (const x of m) { if (x.type === "snapshot") { c.nodes.clear(); add(c, x.snapshot, null); res(); } else if (x.type === "childrenChanged") { (x.removedNodes || []).forEach(id => c.nodes.delete(id)); (x.addedNodes || []).forEach(n => add(c, n, x.nodeId)); } else if (x.type === "attributeChange") { const n = c.nodes.get(x.nodeId); if (n) for (const a of (x.attributes || [{ attribute: x.attribute, newValue: x.newValue }])) n.attributes[a.attribute] = a.newValue; } else if (x.type === "ping") c.ws.send(JSON.stringify({ type: "pong", pong: x.ping })); } });
  });
  return c;
}
function add(c, n, parent) { if (!n) return; c.nodes.set(n.nodeId, { nodeId: n.nodeId, tag: String(n.tag || "").toLowerCase(), attributes: Object.assign({}, n.attributes || {}), parent }); if (n.attributes && n.attributes.id) c.ids[n.attributes.id] = n.nodeId; (n.children || []).forEach(ch => add(c, ch, n.nodeId)); }
const send = (c, id, name, p) => c.ws.send(JSON.stringify({ type: "event", nodeId: id, name, bubbles: true, params: p || {} }));
const find = (c, f) => [...c.nodes.values()].filter(f);
const A = (n, k) => +n.attributes[k] || 0;
const state = c => JSON.parse(c.nodes.get(c.ids["hb-state"]).attributes["data-state"]);
const roster = c => JSON.parse(c.nodes.get(c.ids["hb-state"]).attributes["data-roster"]);
let fails = 0; const check = (ok, m) => { console.log((ok ? "PASS " : "FAIL ") + m); if (!ok) fails++; };

const o = client(); await o.ready;
const grass = find(o, n => /ground-grass/.test(n.attributes.src || "") && n.attributes["collision-interval"])[0] || find(o, n => n.tag === "m-model" && n.attributes["collision-interval"] === "400")[0];
const probe = find(o, n => n.tag === "m-position-probe")[0];
const toL = (m, x, z) => { const a = A(m, "ry") * Math.PI / 180, c = Math.cos(a), s = Math.sin(a), dx = x - A(m, "x"), dz = z - A(m, "z"); return { x: c * dx - s * dz, z: s * dx + c * dz }; };
const stand = (p, x, z) => { const l = toL(grass, x, z); send(p, grass.nodeId, "collisionmove", { position: { x: l.x, y: 0.1, z: l.z } }); };
const mascotOf = () => find(o, n => n.tag === "m-attr-lerp" && n.attributes.attr === "x,y,z" && n.attributes.duration === "450").map(m => o.nodes.get(m.parent));

// 1. floor beats probe
const a = client(); await a.ready;
send(a, a.ids.signup, "prompt", { value: "Floory" }); await sleep(300);
stand(a, 120, -20); await sleep(400);
let g = mascotOf()[0];
check(g && A(g, "x") === 120 && A(g, "z") === -20, "mascot on the floor spot (120,-20): " + (g && [g.attributes.x, g.attributes.z]));
// an offset probe report 30 m away arrives while the floor is fresh: must be ignored
send(a, probe.nodeId, "positionmove", { elementRelative: { position: { x: 150, y: 0.5, z: 10 }, rotation: { x: 0, y: 0, z: 0 } } });
await sleep(400);
g = mascotOf()[0];
check(A(g, "x") === 120 && A(g, "z") === -20, "fresh floor: probe report ignored, mascot stays at " + [g.attributes.x, g.attributes.z]);
// no floor report for 2.5 s (jumped on a boat): the probe fills in
await sleep(2500);
send(a, probe.nodeId, "positionmove", { elementRelative: { position: { x: 150, y: 0.5, z: 10 }, rotation: { x: 0, y: 0, z: 0 } } });
await sleep(400);
g = mascotOf()[0];
check(A(g, "x") === 150 && A(g, "z") === 10, "no floor for 2 s: probe fills in, mascot at " + [g.attributes.x, g.attributes.z]);
stand(a, 121, -20); await sleep(400);
g = mascotOf()[0];
check(A(g, "x") === 121, "floor takes back over at once: x=" + g.attributes.x);

// 2. reconnect keeps the crew
const P = []; for (let i = 0; i < 10; i++) P.push(client()); await Promise.all(P.map(p => p.ready));
for (let i = 0; i < 10; i++) { send(P[i], P[i].ids.signup, "prompt", { value: "Kid" + i }); await sleep(80); }
await sleep(400);
const crewOf = name => roster(o).findIndex(l => l.includes(name));
const total = () => state(o).crews.reduce((x, y) => x + y, 0);
const before = crewOf("Kid2");
P[2].ws.close(); await sleep(600);
check(crewOf("Kid2") === -1, "Kid2 dropped from the roster on disconnect");
// make another crew smaller than Kid2's old one (its players leave), so a plain sign-up would NOT land on Kid2's crew
const who = [[a, "Floory"]].concat(P.map((p, i) => [p, "Kid" + i])).filter(([, n]) => n !== "Kid2");
const other = [0, 1, 2, 3].filter(c => c !== before).sort((x, y) => state(o).crews[x] - state(o).crews[y])[0];
for (const [p, n] of who) if (crewOf(n) === other && !(state(o).crews[before] > state(o).crews[other])) { p.ws.close(); await sleep(500); }
check(state(o).crews[before] > Math.min(...state(o).crews), "set-up: Kid2's old crew is not the smallest " + JSON.stringify(state(o).crews));
const back = client(); await back.ready;
send(back, back.ids.signup, "prompt", { value: "kid2" }); await sleep(500);
check(crewOf("kid2") === before, "Kid2 reconnects (new id, typed 'kid2') and rejoins crew " + before + ": now " + crewOf("kid2"));
check(find(back, n => n.tag === "m-label" && /Welcome back/.test(n.attributes.content || "")).length === 1, "private 'Welcome back' line shown");
const n0 = total();
check(n0 === roster(o).flat().length, "crew counts match the roster (" + n0 + " signed up): " + JSON.stringify(state(o).crews));
// the stored crew is used once: a second 'Kid2' is a newcomer (gets a suffix, smallest crew, no welcome back)
const dup = client(); await dup.ready;
let min = Math.min(...state(o).crews);
send(dup, dup.ids.signup, "prompt", { value: "Kid2" }); await sleep(400);
check(state(o).crews[crewOf("Kid2 2")] === min + 1, "second 'Kid2' goes to a smallest crew as 'Kid2 2'");
check(find(dup, n => n.tag === "m-label" && /Welcome back/.test(n.attributes.content || "")).length === 0, "...and is not told 'Welcome back'");
// a newcomer typing a CONNECTED player's name is a newcomer too
const twin = client(); await twin.ready;
min = Math.min(...state(o).crews);
send(twin, twin.ids.signup, "prompt", { value: "kid0" }); await sleep(400);
check(state(o).crews[crewOf("kid0 2")] === min + 1, "typing a connected player's name: smallest crew, as 'kid0 2'");
// a brand-new name still goes to the smallest crew
const fresh = client(); await fresh.ready;
min = Math.min(...state(o).crews);
send(fresh, fresh.ids.signup, "prompt", { value: "Newbie" }); await sleep(400);
check(state(o).crews[crewOf("Newbie")] === min + 1, "new player still balanced onto a smallest crew");
check(total() === n0 + 3, "final crew counts add up: " + JSON.stringify(state(o).crews));
console.log(fails ? fails + " FAILED" : "ALL PASS"); process.exit(fails ? 1 : 0);

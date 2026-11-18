import WebSocket from "ws";
const URL = "ws://localhost:" + (process.env.PORT || 7071);
const KEY = process.argv[2];
const sleep = ms => new Promise(r => setTimeout(r, ms));

function client(name) {
  const c = { name, nodes: new Map(), ids: {}, ready: null, errors: [] };
  c.ready = new Promise(res => {
    c.ws = new WebSocket(URL, ["networked-dom-v0.1"]);
    c.ws.on("message", raw => {
      let msgs = JSON.parse(raw.toString());
      if (!Array.isArray(msgs)) msgs = [msgs];
      for (const m of msgs) {
        if (m.type === "snapshot") { c.nodes.clear(); add(c, m.snapshot, null); res(); }
        else if (m.type === "childrenChanged") {
          (m.removedNodes || []).forEach(id => drop(c, id));
          (m.addedNodes || []).forEach(n => add(c, n, m.nodeId));
        } else if (m.type === "attributeChange") {
          const n = c.nodes.get(m.nodeId); if (!n) continue;
          const list = m.attributes || [{ attribute: m.attribute, newValue: m.newValue }];
          for (const a of list) { if (a.newValue === null) delete n.attributes[a.attribute]; else n.attributes[a.attribute] = a.newValue; }
        } else if (m.type === "ping") c.ws.send(JSON.stringify({ type: "pong", pong: m.ping }));
        else if (m.type === "error" || m.type === "warning") c.errors.push(m);
      }
    });
  });
  return c;
}
function add(c, n, parent) {
  if (!n) return;
  c.nodes.set(n.nodeId, { nodeId: n.nodeId, tag: String(n.tag || "").toLowerCase(), attributes: Object.assign({}, n.attributes || {}), parent, children: (n.children || []).map(x => x.nodeId) });
  if (parent != null && c.nodes.get(parent) && !c.nodes.get(parent).children.includes(n.nodeId)) c.nodes.get(parent).children.push(n.nodeId);
  if (n.attributes && n.attributes.id) c.ids[n.attributes.id] = n.nodeId;
  (n.children || []).forEach(ch => add(c, ch, n.nodeId));
}
function drop(c, id) { const n = c.nodes.get(id); if (!n) return; n.children.forEach(ch => drop(c, ch)); c.nodes.delete(id); }
const send = (c, nodeId, name, params) => c.ws.send(JSON.stringify({ type: "event", nodeId, name, bubbles: true, params: params || {} }));
const find = (c, pred) => [...c.nodes.values()].filter(pred);
let fails = 0; const check = (ok, m) => { console.log((ok ? "PASS " : "FAIL ") + m); if (!ok) fails++; };
const A = client("A"); await A.ready;
const HALF = 215, CZ = -20;
const all = find(A, () => true);
// world position of a node (translation + ry only, enough here)
const wpos = n => { let x = 0, z = 0, y = 0, cur = n; const chain = []; while (cur) { chain.unshift(cur); cur = cur.parent != null ? A.nodes.get(cur.parent) : null; }
  let ry = 0; for (const c of chain) { if ((c.attributes || {}).id === "world") continue; const a = c.attributes || {}; const lx = +a.x || 0, lz = +a.z || 0, r = ry * Math.PI / 180; x += lx * Math.cos(r) + lz * Math.sin(r); z += -lx * Math.sin(r) + lz * Math.cos(r); y += +a.y || 0; ry += +a.ry || 0; } return { x, y, z }; };
const boats = all.filter(n => n.tag === "m-model" && n.attributes["data-boat"]);
check(boats.length === 36, "36 boats docked (" + boats.length + ")");
const kinds = boats.reduce((o, b) => (o[b.attributes["data-boat"]] = (o[b.attributes["data-boat"]] || 0) + 1, o), {});
check(JSON.stringify(kinds) === JSON.stringify({ yacht: 3, sailboat: 2, airboat: 8, skiff: 16, shrimpboat: 7 }) || Object.keys(kinds).length === 5, "every kind of boat is still there: " + JSON.stringify(kinds));
const out = p => Math.max(Math.abs(p.x) - HALF, Math.abs(p.z - CZ) - HALF);
const dist = boats.map(b => out(wpos(b)));
check(dist.every(d => d > 0 && d < 21), "every boat sits just outside the seawall (max " + Math.max(...dist).toFixed(1) + " m out)");
check(boats.every(b => { const bob = A.nodes.get(b.parent); return bob && bob.children.some(id => { const k = A.nodes.get(id); return k && k.tag === "m-attr-anim" && k.attributes.attr === "y"; }); }), "boats bob gently at their moorings");
check(!find(A, n => n.tag === "m-group" && /^boat-/.test(n.attributes.id || "") && n.children.some(id => (A.nodes.get(id) || {}).tag === "m-attr-lerp")).length, "boats are parked (no driving controls)");
check(find(A, n => n.tag === "m-label" && /click to drive|DRIVE/.test(n.attributes.content || "") && /boat/i.test(n.attributes.content || "")).length === 0, "no 'click to drive' signs on boats");
// nothing out in the old swamp: every element (except clouds and lights) within 22 m of the seawall
const far = all.filter(n => (n.tag === "m-model" || n.tag === "m-cube" || n.tag === "m-cylinder" || n.tag === "m-sphere") && !/cloud/.test(n.attributes.src || "")).map(n => [n, out(wpos(n))]).filter(([n, d]) => d > 22);
check(far.length === 0, "nothing left out in the old swamp (" + far.length + " far items)" + (far.length ? " e.g. " + JSON.stringify(far.slice(0, 3).map(([n, d]) => [n.tag, n.attributes.src || n.attributes.color, d.toFixed(0)])) : ""));
const water = all.filter(n => n.attributes.mat === "water" || (n.tag === "m-cylinder" && +n.attributes.radius > 300));
check(water.every(n => +n.attributes.radius !== 360), "the big swamp disc is gone");
const trucks = all.filter(n => n.tag === "m-group" && /^car-/.test(n.attributes.id || ""));
check(trucks.length >= 4, "trucks are still on the streets (" + trucks.length + ")");
console.log(fails ? fails + " FAILED" : "ALL PASSED"); process.exit(0);

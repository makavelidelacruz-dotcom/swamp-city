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
const mine = (c, needle) => find(c, n => n.attributes.content && n.attributes.content.includes(needle)).map(n => n.attributes.content);
let fails = 0;
const check = (ok, msg) => { console.log((ok ? "PASS " : "FAIL ") + msg); if (!ok) fails++; };
// crew mascots over players' heads + Visitor Center spawn
const A = client("A"), B = client("B"); await Promise.all([A.ready, B.ready]);
const world = find(B, n => n.tag === "m-group" && n.attributes.id === "world")[0];
check(world && world.attributes.x === "-163" && world.attributes.z === "20", "world is shifted so the Visitor Center plaza is the origin: " + (world && [world.attributes.x, world.attributes.z]));
const join = [0, 1, 2, 3].map(i => find(B, n => n.attributes.id === "join-" + i)[0]);
check(join.every(Boolean), "four check-in stands");
const standG = i => B.nodes.get(join[i].children.find(id => B.nodes.get(id).tag === "m-group"));
check([0, 1, 2, 3].every(i => standG(i).attributes.x === "171" && standG(i).attributes.ry === "-90"), "stands sit in front of the Visitor Center, facing the spawn");
check(find(B, n => n.tag === "m-label" && n.attributes.content === "INTERMISSION").length === 1, "one big screen");
const probe = () => find(A, n => n.tag === "m-position-probe")[0];
check(!!probe(), "position probe is on before any game");
const ICON = /team-(gator|heron|frog|snake)|[0-9a-f]{64}/;
const icons = c => find(c, n => n.tag === "m-group" && n.children.some(id => { const k = c.nodes.get(id); return k && k.tag === "m-attr-lerp" && k.attributes.attr === "x,y,z"; })).map(g => ({ g, m: c.nodes.get(g.children.find(id => c.nodes.get(id).tag === "m-model")) })).filter(o => o.m && ICON.test(o.m.attributes.src || ""));
const pos = (c, x, z, ry) => send(c, probe().nodeId, "positionmove", { elementRelative: { position: { x, y: 0.15, z }, rotation: { x: 0, y: ry || 0, z: 0 } } });
pos(A, 163, -20); await sleep(300);
check(icons(B).length === 0, "no mascot before checking in");
send(A, A.ids["join-0"], "prompt", { value: "Gary" }); await sleep(400);
let ic = icons(B);
check(ic.length === 1 && /gator/.test(ic[0].m.attributes.src), "GATORS player gets a gator over their head, seen by everyone: " + (ic[0] && ic[0].m.attributes.src));
check(ic[0] && ic[0].g.attributes.x === "163" && ic[0].g.attributes.y === "2.35" && ic[0].g.attributes.z === "-20", "mascot sits over their head: " + (ic[0] && [ic[0].g.attributes.x, ic[0].g.attributes.y, ic[0].g.attributes.z]));
pos(A, 120, -60); await sleep(300);
ic = icons(B);
check(ic[0].g.attributes.x === "120" && ic[0].g.attributes.z === "-60", "it follows them");
pos(A, 120.05, -60.05); await sleep(300);
check(icons(B)[0].g.attributes.x === "120", "tiny jitters aren't sent");
send(B, B.ids["join-3"], "prompt", { value: "Cora" }); pos(B, -10, 30); await sleep(400);
ic = icons(A);
check(ic.length === 2 && ic.some(o => /snake/.test(o.m.attributes.src)), "COTTONMOUTHS player gets a snake");
send(A, A.ids["join-1"], "prompt", { value: "Gary" }); await sleep(400);
ic = icons(B);
check(ic.length === 2 && ic.some(o => /heron/.test(o.m.attributes.src)) && !ic.some(o => /gator/.test(o.m.attributes.src)), "switching crew swaps the mascot to a heron");
send(A, A.ids["join-2"], "prompt", { value: "Gary" }); await sleep(400);
check(icons(B).some(o => /frog/.test(o.m.attributes.src)), "BULLFROGS get a frog");
send(A, probe().nodeId, "positionleave", {}); await sleep(300);
check(icons(B).length === 1, "leaving probe range hides the mascot");
pos(A, 50, 50); await sleep(300);
check(icons(B).length === 2, "coming back shows it again");
A.ws.close(); await sleep(600);
check(icons(B).length === 1, "disconnecting removes their mascot");
const lights = find(B, n => n.tag === "m-light" && ["#4fe08f", "#3fd0ff", "#ffc23d", "#c48bff"].includes(n.attributes.color));
check(lights.length === 4, "each hideout has a light in its crew's color");
const beams = find(B, n => n.tag === "m-model" && /beam-(gator|heron|frog|snake)|[0-9a-f]{64}/.test(n.attributes.src || "") && n.attributes.y === "7.4");
check(beams.length === 4 && beams.every(n => n.attributes.visible !== "false" && !n.attributes["data-game"] && !n.attributes.x && !n.attributes.z), "every hideout has an always-on glowing beam straight up out of its roof");
console.log(fails ? fails + " FAILED" : "ALL PASSED"); process.exit(0);

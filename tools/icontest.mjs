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
const roster = c => JSON.parse(c.nodes.get(c.ids["hb-state"]).attributes["data-roster"]);
let fails = 0;
const check = (ok, msg) => { console.log((ok ? "PASS " : "FAIL ") + msg); if (!ok) fails++; };
// crew mascots over players' heads + Visitor Center spawn
const A = client("A"), B = client("B"); await Promise.all([A.ready, B.ready]);
const world = find(B, n => n.tag === "m-group" && n.attributes.id === "world")[0];
check(world && world.attributes.x === "-20" && world.attributes.z === "-242" && world.attributes.ry === "-90", "placed in front: you stand just off the east dock, city straight ahead (-z): " + (world && [world.attributes.x, world.attributes.z, world.attributes.ry]));
check(!find(B, n => /^join-/.test(n.attributes.id || "")).length, "no per-crew stands to click any more");
const sp = find(B, n => n.attributes.id === "signup")[0];
check(sp && sp.tag === "m-prompt", "one sign-up prompt at the dock gate");
check(find(B, n => n.tag === "m-label" && /^0 SIGNED UP/.test(n.attributes.content || "")).length === 1, "sign-up gate shows the count");
check(find(B, n => n.tag === "m-label" && n.attributes.content === "INTERMISSION").length === 1, "one big screen");
const probe = () => find(A, n => n.tag === "m-position-probe")[0];
check(!!probe(), "position probe is on before any game");
const ICON = /team-(gator|heron|frog|snake)|[0-9a-f]{64}/;
const icons = c => find(c, n => n.tag === "m-group" && n.children.some(id => { const k = c.nodes.get(id); return k && k.tag === "m-attr-lerp" && k.attributes.attr === "x,y,z"; })).map(g => ({ g, m: c.nodes.get(g.children.find(id => c.nodes.get(id).tag === "m-model")) })).filter(o => o.m && ICON.test(o.m.attributes.src || ""));
const pos = (c, x, z, ry) => send(c, probe().nodeId, "positionmove", { elementRelative: { position: { x, y: 0.15, z }, rotation: { x: 0, y: ry || 0, z: 0 } } });
pos(A, 163, -20); await sleep(300);
check(icons(B).length === 0, "no mascot before checking in");
send(A, A.ids["signup"], "prompt", { value: "Gary" }); await sleep(400);
let ic = icons(B);
check(ic.length === 1 && /gator/.test(ic[0].m.attributes.src), "first sign-up goes to GATORS and gets a gator over their head, seen by everyone: " + (ic[0] && ic[0].m.attributes.src));
check(ic[0] && ic[0].g.attributes.x === "163" && ic[0].g.attributes.y === "2.35" && ic[0].g.attributes.z === "-20", "mascot sits over their head: " + (ic[0] && [ic[0].g.attributes.x, ic[0].g.attributes.y, ic[0].g.attributes.z]));
pos(A, 120, -60); await sleep(300);
ic = icons(B);
check(ic[0].g.attributes.x === "120" && ic[0].g.attributes.z === "-60", "it follows them");
pos(A, 120.05, -60.05); await sleep(300);
check(icons(B)[0].g.attributes.x === "120", "tiny jitters aren't sent");
send(B, B.ids["signup"], "prompt", { value: "Cora" }); pos(B, -10, 30); await sleep(400);
ic = icons(A);
check(ic.length === 2 && ic.some(o => /heron/.test(o.m.attributes.src)), "second sign-up is put on MUNYONS (heron)");
const C = client("C"), D = client("D"), E = client("E"); await Promise.all([C.ready, D.ready, E.ready]);
const posAs = (c, x, z) => send(c, find(c, n => n.tag === "m-position-probe")[0].nodeId, "positionmove", { elementRelative: { position: { x, y: 0.15, z }, rotation: { x: 0, y: 0, z: 0 } } });
send(C, C.ids["signup"], "prompt", { value: "Cy" }); posAs(C, 10, 10); await sleep(300);
send(D, D.ids["signup"], "prompt", { value: "Di" }); posAs(D, 12, 10); await sleep(300);
ic = icons(B);
check(ic.some(o => /frog/.test(o.m.attributes.src)) && ic.some(o => /snake/.test(o.m.attributes.src)), "third and fourth go to BULLFROGS (frog) and COTTONMOUTHS (snake)");
let r = roster(B);
check(r.every(l => l.length === 1), "four sign-ups, one on each crew: " + JSON.stringify(r));
D.ws.close(); await sleep(500);
send(E, E.ids["signup"], "prompt", { value: "Ed" }); await sleep(400);
r = roster(B);
check(r[3].includes("Ed") && r.every(l => l.length === 1), "when a COTTONMOUTH leaves, the next sign-up fills that crew: " + JSON.stringify(r));
send(A, A.ids["signup"], "prompt", { value: "Gus" }); await sleep(400);
r = roster(B);
check(r[0].includes("Gus") && !r.flat().includes("Gary"), "signing up again just changes your name and keeps your crew: " + JSON.stringify(r));
check(icons(B).some(o => /gator/.test(o.m.attributes.src)), "...and your gator stays over your head");
check(find(B, n => n.tag === "m-label" && /^4 SIGNED UP/.test(n.attributes.content || "")).length === 1, "gate count updates");
const n0 = icons(B).length;
send(A, probe().nodeId, "positionleave", {}); await sleep(300);
check(icons(B).length === n0 - 1, "leaving probe range hides the mascot");
pos(A, 50, 50); await sleep(300);
check(icons(B).length === n0, "coming back shows it again");
A.ws.close(); await sleep(600);
check(icons(B).length === n0 - 1, "disconnecting removes their mascot");
const lights = find(B, n => n.tag === "m-light" && ["#4fe08f", "#3fd0ff", "#ffc23d", "#c48bff"].includes(n.attributes.color));
check(lights.length === 4, "each hideout has a light in its crew's color");
const beams = find(B, n => n.tag === "m-model" && /beam-(gator|heron|frog|snake)|[0-9a-f]{64}/.test(n.attributes.src || "") && n.attributes.y === "7.4");
check(beams.length === 4 && beams.every(n => n.attributes.visible !== "false" && !n.attributes["data-game"] && !n.attributes.x && !n.attributes.z), "every hideout has an always-on glowing beam straight up out of its roof");
console.log(fails ? fails + " FAILED" : "ALL PASSED"); process.exit(0);

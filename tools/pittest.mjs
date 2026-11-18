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
let fails = 0; const check = (ok, msg) => { console.log((ok ? "PASS " : "FAIL ") + msg); if (!ok) fails++; };

const H = client("host"), A = client("A"), B = client("B"); await Promise.all([H.ready, A.ready, B.ready]);
const host = cmd => send(H, H.ids["hb-" + cmd], "click", { key: KEY });
const probe = c => find(c, n => n.tag === "m-position-probe")[0].nodeId;
const at = (c, x, z, y) => send(c, probe(c), "positionmove", { elementRelative: { position: { x, y: y == null ? 0.5 : y, z }, rotation: { x: 0, y: 0, z: 0 } } });
const gators = c => find(c, n => n.tag === "m-model" && /pit-gator|a62c69e6/.test(n.attributes.src || "") && n.attributes.collide === "true");
const animsOn = (c, n) => n.children.map(id => c.nodes.get(id)).filter(k => k && k.tag === "m-attr-anim");
send(A, A.ids["signup"], "prompt", { value: "Ava" }); await sleep(150); send(B, B.ids["signup"], "prompt", { value: "Bo" }); await sleep(400);
const gs = gators(B);
check(gs.length === 5, "five solid pit gators (2 sweepers, 3 lungers): " + gs.length);
const rig = find(B, n => n.tag === "m-group" && n.children.some(id => { const k = B.nodes.get(id); return k && k.tag === "m-group" && k.children.some(j => gs.some(g => g.nodeId === j)); }) && n.attributes.y === "0.5")[0];
check(rig && animsOn(B, rig).length === 0, "idle: the turntable is still");
const jawAnims = find(B, n => n.tag === "m-attr-anim" && n.attributes.attr === "rx" && n.attributes.end === "7");
check(jawAnims.length === 5, "idle: five dozing jaws breathing slowly");
host("arena"); await sleep(500);
const ra = rig && animsOn(B, rig).find(a => a.attributes.attr === "ry");
check(ra && ra.attributes.loop === "true" && ra.attributes.duration === "12000", "live: turntable sweeps the throne every 12 s");
const lx = find(B, n => n.tag === "m-attr-anim" && (n.attributes.attr === "x" || n.attributes.attr === "z") && n.attributes["ping-pong"] === "true" && n.attributes.duration === "1600");
check(lx.length === 6, "live: three lungers charge in and out (x and z keyframes): " + lx.length);
check(find(B, n => n.tag === "m-attr-anim" && n.attributes.attr === "rx" && n.attributes.end === "30").length === 5, "live: all five jaws snapping");
check(find(B, n => n.tag === "m-label" && n.attributes.content === "BRING US GATORS!").length === 4, "jumbotron calls for gators on all four faces");
// GATOR ROUND-UP: little gators loose in the city; grab one, carry it onto the throne
const wild = c => find(c, n => n.tag === "m-group" && n.attributes.sx === "0.25" && n.children.some(id => { const k = c.nodes.get(id); return k && k.tag === "m-model" && /pit-gator|a62c69e6/.test(k.attributes.src || ""); }) && c.nodes.get(n.parent) && c.nodes.get(n.parent).attributes["data-game"] === "arena");
const ws0 = wild(B);
check(ws0.length === 28, "28 little gators loose around the city: " + ws0.length);
const spots = ws0.map(g => B.nodes.get(g.parent)).map(p => [+p.attributes.x, +p.attributes.z]);
check(spots.every(([x, z]) => Math.hypot(x + 75, z + 20) > 26), "none of them start in or next to the pit");
check(new Set(spots.map(([x, z]) => Math.round(x / 20) + "," + Math.round(z / 20))).size > 15, "they're spread out over the city");
const target = ws0[0], tp = B.nodes.get(target.parent), [gx, gz] = [+tp.attributes.x, +tp.attributes.z];
const clickTarget = B.nodes.get(target.children.find(id => B.nodes.get(id).tag === "m-model"));
at(A, gx + 30, gz); await sleep(300);
send(A, clickTarget.nodeId, "click"); await sleep(400);
check(find(A, n => /Get closer/.test(n.attributes.content || "")).length >= 1, "you have to walk up to a gator to grab it");
at(A, gx + 1, gz); await sleep(300);
send(A, clickTarget.nodeId, "click"); await sleep(500);
check(find(A, n => /GOT ONE!/.test(n.attributes.content || "")).length >= 1, "clicking a gator picks it up");
const carried = find(B, n => n.tag === "m-group" && n.attributes.sx === "0.25" && !(B.nodes.get(n.parent) && B.nodes.get(n.parent).attributes["data-game"] === "arena"));
check(carried.length === 1, "everyone sees the player carrying a little gator");
const cg = carried[0] && B.nodes.get(carried[0].parent);
check(cg && Math.abs(+cg.attributes.y - 1.45) < 0.01 && Math.hypot(+cg.attributes.x - (gx + 1), +cg.attributes.z - (gz - 0.45)) < 0.05, "...held in their arms, in front of them at waist height: " + (cg && [cg.attributes.x, cg.attributes.y, cg.attributes.z]));
check(wild(B).length === 27, "it's gone from the street");
at(A, gx + 1.5, gz + 1); await sleep(300);
const firstClick = B.nodes.get(wild(B)[0].children.find(id => B.nodes.get(id).tag === "m-model"));
send(A, firstClick.nodeId, "click"); await sleep(300);
check(find(A, n => /Your arms are full/.test(n.attributes.content || "")).length >= 1, "one gator at a time");
const before = JSON.parse(B.nodes.get(B.ids["hb-state"]).attributes["data-state"]).round[0];
at(A, -75, -20); await sleep(600);
check(find(A, n => /DELIVERED!/.test(n.attributes.content || "")).length >= 1, "carrying it onto the throne delivers it");
await sleep(1300);
const st = JSON.parse(B.nodes.get(B.ids["hb-state"]).attributes["data-state"]);
check(st.round[0] === before + 1, "+1 for the crew: " + JSON.stringify(st.round));
check(wild(B).length === 28, "a new gator turns up somewhere in the city");
check(find(B, n => n.tag === "m-label" && /GATORS LEAD  1/.test(n.attributes.content || "")).length === 4, "jumbotron shows who's leading");
const crown = find(A, n => n.tag === "m-model" && n.attributes.sx === "3" && n.attributes.visible === "true");
check(crown.length === 1, "the leading crew's mascot spins over the jumbotron");
const th = find(A, n => n.tag === "m-cylinder" && n.attributes.radius === "4.5")[0];
check(th && th.attributes.color === "#4fe08f", "throne turns the leading crew's color (GATORS green)");
// Bo grabs one and gets chomped by a lunger on the way to the throne: the gator gets away
const t2 = wild(B)[1], tp2 = B.nodes.get(t2.parent);
at(B, +tp2.attributes.x + 0.5, +tp2.attributes.z); await sleep(300);
send(B, B.nodes.get(t2.children.find(id => B.nodes.get(id).tag === "m-model")).nodeId, "click"); await sleep(500);
at(B, -75, -20 + 4.9, 0.15);
let lost = false;
for (let k = 0; k < 40 && !lost; k++) { await sleep(150); lost = find(B, n => /got away/.test(n.attributes.content || "")).length > 0; }
check(lost, "a pit gator chomps Bo and the gator he was carrying gets away");
check(!find(B, n => n.tag === "m-group" && n.attributes.sx === "0.25" && !(B.nodes.get(n.parent) && B.nodes.get(n.parent).attributes["data-game"] === "arena")).length, "...so he's not carrying it any more");
host("stop"); await sleep(500);
check(wild(B).length === 0, "stopping clears the loose gators");
check(rig && animsOn(B, rig).length === 0 && find(B, n => n.tag === "m-attr-anim" && n.attributes.attr === "rx" && n.attributes.end === "7").length === 5, "stopping puts the gators back to sleep");
check(find(B, n => n.tag === "m-label" && n.attributes.content === "waiting for the host").length === 4, "jumbotron waits for the host");
console.log(fails ? fails + " FAILED" : "ALL PASSED"); process.exit(0);

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
send(A, A.ids["join-0"], "prompt", { value: "Ava" }); send(B, B.ids["join-1"], "prompt", { value: "Bo" }); await sleep(400);
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
check(find(B, n => n.tag === "m-label" && n.attributes.content === "THRONE IS EMPTY").length === 4, "jumbotron shows the throne state on all four faces");
// B stands on the throne in the lunge path of the south gator (90 degrees = +z), A in the safe middle
at(A, -75, -20); at(B, -75, -20 + 4.2);
let chomped = false;
for (let k = 0; k < 40 && !chomped; k++) { await sleep(150); chomped = find(B, n => n.tag === "m-label" && /CHOMPED!/.test(n.attributes.content || "")).length > 0; }
check(chomped, "a lunger chomps the player at the throne's edge (Bo sees CHOMPED!)");
check(!find(A, n => /CHOMPED!/.test(n.attributes.content || "")).length, "only the bitten player gets the personal CHOMPED message");
await sleep(1600);
const faces = find(A, n => n.tag === "m-label" && /GATORS HOLD IT|CHOMP!/.test(n.attributes.content || ""));
check(faces.length >= 4, "while Bo is benched, GATORS hold it alone: " + faces.slice(0, 2).map(n => n.attributes.content));
const crown = find(A, n => n.tag === "m-model" && n.attributes.sx === "3" && n.attributes.visible === "true");
check(crown.length === 1, "the holding crew's mascot spins over the jumbotron");
const th = find(A, n => n.tag === "m-cylinder" && n.attributes.radius === "4.5")[0];
check(th && th.attributes.color === "#4fe08f", "throne turns GATORS green");
host("stop"); await sleep(500);
check(rig && animsOn(B, rig).length === 0 && find(B, n => n.tag === "m-attr-anim" && n.attributes.attr === "rx" && n.attributes.end === "7").length === 5, "stopping puts the gators back to sleep");
check(find(B, n => n.tag === "m-label" && n.attributes.content === "waiting for the host").length === 4, "jumbotron waits for the host");
console.log(fails ? fails + " FAILED" : "ALL PASSED"); process.exit(0);

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
const ctl = client("controller"); await ctl.ready;
const A = client("A"), B = client("B"); await Promise.all([A.ready, B.ready]);
send(A, A.ids["join-0"], "prompt", { value: "Robber" }); send(B, B.ids["join-1"], "prompt", { value: "Watcher" });
await sleep(500);
const host = (cmd, extra) => send(ctl, ctl.ids["hb-" + cmd], "click", Object.assign({ key: KEY }, extra || {}));
const probes = c => find(c, n => n.tag === "m-position-probe");
const bagGroups = c => find(c, n => n.tag === "m-group" && n.children.some(id => { const k = c.nodes.get(id); return k && k.tag === "m-attr-lerp" && k.attributes.attr === "x,y,z,ry"; }) && n.children.some(id => { const k = c.nodes.get(id); return k && k.tag === "m-model" && /money-bag|c4601a60e8d085aa1edf519cb7832d526bb72b0c6794f429ea755588f1199936/.test(k.attributes.src || ""); }));
check(probes(B).length === 0, "no position probe outside the BANK JOB");
check(find(B, n => n.tag === "m-model" && /bank\.glb|0ba48cfd84782e2720910b8e4a4dd6a0e70963084a42e2a2137f994cb0141465/.test(n.attributes.src || "")).length === 1 && /bank-vault|1df32c3d882b40c660013f4a24b776a7834cf4455570a458bfb8745136c092d3/.test((B.nodes.get(B.ids["vault"]) || { attributes: {} }).attributes.src || ""), "modeled bank and vault are in the world");
host("heist"); await sleep(500);
check(probes(B).length === 1 && +probes(B)[0].attributes.range >= 400, "the BANK JOB adds a position probe covering the city");
const loot = find(B, n => n.attributes["data-game"] === "heist")[0];
check(loot && find(B, n => n.tag === "m-model" && /money-bag|c4601a60e8d085aa1edf519cb7832d526bb72b0c6794f429ea755588f1199936/.test(n.attributes.src || "")).length >= 12, "piles of money bags round the vault");
send(A, A.ids["vault"], "click", {}); await sleep(400);
check(mine(A, "BAG GRABBED").length >= 1, "Robber grabs a bag");
let bags = bagGroups(B);
check(bags.length === 1, "everyone can see one carried money bag (" + bags.length + ")");
// Robber walks off: the probe reports their position, facing north (ry 0)
const probeId = probes(A)[0].nodeId;
send(A, probeId, "positionenter", { elementRelative: { position: { x: 10, y: 0.15, z: -40 }, rotation: { x: 0, y: 0, z: 0 } }, documentRelative: { position: { x: 10, y: 0.15, z: -40 }, rotation: { x: 0, y: 0, z: 0 } } });
await sleep(300);
let g = bagGroups(B)[0].attributes;
check(Math.abs(+g.x - 10) < 0.01 && Math.abs(+g.z - (-40 + 0.32)) < 0.01 && Math.abs(+g.y - 1.3) < 0.01, "the bag rides on the Robber's back: " + [g.x, g.y, g.z].join(","));
send(A, probeId, "positionmove", { elementRelative: { position: { x: 30, y: 0.15, z: -60 }, rotation: { x: 0, y: 90, z: 0 } }, documentRelative: { position: { x: 30, y: 0.15, z: -60 }, rotation: { x: 0, y: 90, z: 0 } } });
await sleep(300);
g = bagGroups(B)[0].attributes;
check(Math.abs(+g.x - 30.32) < 0.01 && Math.abs(+g.z - (-60)) < 0.01 && g.ry === "90", "it follows them and turns with them: " + [g.x, g.z, g.ry].join(","));
// someone else's probe report doesn't move the Robber's bag
send(B, probeId, "positionmove", { elementRelative: { position: { x: -80, y: 0.15, z: 50 }, rotation: { x: 0, y: 0, z: 0 } } });
await sleep(300);
check(bagGroups(B)[0].attributes.x === g.x, "other players' positions don't move it");
// bank it at the GATORS hideout
const dropFace = (c, i) => find(c, n => n.tag === "m-label" && n.attributes.x === "6.3" && n.attributes.content === "")[i];
send(A, dropFace(A, 0).nodeId, "click", {}); await sleep(400);
check(JSON.parse(ctl.nodes.get(ctl.ids["hb-state"]).attributes["data-state"]).round[0] === 1, "bag banked for GATORS");
check(bagGroups(B).length === 0, "the carried bag disappears once it's banked");
// grab again, then leave the game while carrying
await sleep(3200);
send(A, A.ids["vault"], "click", {}); await sleep(400);
check(bagGroups(B).length === 1, "a fresh bag for the next run");
host("stop"); await sleep(500);
check(bagGroups(B).length === 0 && probes(B).length === 0, "stopping the job clears bags and the probe");
console.log(fails ? fails + " FAILED" : "ALL PASSED"); process.exit(0);

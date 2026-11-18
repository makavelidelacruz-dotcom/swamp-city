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
const state = c => JSON.parse(c.nodes.get(c.ids["hb-state"]).attributes["data-state"]);
const roster = c => JSON.parse(c.nodes.get(c.ids["hb-state"]).attributes["data-roster"]);
const mine = (c, needle) => find(c, n => n.attributes.content && n.attributes.content.includes(needle)).map(n => n.attributes.content);
const allMine = c => find(c, n => n.tag === "m-label" && n.attributes["font-size"] === "26").map(n => n.attributes.content);
let fails = 0;
const check = (ok, msg) => { console.log((ok ? "PASS " : "FAIL ") + msg); if (!ok) fails++; };

const ctl = client("controller");
await ctl.ready;
console.log("nodes in snapshot:", ctl.nodes.size, " tags:", JSON.stringify(Object.entries(find(ctl, () => true).reduce((a, n) => (a[n.tag] = (a[n.tag] || 0) + 1, a), {})).sort((a, b) => b[1] - a[1])));
const P = [];
for (let i = 0; i < 8; i++) { P.push(client("P" + i)); }
await Promise.all(P.map(p => p.ready));

// check in: P0,P4 GATORS  P1,P5 MUNYONS  P2,P6 BULLFROGS  P3,P7 COTTONMOUTHS
for (let i = 0; i < P.length; i++) { send(P[i], P[i].ids["signup"], "prompt", { value: "Player " + i }); await sleep(120); }   // one sign-up; crews are dealt out evenly in turn
await sleep(600);
const r = roster(ctl);
check(r.every(l => l.length === 2), "4 teams x 2 players in roster: " + JSON.stringify(r));
check(mine(P[0], "Welcome Player 0").length === 1 && mine(P[1], "Welcome Player 0").length === 0, "per-player welcome visible only to its owner: " + JSON.stringify(allMine(P[0])));
check(state(ctl).players === 8, "state shows 8 players");
send(P[0], P[0].ids["signup"], "prompt", { value: "Player 1" }); // name clash -> should dedupe, crew kept
await sleep(300);
check(roster(ctl)[0].includes("Player 1 2"), "duplicate name gets a suffix: " + JSON.stringify(roster(ctl)[0]));

// host key
const host = (cmd, extra) => send(ctl, ctl.ids["hb-" + cmd], "click", Object.assign({ key: KEY }, extra || {}));
send(ctl, ctl.ids["hb-heist"], "click", { key: "wrong" });
await sleep(300);
check(state(ctl).active === null, "wrong host code is ignored");
host("heist");
await sleep(400);
check(state(ctl).active === "heist", "host starts BANK JOB");
const vault = P[0].ids["vault"];
send(P[0], vault, "click", {});
await sleep(300);
check(mine(P[0], "BAG GRABBED").length >= 1, "P0 grabs a bag");
// find hideout drop faces
const dropFace = (c, team) => find(c, n => n.tag === "m-label" && n.attributes.x === "6.3" && n.attributes.content === "")[["GATORS", "MUNYONS", "BULLFROGS", "COTTONMOUTHS"].indexOf(team)];
send(P[0], dropFace(P[0], "MUNYONS").nodeId, "click", {});
await sleep(300);
check(mine(P[0], "Wrong hideout").length >= 1, "wrong hideout rejected");
send(P[0], dropFace(P[0], "GATORS").nodeId, "click", {});
await sleep(300);
check(state(ctl).round[0] === 1 && state(ctl).series[0] === 1, "bag banked for GATORS: round " + JSON.stringify(state(ctl).round));
check(find(P[0], n => n.attributes["data-game"] === "heist" && n.attributes.visible === "true").length > 0, "heist beacons visible while live");

// BAYOU RUN was removed: a "race" command does nothing, and there are no checkpoints
check(ctl.ids["hb-race"] === undefined && state(ctl).active === "heist", "no race button in the host bank (BAYOU RUN removed)");
check(find(P[1], n => n.tag === "m-cube" && n.attributes["collision-interval"] === "200").length === 0, "no checkpoint pads in the world");
check(!state(ctl).games || !("race" in state(ctl).games), "no BAYOU RUN in the game list");

// arena
host("arena");
await sleep(300);
check(find(P[0], n => n.attributes["data-game"] === "heist" && n.attributes.visible === "true").length === 0, "heist beacons hidden again");
// the throne is counted from the position probe; stand in the middle, where no gator can reach
const probeOf = c => find(c, n => n.tag === "m-position-probe")[0].nodeId;
const at = (c, x, z, y) => send(c, probeOf(c), "positionmove", { elementRelative: { position: { x, y: y == null ? 0.5 : y, z }, rotation: { x: 0, y: 0, z: 0 } } });
at(P[0], -75.3, -20); at(P[4], -74.7, -20); at(P[1], -75, -19.6);
await sleep(3200);
const ar = state(ctl).round;
check(ar[0] >= 2 && ar[1] === 0, "GATORS (2 on throne) out-hold MUNYONS (1): " + JSON.stringify(ar));
at(P[4], -40, -20);
await sleep(2200);
check(state(ctl).games.arena.includes("CONTESTED"), "1 v 1 is contested: " + state(ctl).games.arena);
at(P[0], -20, -20); at(P[1], -20, -18);

// turf: claim houses
host("turf");
await sleep(300);
const claims = c => find(c, n => n.tag === "m-label" && n.attributes.content === "CLAIM THIS HOUSE");
const houses = claims(P[2]);
check(houses.length >= 80, "every house has a claim button: " + houses.length);
const doors = find(P[2], n => n.tag === "m-cube" && n.attributes.color === "#5a3a22");
check(doors.length === houses.length, "every house has a door: " + doors.length);
const terrCount = name => find(P[2], n => n.tag === "m-label" && n.attributes.content === name + " TERRITORY  |  click to claim").length;
const tc = ["UPTOWN", "VOODOO QUARTER", "BAYOU VILLAGE", "OLD TOWN"].map(terrCount);
check(tc.every(c => c === tc[0] && c > 0) && tc[0] * 4 === houses.length, "four territories with the same number of houses: " + JSON.stringify(tc));
const doorGroup = P[2].nodes.get(doors[0].parent);
send(P[2], doors[0].nodeId, "click");
await sleep(300);
check(P[2].nodes.get(doorGroup.nodeId).attributes.ry === "-100", "clicking a door opens it");
send(P[2], houses[0].nodeId, "click");
await sleep(300);
send(P[3], houses[0].nodeId, "click"); // locked
await sleep(300);
check(mine(P[3], "locked").length >= 1, "a freshly claimed house is locked");
check(find(P[2], n => n.tag === "m-label" && n.attributes.content === "BULLFROGS").length >= 1, "the house sign shows the owner");
await sleep(10200);
check(state(ctl).round[2] >= 1, "BULLFROGS earn income from their house: " + JSON.stringify(state(ctl).round));

// cars
const car = P[5].nodes.get(P[5].ids["car-0"]);
const hood = car.children.map(id => P[5].nodes.get(id)).find(n => n.tag === "m-model") || car.children.map(id => P[5].nodes.get(id)).filter(n => n.tag === "m-cube")[1];
send(P[5], hood.nodeId, "click", {});
await sleep(300);
const gas = find(P[5], n => n.tag === "m-label" && n.attributes.content === "GO");
check(gas.length === 1, "driver sees the dashboard");
check(find(P[6], n => n.tag === "m-label" && n.attributes.content === "GO").length === 0, "other players don't see it");
const cp = () => { const a = P[5].nodes.get(P[5].ids["car-0"]).attributes; return [+a.x, +a.z]; }; const d0 = cp(), dist = p => Math.hypot(p[0] - d0[0], p[1] - d0[1]), ry0 = +car.attributes.ry; const x0 = 0;
send(P[5], gas[0].nodeId, "click", {});
await sleep(400);
const zEarly = dist(cp());
check(zEarly - x0 < 0.3, "starts off very slowly: " + (zEarly - x0).toFixed(2) + " m in the first 0.4 s");
await sleep(6600);
const z1 = dist(cp());
check(z1 > x0 + 4, "car drives forward: z " + x0 + " -> " + z1);
send(P[5], find(P[5], n => n.tag === "m-label" && n.attributes.content === "STOP")[0].nodeId, "click", {});
await sleep(300);
const zB1 = dist(cp()); await sleep(300);
check(dist(cp()) !== zB1, "BRAKE slows it gradually instead of a dead stop");
await sleep(4500);
const zA = dist(cp()); await sleep(600);
check(zA === dist(cp()), "BRAKE stops the car");
send(P[5], find(P[5], n => n.tag === "m-label" && n.attributes.content === "< LEFT")[0].nodeId, "click", {});
await sleep(400);
const ryMid = +P[5].nodes.get(P[5].ids["car-0"]).attributes.ry;
check(ryMid > ry0 && ryMid < ry0 + 22.5, "LEFT eases round (mid-turn " + ryMid + ")");
await sleep(2400);
check(+P[5].nodes.get(P[5].ids["car-0"]).attributes.ry === ry0 + 22.5, "LEFT turns 22.5 deg");
send(P[6], hood.nodeId, "click", {});
await sleep(200);
check(mine(P[6], "Taken").length === 1, "second player can't steal the wheel");

// casino (one full spin)
host("casino");
await sleep(300);
const betFace = find(P[7], n => n.tag === "m-label" && n.attributes.content === "BET GATOR")[0];
const kiosk = find(P[7], n => n.tag === "m-model" && /bet-gator|7829789cdd2fe3fdf95f6c470f15a2f732ff3c195a196c8a261e6fbbc974bd96/.test(n.attributes.src || ""))[0];   // modeled bet kiosk
const faceNode = kiosk || P[7].nodes.get(P[7].nodes.get(betFace.parent).children.find(id => P[7].nodes.get(id).tag === "m-cube"));
send(P[7], faceNode.nodeId, "click", {});
await sleep(300);
check(mine(P[7], "Bet placed").length === 1, "bet placed on GATOR");
console.log("waiting for the spin...");
await sleep(26500);
const res = state(ctl).games.casino;
const got = mine(P[7], "no luck").length + mine(P[7], "+2 for").length;
check(got === 1, "spin resolved and P7 got a result: " + res + " / " + JSON.stringify(allMine(P[7])));

// note + stop + disconnect
host("note", { text: "Bayou Run in 30 seconds" });
await sleep(1200);
check(state(ctl).note === "Bayou Run in 30 seconds", "host note shows");
host("stop");
await sleep(300);
check(state(ctl).active === null, "stop returns to intermission");
host("cars");
await sleep(500);
check(P[5].nodes.get(P[5].ids["car-0"]).attributes.x === "188" && P[5].nodes.get(P[5].ids["car-0"]).attributes.z === String(-20 - 33), "reset puts cars home");
P[0].ws.close();
await sleep(600);
check(roster(ctl)[0].length === 1, "disconnect removes the player from the roster");
check([ctl, ...P].every(c => !c.errors.length), "no protocol errors");
console.log(fails ? fails + " FAILED" : "ALL PASSED");
process.exit(0);

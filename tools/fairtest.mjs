import WebSocket from "ws";
const PORT = process.env.PORT || 7071;
const sleep = ms => new Promise(r => setTimeout(r, ms));
const nodes = new Map(); const ids = {};
const add = (n, p) => { if (!n) return; nodes.set(n.nodeId, { id: n.nodeId, tag: String(n.tag || "").toLowerCase(), a: Object.assign({}, n.attributes || {}), p, ch: (n.children || []).map(c => c.nodeId) }); (n.children || []).forEach(c => add(c, n.nodeId)); };
const drop = id => { const n = nodes.get(id); if (!n) return; n.ch.forEach(drop); nodes.delete(id); };
let ws; await new Promise(res => { ws = new WebSocket("ws://localhost:" + PORT, ["networked-dom-v0.1"]);
  ws.on("message", raw => { let ms = JSON.parse(raw.toString()); if (!Array.isArray(ms)) ms = [ms];
    for (const m of ms) {
      if (m.type === "snapshot") { add(m.snapshot, null); res(); }
      else if (m.type === "childrenChanged") { const par = nodes.get(m.nodeId); (m.removedNodes || []).forEach(id => { drop(id); if (par) par.ch = par.ch.filter(x => x !== id); }); (m.addedNodes || []).forEach(n => { add(n, m.nodeId); if (par && n) par.ch.push(n.nodeId); }); }
      else if (m.type === "attributeChange") { const n = nodes.get(m.nodeId); if (!n) continue; for (const a of (m.attributes || [{ attribute: m.attribute, newValue: m.newValue }])) { if (a.newValue === null) delete n.a[a.attribute]; else n.a[a.attribute] = a.newValue; } }
      else if (m.type === "ping") ws.send(JSON.stringify({ type: "pong", pong: m.ping }));
    } }); });
const all = () => [...nodes.values()];
const kids = n => n.ch.map(i => nodes.get(i)).filter(Boolean);
const anims = (n, attr) => kids(n).filter(c => c.tag === "m-attr-anim" && (!attr || c.a.attr === attr));
const lab = re => all().filter(n => n.tag === "m-label" && re.test(n.a.content || ""));
const models = re => all().filter(n => n.tag === "m-model" && re.test(n.a.src || ""));
const ghosts = n => kids(n).filter(c => (c.tag === "m-cube" || c.tag === "m-cylinder") && c.a.opacity === "0");
const send = (n, params) => ws.send(JSON.stringify({ type: "event", nodeId: n.id, name: "click", bubbles: true, params: params || {} }));
let fails = 0; const check = (ok, m) => { console.log((ok ? "PASS " : "FAIL ") + m); if (!ok) fails++; };

// Ferris wheel
const rim = models(/ferris-rim/)[0]; const spin = rim && nodes.get(rim.p);
check(!!spin && anims(spin, "rz")[0]?.a.loop === "true" && +anims(spin, "rz")[0].a.duration === 120000, "Bayou Eye turns: one loop every 2 minutes");
const gond = models(/gondola-/);
check(gond.length === 12, "12 gondolas (" + gond.length + ")");
const gg = gond.map(g => nodes.get(g.p));
check(gg.every(g => anims(g, "rz")[0] && +anims(g, "rz")[0].a.end === -360 && anims(g, "rz")[0].a.duration === anims(spin, "rz")[0].a.duration), "every gondola counter-turns so it stays level");
check(gg.every(g => ghosts(g).length === 5), "every gondola has a hidden floor and 4 walls");
const bottom = gg.find(g => Math.abs(+g.a.x) < 0.01 && +g.a.y < 0);
const hubY = +spin.a.y, floorTop = hubY + +bottom.a.y - 3.0;
check(Math.abs(floorTop - 1.35) < 0.05, "bottom gondola floor sits just above the boarding deck (y " + floorTop.toFixed(2) + ")");
check(models(/ferris-frame/)[0].a.collide !== "false", "the boarding platform and stairs are solid");
// Carousel
const car = models(/^.*carousel(\.glb|$)|\/carousel$|carousel"?$/).find(n => !/base|gator|frog/.test(n.a.src)) || models(/carousel/).find(n => !/base|gator|frog/.test(n.a.src));
const rot = nodes.get(car.p);
check(anims(rot, "ry")[0]?.a.loop === "true", "Gator-Go-Round keeps turning");
check(ghosts(rot).some(g => g.tag === "m-cylinder" && +g.a.radius === 6.5), "it has a solid deck that turns with it");
const figs = models(/carousel-(gator|frog)/);
check(figs.length === 16 && figs.every(f => anims(nodes.get(f.p), "y")[0]?.a["ping-pong"] === "true"), "16 gators and frogs bob up and down (" + figs.length + ")");
// Drop tower
const ringM = models(/drop-ring/)[0]; const ring = nodes.get(ringM.p);
check(ghosts(ring).length >= 28, "Gator Drop ring has a floor, lip and collar (" + ghosts(ring).length + ")");
const st = lab(/^BOARDING|^GATOR DROP -|^GOING UP|^HANG ON|^GATOR DROP!!!/)[0];
check(!!st && /BOARDING|STARTING/.test(st.a.content), "drop tower starts by boarding: " + (st && st.a.content));
// Whack-a-Gator
const startL = lab(/CLICK HERE TO PLAY/)[0];
check(!!startL, "Whack-a-Gator has a start button");
send(startL); await sleep(400);
check(/  0  \|  \d+s/.test(startL.a.content), "clicking starts a 20 s game: " + startL.a.content);
let bops = 0, popped = 0;
const pops = models(/whack-gator/).map(m => ({ m, g: nodes.get(m.p) }));
for (let i = 0; i < 40; i++) {
  await sleep(250);
  for (const p of pops) {
    const an = anims(p.g, "y")[0];
    if (an && +an.a.end === 0 && !p.seen) { p.seen = an.id; popped++; send(p.m); bops++; }
    if (an && +an.a.end !== 0) p.seen = null;
  }
}
await sleep(400);
const got = +(startL.a.content.match(/  (\d+)  \|/) || [])[1];
check(popped >= 5 && got >= 5, "gators pop up and bopping them scores (" + popped + " popped, " + got + " bopped)");
await sleep(11000);
check(/^LAST: .* \d+  \|  CLICK TO PLAY/.test(startL.a.content) && /^HIGH SCORE  \d+/.test(lab(/^HIGH SCORE/)[0].a.content), "game ends and the high score is posted: " + lab(/^HIGH SCORE/)[0].a.content);
// High striker
const swing = lab(/^SWING!$/)[0];
const needle = all().find(n => n.tag === "m-cube" && anims(n, "x")[0]?.a["ping-pong"] === "true");
check(!!swing && !!needle, "Test Your Bite has a sweeping needle and a SWING! button");
send(swing); await sleep(300);
const puck = nodes.get(models(/striker-puck/)[0].p);
const pa = anims(puck, "y")[0];
check(pa && +pa.a.end > 0.9 && +pa.a.end <= 7.45, "the puck flies up the scale (to " + (pa && pa.a.end) + ")");
await sleep(2200);
check(lab(/^.+: (SKEETER|TADPOLE|CATFISH|BULLFROG|GATOR!)/).length === 1, "the result is shown: " + (lab(/^.+: (SKEETER|TADPOLE|CATFISH|BULLFROG|GATOR!)/)[0] || { a: {} }).a.content);
// drop tower full cycle
let seen = [], t0 = Date.now();
while (Date.now() - t0 < 60000) { const s = lab(/^BOARDING|^GOING UP|^HANG ON|^GATOR DROP!!!/)[0]; const c = s ? s.a.content.replace(/\d+s$/, "") : ""; if (c && seen[seen.length - 1] !== c) seen.push(c); if (seen.includes("GOING UP... HOLD ON") && seen[seen.length - 1] === "GATOR DROP!!!") break; await sleep(400); }
const ya = anims(ring, "y")[0];
const iu = seen.indexOf("GOING UP... HOLD ON");
check(iu >= 0 && seen.slice(iu).includes("HANG ON...") && seen[seen.length - 1] === "GATOR DROP!!!", "drop tower goes up, hangs, then drops: " + seen.join(" > "));
await sleep(4500);
const yb = anims(ring, "y")[0];
check(yb && +yb.a.end === +ring.a.y && Math.abs(+yb.a.end - 0.7) < 0.01, "after the drop the ring settles back at boarding height (" + (yb && yb.a.end) + ")");
check(ya && +ya.a.end < +ring.a.y + 2 || (ya && ya.a.easing === "easeOutQuad"), "the ring comes back down to the boarding height");
const baked = models(/city-a/).length > 0;
check(baked || (lab(/^SWAMP FAIR$/).length === 1 && lab(/^BAYOU EYE$|^GATOR-GO-ROUND$|^GATOR DROP$/).length === 3), baked ? "signs are painted into the baked city" : "fair and ride signs are up");
console.log(fails ? fails + " FAILED" : "ALL PASSED"); process.exit(0);

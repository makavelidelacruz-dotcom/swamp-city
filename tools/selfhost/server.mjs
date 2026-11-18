// Self-hosted Swamp City: runs the readable world file on a plain MML (networked-dom) server, so the event
// no longer depends on an open MML editor tab and has no 67 KB document limit.
//
//   cd tools/selfhost && npm install
//   HOST_KEY=<your private host code> PORT=8080 node server.mjs
//
// Players join ws://<host>:<port>/ (put TLS in front for wss://, e.g. Caddy: `swamp.example.com { reverse_proxy :8080 }`).
// The host code is read from the environment and never written to disk or GitHub.
import fs from "fs";
import path from "path";
import http from "http";
import { fileURLToPath, pathToFileURL } from "url";
import { WebSocketServer } from "ws";
import { EditableNetworkedDOM, ObservableDOM, JSDOMRunnerFactory } from "@mml-io/networked-dom-server";

const here = path.dirname(fileURLToPath(import.meta.url));
const file = path.resolve(here, process.env.DOC || "../../chaos-trials-swamp-city.html");
const port = Number(process.env.PORT || 8080);
const key = process.env.HOST_KEY || "";
if (!/^[0-9A-Za-z_-]{16,}$/.test(key)) { console.error("Set HOST_KEY to a private code (16+ letters/digits)."); process.exit(1); }
if (key === "2164fdc8f46047cdde8b2b0d4a83e3cc") { console.error("HOST_KEY is the public placeholder from GitHub. Use your own private code."); process.exit(1); }

let src = fs.readFileSync(file, "utf8");
if (!/HOST_KEY: "[^"]*"/.test(src)) { console.error("No HOST_KEY setting found in " + file + "; refusing to start with its built-in code."); process.exit(1); }
src = src.replace(/HOST_KEY: "[^"]*"/, `HOST_KEY: "${key}"`);
if (process.env.ASSET_HOST) src = src.replace(/ASSET_HOST: "[^"]*"/, `ASSET_HOST: "${process.env.ASSET_HOST}"`);

const doc = new EditableNetworkedDOM(pathToFileURL(file).href, (params, cb) => new ObservableDOM(params, cb, JSDOMRunnerFactory));
doc.load(src);

// A click that arrives for a node the game just removed (a gator someone else grabbed) throws inside the
// library, and so does a malformed frame from a buggy or hostile client. Before the server is listening, any error
// stops it (bad config, busy port). Once it is live, errors are logged and the world keeps running: a restart
// would clear every sign-up.
let live = false;
const onError = kind => e => {
  if (!live) { console.error(new Date().toISOString(), "fatal" + kind + ":", e); process.exit(1); }
  console.error(new Date().toISOString(), "kept running after" + kind + ":", (e && e.message) || e);
};
process.on("uncaughtException", onError(""));
process.on("unhandledRejection", onError(" (promise)"));

const server = http.createServer((req, res) => {
  if (req.url === "/health") { res.writeHead(200, { "content-type": "text/plain" }); return res.end("ok " + wss.clients.size + " connected"); }
  res.writeHead(404); res.end();
});
const wss = new WebSocketServer({
  server,
  handleProtocols: protocols => ["networked-dom-v0.2", "networked-dom-v0.1"].find(p => protocols.has ? protocols.has(p) : [...protocols].includes(p)) || false,
});
wss.on("connection", ws => {
  ws.alive = true;
  ws.on("pong", () => { ws.alive = true; });
  ws.on("error", e => console.error(new Date().toISOString(), "socket error:", e.message));
  doc.addWebSocket(ws);
  ws.on("close", () => { if (doc.hasWebSocket(ws)) doc.removeWebSocket(ws); });
});
// Drop dead connections (network cut without a close) after ~30 s, so a reconnecting player's old copy ("ghost")
// frees their name and crew slot. Every WebSocket client answers protocol pings automatically. If a proxy in front
// does not pass pongs back (players get cut off every ~30 s), start with GHOST_PING=0 to switch this off.
if (process.env.GHOST_PING !== "0") setInterval(() => {
  for (const ws of wss.clients) {
    if (!ws.alive) { ws.terminate(); continue; }
    ws.alive = false;
    try { ws.ping(); } catch (e) { /* closing */ }
  }
}, 15000);
server.on("error", e => { if (!live) { console.error("could not start:", e.message); process.exit(1); } console.error("server error:", e.message); });
wss.on("error", e => { if (!live) { console.error("could not start:", e.message); process.exit(1); } console.error("ws server error:", e.message); });
server.listen(port, () => { live = true; });
server.on("listening", () => console.log(`Swamp City live on ws://0.0.0.0:${port}/  (doc: ${path.basename(file)})`));

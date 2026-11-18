// Build a small "packed" Swamp City document for the MML editor:
//  - visible, editable settings block (window.SWAMP_CONFIG = {...})
//  - the game code minified + gzipped + base64, unpacked in the browser runner at start-up
// usage: node pack.mjs source.html assetUrls.json hostKey out.html
import fs from 'fs';
import zlib from 'zlib';
import { minify } from 'terser';

const [, , srcPath, urlsPath, hostKey, outPath] = process.argv;
const src = fs.readFileSync(srcPath, 'utf8');
const s = src.indexOf('<script>'), e = src.lastIndexOf('</script>');
let js = src.slice(s + 8, e);
const markup = src.slice(0, s).replace(/<!--[\s\S]*?-->\s*/, '').replace(/\n\s+/g, '\n').trim();

// pull the CONFIG object literal out (balanced braces)
const start = js.indexOf('const CONFIG = {');
let i = js.indexOf('{', start), depth = 0, end = -1;
for (; i < js.length; i++) { if (js[i] === '{') depth++; else if (js[i] === '}') { depth--; if (depth === 0) { end = i; break; } } }
let configText = js.slice(js.indexOf('{', start), end + 1);
js = js.slice(0, start) + 'const CONFIG = window.SWAMP_CONFIG;' + js.slice(end + 2);

// fill in this project's values
const urls = JSON.parse(fs.readFileSync(urlsPath, 'utf8'));
const short = u => u.replace(/^https:\/\/mmlstorage\.com\/([0-9a-f]{64})$/, "$1");   // mmlstorage links go in as bare file ids
const urlLines = Object.keys(urls).sort().map(k => `"${k}":"${short(urls[k])}"`).reduce((rows, e, i) => { if (i % 2 === 0) rows.push([e]); else rows[rows.length - 1].push(e); return rows; }, []).map(r => '      ' + r.join(', ')).join(',\n');
configText = configText
  .replace(/HOST_KEY: "[^"]*"/, `HOST_KEY: "${hostKey}"`)
  .replace(/ASSET_HOST: "[^"]*"/, 'ASSET_HOST: ""')
  .replace(/ASSET_URLS: \{\}/, 'ASSET_URLS: {\n' + urlLines + '\n    }');

const min = (await minify(js, { compress: { passes: 2 }, mangle: true, format: { comments: false } })).code;
const packed = zlib.gzipSync(Buffer.from(min, 'utf8'), { level: 9 }).toString('base64');
const loader = `(async () => {
  const bin = Uint8Array.from(atob(window.SWAMP_CODE), c => c.charCodeAt(0));
  let code;
  try {
    code = await new Response(new Blob([bin]).stream().pipeThrough(new DecompressionStream("gzip"))).text();
  } catch (e) {
    // Fallback for MML servers without Blob.stream/DecompressionStream: plain-JS gzip inflate.
    code = (function (d) {
      let p = 10, f = d[3], bb = 0, bc = 0;
      if (f & 4) p += 2 + (d[10] | d[11] << 8);
      if (f & 8) while (d[p++]);
      if (f & 16) while (d[p++]);
      if (f & 2) p += 2;
      const out = [];
      const bits = n => { while (bc < n) { if (p >= d.length) throw new Error("truncated"); bb |= d[p++] << bc; bc += 8; } const v = bb & ((1 << n) - 1); bb >>>= n; bc -= n; return v; };
      const build = (lens) => { const cnt = new Uint16Array(16), offs = new Uint16Array(16), sym = new Uint16Array(lens.length);
        for (const l of lens) cnt[l]++; cnt[0] = 0; for (let i = 1; i < 16; i++) offs[i] = offs[i - 1] + cnt[i - 1];
        for (let i = 0; i < lens.length; i++) if (lens[i]) sym[offs[lens[i]]++] = i; return { cnt, sym }; };
      const dec = (h) => { let code = 0, first = 0, idx = 0;
        for (let l = 1; l < 16; l++) { code |= bits(1); const c = h.cnt[l]; if (code - c < first) return h.sym[idx + code - first]; idx += c; first += c; first <<= 1; code <<= 1; }
        throw new Error("bad code"); };
      const LB = [3,4,5,6,7,8,9,10,11,13,15,17,19,23,27,31,35,43,51,59,67,83,99,115,131,163,195,227,258], LE = [0,0,0,0,0,0,0,0,1,1,1,1,2,2,2,2,3,3,3,3,4,4,4,4,5,5,5,5,0];
      const DB = [1,2,3,4,5,7,9,13,17,25,33,49,65,97,129,193,257,385,513,769,1025,1537,2049,3073,4097,6145,8193,12289,16385,24577], DE = [0,0,0,0,1,1,2,2,3,3,4,4,5,5,6,6,7,7,8,8,9,9,10,10,11,11,12,12,13,13];
      let fl, fd;
      for (let last = 0; !last;) {
        last = bits(1); const type = bits(2);
        if (type === 0) { bb = 0; bc = 0; const len = d[p] | d[p + 1] << 8; p += 4; for (let i = 0; i < len; i++) out.push(d[p++]); continue; }
        let lt, dt;
        if (type === 1) {
          if (!fl) { const l = new Array(288); for (let i = 0; i < 288; i++) l[i] = i < 144 ? 8 : i < 256 ? 9 : i < 280 ? 7 : 8; fl = build(l); fd = build(new Array(30).fill(5)); }
          lt = fl; dt = fd;
        } else {
          const hl = bits(5) + 257, hd = bits(5) + 1, hc = bits(4) + 4, ord = [16,17,18,0,8,7,9,6,10,5,11,4,12,3,13,2,14,1,15], cl = new Array(19).fill(0);
          for (let i = 0; i < hc; i++) cl[ord[i]] = bits(3);
          const ch = build(cl), ls = [];
          while (ls.length < hl + hd) { const s = dec(ch);
            if (s < 16) ls.push(s); else if (s === 16) { const r = ls[ls.length - 1], n = 3 + bits(2); for (let i = 0; i < n; i++) ls.push(r); }
            else { const n = s === 17 ? 3 + bits(3) : 11 + bits(7); for (let i = 0; i < n; i++) ls.push(0); } }
          lt = build(ls.slice(0, hl)); dt = build(ls.slice(hl));
        }
        for (;;) { const s = dec(lt); if (s < 256) out.push(s); else if (s === 256) break;
          else { const li = s - 257, len = LB[li] + bits(LE[li]), di = dec(dt), dist = DB[di] + bits(DE[di]); for (let i = 0, st = out.length - dist; i < len; i++) out.push(out[st + i]); } }
      }
      let s = ""; for (let i = 0; i < out.length; i += 8192) s += String.fromCharCode.apply(null, out.slice(i, i + 8192));
      try { return decodeURIComponent(escape(s)); } catch (e2) { return s; }
    })(bin);
  }
  new Function(code)();
})();`;

const out = `<!--
  CHAOS TRIALS: SWAMP CITY
  Settings are below in plain text - edit them freely (host code, lights, detail, model links).
  The game code itself is packed at the bottom to keep this document small enough for the MML editor.
  Readable source + guide: github.com/makavelidelacruz-dotcom/swamp-city
-->
${markup}
<script>
  window.SWAMP_CONFIG = ${configText.replace(/\n {2}/g, '\n')};
</script>
<script>
window.SWAMP_CODE = "${packed}";
${loader}
</script>
`;
fs.writeFileSync(outPath, out);
console.log('packed doc bytes', Buffer.byteLength(out), '| js min', min.length, '| gz b64', packed.length);

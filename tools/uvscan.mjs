// list primitives without TEXCOORD_0, and TEXCOORD_0 with non-finite values
import fs from 'fs';
for (const f of process.argv.slice(2)) {
  const b = fs.readFileSync(f); const jl = b.readUInt32LE(12); const j = JSON.parse(b.slice(20, 20 + jl).toString());
  const binStart = 20 + jl + 8;
  let noUV = 0, total = 0, bad = [];
  for (const m of j.meshes || []) for (const p of m.primitives) { total++;
    if (p.attributes.TEXCOORD_0 === undefined) { noUV++; continue; }
    const a = j.accessors[p.attributes.TEXCOORD_0], v = j.bufferViews[a.bufferView];
    const off = binStart + (v.byteOffset || 0) + (a.byteOffset || 0), stride = v.byteStride || 8;
    let n = 0; for (let i = 0; i < a.count; i++) for (let k = 0; k < 2; k++) { const x = b.readFloatLE(off + i * stride + k * 4); if (!Number.isFinite(x)) n++; }
    if (n) bad.push((j.materials?.[p.material]?.name || p.material) + ':' + n);
  }
  if (noUV || bad.length) console.log(f.split('/').pop().padEnd(22), `noUV ${noUV}/${total}`, bad.length ? 'NONFINITE ' + bad.join(' ') : '');
}

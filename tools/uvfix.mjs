// Add TEXCOORD_0 to every primitive that lacks one, and replace non-finite UV values.
// Box projection: each vertex takes the two axes its normal is least aligned with. Scale 1 UV unit per metre.
// usage: node uvfix.mjs in.glb out.glb
import { NodeIO } from '@gltf-transform/core';
import { ALL_EXTENSIONS } from '@gltf-transform/extensions';
const [, , src, dst] = process.argv;
const io = new NodeIO().registerExtensions(ALL_EXTENSIONS); const doc = await io.read(src); const buf = doc.getRoot().listBuffers()[0];
let added = 0, repaired = 0;
for (const mesh of doc.getRoot().listMeshes()) for (const prim of mesh.listPrimitives()) {
  const pos = prim.getAttribute('POSITION'); if (!pos) continue;
  const nor = prim.getAttribute('NORMAL'); let uv = prim.getAttribute('TEXCOORD_0');
  const n = pos.getCount(), p = [0, 0, 0], q = [0, 0, 0];
  const boxUV = i => { pos.getElement(i, p); let ax = 1;
    if (nor) { nor.getElement(i, q); const a = q.map(Math.abs); ax = a[0] >= a[1] && a[0] >= a[2] ? 0 : a[1] >= a[2] ? 1 : 2; }
    return ax === 0 ? [p[2], -p[1]] : ax === 1 ? [p[0], p[2]] : [p[0], -p[1]]; };
  if (!uv) {
    const arr = new Float32Array(n * 2); for (let i = 0; i < n; i++) { const t = boxUV(i); arr[2 * i] = t[0]; arr[2 * i + 1] = t[1]; }
    prim.setAttribute('TEXCOORD_0', doc.createAccessor().setType('VEC2').setArray(arr).setBuffer(buf)); added++;
  } else {
    const arr = uv.getArray().slice(); let bad = 0;
    for (let i = 0; i < n; i++) if (!Number.isFinite(arr[2 * i]) || !Number.isFinite(arr[2 * i + 1])) { const t = boxUV(i); arr[2 * i] = t[0]; arr[2 * i + 1] = t[1]; bad++; }
    if (bad) { prim.setAttribute('TEXCOORD_0', doc.createAccessor().setType('VEC2').setArray(arr).setBuffer(buf)); if (uv.listParents().length <= 1) uv.dispose(); repaired += bad; }
  }
}
await io.write(dst, doc);
console.log(src.split('/').pop(), 'added', added, 'repaired', repaired);

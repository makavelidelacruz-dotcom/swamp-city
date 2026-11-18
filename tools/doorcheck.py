import json, math, sys
d = json.load(open('/tmp/claude-doors.json'))
CZ, HALF = -20, 215
ROADS = [-200, -150, -100, -50, 50, 100, 150, 200]
FOOT = [f for f in d['foot'] if 'x1' in f]
def on_street(x, z):
    if abs(x) > HALF or abs(z - CZ) > HALF: return False
    return any(abs(x - r) <= 5 for r in ROADS) or any(abs(z - CZ - r) <= 5 for r in ROADS)
def on_plaza(x, z): return abs(x) < 46 and abs(z - CZ) < 46
def blocked_by(x, z, own):
    for i, f in enumerate(FOOT):
        if i in own: continue
        if f['x1'] - 0.2 < x < f['x2'] + 0.2 and f['z1'] - 0.2 < z < f['z2'] + 0.2: return i
    return None
def check(kind, cx, cz, ry, lx, lz, name=''):
    a = math.radians(ry); nx, nz = math.sin(a), math.cos(a)
    px, pz = cx + lx * math.cos(a) + lz * math.sin(a), cz - lx * math.sin(a) + lz * math.cos(a)
    own = {i for i, f in enumerate(FOOT) if f['x1'] - 0.5 <= cx <= f['x2'] + 0.5 and f['z1'] - 0.5 <= cz <= f['z2'] + 0.5}
    for s in range(1, 121):
        t = s * 0.5; x, z = px + nx * t, pz + nz * t
        if on_street(x, z): return ('ok', t, None)
        if on_plaza(x, z): return ('plaza', t, None)
        b = blocked_by(x, z, own)
        if b is not None: return ('BLOCKED', t, FOOT[b])
        if abs(x) > HALF or abs(z - CZ) > HALF: return ('EDGE', t, None)
    return ('FAR', 60, None)
res = []
for h in d['houses']: res.append((h['kind'], h['x'], h['z'], h['ry'], check(h['kind'], h['x'], h['z'], h['ry'], h['doorX'], h['frontZ'])))
for o in d['other']: res.append((o['kind'] + (':' + o['name'] if o.get('name') else ''), o['x'], o['z'], o['ry'], check(o['kind'], o['x'], o['z'], o['ry'], 0, o['d'] / 2 + 0.1)))
from collections import Counter
print(Counter(r[4][0] for r in res))
for r in res:
    st, t, f = r[4]
    if st not in ('ok', 'plaza') or t > 14:
        print(f"{st:8} {t:5.1f}m  {r[0]:28} at ({r[1]:7.1f},{r[2]:7.1f}) ry {r[3]:6.1f}" + (f"  hits {f}" if f else ''))

print('\n--- best facing per building (shortest clear walk to a street or the plaza) ---')
def best_dirs(kind, cx, cz, ry, lx, lzf, w=None, dd=None):
    out = []
    for r in (0, 90, 180, 270):
        st, t, f = check(kind, cx, cz, r, lx, lzf)
        out.append((r, st, t))
    return out
flag = []
items = [(h['kind'], h['x'], h['z'], h['ry'], h['doorX'], h['frontZ']) for h in d['houses']] + [(o['kind'] + (':' + o['name'] if o.get('name') else ''), o['x'], o['z'], o['ry'], 0, o['d'] / 2 + 0.1) for o in d['other']]
for kind, cx, cz, ry, lx, lz in items:
    opts = best_dirs(kind, cx, cz, ry, lx, lz)
    cur = [o for o in opts if o[0] == round(ry) % 360][0]
    good = [o for o in opts if o[1] in ('ok', 'plaza')]
    best = min(good, key=lambda o: o[2]) if good else None
    if cur[1] not in ('ok', 'plaza') or (best and cur[2] > best[2] + 4 and cur[2] > 8):
        flag.append((kind, cx, cz, ry, cur, best))
for f in flag: print(f"{f[0]:28} ({f[1]:7.1f},{f[2]:7.1f}) now ry {f[3]:5.0f} -> {f[4][1]} {f[4][2]:.1f}m | best ry {f[5][0] if f[5] else '-'} {f[5][1] if f[5] else ''} {f[5][2] if f[5] else ''}m")
print(len(flag), 'to fix')

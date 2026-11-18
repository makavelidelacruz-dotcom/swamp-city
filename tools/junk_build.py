# GATOR JUNK yard dressing (CC0, original), one model for the whole inside of the fence.
# Wrecked sedans and pickups (rusty paint, cracked glass, missing wheels on cinder blocks, open hoods, one on its roof),
# stacks of wrecks along the fence, a car crusher with a flattened car and a pyramid of crushed bales, a crawler crane
# with a magnet lifting a wreck, tire towers, oil drums, a scrap heap, an office trailer, a burn barrel, floodlights,
# and a dirt yard floor with oil stains.
# Model space is MML-style: x east, y up, z south; the yard is centred on 0, about 34 x 34 m; the gate is on +x.
import bpy, math, random, sys
sys.path.insert(0, '/home/claude/bscripts')
import boats_build as bb
from boats_build import reset, mat, srgb, smooth, mesh_obj, box_uv
from mathutils import Vector
R = random.Random(7)
def B(x, y, z): return (x, -z, y)
def S(w, h, d): return (w, d, h)

reset(); bb._mats.clear()
PAINT = {k: mat('paint-' + k, (1, 1, 1), f'junk-{k}.jpg', 0.85, 0.15) for k in ['red', 'blue', 'green', 'cream', 'teal', 'black']}
RUST = mat('rust', (1, 1, 1), 'junk-rust.jpg', 0.9, 0.2)
GLASS = mat('glass', (1, 1, 1), 'junk-glass.jpg', 0.25, 0.1)
TIRE = mat('tire', (1, 1, 1), 'tire.jpg', 0.95)
RIM = mat('rim', srgb('#a9aaa8'), 'rim.jpg', 0.5, 0.4)
HOLE = mat('hole', srgb('#141414'), None, 0.9)
BLOCK = mat('cinder', srgb('#8d8b86'), None, 0.95)
DIRT = mat('dirt', (1, 1, 1), 'junk-dirt.jpg', 1.0)
CRUSH = mat('crusher', (1, 1, 1), 'junk-crusher.jpg', 0.7, 0.2)
BALE = mat('bale', (1, 1, 1), 'junk-bale.jpg', 0.8, 0.3)
SIDING = mat('siding', (1, 1, 1), 'junk-siding.jpg', 0.7, 0.3)
STEEL = mat('steel', srgb('#9a9ea3'), None, 0.4, 0.7)
DARK = mat('darkmetal', srgb('#2a2a2a'), None, 0.6, 0.5)
WOOD = mat('pallet', srgb('#8a6a42'), None, 0.9)
FIRE = mat('fire', srgb('#ff8a2a'), None, 0.5, 0, emit=srgb('#ff7a1a'), emit_k=4.0)
LAMP = mat('lamp', srgb('#fff2cc'), None, 0.3, 0, emit=srgb('#fff2cc'), emit_k=3.0)
DRUMS = [mat('drum-' + c, srgb(h), 'junk-rust.jpg', 0.8, 0.3) for c, h in [('blue', '#5a7fb8'), ('red', '#c0473a'), ('yellow', '#e0b440'), ('green', '#6d9a5a')]]

def grab(fn):
    """Run fn (which makes parts), join everything it made into one object and return it."""
    before = set(bpy.context.scene.objects)
    fn()
    made = [o for o in bpy.context.scene.objects if o not in before and o.type == 'MESH']
    bpy.ops.object.select_all(action='DESELECT')
    for o in made: o.select_set(True)
    bpy.context.view_layer.objects.active = made[0]
    if len(made) > 1: bpy.ops.object.join()
    return bpy.context.active_object

def place(o, x, y, z, ry=0, rx=0, rz=0):
    """Turn a part built at the origin (MML axes) and move it: ry about up, then rx / rz tilts."""
    o.rotation_mode = 'XYZ'
    o.rotation_euler = (math.radians(rx), math.radians(-rz), math.radians(ry))
    o.location = B(x, y, z)
    bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); bpy.context.view_layer.objects.active = o
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    return o

def box(n, w, h, d, x, y, z, m, bev=0.04, seg=1, rot=(0, 0, 0), tile=1.0):
    return bb.rbox(n, S(w, h, d), B(x, y, z), m, bev, seg, rot, tile)

def wheel(x, z, r=0.33, flat=False, rim=True):
    o = bb.cyl('tire', r, 0.24, B(x, r * (0.8 if flat else 1), z), TIRE, rot=(math.radians(90), 0, 0), verts=14)
    if flat: o.scale = (1, 1, 1)
    if rim: bb.cyl('rim', r * 0.55, 0.26, B(x, r * (0.8 if flat else 1), z), RIM, rot=(math.radians(90), 0, 0), verts=10)

def cabin(x0, x1, xt0, xt1, y0, y1, hw, thw, m):
    """A tapered cabin (glass all round) between x0..x1 at the bottom and xt0..xt1 at the roof line."""
    v = [B(x0, y0, -hw), B(x1, y0, -hw), B(x1, y0, hw), B(x0, y0, hw), B(xt0, y1, -thw), B(xt1, y1, -thw), B(xt1, y1, thw), B(xt0, y1, thw)]
    f = [(0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]
    o = mesh_obj('cabin', v, f, m); box_uv(o, 1.6)
    for p in o.data.polygons: p.use_smooth = False
    return o

def sedan(paint, wheels='all', hood=False, crush=1.0, doorless=False, lights=True):
    P = PAINT[paint]
    def make():
        box('body', 4.4, 0.55, 1.76, 0, 0.62, 0, P, 0.08, 2)
        h = 0.48 * crush
        cabin(-1.15, 0.85, -0.75, 0.45, 0.9, 0.9 + h, 0.82, 0.72, GLASS)
        box('roof', 1.25, 0.06, 1.48, -0.15, 0.92 + h, 0, P, 0.02)
        for sz in (-1, 1):   # door pillars
            for px in (-1.0, -0.15, 0.7): box('pillar', 0.08, h, 0.06, px * (1 - 0.15 * (px > 0)), 0.9 + h / 2, sz * 0.78, P, 0.0)
        box('bumperF', 0.18, 0.2, 1.8, 2.25, 0.45, 0, RUST, 0.04)
        box('bumperR', 0.18, 0.2, 1.8, -2.25, 0.45, 0, RUST, 0.04)
        box('grille', 0.04, 0.22, 1.0, 2.21, 0.68, 0, DARK, 0.0)
        if lights:
            for sz in (-0.62, 0.62): box('light', 0.04, 0.14, 0.28, 2.22, 0.7, sz, GLASS, 0.0)
        if hood:   # hood propped open
            box('hood', 1.4, 0.05, 1.6, 1.3, 1.25, 0, P, 0.02, rot=(0, math.radians(-40), 0))
            box('engine', 1.1, 0.4, 1.1, 1.45, 0.75, 0, DARK, 0.05)
        if doorless: box('doorhole', 0.95, 0.5, 0.04, -0.55, 0.7, 0.9, HOLE, 0.0)
        for i, (wx, wz) in enumerate([(1.4, -0.82), (1.4, 0.82), (-1.4, -0.82), (-1.4, 0.82)]):
            if wheels == 'all' or (wheels == 'some' and i % 3 == 0): wheel(wx, wz, flat=(i == 3 and wheels == 'all'))
            elif wheels != 'none' or True:
                box('block', 0.4, 0.38, 0.2, wx, 0.19, wz * 0.8, BLOCK, 0.01)
    return grab(make)

def pickup(paint, wheels='all'):
    P = PAINT[paint]
    def make():
        box('cabfront', 2.2, 0.6, 1.86, 1.25, 0.68, 0, P, 0.08, 2)
        cabin(-0.15, 1.0, 0.0, 0.75, 0.98, 1.5, 0.86, 0.8, GLASS)
        box('roof', 0.8, 0.06, 1.62, 0.38, 1.52, 0, P, 0.02)
        box('bedfloor', 2.3, 0.12, 1.86, -1.3, 0.55, 0, RUST, 0.02)
        for sz in (-1, 1): box('bedside', 2.3, 0.5, 0.08, -1.3, 0.86, sz * 0.89, P, 0.02)
        box('tailgate', 0.08, 0.5, 1.86, -2.43, 0.86, 0, P, 0.02)
        box('bumperF', 0.18, 0.22, 1.9, 2.42, 0.45, 0, RUST, 0.04)
        box('grille', 0.04, 0.3, 1.2, 2.36, 0.72, 0, DARK, 0.0)
        for i, (wx, wz) in enumerate([(1.5, -0.88), (1.5, 0.88), (-1.5, -0.88), (-1.5, 0.88)]):
            if wheels == 'all' or (wheels == 'some' and i % 2 == 0): wheel(wx, wz, 0.38)
            else: box('block', 0.4, 0.42, 0.2, wx, 0.21, wz * 0.8, BLOCK, 0.01)
        for k in range(3): box('junkinbed', 0.5, 0.3, 0.4, -1.8 + k * 0.6, 0.78, -0.3 + 0.3 * (k % 2), [RUST, TIRE, DARK][k], 0.03)
    return grab(make)

def bale(x, y, z, ry):
    o = box('bale', 1.6, 0.75, 1.1, 0, 0, 0, BALE, 0.06, 1, tile=1.2)
    return place(o, x, y + 0.375, z, ry)

def tire_stack(x, z, n):
    for k in range(n):
        o = bb.cyl('tire', 0.38, 0.26, B(0, 0, 0), TIRE, verts=16)
        bb.cyl('hole', 0.22, 0.27, B(0, 0, 0), HOLE, verts=10)
    # (the simple cylinders are joined below per stack)

def tires(x, z, n, lean=0):
    def make():
        for k in range(n):
            dx, dz = R.uniform(-0.06, 0.06), R.uniform(-0.06, 0.06)
            bb.cyl('tire', 0.38, 0.25, B(x + dx, 0.13 + k * 0.25, z + dz), TIRE, verts=16)
            bb.cyl('hole', 0.21, 0.26, B(x + dx, 0.13 + k * 0.25, z + dz), HOLE, verts=10)
    return grab(make)

def drum(x, z, tipped=False, ry=0):
    m = R.choice(DRUMS)
    o = bb.cyl('drum', 0.3, 0.9, B(0, 0, 0), m, verts=14)
    return place(o, x, 0.3 if tipped else 0.45, z, ry, 90 if tipped else 0)

# ---------------------------------------------------------------- the yard
box('ground', 33.4, 0.04, 33.4, 0, 0.02, 0, DIRT, 0.0, tile=33.4)

# stacks of wrecks along the west fence (length north-south), 1 to 3 high
cols = list(PAINT)
for i, z in enumerate([-13.5, -8.8, -4.1, 0.6, 5.3, 10.0, 14.2]):
    n = [3, 2, 3, 1, 2, 3, 2][i]
    for k in range(n):
        o = sedan(R.choice(cols), wheels=R.choice(['all', 'some', 'none']), crush=1.0 if k == n - 1 else 0.55, lights=R.random() < 0.6)
        place(o, -14.6 + R.uniform(-0.15, 0.15), k * 1.12, z + R.uniform(-0.2, 0.2), 90 + R.uniform(-7, 7))
# a row along the north fence (length east-west)
for i, x in enumerate([-8.5, -3.6, 1.3]):
    n = [2, 1, 2][i]
    for k in range(n):
        o = sedan(R.choice(cols), wheels='some', crush=1.0 if k == n - 1 else 0.55, hood=(k == n - 1 and i == 1))
        place(o, x + R.uniform(-0.2, 0.2), k * 1.12, -14.9, R.uniform(-6, 6))

# scattered wrecks in the yard
place(sedan('red', wheels='some', hood=True), 4.0, 0, 6.0, 25)
place(sedan('teal', wheels='none', doorless=True), -2.5, 0, 9.8, -70)
place(sedan('cream', wheels='all', crush=0.7), 1.5, 1.38, 13.6, 180, 180)     # on its roof
place(pickup('blue', wheels='some'), 9.5, 0, 9.5, -35)
place(pickup('green', wheels='all'), 12.5, 0, 14.6, 5)
place(sedan('black', wheels='some'), 8.0, 0.32, -6.6, 100, 0, 18)            # tipped on a tire pile

# car crusher with a flattened car, and the bales it made
def crusher():
    box('bed', 7.0, 1.0, 3.0, 0, 0.5, 0, CRUSH, 0.06, 1, tile=2)
    for sz in (-1, 1): box('wall', 7.0, 1.4, 0.3, 0, 1.7, sz * 1.35, CRUSH, 0.04, tile=2)
    for px in (-3.1, 3.1):
        for sz in (-1.35, 1.35): bb.cyl('ram', 0.16, 3.8, B(px, 2.9, sz), STEEL, verts=10)
    box('press', 6.8, 0.4, 2.6, 0, 3.4, 0, CRUSH, 0.05, tile=2)
    box('flat', 4.3, 0.35, 1.8, 0.2, 1.2, 0, BALE, 0.04, tile=1.4)
    box('booth', 1.6, 2.2, 1.6, 4.6, 1.1, 0.4, CRUSH, 0.05, tile=2)
    box('boothglass', 1.62, 0.8, 1.2, 4.6, 1.75, 0.4, GLASS, 0.0)
place(grab(crusher), -8.8, 0, 9.6, 0)
for k, (x, y, z) in enumerate([(-1.2, 0, 7.0), (0.5, 0, 7.0), (2.2, 0, 7.0), (-0.35, 0.75, 7.0), (1.35, 0.75, 7.0), (0.5, 1.5, 7.0),
                                 (-1.2, 0, 8.2), (0.5, 0, 8.2), (2.2, 0, 8.2)]):
    bale(x - 1.5, y, z + 2.5, R.uniform(-6, 6))

# crawler crane with an electromagnet lifting a wreck over the yard
CX, CZ = -8.5, -7.5
def crane():
    for sz in (-1.2, 1.2): box('track', 4.2, 0.8, 0.8, 0, 0.4, sz, DARK, 0.2, 2)
    box('deck', 3.6, 0.5, 2.8, 0, 1.05, 0, CRUSH, 0.05, tile=2)
    box('cab', 1.6, 1.8, 1.6, -0.3, 2.2, 1.0, CRUSH, 0.05, tile=2)
    box('cabglass', 1.62, 0.8, 1.3, -0.3, 2.6, 1.0, GLASS, 0.0)
    box('engine', 1.8, 1.2, 2.0, -1.6, 1.9, -0.2, CRUSH, 0.05, tile=2)
CRANE = grab(crane); place(CRANE, CX, 0, CZ, -45)
tip = (CX + 6.0, 11.5, CZ + 6.0); foot = (CX + 0.6, 1.6, CZ + 0.6)
bb.tube('boom', B(*foot), B(*tip), 0.32, CRUSH, verts=8)
bb.tube('boom2', B(foot[0] - 0.5, foot[1], foot[2] + 0.5), B(*tip), 0.22, CRUSH, verts=8)
bb.tube('cable', B(*tip), B(tip[0], 6.9, tip[2]), 0.04, DARK, verts=6)
bb.cyl('magnet', 0.9, 0.35, B(tip[0], 6.7, tip[2]), DARK, verts=18)
place(sedan('green', wheels='some'), tip[0], 5.15, tip[2], 30, 0, 6)   # the wreck hangs under the magnet

# tire towers and loose tires
for (x, z, n) in [(15.2, 12.2, 7), (14.4, 13.2, 5), (15.4, 13.6, 6), (5.0, 15.0, 4), (6.0, 14.6, 6), (8.3, -6.6, 3), (7.6, -7.4, 2)]:
    tires(x, z, n)
for (x, z, ry) in [(10.5, 5.2, 20), (3.0, 3.0, 70)]:
    o = bb.cyl('tire', 0.38, 0.25, B(0, 0, 0), TIRE, verts=16); place(o, x, 0.38, z, ry, 90)

# oil drums, a few tipped over
for (x, z, t) in [(14.8, -8.0, False), (15.4, -7.2, False), (14.6, -6.4, True), (15.5, -9.0, False), (-3.0, 3.5, True), (12.0, 11.6, False)]:
    drum(x, z, t, R.uniform(0, 360))

# scrap heap: a rusty mound bristling with bars, panels and wheels
bpy.ops.mesh.primitive_cone_add(radius1=3.6, radius2=0.6, depth=2.4, vertices=14, location=B(-1.0, 1.2, -9.5))
o = bpy.context.active_object; o.data.materials.append(RUST); box_uv(o, 2.0)
for k in range(16):
    a = R.uniform(0, 6.28); r = R.uniform(0.6, 3.0); x = -1.0 + math.cos(a) * r; z = -9.5 + math.sin(a) * r; y = 2.4 * (1 - r / 3.8)
    kind = k % 4
    if kind == 0: bb.tube('bar', B(x, y, z), B(x + R.uniform(-1.4, 1.4), y + R.uniform(0.3, 1.4), z + R.uniform(-1.4, 1.4)), 0.05, RUST, verts=6)
    elif kind == 1: box('panel', R.uniform(0.8, 1.6), 0.05, R.uniform(0.5, 1.1), x, y + 0.1, z, R.choice(list(PAINT.values())), 0.0, rot=(R.uniform(-0.8, 0.8), R.uniform(-0.8, 0.8), R.uniform(0, 3)))
    elif kind == 2: place(bb.cyl('rim', 0.3, 0.2, B(0, 0, 0), RIM, verts=12), x, y + 0.1, z, R.uniform(0, 360), R.uniform(30, 90))
    else: box('block', 0.6, 0.4, 0.5, x, y + 0.1, z, DARK, 0.05, rot=(R.uniform(-0.5, 0.5), R.uniform(-0.5, 0.5), R.uniform(0, 3)))

# engine blocks on a pallet by the office
box('pallet', 1.4, 0.15, 1.2, 4.6, 0.08, -5.6, WOOD, 0.01)
for k in range(2): box('engineblock', 0.6, 0.5, 0.5, 4.3 + k * 0.6, 0.4, -5.6, DARK, 0.06)

# office trailer on cinder blocks, door and windows facing the driveway
def office():
    box('trailer', 7.2, 2.6, 2.6, 0, 1.75, 0, SIDING, 0.03, tile=2.5)
    box('roof', 7.4, 0.12, 2.8, 0, 3.1, 0, RUST, 0.02)
    box('door', 0.9, 2.0, 0.06, 1.6, 1.45, 1.31, HOLE, 0.0)
    for wx in (-2.4, -0.6, 3.0): box('window', 1.2, 0.8, 0.06, wx, 2.0, 1.31, GLASS, 0.0)
    for bx in (-3.0, 0, 3.0):
        for bz in (-1.0, 1.0): box('block', 0.4, 0.45, 0.4, bx, 0.22, bz, BLOCK, 0.01)
    for k in range(3): box('step', 1.2, 0.15, 0.35, 1.6, 0.15 + k * 0.15, 2.0 - k * 0.3, WOOD, 0.01)
    box('acunit', 0.8, 0.6, 0.7, -3.1, 2.0, 1.6, STEEL, 0.04)
place(grab(office), 10.8, 0, -11.6, 0)

# burn barrel with a fire in it
bb.cyl('barrel', 0.32, 0.9, B(6.6, 0.45, 2.6), RUST, verts=14)
for k in range(3):
    bpy.ops.mesh.primitive_cone_add(radius1=0.18, radius2=0.0, depth=0.6 + k * 0.15, vertices=8, location=B(6.6 + (k - 1) * 0.1, 1.15 + k * 0.05, 2.6 + (k % 2) * 0.08))
    o = bpy.context.active_object; o.data.materials.append(FIRE); box_uv(o)

# two floodlight poles in opposite corners
for (x, z, ry) in [(16.0, -16.0, 225), (-16.0, 16.0, 45)]:
    bb.cyl('pole', 0.12, 8.0, B(x, 4.0, z), DARK, verts=10)
    def head():
        box('lamphead', 1.2, 0.5, 0.4, 0, 0, 0, DARK, 0.03)
        box('lampface', 1.0, 0.35, 0.05, 0, 0, 0.22, LAMP, 0.0)
    o = grab(head); place(o, x, 8.0, z, ry, -25)

# fence posts, top rail and barbed wire on the chain-link (the mesh itself is in the city), plus an open gate
def rail(a, b, y, r=0.04): bb.tube('rail', B(a[0], y, a[1]), B(b[0], y, b[1]), r, STEEL, verts=6)
edges = [((-17, -17), (17, -17)), ((-17, 17), (17, 17)), ((-17, -17), (-17, 17)), ((17, -17), (17, -5)), ((17, 5), (17, 17))]
for (a, b) in edges:
    L = math.dist(a, b); n = max(1, round(L / 3.4))
    for k in range(n + 1):
        x = a[0] + (b[0] - a[0]) * k / n; z = a[1] + (b[1] - a[1]) * k / n
        bb.cyl('post', 0.06, 2.9, B(x, 1.45, z), STEEL, verts=8)
    rail(a, b, 2.6); rail(a, b, 2.95, 0.015); rail(a, b, 3.15, 0.015)   # top rail and two strands of barbed wire
for gz in (-5, 5): bb.cyl('gatepost', 0.12, 3.2, B(17, 1.6, gz), DARK, verts=10)
for gz, sgn in ((-5, 1), (5, -1)):   # two gate leaves swung open outward
    def leaf():
        for y in (0.3, 1.3, 2.3): box('gbar', 4.6, 0.06, 0.06, 2.3, y, 0, STEEL, 0.0)
        for x in (0.05, 2.3, 4.55): box('gstile', 0.06, 2.1, 0.06, x, 1.3, 0, STEEL, 0.0)
        box('gmesh', 4.5, 2.0, 0.02, 2.3, 1.3, 0, mat('mesh', srgb('#6a6a64'), None, 0.6, 0.5), 0.0)
    place(grab(leaf), 17, 0, gz, sgn * 60)

bb.join_all('gator-junk')
bb.export_safe('gator-junk')

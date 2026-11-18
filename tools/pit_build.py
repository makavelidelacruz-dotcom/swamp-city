# GATOR PIT (CC0, original): the arena shell, and the snapping gators that guard the throne.
#   pit-arena.glb  sand floor, a ring of swamp mud round the throne, stone dais rim with a gold band, palisade wall with sharpened logs on a mossy stone base, three tiers of
#                  bleachers, crew banners, tiki torches, a "jaws" entrance arch on the east with a giant gator head,
#                  a log arch on the west, four floodlight towers and cables holding the jumbotron frame.
#   pit-gator.glb  a 5 m gator (body, upper jaw with teeth, glowing eyes), facing +z, belly at y = 0.
#   pit-jaw.glb    its lower jaw, hinged at the origin, reaching along +z (the world snaps it open with rx).
# Model space is MML-style: x east, y up, z south; the arena is centred on 0; entrances on +x and -x.
import bpy, math, random, sys
sys.path.insert(0, '/home/claude/bscripts')
import boats_build as bb
from boats_build import reset, mat, srgb, mesh_obj, box_uv
R = random.Random(3)
def B(x, y, z): return (x, -z, y)
def S(w, h, d): return (w, d, h)
def box(n, w, h, d, x, y, z, m, bev=0.03, seg=1, ry=0, tile=1.0, rx=0, rz=0):
    return bb.rbox(n, S(w, h, d), B(x, y, z), m, bev, seg, (math.radians(rx), math.radians(-rz), math.radians(ry)), tile)
def cyl(n, r, h, x, y, z, m, v=16, tile=1.0, cap=True):
    return bb.cyl(n, r, h, B(x, y, z), m, verts=v, tile=tile, cap=cap)
def tube(n, a, b, r, m, v=8): return bb.tube(n, B(*a), B(*b), r, m, verts=v)
def cone(n, r1, r2, h, x, y, z, m, v=8, down=False):
    bpy.ops.mesh.primitive_cone_add(radius1=r1, radius2=r2, depth=h, vertices=v, location=B(x, y, z), rotation=(math.pi if down else 0, 0, 0))
    o = bpy.context.active_object; o.name = n; o.data.materials.append(m); box_uv(o); return o
def ball(n, r, x, y, z, m, sc=(1, 1, 1), seg=14, rings=8): return bb.sphere(n, r, B(x, y, z), m, scale=(sc[0], sc[2], sc[1]), seg=seg, rings=rings)
def ring(n, r0, r1, y, m, v=64, tile=4.0):
    verts, faces = [], []
    for k in range(v):
        a = k / v * 2 * math.pi
        verts += [B(math.cos(a) * r0, y, math.sin(a) * r0), B(math.cos(a) * r1, y, math.sin(a) * r1)]
    for k in range(v):
        a, b2 = 2 * k, 2 * ((k + 1) % v)
        faces.append((a, b2, b2 + 1, a + 1))
    o = mesh_obj(n, verts, faces, m); box_uv(o, tile)
    for p in o.data.polygons: p.use_smooth = True
    return o

def materials():
    bb._mats.clear()
    return dict(
        sand=mat('sand', (1, 1, 1), 'pit-sand.jpg', 0.95), mud=mat('mud', (1, 1, 1), 'pit-mud.jpg', 0.35),
        logs=mat('logs', (1, 1, 1), 'pit-logs.jpg', 0.9), stone=mat('stone', (1, 1, 1), 'pit-stone.jpg', 0.9),
        planks=mat('planks', (1, 1, 1), 'pit-planks.jpg', 0.85), gold=mat('gold', (1, 1, 1), 'pit-gold.jpg', 0.35, 0.8),
        bone=mat('bone', srgb('#e8dfc8'), None, 0.6), dark=mat('dark', srgb('#26231f'), None, 0.6, 0.4),
        steel=mat('steel', srgb('#8d9297'), None, 0.45, 0.7), rope=mat('rope', srgb('#5a4a32'), None, 0.9),
        fire=mat('fire', srgb('#ff8a2a'), None, 0.5, 0, emit=srgb('#ff7a1a'), emit_k=4.0),
        lamp=mat('lamp', srgb('#fff2cc'), None, 0.3, 0, emit=srgb('#fff2cc'), emit_k=3.0),
        skin=mat('skin', (1, 1, 1), 'gatorskin.jpg', 0.7), belly=mat('belly', srgb('#c9c08a'), None, 0.7),
        eye=mat('eye', srgb('#ffd23a'), None, 0.3, 0, emit=srgb('#ffcc22'), emit_k=2.5), pupil=mat('pupil', srgb('#0d0d0d'), None, 0.3),
        tooth=mat('tooth', srgb('#f4efdc'), None, 0.4), mouth=mat('mouth', srgb('#8a2c2a'), None, 0.6),
        banners=[mat('banner-' + t, (1, 1, 1), f'pit-banner-{t}.jpg', 0.8) for t in ['gator', 'heron', 'frog', 'snake']],
    )

N = 16
def arena():
    reset(); M = materials()
    cyl('floor', 14.7, 0.06, 0, 0.03, 0, M['sand'], v=48, tile=5)
    ring('mud', 5.0, 9.8, 0.065, M['mud'], tile=4)
    for k in range(9):   # glossy puddles in the mud
        a = R.uniform(0, 6.28); r = R.uniform(6.0, 9.0)
        cyl('puddle', R.uniform(0.5, 1.1), 0.01, math.cos(a) * r, 0.072, math.sin(a) * r, M['mud'], v=12)
    for k in range(10):  # old bones in the mud
        a = R.uniform(0, 6.28); r = R.uniform(5.8, 9.4); x, z = math.cos(a) * r, math.sin(a) * r; b = R.uniform(0, 6.28)
        tube('bone', (x, 0.12, z), (x + math.cos(b) * 0.7, 0.12, z + math.sin(b) * 0.7), 0.05, M['bone'], 6)
        ball('knob', 0.09, x, 0.12, z, M['bone'])
    # the dais rim: stone ring with a gold band (the walkable throne disc itself is live in the world)
    for k in range(24):
        a = (k + 0.5) / 24 * 360
        box('rim', 1.33, 0.55, 0.45, math.cos(math.radians(a)) * 4.78, 0.28, math.sin(math.radians(a)) * 4.78, M['stone'], 0.04, ry=-a + 90, tile=1.2)
    ring('band', 4.55, 5.02, 0.565, M['gold'], v=48, tile=1.0)
    # palisade wall on a mossy stone base, sharpened logs along the top, gaps for the two entrances
    for k in range(N):
        if k in (0, N // 2): continue
        th = k / N * 360; rad = math.radians(th); ry = -(th + 90)
        ch = 2 * 15.5 * math.sin(math.pi / N) + 0.3
        box('base', ch, 0.9, 0.9, math.cos(rad) * 15.5, 0.45, math.sin(rad) * 15.5, M['stone'], 0.04, ry=ry, tile=1.5)
        box('wall', ch, 2.4, 0.6, math.cos(rad) * 15.5, 2.1, math.sin(rad) * 15.5, M['logs'], 0.02, ry=ry, tile=2.4)
        for j in range(6):   # sharpened tips
            off = (j - 2.5) / 6 * ch; px = math.cos(rad) * 15.5 - math.sin(rad) * off; pz = math.sin(rad) * 15.5 + math.cos(rad) * off
            cone('tip', 0.28, 0, 0.6, px, 3.6, pz, M['logs'], 6)
        for t in range(3):   # bleachers: plank tiers with a seat board on each
            rr = 16.9 + t * 1.3; c2 = 2 * rr * math.sin(math.pi / N) + 0.3
            box('tier', c2, 1.2 * (t + 1), 1.3, math.cos(rad) * rr, 0.6 * (t + 1), math.sin(rad) * rr, M['planks'], 0.02, ry=ry, tile=1.3)
            box('seatboard', c2, 0.1, 0.45, math.cos(rad) * (rr - 0.3), 1.2 * (t + 1) + 0.05, math.sin(rad) * (rr - 0.3), M['planks'], 0.01, ry=ry)
        c3 = 2 * 20.3 * math.sin(math.pi / N) + 0.3
        box('backwall', c3, 4.6, 0.4, math.cos(rad) * 20.3, 2.3, math.sin(rad) * 20.3, M['logs'], 0.02, ry=ry, tile=2.4)
        if k % 2 == 1:   # crew banners on the back wall, cycling through the four colors
            bm = M['banners'][(k // 2) % 4]
            bx, bz = math.cos(rad) * 20.05, math.sin(rad) * 20.05
            box('banner', 1.4, 2.6, 0.04, bx, 3.6, bz, bm, 0.0, ry=ry + 180)
            tube('bannerpole', (bx - math.sin(rad) * 0.85, 4.95, bz + math.cos(rad) * 0.85), (bx + math.sin(rad) * 0.85, 4.95, bz - math.cos(rad) * 0.85), 0.04, M['dark'], 6)
        if k % 2 == 0:   # tiki torches on the wall top
            tx, tz = math.cos(rad) * 15.1, math.sin(rad) * 15.1
            cyl('torchpole', 0.07, 1.6, tx, 4.1, tz, M['logs'], 6)
            cone('bowl', 0.12, 0.3, 0.35, tx, 5.0, tz, M['dark'], 8)
            cone('flame', 0.24, 0, 0.75, tx, 5.55, tz, M['fire'], 8)
            cone('flame2', 0.14, 0, 0.5, tx + 0.08, 5.6, tz + 0.05, M['fire'], 6)
    # east entrance: stone pillars, a lintel lined with fangs, and a giant gator head on top looking out
    for sz in (-3.6, 3.6):
        box('pillar', 1.3, 5.6, 1.3, 15.5, 2.8, sz, M['stone'], 0.05, tile=1.5)
        cone('cap', 0.9, 0.2, 0.7, 15.5, 5.95, sz, M['gold'], 8)
    box('lintel', 1.4, 1.0, 8.6, 15.5, 4.95, 0, M['logs'], 0.04, tile=2)
    for j in range(11): cone('fang', 0.2, 0, 0.75, 16.15, 4.1, -2.6 + j * 0.52, M['tooth'], 6, down=True)
    box('headbody', 2.6, 1.0, 2.6, 15.3, 5.9, 0, M['skin'], 0.25, 2, tile=1.2)
    box('snoutU', 3.4, 0.55, 1.7, 17.3, 6.15, 0, M['skin'], 0.2, 2, tile=1.2)
    box('snoutL', 3.0, 0.35, 1.5, 17.1, 5.55, 0, M['skin'], 0.15, 2, tile=1.2, rz=-12)
    box('mouth', 2.8, 0.3, 1.3, 17.0, 5.85, 0, M['mouth'], 0.05)
    for j in range(6):
        for sz in (-0.7, 0.7): cone('tooth', 0.08, 0, 0.3, 16.2 + j * 0.45, 5.95, sz * (1 - j * 0.04), M['tooth'], 6, down=True)
    for sz in (-0.75, 0.75):
        ball('eyebump', 0.38, 15.6, 6.55, sz, M['skin'])
        ball('eye', 0.24, 15.75, 6.68, sz * 1.08, M['eye'])
    # west entrance: a log arch
    for sz in (-3.6, 3.6): cyl('post', 0.45, 5.0, -15.5, 2.5, sz, M['logs'], 10, 2)
    cyl('beam', 0.4, 8.4, -15.5, 5.0, 0, M['logs'], 10, 2).rotation_euler = (math.radians(90), 0, 0)
    bpy.ops.object.select_all(action='DESELECT'); o = bpy.context.scene.objects[-1]
    # floodlight towers in the corners, with cables holding the jumbotron frame over the throne
    for a in (45, 135, 225, 315):
        rad = math.radians(a); px, pz = math.cos(rad) * 21, math.sin(rad) * 21
        cyl('tower', 0.28, 13, px, 6.5, pz, M['steel'], 10)
        box('lamps', 2.4, 1.0, 0.5, px * 0.98, 13.2, pz * 0.98, M['dark'], 0.03, ry=-a - 90)
        box('lampface', 2.2, 0.8, 0.05, px * 0.965, 13.2, pz * 0.965, M['lamp'], 0.0, ry=-a - 90)
        tube('cable', (px, 12.6, pz), (math.cos(rad) * 3.2, 10.9, math.sin(rad) * 3.2), 0.035, M['dark'], 6)
    box('jumbo', 6.0, 2.4, 6.0, 0, 9.6, 0, M['dark'], 0.08, 2)
    box('jumbotop', 6.4, 0.25, 6.4, 0, 10.9, 0, M['gold'], 0.04)
    box('jumbobot', 6.4, 0.25, 6.4, 0, 8.3, 0, M['gold'], 0.04)
    bb.join_all('pit-arena'); bb.export_safe('pit-arena')

def gator_body():
    reset(); M = materials()
    ball('body', 0.75, 0, 0.42, 0, M['skin'], (1.0, 0.55, 1.75), 18, 10)
    ball('belly', 0.7, 0, 0.3, 0.1, M['belly'], (0.9, 0.35, 1.6), 16, 8)
    ball('neck', 0.55, 0, 0.42, 1.2, M['skin'], (1.0, 0.6, 0.9))
    # upper jaw: a long tapered snout with a row of teeth along each side
    box('skull', 0.95, 0.45, 0.8, 0, 0.52, 1.75, M['skin'], 0.15, 2, tile=0.8)
    box('snout', 0.62, 0.3, 1.4, 0, 0.45, 2.75, M['skin'], 0.12, 2, tile=0.8)
    box('palate', 0.56, 0.06, 1.9, 0, 0.29, 2.45, M['mouth'], 0.02)
    for j in range(8):
        for sx in (-1, 1): cone('tooth', 0.045, 0, 0.17, sx * (0.27 - j * 0.012), 0.22, 1.6 + j * 0.24, M['tooth'], 6, down=True)
    for sx in (-1, 1):
        ball('eyebump', 0.17, sx * 0.3, 0.78, 1.55, M['skin'])
        ball('eye', 0.11, sx * 0.34, 0.86, 1.6, M['eye'])
        ball('pupil', 0.05, sx * 0.37, 0.88, 1.68, M['pupil'], (0.4, 1, 1))
        ball('nostril', 0.05, sx * 0.12, 0.62, 3.35, M['skin'])
    # tail: tapering segments with a double ridge of scutes, curling slightly
    for k in range(7):
        t = k / 6; z = -1.2 - k * 0.45; x = 0.25 * t * t
        ball('tail', 0.5 * (1 - 0.75 * t), x, 0.38 - 0.12 * t, z, M['skin'], (1, 0.6, 1.3), 12, 8)
        for sx in (-1, 1): cone('scute', 0.07, 0, 0.18, x + sx * 0.12 * (1 - t), 0.62 - 0.22 * t, z, M['skin'], 4)
    for k in range(6):
        for sx in (-1, 1): cone('scute', 0.08, 0, 0.2, sx * 0.25, 0.86, -0.9 + k * 0.38, M['skin'], 4)
    for sx in (-1, 1):   # splayed legs with claws
        for z, back in ((0.85, False), (-0.85, True)):
            tube('leg', (sx * 0.55, 0.35, z), (sx * 1.05, 0.12, z + (-0.15 if back else 0.15)), 0.17, M['skin'], 8)
            ball('foot', 0.2, sx * 1.1, 0.08, z + (-0.2 if back else 0.25), M['skin'], (1.2, 0.5, 1.3))
            for c in (-1, 0, 1): ball('claw', 0.035, sx * 1.12 + c * 0.08, 0.05, z + (-0.42 if back else 0.48), M['tooth'], (1, 0.6, 1.8), 6, 4)
    bb.join_all('pit-gator'); bb.export_safe('pit-gator')

def gator_jaw():
    reset(); M = materials()
    box('jawbone', 0.6, 0.18, 1.95, 0, -0.05, 0.98, M['skin'], 0.08, 2, tile=0.8)
    box('tongue', 0.45, 0.04, 1.6, 0, 0.05, 0.95, M['mouth'], 0.02)
    for j in range(8):
        for sx in (-1, 1): cone('tooth', 0.04, 0, 0.15, sx * (0.24 - j * 0.012), 0.12, 0.25 + j * 0.22, M['tooth'], 6)
    bb.join_all('pit-jaw'); bb.export_safe('pit-jaw')

arena(); gator_body(); gator_jaw()

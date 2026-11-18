# Swamp Fair models (CC0, modeled from scratch for Swamp City).
# MML axes: x right, y up, z toward the viewer. Blender = (x, -z, y). Origins are noted per model.
import bpy, bmesh, math, sys
sys.path.insert(0, '/home/claude/bscripts')
import boats_build as bb
from boats_build import reset, mat, srgb, box_uv, smooth, join_all, OUT
from mathutils import Vector

def P(x, y, z): return (x, -z, y)
def S(w, h, d): return (w, d, h)
def part(name, size, loc, m, bevel=0.03, seg=2, rot=(0, 0, 0), tile=1.0):
    return bb.rbox(name, S(*size), P(*loc), m, bevel, seg, rot, tile)
def tubeM(name, a, b, r, m, verts=8): return bb.tube(name, P(*a), P(*b), r, m, verts)
def ball(name, r, at, m, seg=6, rings=4): return bb.sphere(name, r, P(*at), m, seg=seg, rings=rings)
def ringZ(name, R, r, at, m, segs=64, minor=8):
    """torus whose axis is MML z (a wheel rim)"""
    bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=r, location=P(*at), rotation=(math.radians(90), 0, 0), major_segments=segs, minor_segments=minor)
    o = bpy.context.active_object; o.name = name; o.data.materials.append(m); box_uv(o); smooth(o, 60); return o
def ringY(name, R, r, at, m, segs=64, minor=8):
    """torus lying flat (axis MML y)"""
    bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=r, location=P(*at), major_segments=segs, minor_segments=minor)
    o = bpy.context.active_object; o.name = name; o.data.materials.append(m); box_uv(o); smooth(o, 60); return o
def cylY(name, r, h, at, m, verts=24, tile=1.0, cap=True): return bb.cyl(name, r, h, P(*at), m, verts=verts, tile=tile, cap=cap)
def cone(name, r1, r2, h, at, m, verts=24):
    bpy.ops.mesh.primitive_cone_add(radius1=r1, radius2=r2, depth=h, location=P(*at), vertices=verts)
    o = bpy.context.active_object; o.name = name; o.data.materials.append(m); box_uv(o); smooth(o, 50); return o
def uvplane(o, w, h, cx, cy, flip=False):
    """map a flat face texture 0..1 across w x h (MML x/y) centred on (cx, cy)"""
    me = o.data; uv = me.uv_layers.active.data; mw = o.matrix_world
    for p in me.polygons:
        for li in p.loop_indices:
            v = mw @ me.vertices[me.loops[li].vertex_index].co   # world: Blender x, y(-z), z(up)
            u = (v.x - cx) / w
            uv[li].uv = ((-u if flip else u) + 0.5, (v.z - cy) / h + 0.5)   # flip for faces seen from -z
def export(name):
    join_all(name)
    try: bpy.ops.export_scene.gltf(filepath=OUT + name + '.glb', export_format='GLB', export_apply=True, export_yup=True, export_vertex_color='NONE')
    except TypeError: bpy.ops.export_scene.gltf(filepath=OUT + name + '.glb', export_format='GLB', export_apply=True, export_yup=True)
    print('exported', name)

def M():
    return dict(
        WHITE=mat('enamel', srgb('#f2ede0'), None, 0.35, 0.1),
        TEAL=mat('teal', srgb('#1f8f8a'), None, 0.35, 0.2),
        STEEL=mat('steel', srgb('#cfd4d8'), None, 0.3, 0.6),
        DARK=mat('dark', srgb('#1a1418'), None, 0.6),
        GOLD=mat('gold', srgb('#d9a33a'), 'gold.jpg', 0.3, 0.45),
        WOOD=mat('woodpolish', srgb('#6b4426'), 'teak.jpg', 0.5),
        DECK=mat('deck', srgb('#8a6a48'), 'teak.jpg', 0.7),
        CONC=mat('concrete', srgb('#9a968c'), None, 0.9),
        BULB=mat('bulb', srgb('#ffe2a0'), None, 0.2, emit=srgb('#ffd27a'), emit_k=1.8),
        BULBP=mat('bulbpink', srgb('#ffb3e0'), None, 0.2, emit=srgb('#ff6ec7'), emit_k=1.6),
        BULBT=mat('bulbteal', srgb('#b3fff6'), None, 0.2, emit=srgb('#3ff2e0'), emit_k=1.6),
        EYE=mat('gatoreye', srgb('#ffd23b'), None, 0.2, emit=srgb('#ffd23b'), emit_k=2.0))

# =====================================================================
# BAYOU EYE Ferris wheel. Wheel plane = MML x/y, spins about z. Hub at (0, 18.2, 0) in the frame model.
# ferris-frame: origin on the ground under the hub. ferris-rim: origin at the hub. gondola: origin at its hanger pivot.
# =====================================================================
HUB, R = 18.2, 14.0
def ferris_frame():
    reset(); bb._mats.clear(); m = M()
    for zs in (-1, 1):
        z = zs * 2.7
        for xs in (-1, 1):
            foot = (xs * 8.0, 0.2, zs * 3.8); top = (xs * 0.35, HUB, z)
            tubeM(f'leg{zs}{xs}', foot, top, 0.32, m['WHITE'], 12)
            part(f'pad{zs}{xs}', (1.6, 0.4, 1.6), (foot[0], 0.2, foot[2]), m['CONC'], 0.04)
        for k, y in enumerate((3.5, 7.5, 11.5, 15.0)):    # cross braces
            t = y / HUB; xw = 8.0 * (1 - t) + 0.35 * t; zz = zs * (3.8 * (1 - t) + 2.7 * t)
            tubeM(f'br{zs}{k}', (-xw, y, zz), (xw, y, zz), 0.16, m['TEAL'], 8)
            if k < 3:
                y2 = (3.5, 7.5, 11.5, 15.0)[k + 1]; t2 = y2 / HUB; xw2 = 8.0 * (1 - t2) + 0.35 * t2; zz2 = zs * (3.8 * (1 - t2) + 2.7 * t2)
                tubeM(f'dg{zs}{k}a', (-xw, y, zz), (xw2, y2, zz2), 0.1, m['TEAL'], 6)
                tubeM(f'dg{zs}{k}b', (xw, y, zz), (-xw2, y2, zz2), 0.1, m['TEAL'], 6)
        cylY(f'bearing{zs}', 0.75, 0.5, (0, HUB, 0), m['DARK'])  # placeholder, rotated below
        o = bpy.context.active_object; o.location = P(0, HUB, z); o.rotation_euler = (math.radians(90), 0, 0); bpy.ops.object.transform_apply(rotation=True)
    tubeM('axle', (0, HUB, -3.0), (0, HUB, 3.0), 0.42, m['STEEL'], 16)
    # loading platform in front (-z), deck at y 1.0, stairs down toward the entrance
    part('deck', (7.0, 0.2, 3.2), (0, 0.9, -2.9), m['DECK'], 0.02, tile=1.5)
    for xs in (-1, 1):
        for zz in (-1.4, -4.4): part(f'post{xs}{zz}', (0.18, 0.9, 0.18), (xs * 3.4, 0.45, zz), m['WOOD'], 0.02)
    for k in range(5):   # stairs from the deck down to the ground, toward -z
        part(f'step{k}', (3.0, 0.16, 0.42), (0, 0.8 - k * 0.18, -4.7 - k * 0.42), m['DECK'], 0.01, tile=1.5)
    for xs in (-1, 1):   # platform handrails, side and front, leaving the stair gap and the gondola side open
        tubeM(f'hrS{xs}', (xs * 3.45, 2.0, -1.4), (xs * 3.45, 2.0, -4.45), 0.05, m['GOLD'])
        tubeM(f'hrF{xs}', (xs * 3.45, 2.0, -4.45), (xs * 1.6, 2.0, -4.45), 0.05, m['GOLD'])
        tubeM(f'hrStair{xs}', (xs * 1.55, 2.0, -4.45), (xs * 1.55, 1.1, -6.6), 0.05, m['GOLD'])
        for zz in (-1.4, -2.9, -4.45): tubeM(f'hp{xs}{zz}', (xs * 3.45, 1.0, zz), (xs * 3.45, 2.0, zz), 0.04, m['GOLD'])
    # ticket booth on the platform corner
    part('booth', (1.3, 2.2, 1.3), (-5.2, 1.1, -4.6), m['TEAL'], 0.04)
    part('booth-roof', (1.6, 0.2, 1.6), (-5.2, 2.3, -4.6), m['GOLD'], 0.04)
    export('ferris-frame')

def ferris_rim():
    reset(); bb._mats.clear(); m = M()
    for zs in (-1, 1):
        z = zs * 1.3
        ringZ(f'rim{zs}', R, 0.2, (0, 0, z), m['WHITE'], 96, 8)
        ringZ(f'rimin{zs}', R * 0.62, 0.13, (0, 0, z), m['TEAL'], 72, 6)
        for k in range(12):
            a = math.radians(k * 30 + 15)
            tubeM(f'sp{zs}{k}', (math.cos(a) * 1.0, math.sin(a) * 1.0, z * 0.8), (math.cos(a) * R, math.sin(a) * R, z), 0.07, m['WHITE'], 6)
            a2 = math.radians(k * 30); a3 = math.radians(k * 30 + 30)
            tubeM(f'zz{zs}{k}', (math.cos(a2) * R * 0.62, math.sin(a2) * R * 0.62, z), (math.cos(a3) * R, math.sin(a3) * R, z), 0.05, m['TEAL'], 6)
        for k in range(72):   # rim bulbs, alternating warm and pink
            a = math.radians(k * 5)
            ball(f'b{zs}{k}', 0.13, (math.cos(a) * (R + 0.25), math.sin(a) * (R + 0.25), z), m['BULB'] if k % 2 else m['BULBP'])
        for k in range(36):
            a = math.radians(k * 10)
            ball(f'bi{zs}{k}', 0.1, (math.cos(a) * (R * 0.62 + 0.18), math.sin(a) * (R * 0.62 + 0.18), z), m['BULBT'])
    for k in range(12):   # gondola axles between the rims
        a = math.radians(k * 30)
        tubeM(f'gax{k}', (math.cos(a) * R, math.sin(a) * R, -1.35), (math.cos(a) * R, math.sin(a) * R, 1.35), 0.09, m['STEEL'], 8)
    # hub: gold drum with a bulb sunburst on both faces
    bpy.ops.mesh.primitive_cylinder_add(radius=1.6, depth=1.9, location=P(0, 0, 0), rotation=(math.radians(90), 0, 0), vertices=32)
    o = bpy.context.active_object; o.data.materials.append(m['GOLD']); box_uv(o); smooth(o, 50)
    for zs in (-1, 1):
        for k in range(16):
            a = math.radians(k * 22.5)
            ball(f'hb{zs}{k}', 0.12, (math.cos(a) * 1.3, math.sin(a) * 1.3, zs * 0.98), m['BULB'])
        ball(f'hc{zs}', 0.45, (0, 0, zs * 1.0), m['BULBP'], 12, 8)
    export('ferris-rim')

def gondola(name, paint):
    reset(); bb._mats.clear(); m = M()
    PNT = mat('paint-' + paint, srgb(paint), 'carpaint.jpg', 0.3, 0.3)
    FL = -3.0   # floor top, below the pivot
    part('floor', (2.4, 0.16, 1.8), (0, FL - 0.08, 0), m['DECK'], 0.03, tile=1.2)
    part('tub-bottom', (2.5, 0.35, 1.9), (0, FL - 0.3, 0), PNT, 0.12, 3)
    part('wall-back', (2.5, 0.95, 0.1), (0, FL + 0.47, 0.9), PNT, 0.04)
    for xs in (-1, 1): part(f'wall{xs}', (0.1, 0.95, 1.9), (xs * 1.2, FL + 0.47, 0), PNT, 0.04)
    part('wall-front', (2.5, 0.45, 0.1), (0, FL + 0.22, -0.9), PNT, 0.04)   # low front lip you hop over
    part('trim', (2.62, 0.08, 2.02), (0, FL + 0.96, 0), m['GOLD'], 0.02)
    part('bench', (2.1, 0.12, 0.45), (0, FL + 0.45, 0.6), m['WOOD'], 0.02)
    # canopy: scalloped dome on four posts, hangers up to the pivot
    for xs in (-1, 1):
        for zs in (-1, 1): tubeM(f'post{xs}{zs}', (xs * 1.15, FL + 0.9, zs * 0.85), (xs * 1.05, FL + 2.3, zs * 0.8), 0.04, m['GOLD'], 6)
    c = cone('canopy', 1.55, 0.25, 0.7, (0, FL + 2.6, 0), PNT, 16); c.scale = (1.0, 0.8, 1.0); bpy.ops.object.transform_apply(scale=True)
    ringY('canopy-edge', 1.5, 0.06, (0, FL + 2.27, 0), m['GOLD'], 32, 6).scale = (1.0, 0.8, 1.0); bpy.ops.object.transform_apply(scale=True)
    for k in range(12):
        a = math.radians(k * 30); ball(f'cb{k}', 0.07, (math.cos(a) * 1.5, FL + 2.22, math.sin(a) * 1.2), m['BULB'])
    tubeM('hanger', (0, FL + 2.9, 0), (0, 0, 0), 0.07, m['STEEL'], 8)
    part('yoke', (0.3, 0.3, 0.3), (0, 0, 0), m['DARK'], 0.05)
    export(name)

# =====================================================================
# GATOR-GO-ROUND carousel. carousel: the turning part, origin at the centre on the ground.
# carousel-base: the fixed step ring. Figures ride poles at r 3.2 (inner) and 5.0 (outer).
# =====================================================================
def carousel():
    reset(); bb._mats.clear(); m = M()
    RED = mat('carouselred', srgb('#8a1c3a'), None, 0.4, 0.1)
    FASC = mat('fascia', (1, 1, 1), 'carousel-fascia.jpg', 0.4, emit=True, emit_k=0.35)
    cylY('deck', 6.5, 0.3, (0, 0.45, 0), m['DECK'], 48, tile=1.5)
    ringY('deck-edge', 6.5, 0.1, (0, 0.55, 0), m['GOLD'], 72, 6)
    cylY('deck-skirt', 6.45, 0.35, (0, 0.2, 0), RED, 48)
    cylY('column', 1.1, 4.5, (0, 2.85, 0), RED, 24)
    for k in range(8):   # mirror panels on the centre column
        a = math.radians(k * 45 + 22.5)
        part(f'mir{k}', (0.6, 1.6, 0.04), (math.cos(a) * 1.12, 2.4, math.sin(a) * 1.12), m['STEEL'], 0.0, rot=(0, 0, -a + math.pi / 2))
    for rr, n, off in ((3.2, 8, 0), (5.0, 8, 22.5)):     # brass poles
        for k in range(n):
            a = math.radians(k * 45 + off)
            cylY(f'pole{rr}{k}', 0.05, 4.0, (math.cos(a) * rr, 2.6, math.sin(a) * rr), m['GOLD'], 10)
    # canopy: fascia drum, scalloped valance, striped roof cone, finial
    cyl = cylY('fascia', 7.0, 0.8, (0, 4.95, 0), FASC, 48, cap=False)
    me = cyl.data
    for p in me.polygons:
        for li in p.loop_indices:
            v = me.vertices[me.loops[li].vertex_index].co
            me.uv_layers.active.data[li].uv = ((math.atan2(v.y, v.x) / (2 * math.pi) + 0.5) * 8, (v.z + 0.4) / 0.8)   # local coords, centred
    cylY('ceiling', 6.95, 0.1, (0, 4.6, 0), RED, 48)
    for k in range(24):    # scallops
        a = math.radians(k * 15)
        bb.sphere(f'sc{k}', 0.55, P(math.cos(a) * 7.0, 4.5, math.sin(a) * 7.0), RED, scale=(1, 1, 0.5), seg=10, rings=6)
    roof = cone('roof', 7.4, 0.3, 2.4, (0, 6.55, 0), mat('stripe-red', (1, 1, 1), 'stripe-red.jpg', 0.6), 32)
    me = roof.data
    for p in me.polygons:
        for li in p.loop_indices:
            v = me.vertices[me.loops[li].vertex_index].co
            me.uv_layers.active.data[li].uv = ((math.atan2(v.y, v.x) / (2 * math.pi) + 0.5) * 4, v.z / 2.4)
    ball('finial', 0.45, (0, 8.0, 0), m['GOLD'], 14, 8); cylY('spire', 0.06, 1.2, (0, 8.6, 0), m['GOLD'], 8)
    for k in range(48):
        a = math.radians(k * 7.5)
        ball(f'fb{k}', 0.09, (math.cos(a) * 7.06, 5.37, math.sin(a) * 7.06), m['BULB'])
        ball(f'fb2{k}', 0.09, (math.cos(a) * 7.06, 4.53, math.sin(a) * 7.06), m['BULBP'] if k % 2 else m['BULB'])
    export('carousel')

def carousel_base():
    reset(); bb._mats.clear(); m = M()
    RED = mat('carouselred', srgb('#8a1c3a'), None, 0.4, 0.1)
    bpy.ops.mesh.primitive_cylinder_add(radius=7.6, depth=0.3, location=P(0, 0.15, 0), vertices=64)
    o = bpy.context.active_object; o.data.materials.append(m['DECK']); box_uv(o, 1.5)
    bpy.ops.mesh.primitive_cylinder_add(radius=6.6, depth=1.0, location=P(0, 0.15, 0), vertices=64)
    c = bpy.context.active_object
    mod = o.modifiers.new('ring', 'BOOLEAN'); mod.operation = 'DIFFERENCE'; mod.object = c
    try: mod.solver = 'EXACT'
    except Exception: pass
    bpy.context.view_layer.objects.active = o; bpy.ops.object.modifier_apply(modifier='ring'); bpy.data.objects.remove(c)
    ringY('base-edge', 7.6, 0.08, (0, 0.3, 0), m['GOLD'], 72, 6)
    for k in range(16):   # little rope stanchions, leaving the entrance (-z) open
        a = math.radians(k * 22.5 + 11.25)
        if abs(math.degrees(a) - 270) < 25: continue
        cylY(f'st{k}', 0.05, 0.9, (math.cos(a) * 7.9, 0.45, math.sin(a) * 7.9), m['GOLD'], 8)
        ball(f'stb{k}', 0.08, (math.cos(a) * 7.9, 0.95, math.sin(a) * 7.9), m['GOLD'])
    export('carousel-base')

def carousel_gator():
    """origin on the pole axis at deck level; body centred around y 1.2, nose toward +x (direction of travel)"""
    reset(); bb._mats.clear(); m = M()
    SK = mat('gatorpaint', (1, 1, 1), 'gatorpaint.jpg', 0.45)
    BELLY = mat('belly', srgb('#e8dca0'), None, 0.5)
    SAD = mat('saddle', srgb('#b3203a'), None, 0.4)
    body = bb.sphere('body', 0.5, P(0, 1.2, 0), SK, scale=(1.5, 0.55, 0.45), seg=20, rings=12)
    bb.sphere('belly', 0.45, P(0, 1.1, 0), BELLY, scale=(1.35, 0.5, 0.35), seg=16, rings=10)
    bb.sphere('head', 0.32, P(0.85, 1.35, 0), SK, scale=(1.3, 0.8, 0.75), seg=16, rings=10)
    part('snout', (0.6, 0.16, 0.34), (1.25, 1.3, 0), SK, 0.06, 3)
    part('jaw', (0.55, 0.1, 0.3), (1.22, 1.17, 0), SK, 0.04, 2, rot=(0, math.radians(-8), 0))
    for zs in (-1, 1):
        ball(f'eye{zs}', 0.09, (0.85, 1.58, zs * 0.14), m['EYE'], 10, 6)
        tubeM(f'legf{zs}', (0.4, 1.0, zs * 0.18), (0.6, 0.65, zs * 0.4), 0.07, SK)
        tubeM(f'legb{zs}', (-0.45, 1.0, zs * 0.18), (-0.7, 0.7, zs * 0.42), 0.08, SK)
    tubeM('tail1', (-0.7, 1.15, 0), (-1.3, 1.25, 0.1), 0.14, SK, 10); tubeM('tail2', (-1.3, 1.25, 0.1), (-1.8, 1.5, 0.25), 0.08, SK, 8)
    part('saddle', (0.6, 0.12, 0.6), (-0.05, 1.47, 0), SAD, 0.05, 3)
    for zs in (-1, 1): part(f'stirrup{zs}', (0.1, 0.4, 0.04), (-0.05, 1.2, zs * 0.33), m['GOLD'], 0.01)
    export('carousel-gator')

def carousel_frog():
    reset(); bb._mats.clear(); m = M()
    FR = mat('frog', srgb('#6fd04a'), None, 0.45)
    BELLY = mat('belly', srgb('#f0e6b0'), None, 0.5)
    SAD = mat('saddle', srgb('#2a6fd0'), None, 0.4)
    bb.sphere('body', 0.55, P(0, 1.15, 0), FR, scale=(1.1, 0.75, 0.85), seg=20, rings=12)
    bb.sphere('belly', 0.45, P(0.2, 1.05, 0), BELLY, scale=(0.9, 0.6, 0.75), seg=16, rings=10)
    for zs in (-1, 1):
        ball(f'eyeball{zs}', 0.17, (0.42, 1.62, zs * 0.25), mat('white', srgb('#ffffff'), None, 0.3), 12, 8)
        ball(f'pupil{zs}', 0.08, (0.55, 1.65, zs * 0.27), m['DARK'], 8, 6)
        tubeM(f'legb{zs}', (-0.35, 1.0, zs * 0.4), (-0.1, 0.65, zs * 0.6), 0.12, FR)
        tubeM(f'legf{zs}', (0.4, 0.95, zs * 0.3), (0.55, 0.62, zs * 0.38), 0.07, FR)
    bb.sphere('mouth', 0.3, P(0.55, 1.25, 0), mat('mouth', srgb('#b02a40'), None, 0.5), scale=(0.3, 0.12, 1.0), seg=12, rings=6)
    part('saddle', (0.55, 0.12, 0.6), (-0.1, 1.55, 0), SAD, 0.05, 3)
    export('carousel-frog')

# =====================================================================
# GATOR DROP tower. drop-tower: origin at the base centre. drop-ring: the riding ring, origin at its floor centre.
# =====================================================================
TOWER = 32.0
def drop_tower():
    reset(); bb._mats.clear(); m = M()
    SK = mat('gatorpaint', (1, 1, 1), 'gatorpaint.jpg', 0.45)
    PURP = mat('purple', srgb('#5a2a8a'), None, 0.4, 0.2)
    h = 1.1
    for xs in (-1, 1):
        for zs in (-1, 1): tubeM(f'c{xs}{zs}', (xs * h, 0, zs * h), (xs * h, TOWER, zs * h), 0.16, m['WHITE'], 10)
    y = 0.0; k = 0
    while y < TOWER - 0.1:
        y2 = min(TOWER, y + 2.0)
        for a, b in (((-h, -h), (h, -h)), ((h, -h), (h, h)), ((h, h), (-h, h)), ((-h, h), (-h, -h))):
            tubeM(f'r{k}{a}', (a[0], y2, a[1]), (b[0], y2, b[1]), 0.06, PURP, 6)
            tubeM(f'd{k}{a}', (a[0], y, a[1]), (b[0], y2, b[1]), 0.04, PURP, 6)
        y = y2; k += 1
    for k in range(int(TOWER / 1.0)):   # chase lights up two faces
        ball(f'l{k}', 0.1, (0, 0.5 + k, -h - 0.12), m['BULBP'] if k % 2 else m['BULB'])
        ball(f'm{k}', 0.1, (0, 0.5 + k, h + 0.12), m['BULBT'] if k % 2 else m['BULB'])
    # base plinth with steps
    cylY('plinth', 4.8, 0.3, (0, 0.15, 0), m['CONC'], 48)
    ringY('plinth-edge', 4.8, 0.06, (0, 0.3, 0), m['GOLD'], 64, 6)
    # top: cap and a giant gator head, jaws open to the north (-z)
    part('cap', (3.4, 0.6, 3.4), (0, TOWER + 0.3, 0), PURP, 0.1, 3)
    bb.sphere('head', 1.6, P(0, TOWER + 2.0, 0.4), SK, scale=(1.05, 0.75, 1.15), seg=24, rings=14)
    part('upper-jaw', (2.0, 0.55, 2.8), (0, TOWER + 2.45, -2.2), SK, 0.25, 3, rot=(math.radians(-14), 0, 0))
    part('lower-jaw', (1.9, 0.4, 2.5), (0, TOWER + 1.1, -1.9), SK, 0.2, 3, rot=(math.radians(10), 0, 0))
    part('mouth', (1.7, 0.6, 2.2), (0, TOWER + 1.75, -1.6), mat('mouth', srgb('#8a1c2a'), None, 0.6), 0.2, 3)
    tw = mat('tooth', srgb('#fffbe8'), None, 0.3)
    for k in range(7):
        x = -0.8 + k * 0.27
        cone(f'tu{k}', 0.1, 0.0, 0.32, (x, TOWER + 2.0, -3.2 + abs(x) * 0.3), tw, 8).rotation_euler = (math.radians(180), 0, 0)
        bpy.ops.object.transform_apply(rotation=True)
        cone(f'tl{k}', 0.09, 0.0, 0.28, (x, TOWER + 1.42, -2.95 + abs(x) * 0.3), tw, 8)
    for xs in (-1, 1):
        ball(f'eyebump{xs}', 0.5, (xs * 0.75, TOWER + 3.05, -0.3), SK, 14, 10)
        ball(f'eye{xs}', 0.32, (xs * 0.78, TOWER + 3.2, -0.62), m['EYE'], 14, 10)
        part(f'pupil{xs}', (0.08, 0.42, 0.06), (xs * 0.78, TOWER + 3.2, -0.93), m['DARK'], 0.02)
        ball(f'nostril{xs}', 0.12, (xs * 0.35, TOWER + 2.75, -3.45), m['DARK'], 8, 6)
    export('drop-tower')

def drop_ring():
    reset(); bb._mats.clear(); m = M()
    PURP = mat('purple', srgb('#5a2a8a'), None, 0.4, 0.2)
    bpy.ops.mesh.primitive_cylinder_add(radius=3.7, depth=0.2, location=P(0, -0.1, 0), vertices=48)
    o = bpy.context.active_object; o.data.materials.append(m['DECK']); box_uv(o, 1.2)
    bpy.ops.mesh.primitive_cylinder_add(radius=1.75, depth=1.0, location=P(0, -0.1, 0), vertices=48)
    c = bpy.context.active_object
    mod = o.modifiers.new('hole', 'BOOLEAN'); mod.operation = 'DIFFERENCE'; mod.object = c
    try: mod.solver = 'EXACT'
    except Exception: pass
    bpy.context.view_layer.objects.active = o; bpy.ops.object.modifier_apply(modifier='hole'); bpy.data.objects.remove(c)
    ringY('outer-lip', 3.7, 0.12, (0, 0.5, 0), m['GOLD'], 64, 6)
    for k in range(16):
        a = math.radians(k * 22.5)
        cylY(f'lp{k}', 0.05, 0.5, (math.cos(a) * 3.7, 0.25, math.sin(a) * 3.7), m['GOLD'], 6)
    for k in range(8):   # seat backs facing out, with shoulder bars, against the inner collar
        a = math.radians(k * 45 + 22.5)
        cx, cz = math.cos(a) * 2.15, math.sin(a) * 2.15
        part(f'seat{k}', (0.9, 1.6, 0.25), (cx, 0.8, cz), PURP, 0.08, 3, rot=(0, 0, -a - math.pi / 2))
        part(f'head{k}', (0.5, 0.35, 0.3), (math.cos(a) * 2.15, 1.75, math.sin(a) * 2.15), PURP, 0.1, 3, rot=(0, 0, -a - math.pi / 2))
    cylY('collar', 1.85, 1.9, (0, 0.95, 0), m['WHITE'], 32, cap=False)
    ringY('collar-top', 1.85, 0.1, (0, 1.9, 0), m['GOLD'], 48, 6)
    for k in range(24):
        a = math.radians(k * 15); ball(f'rb{k}', 0.07, (math.cos(a) * 3.82, 0.0, math.sin(a) * 3.82), m['BULBP'] if k % 2 else m['BULBT'])
    export('drop-ring')

# =====================================================================
# Midway: Whack-a-Gator booth (+ popper), high striker (+ puck), entrance arch, food stands, light pole, garland
# =====================================================================
def whack_booth():
    """origin at the front of the counter on the ground; holes at x -1.4..1.4 step 0.7, centre z -0.45, top y 1.0"""
    reset(); bb._mats.clear(); m = M()
    ST = mat('stripe-teal', (1, 1, 1), 'stripe-teal.jpg', 0.6)
    BRD = mat('whack-board', (1, 1, 1), 'whack-board.jpg', 0.4, emit=True, emit_k=0.6)
    GRN = mat('green', srgb('#1f5a34'), None, 0.5)
    part('counter', (4.2, 1.0, 1.0), (0, 0.5, -0.5), GRN, 0.04)
    part('counter-top', (4.4, 0.08, 1.15), (0, 1.0, -0.5), m['WOOD'], 0.02)
    for k in range(5):
        x = -1.4 + k * 0.7
        cylY(f'hole{k}', 0.22, 0.03, (x, 1.05, -0.45), m['DARK'], 20)
        ringY(f'holering{k}', 0.24, 0.035, (x, 1.06, -0.45), m['GOLD'], 24, 6)
    part('back', (4.4, 3.4, 0.15), (0, 1.7, -2.2), GRN, 0.03)
    brd = part('board', (3.8, 1.9, 0.04), (0, 2.25, -2.1), BRD, 0.0)
    uvplane(brd, 3.8, 1.9, 0, 2.25)
    for xs in (-1, 1):
        part(f'side{xs}', (0.15, 3.4, 2.0), (xs * 2.2, 1.7, -1.2), GRN, 0.03)
        tubeM(f'pole{xs}', (xs * 2.3, 0, 0.1), (xs * 2.3, 3.5, 0.1), 0.07, m['GOLD'], 8)
    aw = part('awning', (4.8, 0.08, 2.6), (0, 3.55, -0.9), ST, 0.0, rot=(math.radians(-12), 0, 0), tile=1.0)
    for k in range(12): ball(f'ab{k}', 0.08, (-2.3 + k * 0.42, 3.3, 0.35), m['BULB'])
    export('whack-booth')

def whack_gator():
    """pops up through a hole: origin at the counter top, head centre at y 0.18 when up"""
    reset(); bb._mats.clear(); m = M()
    SK = mat('gatorpaint', (1, 1, 1), 'gatorpaint.jpg', 0.45)
    bb.sphere('head', 0.2, P(0, 0.1, 0), SK, scale=(0.9, 1.0, 1.1), seg=14, rings=10)
    part('snout', (0.24, 0.1, 0.3), (0, 0.08, 0.2), SK, 0.04, 2)
    for xs in (-1, 1):
        ball(f'eye{xs}', 0.06, (xs * 0.09, 0.27, 0.06), m['EYE'], 8, 6)
        ball(f'pupil{xs}', 0.025, (xs * 0.09, 0.28, 0.115), m['DARK'], 6, 4)
    cylY('neck', 0.15, 0.5, (0, -0.25, 0), SK, 14)
    export('whack-gator')

def striker():
    """high striker: origin at the pad on the ground; puck track runs up the front of the pole from y 0.9 to 7.4"""
    reset(); bb._mats.clear(); m = M()
    SC = mat('striker-scale', (1, 1, 1), 'striker-scale.jpg', 0.5, emit=True, emit_k=0.3)
    RED = mat('carouselred', srgb('#8a1c3a'), None, 0.4, 0.1)
    part('base', (2.0, 0.3, 1.6), (0, 0.15, 0), m['WOOD'], 0.04)
    part('pad', (0.8, 0.18, 0.6), (0, 0.39, 0.25), RED, 0.05, 3)
    part('pad-plate', (0.6, 0.04, 0.45), (0, 0.5, 0.25), m['STEEL'], 0.01)
    part('pole', (0.6, 7.2, 0.3), (0, 3.9, -0.45), RED, 0.04)
    sc = part('scale', (0.5, 6.4, 0.04), (0, 4.1, -0.28), SC, 0.0)
    uvplane(sc, 0.5, 6.4, 0, 4.1)
    for xs in (-1, 1): tubeM(f'rail{xs}', (xs * 0.33, 0.9, -0.25), (xs * 0.33, 7.4, -0.25), 0.025, m['STEEL'], 6)
    bb.sphere('bell', 0.42, P(0, 7.85, -0.3), m['GOLD'], scale=(1, 0.7, 1), seg=20, rings=10)
    ball('bell-knob', 0.08, (0, 8.18, -0.3), m['GOLD'])
    for k in range(10): ball(f'sb{k}', 0.07, (-0.38 if k % 2 else 0.38, 1.0 + k * 0.7, -0.24), m['BULB'])
    # mallet resting against the base
    tubeM('handle', (0.75, 0.3, 0.55), (1.05, 1.5, 0.3), 0.04, m['WOOD'], 8)
    part('mallet', (0.5, 0.26, 0.26), (1.07, 1.55, 0.3), RED, 0.06, 3, rot=(0, math.radians(14), 0))
    export('striker')

def striker_puck():
    reset(); bb._mats.clear(); m = M()
    part('puck', (0.3, 0.18, 0.12), (0, 0, 0), mat('puck', srgb('#ff3b3b'), None, 0.3, emit=srgb('#ff3b3b'), emit_k=0.6), 0.05, 3)
    export('striker-puck')

def fair_arch():
    """entrance arch spanning x -6..6, facing -z; sign label sits in code at y ~6.6"""
    reset(); bb._mats.clear(); m = M()
    SR = mat('stripe-red', (1, 1, 1), 'stripe-red.jpg', 0.6)
    PURP = mat('purple', srgb('#5a2a8a'), None, 0.4, 0.2)
    for xs in (-1, 1):
        x = xs * 6.0
        o = cylY(f'tower{xs}', 0.9, 7.0, (x, 3.5, 0), SR, 24, cap=False)
        me = o.data
        for p in me.polygons:
            for li in p.loop_indices:
                v = me.vertices[me.loops[li].vertex_index].co
                me.uv_layers.active.data[li].uv = ((math.atan2(v.y, v.x) / (2 * math.pi) + 0.5) * 3, v.z / 7)   # local coords
        ringY(f'band{xs}', 0.95, 0.08, (x, 7.0, 0), m['GOLD'], 32, 6)
        ringY(f'band2{xs}', 0.95, 0.08, (x, 0.3, 0), m['GOLD'], 32, 6)
        bb.sphere(f'dome{xs}', 1.0, P(x, 7.5, 0), PURP, scale=(1, 1.3, 1), seg=20, rings=12)
        cone(f'spike{xs}', 0.18, 0.0, 1.2, (x, 9.3, 0), m['GOLD'], 10)
        ball(f'top{xs}', 0.22, (x, 8.7, 0), m['GOLD'], 12, 8)
        for k in range(12): ball(f'tb{xs}{k}', 0.08, (x + math.cos(math.radians(k * 30)) * 0.95, 6.8, math.sin(math.radians(k * 30)) * 0.95), m['BULB'])
    # arched truss: two curved tubes with rungs and bulbs
    pts = [(math.cos(math.radians(a)) * 5.2, 5.6 + math.sin(math.radians(a)) * 1.6) for a in range(0, 181, 10)]
    for zs in (-1, 1):
        for i in range(len(pts) - 1):
            tubeM(f'ar{zs}{i}', (pts[i][0], pts[i][1], zs * 0.3), (pts[i + 1][0], pts[i + 1][1], zs * 0.3), 0.09, m['GOLD'], 8)
    for i, (x, y) in enumerate(pts):
        tubeM(f'rung{i}', (x, y, -0.3), (x, y, 0.3), 0.04, m['GOLD'], 6)
        ball(f'ab{i}', 0.12, (x, y + 0.16, -0.32), m['BULBP'] if i % 2 else m['BULB'])
    part('sign-back', (9.0, 1.4, 0.12), (0, 5.2, 0.05), PURP, 0.05, 3)
    export('fair-arch')

def stand(key, stripe):
    """food stand: origin at the front of the counter on the ground, facing -z; 3.2 wide"""
    reset(); bb._mats.clear(); m = M()
    ST = mat('stripe-' + stripe, (1, 1, 1), 'stripe-' + stripe + '.jpg', 0.6)
    HDR = mat('stand-' + key, (1, 1, 1), 'stand-' + key + '.jpg', 0.4, emit=True, emit_k=0.55)
    BODY = mat('standbody', srgb('#f2ede0'), 'paintwood.jpg', 0.6)
    part('body', (3.2, 2.4, 2.2), (0, 1.2, 1.1), BODY, 0.04)
    part('window', (2.6, 1.0, 0.05), (0, 1.75, -0.02), m['DARK'], 0.0)
    part('counter', (3.0, 0.1, 0.5), (0, 1.15, -0.2), m['WOOD'], 0.02)
    for k, x in enumerate((-0.9, -0.4, 0.5, 1.0)):
        cylY(f'cup{k}', 0.07, 0.18, (x, 1.29, -0.2), mat('cup' + str(k % 2), srgb(['#ff6ec7', '#3ff2e0'][k % 2]), None, 0.4), 10)
    aw = part('awning', (3.6, 0.06, 1.3), (0, 2.55, -0.45), ST, 0.0, rot=(math.radians(-18), 0, 0))
    for k in range(9): ball(f'v{k}', 0.12, (-1.6 + k * 0.4, 2.33, -1.08), ST, 8, 4)
    hdr = part('header', (3.2, 0.8, 0.08), (0, 3.15, 0.1), HDR, 0.0)
    uvplane(hdr, 3.2, 0.8, 0, 3.15, flip=True)
    part('header-back', (3.3, 0.9, 0.1), (0, 3.15, 0.2), m['DARK'], 0.02)
    for k in range(8): ball(f'b{k}', 0.06, (-1.4 + k * 0.4, 3.62, 0.04), m['BULB'])
    export('stand-' + key)

def fair_pole():
    """striped light pole, origin on the ground; the garland hooks at y 5.6"""
    reset(); bb._mats.clear(); m = M()
    o = cylY('pole', 0.11, 5.8, (0, 2.9, 0), mat('stripe-gold', (1, 1, 1), 'stripe-gold.jpg', 0.5), 12, cap=False)
    me = o.data
    for p in me.polygons:
        for li in p.loop_indices:
            v = me.vertices[me.loops[li].vertex_index].co
            me.uv_layers.active.data[li].uv = (math.atan2(v.y, v.x) / (2 * math.pi) + 0.5, v.z / 0.8)
    cylY('foot', 0.3, 0.2, (0, 0.1, 0), m['DARK'], 16)
    ball('lamp', 0.32, (0, 6.05, 0), m['BULB'], 14, 10)
    cone('lamp-cap', 0.38, 0.05, 0.3, (0, 6.42, 0), m['GOLD'], 14)
    for k in range(4):
        a = math.radians(k * 90)
        tubeM(f'arm{k}', (0, 5.6, 0), (math.cos(a) * 0.5, 5.75, math.sin(a) * 0.5), 0.03, m['GOLD'], 6)
        ball(f'lb{k}', 0.13, (math.cos(a) * 0.55, 5.6, math.sin(a) * 0.55), m['BULBP'] if k % 2 else m['BULBT'], 10, 6)
    export('fair-pole')

def fair_garland():
    """one 12 m span of string lights along +x from (0,0,0) to (12,0,0), sagging 0.8 m"""
    reset(); bb._mats.clear(); m = M()
    pts = [(x, -0.8 * (1 - ((x - 6) / 6) ** 2), 0) for x in [i * 0.5 for i in range(25)]]
    for i in range(len(pts) - 1): tubeM(f'w{i}', pts[i], pts[i + 1], 0.012, m['DARK'], 4)
    cols = [m['BULB'], m['BULBP'], m['BULBT'], m['BULB']]
    for i in range(1, 24):
        x, y, z = pts[i]; ball(f'b{i}', 0.07, (x, y - 0.1, z), cols[i % 4], 8, 6)
    export('fair-garland')

ferris_frame(); ferris_rim()
for nm, c in (('gondola-pink', '#e0457a'), ('gondola-teal', '#1f9f9a'), ('gondola-gold', '#d9a21b'), ('gondola-purple', '#7a3cb0')): gondola(nm, c)
carousel(); carousel_base(); carousel_gator(); carousel_frog()
drop_tower(); drop_ring()
whack_booth(); whack_gator(); striker(); striker_puck(); fair_arch()
for key, st in (('funnel', 'red'), ('boudin', 'gold'), ('snowball', 'teal'), ('gatorstick', 'purple')): stand(key, st)
fair_pole(); fair_garland()

# Bayou Savings & Trust (CC0, modeled for Swamp City): neoclassical bank, the vault, and money bags.
# MML axes: x right, y up, z toward the viewer. Blender = (x, -z, y).
# bank: origin at the bank centre on the ground (MML (0, 0, CZ)). North (-z) is the columned front; the big screen hangs on the south face.
import bpy, bmesh, math, sys
sys.path.insert(0, '/home/claude/bscripts')
import boats_build as bb
from boats_build import reset, mat, srgb, box_uv, smooth, join_all, OUT

def P(x, y, z): return (x, -z, y)
def S(w, h, d): return (w, d, h)
def part(name, size, loc, m, bevel=0.03, seg=2, rot=(0, 0, 0), tile=1.0):
    return bb.rbox(name, S(*size), P(*loc), m, bevel, seg, rot, tile)
def tubeM(name, a, b, r, m, verts=8): return bb.tube(name, P(*a), P(*b), r, m, verts)
def ball(name, r, at, m, seg=8, rings=6, scale=(1, 1, 1)): return bb.sphere(name, r, P(*at), m, scale=scale, seg=seg, rings=rings)
def cylY(name, r, h, at, m, verts=24, cap=True): return bb.cyl(name, r, h, P(*at), m, verts=verts, cap=cap)
def ringY(name, R, r, at, m, segs=48, minor=8):
    bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=r, location=P(*at), major_segments=segs, minor_segments=minor)
    o = bpy.context.active_object; o.name = name; o.data.materials.append(m); box_uv(o); smooth(o, 60); return o
def uv2(o, tu, tv):
    """box projection with separate horizontal / vertical tile sizes (meters)"""
    me = o.data
    if not me.uv_layers: me.uv_layers.new()
    uv = me.uv_layers.active.data; mw = o.matrix_world
    for p in me.polygons:
        n = p.normal; ax = max(range(3), key=lambda i: abs(n[i]))
        for li in p.loop_indices:
            v = mw @ me.vertices[me.loops[li].vertex_index].co
            if ax == 0: uv[li].uv = (v.y / tu, v.z / tv)
            elif ax == 1: uv[li].uv = (v.x / tu, v.z / tv)
            else: uv[li].uv = (v.x / tu, v.y / tu)
def stone(name, size, loc, m, bevel=0.02):
    o = part(name, size, loc, m, bevel); uv2(o, 2.4, 1.2); return o
def column_uv(o, r):
    me = o.data; uv = me.uv_layers.active.data
    for p in me.polygons:
        for li in p.loop_indices:
            v = me.vertices[me.loops[li].vertex_index].co
            uv[li].uv = (math.atan2(v.y, v.x) / (2 * math.pi) + 0.5, v.z / 4.0)
def export(name):
    join_all(name)
    try: bpy.ops.export_scene.gltf(filepath=OUT + name + '.glb', export_format='GLB', export_apply=True, export_yup=True, export_vertex_color='NONE')
    except TypeError: bpy.ops.export_scene.gltf(filepath=OUT + name + '.glb', export_format='GLB', export_apply=True, export_yup=True)
    print('exported', name)

def mats():
    return dict(
        STONE=mat('bankstone', (1, 1, 1), 'bankstone.jpg', 0.75),
        GRAN=mat('granite', (1, 1, 1), 'granite.jpg', 0.5),
        FLOOR=mat('marblefloor', (1, 1, 1), 'marblefloor.jpg', 0.2),
        FLUTE=mat('flutes', (1, 1, 1), 'flutes.jpg', 0.55),
        COPPER=mat('copper', (1, 1, 1), 'copper.jpg', 0.5, 0.3),
        GOLD=mat('gold', srgb('#d9a33a'), 'gold.jpg', 0.3, 0.6),
        BRONZE=mat('bronze', srgb('#7a5a2a'), 'gold.jpg', 0.4, 0.6),
        WOOD=mat('woodpolish', srgb('#5a3418'), 'teak.jpg', 0.45),
        GLASS=mat('glass', srgb('#1d3a4a'), None, 0.05, 0.4),
        WARM=mat('warmglass', srgb('#ffd9a0'), None, 0.2, emit=srgb('#ffcf80'), emit_k=0.8),
        STEEL=mat('steel', srgb('#a9b0b6'), 'metal.jpg' if False else None, 0.25, 0.85),
        DARK=mat('dark', srgb('#15161a'), None, 0.5),
        BULB=mat('bulb', srgb('#ffe2a0'), None, 0.2, emit=srgb('#ffd27a'), emit_k=1.8),
        VELVET=mat('velvet', srgb('#8a1020'), None, 0.8),
        COFFER=mat('coffer', (1, 1, 1), 'coffer.jpg', 0.6),
        ATM=mat('atm', (1, 1, 1), 'atm.jpg', 0.3, emit=True, emit_k=0.7),
        TELLER=mat('teller', (1, 1, 1), 'teller.jpg', 0.3, emit=True, emit_k=0.4))

def flat_uv(o, w, h, cx, cy, flip=False):
    me = o.data; uv = me.uv_layers.active.data; mw = o.matrix_world
    for p in me.polygons:
        for li in p.loop_indices:
            v = mw @ me.vertices[me.loops[li].vertex_index].co
            u = (v.x - cx) / w; uv[li].uv = ((-u if flip else u) + 0.5, (v.z - cy) / h + 0.5)

def column(name, x, z, y0, y1, r, m):
    h = y1 - y0
    part(name + 'base', (r * 2.6, 0.35, r * 2.6), (x, y0 + 0.175, z), m['STONE'], 0.04)
    ringY(name + 'torus', r * 1.1, 0.1, (x, y0 + 0.42, z), m['STONE'], 24, 6)
    o = cylY(name + 'shaft', r, h - 1.0, (x, y0 + 0.35 + (h - 1.0) / 2, z), m['FLUTE'], 24, cap=False); column_uv(o, r)
    ringY(name + 'neck', r * 1.05, 0.08, (x, y1 - 0.62, z), m['GOLD'], 24, 6)
    bpy.ops.mesh.primitive_cone_add(radius1=r * 1.0, radius2=r * 1.45, depth=0.35, location=P(x, y1 - 0.42, z), vertices=24)
    c = bpy.context.active_object; c.data.materials.append(m['STONE']); box_uv(c)
    part(name + 'abacus', (r * 3.0, 0.25, r * 3.0), (x, y1 - 0.12, z), m['STONE'], 0.03)

def bank():
    reset(); bb._mats.clear(); m = mats()
    BX, BZ, H, T = 13.0, 12.0, 12.0, 0.8
    # walls (doorways 6 m wide x 5 m tall, centred north and south)
    for s in (-1, 1):
        stone(f'wallX{s}', (T, H, 2 * BZ), (s * (BX - T / 2), H / 2, 0), m['STONE'])
        zz = s * (BZ - T / 2)
        for xs in (-1, 1): stone(f'wallZ{s}{xs}', (BX - 3, H, T), (xs * (3 + (BX - 3) / 2), H / 2, zz), m['STONE'])
        stone(f'lintel{s}', (6, H - 5, T), (0, 5 + (H - 5) / 2, zz), m['STONE'])
        # bronze door surround and two leaves swung open inward
        part(f'doorframeT{s}', (6.4, 0.35, T + 0.2), (0, 5.15, zz), m['BRONZE'], 0.04)
        for xs in (-1, 1):
            part(f'doorframe{s}{xs}', (0.3, 5.0, T + 0.2), (xs * 3.05, 2.5, zz), m['BRONZE'], 0.04)
            hx, hz = xs * 2.9, zz - s * 0.45
            ang = math.radians(100) * xs * -s
            leaf = part(f'leaf{s}{xs}', (1.45, 4.8, 0.12), (hx - xs * 0.72, 2.45, hz), m['BRONZE'], 0.02)
            leaf.rotation_euler = (0, 0, 0)
            bpy.context.view_layer.objects.active = leaf
            # rotate the leaf about its hinge (vertical axis through (hx, hz))
            import mathutils
            R = mathutils.Matrix.Translation(P(hx, 0, hz)) @ mathutils.Matrix.Rotation(ang, 4, 'Z') @ mathutils.Matrix.Translation([-c for c in P(hx, 0, hz)])
            leaf.data.transform(R)
            for k in range(3): part(f'panel{s}{xs}{k}', (1.1, 1.2, 0.04), (0, 0, 0), m['GOLD'], 0.01)
            for k in range(3):
                pn = bpy.data.objects[f'panel{s}{xs}{k}']
                pn.data.transform(__import__('mathutils').Matrix.Translation(P(hx - xs * 0.72, 1.0 + k * 1.5, hz - s * 0.08)))
                pn.data.transform(R)
    # granite plinth band outside, cornice with dentils, attic, roof
    for s in (-1, 1):
        part(f'plinthX{s}', (0.3, 1.0, 2 * BZ + 0.6), (s * (BX + 0.15), 0.5, 0), m['GRAN'], 0.02)
        for xs in (-1, 1): part(f'plinthZ{s}{xs}', (BX - 3 + 0.3, 1.0, 0.3), (xs * (3 + (BX - 3) / 2 + 0.15), 0.5, s * (BZ + 0.15)), m['GRAN'], 0.02)
    part('cornice', (2 * BX + 1.2, 0.6, 2 * BZ + 1.2), (0, H - 0.3, 0), m['STONE'], 0.08, 3)
    part('cornice-cap', (2 * BX + 1.5, 0.25, 2 * BZ + 1.5), (0, H + 0.1, 0), m['STONE'], 0.04)
    for s in (-1, 1):
        for k in range(int(2 * BX / 0.6)):
            x = -BX + 0.3 + k * 0.6
            part(f'dentN{s}{k}', (0.3, 0.3, 0.3), (x, H - 0.75, s * (BZ + 0.45)), m['STONE'], 0.0)
        for k in range(int(2 * BZ / 0.6)):
            z = -BZ + 0.3 + k * 0.6
            part(f'dentE{s}{k}', (0.3, 0.3, 0.3), (s * (BX + 0.45), H - 0.75, z), m['STONE'], 0.0)
    stone('attic', (2 * BX - 1.0, 0.9, 2 * BZ - 1.0), (0, H + 0.65, 0), m['STONE'])
    part('roof', (2 * BX - 1.4, 0.2, 2 * BZ - 1.4), (0, H + 1.15, 0), m['GRAN'], 0.0)
    # dome: drum with windows, copper dome, lantern, gold finial
    cylY('drum', 6.4, 1.8, (0, H + 2.1, 0), m['STONE'], 48)
    for k in range(16):
        a = k * 2 * math.pi / 16
        part(f'drumwin{k}', (0.7, 1.0, 0.1), (math.cos(a) * 6.42, H + 2.1, math.sin(a) * 6.42), m['WARM'], 0.0, rot=(0, 0, -a + math.pi / 2))
    ringY('drum-cap', 6.5, 0.18, (0, H + 3.0, 0), m['STONE'], 64, 8)
    ball('dome', 6.3, (0, H + 3.0, 0), m['COPPER'], 40, 20, scale=(1, 1, 0.62))
    cylY('lantern', 0.9, 1.6, (0, H + 3.0 + 3.9 + 0.8, 0), m['STONE'], 16)
    for k in range(8):
        a = k * math.pi / 4
        part(f'lanwin{k}', (0.35, 0.9, 0.06), (math.cos(a) * 0.92, H + 7.7, math.sin(a) * 0.92), m['WARM'], 0.0, rot=(0, 0, -a + math.pi / 2))
    ball('lantern-dome', 1.0, (0, H + 8.5, 0), m['COPPER'], 20, 10, scale=(1, 1, 0.7))
    ball('finial', 0.32, (0, H + 9.4, 0), m['GOLD'], 14, 8)
    # tall arched windows on the east and west walls, pilasters between
    for s in (-1, 1):
        for k, z in enumerate((-7.0, 0.0, 7.0)):
            for face, off in (('o', 0.42), ('i', -0.42)):
                xx = s * (BX - T / 2 + off)
                part(f'win{s}{k}{face}', (0.06, 5.2, 2.2), (xx, 5.6, z), m['GLASS'], 0.0)
                bpy.ops.mesh.primitive_cylinder_add(radius=1.1, depth=0.06, location=P(xx, 8.2, z), rotation=(0, math.radians(90), 0), vertices=24)
                o = bpy.context.active_object; o.data.materials.append(m['GLASS']); box_uv(o)
            for zz in (-1.25, 1.25): part(f'wf{s}{k}{zz}', (0.25, 5.4, 0.25), (s * (BX + 0.05), 5.6, z + zz), m['STONE'], 0.03)
            part(f'sill{s}{k}', (0.5, 0.25, 2.8), (s * (BX + 0.1), 2.95, z), m['STONE'], 0.03)
            part(f'key{s}{k}', (0.4, 0.8, 0.5), (s * (BX + 0.1), 9.5, z), m['STONE'], 0.04)
            for g in range(5): part(f'grille{s}{k}{g}', (0.05, 5.2, 0.05), (s * (BX + 0.05), 5.6, z - 0.9 + g * 0.45), m['BRONZE'], 0.0)
        for z in (-10.5, -3.5, 3.5, 10.5): part(f'pil{s}{z}', (0.35, H - 1.6, 0.9), (s * (BX + 0.17), 0.8 + (H - 1.6) / 2, z), m['STONE'], 0.03)
    # NORTH FRONT: stylobate + steps, four giant columns, entablature (sign sits on the frieze in code), pediment with a gold medallion
    part('stylobate', (22.0, 0.6, 3.6), (0, 0.3, -BZ - 1.8), m['GRAN'], 0.03)
    for k in range(2): part(f'step{k}', (16.0, 0.3, 0.6), (0, 0.15 + k * 0.15 - 0.15, -BZ - 3.6 - 0.3 - k * 0.0), m['GRAN'], 0.02)
    part('step-low', (16.0, 0.3, 0.7), (0, 0.15, -BZ - 3.95), m['GRAN'], 0.02)
    for x in (-8.8, -4.6, 4.6, 8.8): column(f'col{x}', x, -BZ - 2.0, 0.6, 10.4, 0.6, m)
    stone('architrave', (22.6, 0.6, 3.2), (0, 10.7, -BZ - 1.6), m['STONE'])
    stone('frieze', (22.6, 1.3, 2.9), (0, 11.65, -BZ - 1.45), m['STONE'])
    part('pcornice', (23.2, 0.4, 3.6), (0, 12.5, -BZ - 1.8), m['STONE'], 0.06, 3)
    # pediment: triangular prism
    bm = bmesh.new()
    zf, zb = -BZ - 3.4, -BZ - 0.2
    pts = [(-11.4, 12.7), (11.4, 12.7), (0, 15.6)]
    vf = [bm.verts.new(P(x, y, zf)) for x, y in pts]; vb = [bm.verts.new(P(x, y, zb)) for x, y in pts]
    bm.faces.new(vf); bm.faces.new(list(reversed(vb)))
    for i in range(3): bm.faces.new([vf[i], vf[(i + 1) % 3], vb[(i + 1) % 3], vb[i]])
    me = bpy.data.meshes.new('pediment'); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new('pediment', me); bpy.context.scene.collection.objects.link(o); o.data.materials.append(m['STONE']); uv2(o, 2.4, 1.2)
    for s in (-1, 1): tubeM(f'rake{s}', (s * 11.6, 12.65, zf - 0.15), (0, 15.75, zf - 0.15), 0.22, m['STONE'], 8)
    bpy.ops.mesh.primitive_cylinder_add(radius=1.0, depth=0.25, location=P(0, 13.85, zf - 0.1), rotation=(math.radians(90), 0, 0), vertices=32)
    o = bpy.context.active_object; o.data.materials.append(m['GOLD']); box_uv(o)
    bpy.ops.mesh.primitive_torus_add(major_radius=1.15, minor_radius=0.1, location=P(0, 13.85, zf - 0.2), rotation=(math.radians(90), 0, 0), major_segments=32, minor_segments=6)
    o = bpy.context.active_object; o.data.materials.append(m['GOLD']); box_uv(o)
    # south: steps under the big screen door, corner columns
    part('south-steps', (14.0, 0.3, 3.0), (0, 0.15, BZ + 1.5), m['GRAN'], 0.02)
    for x in (-12.2, -10.2, 10.2, 12.2): column(f'scol{x}', x, BZ + 1.6, 0.0, H - 0.6, 0.5, m)
    # ATMs on the front corners, bronze lamp posts by the steps
    for s in (-1, 1):
        part(f'atm{s}', (0.9, 2.0, 0.6), (s * 10.8, 1.6, -BZ - 3.1), m['DARK'], 0.05, 3)
        o = part(f'atmscreen{s}', (0.7, 0.52, 0.02), (s * 10.8, 2.05, -BZ - 3.41), m['ATM'], 0.0); flat_uv(o, 0.7, 0.52, s * 10.8, 2.05, flip=True)
        part(f'atmhood{s}', (1.0, 0.12, 0.3), (s * 10.8, 2.55, -BZ - 3.5), m['GOLD'], 0.02)
        tubeM(f'lamp{s}', (s * 7.2, 0.6, -BZ - 3.4), (s * 7.2, 4.2, -BZ - 3.4), 0.08, m['BRONZE'], 10)
        ball(f'lampglobe{s}', 0.35, (s * 7.2, 4.5, -BZ - 3.4), m['BULB'], 14, 8)
    # INTERIOR: marble floor, wainscot, coffered ceiling, teller counters, chandeliers, velvet ropes
    o = part('floor', (2 * BX - 1.6, 0.16, 2 * BZ - 1.6), (0, 0.08, 0), m['FLOOR'], 0.0)
    me = o.data; uv = me.uv_layers.active.data
    for p in me.polygons:
        for li in p.loop_indices:
            v = me.vertices[me.loops[li].vertex_index].co; uv[li].uv = (v.x / 2.0, v.y / 2.0)
    for s in (-1, 1):
        part(f'wainX{s}', (0.06, 1.4, 2 * BZ - 1.6), (s * (BX - T - 0.03), 0.86, 0), m['WOOD'], 0.0)
    part('ceiling', (2 * BX - 1.6, 0.1, 2 * BZ - 1.6), (0, H - 0.65, 0), m['COFFER'], 0.0, tile=3.0)
    for s in (-1, 1):
        x = s * 9.0
        part(f'counter{s}', (1.1, 1.15, 13.0), (x, 0.73, 0), m['WOOD'], 0.04, 3)
        part(f'countertop{s}', (1.3, 0.08, 13.2), (x, 1.34, 0), m['FLOOR'], 0.02)
        for k in range(9): tubeM(f'bar{s}{k}', (x - s * 0.3, 1.38, -6.0 + k * 1.5), (x - s * 0.3, 2.6, -6.0 + k * 1.5), 0.035, m['GOLD'], 8)
        part(f'barrail{s}', (0.08, 0.08, 12.2), (x - s * 0.3, 2.62, 0), m['GOLD'], 0.01)
        o = part(f'teller{s}', (0.04, 0.5, 2.0), (x - s * 0.62, 3.0, 0), m['TELLER'], 0.0)
        me = o.data; uv = me.uv_layers.active.data
        for p in me.polygons:
            for li in p.loop_indices:
                v = me.vertices[me.loops[li].vertex_index].co
                u = (v.y - 0) / 2.0; uv[li].uv = ((-u if s > 0 else u) + 0.5, (v.z - 3.0) / 0.5 + 0.5)
        for k in range(4): ball(f'lampc{s}{k}', 0.12, (x, 1.6, -4.5 + k * 3), m['BULB'], 10, 6)
    for z in (-6.5, 6.5):
        tubeM(f'chain{z}', (0, H - 0.7, z), (0, 8.6, z), 0.03, m['GOLD'], 6)
        ringY(f'chand{z}', 1.2, 0.06, (0, 8.4, z), m['GOLD'], 32, 6)
        ringY(f'chand2{z}', 0.7, 0.05, (0, 8.9, z), m['GOLD'], 24, 6)
        for k in range(10):
            a = k * 2 * math.pi / 10; ball(f'cb{z}{k}', 0.11, (math.cos(a) * 1.2, 8.55, z + math.sin(a) * 1.2), m['BULB'])
        for k in range(6):
            a = k * 2 * math.pi / 6; ball(f'cb2{z}{k}', 0.09, (math.cos(a) * 0.7, 9.03, z + math.sin(a) * 0.7), m['BULB'])
    for s in (-1, 1):   # velvet rope queue inside the north door
        for k in range(4):
            x = s * (1.4 + k * 1.3)
            cylY(f'stan{s}{k}', 0.05, 1.0, (x, 0.66, -8.6), m['GOLD'], 10); ball(f'stanb{s}{k}', 0.08, (x, 1.18, -8.6), m['GOLD'])
            if k < 3: tubeM(f'rope{s}{k}', (x, 1.0, -8.6), (s * (1.4 + (k + 1) * 1.3), 1.0, -8.6), 0.035, m['VELVET'], 6)
    export('bank')

def money_bag_parts(m, x, y, z, s=1.0, name='mb'):
    """a squat burlap sack: wide round body, short pinched neck tied with gold rope, ruffled top"""
    bb.sphere(name + 'body', 0.34 * s, P(x, y + 0.3 * s, z), m['SACK'], scale=(1.12, 1.0, 0.92), seg=18, rings=12)
    o = bpy.context.active_object; me = o.data
    for v in me.vertices:                       # flatten the bottom so it sits on the floor, and sag the shoulders
        if v.co.z < y + 0.08 * s: v.co.z = y + 0.06 * s + (v.co.z - (y + 0.08 * s)) * 0.15
    if not me.uv_layers: me.uv_layers.new()
    uv = me.uv_layers.active.data
    for p in me.polygons:
        for li in p.loop_indices:
            v = me.vertices[me.loops[li].vertex_index].co
            uv[li].uv = (math.atan2(v.x - x, -(v.y + z)) / (2 * math.pi) + 0.5, (v.z - y) / (0.64 * s))
    cylY(name + 'neck', 0.075 * s, 0.1 * s, (x, y + 0.63 * s, z), m['SACK'], 12)
    bpy.ops.mesh.primitive_cone_add(radius1=0.06 * s, radius2=0.2 * s, depth=0.15 * s, location=P(x, y + 0.74 * s, z), vertices=10)
    c = bpy.context.active_object; c.data.materials.append(m['SACK']); box_uv(c, 0.5)
    ringY(name + 'rope', 0.085 * s, 0.025 * s, (x, y + 0.64 * s, z), m['GOLD'], 16, 6)

def money_bag():
    reset(); bb._mats.clear(); m = mats(); m['SACK'] = mat('moneybag', (1, 1, 1), 'moneybag.jpg', 0.85)
    money_bag_parts(m, 0, 0, 0)
    export('money-bag')

def vault():
    """origin at the vault centre on the floor; doorways face north (-z) and south (+z)"""
    reset(); bb._mats.clear(); m = mats(); m['SACK'] = mat('moneybag', (1, 1, 1), 'moneybag.jpg', 0.85)
    R, Hh = 3.2, 4.6
    bpy.ops.mesh.primitive_cylinder_add(radius=R, depth=Hh, location=P(0, Hh / 2, 0), vertices=48)
    drum = bpy.context.active_object; drum.data.materials.append(m['STEEL'])
    bpy.ops.mesh.primitive_cylinder_add(radius=R - 0.45, depth=Hh - 0.5, location=P(0, Hh / 2 + 0.05, 0), vertices=48)
    inner = bpy.context.active_object
    for o2 in (inner,):
        mod = drum.modifiers.new('hollow', 'BOOLEAN'); mod.operation = 'DIFFERENCE'; mod.object = o2
        try: mod.solver = 'EXACT'
        except Exception: pass
        bpy.context.view_layer.objects.active = drum; bpy.ops.object.modifier_apply(modifier='hollow')
    bpy.data.objects.remove(inner)
    for s in (-1, 1):   # doorways
        bpy.ops.mesh.primitive_cube_add(size=1, location=P(0, 1.6, s * R))
        c = bpy.context.active_object; c.scale = S(2.3, 3.0, 1.6); bpy.ops.object.transform_apply(scale=True)
        mod = drum.modifiers.new('door', 'BOOLEAN'); mod.operation = 'DIFFERENCE'; mod.object = c
        try: mod.solver = 'EXACT'
        except Exception: pass
        bpy.context.view_layer.objects.active = drum; bpy.ops.object.modifier_apply(modifier='door'); bpy.data.objects.remove(c)
    box_uv(drum, 1.0); smooth(drum, 30)
    for y in (0.3, 2.3, 4.3): ringY(f'band{y}', R + 0.02, 0.08, (0, y, 0), m['STEEL'], 64, 6)
    for k in range(32):
        a = k * 2 * math.pi / 32
        for y in (0.45, 4.15):
            if abs(math.cos(a)) < 0.37 and y < 3: continue
            ball(f'rivet{k}{y}', 0.06, (math.sin(a) * (R + 0.04), y, math.cos(a) * (R + 0.04)), m['STEEL'], 6, 4)
    ringY('topring', R + 0.05, 0.12, (0, Hh, 0), m['GOLD'], 64, 6)
    # the two big round doors, swung open beside each doorway
    for s in (-1, 1):
        hx, hz = 1.3, s * (R + 0.15)
        door = []
        bpy.ops.mesh.primitive_cylinder_add(radius=1.55, depth=0.55, location=P(0, 1.65, 0), rotation=(math.radians(90), 0, 0), vertices=40)
        d = bpy.context.active_object; d.data.materials.append(m['STEEL']); box_uv(d); smooth(d, 30); door.append(d)
        for r_, w_ in ((1.2, 0.06), (0.8, 0.05)):
            bpy.ops.mesh.primitive_torus_add(major_radius=r_, minor_radius=w_, location=P(0, 1.65, -0.29), rotation=(math.radians(90), 0, 0), major_segments=40, minor_segments=6)
            t = bpy.context.active_object; t.data.materials.append(m['GOLD']); box_uv(t); door.append(t)
        for k in range(12):
            a = k * 2 * math.pi / 12
            bpy.ops.mesh.primitive_cylinder_add(radius=0.09, depth=0.5, location=P(math.cos(a) * 1.55, 1.65 + math.sin(a) * 1.55, 0), rotation=(0, math.radians(90), a), vertices=10)
            b = bpy.context.active_object; b.data.materials.append(m['STEEL']); box_uv(b); door.append(b)
        bpy.ops.mesh.primitive_torus_add(major_radius=0.45, minor_radius=0.05, location=P(0, 1.65, -0.5), rotation=(math.radians(90), 0, 0), major_segments=24, minor_segments=6)
        w = bpy.context.active_object; w.data.materials.append(m['GOLD']); box_uv(w); door.append(w)
        for k in range(4):
            a = k * math.pi / 2 + math.pi / 4
            door.append(tubeM(f'spoke{s}{k}', (0, 1.65, -0.5), (math.cos(a) * 0.45, 1.65 + math.sin(a) * 0.45, -0.5), 0.035, m['GOLD'], 6))
        door.append(tubeM(f'hub{s}', (0, 1.65, -0.25), (0, 1.65, -0.55), 0.09, m['GOLD'], 10))
        import mathutils
        # door face points away from the vault (+s), centred on the doorway, then swung open about the hinge at x = +1.3
        flip = mathutils.Matrix.Rotation(math.radians(180) if s > 0 else 0, 4, 'Z')
        M = (mathutils.Matrix.Translation(P(hx, 0, hz)) @ mathutils.Matrix.Rotation(math.radians(105) * s, 4, 'Z') @ mathutils.Matrix.Translation([-c for c in P(hx, 0, hz)])
             @ mathutils.Matrix.Translation(P(0, 0, hz)) @ flip)
        for o in door:
            bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); bpy.context.view_layer.objects.active = o
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
            o.data.transform(M)
        # hinge pins
        cylY(f'hinge{s}', 0.12, 2.6, (hx, 1.65, hz), m['GOLD'], 12)
    # floor, shelves with money bags and gold bars between the doorways
    cylY('vfloor', R - 0.45, 0.1, (0, 0.05, 0), m['FLOOR'], 40)
    gold_bar = m['GOLD']
    for side in (-1, 1):
        for lvl, y in enumerate((0.0, 1.15, 2.3)):
            bpy.ops.mesh.primitive_cylinder_add(radius=R - 0.5, depth=0.06, location=P(0, y + 0.08, 0), vertices=40)
            sh = bpy.context.active_object; sh.data.materials.append(m['WOOD']); box_uv(sh)
            # keep only the shelf arc on this side (x * side > 1.2)
            bm = bmesh.new(); bm.from_mesh(sh.data)
            bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.x * side < 1.0], context='VERTS')
            bm.to_mesh(sh.data); bm.free()
            for k in range(5):
                a = math.radians(-50 + k * 25)
                x, z = side * math.cos(a) * (R - 0.95), math.sin(a) * (R - 0.95)
                if (lvl + k) % 3 == 2:
                    for gy in range(3):
                        for gx in range(2): part(f'bar{side}{lvl}{k}{gy}{gx}', (0.32, 0.1, 0.16), (x + (gx - 0.5) * 0.17, y + 0.16 + gy * 0.1, z), gold_bar, 0.015)
                else:
                    money_bag_parts(m, x, y + 0.11, z, 0.75, name=f'mb{side}{lvl}{k}')
    o = part('plate', (1.4, 0.4, 0.05), (0, 3.6, -R - 0.03), m['GOLD'], 0.01)
    export('bank-vault')

bank(); money_bag(); vault()

# Lucky Wheel bet kiosks (CC0): wood plinth, gold posts, lit sign face with the symbol art, bulb crest.
# MML axes: x right, y up, z toward the player. Sign face is 2.9 x 2.0 m, centred at y 1.45, front at z 0.1.
import bpy, math, sys
sys.path.insert(0, '/home/claude/bscripts')
import boats_build as bb
from boats_build import reset, mat, srgb, box_uv, smooth, join_all, OUT
def B(x, y, z): return (x, -z, y)
def S(w, h, d): return (w, d, h)
def part(name, size, loc, m, bevel=0.03, seg=2, rot=(0, 0, 0), tile=1.0):
    return bb.rbox(name, S(*size), B(*loc), m, bevel, seg, rot, tile)

def kiosk(sym):
    reset(); bb._mats.clear()
    WOOD = mat('woodpolish', srgb('#4a2a18'), 'teak.jpg', 0.45)
    GOLD = mat('gold', srgb('#d9a33a'), 'gold.jpg', 0.3, 0.45)
    DK = mat('dark', srgb('#140c16'), None, 0.5)
    FACE = mat('bet-' + sym, (1, 1, 1), 'bet-' + sym + '.jpg', 0.35, emit=True, emit_k=0.85)
    BULB = mat('bulb', srgb('#ffe2a0'), None, 0.2, emit=srgb('#ffd27a'), emit_k=1.6)
    # plinth with gold kick strip and a step
    part('plinth', (3.3, 0.3, 1.0), (0, 0.15, -0.15), WOOD, 0.04, 2)
    part('kick', (3.34, 0.05, 1.04), (0, 0.29, -0.15), GOLD, 0.01)
    part('step', (2.6, 0.12, 0.35), (0, 0.06, 0.48), WOOD, 0.03, 2)
    # back cabinet and the sign face
    part('cabinet', (3.1, 2.2, 0.22), (0, 1.45, -0.04), DK, 0.05, 3)
    face = part('face', (2.9, 2.0, 0.02), (0, 1.45, 0.085), FACE, 0.0)
    me = face.data; uv = me.uv_layers.active.data; mw = face.matrix_world
    for p in me.polygons:
        for li in p.loop_indices:
            v = mw @ me.vertices[me.loops[li].vertex_index].co    # world Blender coords: x, -z, y
            uv[li].uv = (v.x / 2.9 + 0.5, (v.z - 1.45) / 2.0 + 0.5)
    # gold frame bars around the face
    part('frame-t', (3.16, 0.1, 0.12), (0, 2.5, 0.06), GOLD, 0.03); part('frame-b', (3.16, 0.1, 0.12), (0, 0.4, 0.06), GOLD, 0.03)
    for s in (-1, 1):
        part(f'frame{s}', (0.1, 2.2, 0.12), (s * 1.53, 1.45, 0.06), GOLD, 0.03)
        bb.cyl(f'post{s}', 0.07, 2.75, B(s * 1.62, 1.6, -0.12), GOLD, verts=16)
        bb.sphere(f'finial{s}', 0.13, B(s * 1.62, 3.02, -0.12), GOLD, seg=14, rings=8)
    # arched crest with bulbs
    bpy.ops.mesh.primitive_cylinder_add(radius=1.0, depth=0.14, location=B(0, 2.55, -0.04), rotation=(math.radians(90), 0, 0), vertices=48)
    crest = bpy.context.active_object; crest.name = 'crest'
    import bmesh
    bm = bmesh.new(); bm.from_mesh(crest.data)
    bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=(0, 0, 2.56), plane_no=(0, 0, -1), clear_inner=True)
    bmesh.ops.contextual_create(bm, geom=[e for e in bm.edges if e.is_boundary])
    bm.to_mesh(crest.data); bm.free()
    crest.data.materials.append(DK); box_uv(crest); crest.scale = (1.0, 1.0, 0.55); bpy.ops.object.transform_apply(scale=True)
    bpy.ops.mesh.primitive_torus_add(major_radius=1.0, minor_radius=0.05, location=B(0, 2.55, 0.04), rotation=(math.radians(90), 0, 0), major_segments=48, minor_segments=8)
    rim = bpy.context.active_object; rim.name = 'crest-rim'
    bm = bmesh.new(); bm.from_mesh(rim.data)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if (rim.matrix_world @ v.co).z < 2.53], context='VERTS')
    bm.to_mesh(rim.data); bm.free(); rim.scale = (1.0, 1.0, 0.55); bpy.ops.object.transform_apply(scale=True)
    rim.data.materials.append(GOLD); box_uv(rim); smooth(rim, 60)
    for k in range(11):
        a = math.radians(10 + k * 16)
        bb.sphere(f'cb{k}', 0.05, B(math.cos(a) * 0.86, 2.55 + math.sin(a) * 0.86 * 0.55, 0.06), BULB, seg=8, rings=5)
    for k in range(13):
        bb.sphere(f'tb{k}', 0.04, B(-1.44 + k * 0.24, 2.5, 0.13), BULB, seg=8, rings=5)
    join_all('bet-' + sym)
    try: bpy.ops.export_scene.gltf(filepath=OUT + 'bet-' + sym + '.glb', export_format='GLB', export_apply=True, export_yup=True, export_vertex_color='NONE')
    except TypeError: bpy.ops.export_scene.gltf(filepath=OUT + 'bet-' + sym + '.glb', export_format='GLB', export_apply=True, export_yup=True)
    print('exported bet-' + sym)

for s in ('crown', 'gator', 'frog', 'skull'): kiosk(s)

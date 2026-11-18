# Team markers that float over each checked-in player (CC0, original): a gator, a heron, a bullfrog and a
# cottonmouth snake, each in its crew color with a soft glow, standing on a thin glowing halo ring.
# MML axes: x right, y up, z toward the viewer. Each figure is about 0.75 m tall, base at y = 0, facing +z.
import bpy, math, sys
sys.path.insert(0, '/home/claude/bscripts')
import boats_build as bb
from boats_build import reset, mat, srgb, smooth, join_all, OUT
def B(x, y, z): return (x, -z, y)
def S(w, h, d): return (w, d, h)
def ball(n, r, loc, m, sc=(1, 1, 1), seg=20, rings=12): return bb.sphere(n, r, B(*loc), m, scale=(sc[0], sc[2], sc[1]), seg=seg, rings=rings)
def stick(n, a, b, r, m, v=10): return bb.tube(n, B(*a), B(*b), r, m, verts=v)

def mats(col, belly, acc):
    c = srgb(col)
    return dict(
        body=mat('body', c, None, 0.45, emit=c, emit_k=0.45),
        belly=mat('belly', srgb(belly), None, 0.5, emit=srgb(belly), emit_k=0.25),
        acc=mat('acc', srgb(acc), None, 0.4, emit=srgb(acc), emit_k=0.3),
        eye=mat('eye', srgb('#ffffff'), None, 0.2, emit=srgb('#ffffff'), emit_k=0.35),
        pupil=mat('pupil', srgb('#101010'), None, 0.3),
        halo=mat('halo', c, None, 0.3, emit=c, emit_k=1.4),
    )

def halo(M):
    bpy.ops.mesh.primitive_torus_add(major_radius=0.3, minor_radius=0.022, location=B(0, 0.02, 0), rotation=(0, 0, 0), major_segments=40, minor_segments=8)
    o = bpy.context.active_object; o.name = 'halo'; o.data.materials.append(M['halo']); bb.box_uv(o); smooth(o, 60)

def eyes(M, x, y, z, r=0.07, look=(0, 0, 1)):
    for s in (-1, 1):
        ball(f'eye{s}', r, (s * x, y, z), M['eye'])
        ball(f'pup{s}', r * 0.5, (s * x + look[0] * r * 0.15, y + 0.005, z + r * 0.62), M['pupil'])

def finish(name):
    join_all(name)
    bb.export_safe(name)

def gator():
    reset(); bb._mats.clear(); M = mats('#4fe08f', '#d9f7a8', '#f6f0d8'); halo(M)
    ball('body', 0.2, (0, 0.2, -0.02), M['body'], (1.05, 0.62, 1.45))
    ball('belly', 0.18, (0, 0.15, 0.0), M['belly'], (0.95, 0.45, 1.3))
    ball('head', 0.15, (0, 0.27, 0.27), M['body'], (1.1, 0.75, 1.0))
    bb.rbox('snout', S(0.2, 0.09, 0.26), B(0, 0.25, 0.43), M['body'], 0.04, 3)
    bb.rbox('jaw', S(0.18, 0.05, 0.24), B(0, 0.19, 0.42), M['belly'], 0.02, 2)
    for s in (-1, 1):
        for k in range(4): bb.rbox(f'tooth{s}{k}', S(0.018, 0.035, 0.018), B(s * 0.085, 0.215, 0.33 + k * 0.05), M['acc'], 0.004, 1)
        ball(f'nost{s}', 0.016, (s * 0.04, 0.3, 0.55), M['pupil'])
    eyes(M, 0.065, 0.37, 0.26, 0.06)
    for k in range(5): bb.rbox(f'ridge{k}', S(0.05, 0.05, 0.05), B(0, 0.33 - k * 0.012, 0.12 - k * 0.09), M['body'], 0.015, 2, rot=(0, math.radians(45), 0))
    for k in range(7):   # tail curling to one side
        t = k / 6
        ball(f'tail{k}', 0.1 * (1 - t * 0.7), (0.12 * t * t, 0.17 - t * 0.08, -0.24 - k * 0.055), M['body'], (1, 0.7, 1.3))
    for sx in (-1, 1):
        for sz in (0.13, -0.15):
            ball(f'leg{sx}{sz}', 0.055, (sx * 0.2, 0.08, sz), M['body'], (1.2, 1, 1.1))
    finish('team-gator')

def heron():
    reset(); bb._mats.clear(); M = mats('#3fd0ff', '#eaf8ff', '#ffc23d'); halo(M)
    for s in (-1, 1): stick(f'leg{s}', (s * 0.05, 0.0, 0.0), (s * 0.05, 0.25, -0.02), 0.014, M['acc'], 6)
    ball('body', 0.15, (0, 0.33, -0.04), M['body'], (0.9, 0.85, 1.35))
    ball('chest', 0.11, (0, 0.33, 0.06), M['belly'], (0.85, 0.95, 0.9))
    for s in (-1, 1): ball(f'wing{s}', 0.12, (s * 0.1, 0.35, -0.08), M['body'], (0.35, 0.65, 1.35))
    bb.rbox('tailf', S(0.1, 0.03, 0.12), B(0, 0.36, -0.24), M['body'], 0.012, 2, rot=(math.radians(-20), 0, 0))
    pts = [(0, 0.4, 0.08), (0, 0.5, 0.1), (0, 0.58, 0.05), (0, 0.66, 0.06), (0, 0.72, 0.1)]   # S-curved neck
    for k in range(len(pts) - 1): stick(f'neck{k}', pts[k], pts[k + 1], 0.04 - k * 0.004, M['body'], 10)
    for k, p in enumerate(pts): ball(f'nj{k}', 0.04 - k * 0.004, p, M['body'])
    ball('head', 0.065, (0, 0.75, 0.12), M['body'], (0.9, 0.85, 1.15))
    bpy.ops.mesh.primitive_cone_add(radius1=0.028, radius2=0.002, depth=0.2, vertices=10, location=B(0, 0.745, 0.27), rotation=(math.radians(90), 0, 0))
    o = bpy.context.active_object; o.name = 'beak'; o.rotation_euler = (math.radians(90), 0, 0); o.data.materials.append(M['acc']); bb.box_uv(o)
    # cone points along +z in Blender before rotation; rotate so it points to MML +z (Blender -y)
    o.rotation_euler = (math.radians(90), 0, 0); bpy.ops.object.transform_apply(rotation=True)
    for k in range(2): stick(f'crest{k}', (0, 0.78, 0.08), (0, 0.8 + k * 0.02, -0.06 - k * 0.04), 0.008, M['body'], 6)
    eyes(M, 0.042, 0.77, 0.15, 0.022)
    finish('team-heron')

def frog():
    reset(); bb._mats.clear(); M = mats('#ffc23d', '#fff1c0', '#2b1a10'); halo(M)
    ball('body', 0.24, (0, 0.2, -0.02), M['body'], (1.1, 0.78, 1.0))
    ball('belly', 0.2, (0, 0.17, 0.07), M['belly'], (1.0, 0.72, 0.85))
    for s in (-1, 1):
        ball(f'bump{s}', 0.11, (s * 0.12, 0.38, 0.06), M['body'])
        ball(f'eye{s}', 0.085, (s * 0.12, 0.41, 0.1), M['eye'])
        ball(f'pup{s}', 0.045, (s * 0.12, 0.415, 0.17), M['pupil'], (1, 0.7, 1))
        ball(f'thigh{s}', 0.12, (s * 0.2, 0.1, -0.08), M['body'], (0.8, 0.7, 1.3))
        ball(f'foot{s}', 0.06, (s * 0.24, 0.025, 0.08), M['body'], (1.3, 0.4, 1.4))
        ball(f'arm{s}', 0.05, (s * 0.14, 0.07, 0.2), M['body'], (0.9, 1.4, 0.9))
        ball(f'cheek{s}', 0.035, (s * 0.15, 0.24, 0.2), M['acc'] if False else M['belly'])
    for s in (-1, 1):
        for k in range(3): ball(f'spot{s}{k}', 0.03, (s * (0.1 + k * 0.05), 0.33 - k * 0.04, -0.12 + k * 0.03), M['acc'], (1, 0.4, 1))
    finish('team-frog')

def snake():
    reset(); bb._mats.clear(); M = mats('#c48bff', '#f4e6ff', '#ffffff'); halo(M)
    # coiled body: a helix of overlapping spheres, tapering to the tail on top of the coil
    n = 46
    for k in range(n):
        t = k / (n - 1); a = t * math.pi * 2 * 2.2
        r = 0.2 - t * 0.09; y = 0.07 + t * 0.2
        ball(f'c{k}', 0.07 - t * 0.02, (math.cos(a) * r, y, math.sin(a) * r), M['body'], seg=12, rings=8)
    # neck rising out of the coil and the head, mouth open white (a cottonmouth)
    pts = [(0.0, 0.28, -0.05), (0.0, 0.38, 0.0), (0.0, 0.48, 0.06), (0.0, 0.54, 0.12)]
    for k in range(len(pts) - 1): stick(f'neck{k}', pts[k], pts[k + 1], 0.05, M['body'], 12)
    for k, p in enumerate(pts): ball(f'nj{k}', 0.05, p, M['body'])
    ball('belly', 0.045, (0, 0.44, 0.06), M['belly'], (1, 1.6, 0.7))
    ball('head', 0.08, (0, 0.58, 0.18), M['body'], (1.15, 0.7, 1.35))
    bb.rbox('mouth', S(0.1, 0.025, 0.1), B(0, 0.545, 0.25), M['acc'], 0.01, 2)
    bb.rbox('jaw', S(0.1, 0.03, 0.1), B(0, 0.52, 0.24), M['body'], 0.012, 2, rot=(math.radians(18), 0, 0))
    for s in (-1, 1):
        stick(f'fang{s}', (s * 0.03, 0.56, 0.28), (s * 0.03, 0.525, 0.285), 0.007, M['acc'], 6)
        stick(f'tongue{s}', (0, 0.535, 0.29), (s * 0.03, 0.535, 0.38), 0.006, mat('tongue', srgb('#ff3b5c'), None, 0.4, emit=srgb('#ff3b5c'), emit_k=0.4), 6)
    eyes(M, 0.055, 0.63, 0.19, 0.03)
    finish('team-snake')

gator(); heron(); frog(); snake()

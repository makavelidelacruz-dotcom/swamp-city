# Crew beacons (CC0): a glowing beam of the crew's color, 60 m tall, fading out toward the top. Base at y = 0.
import bpy, math, sys
sys.path.insert(0, '/home/claude/bscripts')
import boats_build as bb
from boats_build import reset, srgb, OUT
TEX = '/home/claude/boats/tex/'
def beam_mat(name, col, k_alpha, k_emit):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']
    t = nt.nodes.new('ShaderNodeTexImage'); t.image = bpy.data.images.load(TEX + 'beamfade.png', check_existing=True)
    c = srgb(col)
    b.inputs['Base Color'].default_value = (*c, 1); b.inputs['Roughness'].default_value = 1.0
    b.inputs['Emission Color'].default_value = (*c, 1); b.inputs['Emission Strength'].default_value = k_emit
    mul = nt.nodes.new('ShaderNodeMath'); mul.operation = 'MULTIPLY'; mul.inputs[1].default_value = k_alpha
    nt.links.new(t.outputs['Alpha'], mul.inputs[0]); nt.links.new(mul.outputs[0], b.inputs['Alpha'])
    try: m.surface_render_method = 'BLENDED'
    except Exception: pass
    try: m.blend_method = 'BLEND'
    except Exception: pass
    m.use_backface_culling = False
    return m
def tube(name, r, m):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=60, location=(0, 0, 30), vertices=24, end_fill_type='NOTHING', calc_uvs=True)
    o = bpy.context.active_object; o.name = name; o.data.materials.append(m)
    # UV v = height: 0 at the base, 1 at the top (the texture is opaque at v=0 after glTF's flip)
    uv = o.data.uv_layers.active.data
    for p in o.data.polygons:
        for li in p.loop_indices:
            z = o.data.vertices[o.data.loops[li].vertex_index].co.z
            uv[li].uv = (uv[li].uv[0], 1 - (z + 30) / 60)
    return o
for team, col in [('gator', '#4fe08f'), ('heron', '#3fd0ff'), ('frog', '#ffc23d'), ('snake', '#c48bff')]:
    reset()
    tube('glow', 2.0, beam_mat('beam-glow', col, 0.38, 1.2))
    tube('core', 0.6, beam_mat('beam-core', col, 0.85, 3.0))
    bpy.ops.object.select_all(action='SELECT'); bpy.context.view_layer.objects.active = bpy.data.objects['glow']; bpy.ops.object.join()
    bb.export_safe('beam-' + team)

"""Shared helpers: scene reset, materials, procedural meshes, textures, keyframes.
Used by every build script in حكايات جدتي (My Grandmother's Tales)."""
import bpy, bmesh, math, os
import numpy as np
from mathutils import Vector, Matrix, Euler

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
TEX_DIR = os.path.join(ROOT, 'shared_assets', 'textures')
os.makedirs(TEX_DIR, exist_ok=True)


def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    for c in (bpy.data.meshes, bpy.data.materials, bpy.data.objects):
        for d in list(c):
            c.remove(d)


def coll(name, parent=None):
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name)
        (parent or bpy.context.scene.collection).children.link(c)
    return c


def link(obj, collection):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    collection.objects.link(obj)
    return obj


# ---------------------------------------------------------------- materials
_MATS = {}


def mat(name, color=(0.8, 0.8, 0.8), rough=0.6, metal=0.0, sheen=0.0, sss=0.0,
        emission=None, estr=0.0, coat=0.0, alpha=1.0, image=None, uv_scale=1.0,
        bump=0.0, transmission=0.0, ior=1.45):
    """Principled material factory (cached by name, so assets share materials)."""
    if name in _MATS and _MATS[name].name in bpy.data.materials:
        return _MATS[name]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    p = nt.nodes['Principled BSDF']
    p.inputs['Base Color'].default_value = (*color[:3], 1)
    p.inputs['Roughness'].default_value = rough
    p.inputs['Metallic'].default_value = metal
    if sheen:
        p.inputs['Sheen Weight'].default_value = sheen
        p.inputs['Sheen Roughness'].default_value = 0.5
    if sss:
        p.inputs['Subsurface Weight'].default_value = sss
        p.inputs['Subsurface Radius'].default_value = (1.0, 0.35, 0.2)
        p.inputs['Subsurface Scale'].default_value = 0.01
    if coat:
        p.inputs['Coat Weight'].default_value = coat
    if transmission:
        p.inputs['Transmission Weight'].default_value = transmission
        p.inputs['IOR'].default_value = ior
    if emission is not None:
        p.inputs['Emission Color'].default_value = (*emission[:3], 1)
        p.inputs['Emission Strength'].default_value = estr
    if alpha < 1:
        p.inputs['Alpha'].default_value = alpha
        m.surface_render_method = 'BLENDED'
    if image:
        tc = nt.nodes.new('ShaderNodeTexCoord')
        mp = nt.nodes.new('ShaderNodeMapping')
        mp.inputs['Scale'].default_value = (uv_scale, uv_scale, uv_scale)
        im = nt.nodes.new('ShaderNodeTexImage')
        im.image = image
        nt.links.new(tc.outputs['UV'], mp.inputs['Vector'])
        nt.links.new(mp.outputs['Vector'], im.inputs['Vector'])
        nt.links.new(im.outputs['Color'], p.inputs['Base Color'])
        if bump:
            b = nt.nodes.new('ShaderNodeBump')
            b.inputs['Strength'].default_value = bump
            nt.links.new(im.outputs['Color'], b.inputs['Height'])
            nt.links.new(b.outputs['Normal'], p.inputs['Normal'])
    elif bump:
        nz = nt.nodes.new('ShaderNodeTexNoise')
        nz.inputs['Scale'].default_value = 60
        nz.inputs['Detail'].default_value = 4
        b = nt.nodes.new('ShaderNodeBump')
        b.inputs['Strength'].default_value = bump
        b.inputs['Distance'].default_value = 0.02
        nt.links.new(nz.outputs['Fac'], b.inputs['Height'])
        nt.links.new(b.outputs['Normal'], p.inputs['Normal'])
    m.diffuse_color = (*color[:3], 1)
    _MATS[name] = m
    return m


def eye_mat(name, iris=(0.12, 0.06, 0.03), radius=1.0):
    """Eyeball: white sclera, brown iris, black pupil, computed from object -Y axis."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    p = nt.nodes['Principled BSDF']
    p.inputs['Roughness'].default_value = 0.08
    p.inputs['Coat Weight'].default_value = 1.0
    tc = nt.nodes.new('ShaderNodeTexCoord')
    sep = nt.nodes.new('ShaderNodeSeparateXYZ')
    nt.links.new(tc.outputs['Object'], sep.inputs['Vector'])
    neg = nt.nodes.new('ShaderNodeMath'); neg.operation = 'MULTIPLY'
    neg.inputs[1].default_value = -1.0 / radius
    nt.links.new(sep.outputs['Y'], neg.inputs[0])
    ramp = nt.nodes.new('ShaderNodeValToRGB')
    cr = ramp.color_ramp
    cr.interpolation = 'EASE'
    cr.elements[0].position = 0.0; cr.elements[0].color = (0.93, 0.92, 0.9, 1)
    cr.elements[1].position = 0.70; cr.elements[1].color = (0.93, 0.92, 0.9, 1)
    for pos, col in ((0.735, (*iris, 1)), (0.86, (iris[0] * 1.6, iris[1] * 1.6, iris[2] * 1.6, 1)),
                     (0.885, (0.01, 0.006, 0.004, 1)), (1.0, (0.0, 0.0, 0.0, 1))):
        e = cr.elements.new(pos); e.color = col
    nt.links.new(neg.outputs[0], ramp.inputs['Fac'])
    nt.links.new(ramp.outputs['Color'], p.inputs['Base Color'])
    return m


def image_from_array(name, arr):
    """arr: HxWx3/4 float 0..1 -> packed bpy image (also saved as png)."""
    h, w = arr.shape[:2]
    if arr.shape[2] == 3:
        arr = np.concatenate([arr, np.ones((h, w, 1))], axis=2)
    img = bpy.data.images.new(name, w, h, alpha=True)
    img.pixels.foreach_set(np.flipud(arr).astype(np.float32).ravel())
    path = os.path.join(TEX_DIR, name + '.png')
    img.filepath_raw = path
    img.file_format = 'PNG'
    img.save()
    img.pack()
    return img


# ---------------------------------------------------------------- meshes
def obj_from_data(name, verts, faces, collection=None, smooth=True):
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(v) for v in verts], [], [tuple(f) for f in faces])
    me.update()
    o = bpy.data.objects.new(name, me)
    (collection or bpy.context.scene.collection).objects.link(o)
    if smooth:
        me.shade_smooth()
    return o


def lathe(name, profile, seg=24, sx=1.0, sy=1.0, cap_top=True, cap_bot=True,
          collection=None, mat_=None, subsurf=1, uv=True, shape=None):
    """Revolve a (radius, z) profile around Z.  shape(theta, z) -> radial multiplier
    lets us sculpt (cheeks, chins, folds).  Returns smooth object."""
    verts, faces = [], []
    n = len(profile)
    for i, (r, z) in enumerate(profile):
        for j in range(seg):
            t = 2 * math.pi * j / seg
            k = shape(t, z) if shape else 1.0
            verts.append((math.sin(t) * r * sx * k, -math.cos(t) * r * sy * k, z))
    for i in range(n - 1):
        for j in range(seg):
            a = i * seg + j; b = i * seg + (j + 1) % seg
            faces.append((a, b, b + seg, a + seg))
    if cap_bot and profile[0][0] > 1e-5:
        verts.append((0, 0, profile[0][1])); c = len(verts) - 1
        for j in range(seg):
            faces.append((c, (j + 1) % seg, j))
    if cap_top and profile[-1][0] > 1e-5:
        verts.append((0, 0, profile[-1][1])); c = len(verts) - 1
        base = (n - 1) * seg
        for j in range(seg):
            faces.append((c, base + j, base + (j + 1) % seg))
    o = obj_from_data(name, verts, faces, collection)
    if uv:
        _cyl_uv(o, seg, n)
    if mat_:
        o.data.materials.append(mat_)
    if subsurf:
        add_subsurf(o, subsurf)
    return o


def _cyl_uv(o, seg, n):
    me = o.data
    uvl = me.uv_layers.new(name='UV')
    for poly in me.polygons:
        for li in poly.loop_indices:
            vi = me.loops[li].vertex_index
            if vi < seg * n:
                i, j = divmod(vi, seg)
                uvl.data[li].uv = (j / seg, i / max(n - 1, 1))
            else:
                uvl.data[li].uv = (0.5, 0.5)
    # fix seam wrap
    for poly in me.polygons:
        us = [uvl.data[li].uv[0] for li in poly.loop_indices]
        if max(us) - min(us) > 0.5:
            for li in poly.loop_indices:
                if uvl.data[li].uv[0] < 0.5:
                    uvl.data[li].uv[0] += 1.0


def sphere(name, r=1.0, loc=(0, 0, 0), scale=(1, 1, 1), seg=24, rings=12,
           collection=None, mat_=None, subsurf=0):
    prof = [(r * math.sin(math.pi * i / rings), -r * math.cos(math.pi * i / rings))
            for i in range(rings + 1)]
    prof[0] = (0.0, -r); prof[-1] = (0.0, r)
    o = lathe(name, prof[1:-1], seg, cap_top=False, cap_bot=False, collection=collection,
              mat_=mat_, subsurf=subsurf)
    # close poles
    me = o.data
    bm = bmesh.new(); bm.from_mesh(me)
    bm.verts.ensure_lookup_table()
    bot = bm.verts.new((0, 0, -r)); top = bm.verts.new((0, 0, r))
    ring0 = bm.verts[0:seg]; ringN = bm.verts[(rings - 2) * seg:(rings - 1) * seg]
    for j in range(seg):
        bm.faces.new((bot, ring0[(j + 1) % seg], ring0[j]))
        bm.faces.new((top, ringN[j], ringN[(j + 1) % seg]))
    for f in bm.faces:
        f.smooth = True
    bm.to_mesh(me); bm.free()
    o.location = loc; o.scale = scale
    return o


def rbox(name, size=(1, 1, 1), loc=(0, 0, 0), bevel=0.05, collection=None, mat_=None,
         segments=3, rot=(0, 0, 0)):
    """Rounded box (bevel modifier, kept live for reuse/editing)."""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co = Vector((v.co.x * size[0], v.co.y * size[1], v.co.z * size[2]))
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me)
    (collection or bpy.context.scene.collection).objects.link(o)
    o.location = loc; o.rotation_euler = rot
    if bevel > 0:
        b = o.modifiers.new('bevel', 'BEVEL')
        b.width = min(bevel, min(size) * 0.49); b.segments = segments
        b.limit_method = 'NONE'
        me.shade_smooth()
        o.modifiers.new('wn', 'WEIGHTED_NORMAL').keep_sharp = True
    if mat_:
        me.materials.append(mat_)
    _box_uv(o)
    return o


def _box_uv(o):
    me = o.data
    uvl = me.uv_layers.new(name='UV')
    for poly in me.polygons:
        n = poly.normal
        ax = max(range(3), key=lambda i: abs(n[i]))
        for li in poly.loop_indices:
            co = me.vertices[me.loops[li].vertex_index].co
            u, v = [(co.y, co.z), (co.x, co.z), (co.x, co.y)][ax]
            uvl.data[li].uv = (u, v)


def cyl(name, r=0.05, h=1.0, loc=(0, 0, 0), rot=(0, 0, 0), seg=16, collection=None,
        mat_=None, r2=None):
    r2 = r if r2 is None else r2
    o = lathe(name, [(r, 0), (r2, h)], seg, collection=collection, mat_=mat_, subsurf=0)
    o.location = loc; o.rotation_euler = rot
    o.data.shade_flat() if seg < 8 else None
    return o


def add_subsurf(o, lvl=1, render=None):
    m = o.modifiers.new('subd', 'SUBSURF')
    m.levels = lvl; m.render_levels = lvl if render is None else render
    return m


def plane(name, w, d, loc=(0, 0, 0), rot=(0, 0, 0), collection=None, mat_=None, uv_scale=1.0):
    hw, hd = w / 2, d / 2
    o = obj_from_data(name, [(-hw, -hd, 0), (hw, -hd, 0), (hw, hd, 0), (-hw, hd, 0)],
                      [(0, 1, 2, 3)], collection, smooth=False)
    uvl = o.data.uv_layers.new(name='UV')
    for li, uvv in zip(range(4), [(0, 0), (w * uv_scale, 0), (w * uv_scale, d * uv_scale), (0, d * uv_scale)]):
        uvl.data[li].uv = uvv
    o.location = loc; o.rotation_euler = rot
    if mat_:
        o.data.materials.append(mat_)
    return o


def instance(src, name, loc=(0, 0, 0), rot=(0, 0, 0), scale=None, collection=None):
    """Linked duplicate: shares mesh data (efficient instancing)."""
    o = src.copy()
    o.name = name
    o.location = loc; o.rotation_euler = rot
    if scale:
        o.scale = scale
    (collection or src.users_collection[0]).objects.link(o)
    return o


def join(objs, name):
    ctx = bpy.context
    for o in ctx.view_layer.objects:
        o.select_set(False)
    for o in objs:
        o.select_set(True)
    ctx.view_layer.objects.active = objs[0]
    with ctx.temp_override(active_object=objs[0], selected_editable_objects=objs, selected_objects=objs):
        bpy.ops.object.join()
    objs[0].name = name
    return objs[0]


def apply_mods(o):
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(o.evaluated_get(dg))
    o.modifiers.clear()
    old = o.data; o.data = me
    if old.users == 0:
        bpy.data.meshes.remove(old)


# ---------------------------------------------------------------- keyframes
def key(idb, path, frame, value, index=-1, interp=None):
    if index >= 0:
        getattr(idb, path)[index] = value
    else:
        setattr(idb, path, value)
    idb.keyframe_insert(path, index=index, frame=frame)
    if interp:
        set_last_interp(idb, path, interp)


def set_last_interp(idb, path, interp):
    ad = idb.animation_data
    if not ad or not ad.action:
        return
    for fc in fcurves_of(ad):
        if fc.data_path == path:
            for kp in fc.keyframe_points:
                kp.interpolation = interp


def fcurves_of(ad):
    """Blender 4.4+ layered actions; fall back to legacy action.fcurves."""
    act = ad.action
    if hasattr(act, 'fcurves') and len(getattr(act, 'fcurves', [])):
        return list(act.fcurves)
    out = []
    try:
        slot = ad.action_slot
        for layer in act.layers:
            for strip in layer.strips:
                cb = strip.channelbag(slot)
                if cb:
                    out.extend(cb.fcurves)
    except Exception:
        pass
    return out


def smoothstep(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def lerp(a, b, t):
    return a + (b - a) * t


def vlerp(a, b, t):
    return tuple(lerp(x, y, t) for x, y in zip(a, b))

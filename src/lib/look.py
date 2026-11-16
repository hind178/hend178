"""Render settings, world, sun and the warm->cool lighting arc."""
import bpy, math
from . import util as U

# mood presets: sun colour, sun strength, sky colour, sky strength, sun elevation, azimuth
MOODS = {
    'warm_morning': ((1.0, 0.86, 0.66), 4.2, (0.55, 0.68, 0.85), 0.9, 38, -40),
    'warm_noon':    ((1.0, 0.9, 0.75), 4.6, (0.55, 0.7, 0.9), 1.0, 55, -20),
    'interior_warm': ((1.0, 0.82, 0.6), 4.0, (0.6, 0.62, 0.65), 0.55, 35, 160),
    'tense':        ((0.95, 0.9, 0.85), 3.4, (0.55, 0.62, 0.72), 0.85, 50, -10),
    'cool_after':   ((0.85, 0.87, 0.92), 2.6, (0.5, 0.58, 0.7), 0.8, 30, 20),
    'late_cool':    ((0.95, 0.78, 0.62), 1.8, (0.42, 0.48, 0.62), 0.7, 14, 60),
    'interior_cool': ((0.8, 0.85, 0.95), 2.2, (0.45, 0.5, 0.6), 0.5, 22, 160),
    'hospital':     ((0.75, 0.85, 1.0), 1.6, (0.5, 0.58, 0.7), 0.6, 25, 90),
    'dusk':         ((0.95, 0.6, 0.42), 1.2, (0.3, 0.32, 0.45), 0.45, 6, 70),
}


def setup_render(engine='BLENDER_EEVEE', res=(1080, 1920), pct=100, samples=16):
    sc = bpy.context.scene
    sc.render.engine = engine
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.resolution_percentage = pct
    sc.render.fps = 30
    sc.view_settings.view_transform = 'AgX'
    sc.view_settings.look = 'AgX - Medium High Contrast'
    sc.render.film_transparent = False
    if engine == 'CYCLES':
        sc.cycles.samples = samples
        sc.cycles.use_denoising = True
        c = sc.cycles
        c.max_bounces = 3
        c.diffuse_bounces = 2; c.glossy_bounces = 1
        c.transmission_bounces = 2; c.transparent_max_bounces = 4; c.volume_bounces = 0
        c.caustics_reflective = False; c.caustics_refractive = False
        c.use_adaptive_sampling = True
        c.adaptive_threshold = 0.08
        c.adaptive_min_samples = 2
        c.blur_glossy = 1.5
        c.use_fast_gi = True
        c.fast_gi_method = 'ADD'
        c.denoiser = 'OPENIMAGEDENOISE'
        c.denoising_input_passes = 'RGB_ALBEDO_NORMAL'
        c.denoising_prefilter = 'ACCURATE'
        c.use_auto_tile = False
        sc.render.use_persistent_data = True
        sc.render.threads_mode = 'AUTO'
    else:
        ee = sc.eevee
        ee.taa_render_samples = samples
        for attr, v in (('use_shadows', True), ('use_raytracing', False), ('shadow_ray_count', 1),
                        ('shadow_step_count', 4), ('use_gtao', True), ('gtao_distance', 0.6)):
            if hasattr(ee, attr):
                setattr(ee, attr, v)
    sc.render.use_motion_blur = False
    return sc


def setup_world():
    sc = bpy.context.scene
    w = bpy.data.worlds.get('World') or bpy.data.worlds.new('World')
    sc.world = w
    w.use_nodes = True
    bg = w.node_tree.nodes['Background']
    sun = bpy.data.objects.get('SUN')
    if not sun:
        sun = bpy.data.objects.new('SUN', bpy.data.lights.new('SUN', 'SUN'))
        sc.collection.objects.link(sun)
        sun.data.angle = math.radians(2.5)
    return w, bg, sun


def apply_mood(frame, mood, sun_az_offset=0.0):
    """Key world + sun for a shot (constant across the shot, cut-to-cut changes)."""
    w, bg, sun = setup_world()
    col, st, sky, skys, elev, az = MOODS[mood]
    sun.data.color = col; sun.data.energy = st
    sun.rotation_euler = (math.radians(90 - elev), 0, math.radians(az + sun_az_offset))
    bg.inputs[0].default_value = (*sky, 1); bg.inputs[1].default_value = skys
    for lo in bpy.data.objects:
        if lo.type == 'LIGHT' and 'base_energy' in lo:
            warm = mood in ('warm_morning', 'warm_noon', 'interior_warm')
            lo.data.color = (1.0, 0.84, 0.64) if warm else ((0.75, 0.84, 1.0) if mood in ('hospital',) else (0.82, 0.86, 0.95))
            lo.data.energy = lo['base_energy'] * (1.0 if warm else 0.7)
            lo.data.keyframe_insert('color', frame=frame); lo.data.keyframe_insert('energy', frame=frame)
    for idb, path in ((sun.data, 'color'), (sun.data, 'energy'), (sun, 'rotation_euler')):
        idb.keyframe_insert(path, frame=frame)
    bg.inputs[0].keyframe_insert('default_value', frame=frame)
    bg.inputs[1].keyframe_insert('default_value', frame=frame)


def const_all(idb):
    ad = getattr(idb, 'animation_data', None)
    if ad and ad.action:
        for fc in U.fcurves_of(ad):
            for k in fc.keyframe_points:
                k.interpolation = 'CONSTANT'


def camera(name, coll=None):
    cam = bpy.data.objects.new(name, bpy.data.cameras.new(name))
    (coll or bpy.context.scene.collection).objects.link(cam)
    cam.data.sensor_width = 36
    cam.data.dof.use_dof = True
    cam.data.dof.aperture_fstop = 2.8
    cam.data.clip_start = 0.02
    cam.data.clip_end = 400
    return cam


def aim(cam, eye, target, roll=0.0):
    from mathutils import Vector
    d = (Vector(target) - Vector(eye))
    cam.location = eye
    q = d.to_track_quat('-Z', 'Y')
    cam.rotation_mode = 'XYZ'
    prev = cam.rotation_euler.copy()
    e = q.to_euler('XYZ', prev)          # continuous with previous key (no 2*pi spins)
    e.y += roll
    cam.rotation_euler = e
    return d.length


def area(name, loc, rot, size, energy, coll=None, shape='RECTANGLE', size_y=None):
    """Static practical/window light; colour+energy follow apply_mood()."""
    ld = bpy.data.lights.new(name, 'AREA'); ld.shape = shape; ld.size = size
    if size_y:
        ld.size_y = size_y
    ld.energy = energy
    o = bpy.data.objects.new(name, ld)
    (coll or bpy.context.scene.collection).objects.link(o)
    o.location = loc; o.rotation_euler = rot
    o['base_energy'] = energy
    return o

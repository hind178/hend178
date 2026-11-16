"""Procedural stylized character builder + rig.

One builder makes every character (Hind, Huda, Mother, Neighbour, crowd) from a
spec dict, so rigs, bone names and facial controls are identical and every
animation helper in anim.py works on all of them.

Convention: character faces -Y, its left side is +X ('.L').
Facial controls are bones (eye.L/R look, lid.L/R blink, brow.L/R) plus shape
keys on the mouth mesh (smile, sad, open, oh, cry)."""
import bpy, math, random
import numpy as np
from mathutils import Vector, Matrix
from . import util as U

# ------------------------------------------------------------------ specs
SKIN_CHILD = (0.80, 0.56, 0.42)

HIND = dict(
    name='Hind', H=1.02, head=0.145, child=True, skin=SKIN_CHILD,
    hair=(0.16, 0.085, 0.045), hair_style='bangs_straight', outfit='hind',
    eye=0.27, iris=(0.10, 0.05, 0.025), cheek=0.10, seed=5)
HUDA = dict(
    name='Huda', H=1.20, head=0.148, child=True, skin=(0.78, 0.55, 0.42),
    hair=(0.025, 0.02, 0.018), hair_style='bob_side', outfit='huda',
    eye=0.27, iris=(0.07, 0.035, 0.02), cheek=0.06, seed=7)


def adult(name, outfit, skin=(0.70, 0.48, 0.35), hair=(0.03, 0.025, 0.02),
          hair_style='scarf', H=1.62, cloth=(0.4, 0.1, 0.1), cloth2=(0.9, 0.9, 0.85),
          male=False, seed=1):
    return dict(name=name, H=H, head=0.105 if not male else 0.11, child=False, skin=skin,
                hair=hair, hair_style=hair_style, outfit=outfit, eye=0.20,
                iris=(0.06, 0.03, 0.015), cheek=0.02, cloth=cloth, cloth2=cloth2,
                male=male, seed=seed)


# ------------------------------------------------------------------ geometry helpers
def shell(name, R, center, phi_bot, t_span=math.pi, wrap=True, nt=48, nphi=18,
          phi_top=0.001, kfn=None, mat_=None, thick=0.0, subsurf=1, coll=None):
    """Spherical shell patch. phi measured from +Z (top). t=0 is front (-Y).
    phi_bot(t) gives the lower edge per azimuth -> hairlines, hoods, lids."""
    verts, faces = [], []
    ts = [(-t_span + 2 * t_span * i / (nt if wrap else nt - 1)) for i in range(nt)]
    for t in ts:
        pb = phi_bot(t)
        pt = phi_top(t) if callable(phi_top) else phi_top
        for j in range(nphi):
            p = pt + (pb - pt) * j / (nphi - 1)
            k = kfn(t, p) if kfn else 1.0
            verts.append((center[0] + R * k * math.sin(p) * math.sin(t),
                          center[1] - R * k * math.sin(p) * math.cos(t),
                          center[2] + R * k * math.cos(p)))
    cols = nt if wrap else nt - 1
    for i in range(cols):
        i2 = (i + 1) % nt
        for j in range(nphi - 1):
            faces.append((i * nphi + j, i2 * nphi + j, i2 * nphi + j + 1, i * nphi + j + 1))
    o = U.obj_from_data(name, verts, faces, coll)
    if mat_:
        o.data.materials.append(mat_)
    if thick:
        s = o.modifiers.new('solid', 'SOLIDIFY'); s.thickness = thick; s.offset = 1
    if subsurf:
        U.add_subsurf(o, subsurf)
    return o


def capsule(name, r1, r2, length, seg=16, coll=None, mat_=None, flat=1.0, bulge=0.0):
    """Limb segment along -Z from origin, rounded ends."""
    prof = []
    n = 5
    for i in range(n):  # bottom cap
        a = math.pi / 2 * i / n
        prof.append((r2 * math.sin(a) + 1e-4, -length - r2 * math.cos(a)))
    m = 6
    for i in range(m + 1):
        t = i / m
        r = r2 + (r1 - r2) * t + bulge * math.sin(math.pi * t)
        prof.append((r, -length + length * t))
    for i in range(1, n + 1):
        a = math.pi / 2 * i / n
        prof.append((r1 * math.cos(a) + 1e-4, r1 * math.sin(a)))
    return U.lathe(name, prof, seg, sy=flat, collection=coll, mat_=mat_, subsurf=1)


# ------------------------------------------------------------------ builder
class Char:
    """Handle to a built character (armature + metadata)."""
    def __init__(self, spec, arm, coll):
        self.spec, self.arm, self.coll = spec, arm, coll
        self.name = spec['name']
        self.mouth = None
        self.parts = []

    def pb(self, b):
        return self.arm.pose.bones[b]


def build(spec, collection=None):
    rnd = random.Random(spec.get('seed', 1))
    name = spec['name']
    H, child = spec['H'], spec['child']
    r = spec['head']
    coll = U.coll('CH_' + name, collection)
    # ---- key heights
    if child:
        za, zk, zh, zw, zs = 0.055 * H, 0.27 * H, 0.47 * H, 0.56 * H, 0.745 * H
        zc = zs + 0.03 * H
        sw, hw = 0.115 * H, 0.055 * H
        ua, fa, hl = 0.15 * H, 0.13 * H, 0.085 * H
    else:
        za, zk, zh, zw, zs = 0.045 * H, 0.27 * H, 0.50 * H, 0.60 * H, 0.81 * H
        zc = zs + 0.035 * H
        sw, hw = 0.12 * H, 0.06 * H
        ua, fa, hl = 0.18 * H, 0.15 * H, 0.10 * H
    hc = zc + r * (0.72 if child else 0.85)  # head centre
    top = hc + r
    # ---- armature
    ad = bpy.data.armatures.new(name + '_rig')
    arm = bpy.data.objects.new(name + '_RIG', ad)
    coll.objects.link(arm)
    ad.display_type = 'STICK'
    bpy.context.view_layer.objects.active = arm
    arm.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    eb = ad.edit_bones

    def bone(n, h, t, parent=None, roll=0.0):
        b = eb.new(n); b.head = h; b.tail = t; b.roll = roll
        if parent:
            b.parent = eb[parent]
        return b

    bone('root', (0, 0, 0), (0, 0.2, 0))
    bone('hips', (0, 0, zh), (0, 0, zw), 'root')
    bone('spine', (0, 0, zw), (0, 0, zs), 'hips')
    bone('neck', (0, 0, zs), (0, 0, zc), 'spine')
    bone('head', (0, 0, zc), (0, 0, top), 'neck')
    bone('skirt', (0, 0, zw), (0, 0, zw - 0.15), 'hips')
    ez = hc - 0.06 * r
    ex = 0.40 * r
    er = spec['eye'] * r
    ey = -math.sqrt(max(r * r - ex * ex - (ez - hc) ** 2, 0)) * 0.93 + er * 0.45
    for s, sx in (('L', 1), ('R', -1)):
        bone('eye.' + s, (sx * ex, ey, ez), (sx * ex, ey - 0.03, ez), 'head')
        bone('lid.' + s, (sx * ex, ey, ez), (sx * ex, ey - 0.03, ez), 'head')
        bone('brow.' + s, (sx * ex, ey - er * 0.5, ez + er * 1.55), (sx * ex, ey - er * 0.5 - 0.03, ez + er * 1.55), 'head')
        sh = (sx * sw, 0, zs - 0.015 * H)
        el = (sx * (sw + 0.012 * H), 0.004, sh[2] - ua)
        wr = (sx * (sw + 0.018 * H), 0.0, el[2] - fa)
        bone('upperarm.' + s, sh, el, 'spine')
        bone('forearm.' + s, el, wr, 'upperarm.' + s)
        hand_end = (wr[0], wr[1], wr[2] - hl * 0.55)
        bone('hand.' + s, wr, hand_end, 'forearm.' + s)
        bone('fingers.' + s, hand_end, (wr[0], wr[1] - 0.004, hand_end[2] - hl * 0.45), 'hand.' + s)
        bone('pinky.' + s, (wr[0], wr[1] + 0.012 * H / 1.0, hand_end[2] + 0.004),
             (wr[0], wr[1] + 0.012 * H, hand_end[2] - hl * 0.36), 'hand.' + s)
        bone('thigh.' + s, (sx * hw, 0, zh), (sx * hw, 0, zk), 'hips')
        bone('shin.' + s, (sx * hw, 0, zk), (sx * hw, 0.0, za), 'thigh.' + s)
        bone('foot.' + s, (sx * hw, 0, za), (sx * hw, -0.09 * H, 0.012), 'shin.' + s)
    if spec['outfit'] == 'hind':
        bone('tassel', (-0.06 * H, -0.09 * H, zw - 0.02), (-0.06 * H, -0.095 * H, zw - 0.17 * H), 'hips')
    bpy.ops.object.mode_set(mode='OBJECT')
    for pbn in arm.pose.bones:
        pbn.rotation_mode = 'XYZ'
    ch = Char(spec, arm, coll)
    ch.dims = dict(za=za, zk=zk, zh=zh, zw=zw, zs=zs, zc=zc, hc=hc, r=r, sw=sw, hw=hw,
                   ua=ua, fa=fa, hl=hl, ex=ex, ey=ey, ez=ez, er=er, top=top)

    def attach(o, b, apply=True):
        if apply and o.modifiers:
            U.apply_mods(o)
        bn = ad.bones[b]
        o.parent = arm; o.parent_type = 'BONE'; o.parent_bone = b
        o.matrix_parent_inverse = (arm.matrix_world @ bn.matrix_local @
                                   Matrix.Translation((0, bn.length, 0))).inverted()
        U.link(o, coll)
        ch.parts.append(o)
        return o

    # ---- materials
    skin = U.mat(name + '_skin', spec['skin'], rough=0.5, sheen=0.25)
    hairm = hair_mat(name + '_hair', spec['hair'])
    eyem = U.eye_mat(name + '_eye', spec['iris'], spec['eye'] * spec['head'])
    hi = U.mat('eye_highlight', (1, 1, 1), emission=(1, 1, 1), estr=4.0)
    lash = U.mat(name + '_lash', (0.03, 0.02, 0.018), rough=0.5)
    lips = U.mat(name + '_mouth', (0.42, 0.13, 0.12), rough=0.45)
    blush = U.mat(name + '_blush', (0.95, 0.42, 0.38), rough=0.6, alpha=0.35)

    # ---- head
    def head_shape(t, z):
        zz = (z - hc) / r
        front = 0.5 + 0.5 * math.cos(t)
        side = abs(math.sin(t))
        cheek = spec['cheek'] * math.exp(-((zz + 0.38) / 0.28) ** 2) * (0.35 + 0.65 * side) * (0.5 + front)
        chin = -0.08 * max(0, -zz - 0.55) * (1 - front * 0.5)
        back = 0.06 * math.exp(-((zz - 0.15) / 0.5) ** 2) * (1 - front)
        return 1 + cheek + chin + back - 0.05 * front * max(0, zz)

    rings = 22
    prof = []
    for i in range(1, rings):
        a = math.pi * i / rings
        prof.append((r * math.sin(a), hc - r * math.cos(a) * (1.0 if i > rings / 2 else 0.98)))
    hd = U.lathe(name + '_head', prof, 40, sx=1.0, sy=0.96, collection=coll, mat_=skin,
                 subsurf=2, shape=head_shape)
    attach(hd, 'head')
    # nose, ears
    ny = -r * 0.98
    nose = U.sphere(name + '_nose', r * (0.085 if child else 0.11), (0, ny, hc - 0.33 * r),
                    (1.0, 0.9, 0.85 if child else 1.2), collection=coll, mat_=skin, subsurf=1)
    attach(nose, 'head')
    for s, sx in (('L', 1), ('R', -1)):
        ear = U.sphere(name + '_ear' + s, r * 0.2, (sx * r * 1.0, 0.05 * r, hc - 0.1 * r),
                       (0.45, 0.8, 1.15), collection=coll, mat_=skin, subsurf=1)
        attach(ear, 'head')
        if spec['cheek'] > 0.05:
            b = U.sphere(name + '_blush' + s, r * 0.17, (sx * r * 0.52, -r * 0.83, hc - 0.35 * r),
                         (1.1, 0.35, 0.7), collection=coll, mat_=blush)
            b.rotation_euler = (0, 0, sx * 0.55)
            attach(b, 'head')
    # neck
    nk = capsule(name + '_neck', r * 0.36, r * 0.38, zc - zs + r * 0.4, coll=coll, mat_=skin)
    nk.location = (0, 0.01, zc + r * 0.35)
    attach(nk, 'neck')

    # ---- eyes
    for s, sx in (('L', 1), ('R', -1)):
        c = (sx * ex, ey, ez)
        eb_ = U.sphere(name + '_eyeball' + s, er, c, collection=coll, mat_=eyem, seg=32, rings=16)
        attach(eb_, 'eye.' + s)
        h1 = U.sphere(name + '_hl' + s, er * 0.17, (c[0] + er * 0.32, c[1] - er * 0.93, c[2] + er * 0.36),
                      collection=coll, mat_=hi, seg=10, rings=6)
        attach(h1, 'head')
        h2 = U.sphere(name + '_hl2' + s, er * 0.08, (c[0] - er * 0.25, c[1] - er * 0.97, c[2] - er * 0.2),
                      collection=coll, mat_=hi, seg=8, rings=5)
        attach(h2, 'head')
        # upper lid: cap phi 0..100deg, opened by rotating back (bone X rot)
        lid = shell(name + '_lid' + s, er * 1.09, c, lambda t: math.radians(100),
                    nt=32, nphi=10, mat_=skin, thick=er * 0.05, subsurf=1, coll=coll)
        attach(lid, 'lid.' + s)
        lashes = shell(name + '_lash' + s, er * 1.13, c,
                       lambda t: math.radians(100 + 6 * math.cos(t)), t_span=math.radians(80),
                       wrap=False, nt=14, nphi=3, phi_top=lambda t: math.radians(93 + 0 * t),
                       mat_=lash, thick=er * 0.10, subsurf=1, coll=coll)
        attach(lashes, 'lid.' + s)
        low = shell(name + '_lowlid' + s, er * 1.06, c, lambda t: math.radians(180),
                    phi_top=math.radians(132), nt=24, nphi=5, mat_=skin, thick=er * 0.05, coll=coll)
        attach(low, 'head')
        # brow
        bw = U.sphere(name + '_brow' + s, 1.0, (sx * ex, ey - er * 0.45, ez + er * 1.55),
                      (er * 0.95, er * 0.16, er * (0.14 if child else 0.17)), collection=coll,
                      mat_=lash if spec['hair_style'] != 'bangs_straight' else hairm, subsurf=1)
        bw.rotation_euler = (0.2, 0, -sx * 0.12)
        attach(bw, 'brow.' + s)

    # ---- mouth with shape keys
    ch.mouth = build_mouth(ch, coll, lips, hd)
    # ---- hair
    build_hair(ch, coll, hairm, skin)
    # ---- body + outfit
    build_body(ch, coll, skin, attach)
    # rest pose: lids open
    reset_pose(ch)
    ch.arm['char_spec'] = str({k: v for k, v in spec.items()})
    return ch


def hair_mat(name, color):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; p = nt.nodes['Principled BSDF']
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Roughness'].default_value = 0.38
    p.inputs['Coat Weight'].default_value = 0.35
    p.inputs['Sheen Weight'].default_value = 0.4
    p.inputs['Sheen Tint'].default_value = (0.6, 0.45, 0.35, 1)
    tc = nt.nodes.new('ShaderNodeTexCoord')
    w = nt.nodes.new('ShaderNodeTexWave'); w.wave_type = 'BANDS'; w.bands_direction = 'X'
    w.inputs['Scale'].default_value = 26; w.inputs['Distortion'].default_value = 6
    w.inputs['Detail'].default_value = 3
    mp = nt.nodes.new('ShaderNodeMapping'); mp.inputs['Rotation'].default_value = (0, 0, 1.57)
    nt.links.new(tc.outputs['Object'], mp.inputs['Vector'])
    nt.links.new(mp.outputs['Vector'], w.inputs['Vector'])
    b = nt.nodes.new('ShaderNodeBump'); b.inputs['Strength'].default_value = 0.35
    nt.links.new(w.outputs['Fac'], b.inputs['Height'])
    nt.links.new(b.outputs['Normal'], p.inputs['Normal'])
    m.diffuse_color = (*color, 1)
    return m


def build_mouth(ch, coll, lips, head):
    d = ch.dims; r = d['r']; hc = d['hc']
    child = ch.spec['child']
    w = r * (0.30 if child else 0.36)
    zc = hc - r * (0.56 if child else 0.6)
    n = 20
    def surf_y(x, z):
        return -math.sqrt(max(r * r - x * x - (z - hc) ** 2, 1e-6)) * 0.96 * (1 + 0.03) - 0.002
    base = []
    for i in range(n):
        a = 2 * math.pi * i / n
        x = math.cos(a) * w * 0.5; z = zc + math.sin(a) * w * 0.035
        base.append([x, 0, z])
    base.append([0, 0, zc])
    verts = [(x, surf_y(x, z), z) for x, _, z in base]
    faces = [(n, i, (i + 1) % n) for i in range(n)]
    o = U.obj_from_data(ch.name + '_mouth', verts, faces, coll)
    o.data.materials.append(lips)
    o.shape_key_add(name='Basis')

    def sk(nm, fn):
        k = o.shape_key_add(name=nm, from_mix=False)
        for i, (x, _, z) in enumerate(base):
            nx, nz = fn(x / (w * 0.5), (z - zc) / (w * 0.5), i)
            X = nx * w * 0.5; Z = zc + nz * w * 0.5
            k.data[i].co = (X, surf_y(X, Z) - 0.002 * (1 - abs(nx)), Z)
    sk('smile', lambda u, v, i: (u * 1.05, v + 0.32 * u * u - 0.08 - (0.12 * (1 - u * u) if v < 0 else 0)))
    sk('sad', lambda u, v, i: (u * 0.85, v - 0.25 * u * u + 0.06))
    sk('open', lambda u, v, i: (u * 0.8, v * 9.0 - 0.15 if i < n else -0.1))
    sk('oh', lambda u, v, i: (u * 0.45, v * 9.0 - 0.1 if i < n else -0.05))
    sk('cry', lambda u, v, i: (u * 0.95, (v * 6 if v < 0 else v * 3) - 0.28 * u * u + 0.05))
    for kb in o.data.shape_keys.key_blocks:
        kb.value = 0.0
    U.add_subsurf(o, 1)
    bn = ch.arm.data.bones['head']
    o.parent = ch.arm; o.parent_type = 'BONE'; o.parent_bone = 'head'
    o.matrix_parent_inverse = (ch.arm.matrix_world @ bn.matrix_local @ Matrix.Translation((0, bn.length, 0))).inverted()
    ch.parts.append(o)
    return o


def build_hair(ch, coll, hairm, skin):
    d = ch.dims; r = d['r']; hc = d['hc']; s = ch.spec; st = s['hair_style']
    c = (0, 0.03 * r, hc + 0.02 * r)
    parts = []
    deg = math.radians
    def smoothfront(t, front_phi, side_phi, width=deg(62)):
        f = math.exp(-(t / width) ** 4)
        return front_phi * f + side_phi * (1 - f)
    if st == 'bob_side':   # Huda: black jaw-length bob, side-swept fringe, white clip
        main = shell(ch.name + '_hair', r * 1.10, c,
                     lambda t: smoothfront(t, deg(42), deg(132) + deg(4) * math.sin(t * 9)),
                     kfn=lambda t, p: 1 + 0.07 * math.sin(p) ** 3 + 0.02 * math.sin(t * 13) * (p / 2.4),
                     mat_=hairm, thick=0.022, coll=coll, nt=56, nphi=22)
        parts.append(main)
        fr = shell(ch.name + '_fringe', r * 1.075, (0, 0.0, hc + 0.02 * r),
                   lambda t: deg(66) + deg(14) * (t / deg(80)) + deg(3) * math.sin(t * 16),
                   t_span=deg(82), wrap=False, nt=30, nphi=12, phi_top=deg(18),
                   kfn=lambda t, p: 1 + 0.06 * math.sin(p * 1.2) - 0.03 * (t / deg(82)),
                   mat_=hairm, thick=0.016, coll=coll)
        parts.append(fr)
        clip = U.rbox(ch.name + '_clip', (r * 0.42, r * 0.12, r * 0.12), (-r * 0.2, -r * 0.28, hc + r * 1.06),
                      bevel=r * 0.05, collection=coll,
                      mat_=U.mat('clip_white', (0.95, 0.9, 0.9), rough=0.3, coat=0.5))
        clip.rotation_euler = (0.5, 0.0, 0.25)
        bow = U.sphere(ch.name + '_clipbow', r * 0.09, (-r * 0.2, -r * 0.33, hc + r * 1.07), (1.3, 0.6, 0.8),
                       collection=coll, mat_=U.mat('clip_pink', (0.95, 0.6, 0.65), rough=0.35), subsurf=1)
        parts += [clip, bow]
    elif st == 'bangs_straight':   # Hind: brown, straight bangs, black fuzzy headpiece
        main = shell(ch.name + '_hair', r * 1.07, c,
                     lambda t: smoothfront(t, deg(45), deg(118) + deg(4) * math.sin(t * 11)),
                     mat_=hairm, thick=0.02, coll=coll, nt=48, nphi=18)
        fr = shell(ch.name + '_fringe', r * 1.075, (0, 0, hc + 0.01 * r),
                   lambda t: deg(67) + deg(2.5) * math.sin(t * 20),
                   t_span=deg(78), wrap=False, nt=30, nphi=10, phi_top=deg(20),
                   kfn=lambda t, p: 1 + 0.05 * math.sin(p * 1.3), mat_=hairm, thick=0.016, coll=coll)
        parts += [main, fr]
        fur = fur_mat('hind_headpiece')
        hood = shell(ch.name + '_headpiece', r * 1.2, (0, 0.06 * r, hc + 0.1 * r),
                     lambda t: smoothfront(t, deg(52), deg(150), width=deg(70)) + deg(5) * math.sin(t * 17),
                     kfn=lambda t, p: 1 + 0.12 * math.sin(p) ** 2,
                     mat_=fur, thick=0.03, coll=coll, nt=60, nphi=22)
        dsp = hood.modifiers.new('fuzz', 'DISPLACE')
        tex = bpy.data.textures.new('fuzz_tex', 'CLOUDS'); tex.noise_scale = 0.012; tex.noise_depth = 2
        dsp.texture = tex; dsp.strength = 0.018; dsp.mid_level = 0.5
        hood.modifiers.move(2, 0) if len(hood.modifiers) > 2 else None
        parts.append(hood)
        gold = U.mat('gold_trim', (0.85, 0.62, 0.25), rough=0.25, metal=1.0)
        for i, (zz, ww) in enumerate(((0.95, 0.5), (0.83, 0.36))):
            g = U.cyl(ch.name + f'_pin{i}', r * 0.022, r * ww, (r * ww * 0.5, -r * (0.98 - 0.08 * i), hc + r * (0.98 - 0.13 * i)),
                      rot=(0, -math.pi / 2, 0.1), collection=coll, mat_=gold, seg=8)
            parts.append(g)
    elif st == 'scarf':   # adult women: headscarf/abaya hood
        sc = shell(ch.name + '_scarf', r * 1.16, (0, 0.05 * r, hc + 0.03 * r),
                   lambda t: smoothfront(t, deg(40), deg(165), width=deg(55)),
                   kfn=lambda t, p: 1 + 0.15 * max(0, p - 1.8),
                   mat_=U.mat(ch.name + '_scarfmat', s.get('cloth2', (0.1, 0.1, 0.1)), rough=0.8, sheen=0.5),
                   thick=0.012, coll=coll, nt=48, nphi=20)
        parts.append(sc)
    elif st == 'short_male':
        main = shell(ch.name + '_hair', r * 1.05, c, lambda t: smoothfront(t, deg(38), deg(95)),
                     mat_=hairm, thick=0.015, coll=coll, nt=40, nphi=14)
        parts.append(main)
        mus = U.sphere(ch.name + '_moustache', r * 0.25, (0, -r * 0.93, d['hc'] - r * 0.45), (1.2, 0.35, 0.3),
                       collection=coll, mat_=hairm, subsurf=1)
        parts.append(mus)
    for p in parts:
        U.apply_mods(p)
        bn = ch.arm.data.bones['head']
        p.parent = ch.arm; p.parent_type = 'BONE'; p.parent_bone = 'head'
        p.matrix_parent_inverse = (ch.arm.matrix_world @ bn.matrix_local @ Matrix.Translation((0, bn.length, 0))).inverted()
        ch.parts.append(p)


def fur_mat(name):
    m = bpy.data.materials.get(name)
    if m:
        return m
    m = U.mat(name, (0.012, 0.011, 0.012), rough=0.9, sheen=1.0)
    m.node_tree.nodes['Principled BSDF'].inputs['Sheen Tint'].default_value = (0.5, 0.5, 0.55, 1)
    return m


def pattern_dress_img():
    """Green vintage print from the photo: white rounded frames with colourful motifs."""
    img = bpy.data.images.get('huda_dress_print')
    if img:
        return img
    W = Hh = 512
    rng = np.random.default_rng(7)
    a = np.zeros((Hh, W, 3)); a[:] = (0.04, 0.22, 0.09)
    yy, xx = np.mgrid[0:Hh, 0:W]
    cols = [(0.85, 0.75, 0.15), (0.75, 0.2, 0.45), (0.25, 0.45, 0.8), (0.85, 0.45, 0.2), (0.55, 0.25, 0.65)]
    for gy in range(4):
        for gx in range(4):
            cx = gx * 128 + 64 + rng.integers(-18, 18) + (64 if gy % 2 else 0)
            cy = gy * 128 + 64 + rng.integers(-14, 14)
            w, h = rng.integers(34, 46), rng.integers(40, 54)
            for ox in (-W, 0, W):
                dx = np.abs(xx - cx - ox) - w; dy = np.abs(yy - cy) - h
                dist = np.sqrt(np.maximum(dx, 0) ** 2 + np.maximum(dy, 0) ** 2) + np.minimum(np.maximum(dx, dy), 0)
                ring = (np.abs(dist + 6) < 4)
                a[ring] = (0.92, 0.92, 0.86)
                for k in range(5):
                    bx = cx + ox + rng.integers(-w + 10, w - 10); by = cy + rng.integers(-h + 10, h - 10)
                    br = rng.integers(5, 11)
                    m = ((xx - bx) ** 2 + (yy - by) ** 2 < br * br) & (dist < -8)
                    a[m] = cols[rng.integers(0, len(cols))]
    return U.image_from_array('huda_dress_print', a)


def carpet_img():
    img = bpy.data.images.get('iraqi_carpet')
    if img:
        return img
    W = 512
    yy, xx = np.mgrid[0:W, 0:W] / W
    a = np.zeros((W, W, 3)); a[:] = (0.45, 0.05, 0.06)
    cx, cy = np.abs(xx - 0.5), np.abs(yy - 0.5)
    border = (np.maximum(cx, cy) > 0.40)
    a[border] = (0.08, 0.1, 0.25)
    a[(np.maximum(cx, cy) > 0.385) & (np.maximum(cx, cy) < 0.40)] = (0.85, 0.7, 0.4)
    a[(np.maximum(cx, cy) > 0.455) & (np.maximum(cx, cy) < 0.47)] = (0.85, 0.7, 0.4)
    med = (cx + cy) < 0.22
    a[med] = (0.08, 0.1, 0.25)
    a[((cx + cy) < 0.14)] = (0.85, 0.7, 0.4)
    a[((cx + cy) < 0.09)] = (0.45, 0.05, 0.06)
    pat = (np.sin(xx * 80) * np.sin(yy * 80) > 0.6) & ~border & ~med
    a[pat] = (0.6, 0.15, 0.1)
    rose = ((np.sin(xx * 25.13) * np.sin(yy * 25.13)) > 0.8) & border
    a[rose] = (0.75, 0.55, 0.3)
    return U.image_from_array('iraqi_carpet', a)


def build_body(ch, coll, skin, attach):
    s = ch.spec; d = ch.dims; H = s['H']; o_ = s['outfit']
    zs, zw, zh, zk, za = d['zs'], d['zw'], d['zh'], d['zk'], d['za']
    child = s['child']
    tw = 0.10 * H if child else 0.115 * H   # torso half width
    gold = U.mat('gold_trim', (0.85, 0.62, 0.25), rough=0.25, metal=1.0)
    white = U.mat('cloth_white', (0.86, 0.85, 0.80), rough=0.75, sheen=0.4)
    if o_ == 'hind':
        top_m = U.mat('hind_velvet', (0.03, 0.02, 0.025), rough=0.55, sheen=1.0)
        top_m.node_tree.nodes['Principled BSDF'].inputs['Sheen Tint'].default_value = (0.35, 0.3, 0.4, 1)
        sleeve_m, leg_m = top_m, top_m
        skirt_m = top_m
        shoe_m = U.mat('shoe_red', (0.6, 0.05, 0.05), rough=0.4, coat=0.3)
        sock_m = white
    elif o_ == 'huda':
        top_m = U.mat('huda_blouse', (0.88, 0.86, 0.78), rough=0.7, sheen=0.5, bump=0.25)
        sleeve_m = top_m
        skirt_m = U.mat('huda_dress', (0.1, 0.4, 0.15), rough=0.7, sheen=0.4, image=pattern_dress_img(), uv_scale=2.0)
        leg_m = U.mat('tights_white', (0.88, 0.87, 0.84), rough=0.6, sheen=0.3)
        shoe_m = U.mat('shoe_black', (0.015, 0.015, 0.02), rough=0.15, coat=1.0)
        sock_m = leg_m
    else:
        top_m = U.mat(ch.name + '_cloth', s['cloth'], rough=0.75, sheen=0.5)
        sleeve_m = top_m; skirt_m = top_m
        leg_m = U.mat('trousers_dark', (0.08, 0.08, 0.1), rough=0.7) if s.get('male') else top_m
        shoe_m = U.mat('shoe_brown', (0.12, 0.07, 0.04), rough=0.4)
        sock_m = skin
    # torso
    def torso_shape(t, z):
        return 1 + 0.06 * math.cos(t)
    torso_prof = [(tw * 0.92, zw - 0.02), (tw * 1.0, zw + 0.05 * H), (tw * 1.07, zs - 0.07 * H),
                  (tw * 1.02, zs - 0.03 * H), (tw * 0.75, zs), (tw * 0.42, zs + 0.012 * H)]
    torso = U.lathe(ch.name + '_torso', torso_prof, 32, sx=1.0, sy=0.72 if child else 0.62,
                    collection=coll, mat_=top_m, subsurf=2, shape=torso_shape)
    attach(torso, 'spine')
    if child:  # little tummy
        tum = U.sphere(ch.name + '_tummy', tw * 0.8, (0, -tw * 0.18, zw + 0.03 * H), (1.0, 0.7, 0.85),
                       collection=coll, mat_=top_m, subsurf=1)
        attach(tum, 'spine')
    # outfit specifics on torso
    if o_ == 'hind':
        # open jacket front: white shirt V + collar + gold piping
        shirt = U.sphere('Hind_shirtfront', 1.0, (0, -tw * 0.66, zs - 0.035 * H), (tw * 0.30, tw * 0.1, 0.05 * H),
                         collection=coll, mat_=white, subsurf=1)
        attach(shirt, 'spine')
        for sx in (1, -1):
            col_ = U.rbox(f'Hind_collar{sx}', (tw * 0.42, 0.012, tw * 0.3), (sx * tw * 0.22, -tw * 0.62, zs + 0.004),
                          bevel=0.01, collection=coll, mat_=white)
            col_.rotation_euler = (0.5, sx * 0.25, sx * 0.55)
            attach(col_, 'spine')
            pip = U.cyl(f'Hind_piping{sx}', 0.004, zs - zh + 0.05 * H, (sx * tw * 0.26, -tw * 0.745, zh - 0.1 * H),
                        collection=coll, mat_=gold, seg=6)
            attach(pip, 'spine')
    elif o_ == 'huda':
        lace_m = U.mat('lace', (0.95, 0.94, 0.9), rough=0.8, sheen=0.6, bump=0.8)
        bib = U.sphere('Huda_lacebib', 1.0, (0, -tw * 0.68, zs - 0.06 * H), (tw * 0.5, tw * 0.1, 0.065 * H),
                       collection=coll, mat_=lace_m, subsurf=1)
        attach(bib, 'spine')
        for i in range(7):
            u = (i - 3) / 3.0
            ru = U.sphere(f'Huda_ruffle{i}', 1.0, (u * tw * 0.5, -tw * 0.70 + 0.01 * u * u, zs - 0.12 * H + 0.03 * H * u * u),
                          (tw * 0.1, tw * 0.07, 0.022 * H), collection=coll, mat_=lace_m, subsurf=1)
            attach(ru, 'spine')
        for sx in (1, -1):
            strap = U.rbox(f'Huda_strap{sx}', (tw * 0.38, tw * 1.55, 0.13 * H),
                           (sx * tw * 0.72, 0.0, zs - 0.09 * H), bevel=0.02, collection=coll, mat_=skirt_m)
            attach(strap, 'spine')
        bodice = U.lathe('Huda_bodice', [(tw * 0.97, zw - 0.02), (tw * 1.03, zw + 0.06 * H), (tw * 1.08, zw + 0.09 * H)],
                         32, sy=0.74, collection=coll, mat_=skirt_m, subsurf=1)
        attach(bodice, 'spine')
    elif o_ in ('mother', 'abaya'):
        pass
    # hips / skirt / trousers
    if o_ == 'huda':
        sk = U.lathe('Huda_skirt', [(tw * 0.95, zw + 0.01), (tw * 1.25, zh), (tw * 1.75, zk + 0.02 * H),
                                     (tw * 1.9, zk - 0.035 * H)],
                     40, sy=0.85, collection=coll, mat_=skirt_m, subsurf=1, cap_top=False, cap_bot=False,
                     shape=lambda t, z: 1 + 0.035 * math.sin(t * 9) * max(0, (zh - z) / 0.2))
        attach(sk, 'skirt')
        lace_m = U.mat('lace', (0.95, 0.94, 0.9))
        hem = U.lathe('Huda_lacehem', [(tw * 1.88, zk - 0.03 * H), (tw * 1.98, zk - 0.075 * H)],
                      48, sy=0.85, collection=coll, mat_=lace_m, subsurf=1, cap_top=False, cap_bot=False,
                      shape=lambda t, z: 1 + 0.03 * math.sin(t * 24) * (1 if z < zk - 0.05 * H else 0))
        sol = hem.modifiers.new('s', 'SOLIDIFY'); sol.thickness = 0.004
        attach(hem, 'skirt')
    elif o_ == 'hind':
        jk = U.lathe('Hind_jacketskirt', [(tw * 0.93, zw + 0.02), (tw * 1.08, zh), (tw * 1.25, zh - 0.12 * H)],
                     36, sy=0.8, collection=coll, mat_=top_m, subsurf=1, cap_top=False, cap_bot=False)
        sol = jk.modifiers.new('s', 'SOLIDIFY'); sol.thickness = 0.008
        attach(jk, 'hips')
        pel = U.sphere('Hind_pelvis', 1.0, (0, 0, zh + 0.01), (tw * 0.95, tw * 0.75, 0.07 * H), collection=coll,
                       mat_=top_m, subsurf=1)
        attach(pel, 'hips')
        sash = U.lathe('Hind_sash', [(tw * 0.96, zw - 0.025), (tw * 0.98, zw + 0.02)], 32, sy=0.76,
                       collection=coll, mat_=top_m, subsurf=1)
        attach(sash, 'hips')
        # tassel cord
        cord = U.cyl('Hind_cord', 0.003, 0.15 * H, (-0.06 * H, -0.093 * H, zw - 0.17 * H), collection=coll,
                     mat_=top_m, seg=6)
        attach(cord, 'tassel')
        tas = U.lathe('Hind_tasselend', [(0.004, 0), (0.012, -0.02), (0.016, -0.05), (0.002, -0.055)], 12,
                      collection=coll, mat_=top_m, subsurf=1)
        tas.location = (-0.06 * H, -0.095 * H, zw - 0.17 * H)
        attach(tas, 'tassel')
    else:  # adults: long robe / abaya / dishdasha
        robe = U.lathe(ch.name + '_robe', [(tw * 0.92, zw + 0.02), (tw * 1.1, zh), (tw * 1.32, zk),
                                           (tw * 1.45, za + 0.04)],
                       36, sy=0.8, collection=coll, mat_=skirt_m, subsurf=1, cap_top=False, cap_bot=False,
                       shape=lambda t, z: 1 + 0.03 * math.sin(t * 7) * max(0, (zh - z) / 0.3))
        sol = robe.modifiers.new('s', 'SOLIDIFY'); sol.thickness = 0.008
        attach(robe, 'skirt')
        pel = U.sphere(ch.name + '_pelvis', 1.0, (0, 0, zh + 0.01), (tw * 0.95, tw * 0.75, 0.07 * H),
                       collection=coll, mat_=skirt_m, subsurf=1)
        attach(pel, 'hips')
    # legs
    for sx, S in ((1, 'L'), (-1, 'R')):
        hx = sx * d['hw']
        if o_ == 'hind':
            th = capsule(f'Hind_trouser{S}', 0.062 * H, 0.055 * H, zh - zk, coll=coll, mat_=leg_m, bulge=0.008)
            sh_ = capsule(f'Hind_trouserlow{S}', 0.055 * H, 0.04 * H, zk - za - 0.03, coll=coll, mat_=leg_m, bulge=0.006)
        else:
            th = capsule(f'{ch.name}_thigh{S}', 0.05 * H, 0.038 * H, zh - zk, coll=coll, mat_=leg_m)
            sh_ = capsule(f'{ch.name}_shin{S}', 0.037 * H, 0.028 * H, zk - za, coll=coll,
                          mat_=sock_m if o_ != 'huda' else leg_m)
        th.location = (hx, 0, zh); attach(th, 'thigh.' + S)
        sh_.location = (hx, 0, zk); attach(sh_, 'shin.' + S)
        # shoe
        fl = 0.13 * H if child else 0.15 * H
        shoe = U.lathe(f'{ch.name}_shoe{S}', [(0.0, 0.0), (0.045 * H, 0.002), (0.05 * H, 0.03 * H),
                                               (0.035 * H, 0.06 * H), (0.0, 0.065 * H)],
                       24, sx=0.75, sy=1.0, collection=coll, mat_=shoe_m, subsurf=2,
                       shape=lambda t, z: 1 + 0.55 * max(0, math.cos(t)) * (1 - z / (0.065 * H)))
        shoe.location = (hx, -0.022 * H, 0.0); attach(shoe, 'foot.' + S)
        if o_ == 'hind':   # red/white sneaker: white sole + white toe stripes
            sole = U.lathe(f'Hind_sole{S}', [(0.0, 0.0), (0.05 * H, 0.0), (0.052 * H, 0.014 * H), (0.0, 0.014 * H)],
                           24, sx=0.78, collection=coll, mat_=white, subsurf=1,
                           shape=lambda t, z: 1 + 0.55 * max(0, math.cos(t)))
            sole.location = (hx, -0.022 * H, 0.0); attach(sole, 'foot.' + S)
            for k in range(2):
                strp = U.rbox(f'Hind_shoestripe{S}{k}', (0.075 * H, 0.012 * H, 0.006), (hx, -0.06 * H + k * 0.025 * H, 0.04 * H - k * 0.006),
                              bevel=0.002, collection=coll, mat_=white)
                strp.rotation_euler = (0.6, 0, 0)
                attach(strp, 'foot.' + S)
        if o_ == 'huda':
            strap = U.rbox(f'Huda_shoestrap{S}', (0.085 * H, 0.012 * H, 0.008), (hx, -0.035 * H, 0.05 * H),
                           bevel=0.003, collection=coll, mat_=shoe_m)
            attach(strap, 'foot.' + S)
    # arms
    for sx, S in ((1, 'L'), (-1, 'R')):
        ar = ch.arm.data.bones
        ub = ar['upperarm.' + S]; fb = ar['forearm.' + S]; hb = ar['hand.' + S]
        sl_r = 0.040 * H if child else 0.04 * H
        up = capsule(f'{ch.name}_upperarm{S}', sl_r * 1.05, sl_r * 0.92, ub.length, coll=coll, mat_=sleeve_m)
        _align(up, ub)
        attach(up, 'upperarm.' + S)
        fo = capsule(f'{ch.name}_forearm{S}', sl_r * 0.92, sl_r * 0.85, fb.length, coll=coll, mat_=sleeve_m,
                     bulge=0.004 if o_ == 'huda' else 0)
        _align(fo, fb)
        attach(fo, 'forearm.' + S)
        cuff_m = white if o_ in ('hind',) else (U.mat('lace', (0.95, 0.94, 0.9)) if o_ == 'huda' else sleeve_m)
        cuff = U.lathe(f'{ch.name}_cuff{S}', [(sl_r * 0.85, 0), (sl_r * 0.9, -0.018)], 20, collection=coll,
                       mat_=cuff_m, subsurf=1)
        _align(cuff, fb, at_tail=True)
        attach(cuff, 'forearm.' + S)
        build_hand(ch, S, sx, skin, coll, attach)


def _align(o, b, at_tail=False):
    """Place a -Z-built mesh along a bone (rest pose, armature at origin)."""
    head = Vector(b.head_local); tail = Vector(b.tail_local)
    dirv = (tail - head).normalized()
    q = Vector((0, 0, -1)).rotation_difference(dirv)
    o.rotation_mode = 'QUATERNION'
    o.rotation_quaternion = q
    o.location = tail if at_tail else head


def build_hand(ch, S, sx, skin, coll, attach):
    H = ch.spec['H']; child = ch.spec['child']
    hb = ch.arm.data.bones['hand.' + S]
    k = 0.85 if child else 1.0
    base = Vector(hb.head_local)
    palm_len = hb.length
    palm = U.sphere(f'{ch.name}_palm{S}', 1.0, base + Vector((0, 0, -palm_len * 0.5)),
                    (0.012 * H, 0.03 * k * H / 1.1, palm_len * 0.62),
                    collection=coll, mat_=skin, subsurf=1)
    attach(palm, 'hand.' + S)
    thumb = capsule(f'{ch.name}_thumb{S}', 0.0075 * H / 1.1, 0.0065 * H / 1.1, palm_len * 0.55, coll=coll, mat_=skin)
    thumb.location = base + Vector((-sx * 0.004, -0.022 * H / 1.1, -palm_len * 0.3))
    thumb.rotation_euler = (-0.6, 0, 0)
    attach(thumb, 'hand.' + S)
    fb = ch.arm.data.bones['fingers.' + S]
    fbase = Vector(fb.head_local)
    fl = fb.length
    for i, off in enumerate((-0.018, -0.006, 0.006)):
        f = capsule(f'{ch.name}_finger{S}{i}', 0.0068 * H / 1.1, 0.006 * H / 1.1, fl * (0.9 if i != 1 else 1.0),
                    coll=coll, mat_=skin)
        f.location = fbase + Vector((0, off * H / 1.1, 0.004))
        attach(f, 'fingers.' + S)
    pb_ = ch.arm.data.bones['pinky.' + S]
    p = capsule(f'{ch.name}_pinky{S}', 0.0058 * H / 1.1, 0.0052 * H / 1.1, pb_.length, coll=coll, mat_=skin)
    p.location = Vector(pb_.head_local)
    attach(p, 'pinky.' + S)


# ------------------------------------------------------------------ pose basics
LID_OPEN = 0.80       # radians about bone X (+ = opens upward; bone X is world -X)
LID_CLOSED = -0.62


def reset_pose(ch):
    for pb in ch.arm.pose.bones:
        pb.location = (0, 0, 0); pb.rotation_euler = (0, 0, 0); pb.scale = (1, 1, 1)
    for s in 'LR':
        ch.pb('lid.' + s).rotation_euler.x = LID_OPEN


def build_rabbit(name='Rabbit', coll=None):
    """Small white plush rabbit (Hind's)."""
    c = U.coll('PROP_' + name, coll)
    fur = U.mat('plush_white', (0.92, 0.9, 0.88), rough=0.95, sheen=1.0, bump=0.3)
    pink = U.mat('plush_pink', (0.95, 0.6, 0.62), rough=0.9, sheen=0.6)
    bead = U.mat('bead_black', (0.01, 0.01, 0.01), rough=0.1, coat=1.0)
    parts = [U.sphere('rb_body', 0.045, (0, 0, 0.045), (1.0, 0.9, 1.1), collection=c, mat_=fur, subsurf=1),
             U.sphere('rb_head', 0.036, (0, -0.01, 0.112), collection=c, mat_=fur, subsurf=1),
             U.sphere('rb_tail', 0.013, (0, 0.043, 0.03), collection=c, mat_=fur, subsurf=1),
             U.sphere('rb_nose', 0.006, (0, -0.045, 0.108), collection=c, mat_=pink, subsurf=1)]
    for sx in (1, -1):
        parts.append(U.sphere(f'rb_ear{sx}', 1.0, (sx * 0.016, 0.0, 0.17), (0.012, 0.007, 0.045), collection=c, mat_=fur, subsurf=1))
        parts.append(U.sphere(f'rb_earin{sx}', 1.0, (sx * 0.016, -0.0055, 0.17), (0.007, 0.003, 0.034), collection=c, mat_=pink, subsurf=1))
        parts.append(U.sphere(f'rb_eye{sx}', 0.0055, (sx * 0.016, -0.04, 0.12), collection=c, mat_=bead))
        parts.append(U.sphere(f'rb_paw{sx}', 0.014, (sx * 0.032, -0.03, 0.045), (1, 1, 1.4), collection=c, mat_=fur, subsurf=1))
        parts.append(U.sphere(f'rb_foot{sx}', 0.016, (sx * 0.025, -0.02, 0.012), (1, 1.4, 0.7), collection=c, mat_=fur, subsurf=1))
    for p in parts:
        if p.modifiers:
            U.apply_mods(p)
    for p in parts:
        if p.name.startswith('rb_ear'):
            p.rotation_euler = (0.15, 0, 0)
    r = U.join(parts, name)
    return r

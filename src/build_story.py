"""Episode 01 'The Promise' - assemble story.blend from the LOCKED shared assets,
animate every shot of shotlist.SHOTS, bind cameras with timeline markers.

python build_story.py [--only S19,S20]   (--only keeps all shots but is handy for tests)"""
import sys, os, json, math, random
sys.path.insert(0, os.path.dirname(__file__))
import bpy
from mathutils import Vector, Matrix, Euler
from lib import util as U, character as C, anim as A, env as E, look as L
import shotlist as SL

ROOT = U.ROOT
SA = os.path.join(ROOT, 'shared_assets')
EP = os.path.join(ROOT, 'episode_01')
PI = math.pi
HZ = E.SIDE_Z
FACE_Y = PI            # rotation that faces +Y (towards the road / north)
FACE_NY = 0.0          # faces -Y
FACE_X = PI / 2        # faces +X
FACE_NX = -PI / 2      # faces -X


# ------------------------------------------------------------------ loading
def append_colls(path, names=None):
    with bpy.data.libraries.load(path, link=False) as (src, dst):
        dst.collections = [c for c in src.collections if names is None or c in names]
        dst.actions = list(src.actions)
    for c in dst.collections:
        if not any(c.name in p.children for p in [bpy.context.scene.collection]):
            pass
    return dst.collections


def load_char(coll):
    arm = next(o for o in coll.all_objects if o.type == 'ARMATURE')
    spec = json.loads(arm['spec'])
    ch = C.Char(spec, arm, coll)
    ch.dims = json.loads(arm['dims'])
    ch.mouth = bpy.data.objects[arm['mouth']]
    return ch


class Story:
    def __init__(self):
        U.reset_scene()
        sc = self.sc = bpy.context.scene
        sc.name = 'Episode01_ThePromise'
        sc.frame_start, sc.frame_end = 1, SL.LAST_FRAME
        L.setup_render('CYCLES', (1080, 1920), samples=8)
        L.setup_world()
        self.cast_root = U.coll('CAST')
        self.cam_root = U.coll('CAMERAS')
        envs = append_colls(os.path.join(SA, 'environments.blend'))
        for c in envs:
            if c.name == 'ENVIRONMENTS':
                sc.collection.children.link(c)
        self.ch = {}
        for f, names in (('hind.blend', None), ('huda.blend', None), ('adults.blend', None)):
            for c in append_colls(os.path.join(SA, f)):
                if c.name.startswith('CH_') or c.name.startswith('PROP_'):
                    self.cast_root.children.link(c)
                if c.name.startswith('CH_'):
                    self.ch[c.name[3:]] = load_char(c)
        for chh in self.ch.values():
            chh.arm.animation_data_create()
            C.reset_pose(chh)
            fe = bpy.data.objects.new('FOCUS_' + chh.name, None); self.cast_root.objects.link(fe)
            fe.location = (0, chh.dims['ey'] - chh.dims['er'], chh.dims['ez'])
            self.parent_bone(fe, chh, 'head')
            chh.focus = fe
        self.hind, self.huda = self.ch['Hind'], self.ch['Huda']
        self.mother, self.neighbour, self.shopkeeper = self.ch['Mother'], self.ch['Neighbour'], self.ch['Shopkeeper']
        self.crowd = [self.ch[n] for n in ('Man1', 'Man2', 'Man3', 'Woman1', 'Woman2', 'Shopkeeper')]
        self.cars = {n: bpy.data.objects[n] for n in ('Taxi', 'Sedan', 'Sedan2', 'Van', 'Ambulance')}
        self.shot_sets = {}
        self.boundaries = []
        self._props()

    # -------------------------------------------------------------- props
    def _props(self):
        pc = U.coll('STORY_PROPS')
        self.pc = pc
        rab = bpy.data.objects['Rabbit']
        self.rabbit_free = rab
        self.rabbit_held = U.instance(rab, 'Rabbit_held', collection=pc)
        self.attach_to_hand(self.rabbit_held, self.hind, 'hand.R', A.HOLD_RABBIT, (0.0, -0.06, 0.03), (0, 0, 0.3))
        bag = bpy.data.objects['veg_bag']
        self.bag_huda = U.instance(bag, 'bag_huda', collection=pc)
        self.attach_to_hand(self.bag_huda, self.huda, 'hand.L', A.CARRY_BAG_L, (0.0, 0.0, -0.36), (0, 0, 0))
        self.bag_shop = U.instance(bag, 'bag_shop', collection=pc)
        self.attach_to_hand(self.bag_shop, self.shopkeeper, 'hand.R', A.GIVE_COINS, (0.0, -0.05, -0.38), (0, 0, 0))
        note = bpy.data.objects['banknote']
        self.note_mother = U.instance(note, 'note_mother', collection=pc)
        self.attach_to_hand(self.note_mother, self.mother, 'hand.R', A.GIVE_COINS, (0.0, -0.03, -0.09), (0.3, 0, 0))
        self.note_huda = U.instance(note, 'note_huda', collection=pc)
        self.attach_to_hand(self.note_huda, self.huda, 'hand.L', A.TAKE_COINS, (0.0, -0.025, -0.07), (0.3, 0, 0))
        self.torn = bpy.data.objects['torn_bag']
        self.tomato = U.instance(bpy.data.objects['tomato_src'], 'rolling_tomato', collection=pc)
        self.scatter = []
        rnd = random.Random(3)
        for i, nm in enumerate(['tomato_src', 'tomato_src', 'cucumber_src', 'onion_src', 'tomato_src', 'cucumber_src', 'eggplant_src']):
            o = U.instance(bpy.data.objects[nm], f'scatter{i}', (0, 0, -60), collection=pc)
            self.scatter.append(o)
        self.ball = bpy.data.objects['toy_ball']; self.toycar = bpy.data.objects['toy_car']
        for i, o in enumerate(bpy.data.objects[f'toy_block{i}'] for i in range(4)):
            o.location = (102.0 + 0.12 * i, 2.0 + 0.05 * (i % 2), 0.035 + (0.07 if i == 3 else 0)); o.rotation_euler = (0, 0, 0.3 * i)
        self.home_door = bpy.data.objects['home_door']
        self.front_door = bpy.data.objects['front_door']
        # steam wisps
        steam_m = U.mat('steam', (1, 1, 1), rough=1.0, alpha=0.18)
        self.steam = [U.sphere(f'steam{i}', 0.05, (0, 0, -60), (1, 1, 1.6), collection=pc, mat_=steam_m, subsurf=1) for i in range(5)]
        # tears (Hind)
        tear_m = U.mat('tear', (0.8, 0.85, 0.9), rough=0.02, transmission=0.9, coat=1.0)
        self.tears = []
        d = self.hind.dims
        for s in (1, -1):
            t = U.sphere(f'tear{s}', d['er'] * 0.16, (s * d['ex'], d['ey'] - d['er'] * 0.85, d['ez'] - d['er'] * 0.95),
                         (1, 0.7, 1.4), collection=pc, mat_=tear_m)
            self.parent_bone(t, self.hind, 'head')
            self.tears.append(t)
        # macro hands
        self.hp = {}
        H = self.hind.spec['H']
        hs = self.ch_mat(self.hind, 'skin'); us = self.ch_mat(self.huda, 'skin'); ms = self.ch_mat(self.mother, 'skin')
        self.hp['huda'] = hand_prop('hp_huda', us, U.mat('lace', (0.95, 0.94, 0.9)), U.mat('huda_blouse', (0.88, 0.86, 0.78)), 1.0, pc)
        self.hp['hind'] = hand_prop('hp_hind', hs, U.mat('cloth_white', (0.86, 0.85, 0.8)), U.mat('hind_velvet', (0.03, 0.02, 0.025)), 0.9, pc)
        self.hp['mother'] = hand_prop('hp_mother', ms, U.mat('Mother_cloth', (0.42, 0.1, 0.13)), U.mat('Mother_cloth', (0.42, 0.1, 0.13)), 1.45, pc, kind='relaxed')
        self.hp['huda_bed'] = hand_prop('hp_huda_bed', us, U.mat('lace', (0.95, 0.94, 0.9)), U.mat('huda_blouse', (0.88, 0.86, 0.78)), 1.0, pc, kind='relaxed')
        for h in self.hp.values():
            h['root'].location = (0, 0, -70)
        self.park_props = [self.rabbit_free, self.torn, self.tomato, *self.scatter, *self.steam,
                           *[h['root'] for h in self.hp.values()]]

    def ch_mat(self, ch, kind):
        return bpy.data.materials[f'{ch.name}_{kind}']

    def parent_bone(self, o, ch, bone):
        bn = ch.arm.data.bones[bone]
        mw = o.matrix_world.copy()
        o.parent = ch.arm; o.parent_type = 'BONE'; o.parent_bone = bone
        o.matrix_parent_inverse = (ch.arm.matrix_world @ bn.matrix_local @ Matrix.Translation((0, bn.length, 0))).inverted()

    def attach_to_hand(self, o, ch, bone, pose_dict, offset, rot):
        """Parent prop to a hand bone at its rest position + offset (rest space)."""
        bn = ch.arm.data.bones[bone]
        tail = bn.tail_local
        o.location = Vector(tail) + Vector(offset)
        o.rotation_euler = rot
        o.parent = ch.arm; o.parent_type = 'BONE'; o.parent_bone = bone
        o.matrix_parent_inverse = (bn.matrix_local @ Matrix.Translation((0, bn.length, 0))).inverted()

    # -------------------------------------------------------------- helpers
    def vis(self, o, f, show):
        """Key render/viewport visibility (constant)."""
        for oo in [o] + list(o.children_recursive):
            oo.hide_render = not show; oo.hide_viewport = False
            oo.keyframe_insert('hide_render', frame=f)

    def park(self, ch, f):
        A.kb(ch, 'root', f, loc=(0, 0, -100))

    def place(self, ch, f, xy, rot, z=0.0):
        A.kb(ch, 'root', f, loc=(xy[0], xy[1], z), rot=(0, 0, rot))

    def obj_key(self, o, f, loc=None, rot=None, scale=None):
        if loc is not None:
            o.location = loc; o.keyframe_insert('location', frame=f)
        if rot is not None:
            o.rotation_euler = rot; o.keyframe_insert('rotation_euler', frame=f)
        if scale is not None:
            o.scale = scale; o.keyframe_insert('scale', frame=f)

    def bone_world(self, ch, bone, f, along=0.0):
        self.sc.frame_set(f)
        pb = ch.arm.pose.bones[bone]
        return ch.arm.matrix_world @ pb.matrix @ Vector((0, along, 0))

    def head(self, ch, f, eyes=True):
        d = ch.dims
        return self.bone_world(ch, 'head', f, (d['hc'] - d['zc']) - (0.06 * d['r'] if eyes else 0))

    def front(self, ch, f, dist, ang=0.0, dz=0.0, side=0.0):
        """Camera eye placed in front of the face, using the head bone's real orientation."""
        self.sc.frame_set(f)
        pb = ch.arm.pose.bones['head']
        M = ch.arm.matrix_world.to_3x3() @ pb.matrix.to_3x3()
        fwd = (M @ Vector((0, 0, 1))).normalized(); up = (M @ Vector((0, 1, 0))).normalized()
        right = fwd.cross(up).normalized()
        h = self.head(ch, f)
        d = (Matrix.Rotation(ang, 3, up) @ fwd)
        return h + d * dist + up * dz + right * side, h

    def cam(self, sid, f0, f1, eye0, tgt0, eye1=None, tgt1=None, lens=35, focus=None, fstop=2.8,
            shake=0.0, lens1=None, focus_dist=None):
        cam = L.camera('CAM_' + sid, self.cam_root)
        cam.data.lens = lens
        cam.data.dof.aperture_fstop = fstop
        if isinstance(focus, tuple) and len(focus) == 2 and isinstance(focus[0], C.Char):
            cam.data.dof.focus_object = focus[0].focus
        elif isinstance(focus, bpy.types.Object):
            cam.data.dof.focus_object = focus
        else:
            cam.data.dof.focus_distance = focus_dist or (Vector(tgt0) - Vector(eye0)).length
        eye1 = eye1 or eye0; tgt1 = tgt1 or tgt0
        L.aim(cam, eye0, tgt0)
        cam.keyframe_insert('location', frame=f0); cam.keyframe_insert('rotation_euler', frame=f0)
        cam.data.keyframe_insert('lens', frame=f0)
        if shake:
            rnd = random.Random(hash(sid) & 0xffff)
            for f in range(f0 + 4, f1, 4):
                t = (f - f0) / max(1, f1 - f0)
                e = Vector(eye0).lerp(Vector(eye1), U.smoothstep(t)); g = Vector(tgt0).lerp(Vector(tgt1), U.smoothstep(t))
                e += Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-1, 1))) * shake
                L.aim(cam, e, g)
                cam.keyframe_insert('location', frame=f); cam.keyframe_insert('rotation_euler', frame=f)
        L.aim(cam, eye1, tgt1)
        cam.data.lens = lens1 or lens
        cam.keyframe_insert('location', frame=f1); cam.keyframe_insert('rotation_euler', frame=f1)
        cam.data.keyframe_insert('lens', frame=f1)
        if focus_dist and not focus:
            pass
        m = self.sc.timeline_markers.new(sid, frame=f0); m.camera = cam
        return cam

    def focus_pull(self, cam, f0, d0, f1, d1):
        cam.data.dof.focus_object = None
        cam.data.dof.focus_distance = d0; cam.data.dof.keyframe_insert('focus_distance', frame=f0)
        cam.data.dof.focus_distance = d1; cam.data.dof.keyframe_insert('focus_distance', frame=f1)

    def car_drive(self, name, f0, f1, x0, x1, y, park_after=True):
        o = self.cars[name]
        rot = 0 if x1 > x0 else PI
        self.obj_key(o, f0, loc=(x0, y, 0), rot=(0, 0, rot))
        self.obj_key(o, f1, loc=(x1, y, 0), rot=(0, 0, rot))
        U.set_last_interp(o, 'location', 'LINEAR')
        dist = abs(x1 - x0)
        for w in o.children:
            if '_wheel' in w.name:
                w.rotation_euler[1] = 0; w.keyframe_insert('rotation_euler', index=1, frame=f0)
                w.rotation_euler[1] = dist / 0.34; w.keyframe_insert('rotation_euler', index=1, frame=f1)
                U.set_last_interp(w, 'rotation_euler', 'LINEAR')

    def car_hold(self, name, f, loc, rot=0.0):
        self.obj_key(self.cars[name], f, loc=loc, rot=(0, 0, rot))

    def ground(self, x, y):
        if x > 50:
            return 0.0
        return HZ if (y < 0.0 or y > 7.0) else 0.0

    def walk(self, ch, f0, f1, pts, run=False, **kw):
        A.walk(ch, f0, f1, pts, run=run, **kw)
        # lift onto sidewalks
        ad = ch.arm.animation_data
        for fc in U.fcurves_of(ad):
            if fc.data_path == 'pose.bones["root"].location' and fc.array_index == 2:
                xs = {round(k.co.x): k for k in fc.keyframe_points}
        fx = fy = None
        for fc in U.fcurves_of(ad):
            if fc.data_path == 'pose.bones["root"].location':
                if fc.array_index == 0: fx = fc
                if fc.array_index == 1: fy = fc
        for fc in U.fcurves_of(ad):
            if fc.data_path == 'pose.bones["root"].location' and fc.array_index == 2:
                for k in fc.keyframe_points:
                    if f0 <= k.co.x <= f1:
                        k.co.y += self.ground(fx.evaluate(k.co.x), fy.evaluate(k.co.x))
                        k.handle_left.y = k.handle_right.y = k.co.y
                        k.handle_left_type = k.handle_right_type = 'AUTO_CLAMPED'

    # -------------------------------------------------------------- shot driver
    def run(self, only=None):
        everyone = list(self.ch.values())
        for s in SL.SHOTS:
            sid = s[0]; f0, f1 = SL.frames(s)
            self.boundaries.append(f0)
            self.shot_sets[sid] = s[3]
            L.apply_mood(f0, s[4])
            # default: everyone parked, props hidden, cars parked
            for chh in everyone:
                self.park(chh, f0)
                A.pose(chh, f0)
                A.expr(chh, f0, 'neutral')
            for o in self.park_props:
                self.obj_key(o, f0, loc=(0, 0, -70))
            for o in (self.rabbit_held, self.bag_huda, self.bag_shop, self.note_huda, self.note_mother, *self.tears):
                self.vis(o, f0, False)
            for n in self.cars:
                self.car_hold(n, f0, (0, 0, -80))
            for b in self.cars['Ambulance'].children:
                if 'beacon' in b.name:
                    b.active_material.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value = 0
                    b.active_material.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].keyframe_insert('default_value', frame=f0)
            self.obj_key(self.home_door, f0, rot=(0, 0, 0)); self.obj_key(self.front_door, f0, rot=(0, 0, 0))
            self.obj_key(self.ball, f0, loc=(101.4, 3.2, 0.09)); self.obj_key(self.toycar, f0, loc=(103.3, 2.0, 0.03), rot=(0, 0, 0.4))
            getattr(self, sid.lower())(f0, f1)
        self.apply_cuts()
        self.sc.frame_set(1)

    def apply_cuts(self):
        """Make every property hold its value across cuts (no blending between shots)."""
        bset = sorted(self.boundaries)
        ids = [o for o in bpy.data.objects] + [o.data for o in bpy.data.objects if o.data] + \
              [k for k in bpy.data.shape_keys] + [m.node_tree for m in bpy.data.materials if m.node_tree] + \
              [w.node_tree for w in bpy.data.worlds]
        for idb in ids:
            ad = getattr(idb, 'animation_data', None)
            if not ad or not ad.action:
                continue
            for fc in U.fcurves_of(ad):
                kps = fc.keyframe_points
                frames_ = [k.co.x for k in kps]
                for i in range(len(kps) - 1):
                    a, b = frames_[i], frames_[i + 1]
                    for bb in bset:
                        if a < bb <= b:
                            kps[i].interpolation = 'CONSTANT'
                            break
                if fc.data_path in ('hide_render',) or 'Emission' in fc.data_path:
                    for k in kps:
                        k.interpolation = 'CONSTANT'

    def common(self, f0, f1, chars, seed=0):
        for i, chh in enumerate(chars):
            A.blinks(chh, f0, f1, seed=seed + i)
            A.tassel_sway(chh, f0, f1)

    # ============================================================== SHOTS
    # ---- 01 THE TWO SISTERS
    def cu(self, sid, ch, f0, f1, d0=0.7, d1=0.58, ang=0.3, dz=0.02, lens=50, fstop=2.0, side=0.0, shake=0.0, tz=-0.02):
        e0, h = self.front(ch, f0, d0, ang, dz, side)
        e1, _ = self.front(ch, f0, d1, ang, dz, side)
        t = h + Vector((0, 0, tz))
        return self.cam(sid, f0, f1, e0, t, e1, t, lens=lens, focus=(ch, 'head'), fstop=fstop, shake=shake)

    def s01(self, f0, f1):
        hx, hy = E.HOME_DOOR
        self.cam('S01', f0, f1, (hx + 6, 9.0, 15.0), (hx, -3.0, 4.0), (hx + 3.5, 5.0, 2.4), (hx, -3.0, 1.6), lens=28, fstop=8)
        self.car_drive('Taxi', f0, f1, -40, -8, 5.2)
        self.car_drive('Sedan', f0, f1, 5, -30, 1.8)
        self.place(self.neighbour, f0, (hx + 8, -1.4), FACE_NX, HZ)
        self.walk(self.neighbour, f0, f1, [(hx + 9, -1.4), (hx + 4.5, -1.4)])

    def _living_sit(self, f0):
        hi, hu = self.hind, self.huda
        self.place(hi, f0, (102.55, 2.15), FACE_X - 0.5, -(hi.dims['zh'] - 0.07))
        A.pose(hi, f0, A.SIT_FLOOR)
        self.place(hu, f0, (103.45, 2.65), FACE_NX - 0.4, -(hu.dims['zh'] - 0.07))
        A.pose(hu, f0, A.SIT_FLOOR)

    def s02(self, f0, f1):
        hi, hu = self.hind, self.huda
        self._living_sit(f0)
        A.expr(hi, f0, 'happy'); A.expr(hu, f0, 'smile')
        # Huda builds a little tower, Hind claps / laughs
        A.kb(hu, 'upperarm.R', f0 + 20, rot=(-0.9, 0, 0.1)); A.kb(hu, 'forearm.R', f0 + 20, rot=(-0.6, 0, 0))
        A.kb(hu, 'upperarm.R', f0 + 70, rot=(-0.6, 0, 0.1))
        A.expr(hi, f0 + 60, 'laugh'); A.expr(hu, f0 + 75, 'laugh'); A.expr(hi, f1, 'smile')
        for f in range(f0 + 60, f0 + 110, 8):
            A.kb(hi, 'spine', f, rot=(0.25 + 0.06 * ((f // 8) % 2), 0, 0))
        A.look(hi, f0, 0.3, -0.25); A.look(hu, f0, -0.3, -0.3)
        A.look(hi, f0 + 60, 0.35, 0.1); A.look(hu, f0 + 75, -0.4, 0.05)
        self.obj_key(self.rabbit_free, f0, loc=(102.25, 1.85, 0.0), rot=(0, 0, -0.6))
        self.common(f0, f1, [hi, hu], 2)
        self.cam('S02', f0, f1, (104.9, 0.25, 1.35), (103.0, 2.4, 0.35), (104.4, 0.75, 1.05), (103.0, 2.4, 0.4), lens=26,
                 focus=(hi, 'head'), fstop=4)

    def s03(self, f0, f1):
        hi, hu = self.hind, self.huda
        self._living_sit(f0)
        A.pose(hi, f0, A.SIT_FLOOR, A.HOLD_RABBIT)
        self.vis(self.rabbit_held, f0, True)
        A.expr(hi, f0, 'smile'); A.expr(hi, f0 + 50, 'happy')
        A.look(hi, f0, -0.15, 0.05, tilt=0.08); A.look(hi, f0 + 60, -0.05, 0.12, tilt=0.12)
        A.breathe(hi, f0, f1, spine_base=(0.2, 0, 0))
        self.common(f0, f1, [hi, hu], 3)
        self.cu('S03', hi, f0, f1, 0.95, 0.8, ang=0.35, dz=0.0, lens=50, tz=-0.1)
    def s04(self, f0, f1):
        hi, hu = self.hind, self.huda
        self._living_sit(f0)
        A.expr(hu, f0, 'gentle'); A.expr(hu, f0 + 45, 'smile')
        A.look(hu, f0, 0.25, -0.1); A.look(hu, f0 + 40, 0.1, 0.1, tilt=-0.06)
        A.breathe(hu, f0, f1, spine_base=(0.2, 0, 0))
        self.common(f0, f1, [hi, hu], 4)
        self.cu('S04', hu, f0, f1, 0.95, 0.8, ang=-0.3, dz=0.02, lens=50, tz=-0.08)
    def s05(self, f0, f1):
        hi, hu = self.hind, self.huda
        self.place(hu, f0, (103.7, 3.0), FACE_NX, 0); self.place(hi, f0, (104.6, 3.3), FACE_NX, 0)
        A.expr(hu, f0, 'happy'); A.expr(hi, f0, 'happy')
        self.walk(hu, f0, f1, [(103.7, 3.0), (102.2, 2.2), (101.3, 1.2)])
        self.walk(hi, f0 + 10, f1, [(104.6, 3.3), (103.3, 2.7), (102.2, 1.85)])
        A.look(hi, f0, 0, 0.15, head=False)
        self.common(f0, f1, [hi, hu], 5)
        self.cam('S05', f0, f1, (104.6, 0.4, 1.0), (103.3, 2.9, 0.7), (102.6, 0.3, 0.95), (101.9, 2.0, 0.65), lens=24,
                 focus=(hu, 'head'), fstop=4)

    def s06(self, f0, f1):
        hi, hu = self.hind, self.huda
        self.place(hi, f0, (103.0, 1.7), FACE_Y, 0); self.place(hu, f0, (103.0, 3.15), FACE_NY, 0)
        A.expr(hi, f0, 'laugh'); A.expr(hu, f0, 'laugh')
        catch = A.P(upperarm_L=(-1.0, 0, 0.1), upperarm_R=(-1.0, 0, -0.1), forearm_L=(-0.5, 0, 0.3), forearm_R=(-0.5, 0, -0.3))
        throw = A.P(upperarm_L=(-1.6, 0, 0.1), upperarm_R=(-1.6, 0, -0.1), forearm_L=(-0.2, 0, 0.2), forearm_R=(-0.2, 0, -0.2))
        mid = (f0 + f1) // 2
        A.pose(hu, f0, throw); A.pose(hi, f0, catch)
        A.pose(hu, f0 + 12, catch); A.pose(hi, mid - 6, catch); A.pose(hi, mid + 6, throw); A.pose(hu, f1 - 4, catch)
        bh = 0.72
        pts = [(f0, (103.0, 2.9, bh + 0.3)), (f0 + (mid - f0) // 2, (103.0, 2.45, 1.3)), (mid, (103.0, 1.95, bh)),
               (mid + 6, (103.0, 1.95, bh + 0.1)), (mid + 6 + (f1 - mid - 6) // 2, (103.0, 2.45, 1.4)), (f1, (103.0, 2.9, bh + 0.2))]
        for f, p in pts:
            self.obj_key(self.ball, f, loc=p)
        for chh in (hi, hu):
            for f in range(f0, f1, 10):
                A.kb(chh, 'spine', f, rot=(0.05 * ((f // 10) % 2), 0, 0))
        self.common(f0, f1, [hi, hu], 6)
        self.cam('S06', f0, f1, (105.75, 2.3, 0.5), (103.0, 2.45, 0.85), (105.6, 2.55, 0.55), (103.0, 2.45, 0.85), lens=20,
                 focus=self.ball, fstop=4)
    def s07(self, f0, f1):
        hi, hu = self.hind, self.huda
        self.place(hi, f0, (103.0, 2.08), FACE_Y, 0); self.place(hu, f0, (103.0, 2.74), FACE_NY, 0)
        A.pose(hi, f0, A.TUG); A.pose(hu, f0, A.TUG)
        A.expr(hi, f0, 'pout'); A.expr(hu, f0, 'worried', 0.6); A.expr(hu, f0 + 40, 'pout', 0.7)
        for i, f in enumerate(range(f0, f1, 9)):
            d = 0.05 * (1 if i % 2 else -1)
            self.obj_key(self.toycar, f, loc=(103.0, 2.41 + d, 0.64), rot=(0, 0, 0))
            A.kb(hi, 'spine', f, rot=(-0.15 - (0.08 if d < 0 else 0), 0, 0)); A.kb(hu, 'spine', f, rot=(-0.15 - (0.08 if d > 0 else 0), 0, 0))
        self.common(f0, f1, [hi, hu], 7)
        self.cam('S07', f0, f1, (104.45, 2.0, 0.95), (103.0, 2.4, 0.8), (104.25, 2.15, 0.9), (103.0, 2.4, 0.8), lens=32,
                 focus=self.toycar, fstop=3.2)
    def s08(self, f0, f1):
        hi, hu = self.hind, self.huda
        self.place(hi, f0, (103.0, 2.12), FACE_Y, 0); self.place(hu, f0, (103.0, 2.66), FACE_NY, 0)
        A.pose(hu, f0, A.GIVE_COINS); A.expr(hu, f0, 'gentle'); A.expr(hi, f0, 'pout', 0.6)
        self.obj_key(self.toycar, f0, loc=(103.03, 2.4, 0.7), rot=(0, 0, 0))
        self.obj_key(self.toycar, f0 + 25, loc=(103.0, 2.3, 0.6), rot=(0, 0, 0))
        A.pose(hi, f0 + 25, A.HOLD_RABBIT)
        A.pose(hu, f0 + 35, A.HUG); A.pose(hi, f0 + 40, A.HUG)
        A.expr(hi, f0 + 30, 'laugh'); A.expr(hu, f0 + 32, 'smile')
        self.place(hu, f0 + 35, (103.0, 2.44), FACE_NY, 0)
        A.kb(hi, 'head', f0 + 45, rot=(0.1, 0, 0.2)); A.kb(hu, 'head', f0 + 45, rot=(0.25, 0, -0.15))
        self.common(f0, f1, [hi, hu], 8)
        self.cam('S08', f0, f1, (104.35, 1.55, 1.05), (103.0, 2.35, 0.85), (104.2, 1.75, 1.0), (103.0, 2.35, 0.85), lens=34,
                 focus=(hi, 'head'), fstop=2.8)
    def s09(self, f0, f1):
        mo = self.mother
        self.place(mo, f0, (106.9, 4.0), FACE_Y, 0)
        A.pose(mo, f0, A.COOK); A.expr(mo, f0, 'gentle')
        for i, f in enumerate(range(f0, f1, 10)):
            A.kb(mo, 'forearm.R', f, rot=(-1.2, 0, -0.4 + 0.25 * math.sin(i * 1.3)))
        A.breathe(mo, f0, f1, spine_base=(0.12, 0, 0))
        self.steam_anim(f0, f1, Vector((106.85, 4.6, 1.15)))
        self.common(f0, f1, [mo], 9)
        self.cam('S09', f0, f1, (108.3, 2.6, 1.65), (106.9, 4.5, 1.15), (107.85, 3.0, 1.55), (106.9, 4.5, 1.15), lens=30,
                 focus=(mo, 'head'), fstop=3.5)

    def steam_anim(self, f0, f1, base):
        rnd = random.Random(4)
        for i, s in enumerate(self.steam):
            off = (i / len(self.steam)) * 30
            for k, f in enumerate(range(f0, f1 + 1, 6)):
                t = ((f - f0 + off) % 30) / 30
                self.obj_key(s, f, loc=base + Vector((0.03 * math.sin(i + t * 4), 0.02 * math.cos(i * 2 + t * 3), t * 0.45)),
                             scale=(0.6 + t * 1.6,) * 3)

    def s10(self, f0, f1):
        mo = self.mother
        self.place(mo, f0, (108.65, 3.95), FACE_Y, 0)
        A.pose(mo, f0, A.P(spine=(0.25, 0, 0), neck=(0.3, 0, 0)))
        A.pose(mo, f0 + 30, A.P(spine=(0.35, 0, 0), neck=(0.35, 0, 0), upperarm_R=(-1.0, 0, -0.25), forearm_R=(-0.4, 0, 0)))
        A.expr(mo, f0, 'neutral'); A.expr(mo, f0 + 45, 'worried')
        A.look(mo, f0 + 45, -0.3, -0.3)
        self.common(f0, f1, [mo], 10)
        self.cam('S10', f0, f1, (109.95, 3.55, 1.6), (109.25, 4.5, 0.95), (109.85, 3.7, 1.5), (109.25, 4.5, 0.95), lens=32,
                 focus=bpy.data.objects['k_basket'], fstop=2.4)
    def s11(self, f0, f1):
        mo, hu, hi = self.mother, self.huda, self.hind
        self.place(mo, f0, (107.35, 2.2), FACE_NX, 0)
        A.expr(mo, f0, 'talk'); A.talk(mo, f0 + 5, f0 + 70, seed=11)
        A.look(mo, f0, -0.3, 0.0)
        self.place(hu, f0, (104.9, 2.25), FACE_X, 0)
        self.walk(hu, f0, f0 + 45, [(104.9, 2.25), (106.65, 2.2)])
        self.place(hi, f0, (104.6, 2.6), FACE_X, 0)
        self.walk(hi, f0 + 10, f0 + 55, [(104.4, 2.6), (105.85, 2.55)])
        A.pose(hi, f0 + 56, A.HOLD_RABBIT); self.vis(self.rabbit_held, f0, True)
        A.pose(mo, f0 + 50, A.GIVE_COINS); self.vis(self.note_mother, f0 + 50, True); self.vis(self.note_mother, f0 + 82, False)
        A.pose(hu, f0 + 60, A.TAKE_COINS); A.pose(hu, f0 + 82, A.TAKE_COINS, A.P(forearm_L=(-1.2, 0, 0)))
        self.vis(self.note_huda, f0 + 82, True)
        A.pose(mo, f0 + 90)
        A.expr(hu, f0 + 40, 'smile'); A.look(hu, f0 + 40, 0, 0.35); A.expr(hi, f0 + 50, 'happy'); A.look(hi, f0 + 50, 0.2, 0.3)
        self.common(f0, f1, [mo, hu, hi], 11)
        self.cam('S11', f0, f1, (106.2, 0.35, 1.5), (106.5, 2.3, 1.15), (106.5, 0.4, 1.45), (106.8, 2.3, 1.15), lens=20,
                 focus=(hu, 'head'), fstop=3.2)

    # ---- 02 THE PROMISE
    def s12(self, f0, f1):
        hu, hi = self.huda, self.hind
        hx, hy = E.HOME_DOOR
        self.obj_key(self.home_door, f0, rot=(0, 0, 0)); self.obj_key(self.home_door, f0 + 20, rot=(0, 0, 1.6))
        self.place(hu, f0, (hx, -3.3), FACE_Y, HZ)
        self.walk(hu, f0 + 10, f1, [(hx, -3.3), (hx, -2.0), (hx + 2.2, -1.4)])
        A.pose(hu, f0, A.P(upperarm_L=(-0.3, 0, -0.1), forearm_L=(-0.9, 0, 0.2))); self.vis(self.note_huda, f0, True)
        self.place(hi, f0, (hx, -3.6), FACE_Y, HZ)
        self.walk(hi, f0 + 40, f1, [(hx, -3.6), (hx - 0.1, -2.4), (hx + 1.2, -1.75)], carry='R')
        A.pose(hi, f0, A.HOLD_RABBIT); A.pose(hi, f0 + 40, A.HOLD_RABBIT, base={})
        self.vis(self.rabbit_held, f0, True)
        A.expr(hu, f0, 'smile'); A.expr(hi, f0, 'happy')
        self.common(f0, f1, [hu, hi], 12)
        self.cam('S12', f0, f1, (hx + 3.2, 1.6, 1.3), (hx, -2.6, 1.0), (hx + 3.8, 1.2, 1.2), (hx + 1.2, -2.0, 0.9), lens=30,
                 focus=(hu, 'head'), fstop=4)

    def s13(self, f0, f1):
        hu, hi = self.huda, self.hind
        x0, x1 = -15.5, -11.2
        self.place(hu, f0, (x0, -1.5), FACE_X, HZ); self.place(hi, f0, (x0 - 0.25, -0.9), FACE_X, HZ)
        self.walk(hu, f0, f1, [(x0, -1.5), (x1, -1.5)], carry='L')
        self.walk(hi, f0, f1, [(x0 - 0.25, -0.9), (x1 - 0.25, -0.9)], carry='R')
        A.pose(hi, f0, A.HOLD_RABBIT, base={}); self.vis(self.rabbit_held, f0, True)
        A.pose(hu, f0, A.P(upperarm_L=(-0.3, 0, -0.1), forearm_L=(-0.9, 0, 0.2)), base={}); self.vis(self.note_huda, f0, True)
        A.expr(hu, f0, 'smile'); A.expr(hi, f0, 'happy')
        A.look(hi, f0 + 40, 0.5, 0.25); A.look(hu, f0 + 60, -0.4, -0.1)
        self.car_drive('Taxi', f0, f1, -30, 10, 6.1)
        self.car_drive('Sedan2', f0, f1, 20, -25, 4.4)
        self.common(f0, f1, [hu, hi], 13)
        self.cam('S13', f0, f1, (x0 + 0.6, 1.4, 0.95), (x0 + 0.3, -1.45, 0.75), (x1 + 0.6, 1.4, 0.95), (x1 + 0.3, -1.45, 0.75), lens=30,
                 focus=(hu, 'head'), fstop=3.5)

    def s14(self, f0, f1):
        hu, hi = self.huda, self.hind
        self.place(hu, f0, (-4.8, -0.6), FACE_X, HZ); self.place(hi, f0, (-5.3, -1.1), FACE_X, HZ)
        self.walk(hu, f0, f0 + 85, [(-4.8, -0.6), (-1.45, -0.4)], carry='L')
        self.walk(hi, f0, f0 + 95, [(-5.3, -1.1), (-1.0, -0.55)], carry='R')
        A.pose(hi, f0, A.HOLD_RABBIT, base={}); self.vis(self.rabbit_held, f0, True)
        A.pose(hu, f0 + 86, A.HOLD_HAND_L, A.P(upperarm_R=(0.05, 0, 0.1)))
        A.kb(hu, 'root', f0 + 100, rot=(0, 0, FACE_Y + 0.6)); A.kb(hi, 'root', f0 + 100, rot=(0, 0, FACE_Y - 0.3))
        A.pose(hi, f0 + 96, A.HOLD_RABBIT)
        A.expr(hu, f0 + 80, 'neutral'); A.look(hu, f0 + 90, -0.6, 0.0)
        self.car_drive('Sedan', f0, f1, -30, 15, 1.8)
        self.car_drive('Taxi', f0 + 30, f1, 25, -15, 5.2)
        self.common(f0, f1, [hu, hi], 14)
        self.cam('S14', f0, f1, (-4.2, -2.75, 1.9), (-0.5, 9.0, 1.4), (-3.2, -2.7, 1.6), (0.0, 9.0, 1.4), lens=24,
                 focus_dist=9.0, fstop=5.6)

    def _curb_pair(self, f0, huda_face=FACE_X, hind_face=FACE_NX):
        hu, hi = self.huda, self.hind
        self.place(hu, f0, (-1.55, -0.45), huda_face, HZ); self.place(hi, f0, (-0.95, -0.5), hind_face, HZ)

    def s15(self, f0, f1):
        hu, hi = self.huda, self.hind
        self._curb_pair(f0)
        A.pose(hi, f0, A.HOLD_RABBIT); self.vis(self.rabbit_held, f0, True)
        point = A.P(upperarm_L=(-0.35, 0, -1.35), forearm_L=(-0.1, 0, 0), fingers_L=(0, 0, 1.2), pinky_L=(0, 0, 1.2))
        A.pose(hu, f0 + 10, point, A.P(spine=(0.15, 0, 0)))
        A.look(hu, f0 + 10, 0.9, 0.0, head_amt=0.6); A.look(hu, f0 + 60, 0.0, -0.25, head_amt=0.5)
        A.expr(hu, f0, 'worried', 0.7); A.talk(hu, f0 + 15, f1 - 10, seed=15, rate=3.5)
        A.look(hi, f0 + 20, -0.9, 0.0); A.look(hi, f0 + 70, 0.0, 0.3)
        A.expr(hi, f0, 'neutral'); A.expr(hi, f0 + 60, 'worried', 0.5)
        self.car_drive('Taxi', f0 + 5, f0 + 70, -25, 20, 2.7)
        self.car_drive('Van', f0 + 40, f1, 25, -20, 5.2)
        self.common(f0, f1, [hu, hi], 15)
        self.cam('S15', f0, f1, (-1.25, 1.25, 0.95), (-1.25, -0.45, 0.95), (-1.25, 1.05, 0.95), (-1.25, -0.45, 0.95), lens=34,
                 focus=(hu, 'head'), fstop=2.8)

    def s16(self, f0, f1):
        hu, hi = self.huda, self.hind
        self._curb_pair(f0)
        A.pose(hi, f0, A.HOLD_RABBIT); self.vis(self.rabbit_held, f0, True)
        A.pose(hu, f0, A.P(spine=(0.3, 0, 0), neck=(0.15, 0, 0), upperarm_L=(-0.6, 0, -0.1), forearm_L=(-0.8, 0, 0.3)))
        A.expr(hu, f0, 'gentle'); A.talk(hu, f0 + 5, f1 - 15, seed=16, rate=3.6)
        A.look(hu, f0, 0, -0.35)
        A.expr(hi, f0, 'worried', 0.5); A.look(hi, f0, 0, 0.4)
        self.common(f0, f1, [hu, hi], 16)
        self.cu('S16', hu, f0, f1, 0.85, 0.72, ang=0.45, dz=-0.05, lens=50)

    def s17(self, f0, f1):
        hu, hi = self.huda, self.hind
        self._curb_pair(f0)
        A.pose(hi, f0, A.CLUTCH_RABBIT); self.vis(self.rabbit_held, f0, True)
        A.pose(hu, f0, A.P(spine=(0.3, 0, 0), neck=(0.15, 0, 0)))
        A.expr(hi, f0, 'pout'); A.expr(hi, f0 + 35, 'sad')
        A.look(hi, f0, 0, 0.35); A.look(hi, f0 + 30, 0.25, -0.45, head_amt=0.7)
        self.common(f0, f1, [hu, hi], 17)
        self.cu('S17', hi, f0, f1, 0.8, 0.68, ang=-0.6, dz=0.08, lens=50)

    def s18(self, f0, f1):
        hu, hi = self.huda, self.hind
        self._curb_pair(f0)
        A.pose(hi, f0, A.HOLD_RABBIT); self.vis(self.rabbit_held, f0, True)
        A.pose(hu, f0, A.P(spine=(0.3, 0, 0), neck=(0.1, 0, 0)))
        A.pose(hu, f0 + 30, A.PINKY_OUT_R, A.P(spine=(0.35, 0, 0), neck=(0.1, 0, 0)))
        A.expr(hu, f0, 'smile'); A.look(hu, f0, 0, -0.35)
        A.expr(hi, f0, 'sad', 0.7); A.look(hi, f0, 0.1, -0.2)
        A.look(hi, f0 + 40, 0, 0.35); A.expr(hi, f0 + 55, 'happy', 0.7)
        A.pose(hi, f0 + 60, A.HOLD_RABBIT, A.PINKY_OUT_L)
        self.common(f0, f1, [hu, hi], 18)
        self.cam('S18', f0, f1, (-1.25, 1.15, 0.85), (-1.25, -0.47, 0.88), (-1.25, 1.0, 0.82), (-1.25, -0.47, 0.82), lens=45,
                 focus=(hi, 'head'), fstop=2.4)

    def s19(self, f0, f1):
        hu, hi = self.huda, self.hind
        self._curb_pair(f0)
        A.pose(hu, f0, A.P(spine=(0.35, 0, 0)))
        A.pose(hi, f0, A.HOLD_RABBIT); self.vis(self.rabbit_held, f0, True)
        A.expr(hu, f0, 'smile'); A.expr(hi, f0, 'happy')
        c = Vector((-1.25, -0.47, 0.8))
        hd, hn = self.hp['huda'], self.hp['hind']
        self.park(hu, f0); self.park(hi, f0); self.vis(self.rabbit_held, f0, False)   # macro: only the two hands
        # Huda's fist from the left, Hind's (smaller) from the right; little fingers meet and hook.
        self.obj_key(hd['root'], f0, loc=c + Vector((-0.2, 0.007, 0.012)), rot=(0, 0, 0.0))
        self.obj_key(hd['root'], f0 + 38, loc=c + Vector((-0.086, 0.007, 0.0)), rot=(0, 0, 0.0))
        self.obj_key(hn['root'], f0, loc=c + Vector((0.2, -0.007, -0.01)), rot=(0, 0, PI))
        self.obj_key(hn['root'], f0 + 38, loc=c + Vector((0.078, -0.007, -0.004)), rot=(0, 0, PI))
        for h in (hd, hn):
            self.obj_key(h['pinky'], f0, rot=(0, 0.15, 0))
            self.obj_key(h['pinky'], f0 + 36, rot=(0, 0.05, 0))
            self.obj_key(h['pinky'], f0 + 52, rot=(0, -0.75, 0))
        for f, dz in ((f0 + 70, 0.006), (f0 + 88, -0.003), (f0 + 106, 0.004), (f1, 0.0)):
            self.obj_key(hd['root'], f, loc=c + Vector((-0.086, 0.007, dz)))
            self.obj_key(hn['root'], f, loc=c + Vector((0.078, -0.007, dz - 0.004)))
        cam = self.cam('S19', f0, f1, c + Vector((-0.004, 0.52, 0.03)), c + Vector((-0.004, 0, -0.012)),
                       c + Vector((-0.004, 0.34, 0.0)), c + Vector((-0.004, 0, -0.015)), lens=50, fstop=4.0)
        self.focus_pull(cam, f0, 0.52, f1, 0.34)
    def s20(self, f0, f1):
        hu, hi = self.huda, self.hind
        self.place(hi, f0, (-0.95, -0.5), FACE_Y, HZ)
        A.pose(hi, f0, A.HOLD_RABBIT); self.vis(self.rabbit_held, f0, True)
        self.place(hu, f0, (-1.5, -0.25), FACE_Y, HZ)
        A.look(hu, f0 + 5, 0.9, 0.0, head_amt=0.7); A.look(hu, f0 + 22, -0.9, 0.0, head_amt=0.7); A.look(hu, f0 + 38, 0, 0)
        self.walk(hu, f0 + 40, f1, [(-1.5, -0.25), (-0.9, 3.5), (-0.3, 6.6)], carry='L')
        A.expr(hi, f0, 'neutral'); A.look(hi, f0 + 40, 0, 0.1)
        self.common(f0, f1, [hu, hi], 20)
        self.cam('S20', f0, f1, (-1.55, -1.7, 0.78), (-0.6, 6.0, 0.95), (-1.5, -1.6, 0.8), (-0.4, 7.0, 1.0), lens=30,
                 focus=(hu, 'head'), fstop=3.5)

    def s21(self, f0, f1):
        hu, sk = self.huda, self.shopkeeper
        self.place(sk, f0, (1.0, 11.0), FACE_NX, HZ)
        self.place(hu, f0, (0.25, 10.95), FACE_X, HZ)
        A.pose(sk, f0, A.P(upperarm_R=(-0.7, 0, 0.1), forearm_R=(-0.9, 0, 0)))
        A.pose(sk, f0 + 45, A.GIVE_COINS); self.vis(self.bag_shop, f0, True); self.vis(self.bag_shop, f0 + 70, False)
        A.pose(hu, f0 + 55, A.TAKE_COINS); A.pose(hu, f0 + 70, A.CARRY_BAG_L); self.vis(self.bag_huda, f0 + 70, True)
        A.expr(sk, f0, 'smile'); A.talk(sk, f0 + 5, f0 + 40, seed=21)
        A.expr(hu, f0, 'smile'); A.look(hu, f0, 0.2, 0.35)
        self.common(f0, f1, [hu, sk], 21)
        self.cam('S21', f0, f1, (-1.5, 12.9, 1.55), (0.6, 10.95, 1.0), (-1.3, 12.6, 1.5), (0.6, 10.95, 1.0), lens=30,
                 focus=(hu, 'head'), fstop=2.8)

    def s22(self, f0, f1):
        hu, hi = self.huda, self.hind
        self.place(hi, f0, (-0.95, -0.5), FACE_Y, HZ); A.pose(hi, f0, A.HOLD_RABBIT); self.vis(self.rabbit_held, f0, True)
        self.place(hu, f0, (0.2, 9.8), FACE_NY, HZ)
        self.walk(hu, f0, f0 + 40, [(0.2, 9.8), (0.05, 8.2)], carry='L')
        A.pose(hu, f0 + 40, A.CARRY_BAG_L); self.vis(self.bag_huda, f0, True)
        A.wave(hu, f0 + 45, f1, 'R') if False else None
        up = A.P(upperarm_R=(-0.3, 0, 2.3))
        for i, f in enumerate(range(f0 + 45, f1, 6)):
            A.kb(hu, 'upperarm.R', f, rot=(-0.3, 0, 2.3)); A.kb(hu, 'forearm.R', f, rot=(-0.3, 0, -0.45 * math.sin(i * 1.4)))
        A.expr(hu, f0, 'smile'); A.expr(hu, f0 + 45, 'laugh')
        self.common(f0, f1, [hu, hi], 22)
        self.cam('S22', f0, f1, (-1.6, -1.35, 1.2), (0.05, 8.2, 1.1), (-1.55, -1.25, 1.2), (0.05, 8.2, 1.15), lens=70,
                 focus=(hu, 'head'), fstop=2.8)

    def s23(self, f0, f1):
        hu, hi = self.huda, self.hind
        self.place(hi, f0, (-0.95, -0.5), FACE_Y, HZ); A.pose(hi, f0, A.HOLD_RABBIT); self.vis(self.rabbit_held, f0, True)
        self.place(hu, f0, (0.05, 8.2), FACE_NY, HZ); A.pose(hu, f0, A.CARRY_BAG_L); self.vis(self.bag_huda, f0, True)
        A.wave(hi, f0 + 8, f1, 'L')
        A.expr(hi, f0, 'happy'); A.expr(hi, f0 + 12, 'laugh')
        A.look(hi, f0, 0.1, 0.12)
        self.common(f0, f1, [hu, hi], 23)
        self.cu('S23', hi, f0, f1, 1.2, 1.05, ang=0.3, dz=0.0, lens=40, fstop=2.4, tz=-0.15)

    def s24(self, f0, f1):
        hu, hi = self.huda, self.hind
        self.place(hi, f0, (-0.95, -0.5), FACE_Y, HZ); A.pose(hi, f0, A.HOLD_RABBIT); self.vis(self.rabbit_held, f0, True)
        A.wave(hi, f0, f0 + 20, 'L'); A.pose(hi, f0 + 26, A.HOLD_RABBIT)
        A.expr(hi, f0, 'laugh')
        self.place(hu, f0, (0.05, 8.2), FACE_NY, HZ); A.pose(hu, f0, A.CARRY_BAG_L); self.vis(self.bag_huda, f0, True)
        self.walk(hu, f0 + 4, f1, [(0.05, 8.2), (-0.1, 6.6)], carry='L')
        self.car_drive('Van', f0 + 6, f1, -14, 10, 1.9)
        self.cam('S24', f0, f1, (-1.05, -1.75, 0.95), (-0.4, 7.5, 1.0), lens=35, focus=(hu, 'head'), fstop=4)

    def s25(self, f0, f1):
        hi = self.hind
        self.place(hi, f0, (-0.95, -0.5), FACE_Y, HZ); A.pose(hi, f0, A.HOLD_RABBIT); self.vis(self.rabbit_held, f0, True)
        A.expr(hi, f0, 'happy'); A.expr(hi, f0 + 10, 'shock')
        A.kb(hi, 'spine', f0 + 10, rot=(-0.08, 0, 0)); A.kb(hi, 'neck', f0 + 10, rot=(-0.1, 0, 0))
        A.look(hi, f0, 0, 0.1); A.look(hi, f0 + 12, 0.15, 0.08, head_amt=0.3)
        self.car_drive('Van', f0, f1, 10, 22, 1.9)
        self.cu('S25', hi, f0, f1, 0.9, 0.62, ang=0.0, dz=0.0, lens=50, shake=0.006)

    def crowd_ring(self, f, n=6, c=(-0.3, 4.8), r=0.95, walk_from=None, f_end=None, seed=0):
        rnd = random.Random(seed)
        for i, chh in enumerate(self.crowd[:n]):
            a = 2 * PI * i / n + 0.3
            p = (c[0] + math.cos(a) * r * rnd.uniform(0.9, 1.25), c[1] + math.sin(a) * r * rnd.uniform(0.9, 1.25))
            face = A.face_dir(c[0] - p[0], c[1] - p[1])
            if walk_from:
                st = (p[0] + math.cos(a) * 3.2, p[1] + math.sin(a) * 2.6)
                self.place(chh, f, st, face, self.ground(*st))
                self.walk(chh, f + rnd.randint(0, 12), f_end - rnd.randint(0, 10), [st, p], run=True)
                A.kb(chh, 'root', f_end, rot=(0, 0, face))
            else:
                self.place(chh, f, p, face, 0)
            A.pose(chh, f_end or f, A.P(spine=(0.3, 0, 0), neck=(0.25, 0, 0)))
            A.expr(chh, f, 'worried')

    def s26(self, f0, f1):
        self.crowd_ring(f0, 5, walk_from=True, f_end=f1, seed=26)
        self.car_hold('Sedan2', f0, (1.6, 5.4, 0), PI + 0.35)
        self.cam('S26', f0, f1, (-2.3, 0.4, 0.22), (-0.3, 4.8, 1.0), (-2.2, 0.45, 0.24), (-0.3, 4.8, 0.95), lens=22,
                 focus_dist=4.8, fstop=4, shake=0.01)

    def s27(self, f0, f1):
        hi = self.hind
        self.place(hi, f0, (-0.95, -0.5), FACE_Y, HZ); A.pose(hi, f0, A.HOLD_RABBIT)
        self.vis(self.rabbit_held, f0, True); self.vis(self.rabbit_held, f0 + 6, False)
        A.pose(hi, f0 + 12, A.P(upperarm_R=(-0.25, 0, 0.12), forearm_R=(-0.6, 0, 0), fingers_R=(0, 0, 0.1)))
        A.expr(hi, f0, 'shock')
        hp = self.bone_world(hi, 'hand.R', f0 + 6, 0.05)
        top = Vector((hp.x, hp.y - 0.05, hp.z - 0.06)); bot = Vector((-0.86, -0.62, HZ))
        self.obj_key(self.rabbit_free, f0 + 6, loc=top, rot=(0, 0, PI - 0.2))
        n = f1 - f0 - 6
        for k in range(1, 9):
            t = k / 8
            p = top.lerp(bot, t); p.z = top.z + (bot.z - top.z) * (t ** 1.6)
            if k == 8:
                p = bot
            self.obj_key(self.rabbit_free, f0 + 6 + int(n * 0.75 * t), loc=p, rot=(0.25 * t, 0.9 * t, PI - 0.2 + 0.4 * t))
        self.obj_key(self.rabbit_free, f1, loc=bot, rot=(0.25, 1.35, PI + 0.2))
        self.cam('S27', f0, f1, (-0.55, -0.05, 0.42), (-0.9, -0.55, 0.32), (-0.58, -0.08, 0.38), (-0.88, -0.6, 0.25), lens=40,
                 focus=self.rabbit_free, fstop=2.0)

    def _crowd_static(self, f0, f1, seed=28, n=6):
        self.crowd_ring(f0, n, seed=seed)
        for i, chh in enumerate(self.crowd[:n]):
            A.breathe(chh, f0, f1, seed=i, spine_base=(0.3, 0, 0))
            A.look(chh, f0 + 10 * i, 0.2 * math.sin(i), -0.4)
        self.car_hold('Sedan2', f0, (1.6, 5.4, 0), PI + 0.35)

    def _hind_waiting(self, f0, expr='fear', held=False):
        hi = self.hind
        self.place(hi, f0, (-0.95, -0.5), FACE_Y, HZ)
        if held:
            A.pose(hi, f0, A.HOLD_RABBIT); self.vis(self.rabbit_held, f0, True)
        else:
            A.pose(hi, f0, A.P(upperarm_R=(-0.25, 0, 0.12), forearm_R=(-0.6, 0, 0), fingers_R=(0, 0, 0.1)))
            self.obj_key(self.rabbit_free, f0, loc=(-0.86, -0.62, HZ), rot=(0.25, 1.35, PI + 0.2))
        A.expr(hi, f0, expr)

    def s28(self, f0, f1):
        self._crowd_static(f0, f1)
        self._hind_waiting(f0)
        self.cam('S28', f0, f1, (-1.0, -0.3, 0.92), (-0.4, 4.8, 0.95), (-0.95, 0.05, 0.9), (-0.35, 4.8, 0.95), lens=32,
                 focus_dist=5.0, fstop=3.2, shake=0.004)

    def s29(self, f0, f1):
        self._crowd_static(f0, f1, n=5)
        w = self.ch['Woman1']
        self.place(w, f0, (-1.4, 3.85), FACE_NY + 0.3, 0)
        A.pose(w, f0, A.HANDS_ON_HEAD); A.expr(w, f0, 'shock')
        A.talk(w, f0 + 4, f1 - 4, base='shock', rate=5, seed=29)
        A.expr(w, f0 + 4, 'shock')
        h = self.head(w, f0)
        self.cam('S29', f0, f1, h + Vector((0.5, -1.6, -0.25)), h, h + Vector((0.42, -1.35, -0.2)), h, lens=45,
                 focus=(w, 'head'), fstop=2.8, shake=0.006)

    def s30(self, f0, f1):
        self._crowd_static(f0, f1)
        hi = self.hind
        self._hind_waiting(f0, 'fear')
        self.walk(hi, f0 + 10, f0 + 60, [(-0.95, -0.5), (-0.75, -0.2)], step_len=0.25)
        for f, lean in ((f0 + 65, 0.2), (f0 + 85, -0.2), (f0 + 105, 0.25)):
            A.kb(hi, 'spine', f, rot=(0.05, 0, lean)); A.kb(hi, 'foot.L', f, rot=(-0.4, 0, 0)); A.kb(hi, 'foot.R', f, rot=(-0.4, 0, 0))
            A.kb(hi, 'root', f, loc=(-0.75, -0.2, HZ + 0.03))
        self.cam('S30', f0, f1, (-1.35, -1.3, 0.75), (-0.35, 4.8, 0.85), (-1.25, -1.1, 0.72), (-0.35, 4.8, 0.8), lens=30,
                 focus=(hi, 'head'), fstop=3.0)

    def s31(self, f0, f1):
        self._crowd_static(f0, f1)
        hi = self.hind
        self._hind_waiting(f0, 'worried')
        for i, f in enumerate(range(f0 + 15, f1 - 10, 12)):
            A.kb(hi, 'head', f, rot=(0.05, 0.18 * (1 if i % 2 else -1), 0))
        A.expr(hi, f0 + 50, 'sad'); A.look(hi, f0 + 50, 0, -0.1, head=False)
        self.cu('S31', hi, f0, f1, 0.75, 0.6, ang=-0.3, lens=55)

    def s32(self, f0, f1):
        self._crowd_static(f0, f1)
        hi = self.hind
        self._hind_waiting(f0, 'worried')
        A.pose(hi, f0, A.P(upperarm_L=(-0.4, 0, 0.1), forearm_L=(-1.4, 0, 0.6), fingers_L=(0, 0, 1.0)))
        A.look(hi, f0, 0, 0.1)
        h = self.head(hi, f0)
        self.cam('S32', f0, f1, h + Vector((0.32, -0.55, 0.12)), (-0.3, 4.8, 0.9), h + Vector((0.28, -0.42, 0.1)), (-0.3, 4.8, 0.95),
                 lens=40, focus_dist=5.0, fstop=2.8)

    def s33(self, f0, f1):
        self._crowd_static(f0, f1)
        self._hind_waiting(f0)
        p0 = Vector((0.05, 4.0, 0.04)); p1 = Vector((-0.12, 1.45, 0.04))
        n = 6
        for k in range(n + 1):
            t = k / n
            f = f0 + int((f1 - f0) * t)
            p = p0.lerp(p1, 1 - (1 - t) ** 1.4)
            self.obj_key(self.tomato, f, loc=p, rot=(-(p0 - p).length / 0.045, 0, 0.2))
        self.torn_scene(f0)
        self.cam('S33', f0, f1, (-0.12, 0.55, 0.07), (0.0, 3.5, 0.09), (-0.12, 0.6, 0.065), (-0.1, 2.0, 0.06), lens=40,
                 focus=self.tomato, fstop=2.0)

    def torn_scene(self, f0):
        self.obj_key(self.torn, f0, loc=(0.35, 4.05, 0.0), rot=(0, 0, 0.6))
        rnd = random.Random(34)
        for i, o in enumerate(self.scatter):
            self.obj_key(o, f0, loc=(0.35 + rnd.uniform(-0.6, 0.5), 4.05 + rnd.uniform(-0.7, 0.2), 0.04),
                         rot=(rnd.uniform(0, 3), rnd.uniform(0, 3), rnd.uniform(0, 3)))

    def s34(self, f0, f1):
        self._crowd_static(f0, f1)
        self._hind_waiting(f0)
        self.obj_key(self.tomato, f0, loc=(-0.12, 1.45, 0.04))
        self.torn_scene(f0)
        cam = self.cam('S34', f0, f1, (-0.5, 2.0, 0.28), (0.25, 4.0, 0.06), (-0.45, 2.15, 0.26), (0.3, 4.0, 0.06), lens=45, fstop=1.8)
        self.focus_pull(cam, f0, 0.9, f0 + 30, 0.9)
        self.focus_pull(cam, f0 + 30, 0.9, f0 + 55, 2.15)

    def s35(self, f0, f1):
        self._crowd_static(f0, f1)
        hi = self.hind
        self._hind_waiting(f0, 'fear')
        for i, f in enumerate(range(f0, f1, 5)):
            A.look(hi, f, 0.04 * math.sin(i * 2.1), 0.05 + 0.03 * math.cos(i * 1.7), head=False)
        A.expr(hi, f0 + 50, 'fear', 1.2)
        self.cu('S35', hi, f0, f1, 0.6, 0.48, ang=0.1, dz=0.0, lens=70, tz=0.01, fstop=2.8)

    # ---- 04 WAITING
    def beacons(self, f0, f1):
        for b in self.cars['Ambulance'].children:
            if 'beacon' in b.name:
                inp = b.active_material.node_tree.nodes['Principled BSDF'].inputs['Emission Strength']
                for i, f in enumerate(range(f0, f1, 5)):
                    on = (i % 2 == 0) == ('blue' in b.name)
                    inp.default_value = 30 if on else 0
                    inp.keyframe_insert('default_value', frame=f)

    def s36(self, f0, f1):
        self._crowd_static(f0, f1)
        self._hind_waiting(f0, 'fear', held=True)
        self.obj_key(self.cars['Ambulance'], f0, loc=(-30, 5.4, 0), rot=(0, 0, 0))
        self.obj_key(self.cars['Ambulance'], f0 + 75, loc=(-3.6, 5.4, 0))
        self.beacons(f0, f1)
        self.torn_scene(f0)
        self.cam('S36', f0, f1, (-3.2, -2.3, 1.25), (-1.5, 5.0, 1.1), (-3.0, -2.25, 1.2), (-1.2, 5.0, 1.0), lens=24, focus_dist=6.0, fstop=4)

    def s37(self, f0, f1):
        hi = self.hind
        self._hind_waiting(f0, 'fear', held=True)
        self.obj_key(self.cars['Ambulance'], f0, loc=(-1.5, 5.4, 0), rot=(0, 0, 0))
        self.obj_key(self.cars['Ambulance'], f1, loc=(18, 5.4, 0))
        self.beacons(f0, f1)
        rnd = random.Random(37)
        for i, chh in enumerate(self.crowd[:6]):
            st = (-1.8 + i * 0.7, 7.6 if i % 2 else 8.2)
            en = (st[0] + rnd.choice((-4, 4)), st[1] + 0.3)
            self.place(chh, f0, st, 0, HZ)
            self.walk(chh, f0 + rnd.randint(0, 15), f1, [st, en])
        self.torn_scene(f0)
        A.look(hi, f0, 0.6, 0.05); A.look(hi, f1 - 10, 0.9, 0.0)
        self.cam('S37', f0, f1, (-2.4, -0.9, 1.0), (6.0, 5.4, 1.1), (-2.3, -0.85, 1.0), (10.0, 5.4, 1.0), lens=30,
                 focus_dist=6.5, fstop=4)

    def s38(self, f0, f1):
        hi = self.hind
        self._hind_waiting(f0, 'worried', held=True)
        A.breathe(hi, f0, f1)
        sun = bpy.data.objects['SUN']
        for f, el, az in ((f0, 30, 20), (f1, 12, 75)):
            sun.rotation_euler = (math.radians(90 - el), 0, math.radians(az)); sun.keyframe_insert('rotation_euler', frame=f)
        self.car_drive('Taxi', f0, f0 + 30, -25, 25, 1.9); self.car_drive('Sedan', f0 + 35, f0 + 62, 25, -25, 2.1)
        self.car_drive('Van', f0 + 70, f1, -25, 25, 1.9)
        self.cam('S38', f0, f1, (-0.6, 7.9, 2.7), (-0.95, -0.5, 0.6), lens=32, focus=(hi, 'head'), fstop=4)

    def s39(self, f0, f1):
        hi = self.hind
        self._hind_waiting(f0, 'worried', held=True)
        A.pose(hi, f0, A.CLUTCH_RABBIT)
        A.look(hi, f0 + 5, 0.7, 0.05); A.look(hi, f0 + 25, -0.7, 0.05); A.look(hi, f0 + 45, 0, 0.0)
        A.expr(hi, f0 + 25, 'fear')
        self.cu('S39', hi, f0, f1, 0.85, 0.6, ang=0.15, lens=50)

    # ---- 05 THE EMPTY HOUSE
    def s40(self, f0, f1):
        hi = self.hind
        self.place(hi, f0, (-11.0, -1.2), FACE_NX, HZ)
        self.walk(hi, f0, f1, [(-11.0, -1.2), (-17.3, -1.9), (-18.0, -2.6)], run=True, carry='R')
        A.pose(hi, f0, A.CLUTCH_RABBIT, base={}); self.vis(self.rabbit_held, f0, True)
        A.expr(hi, f0, 'fear')
        self.obj_key(self.home_door, f0, rot=(0, 0, 0.25))
        self.cam('S40', f0, f1, (-9.6, 1.2, 0.9), (-11.0, -1.2, 0.7), (-15.6, 1.1, 0.95), (-17.4, -2.0, 0.75), lens=30,
                 focus=(hi, 'head'), fstop=3.2)

    def s41(self, f0, f1):
        hi = self.hind
        self.obj_key(self.front_door, f0, rot=(0, 0, 0)); self.obj_key(self.front_door, f0 + 25, rot=(0, 0, 1.45))
        self.place(hi, f0, (108.0, -4.6), FACE_Y, 0)
        A.pose(hi, f0, A.CLUTCH_RABBIT); self.vis(self.rabbit_held, f0, True)
        self.walk(hi, f0 + 30, f1, [(108.0, -4.6), (108.0, -3.5)], carry='R')
        A.pose(hi, f0 + 30, A.CLUTCH_RABBIT, base={})
        A.expr(hi, f0, 'worried')
        self.cam('S41', f0, f1, (108.6, -0.6, 1.25), (108.0, -4.0, 1.0), (108.5, -0.9, 1.15), (108.0, -4.0, 0.85), lens=28,
                 focus=(hi, 'head'), fstop=3.2)

    def s42(self, f0, f1):
        hi = self.hind
        self.obj_key(self.front_door, f0, rot=(0, 0, 1.45))
        self.place(hi, f0, (108.0, -3.3), FACE_Y, 0)
        self.walk(hi, f0, f1, [(108.0, -3.3), (107.6, -1.5), (107.2, -0.3)], carry='R')
        A.pose(hi, f0, A.CLUTCH_RABBIT, base={}); self.vis(self.rabbit_held, f0, True)
        A.expr(hi, f0, 'call'); A.expr(hi, f0 + 25, 'worried'); A.expr(hi, f0 + 40, 'call')
        A.look(hi, f0 + 10, 0.6, 0.1); A.look(hi, f0 + 35, -0.6, 0.1)
        self.cam('S42', f0, f1, (109.55, -3.6, 1.7), (107.8, -1.5, 0.8), (109.5, -3.5, 1.65), (107.3, -0.5, 0.8), lens=22,
                 focus=(hi, 'head'), fstop=4)

    def s43(self, f0, f1):
        hi = self.hind
        self.place(hi, f0, (107.2, 0.6), FACE_Y, 0)
        self.walk(hi, f0, f0 + 50, [(107.2, 0.6), (107.1, 1.9)], carry='R')
        A.pose(hi, f0, A.CLUTCH_RABBIT, base={}); self.vis(self.rabbit_held, f0, True)
        A.pose(hi, f0 + 52, A.CLUTCH_RABBIT)
        A.expr(hi, f0, 'worried'); A.look(hi, f0 + 55, -0.3, 0.1); A.expr(hi, f0 + 80, 'sad')
        self.cam('S43', f0, f1, (108.3, 0.45, 1.4), (107.0, 3.4, 0.85), (108.25, 0.6, 1.38), (107.0, 3.3, 0.82), lens=22,
                 focus=(hi, 'head'), fstop=3.2)

    def _doorstep(self, f0):
        hx, hy = E.HOME_DOOR
        self.obj_key(self.home_door, f0, rot=(0, 0, 1.6))
        self.place(self.hind, f0, (hx, -2.65), FACE_Y, HZ)

    def s44(self, f0, f1):
        hi, nb = self.hind, self.neighbour
        hx, hy = E.HOME_DOOR
        self._doorstep(f0)
        A.pose(hi, f0, A.CLUTCH_RABBIT); self.vis(self.rabbit_held, f0, True); A.expr(hi, f0, 'sad')
        A.look(hi, f0 + 20, -0.6, 0.15)
        self.place(nb, f0, (hx + 3.6, -0.9), FACE_NX, HZ)
        self.walk(nb, f0, f1 - 5, [(hx + 3.6, -0.9), (hx + 0.6, -1.6), (hx, -1.95)])
        A.expr(nb, f0, 'sad')
        self.cam('S44', f0, f1, (hx - 2.2, -1.3, 1.25), (hx + 0.6, -1.9, 1.0), (hx - 2.0, -1.2, 1.2), (hx + 0.1, -2.2, 0.95), lens=28,
                 focus=(nb, 'head'), fstop=3.2)

    def _kneel_pair(self, f0):
        hi, nb = self.hind, self.neighbour
        hx, hy = E.HOME_DOOR
        self._doorstep(f0)
        self.obj_key(self.rabbit_free, f0, loc=(hx + 0.35, -2.75, HZ + 0.15), rot=(0, 0, PI - 0.4))
        A.pose(hi, f0, A.P(upperarm_L=(-0.55, 0, 0.1), upperarm_R=(-0.55, 0, -0.1), forearm_L=(-0.35, 0, 0), forearm_R=(-0.35, 0, 0)))
        self.place(nb, f0, (hx, -1.95), FACE_NY, HZ - (nb.dims['zh'] - nb.dims['zk']) + 0.04)
        A.pose(nb, f0, A.KNEEL, A.P(upperarm_L=(-0.9, 0, 0.25), upperarm_R=(-0.9, 0, -0.25), forearm_L=(-0.5, 0, 0.2), forearm_R=(-0.5, 0, -0.2)))
        A.expr(nb, f0, 'sad'); A.expr(hi, f0, 'worried')

    def s45(self, f0, f1):
        hi, nb = self.hind, self.neighbour
        hx, hy = E.HOME_DOOR
        self._kneel_pair(f0)
        A.look(hi, f0, 0, 0.2); A.look(nb, f0, 0, -0.1)
        A.breathe(nb, f0, f1, spine_base=(0.15, 0, 0))
        self.common(f0, f1, [hi, nb], 45)
        self.cam('S45', f0, f1, (hx + 1.5, -2.1, 0.85), (hx, -2.3, 0.75), (hx + 1.3, -2.05, 0.82), (hx, -2.3, 0.75), lens=32,
                 focus=(hi, 'head'), fstop=2.8)

    def s46(self, f0, f1):
        hi, nb = self.hind, self.neighbour
        hx, hy = E.HOME_DOOR
        self._kneel_pair(f0)
        A.talk(nb, f0 + 5, f1 - 10, rate=3.0, seed=46); A.expr(nb, f0, 'sad')
        A.kb(nb, 'head', f0 + 40, rot=(0.1, 0, 0.1))
        self.common(f0, f1, [hi, nb], 46)
        self.cu('S46', nb, f0, f1, 0.85, 0.7, ang=-0.55, lens=50)

    def s47(self, f0, f1):
        hi, nb = self.hind, self.neighbour
        self._kneel_pair(f0)
        A.expr(hi, f0, 'shock'); A.expr(hi, f0 + 70, 'cry', 0.6)
        A.look(hi, f0, 0, 0.12)
        self.vis(self.tears[0], f0 + 80, True)
        self.tear_anim(f0 + 80, f1, self.tears[0])
        self.cu('S47', hi, f0, f1, 0.75, 0.55, ang=0.4, dz=0.06, lens=55)

    def tear_anim(self, f0, f1, t):
        d = self.hind.dims
        s = 1 if t.name.endswith('1') else -1
        base = Vector((s * d['ex'], d['ey'] - d['er'] * 0.85, d['ez'] - d['er'] * 0.95))
        self.obj_key(t, f0, loc=base)
        self.obj_key(t, f1, loc=base + Vector((s * 0.012, -0.012, -d['r'] * 0.5)))

    def s48(self, f0, f1):
        hi = self.hind
        self.place(hi, f0, (108.0, -2.0), FACE_NX, 0)
        self.walk(hi, f0, f1, [(108.0, -2.0), (106.0, -2.05), (104.1, -2.0)], run=True)
        A.expr(hi, f0, 'cry', 0.7)
        self.cam('S48', f0, f1, (102.3, -0.75, 1.25), (105.8, -2.1, 0.8), (102.4, -0.8, 1.15), (104.3, -2.2, 0.6), lens=24,
                 focus=(hi, 'head'), fstop=3.2)

    def _pillow_hug(self, f0):
        hi = self.hind
        kn = A.P(thigh_L=(-0.05, 0, 0), thigh_R=(-0.05, 0, 0), shin_L=(1.55, 0, 0), shin_R=(1.55, 0, 0),
                 foot_L=(0.6, 0, 0), foot_R=(0.6, 0, 0), spine=(0.95, 0, 0), neck=(0.25, 0, 0), head=(0.0, 0.0, 0.5),
                 upperarm_L=(-1.5, 0, 0.45), upperarm_R=(-1.5, 0, -0.45), forearm_L=(-1.0, 0, 0.9), forearm_R=(-1.0, 0, -0.9))
        self.place(hi, f0, (103.7, -2.75), FACE_X, -(hi.dims['zk']) + 0.05)
        A.pose(hi, f0, kn)
        pil = bpy.data.objects['huda_pillow']
        self.obj_key(pil, f0, loc=(E.HOUSE_O.x + 4.2, -2.75, 0.6), rot=(0.0, 0.25, 1.57))
        self.obj_key(self.rabbit_free, f0, loc=(104.55, -2.2, 0.51), rot=(0.0, 0.0, 2.6))
        A.expr(hi, f0, 'cry')
        return kn

    def s49(self, f0, f1):
        hi = self.hind
        kn = self._pillow_hug(f0)
        A.shake(hi, f0 + 5, f1, amp=0.05, base=(0.95, 0, 0))
        self.cam('S49', f0, f1, (102.35, -0.85, 1.5), (104.0, -2.6, 0.55), (102.6, -1.05, 1.35), (104.0, -2.6, 0.55), lens=28,
                 focus=(hi, 'head'), fstop=3.2)

    def s50(self, f0, f1):
        hi = self.hind
        self._pillow_hug(f0)
        A.shake(hi, f0, f1, amp=0.04, base=(0.95, 0, 0))
        A.talk(hi, f0 + 20, f1 - 30, rate=3.0, seed=50)
        A.expr(hi, f0, 'cry')
        for t in self.tears:
            self.vis(t, f0, True)
        self.tear_anim(f0, f0 + 60, self.tears[0]); self.tear_anim(f0 + 50, f1, self.tears[1])
        h = self.head(hi, f0)
        self.cam('S50', f0, f1, h + Vector((0.6, 0.85, 0.55)), h + Vector((0, 0, -0.08)), h + Vector((0.5, 0.7, 0.45)), h + Vector((0, 0, -0.08)), lens=40,
                 focus=(hi, 'head'), fstop=2.2)

    # ---- 06 THE CLIFFHANGER
    def _hospital(self, f0):
        hu, mo = self.huda, self.mother
        O = E.HOSP_O
        self.place(hu, f0, (O.x + 0.6, O.y + 0.3), 0, 0.84)
        A.kb(hu, 'root', f0, rot=(-PI / 2, 0, PI))
        A.pose(hu, f0, A.LIE, A.P(upperarm_R=(0.0, 0, 0.05), forearm_R=(0.0, 0, 0)))
        A.expr(hu, f0, 'sleep')
        bl = bpy.data.objects['hblanket']
        self.obj_key(bl, f0, loc=(O.x + 0.6, O.y + 0.35, 0.88), scale=(1.0, 1.3, 1.0))
        sit = A.P(thigh_L=(-1.5, 0, -0.06), thigh_R=(-1.5, 0, 0.06), shin_L=(1.5, 0, 0), shin_R=(1.5, 0, 0),
                  spine=(0.25, 0, 0), neck=(0.2, 0, 0), upperarm_L=(-0.9, 0, 0.2), forearm_L=(-0.5, 0, 0.4),
                  upperarm_R=(-0.5, 0, -0.1), forearm_R=(-1.1, 0, -0.4))
        self.place(mo, f0, (O.x - 0.45, O.y + 0.55), FACE_X, 0.5 - mo.dims['zh'] + 0.06)
        A.pose(mo, f0, sit)
        A.expr(mo, f0, 'sad')
        A.breathe(mo, f0, f0 + 120, spine_base=(0.25, 0, 0))
        A.breathe(hu, f0, f0 + 120, amp=0.01, period=110)
    def s51(self, f0, f1):
        self._hospital(f0)
        A.look(self.mother, f0, 0.0, -0.3)
        self.cam('S51', f0, f1, (E.HOSP_O.x - 1.9, E.HOSP_O.y - 2.2, 1.7), (E.HOSP_O.x + 0.3, E.HOSP_O.y + 0.6, 0.85),
                 (E.HOSP_O.x - 1.6, E.HOSP_O.y - 1.8, 1.6), (E.HOSP_O.x + 0.3, E.HOSP_O.y + 0.6, 0.85), lens=28,
                 focus=(self.mother, 'head'), fstop=3.2)

    def s52(self, f0, f1):
        self._hospital(f0)
        O = E.HOSP_O
        c = Vector((O.x + 0.32, O.y + 0.62, 0.975))
        hd, mo = self.hp['huda_bed'], self.hp['mother']
        self.obj_key(hd['root'], f0, loc=c, rot=(PI / 2, 0, -PI / 2))
        self.obj_key(hd['pinky'], f0, rot=(0, 0.15, 0))
        for i, f in enumerate(range(f0, f1 + 1, 22)):
            self.obj_key(mo['root'], f, loc=c + Vector((-0.12, -0.03, 0.022 + 0.003 * (i % 2))), rot=(PI / 2, 0, -0.25 + 0.05 * (i % 2)))
        self.cam('S52', f0, f1, c + Vector((0.28, -0.34, 0.2)), c + Vector((-0.03, 0, 0)), c + Vector((0.22, -0.27, 0.16)),
                 c + Vector((-0.03, 0, 0)), lens=50, focus=hd['root'], fstop=2.2)
    def _door_sit(self, f0):
        hi = self.hind
        self.obj_key(self.front_door, f0, rot=(0, 0, 1.45))
        sit = A.SIT_KNEES
        self.place(hi, f0, (108.0, -3.25), FACE_NY, -(hi.dims['zh'] - 0.07))
        A.pose(hi, f0, sit)
        self.obj_key(self.rabbit_free, f0, loc=(108.22, -3.45, 0.0), rot=(0, 0, 0.2))
        A.expr(hi, f0, 'sad')
        A.breathe(hi, f0, f0 + 150, spine_base=(0.35, 0, 0))

    def s53(self, f0, f1):
        self._door_sit(f0)
        A.look(self.hind, f0, 0, 0.15); A.look(self.hind, f0 + 80, 0.1, 0.2)
        self.common(f0, f1, [self.hind], 53)
        self.cam('S53', f0, f1, (108.3, -0.6, 1.0), (108.0, -4.0, 0.75), (108.25, -1.4, 0.85), (108.0, -4.0, 0.7), lens=30,
                 focus=(self.hind, 'head'), fstop=2.8)

    def s54(self, f0, f1):
        self._hospital(f0)
        O = E.HOSP_O
        c = Vector((O.x + 0.32, O.y + 0.62, 0.975))
        hd = self.hp['huda_bed']
        self.obj_key(hd['root'], f0, loc=c, rot=(PI / 2, 0, -PI / 2))
        self.obj_key(hd['pinky'], f0, rot=(0, 0.15, 0))
        self.obj_key(hd['pinky'], f1, rot=(0, -0.25, 0))
        self.cam('S54', f0, f1, c + Vector((0.24, -0.24, 0.13)), c + Vector((0, -0.04, 0)), c + Vector((0.19, -0.19, 0.1)),
                 c + Vector((0, -0.04, 0)), lens=55, focus=hd['pinky'], fstop=2.0)
    def s55(self, f0, f1):
        hi = self.hind
        self._door_sit(f0)
        A.pose(hi, f0, A.SIT_KNEES, A.P(fingers_R=(0, 0, -1.0), pinky_R=(0, 0, 0.1)))
        A.look(hi, f0, 0, 0.18)
        self.common(f0, f1, [hi], 55)
        h = self.head(hi, f0)
        self.cam('S55', f0, f1, h + Vector((0.55, 0.6, -0.1)), h + Vector((0, 0, -0.15)), (108.6, -0.2, 1.4), (108.0, -3.8, 0.7),
                 lens=45, lens1=28, focus=(hi, 'head'), fstop=2.8)


def _capsule_x(name, r, L, coll, m):
    """capsule along +X from origin"""
    o = U.lathe(name, [(0.0, -r), (r * 0.75, -r * 0.6), (r, 0.0), (r * 0.95, L), (r * 0.7, L + r * 0.6), (0.0, L + r)],
                14, collection=coll, mat_=m, subsurf=1)
    o.rotation_euler = (0, PI / 2, 0)
    return o


def hand_prop(name, skin, cuff_m, sleeve_m, scale, coll, kind='fist'):
    """Stand-alone hand for macro shots.  Local frame: wrist at origin, hand points +X,
    thumb up (+Z), palm thin along Y.  'fist': curled fingers with the little finger
    free (pinky promise); 'relaxed': open hand resting (rotate root to lay it flat).
    The little finger hangs from an empty 'pinky' pivot: rotate it about Y (negative = curl up)."""
    root = bpy.data.objects.new(name, None); coll.objects.link(root)
    k = scale
    parts = []
    palm = U.rbox(name + '_palm', (0.05 * k, 0.024 * k, 0.046 * k), (0.028 * k, 0, 0.0), bevel=0.011 * k, collection=coll, mat_=skin)
    parts.append(palm)
    if kind == 'fist':
        roll = U.rbox(name + '_fist', (0.026 * k, 0.03 * k, 0.036 * k), (0.06 * k, -0.004 * k, 0.004 * k), bevel=0.0115 * k,
                      collection=coll, mat_=skin)
        parts.append(roll)
        for i, z in enumerate((0.016, 0.004, -0.008)):
            parts.append(U.sphere(f'{name}_knuckle{i}', 0.0075 * k, (0.07 * k, -0.002 * k, z * k), collection=coll, mat_=skin, subsurf=1))
        th = _capsule_x(name + '_thumb', 0.0072 * k, 0.026 * k, coll, skin)
        th.location = (0.034 * k, -0.013 * k, 0.02 * k); th.rotation_euler = (0, PI / 2 + 0.25, -0.15)
        parts.append(th)
        piv = (0.05 * k, 0.0, -0.026 * k)
    else:
        for i, z in enumerate((0.015, 0.005, -0.006)):
            f = _capsule_x(f'{name}_finger{i}', 0.0062 * k, (0.03 - 0.002 * abs(i - 1)) * k, coll, skin)
            f.location = (0.052 * k, 0, z * k); f.rotation_euler = (0, PI / 2 + 0.12, 0)
            parts.append(f)
        th = _capsule_x(name + '_thumb', 0.007 * k, 0.024 * k, coll, skin)
        th.location = (0.026 * k, -0.006 * k, 0.024 * k); th.rotation_euler = (0, PI / 2 - 0.2, 0.25)
        parts.append(th)
        piv = (0.05 * k, 0.0, -0.016 * k)
    cuff = U.lathe(name + '_cuff', [(0.03 * k, -0.012 * k), (0.033 * k, 0.004 * k)], 20, collection=coll, mat_=cuff_m, subsurf=1)
    cuff.rotation_euler = (0, PI / 2, 0); cuff.location = (-0.004 * k, 0, 0)
    sleeve = U.lathe(name + '_sleeve', [(0.032 * k, 0.0), (0.036 * k, 0.12 * k)], 20, collection=coll, mat_=sleeve_m, subsurf=1, cap_top=False)
    sleeve.rotation_euler = (0, -PI / 2, 0); sleeve.location = (-0.012 * k, 0, 0)
    parts += [cuff, sleeve]
    for p in parts:
        p.parent = root
    pk = bpy.data.objects.new(name + '_pinkypivot', None); coll.objects.link(pk)
    pk.parent = root; pk.location = piv
    pf = _capsule_x(name + '_pinky', 0.0058 * k, 0.04 * k if kind == 'fist' else 0.026 * k, coll, skin)
    pf.parent = pk
    return {'root': root, 'pinky': pk}


def main():
    only = None
    st = Story()
    st.run(only)
    # per-shot set table for the renderer
    st.sc['shot_sets'] = json.dumps(st.shot_sets)
    os.makedirs(EP, exist_ok=True)
    with open(os.path.join(EP, 'scene_map.md'), 'w') as fh:
        fh.write('# Episode 01 — The Promise · timestamped scene map\n\n'
                 'Master narration: 190.85 s · 30 fps · frames 1–5726 · 1080×1920 (9:16)\n\n')
        fh.write(SL.scene_map_md() + '\n')
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(EP, 'story.blend'), compress=True)
    print('STORY OK')


if __name__ == '__main__':
    main()

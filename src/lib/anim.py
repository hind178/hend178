"""Reusable procedural animation for the shared rig (see character.py).

Axis conventions (measured from the rig):
  limbs (bones pointing down): rot.x < 0 swings forward, rot.z abducts (L:-, R:+)
  spine/neck/head: rot.x > 0 leans/nods forward, rot.y > 0 turns to char-left, rot.z tilts
  eyes: rot.z > 0 looks to char-left (+X), rot.x > 0 looks up
  lids: rot.x = LID_OPEN .. LID_CLOSED      fingers/pinky curl: L:+z, R:-z
Every function writes keyframes into the character's single action, so a shot is a
sequence of calls; the same calls build the exported reusable Actions."""
import math, random
from mathutils import Vector
from . import character as C

BODY = ['root', 'hips', 'spine', 'neck', 'head', 'skirt', 'upperarm.L', 'upperarm.R', 'forearm.L',
        'forearm.R', 'hand.L', 'hand.R', 'fingers.L', 'fingers.R', 'pinky.L', 'pinky.R', 'thigh.L',
        'thigh.R', 'shin.L', 'shin.R', 'foot.L', 'foot.R']


def kb(ch, bone, frame, rot=None, loc=None):
    if bone not in ch.arm.pose.bones:
        return
    pb = ch.arm.pose.bones[bone]
    if rot is not None:
        pb.rotation_euler = rot
        pb.keyframe_insert('rotation_euler', frame=frame)
    if loc is not None:
        pb.location = loc
        pb.keyframe_insert('location', frame=frame)


# ----------------------------------------------------------------- body poses
def P(**kw):
    """pose helper: P(upperarm_L=(x,y,z), ...)  -> {'upperarm.L': (...)}"""
    return {k.replace('_L', '.L').replace('_R', '.R'): v for k, v in kw.items()}


ARMS_DOWN = P(upperarm_L=(0.05, 0, -0.10), upperarm_R=(0.05, 0, 0.10), forearm_L=(-0.15, 0, 0),
              forearm_R=(-0.15, 0, 0), fingers_L=(0, 0, 0.3), fingers_R=(0, 0, -0.3),
              pinky_L=(0, 0, 0.35), pinky_R=(0, 0, -0.35))
STAND = dict(ARMS_DOWN, **P(spine=(0, 0, 0), neck=(0, 0, 0), head=(0, 0, 0), hips=(0, 0, 0),
                            thigh_L=(0, 0, 0), thigh_R=(0, 0, 0), shin_L=(0, 0, 0), shin_R=(0, 0, 0),
                            foot_L=(0, 0, 0), foot_R=(0, 0, 0), hand_L=(0, 0, 0), hand_R=(0, 0, 0), skirt=(0, 0, 0)))
HOLD_RABBIT = P(upperarm_R=(-0.35, 0, 0.2), forearm_R=(-1.35, 0, -0.25), hand_R=(0.2, 0.0, 0.2),
                fingers_R=(0, 0, -0.9), pinky_R=(0, 0, -0.9))
CLUTCH_RABBIT = P(upperarm_R=(-0.25, 0, 0.12), forearm_R=(-1.7, 0, -0.5), upperarm_L=(-0.3, 0, -0.1),
                  forearm_L=(-1.6, 0, 0.55), fingers_R=(0, 0, -1.0), fingers_L=(0, 0, 1.0))
WAVE_UP = P(upperarm_L=(-0.4, 0, -1.9), forearm_L=(-0.4, 0, 0.2), hand_L=(0, 0, 0))
POINT_R = P(upperarm_R=(-1.35, 0, 0.35), forearm_R=(-0.1, 0, 0), fingers_R=(0, 0, -1.2), pinky_R=(0, 0, -1.2))
PINKY_OUT_R = P(upperarm_R=(-0.55, 0, -0.15), forearm_R=(-1.05, 0, 0.0), hand_R=(0, 0, 0),
                fingers_R=(0, 0, -1.3), pinky_R=(0, 0, 0.15))
PINKY_OUT_L = P(upperarm_L=(-0.55, 0, 0.15), forearm_L=(-1.05, 0, 0.0), fingers_L=(0, 0, 1.3), pinky_L=(0, 0, -0.15))
SIT_FLOOR = P(hips=(-0.15, 0, 0), thigh_L=(-1.45, 0, -0.18), thigh_R=(-1.45, 0, 0.18), shin_L=(1.5, 0, 0),
              shin_R=(1.5, 0, 0), spine=(0.2, 0, 0), upperarm_L=(-0.5, 0, -0.15), upperarm_R=(-0.5, 0, 0.15),
              forearm_L=(-0.8, 0, 0.2), forearm_R=(-0.8, 0, -0.2))
SIT_KNEES = P(hips=(-0.1, 0, 0), thigh_L=(-1.5, 0, -0.08), thigh_R=(-1.5, 0, 0.08), shin_L=(2.2, 0, 0),
              shin_R=(2.2, 0, 0), spine=(0.35, 0, 0), neck=(0.1, 0, 0), upperarm_L=(-0.6, 0, -0.05),
              upperarm_R=(-0.6, 0, 0.05), forearm_L=(-1.2, 0, 0.5), forearm_R=(-1.2, 0, -0.5),
              fingers_L=(0, 0, 0.8), fingers_R=(0, 0, -0.8))
KNEEL = P(thigh_L=(-1.5, 0, -0.1), shin_L=(1.55, 0, 0), thigh_R=(0.05, 0, 0.1), shin_R=(1.55, 0, 0),
          foot_R=(-0.6, 0, 0), spine=(0.15, 0, 0))
LIE = P(head=(0.0, 0.0, 0.25), upperarm_L=(0.0, 0, -0.18), upperarm_R=(0.0, 0, 0.18))
HUG_PILLOW = P(spine=(0.75, 0, 0), neck=(0.3, 0, 0), upperarm_L=(-1.1, 0, 0.35), upperarm_R=(-1.1, 0, -0.35),
               forearm_L=(-1.2, 0, 0.6), forearm_R=(-1.2, 0, -0.6), thigh_L=(-1.4, 0, -0.1),
               thigh_R=(-1.4, 0, 0.1), shin_L=(1.9, 0, 0), shin_R=(1.9, 0, 0))
HANDS_ON_HEAD = P(upperarm_L=(-0.55, 0, 0.22), upperarm_R=(-0.55, 0, -0.22), forearm_L=(-2.35, 0, 0.1),
                  forearm_R=(-2.35, 0, -0.1), hand_L=(0.3, 0, 0), hand_R=(0.3, 0, 0))
GIVE_COINS = P(upperarm_R=(-0.9, 0, 0.1), forearm_R=(-0.7, 0, 0.0), hand_R=(0.3, 0, 0))
TAKE_COINS = P(upperarm_L=(-0.75, 0, -0.1), forearm_L=(-0.8, 0, 0), hand_L=(0.2, 0, 0))
COOK = P(upperarm_R=(-0.6, 0, 0.1), forearm_R=(-1.2, 0, -0.4), upperarm_L=(-0.5, 0, -0.1), forearm_L=(-1.1, 0, 0.4),
         spine=(0.12, 0, 0), neck=(0.15, 0, 0))
HOLD_HAND_L = P(upperarm_L=(0.0, 0, -0.32), forearm_L=(-0.25, 0, 0.0), fingers_L=(0, 0, 0.8))   # reach to the side
HOLD_HAND_R = P(upperarm_R=(0.0, 0, 0.32), forearm_R=(-0.25, 0, 0.0), fingers_R=(0, 0, -0.8))
CARRY_BAG_L = P(upperarm_L=(0.0, 0, -0.18), forearm_L=(-0.3, 0, 0.1), fingers_L=(0, 0, 1.2), pinky_L=(0, 0, 1.2))
TUG = P(upperarm_L=(-1.0, 0, 0.1), upperarm_R=(-1.0, 0, -0.1), forearm_L=(-0.3, 0, 0.2), forearm_R=(-0.3, 0, -0.2),
        spine=(-0.15, 0, 0), fingers_L=(0, 0, 1.2), fingers_R=(0, 0, -1.2))
HUG = P(upperarm_L=(-1.2, 0, -0.2), upperarm_R=(-1.2, 0, 0.2), forearm_L=(-0.9, 0, 0.9), forearm_R=(-0.9, 0, -0.9),
        spine=(0.1, 0, 0))


def pose(ch, frame, *poses, base=STAND, root=None, root_rot=None):
    """Key a full body pose (base + overrides) at frame."""
    p = dict(base)
    for o in poses:
        p.update(o)
    for b, r in p.items():
        kb(ch, b, frame, rot=r)
    if root is not None:
        kb(ch, 'root', frame, loc=root_local(root))
    if root_rot is not None:
        kb(ch, 'root', frame, rot=(0, 0, root_rot))


def root_local(v):
    """root bone points +Y: its local axes == world axes (bone X=X, Y=Y, Z=Z)."""
    return (v[0], v[1], v[2] if len(v) > 2 else 0.0)


def place(ch, frame, xy, facing, z=0.0, interp_const=True):
    """Teleport character for a new shot (constant key so cuts don't blend)."""
    kb(ch, 'root', frame, loc=(xy[0], xy[1], z), rot=(0, 0, facing))
    if interp_const:
        _const_at(ch, frame)


def _const_at(ch, frame):
    ad = ch.arm.animation_data
    from . import util as U
    for fc in U.fcurves_of(ad):
        if 'root' in fc.data_path:
            for k in fc.keyframe_points:
                if abs(k.co.x - frame) < 0.5:
                    k.interpolation = 'CONSTANT'


def face_dir(dx, dy):
    return math.atan2(dx, -dy)


# ----------------------------------------------------------------- face
EXPR = {
    #          smile  sad  open  oh  cry   lid     browL(loc z, rot y)
    'neutral': (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, (0.0, 0.0)),
    'smile':   (0.8, 0.0, 0.0, 0.0, 0.0, -0.12, (0.003, 0.0)),
    'laugh':   (1.0, 0.0, 0.55, 0.0, 0.0, -0.3, (0.005, 0.0)),
    'happy':   (0.6, 0.0, 0.15, 0.0, 0.0, -0.05, (0.004, 0.0)),
    'pout':    (0.0, 0.7, 0.0, 0.3, 0.0, 0.08, (-0.002, -0.25)),
    'sad':     (0.0, 0.85, 0.0, 0.0, 0.0, 0.18, (0.0, -0.35)),
    'worried': (0.0, 0.5, 0.1, 0.0, 0.0, -0.05, (0.004, -0.4)),
    'fear':    (0.0, 0.3, 0.35, 0.3, 0.0, -0.35, (0.008, -0.45)),
    'shock':   (0.0, 0.0, 0.6, 0.6, 0.0, -0.4, (0.01, -0.2)),
    'cry':     (0.0, 0.4, 0.4, 0.0, 1.0, 0.35, (0.002, -0.5)),
    'call':    (0.0, 0.0, 0.5, 0.7, 0.0, -0.15, (0.006, -0.2)),
    'gentle':  (0.45, 0.15, 0.0, 0.0, 0.0, 0.1, (0.002, -0.2)),
    'talk':    (0.2, 0.1, 0.35, 0.2, 0.0, 0.0, (0.002, -0.1)),
    'sleep':   (0.0, 0.0, 0.0, 0.0, 0.0, 99, (0.0, 0.0)),
}


def expr(ch, frame, name, amt=1.0):
    sm, sd, op, oh, cr, lid, (bz, br) = EXPR[name]
    kbk = ch.mouth.data.shape_keys.key_blocks
    for nm, v in (('smile', sm), ('sad', sd), ('open', op), ('oh', oh), ('cry', cr)):
        kbk[nm].value = v * amt
        kbk[nm].keyframe_insert('value', frame=frame)
    lv = C.LID_CLOSED if lid == 99 else C.LID_OPEN - lid * amt
    for s, sg in (('L', 1), ('R', -1)):
        kb(ch, 'lid.' + s, frame, rot=(lv, 0, 0))
        kb(ch, 'brow.' + s, frame, rot=(0, sg * br * amt, 0), loc=(0, 0, bz * amt))
    ch._lid = lv


def talk(ch, f0, f1, base='talk', rate=4.0, seed=0):
    """Lip flap (for characters speaking within narration: mother, neighbour, Huda)."""
    rnd = random.Random(seed)
    kbk = ch.mouth.data.shape_keys.key_blocks
    f = f0
    while f < f1:
        v = rnd.uniform(0.15, 0.7)
        kbk['open'].value = v; kbk['open'].keyframe_insert('value', frame=f)
        kbk['oh'].value = rnd.uniform(0, 0.4); kbk['oh'].keyframe_insert('value', frame=f)
        f += int(30 / rate) + rnd.randint(-1, 2)
    kbk['open'].value = 0; kbk['open'].keyframe_insert('value', frame=f1)
    kbk['oh'].value = 0; kbk['oh'].keyframe_insert('value', frame=f1)


def blinks(ch, f0, f1, seed=1, every=(70, 130), lid=None):
    rnd = random.Random(seed)
    lv = getattr(ch, '_lid', C.LID_OPEN) if lid is None else lid
    f = f0 + rnd.randint(10, 40)
    while f + 6 < f1:
        for s in 'LR':
            kb(ch, 'lid.' + s, f - 1, rot=(lv, 0, 0))
            kb(ch, 'lid.' + s, f + 2, rot=(C.LID_CLOSED, 0, 0))
            kb(ch, 'lid.' + s, f + 5, rot=(lv, 0, 0))
        f += rnd.randint(*every)


def look(ch, frame, yaw=0.0, pitch=0.0, head=True, head_amt=0.5, tilt=0.0):
    for s in 'LR':
        kb(ch, 'eye.' + s, frame, rot=(pitch * 0.6, 0, yaw * 0.6))
    if head:
        kb(ch, 'head', frame, rot=(-pitch * head_amt, yaw * head_amt, tilt))


def breathe(ch, f0, f1, amp=0.025, period=90, seed=0, spine_base=(0, 0, 0)):
    """Idle breathing + tiny weight shift (secondary motion on skirt)."""
    rnd = random.Random(seed)
    ph = rnd.uniform(0, 6.28)
    for f in range(f0, f1 + 1, 15):
        s = math.sin(ph + 2 * math.pi * (f - f0) / period)
        kb(ch, 'spine', f, rot=(spine_base[0] + amp * s, spine_base[1], spine_base[2] + 0.01 * math.sin(ph + f * 0.021)))
        kb(ch, 'skirt', f, rot=(0.012 * math.sin(ph + f * 0.05), 0, 0.015 * math.sin(ph + f * 0.031)))


def walk(ch, f0, f1, pts, run=False, arms=True, carry=None, face_path=True, bag=False, step_len=None):
    """Walk/run along polyline pts [(x,y),..] between f0..f1 (keys every 2 frames).
    Natural cycle: leg swing, knee bend, hip bob/sway, opposite arm swing, skirt flutter."""
    H = ch.spec['H']
    seg = [Vector((*pts[i + 1], 0)) - Vector((*pts[i], 0)) for i in range(len(pts) - 1)]
    lens = [s.length for s in seg]; total = sum(lens)
    stride = step_len or (0.42 * H if not run else 0.75 * H)
    a = 0.55 if run else 0.38
    for f in range(f0, f1 + 1, 2):
        t = (f - f0) / max(1, f1 - f0)
        t = t if run else t  # constant speed
        d = t * total
        i = 0
        while i < len(lens) - 1 and d > lens[i]:
            d -= lens[i]; i += 1
        p = Vector((*pts[i], 0)) + seg[i].normalized() * min(d, lens[i])
        ph = (t * total) / stride * math.pi
        s = math.sin(ph)
        bob = abs(math.cos(ph)) * (0.012 if not run else 0.03) * H
        kb(ch, 'root', f, loc=(p.x, p.y, bob - (0.01 if run else 0.004) * H),
           rot=(0, 0, face_dir(seg[i].x, seg[i].y)) if face_path else None)
        kb(ch, 'thigh.L', f, rot=(-a * s, 0, 0)); kb(ch, 'thigh.R', f, rot=(a * s, 0, 0))
        kb(ch, 'shin.L', f, rot=(max(0, math.sin(ph - 1.2)) * (0.9 if run else 0.6) + 0.05, 0, 0))
        kb(ch, 'shin.R', f, rot=(max(0, -math.sin(ph - 1.2)) * (0.9 if run else 0.6) + 0.05, 0, 0))
        kb(ch, 'foot.L', f, rot=(0.25 * s, 0, 0)); kb(ch, 'foot.R', f, rot=(-0.25 * s, 0, 0))
        kb(ch, 'hips', f, rot=(0, 0.06 * s, 0.03 * s))
        kb(ch, 'spine', f, rot=(0.12 if run else 0.03, -0.08 * s, -0.02 * s))
        kb(ch, 'skirt', f, rot=(0.06 * abs(s) * (1.6 if run else 1), 0, 0.04 * s))
        kb(ch, 'head', f, rot=(-0.04 if run else 0, 0.04 * s, 0))
        if arms:
            aa = 0.7 if run else 0.32
            if carry != 'L':
                kb(ch, 'upperarm.L', f, rot=(aa * s, 0, -0.12)); kb(ch, 'forearm.L', f, rot=(-0.25 - (0.9 if run else 0.15) * (0.5 + 0.5 * s), 0, 0))
            if carry != 'R':
                kb(ch, 'upperarm.R', f, rot=(-aa * s, 0, 0.12)); kb(ch, 'forearm.R', f, rot=(-0.25 - (0.9 if run else 0.15) * (0.5 - 0.5 * s), 0, 0))
        if 'tassel' in ch.arm.pose.bones:
            kb(ch, 'tassel', f, rot=(0.25 * math.sin(ph * 2 - 1), 0, 0.2 * math.sin(ph - 0.7)))


def wave(ch, f0, f1, side='L'):
    up = P(**{f'upperarm_{side}': (-0.3, 0, -2.3 if side == 'L' else 2.3)})
    for i, f in enumerate(range(f0, f1, 6)):
        w = 0.45 * math.sin(i * 1.4)
        kb(ch, 'upperarm.' + side, f, rot=up['upperarm.' + side])
        kb(ch, 'forearm.' + side, f, rot=(-0.3, 0, (w if side == 'L' else -w)))
    kb(ch, 'forearm.' + side, f1, rot=(-0.3, 0, 0))


def tassel_sway(ch, f0, f1, amp=0.08):
    if 'tassel' not in ch.arm.pose.bones:
        return
    for f in range(f0, f1 + 1, 6):
        kb(ch, 'tassel', f, rot=(amp * math.sin(f * 0.13), 0, amp * math.sin(f * 0.09)))


def shake(ch, f0, f1, bone='spine', amp=0.03, rate=0.9, base=(0, 0, 0)):
    """Sobbing shoulders / trembling."""
    for f in range(f0, f1 + 1, 3):
        kb(ch, bone, f, rot=(base[0] + amp * abs(math.sin(f * rate)), base[1], base[2]))

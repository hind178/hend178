"""Procedural environments: nostalgic Iraqi neighbourhood street + grocery shop,
the family house interior, the hospital room, and vehicles.

World layout (metres):
  STREET    origin (0,0): road along X, y 0..7; near sidewalk y<0 (Hind's side),
            shop on far side at x=0 (y=9.5); family home door at x=-18, y=-3.
  HOUSE     origin (100,0): living x0..6 y0..5 | kitchen x6..10 y0..5 |
            bedroom x0..6 y-4..0 | hallway x6..10 y-4..0, front door at (108,-4).
  HOSPITAL  origin (200,0)."""
import bpy, math, random
from . import look as LK
import numpy as np
from mathutils import Vector
from . import util as U
from . import character as C

SIDE_Z = 0.15            # sidewalk height


def camera_only(o):
    o.visible_diffuse = False; o.visible_glossy = False; o.visible_transmission = False
    o.visible_shadow = False; o.visible_volume_scatter = False
HOME_DOOR = (-18.0, -3.0)
SHOP = (0.0, 9.5)
HOUSE_O = Vector((100, 0, 0))
HOSP_O = Vector((200, 0, 0))


# ---------------------------------------------------------------- textures
def brick_img():
    img = bpy.data.images.get('tabouk_brick')
    if img:
        return img
    W, Hh = 512, 512
    rng = np.random.default_rng(3)
    a = np.zeros((Hh, W, 3))
    bh, bw = 32, 96
    mortar = np.array((0.62, 0.56, 0.46))
    a[:] = mortar
    for r in range(Hh // bh):
        off = (bw // 2) * (r % 2)
        for c in range(-1, W // bw + 1):
            x0 = c * bw + off + 3; y0 = r * bh + 3
            base = np.array((0.78, 0.62, 0.40)) * rng.uniform(0.85, 1.1) + rng.uniform(-0.03, 0.03, 3)
            xs = slice(max(x0, 0), min(x0 + bw - 6, W)); ys = slice(y0, y0 + bh - 6)
            a[ys, xs] = base
    a += rng.normal(0, 0.025, a.shape)
    return U.image_from_array('tabouk_brick', np.clip(a, 0, 1))


def tile_img():
    img = bpy.data.images.get('pavement_tiles')
    if img:
        return img
    W = 256
    rng = np.random.default_rng(4)
    a = np.zeros((W, W, 3)); a[:] = (0.45, 0.43, 0.40)
    for i in range(4):
        for j in range(4):
            v = rng.uniform(0.62, 0.72)
            a[i * 64 + 2:i * 64 + 62, j * 64 + 2:j * 64 + 62] = (v, v * 0.95, v * 0.88)
    a += rng.normal(0, 0.02, a.shape)
    return U.image_from_array('pavement_tiles', np.clip(a, 0, 1))


def floor_tile_img():
    img = bpy.data.images.get('terrazzo')
    if img:
        return img
    W = 256
    rng = np.random.default_rng(9)
    a = np.zeros((W, W, 3)); a[:] = (0.72, 0.68, 0.6)
    a += rng.normal(0, 0.04, (W, W, 1)) * (rng.random((W, W, 1)) > 0.85)
    a[::128, :] = (0.5, 0.47, 0.42); a[:, ::128] = (0.5, 0.47, 0.42)
    return U.image_from_array('terrazzo', np.clip(a, 0, 1))


def curb_mat():
    m = bpy.data.materials.get('curb_paint')
    if m:
        return m
    m = U.mat('curb_paint', (0.9, 0.75, 0.1), rough=0.6)
    nt = m.node_tree; p = nt.nodes['Principled BSDF']
    tc = nt.nodes.new('ShaderNodeTexCoord'); sep = nt.nodes.new('ShaderNodeSeparateXYZ')
    nt.links.new(tc.outputs['Object'], sep.inputs['Vector'])
    mm = nt.nodes.new('ShaderNodeMath'); mm.operation = 'PINGPONG'; mm.inputs[1].default_value = 0.5
    nt.links.new(sep.outputs['X'], mm.inputs[0])
    gt = nt.nodes.new('ShaderNodeMath'); gt.operation = 'GREATER_THAN'; gt.inputs[1].default_value = 0.25
    nt.links.new(mm.outputs[0], gt.inputs[0])
    mix = nt.nodes.new('ShaderNodeMix'); mix.data_type = 'RGBA'
    mix.inputs['A'].default_value = (0.02, 0.02, 0.02, 1); mix.inputs['B'].default_value = (0.85, 0.68, 0.08, 1)
    nt.links.new(gt.outputs[0], mix.inputs['Factor'])
    nt.links.new(mix.outputs['Result'], p.inputs['Base Color'])
    return m


def asphalt_mat():
    m = bpy.data.materials.get('asphalt')
    if m:
        return m
    m = U.mat('asphalt', (0.16, 0.155, 0.15), rough=0.85)
    nt = m.node_tree; p = nt.nodes['Principled BSDF']
    nz = nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 0.6; nz.inputs['Detail'].default_value = 6
    ramp = nt.nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color = (0.11, 0.105, 0.1, 1); ramp.color_ramp.elements[1].color = (0.26, 0.24, 0.21, 1)
    nt.links.new(nz.outputs['Fac'], ramp.inputs['Fac'])
    nt.links.new(ramp.outputs['Color'], p.inputs['Base Color'])
    nz2 = nt.nodes.new('ShaderNodeTexNoise'); nz2.inputs['Scale'].default_value = 300
    b = nt.nodes.new('ShaderNodeBump'); b.inputs['Strength'].default_value = 0.3
    nt.links.new(nz2.outputs['Fac'], b.inputs['Height']); nt.links.new(b.outputs['Normal'], p.inputs['Normal'])
    return m


def mats():
    return dict(
        brick=U.mat('brick', (0.78, 0.62, 0.4), rough=0.9, image=brick_img(), uv_scale=0.6, bump=0.3),
        plaster=U.mat('plaster_cream', (0.85, 0.77, 0.62), rough=0.92, bump=0.15),
        plaster2=U.mat('plaster_peach', (0.86, 0.66, 0.52), rough=0.92, bump=0.15),
        tiles=U.mat('pavement', (0.65, 0.62, 0.56), rough=0.85, image=tile_img(), uv_scale=0.8),
        asphalt=asphalt_mat(), curb=curb_mat(),
        metal_teal=U.mat('door_teal', (0.07, 0.38, 0.40), rough=0.45, metal=0.3),
        metal_green=U.mat('door_green', (0.12, 0.33, 0.14), rough=0.45, metal=0.3),
        metal_blue=U.mat('door_blue', (0.12, 0.22, 0.45), rough=0.45, metal=0.3),
        iron=U.mat('iron_black', (0.03, 0.03, 0.03), rough=0.4, metal=0.8),
        glass=U.mat('window_glass', (0.12, 0.16, 0.18), rough=0.05, metal=0.0, coat=1.0),
        wood=U.mat('wood_dark', (0.25, 0.13, 0.06), rough=0.55, bump=0.1),
        tank=U.mat('water_tank', (0.85, 0.85, 0.82), rough=0.4),
        dirt=U.mat('dust_ground', (0.55, 0.47, 0.36), rough=0.95, bump=0.2),
        palm=U.mat('palm_leaf', (0.17, 0.3, 0.09), rough=0.7, sheen=0.3),
        trunk=U.mat('palm_trunk', (0.33, 0.24, 0.15), rough=0.95, bump=0.6),
        pole=U.mat('pole_concrete', (0.55, 0.53, 0.5), rough=0.9),
        wire=U.mat('wire', (0.02, 0.02, 0.02), rough=0.5),
    )


# ---------------------------------------------------------------- street
def house_facade(name, x, y, w, h, side, M, coll, seed=0, door=True, door_mat=None):
    """Two-storey Iraqi house: brick front, parapet, metal door, barred windows,
    balcony, roof water tank + satellite dish.  side=-1 faces -Y (far side), +1 faces +Y."""
    rnd = random.Random(seed)
    d = 8.0
    cy = y - side * d / 2
    body = U.rbox(name, (w, d, h), (x, cy, h / 2), bevel=0.04, collection=coll,
                  mat_=M['brick'] if rnd.random() < 0.7 else M['plaster'])
    fy = y + side * 0.0
    par = U.rbox(name + '_parapet', (w + 0.1, 0.25, 0.5), (x, fy - side * 0.12, h + 0.25), bevel=0.03, collection=coll, mat_=M['plaster'])
    band = U.rbox(name + '_band', (w + 0.06, 0.12, 0.18), (x, fy + side * 0.04, h * 0.5), bevel=0.02, collection=coll, mat_=M['plaster'])
    objs = [body, par, band]
    if door:
        dm = door_mat or rnd.choice([M['metal_teal'], M['metal_green'], M['metal_blue']])
        dx = x + rnd.uniform(-w / 4, w / 4)
        frame = U.rbox(name + '_doorframe', (1.5, 0.12, 2.4), (dx, fy + side * 0.04, 1.2), bevel=0.02, collection=coll, mat_=M['plaster'])
        dr = U.rbox(name + '_door', (1.25, 0.08, 2.2), (dx, fy + side * 0.09, 1.12), bevel=0.02, collection=coll, mat_=dm)
        objs += [frame, dr]
        for k in range(3):
            objs.append(U.rbox(name + f'_doorpanel{k}', (1.0, 0.03, 0.5), (dx, fy + side * 0.135, 0.45 + k * 0.65), bevel=0.01, collection=coll, mat_=dm))
    for k, wx in enumerate((x - w / 3.2, x + w / 3.2)):
        for fl, wz in enumerate((1.6, 4.6)):
            if fl == 0 and door and abs(wx - dx) < 1.3:
                continue
            objs.append(U.rbox(name + f'_win{k}{fl}', (1.2, 0.08, 1.3), (wx, fy + side * 0.03, wz), bevel=0.01, collection=coll, mat_=M['glass']))
            objs.append(U.rbox(name + f'_sill{k}{fl}', (1.4, 0.2, 0.08), (wx, fy + side * 0.1, wz - 0.7), bevel=0.01, collection=coll, mat_=M['plaster']))
            for b in range(5):
                objs.append(U.cyl(name + f'_bar{k}{fl}{b}', 0.012, 1.3, (wx - 0.5 + b * 0.25, fy + side * 0.14, wz - 0.65), collection=coll, mat_=M['iron'], seg=6))
    if rnd.random() < 0.6:
        bx = x + rnd.uniform(-w / 5, w / 5)
        objs.append(U.rbox(name + '_balcony', (2.6, 1.0, 0.12), (bx, fy + side * 0.5, 3.4), bevel=0.02, collection=coll, mat_=M['plaster']))
        for b in range(12):
            objs.append(U.cyl(name + f'_rail{b}', 0.012, 0.9, (bx - 1.25 + b * 0.227, fy + side * 0.98, 3.45), collection=coll, mat_=M['iron'], seg=6))
        objs.append(U.cyl(name + '_railtop', 0.02, 2.6, (bx - 1.3, fy + side * 0.98, 4.36), rot=(0, math.pi / 2, 0), collection=coll, mat_=M['iron'], seg=8))
    # roof water tank + dish
    tx = x + rnd.uniform(-w / 3, w / 3)
    tank = U.lathe(name + '_tank', [(0.5, 0), (0.55, 0.1), (0.55, 1.0), (0.4, 1.2), (0.1, 1.25)], 20, collection=coll, mat_=M['tank'], subsurf=1)
    tank.location = (tx, cy, h + 0.4)
    stand = U.rbox(name + '_tankstand', (1.2, 1.2, 0.4), (tx, cy, h + 0.2), bevel=0.0, collection=coll, mat_=M['iron'])
    objs += [tank, stand]
    if rnd.random() < 0.7:
        dish = U.lathe(name + '_dish', [(0.0, 0), (0.3, 0.05), (0.45, 0.14)], 20, collection=coll, mat_=M['tank'], subsurf=1, cap_top=False)
        dish.location = (x - side * 1.0 + rnd.uniform(-2, 2), cy, h + 1.0); dish.rotation_euler = (side * 1.1, 0, 0)
        objs.append(dish)
    return objs


def palm(name, loc, coll, M, h=7.0, seed=0):
    rnd = random.Random(seed)
    trunk = U.lathe(name + '_trunk', [(0.22, 0), (0.18, h * 0.5), (0.16, h)], 12, collection=coll, mat_=M['trunk'], subsurf=0,
                    shape=lambda t, z: 1 + 0.1 * math.sin(z * 9))
    trunk.location = loc
    parts = [trunk]
    for i in range(11):
        a = 2 * math.pi * i / 11 + rnd.uniform(-0.2, 0.2)
        L = rnd.uniform(2.0, 2.8)
        leaf = U.sphere(name + f'_leaf{i}', 1.0, (0, 0, 0), (0.28, L / 2, 0.02), collection=coll, mat_=M['palm'], seg=12, rings=6)
        droop = rnd.uniform(0.3, 0.8)
        leaf.location = (loc[0] + math.sin(a) * L * 0.45, loc[1] - math.cos(a) * L * 0.45, loc[2] + h - 0.1 - droop * 0.5)
        leaf.rotation_euler = (droop, 0, a + math.pi)
        parts.append(leaf)
    return parts


def wire_curve(name, p0, p1, sag, coll, M):
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'
    sp = cu.splines.new('POLY'); n = 12
    sp.points.add(n - 1)
    for i in range(n):
        t = i / (n - 1)
        p = Vector(p0).lerp(Vector(p1), t)
        p.z -= sag * 4 * t * (1 - t)
        sp.points[i].co = (*p, 1)
    cu.bevel_depth = 0.008
    o = bpy.data.objects.new(name, cu); coll.objects.link(o)
    cu.materials.append(M['wire'])
    return o


def build_street(root):
    coll = U.coll('ENV_Street', root)
    M = mats()
    # ground
    U.plane('road', 160, 7, (0, 3.5, 0), collection=coll, mat_=M['asphalt'])
    U.plane('road_dirt_far', 160, 60, (0, 40, -0.02), collection=coll, mat_=M['dirt'])
    U.plane('ground_far', 400, 300, (0, 0, -0.05), collection=coll, mat_=M['dirt'])
    U.rbox('sidewalk_near', (160, 3.0, SIDE_Z), (0, -1.5, SIDE_Z / 2), bevel=0.0, collection=coll, mat_=M['tiles'])
    U.rbox('sidewalk_far', (160, 2.5, SIDE_Z), (0, 8.25, SIDE_Z / 2), bevel=0.0, collection=coll, mat_=M['tiles'])
    # painted curbs (black/yellow)
    for y, nm in ((-0.12, 'curb_near'), (7.12, 'curb_far')):
        c = U.rbox(nm, (160, 0.24, SIDE_Z + 0.06), (0, y, (SIDE_Z + 0.06) / 2), bevel=0.02, collection=coll, mat_=M['curb'])
    # road markings (faded)
    dash = U.plane('dash', 2.0, 0.12, (0, 3.5, 0.003), collection=coll,
                   mat_=U.mat('road_paint', (0.75, 0.73, 0.66), rough=0.8))
    for i in range(-30, 30):
        if i:
            U.instance(dash, f'dash{i}', (i * 5.0, 3.5, 0.003), collection=coll)
    # houses: near side (facing +Y) and far side (facing -Y)
    xs = -60
    i = 0
    while xs < 60:
        w = random.Random(i).uniform(7, 10)
        cx = xs + w / 2
        door_mat = M['metal_teal'] if abs(cx - HOME_DOOR[0]) < w / 2 else None
        if abs(cx - HOME_DOOR[0]) < w / 2:
            # family home centred on its door; narrow neighbour fills the rest of the slot (no overlaps)
            hw_ = 7.4
            home_objs = house_facade('home', HOME_DOOR[0], -3.0, hw_, 6.6, 1, M, coll, seed=42, door=False)
            gap = (HOME_DOOR[0] - hw_ / 2) - xs
            if gap > 0.5:
                house_facade('near_alley', xs + gap / 2, -3.0, gap - 0.1, 5.6, 1, M, coll, seed=77, door=False)
            hm = M['metal_teal']
            fr = U.rbox('home_doorframe', (1.6, 0.14, 2.5), (HOME_DOOR[0], -2.95, 1.25), bevel=0.02, collection=coll, mat_=M['plaster'])
            dr = U.rbox('home_door', (1.3, 0.08, 2.25), (HOME_DOOR[0] - 0.65, -2.9, 1.125 + 0.15), bevel=0.02, collection=coll, mat_=hm)
            # pivot door at hinge so it can open
            me = dr.data
            for v in me.vertices:
                v.co.x += 0.65
            dr.location.x -= 0.65
            dr.name = 'home_door'
            step = U.rbox('home_step', (1.8, 0.5, 0.15), (HOME_DOOR[0], -2.7, SIDE_Z + 0.07), bevel=0.02, collection=coll, mat_=M['plaster'])
            dark = U.plane('home_doorway_dark', 1.3, 2.25, (HOME_DOOR[0], -2.98, 1.27), (math.pi / 2, 0, 0), collection=coll,
                           mat_=U.mat('doorway_interior', (0.12, 0.09, 0.07), rough=1.0))
        else:
            house_facade(f'near{i}', cx, -3.0, w - 0.15, random.Random(i).uniform(5.8, 7.0), 1, M, coll, seed=i)
        w2 = w   # same slot width as the near side: far houses never overlap
        if not (xs < 3.1 and xs + w2 > -3.1):
            house_facade(f'far{i}', xs + w2 / 2, 9.5, w2 - 0.15, random.Random(i + 9).uniform(5.8, 7.2), -1, M, coll, seed=i + 100)
        else:   # slot shared with the shop: fill only what is left on either side
            for k, (a_, b_) in enumerate(((xs, -3.05), (3.05, xs + w2))):
                if b_ - a_ > 1.0:
                    house_facade(f'far{i}_{k}', (a_ + b_) / 2, 9.5, b_ - a_ - 0.1, 6.4 + 0.5 * k, -1, M, coll,
                                 seed=i + 200 + k, door=(b_ - a_) > 3.5)
        xs += w
        if abs(cx - HOME_DOOR[0]) < w / 2:
            xs = HOME_DOOR[0] + 7.4 / 2 + 0.05
        i += 1
    for k, px in enumerate((-30, -9, 13, 31)):
        palm(f'palm{k}', (px, 12.5 + k % 2, 0), coll, M, h=7 + k % 3, seed=k)
    for k, px in enumerate((-40, -24, 22, 44)):
        palm(f'palmN{k}', (px, -9, 0), coll, M, h=8, seed=k + 10)
    # electricity poles + sagging wires (very Baghdad)
    poles = []
    for k, px in enumerate(range(-48, 60, 14)):
        p = U.cyl(f'pole{k}', 0.12, 8.5, (px, -0.55, 0), collection=coll, mat_=M['pole'], seg=10, r2=0.08)
        arm_ = U.rbox(f'polearm{k}', (0.08, 1.4, 0.08), (px, -0.55, 8.0), bevel=0, collection=coll, mat_=M['iron'])
        poles.append(px)
    for a, b in zip(poles, poles[1:]):
        for j, dy in enumerate((-1.1, -0.55, 0.0, 0.1)):
            wire_curve(f'wire{a}_{j}', (a, -0.55 + dy * 0.6, 8.0 - j * 0.05), (b, -0.55 + dy * 0.6, 8.0 - j * 0.05), 0.5 + j * 0.15, coll, M)
    # wires across the street to the shop
    wire_curve('wire_cross', (poles[3], -0.55, 7.9), (2.0, 9.4, 5.8), 0.9, coll, M)
    build_shop(coll, M)
    return coll


def build_shop(coll, M):
    """Small grocery shop (دكان) across the road with produce crates and awning."""
    x, y = SHOP
    inner = U.mat('shop_inside', (0.55, 0.45, 0.33), rough=0.9)
    # hollow shell: side walls, back wall, roof, lintel over the open front
    for nm, sz, c in (('shop_wallL', (0.7, 6.0, 4.2), (x - 2.65, y + 3.0, 2.1)), ('shop_wallR', (0.7, 6.0, 4.2), (x + 2.65, y + 3.0, 2.1)),
                      ('shop_wallB', (6.0, 0.5, 4.2), (x, y + 5.75, 2.1)), ('shop_roof', (6.0, 6.0, 0.4), (x, y + 3.0, 4.0)),
                      ('shop_lintel', (6.0, 0.4, 1.0), (x, y + 0.2, 3.6))):
        U.rbox(nm, sz, c, bevel=0.03, collection=coll, mat_=M['plaster2'])
    for nm, sz, c in (('shop_inL', (0.02, 5.2, 3.2), (x - 2.29, y + 2.9, 1.75)), ('shop_inR', (0.02, 5.2, 3.2), (x + 2.29, y + 2.9, 1.75)),
                      ('shop_inB', (4.6, 0.02, 3.2), (x, y + 5.49, 1.75)), ('shop_inC', (4.6, 5.2, 0.02), (x, y + 2.9, 3.35))):
        U.rbox(nm, sz, c, bevel=0.0, collection=coll, mat_=inner)
    U.rbox('shop_floor', (4.6, 5.4, 0.05), (x, y + 2.8, SIDE_Z + 0.03), bevel=0, collection=coll, mat_=M['tiles'])
    # shutter rolled up + sign board (blank painted panel: no text/logos)
    U.cyl('shop_shutter', 0.22, 4.8, (x - 2.4, y - 0.05, 3.3), rot=(0, math.pi / 2, 0), collection=coll,
          mat_=U.mat('shutter', (0.5, 0.5, 0.48), rough=0.4, metal=0.7), seg=16)
    U.rbox('shop_sign', (5.6, 0.12, 0.7), (x, y - 0.08, 3.85), bevel=0.03, collection=coll,
           mat_=U.mat('sign_green', (0.08, 0.38, 0.2), rough=0.5))
    U.rbox('shop_signstripe', (5.4, 0.13, 0.12), (x, y - 0.09, 3.65), bevel=0.01, collection=coll,
           mat_=U.mat('sign_white', (0.9, 0.88, 0.8), rough=0.5))
    # striped awning
    aw = U.mat('awning', (0.8, 0.2, 0.15), rough=0.7, sheen=0.5)
    nt = aw.node_tree; p = nt.nodes['Principled BSDF']
    tc = nt.nodes.new('ShaderNodeTexCoord'); sep = nt.nodes.new('ShaderNodeSeparateXYZ')
    nt.links.new(tc.outputs['Object'], sep.inputs['Vector'])
    w_ = nt.nodes.new('ShaderNodeMath'); w_.operation = 'PINGPONG'; w_.inputs[1].default_value = 0.25
    nt.links.new(sep.outputs['X'], w_.inputs[0])
    g = nt.nodes.new('ShaderNodeMath'); g.operation = 'GREATER_THAN'; g.inputs[1].default_value = 0.125
    nt.links.new(w_.outputs[0], g.inputs[0])
    mix = nt.nodes.new('ShaderNodeMix'); mix.data_type = 'RGBA'
    mix.inputs['A'].default_value = (0.85, 0.82, 0.72, 1); mix.inputs['B'].default_value = (0.7, 0.12, 0.08, 1)
    nt.links.new(g.outputs[0], mix.inputs['Factor']); nt.links.new(mix.outputs['Result'], p.inputs['Base Color'])
    awn = U.rbox('shop_awning', (5.8, 1.6, 0.04), (x, y - 0.7, 3.05), bevel=0.0, collection=coll, mat_=aw)
    awn.rotation_euler = (-0.35, 0, 0)
    # crates of produce on the pavement
    crate_m = U.mat('crate_wood', (0.55, 0.38, 0.2), rough=0.8, bump=0.2)
    veg = dict(tomato=U.mat('tomato', (0.75, 0.06, 0.03), rough=0.25, coat=0.5, sss=0.1),
               cucumber=U.mat('cucumber', (0.12, 0.3, 0.06), rough=0.4),
               onion=U.mat('onion', (0.65, 0.4, 0.18), rough=0.45),
               eggplant=U.mat('eggplant', (0.14, 0.03, 0.12), rough=0.2, coat=0.6),
               orange=U.mat('orange', (0.9, 0.45, 0.05), rough=0.5))
    tom = U.sphere('tomato_src', 0.045, (0, 0, -50), (1, 1, 0.85), collection=coll, mat_=veg['tomato'], seg=14, rings=8)
    cuc = U.sphere('cucumber_src', 1.0, (0, 0, -50), (0.025, 0.09, 0.025), collection=coll, mat_=veg['cucumber'], seg=10, rings=6)
    oni = U.sphere('onion_src', 0.04, (0, 0, -50), collection=coll, mat_=veg['onion'], seg=12, rings=7)
    egg = U.sphere('eggplant_src', 1.0, (0, 0, -50), (0.04, 0.09, 0.04), collection=coll, mat_=veg['eggplant'], seg=12, rings=7)
    ora = U.sphere('orange_src', 0.045, (0, 0, -50), collection=coll, mat_=veg['orange'], seg=12, rings=7)
    srcs = [tom, cuc, oni, egg, ora]
    rnd = random.Random(11)
    k = 0
    for row, (cy, cz) in enumerate(((y - 0.2, 0.55), (y + 0.15, 0.85))):
        for cx in np.linspace(x - 2.0, x + 2.0, 5):
            crate = U.rbox(f'crate{row}_{k}', (0.7, 0.45, 0.25), (cx, cy, cz), bevel=0.01, collection=coll, mat_=crate_m)
            crate.rotation_euler = (-0.25 * row, 0, 0)
            src = srcs[(k + row) % len(srcs)]
            for j in range(10):
                U.instance(src, f'veg{k}_{j}', (cx + rnd.uniform(-0.28, 0.28), cy + rnd.uniform(-0.15, 0.15), cz + 0.15 + rnd.uniform(0, 0.05)),
                           (rnd.uniform(0, 3), rnd.uniform(0, 3), rnd.uniform(0, 3)), collection=coll)
            k += 1
        U.rbox(f'stand{row}', (4.8, 0.5, 0.05), (x, cy, cz - 0.16), bevel=0, collection=coll, mat_=crate_m)
    for lx in (-1.6, 1.6):
        U.rbox(f'stand_leg{lx}', (0.06, 0.06, 0.6), (x + lx, y - 0.2, 0.3), bevel=0, collection=coll, mat_=crate_m)
    # shelves inside with tins/boxes
    for sh in range(3):
        U.rbox(f'shelf{sh}', (4.2, 0.4, 0.04), (x, y + 4.0, 0.8 + sh * 0.6), bevel=0, collection=coll, mat_=M['wood'])
        for j in range(14):
            col = [(0.8, 0.2, 0.1), (0.2, 0.4, 0.75), (0.95, 0.8, 0.2), (0.3, 0.6, 0.3)][(j + sh) % 4]
            U.rbox(f'tin{sh}_{j}', (0.18, 0.18, 0.26), (x - 1.9 + j * 0.29, y + 4.0, 0.95 + sh * 0.6), bevel=0.02, collection=coll,
                   mat_=U.mat(f'tin{(j + sh) % 4}', col, rough=0.35, metal=0.4))
    LK.area('L_shop_in', (x, y + 2.0, 3.0), (0, 0, 0), 3.5, 160, coll, size_y=3.0)
    U.rbox('shop_counter', (0.6, 1.8, 1.0), (x + 1.75, y + 2.9, 0.6), bevel=0.02, collection=coll, mat_=M['wood'])
    U.rbox('shop_scale', (0.35, 0.3, 0.12), (x + 1.75, y + 2.6, 1.16), bevel=0.02, collection=coll,
           mat_=U.mat('scale_metal', (0.7, 0.7, 0.7), metal=1.0, rough=0.25))


# ---------------------------------------------------------------- vehicles
def build_car(name, kind, color, coll):
    """Boxy 80s/90s Iraqi street cars: 'sedan', 'taxi' (orange/white), 'van', 'ambulance'.
    Returns an empty (animate it) parenting body + wheels."""
    root = bpy.data.objects.new(name, None); coll.objects.link(root)
    body_m = U.mat(f'carpaint_{name}', color, rough=0.25, metal=0.3, coat=1.0)
    white = U.mat('carpaint_white', (0.85, 0.85, 0.82), rough=0.25, coat=1.0)
    glass = U.mat('car_glass', (0.05, 0.07, 0.08), rough=0.05, coat=1.0)
    tyre = U.mat('tyre', (0.03, 0.03, 0.03), rough=0.8)
    chrome = U.mat('chrome', (0.8, 0.8, 0.8), metal=1.0, rough=0.15)
    parts = []
    if kind in ('sedan', 'taxi'):
        L, W = 4.5, 1.72
        parts.append(U.rbox(name + '_low', (L, W, 0.62), (0, 0, 0.62), bevel=0.08, collection=coll, mat_=body_m))
        parts.append(U.rbox(name + '_cab', (2.3, W - 0.12, 0.55), (-0.15, 0, 1.2), bevel=0.1, collection=coll,
                            mat_=white if kind == 'taxi' else body_m))
        for sx in (1, -1):
            parts.append(U.rbox(name + f'_win{sx}', (2.0, 0.02, 0.38), (-0.15, sx * (W / 2 - 0.05), 1.22), bevel=0.01, collection=coll, mat_=glass))
        parts.append(U.rbox(name + '_ws', (0.04, W - 0.25, 0.42), (1.0, 0, 1.2), bevel=0.01, collection=coll, mat_=glass, rot=(0, -0.55, 0)))
        parts.append(U.rbox(name + '_rw', (0.04, W - 0.25, 0.42), (-1.32, 0, 1.2), bevel=0.01, collection=coll, mat_=glass, rot=(0, 0.55, 0)))
        if kind == 'taxi':
            parts.append(U.rbox(name + '_stripe', (L + 0.02, W + 0.02, 0.12), (0, 0, 0.75), bevel=0.02, collection=coll, mat_=white))
        wz, wxs = 0.33, (1.4, -1.4)
    else:
        L, W = 4.9, 1.9
        hm = white if kind == 'ambulance' else body_m
        parts.append(U.rbox(name + '_box', (L, W, 1.75), (0, 0, 1.25), bevel=0.12, collection=coll, mat_=hm))
        parts.append(U.rbox(name + '_ws', (0.05, W - 0.2, 0.7), (L / 2 - 0.05, 0, 1.55), bevel=0.02, collection=coll, mat_=glass, rot=(0, -0.2, 0)))
        for sx in (1, -1):
            parts.append(U.rbox(name + f'_win{sx}', (1.0, 0.02, 0.55), (1.6, sx * (W / 2 + 0.005), 1.6), bevel=0.01, collection=coll, mat_=glass))
        if kind == 'ambulance':
            red = U.mat('amb_red', (0.75, 0.05, 0.04), rough=0.4)
            for sx in (1, -1):
                parts.append(U.rbox(name + f'_stripe{sx}', (L - 0.3, 0.02, 0.18), (0, sx * (W / 2 + 0.01), 1.0), bevel=0.0, collection=coll, mat_=red))
                cr1 = U.rbox(name + f'_cross{sx}a', (0.5, 0.02, 0.14), (-0.8, sx * (W / 2 + 0.012), 1.55), bevel=0, collection=coll, mat_=red)
                cr2 = U.rbox(name + f'_cross{sx}b', (0.14, 0.02, 0.5), (-0.8, sx * (W / 2 + 0.012), 1.55), bevel=0, collection=coll, mat_=red)
                parts += [cr1, cr2]
            for sx, colr, nm in ((0.5, (0.1, 0.3, 1.0), 'blue'), (-0.5, (1.0, 0.1, 0.05), 'red')):
                lm = U.mat(f'beacon_{nm}', colr, emission=colr, estr=0.0)
                parts.append(U.rbox(name + f'_beacon_{nm}', (0.3, 0.5, 0.15), (1.6, sx * 0.55, 2.2), bevel=0.05, collection=coll, mat_=lm))
        wz, wxs = 0.36, (1.6, -1.6)
    for sx in (1, -1):
        parts.append(U.rbox(name + f'_light{sx}', (0.05, 0.3, 0.16), (L / 2, sx * (W / 2 - 0.3), 0.75), bevel=0.02, collection=coll,
                            mat_=U.mat('headlight', (0.9, 0.9, 0.8), emission=(1, 0.95, 0.8), estr=0.5)))
    parts.append(U.rbox(name + '_bumper', (0.1, W + 0.05, 0.14), (L / 2 + 0.02, 0, 0.42), bevel=0.03, collection=coll, mat_=chrome))
    parts.append(U.rbox(name + '_bumperB', (0.1, W + 0.05, 0.14), (-L / 2 - 0.02, 0, 0.42), bevel=0.03, collection=coll, mat_=chrome))
    for p in parts:
        p.parent = root
    wheel_src = None
    for wx in wxs:
        for sy in (1, -1):
            wh = U.cyl(f'{name}_wheel{wx}{sy}', wz, 0.22, (wx, sy * (W / 2 - 0.05) - 0.11, wz), rot=(-math.pi / 2, 0, 0), collection=coll, mat_=tyre, seg=20)
            hub = U.cyl(f'{name}_hub{wx}{sy}', wz * 0.55, 0.23, (0, 0, -0.005), collection=coll, mat_=chrome, seg=12)
            hub.parent = wh
            wh.parent = root
    return root


# ---------------------------------------------------------------- props
def build_props(root):
    coll = U.coll('PROPS', root)
    bag_m = U.mat('plastic_bag', (0.85, 0.85, 0.8), rough=0.35, sss=0.2, alpha=0.95)
    bag = U.lathe('veg_bag', [(0.06, 0.0), (0.13, 0.04), (0.15, 0.18), (0.12, 0.3), (0.05, 0.34)], 18, sx=1.0, sy=0.7,
                  collection=coll, mat_=bag_m, subsurf=1, shape=lambda t, z: 1 + 0.06 * math.sin(t * 5) * z * 4)
    # handles
    for sx in (1, -1):
        h = U.lathe(f'veg_bag_handle{sx}', [(0.04, 0.0), (0.04, 0.003)], 12, collection=coll, mat_=bag_m, subsurf=0)
    # torn bag on road (flattened, ripped)
    torn = U.lathe('torn_bag', [(0.02, 0.0), (0.2, 0.01), (0.22, 0.03), (0.15, 0.05)], 20, sx=1.3, sy=0.8,
                   collection=coll, mat_=bag_m, subsurf=1, cap_top=False,
                   shape=lambda t, z: 1 + 0.35 * (math.sin(t * 3) > 0.6) * (z > 0.02) - 0.2 * math.sin(t * 7))
    for o in (bag, torn):
        o.location = (0, 0, -60)
    coin_m = U.mat('coin', (0.8, 0.75, 0.6), metal=1.0, rough=0.3)
    coins = U.cyl('coins', 0.012, 0.003, (0, 0, -60), collection=coll, mat_=coin_m, seg=14)
    note = U.rbox('banknote', (0.07, 0.15, 0.002), (0, 0, -60), bevel=0, collection=coll,
                  mat_=U.mat('banknote', (0.55, 0.65, 0.5), rough=0.7))
    toys = dict(
        ball=U.sphere('toy_ball', 0.09, (0, 0, -60), collection=coll, seg=20, rings=10,
                      mat_=U.mat('ball_red', (0.85, 0.15, 0.1), rough=0.3, coat=0.5)),
        car=U.rbox('toy_car', (0.18, 0.09, 0.06), (0, 0, -60), bevel=0.02, collection=coll,
                   mat_=U.mat('toycar_blue', (0.1, 0.3, 0.8), rough=0.3, coat=0.6)))
    for i, c in enumerate([(0.9, 0.7, 0.1), (0.2, 0.6, 0.3), (0.8, 0.2, 0.3), (0.2, 0.4, 0.8)]):
        toys[f'block{i}'] = U.rbox(f'toy_block{i}', (0.07, 0.07, 0.07), (0, 0, -60), bevel=0.008, collection=coll,
                                   mat_=U.mat(f'block{i}', c, rough=0.5))
    return coll


# ---------------------------------------------------------------- house interior
def build_house(root):
    coll = U.coll('ENV_House', root)
    O = HOUSE_O
    M = mats()
    wall_m = U.mat('wall_paint', (0.86, 0.78, 0.62), rough=0.9, bump=0.08)
    wall_low = U.mat('wall_lower', (0.42, 0.55, 0.52), rough=0.6)
    floor_m = U.mat('terrazzo', (0.72, 0.68, 0.6), rough=0.4, image=floor_tile_img(), uv_scale=0.8, coat=0.2)
    H = 3.0
    U.plane('house_floor', 12, 11, O + Vector((5, 0.5, 0)), collection=coll, mat_=floor_m)
    U.plane('house_ceiling', 12, 11, O + Vector((5, 0.5, H)), (math.pi, 0, 0), collection=coll, mat_=wall_m)

    def wall(nm, a, b, openings=()):
        """Wall from a to b (2D, relative), openings: list of (t0,t1,z0,z1) along wall."""
        a = Vector(a); b = Vector(b); L = (b - a).length; d = (b - a).normalized()
        ang = math.atan2(d.y, d.x)
        cuts = sorted(openings)
        segs = []; t = 0.0
        for (t0, t1, z0, z1) in cuts:
            segs.append((t, t0, 0, H))
            if z0 > 0:
                segs.append((t0, t1, 0, z0))
            segs.append((t0, t1, z1, H))
            t = t1
        segs.append((t, L, 0, H))
        for i, (s0, s1, z0, z1) in enumerate(segs):
            if s1 - s0 < 1e-3 or z1 - z0 < 1e-3:
                continue
            c = a + d * (s0 + s1) / 2
            w = U.rbox(f'{nm}_{i}', (s1 - s0, 0.18, z1 - z0), O + Vector((c.x, c.y, (z0 + z1) / 2)), bevel=0, collection=coll, mat_=wall_m)
            w.rotation_euler = (0, 0, ang)
            if z0 == 0 and z1 > 1.0:
                for side in (1, -1):
                    lw = U.rbox(f'{nm}_{i}_dado{side}', (s1 - s0, 0.01, 1.0), O + Vector((c.x, c.y, 0.5)) + Vector((-d.y, d.x, 0)) * 0.095 * side,
                                bevel=0, collection=coll, mat_=wall_low)
                    lw.rotation_euler = (0, 0, ang)
    # outer walls
    wall('w_north', (0, 5), (10, 5), [(2.2, 3.8, 1.0, 2.5), (7.4, 8.6, 1.2, 2.3)])     # living window, kitchen window
    wall('w_west', (0, -4), (0, 5), [(1.0, 2.2, 1.0, 2.3)])                            # bedroom window
    wall('w_east', (10, -4), (10, 5))
    wall('w_south', (0, -4), (10, -4), [(7.4, 8.6, 0.0, 2.3)])                         # front door at x 7.4..8.6
    wall('w_mid_x', (0, 0), (10, 0), [(1.0, 2.2, 0, 2.3), (6.6, 7.8, 0, 2.3)])          # living<->bedroom, kitchen<->hall
    wall('w_mid_y', (6, -4), (6, 5), [(1.3, 2.5, 0, 2.3), (5.6, 6.8, 0, 2.3)])          # bedroom<->hall, living<->kitchen
    # front door (hinged at x=7.4)
    door = U.rbox('front_door', (1.2, 0.07, 2.3), O + Vector((7.4, -4.0, 1.15)), bevel=0.015, collection=coll, mat_=M['metal_teal'])
    for v in door.data.vertices:
        v.co.x += 0.6
    U.rbox('front_door_glass', (0.5, 0.08, 0.5), O + Vector((8.0, -4.0, 1.75)), bevel=0.01, collection=coll,
           mat_=U.mat('door_glass_frost', (0.8, 0.85, 0.85), rough=0.3, emission=(1, 0.95, 0.85), estr=1.5)).parent = door
    # outside backdrop behind door (bright street)
    U.plane('door_outside', 8, 5, O + Vector((8, -7, 2)), (math.pi / 2, 0, 0), collection=coll,
            mat_=U.mat('outside_glow', (0.9, 0.8, 0.6), emission=(1.0, 0.85, 0.65), estr=1.0))
    camera_only(bpy.data.objects['door_outside'])
    U.plane('door_outside_ground', 8, 3, O + Vector((8, -5.5, 0.001)), collection=coll, mat_=M['tiles'])
    # window/fill lights (area lights are far cheaper to sample than emissive panes)
    LK.area('L_living_win', O + Vector((3.0, 4.7, 1.8)), (math.radians(90), 0, 0), 1.6, 110, coll, size_y=1.5)
    LK.area('L_kitchen_win', O + Vector((8.0, 4.7, 1.8)), (math.radians(90), 0, 0), 1.3, 80, coll, size_y=1.2)
    LK.area('L_bed_win', O + Vector((0.3, -2.4, 1.7)), (0, math.radians(-90), 0), 1.4, 70, coll, size_y=1.3)
    LK.area('L_living_fill', O + Vector((3.0, 2.5, 2.9)), (0, 0, 0), 3.0, 55, coll, size_y=2.5)
    LK.area('L_kitchen_fill', O + Vector((8.0, 2.5, 2.9)), (0, 0, 0), 2.5, 45, coll, size_y=2.5)
    LK.area('L_bed_fill', O + Vector((3.0, -2.0, 2.9)), (0, 0, 0), 3.0, 45, coll, size_y=2.0)
    LK.area('L_hall_fill', O + Vector((8.0, -2.0, 2.9)), (0, 0, 0), 2.0, 35, coll, size_y=2.0)
    LK.area('L_door_out', O + Vector((8.0, -4.6, 1.5)), (math.radians(-90), 0, 0), 1.2, 120, coll, size_y=2.2)
    # windows: emissive sky panes (camera-visible only) + iron grill
    for nm, c, rot in (('win_living', (3.0, 5.1, 1.75), 0), ('win_kitchen', (8.0, 5.1, 1.75), 0), ('win_bed', (-0.1, -2.4, 1.65), math.pi / 2)):
        pane = U.plane(nm, 1.6 if 'kitchen' not in nm else 1.2, 1.5, O + Vector(c), (math.pi / 2, 0, rot), collection=coll,
                       mat_=U.mat('window_sky', (0.8, 0.85, 0.9), emission=(1.0, 0.92, 0.8), estr=1.1))
        if rot == 0:
            pane.location.y += 0.01
        camera_only(pane)
        for b in range(5):
            bar = U.cyl(f'{nm}_bar{b}', 0.012, 1.5, O + Vector(c) + (Vector((-0.6 + b * 0.3, -0.06, -0.75)) if rot == 0 else Vector((0.06, -0.6 + b * 0.3, -0.75))),
                        collection=coll, mat_=M['iron'], seg=6)
    # ---- living room
    carpet = U.plane('carpet', 3.4, 2.5, O + Vector((3, 2.4, 0.005)), collection=coll,
                     mat_=U.mat('carpet', (0.45, 0.05, 0.06), rough=0.95, sheen=0.8, image=C.carpet_img()))
    uvl = carpet.data.uv_layers[0]
    for i, uv in enumerate([(0, 0), (1, 0), (1, 1), (0, 1)]):
        uvl.data[i].uv = uv
    cush_m = U.mat('cushion', (0.55, 0.12, 0.1), rough=0.85, sheen=0.7)
    cush2 = U.mat('cushion_gold', (0.75, 0.55, 0.2), rough=0.8, sheen=0.7)
    for i in range(5):
        U.rbox(f'doshak_n{i}', (1.0, 0.7, 0.16), O + Vector((0.8 + i * 1.05, 4.5, 0.08)), bevel=0.06, collection=coll, mat_=cush_m)
        U.rbox(f'pillow_n{i}', (0.8, 0.22, 0.45), O + Vector((0.8 + i * 1.05, 4.75, 0.38)), bevel=0.1, collection=coll, mat_=cush2 if i % 2 else cush_m,
               rot=(-0.2, 0, 0))
    for i in range(3):
        U.rbox(f'doshak_w{i}', (0.7, 1.0, 0.16), O + Vector((0.45, 1.0 + i * 1.05, 0.08)), bevel=0.06, collection=coll, mat_=cush_m)
        U.rbox(f'pillow_w{i}', (0.22, 0.8, 0.45), O + Vector((0.2, 1.0 + i * 1.05, 0.38)), bevel=0.1, collection=coll, mat_=cush2 if i % 2 == 0 else cush_m)
    U.rbox('tv_stand', (1.0, 0.5, 0.6), O + Vector((5.3, 4.5, 0.3)), bevel=0.02, collection=coll, mat_=M['wood'])
    U.rbox('tv_crt', (0.6, 0.5, 0.48), O + Vector((5.3, 4.5, 0.85)), bevel=0.05, collection=coll,
           mat_=U.mat('tv_plastic', (0.18, 0.16, 0.14), rough=0.4))
    U.rbox('tv_screen', (0.46, 0.02, 0.36), O + Vector((5.3, 4.24, 0.86)), bevel=0.03, collection=coll,
           mat_=U.mat('tv_glass', (0.05, 0.06, 0.06), rough=0.1, coat=1.0))
    U.rbox('wall_shelf', (1.4, 0.25, 0.04), O + Vector((1.2, 4.85, 2.0)), bevel=0, collection=coll, mat_=M['wood'])
    clock = U.cyl('wall_clock', 0.2, 0.04, O + Vector((4.6, 4.9, 2.3)), rot=(math.pi / 2, 0, 0), collection=coll,
                  mat_=U.mat('clock_face', (0.92, 0.9, 0.82), rough=0.4), seg=24)
    U.rbox('tray_table', (0.7, 0.7, 0.3), O + Vector((1.25, 3.6, 0.15)), bevel=0.03, collection=coll,
           mat_=U.mat('brass_tray', (0.75, 0.55, 0.25), metal=0.9, rough=0.3))
    for i in range(3):
        U.lathe(f'tea_glass{i}', [(0.018, 0), (0.024, 0.04), (0.02, 0.07), (0.026, 0.09)], 14, collection=coll,
                mat_=U.mat('istikan', (0.55, 0.18, 0.05), rough=0.05, transmission=0.6), subsurf=1, cap_top=False).location = O + Vector((1.1 + i * 0.12, 3.55, 0.31))
    # ceiling fan
    fan = U.cyl('ceiling_fan_hub', 0.12, 0.12, O + Vector((3, 2.5, 2.8)), collection=coll, mat_=U.mat('fan_white', (0.85, 0.85, 0.8), rough=0.4), seg=16)
    for i in range(3):
        bl = U.rbox(f'fan_blade{i}', (0.7, 0.12, 0.01), (0.4, 0, 0.05), bevel=0, collection=coll, mat_=U.mat('fan_white', (0.85, 0.85, 0.8)))
        bl.parent = fan; bl.rotation_euler = (0, 0, i * 2.094)
        bl.location = (math.cos(i * 2.094) * 0.4, math.sin(i * 2.094) * 0.4, 0.05)
    # ---- kitchen
    cab_m = U.mat('kitchen_cab', (0.75, 0.68, 0.55), rough=0.5)
    top_m = U.mat('marble_top', (0.88, 0.86, 0.82), rough=0.2, coat=0.3)
    U.rbox('k_counter', (3.6, 0.65, 0.88), O + Vector((8.0, 4.6, 0.44)), bevel=0.01, collection=coll, mat_=cab_m)
    U.rbox('k_top', (3.7, 0.7, 0.05), O + Vector((8.0, 4.6, 0.9)), bevel=0.01, collection=coll, mat_=top_m)
    U.rbox('k_stove', (0.6, 0.55, 0.06), O + Vector((7.0, 4.6, 0.95)), bevel=0.01, collection=coll,
           mat_=U.mat('stove_steel', (0.6, 0.6, 0.6), metal=0.9, rough=0.3))
    pot = U.lathe('k_pot', [(0.0, 0), (0.15, 0.0), (0.16, 0.02), (0.16, 0.2), (0.17, 0.21)], 24, collection=coll,
                  mat_=U.mat('pot_alu', (0.7, 0.7, 0.72), metal=1.0, rough=0.25), subsurf=1, cap_top=False)
    pot.location = O + Vector((6.85, 4.6, 0.98))
    stew = U.cyl('k_stew', 0.15, 0.01, O + Vector((6.85, 4.6, 1.13)), collection=coll,
                 mat_=U.mat('stew', (0.55, 0.18, 0.05), rough=0.3), seg=24)
    board = U.rbox('k_board', (0.4, 0.28, 0.025), O + Vector((8.3, 4.5, 0.94)), bevel=0.005, collection=coll, mat_=U.mat('board_wood', (0.7, 0.5, 0.3), rough=0.6))
    knife = U.rbox('k_knife', (0.22, 0.03, 0.005), O + Vector((8.35, 4.42, 0.96)), bevel=0, collection=coll, mat_=U.mat('chrome', (0.8, 0.8, 0.8), metal=1, rough=0.15))
    for i in range(3):   # chopped onion half
        U.sphere(f'k_onionpiece{i}', 0.03, O + Vector((8.2 + i * 0.05, 4.52, 0.97)), (1, 1, 0.5), collection=coll, mat_=U.mat('onion', (0.65, 0.4, 0.18)))
    basket = U.lathe('k_basket', [(0.12, 0.0), (0.2, 0.12), (0.22, 0.14)], 20, collection=coll,
                     mat_=U.mat('wicker', (0.6, 0.45, 0.25), rough=0.9, bump=0.8), subsurf=1, cap_top=False)
    basket.location = O + Vector((9.3, 4.55, 0.93))
    U.rbox('k_fridge', (0.75, 0.7, 1.75), O + Vector((9.5, 0.5, 0.875)), bevel=0.06, collection=coll,
           mat_=U.mat('fridge', (0.88, 0.88, 0.84), rough=0.3, coat=0.4))
    U.rbox('k_table', (1.1, 0.8, 0.05), O + Vector((8.0, 2.4, 0.75)), bevel=0.01, collection=coll, mat_=U.mat('formica', (0.75, 0.82, 0.78), rough=0.3))
    for lx, ly in ((-0.5, -0.35), (0.5, -0.35), (-0.5, 0.35), (0.5, 0.35)):
        U.cyl(f'k_tleg{lx}{ly}', 0.02, 0.73, O + Vector((8.0 + lx, 2.4 + ly, 0)), collection=coll, mat_=M['iron'], seg=8)
    # plates set for lunch (unfinished)
    for i in range(3):
        U.cyl(f'k_plate{i}', 0.11, 0.015, O + Vector((7.7 + i * 0.3, 2.4, 0.78)), collection=coll,
              mat_=U.mat('plate', (0.92, 0.92, 0.9), rough=0.2, coat=0.5), seg=20)
    # ---- bedroom (two little beds)
    for i, (bx, col) in enumerate(((1.2, (0.85, 0.55, 0.62)), (4.5, (0.55, 0.7, 0.85)))):
        U.rbox(f'bed{i}_frame', (1.0, 1.9, 0.35), O + Vector((bx, -2.3, 0.18)), bevel=0.04, collection=coll, mat_=M['wood'])
        U.rbox(f'bed{i}_mattress', (0.95, 1.85, 0.15), O + Vector((bx, -2.3, 0.43)), bevel=0.06, collection=coll,
               mat_=U.mat('sheet_white', (0.9, 0.88, 0.85), rough=0.8, sheen=0.5))
        U.rbox(f'bed{i}_blanket', (1.0, 1.2, 0.06), O + Vector((bx, -1.9, 0.52)), bevel=0.03, collection=coll,
               mat_=U.mat(f'blanket{i}', col, rough=0.9, sheen=0.8))
        U.rbox(f'bed{i}_head', (1.0, 0.08, 0.9), O + Vector((bx, -3.25, 0.45)), bevel=0.03, collection=coll, mat_=M['wood'])
    pil = U.rbox('huda_pillow', (0.6, 0.35, 0.14), O + Vector((4.5, -2.95, 0.57)), bevel=0.06, collection=coll,
                 mat_=U.mat('huda_pillow', (0.2, 0.55, 0.3), rough=0.8, sheen=0.7, image=C.pattern_dress_img(), uv_scale=2.0))
    U.rbox('hind_pillow', (0.6, 0.35, 0.14), O + Vector((1.2, -2.95, 0.57)), bevel=0.06, collection=coll,
           mat_=U.mat('pillow_pink', (0.92, 0.7, 0.72), rough=0.8, sheen=0.7))
    U.rbox('wardrobe', (1.2, 0.6, 2.0), O + Vector((2.85, -3.6, 1.0)), bevel=0.02, collection=coll, mat_=M['wood'])
    U.rbox('bed_rug', (1.4, 0.9, 0.01), O + Vector((2.85, -1.5, 0.005)), bevel=0, collection=coll,
           mat_=U.mat('rug_blue', (0.15, 0.25, 0.5), rough=0.95, sheen=0.6))
    # hallway: shoe shelf, mirror
    U.rbox('hall_shelf', (0.9, 0.35, 0.5), O + Vector((9.5, -3.6, 0.25)), bevel=0.02, collection=coll, mat_=M['wood'])
    return coll


# ---------------------------------------------------------------- hospital
def build_hospital(root):
    coll = U.coll('ENV_Hospital', root)
    O = HOSP_O
    wall_m = U.mat('hosp_wall', (0.75, 0.82, 0.8), rough=0.7)
    tile_m = U.mat('hosp_floor', (0.7, 0.72, 0.72), rough=0.3, image=floor_tile_img(), uv_scale=1.2)
    U.plane('hosp_floor', 8, 8, O, collection=coll, mat_=tile_m)
    U.rbox('hosp_wall_back', (8, 0.2, 3), O + Vector((0, 3, 1.5)), bevel=0, collection=coll, mat_=wall_m)
    U.rbox('hosp_wall_left', (0.2, 8, 3), O + Vector((-3, 0, 1.5)), bevel=0, collection=coll, mat_=wall_m)
    U.rbox('hosp_wall_right_a', (0.2, 8, 0.9), O + Vector((3, 0, 0.45)), bevel=0, collection=coll, mat_=wall_m)
    U.rbox('hosp_wall_right_b', (0.2, 8, 0.6), O + Vector((3, 0, 2.7)), bevel=0, collection=coll, mat_=wall_m)
    U.rbox('hosp_wall_right_c', (0.2, 4.6, 1.5), O + Vector((3, -2.4 - 1.2, 1.65)), bevel=0, collection=coll, mat_=wall_m)
    U.plane('hosp_window', 2.4, 1.5, O + Vector((3.15, 1.0, 1.65)), (math.pi / 2, 0, math.pi / 2), collection=coll,
            mat_=U.mat('hosp_sky', (0.7, 0.8, 0.95), emission=(0.75, 0.85, 1.0), estr=2.2))
    camera_only(bpy.data.objects['hosp_window'])
    LK.area('L_hosp_win', O + Vector((2.8, 1.0, 1.7)), (0, math.radians(-90), 0), 2.2, 180, coll, size_y=1.4)
    LK.area('L_hosp_fill', O + Vector((0.0, 0.0, 2.9)), (0, 0, 0), 3.0, 80, coll, size_y=3.0)
    blind_m = U.mat('blinds', (0.9, 0.9, 0.88), rough=0.5)
    for i in range(12):
        U.rbox(f'blind{i}', (0.02, 2.4, 0.06), O + Vector((3.05, 1.0, 0.95 + i * 0.12)), bevel=0, collection=coll, mat_=blind_m,
               rot=(0.9, 0, 0))
    U.plane('hosp_ceiling', 8, 8, O + Vector((0, 0, 3)), (math.pi, 0, 0), collection=coll, mat_=wall_m)
    steel = U.mat('bed_steel', (0.75, 0.76, 0.78), metal=0.9, rough=0.3)
    U.rbox('hbed_frame', (1.0, 2.1, 0.12), O + Vector((0.6, 0.6, 0.55)), bevel=0.02, collection=coll, mat_=steel)
    U.rbox('hbed_mattress', (0.95, 2.0, 0.15), O + Vector((0.6, 0.6, 0.68)), bevel=0.06, collection=coll,
           mat_=U.mat('hsheet', (0.92, 0.93, 0.95), rough=0.8, sheen=0.4))
    U.rbox('hbed_head', (1.05, 0.06, 0.6), O + Vector((0.6, 1.62, 0.9)), bevel=0.02, collection=coll, mat_=steel)
    U.rbox('hbed_foot', (1.05, 0.06, 0.4), O + Vector((0.6, -0.42, 0.8)), bevel=0.02, collection=coll, mat_=steel)
    for lx in (-0.45, 0.45):
        for ly in (-0.35, 1.55):
            U.cyl(f'hbed_leg{lx}{ly}', 0.025, 0.5, O + Vector((0.6 + lx, 0.6 + ly, 0)), collection=coll, mat_=steel, seg=8)
    U.rbox('hpillow', (0.6, 0.35, 0.14), O + Vector((0.6, 1.35, 0.82)), bevel=0.06, collection=coll, mat_=U.mat('hsheet', (0.92, 0.93, 0.95)))
    blanket = U.rbox('hblanket', (1.0, 1.35, 0.16), O + Vector((0.6, 0.15, 0.8)), bevel=0.07, collection=coll,
                     mat_=U.mat('hblanket', (0.55, 0.68, 0.82), rough=0.9, sheen=0.7))
    U.rbox('hchair_seat', (0.5, 0.5, 0.06), O + Vector((-0.45, 0.55, 0.45)), bevel=0.02, collection=coll, mat_=U.mat('chair_blue', (0.2, 0.3, 0.45), rough=0.6))
    U.rbox('hchair_back', (0.06, 0.5, 0.5), O + Vector((-0.72, 0.55, 0.72)), bevel=0.02, collection=coll, mat_=U.mat('chair_blue', (0.2, 0.3, 0.45)))
    U.rbox('hcabinet', (0.45, 0.45, 0.7), O + Vector((1.55, 1.5, 0.35)), bevel=0.02, collection=coll, mat_=U.mat('cab_white', (0.85, 0.86, 0.85), rough=0.4))
    U.lathe('hvase', [(0.03, 0), (0.05, 0.08), (0.03, 0.16), (0.035, 0.2)], 14, collection=coll,
            mat_=U.mat('vase_glass', (0.6, 0.75, 0.8), rough=0.05, transmission=0.8), subsurf=1, cap_top=False).location = O + Vector((1.55, 1.5, 0.7))
    for i in range(3):
        U.sphere(f'hflower{i}', 0.035, O + Vector((1.53 + i * 0.03, 1.5, 0.95 + 0.04 * (i % 2))), collection=coll,
                 mat_=U.mat('flower_yellow', (0.95, 0.75, 0.2), rough=0.6))
    U.rbox('hcurtain', (0.04, 1.6, 2.3), O + Vector((-2.7, 2.0, 1.4)), bevel=0.02, collection=coll,
           mat_=U.mat('curtain_green', (0.45, 0.62, 0.55), rough=0.9, sheen=0.5))
    return coll

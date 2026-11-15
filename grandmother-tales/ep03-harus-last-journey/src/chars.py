"""Character models: Haru (1982), Maryam, Maryam's father (1982), the boy
(father aged 10, 1962), Haru's son (1962), boy's father (1962).

Each character is a parametric 2D puppet drawn with painted fills, cel
shadow, rim light and boiling ink lines.  Head local unit: s=1 means the
head is ~200 px tall.  Figure origin = between the feet.
"""
import math, random
import skia
from core import *

INK = '#3b241c'

CHARS = {
    'haru': dict(skin='#ecc9a6', skin_sh='#c99c7c', hair='#d4d0cb', hair_sh='#9e9893', hair_line='#6d6862',
                 iris='#4a3326', coat='#5a4536', coat_sh='#3b2c22', coat_hi='#7a604c', pants='#3e3a39',
                 shoe='#2a211d', age='old', brow='#cfcac4', heads=6.1, stoop=0.06, scarf=None,
                 mustache='#e2ded8'),
    'maryam': dict(skin='#dcae86', skin_sh='#b98a66', hair='#2b1d17', hair_sh='#170f0c', hair_line='#0e0806',
                   iris='#3a2418', coat='#efe4cf', coat_sh='#cdb999', coat_hi='#fbf6ea', pants='#4a3b45',
                   shoe='#5a3a28', age='child', brow='#2b1d17', heads=4.2, stoop=0, scarf='#7d1e2c',
                   scarf_sh='#55121c', braids=True),
    'father': dict(skin='#d09f78', skin_sh='#a9785a', hair='#1f1814', hair_sh='#0f0b09', hair_line='#080504',
                   iris='#2e1d14', coat='#2f4b3b', coat_sh='#1d3127', coat_hi='#4a6b57', pants='#2c2a2e',
                   shoe='#1f1916', age='adult', brow='#1f1814', heads=6.4, stoop=0, scarf=None,
                   mustache='#1f1814'),
    'boy': dict(skin='#d3a37c', skin_sh='#ab7b5c', hair='#1d1613', hair_sh='#0d0908', hair_line='#060403',
                iris='#2e1d14', coat='#7a5236', coat_sh='#553722', coat_hi='#996c4b', pants='#3b3530',
                shoe='#2a1f18', age='kid', brow='#1d1613', heads=4.5, stoop=0, scarf=None),
    'son': dict(skin='#efcfae', skin_sh='#cda080', hair='#171515', hair_sh='#080707', hair_line='#030303',
                iris='#2a1d16', coat='#1f2b47', coat_sh='#131a2e', coat_hi='#34466c', pants='#25252b',
                shoe='#1a1716', age='young', brow='#171515', heads=6.6, stoop=0, scarf='#dcc7a3',
                scarf_sh='#b39f7c'),
    'oldman62': dict(skin='#cf9c74', skin_sh='#a77556', hair='#2a2420', hair_sh='#15110f', hair_line='#0a0807',
                     iris='#2e1d14', coat='#4e4a44', coat_sh='#34312c', coat_hi='#6a655d', pants='#2f2c2a',
                     shoe='#1f1916', age='adult', brow='#2a2420', heads=6.3, stoop=0, scarf=None,
                     mustache='#2a2420'),
}


def _clip_path(c, path):
    c.save()
    c.clipPath(path, skia.ClipOp.kIntersect, True)


# =================================================================== HEAD
def face_outline(ch, yaw):
    age = ch['age']
    wide = {'old': 0.98, 'child': 1.0, 'kid': 1.0, 'young': 0.93, 'adult': 0.97}[age]
    chin = {'old': 1.0, 'child': 0.86, 'kid': 0.9, 'young': 1.02, 'adult': 1.04}[age]
    jaw = {'old': 0.9, 'child': 0.55, 'kid': 0.65, 'young': 1.05, 'adult': 0.95}[age]
    pts = []
    n = 44
    for i in range(n):
        a = 2 * math.pi * i / n
        x = math.cos(a) * 78 * wide
        yy = math.sin(a)
        y = yy * (100 * chin if yy > 0 else 104)
        if yy > 0:
            x *= 1 - 0.40 * jaw * (yy ** 2.3)
            if age in ('child', 'kid'):
                x *= 1 + 0.05 * math.sin(yy * math.pi)
        x += yaw * 18 * max(0, yy) ** 1.4
        if x * yaw > 0:
            x *= 1 - 0.13 * abs(yaw)
        else:
            x *= 1 + 0.05 * abs(yaw)
        pts.append((x, y))
    return pts


def draw_eye(c, ch, ex, ey, w, h, open_, look, iris_c, near, s, seed, wet=0.0, closed_style='calm', happy=0.0):
    """Anime-style painted eye. (ex,ey) centre, w/h half size."""
    ink = INK
    if open_ < 0.12 or happy > 0.6:
        # closed eye: soft curve (down = calm, up = happy squint)
        if happy > 0.6:
            pts = bezier_pts((ex - w, ey + 2), (ex, ey - h * 0.9), (ex + w, ey + 2), 10)
        else:
            pts = bezier_pts((ex - w, ey), (ex, ey + h * 0.55), (ex + w * 1.05, ey - 1), 10)
        stroke_taper(c, boil(pts, 0.6, seed), 3.2, 4.5, ink)
        if ch['age'] != 'old':
            stroke_taper(c, [(ex + w * 0.8, ey - 1), (ex + w * 1.18, ey - 5)], 3, 1, ink)
        return
    hh = h * open_
    lid_drop = 0.18 if ch['age'] == 'old' else 0.0
    top = [(ex - w, ey + hh * 0.15), (ex - w * 0.35, ey - hh * (1.0 - lid_drop)), (ex + w * 0.4, ey - hh * (0.98 - lid_drop)),
           (ex + w * 1.0, ey - hh * 0.05)]
    bot = [(ex + w * 0.95, ey + hh * 0.18), (ex + w * 0.2, ey + hh * 0.72), (ex - w * 0.55, ey + hh * 0.6)]
    shape = smooth_path(top + bot, closed=True, tension=0.55)
    c.drawPath(shape, P('#fbf6f0'))
    _clip_path(c, shape)
    # lid shadow on the white
    c.drawPath(shape, lin((0, ey - hh), (0, ey + hh * 0.2), [('#9a7f78', 0.55), ('#fbf6f0', 0.0)]))
    ir = h * 0.78
    ix = ex + look[0] * w * 0.45
    iy = ey + look[1] * h * 0.3 + hh * 0.05
    c.drawCircle(ix, iy, ir, P(iris_c))
    c.drawCircle(ix, iy, ir, rad((ix, iy + ir * 0.5), ir * 1.1, [mix(iris_c, '#c88a5a', 0.45), iris_c], [0, 1]))
    c.drawCircle(ix, iy - ir * 0.15, ir * 0.52, P('#0d0705'))
    c.drawCircle(ix, iy, ir, P('#000000', 0.9, stroke=1.6 * s))
    # catchlights
    c.drawCircle(ix - ir * 0.32, iy - ir * 0.38, ir * (0.30 + 0.08 * wet), P('#ffffff', 0.95))
    c.drawCircle(ix + ir * 0.35, iy + ir * 0.35, ir * 0.13, P('#ffffff', 0.8))
    if wet > 0:
        c.drawPath(shape, lin((0, ey), (0, ey + hh), [('#bfe6ff', 0), ('#dff3ff', 0.55 * wet)]))
        c.drawCircle(ix + ir * 0.1, iy + ir * 0.55, ir * 0.18, P('#ffffff', 0.7 * wet))
    c.restore()
    # upper lash line (thick brush stroke with outer flick)
    lash = boil(bezier_pts((ex - w * 1.08, ey + hh * 0.2), (ex - w * 0.1, ey - hh * (1.35 - lid_drop)), (ex + w * 1.12, ey - hh * 0.12), 12), 0.5, seed)
    stroke_taper(c, lash, 3.0 * s + 1, 6.5 * s + 1.4, ink)
    if ch['age'] in ('child', 'kid', 'young') or ch is CHARS['maryam']:
        stroke_taper(c, [(ex + w * 1.0, ey - hh * 0.1), (ex + w * 1.25, ey - hh * 0.38)], 3.5 * s, 1.0, ink)
    # lower line
    low = bezier_pts((ex - w * 0.6, ey + hh * 0.62), (ex + w * 0.2, ey + hh * 0.85), (ex + w * 0.92, ey + hh * 0.22), 8)
    stroke_taper(c, boil(low, 0.4, seed + 1), 1.0, 1.8 * s + 0.4, mix(ink, ch['skin_sh'], 0.35), 0.8)
    if ch['age'] == 'old':
        bag = bezier_pts((ex - w * 0.7, ey + hh * 0.95 + 5), (ex, ey + hh * 1.25 + 7), (ex + w * 0.8, ey + hh * 0.7 + 5), 8)
        stroke_taper(c, bag, 0.6, 1.6 * s, ch['skin_sh'], 0.85)
        # crow's feet on the outer corner of each eye
        side = 1 if near is False else -1
        ox = ex + side * w * 1.1
        for k in range(3):
            stroke_taper(c, [(ox, ey + (k - 1) * 5 * s), (ox + side * 10 * s, ey + (k - 1) * 8 * s)], 1.6 * s, 0.4, ch['skin_sh'], 0.7)


def draw_head(c, ch, x, y, s=1.0, yaw=0.45, tilt=0.0, eye_open=1.0, look=(0.3, 0.0), brow=0.0,
              mouth='neutral', mouth_open=0.0, tears=0.0, tear_t=0.0, blush=0.25, light='#ffd9a8',
              light_dir=-1, rim=0.0, rim_c='#ffe7b8', seed=0, wet=0.0, happy=0.0, shade=1.0, back=False):
    """Draw a head centred at (x,y). yaw>0 faces right. brow: +1 sad/worried, -1 stern."""
    if isinstance(ch, str):
        ch = CHARS[ch]
    c.save()
    c.translate(x, y)
    c.rotate(math.degrees(tilt))
    c.scale(s, s)
    ink = INK
    age = ch['age']
    fx = yaw * 30
    # ---------------- back hair
    _hair_back(c, ch, yaw, seed, wet)
    if back:
        c.restore()
        return
    # ---------------- ear (far from facing)
    ear_x = -yaw * 62 - (8 if yaw >= 0 else -8)
    if abs(yaw) > 0.12:
        sgn = -1 if yaw > 0 else 1
        ex0 = sgn * (70 - abs(yaw) * 10)
        ear = smooth_path([(ex0, -8), (ex0 + sgn * 16, -16), (ex0 + sgn * 20, 6), (ex0 + sgn * 10, 30), (ex0, 26)])
        c.drawPath(ear, P(ch['skin']))
        c.drawPath(ear, P(ch['skin_sh'], 0.6))
        c.drawPath(ear, P(ink, 0.9, stroke=2.4))
    # ---------------- neck stub (under jaw)
    # ---------------- face
    pts = boil(face_outline(ch, yaw), 0.7, seed)
    face = smooth_path(pts, closed=True, tension=0.5)
    c.drawPath(face, P(ch['skin']))
    _clip_path(c, face)
    # light gradient + cel shadow on the side away from the light
    c.drawPath(face, lin((-90 * light_dir, -60), (90 * light_dir, 60), [(light, 0.18), (ch['skin_sh'], 0.0)]))
    sh = skia.Path(face)
    sh.offset(-light_dir * 0 + (16 if light_dir < 0 else -16) * 1.0, 0)
    inv = skia.Path()
    inv.addRect(-200, -200, 200, 200)
    shadow = skia.Op(inv, sh, skia.PathOp.kDifference_PathOp)
    c.drawPath(shadow, P(ch['skin_sh'], 0.55 * shade))
    # hair shadow on forehead
    c.drawOval(skia.Rect(-95 + fx * 0.3, -150, 95 + fx * 0.3, -40), P(ch['skin_sh'], 0.35 * shade, blur=10))
    # blush
    if blush > 0:
        for bx, bs in ((fx - 40 - yaw * 4, 1.0), (fx + 42 - yaw * 8, 1 - 0.4 * yaw)):
            c.drawOval(skia.Rect(bx - 17 * bs, 34, bx + 17 * bs, 50), P('#e8806e', blush * 0.6, blur=6))
    if rim > 0:
        rp = skia.Path(face)
        rp.offset(6 * light_dir, 0)
        rr = skia.Op(face, rp, skia.PathOp.kDifference_PathOp)
        c.drawPath(rr, P(rim_c, rim, blur=2))
    c.restore()
    c.drawPath(face, P(ink, 0.95, stroke=2.8))
    # ---------------- old-age lines
    if age == 'old':
        for k in range(3):
            yy = -62 + k * 9
            stroke_taper(c, boil(bezier_pts((fx - 30 + k * 4, yy), (fx, yy - 4), (fx + 28 - k * 3, yy), 8), 0.4, seed + k), 0.6, 1.6, ch['skin_sh'], 0.65)
        nl = bezier_pts((fx - 22, 42), (fx - 34, 60), (fx - 28, 80), 8)
        stroke_taper(c, nl, 2.0, 0.5, ch['skin_sh'], 0.8)
        nr = bezier_pts((fx + 26 - yaw * 4, 42), (fx + 36 - yaw * 6, 58), (fx + 30 - yaw * 6, 78), 8)
        stroke_taper(c, nr, 1.6, 0.4, ch['skin_sh'], 0.6)
    # ---------------- eyes
    eh = {'old': 9.5, 'child': 17, 'kid': 15, 'young': 12.5, 'adult': 11.5}[age]
    ew = {'old': 17, 'child': 19, 'kid': 18, 'young': 18, 'adult': 18}[age]
    ey = {'old': 6, 'child': 16, 'kid': 12, 'young': 6, 'adult': 6}[age]
    sep = {'old': 33, 'child': 33, 'kid': 33, 'young': 33, 'adult': 34}[age]
    near_x = fx - sep - yaw * 6
    far_x = fx + sep - yaw * 12
    nw = ew * (1 + 0.08 * yaw)
    fw = ew * (1 - 0.32 * abs(yaw))
    if yaw < 0:
        near_x, far_x = fx + sep - yaw * 6, fx - sep - yaw * 12
    draw_eye(c, ch, near_x, ey, nw, eh, eye_open, look, ch['iris'], True, 1.0, seed + 10, wet, happy=happy)
    draw_eye(c, ch, far_x, ey, fw, eh, eye_open, look, ch['iris'], False, 1.0, seed + 20, wet, happy=happy)
    # ---------------- brows
    by = ey - eh - 16 - (4 if age == 'old' else 0)
    for bx, bwid, side in ((near_x, nw, -1 if yaw >= 0 else 1), (far_x, fw, 1 if yaw >= 0 else -1)):
        inner = (bx - side * bwid * 0.95, by - brow * 9 + (-brow) * 0)
        mid = (bx, by - 6 - brow * 2)
        outer = (bx + side * bwid * 1.05, by + 2 + brow * 5)
        bp = bezier_pts(inner, mid, outer, 10)
        wid = 6.5 if age == 'old' else 5
        stroke_taper(c, boil(bp, 0.5, seed + 30 + side), wid, 2.0, ch['brow'] if age != 'old' else '#bdb7b0')
    # ---------------- nose
    nx = fx + yaw * 14
    if age in ('child', 'kid'):
        stroke_taper(c, [(nx + 2, 36), (nx + 5, 41), (nx, 43)], 2.0, 1.2, ch['skin_sh'], 0.9)
    else:
        npts = bezier_pts((nx - 2 + yaw * 4, 12), (nx + 10 * (1 if yaw >= 0 else -1), 40), (nx - 3, 46), 8)
        stroke_taper(c, npts, 0.5, 2.6, mix(ink, ch['skin_sh'], 0.4), 0.85)
        c.drawOval(skia.Rect(nx - 9, 41, nx + 3, 49), P(ch['skin_sh'], 0.55, blur=2))
    # ---------------- mustache
    my = {'old': 66, 'child': 64, 'kid': 66, 'young': 68, 'adult': 69}[age]
    mx = fx + yaw * 9
    if ch.get('mustache') and age in ('adult', 'old'):
        mp = smooth_path([(mx - 26, my - 6), (mx - 10, my - 15), (mx, my - 12), (mx + 12, my - 15), (mx + 27, my - 5),
                          (mx + 12, my - 7), (mx, my - 6), (mx - 12, my - 7)])
        c.drawPath(mp, P(ch['mustache'], 0.95))
        c.drawPath(mp, P(ink, 0.5, stroke=1.2))
    # ---------------- mouth
    _mouth(c, ch, mx, my, mouth, mouth_open, seed)
    # ---------------- tears
    if tears > 0:
        for i, (tx, ph) in enumerate(((near_x + 4, 0.0), (far_x - 3, 0.43))):
            p = (tear_t * 0.55 + ph) % 1.0
            ty = ey + eh + 4 + p * 70
            sz = 4.5 * tears * (1.0 - 0.3 * p)
            # glistening streak
            stroke_taper(c, [(tx, ey + eh + 2), (tx + 1, ty)], 2.8 * tears, 1.5 * tears, '#dff4ff', 0.45 * tears)
            dp = smooth_path([(tx, ty - sz * 2.2), (tx + sz, ty), (tx, ty + sz), (tx - sz, ty)])
            c.drawPath(dp, P('#e8f7ff', 0.85 * tears))
            c.drawCircle(tx - sz * 0.3, ty - sz * 0.2, sz * 0.35, P('#ffffff', 0.9 * tears))
    # ---------------- front hair
    _hair_front(c, ch, yaw, seed, wet)
    c.restore()


def _mouth(c, ch, mx, my, mouth, mo, seed):
    ink = INK
    lipc = mix(ch['skin_sh'], '#b4504a', 0.35)
    if mouth == 'smile':
        pts = bezier_pts((mx - 16, my - 3), (mx, my + 9 + mo * 4), (mx + 17, my - 4), 10)
        if mo > 0.15:
            body = smooth_path(pts + [(mx + 8, my - 1), (mx - 8, my - 1)])
            c.drawPath(body, P('#7a2e2a'))
        stroke_taper(c, boil(pts, 0.4, seed), 2.2, 2.6, ink)
    elif mouth in ('sad', 'cry'):
        w = 15
        pts = bezier_pts((mx - w, my + 4), (mx, my - 5 - mo * 2), (mx + w, my + 5), 10)
        if mo > 0.1:
            op = smooth_path([(mx - w * 0.8, my + 2), (mx, my - 4), (mx + w * 0.8, my + 3), (mx + w * 0.5, my + 4 + mo * 14),
                              (mx, my + 6 + mo * 16), (mx - w * 0.5, my + 4 + mo * 13)])
            c.drawPath(op, P('#5e2220'))
            c.drawOval(skia.Rect(mx - 6, my + mo * 8, mx + 6, my + 5 + mo * 14), P('#b9585a', 0.8))
        stroke_taper(c, boil(pts, 0.4, seed), 2.4, 2.4, ink)
    elif mouth in ('open', 'talk', 'shout'):
        h = 4 + mo * (22 if mouth == 'shout' else 12)
        w = 11 + mo * (6 if mouth == 'shout' else 2)
        op = smooth_path([(mx - w, my), (mx, my - 3), (mx + w, my), (mx + w * 0.6, my + h * 0.8), (mx, my + h), (mx - w * 0.6, my + h * 0.8)])
        c.drawPath(op, P('#5a201e'))
        _clip_path(c, op)
        c.drawOval(skia.Rect(mx - w * 0.7, my + h * 0.45, mx + w * 0.7, my + h * 1.3), P('#c35d5d'))
        c.drawRect(skia.Rect(mx - w, my - 4, mx + w, my + 2.5), P('#f4ece4'))
        c.restore()
        c.drawPath(op, P(ink, 1, stroke=2.2))
    else:  # neutral / soft
        pts = bezier_pts((mx - 12, my), (mx, my + 2.5), (mx + 12, my - 0.5), 8)
        stroke_taper(c, boil(pts, 0.3, seed), 1.8, 2.2, ink)
    # lower lip hint
    stroke_taper(c, [(mx - 5, my + 11 + mo * 8), (mx + 5, my + 11 + mo * 8)], 1.5, 1.5, lipc, 0.45)


def _hair_back(c, ch, yaw, seed, wet):
    age = ch['age']
    hc, hs, hl = ch['hair'], ch['hair_sh'], ch['hair_line']
    if ch is CHARS['maryam'] or ch.get('braids'):
        # back hair volume + two braids hanging past shoulders
        hb = smooth_path(boil([(-92, -10), (-96, -80), (-60, -124), (0, -136), (60, -124), (94, -80), (92, -10), (70, 40), (-70, 40)], 0.8, seed))
        c.drawPath(hb, P(hc))
        c.drawPath(hb, P(hs, 0.5))
        for side in (-1, 1):
            bx = side * 74 - yaw * 18
            for k in range(10):
                yy = 34 + k * 21
                xx = bx + side * (4 * math.sin(k * 0.7)) - yaw * k * 1.5
                r = 18 - k * 0.8
                pp = smooth_path(ellipse_pts(xx + (k % 2) * 3 * side, yy, r, r * 0.95, 12))
                c.drawPath(pp, P(hc))
                c.drawPath(pp, lin((xx - r, yy - r), (xx + r, yy + r), [('#5a3e30', 0.5), (hs, 0.6)]))
                d = 1 if k % 2 else -1
                stroke_taper(c, [(xx - r * 0.8 * d, yy - r * 0.6), (xx + r * 0.6 * d, yy + r * 0.7)], 1.2, 2.2, hl, 0.9)
            # burgundy tie
            ty = 34 + 10 * 21 - 10
            c.drawOval(skia.Rect(bx - 12 - yaw * 12, ty - 6, bx + 12 - yaw * 12, ty + 8), P(ch.get('scarf', '#7d1e2c')))
            tail = [(bx - yaw * 12 + side * 2, ty + 8), (bx - yaw * 14, ty + 30), (bx - yaw * 14 - side * 4, ty + 44)]
            stroke_taper(c, tail, 9, 3, hc)
        return
    if age == 'old':
        for side in (-1, 1):
            pts = [(side * 60, -92), (side * 86, -70), (side * 98, -40), (side * 96, -6), (side * 84, 14), (side * 70, 6),
                   (side * 62, -30)]
            hb = smooth_path(boil(pts, 1.2, seed + side), tension=0.45)
            c.drawPath(hb, P(hc))
            c.drawPath(hb, lin((side * 60, 0), (side * 98, 0), [(hs, 0.2), (hs, 0.7)]))
            for k in range(4):
                y0 = -70 + k * 20
                stroke_taper(c, [(side * 78, y0), (side * 94, y0 + 12)], 1.4, 0.4, ch['hair_line'], 0.55)
            c.drawPath(hb, P(INK, 0.6, stroke=1.8))
        return
    pts = [(-88, -10), (-94, -78), (-62, -126), (0, -138), (62, -126), (94, -78), (90, -10), (64, 6), (-66, 6)]
    if age in ('young', 'kid'):
        pts = [(-86, -6), (-94, -80), (-64, -130), (0, -142), (66, -128), (96, -80), (88, -8), (60, 4), (-64, 4)]
    hb = smooth_path(boil(pts, 0.8, seed))
    c.drawPath(hb, P(hc))
    c.drawPath(hb, P(hs, 0.4))


def _hair_front(c, ch, yaw, seed, wet):
    age = ch['age']
    hc, hs, hl = ch['hair'], ch['hair_sh'], ch['hair_line']
    fx = yaw * 30
    if age == 'old':
        # temple wisps
        for side in (-1, 1):
            bx = side * 66 + fx * 0.15
            for k in range(3):
                stroke_taper(c, [(bx + side * 8, -70 + k * 14), (bx - side * 4, -60 + k * 16)], 2.4, 0.5, hc, 0.9)
        for k in range(7):
            x0 = -54 + k * 17 + fx * 0.3
            pts = bezier_pts((x0 - 6, -92 + abs(k - 3) * 6), (x0 + 6, -108 + abs(k - 3) * 3), (x0 + 22, -96 + abs(k - 3) * 6), 8)
            stroke_taper(c, pts, 2.4, 0.6, hc, 0.9)
            stroke_taper(c, pts, 0.8, 0.3, ch['hair_line'], 0.5)
        # scalp sheen
        c.drawOval(skia.Rect(-30 + fx * 0.3, -104, 20 + fx * 0.3, -84), P('#fff4e6', 0.35, blur=6))
        return
    if ch.get('braids'):
        # centre parting with soft fringe framing the face
        fr = smooth_path(boil([(-86, -10), (-90, -70), (-56, -118), (fx * 0.4, -124), (60, -116), (90, -70), (86, -10),
                               (74, -30), (60, -70), (fx * 0.4 + 6, -92), (fx * 0.4 - 4, -92), (-52, -66), (-72, -26)], 0.8, seed + 3))
        c.drawPath(fr, P(hc))
        c.drawPath(fr, lin((-60, -120), (60, -40), [(hl, 0), ('#5a3a2c', 0.35)]))
        # shine band
        sb = smooth_path([(-60, -96), (-20, -112), (30, -110), (62, -92), (40, -98), (0, -102), (-40, -90)])
        c.drawPath(sb, P('#7a5a48', 0.55))
        c.drawPath(fr, P(INK, 0.9, stroke=2.4))
        return
    # short hair with fringe (son / boy / father / oldman62)
    if age == 'young':
        pts = [(-90, -4), (-96, -72), (-66, -126), (0, -144), (70, -128), (98, -76), (92, -6), (86, -40),
               (70, -56), (50, -50), (30, -66), (6, -56), (-16, -70), (-40, -58), (-62, -64), (-80, -34)]
    elif age == 'kid':
        pts = [(-88, 0), (-98, -76), (-70, -130), (0, -146), (72, -132), (100, -80), (90, 0), (82, -30),
               (66, -44), (48, -36), (30, -56), (8, -44), (-14, -60), (-36, -46), (-58, -56), (-80, -24)]
    else:  # adult - neater side part
        pts = [(-86, -10), (-92, -80), (-60, -128), (10, -138), (72, -122), (94, -76), (88, -14), (80, -46),
               (66, -70), (40, -82), (10, -88), (-20, -84), (-50, -72), (-72, -50)]
    pts = [(x + fx * 0.25, y) for x, y in pts]
    fr = smooth_path(boil(pts, 0.9, seed + 3), tension=0.45)
    c.drawPath(fr, P(hc))
    c.drawPath(fr, lin((-60, -140), (60, -40), [('#4a4648' if age != 'kid' else '#3a2e28', 0.5), (hc, 0)]))
    if wet:
        c.drawPath(fr, P('#9fb6d8', 0.18 * wet))
    sb = smooth_path([(-56 + fx * 0.25, -108), (-10 + fx * 0.25, -126), (40 + fx * 0.25, -118), (14 + fx * 0.25, -114), (-30 + fx * 0.25, -104)])
    c.drawPath(sb, P('#6c6a78' if age == 'young' else '#5a4a40', 0.45))
    c.drawPath(fr, P(INK, 0.9, stroke=2.4))


# =================================================================== BODY
def _limb(c, p0, p1, p2, w0, w1, color, shade, seed, outline=True):
    pts = [p0, ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2), p1, ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2), p2]
    # build thick path from polyline
    left, right = [], []
    n = len(pts)
    for i, (x, y) in enumerate(pts):
        a = pts[min(i + 1, n - 1)]
        b = pts[max(i - 1, 0)]
        dx, dy = a[0] - b[0], a[1] - b[1]
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        w = lerp(w0, w1, i / (n - 1)) / 2
        left.append((x + nx * w, y + ny * w))
        right.append((x - nx * w, y - ny * w))
    path = smooth_path(boil(left + right[::-1], 0.8, seed), tension=0.45)
    c.drawPath(path, P(color))
    _clip_path(c, path)
    c.drawPath(path, lin((p0[0] - w0, 0), (p0[0] + w0, 0), [(shade, 0.0), (shade, 0.6)]))
    c.restore()
    if outline:
        c.drawPath(path, P(INK, 0.9, stroke=3))
    return path


def _hand(c, x, y, ang, size, skin, skin_sh, seed, grip=False, open_=0.5):
    c.save()
    c.translate(x, y)
    c.rotate(math.degrees(ang))
    s = size
    palm = smooth_path(boil([(-0.45 * s, -0.1 * s), (0.45 * s, -0.1 * s), (0.5 * s, 0.6 * s), (0.25 * s, 0.95 * s),
                             (-0.25 * s, 0.95 * s), (-0.5 * s, 0.6 * s)], 0.6, seed))
    c.drawPath(palm, P(skin))
    c.drawPath(palm, P(skin_sh, 0.35))
    c.drawPath(palm, P(INK, 0.9, stroke=2.4))
    if not grip:
        for k in range(4):
            fx = -0.33 * s + k * 0.22 * s
            L = (0.42 + 0.08 * (1 - abs(k - 1.5))) * s * (0.7 + 0.3 * open_)
            fp = [(fx, 0.85 * s), (fx + (k - 1.5) * 0.04 * s * open_, 0.85 * s + L)]
            stroke_taper(c, fp, 0.2 * s, 0.17 * s, INK, 0.9)
            stroke_taper(c, fp, 0.16 * s, 0.13 * s, skin, 1.0)
    else:
        knuck = smooth_path([(-0.48 * s, 0.6 * s), (0.48 * s, 0.6 * s), (0.42 * s, 1.1 * s), (-0.42 * s, 1.1 * s)])
        c.drawPath(knuck, P(skin))
        c.drawPath(knuck, P(INK, 0.8, stroke=2))
    thumb = [(0.4 * s, 0.25 * s), (0.65 * s, 0.6 * s), (0.6 * s, 0.85 * s)]
    stroke_taper(c, thumb, 0.24 * s, 0.18 * s, INK, 0.9)
    stroke_taper(c, thumb, 0.19 * s, 0.13 * s, skin, 1)
    c.restore()


def figure(c, ch, x, y, s=1.0, yaw=0.45, t=0.0, seed=0, lean=0.0, sit=False, walk=None, arms=None,
           head=None, breathe=1.0, wind=0.0, flip=False, wet=0.0, back=False, light_dir=-1, rim=0.0, rim_c='#ffe7b8',
           legs_hidden=False, sleeve_drip=False):
    """Full-body puppet.  arms = dict(L=(shoulder_deg, elbow_deg), R=(...), Lgrip, Rgrip)
    angles in degrees: 0 = hanging down, + = rotate toward facing direction (forward/up).
    head = kwargs for draw_head (expressions)."""
    if isinstance(ch, str):
        ch = CHARS[ch]
    head = dict(head or {})
    arms = dict(arms or {})
    tq = on_twos(t)
    c.save()
    c.translate(x, y)
    c.scale(s * (-1 if flip else 1), s)
    child = ch['age'] in ('child', 'kid')
    hip_y = -330 if child else -600
    sh_y = -590 if child else -1010
    head_y = -705 if child else -1135
    if ch['age'] == 'old':
        sh_y += 20
        head_y += 30
    br = math.sin(tq * 2 * math.pi / 3.6) * 5 * breathe
    stoop = ch['stoop']
    sw = (62 if child else 92) * (1 - 0.25 * abs(yaw))
    hem_y = -150 if child else -330
    # ----- legs
    lw = 46 if child else 62
    if not legs_hidden:
        if sit:
            knee_x = 210 if not child else 150
            for k, off in ((0, -18), (1, 22)):
                hx = off * (1 - abs(yaw) * 0.4)
                p0 = (hx, hip_y)
                p1 = (hx + knee_x, hip_y - 6)
                p2 = (hx + knee_x - 10, hip_y + (260 if not child else 190))
                _limb(c, p0, p1, p2, lw + 14, lw - 6, ch['pants'], '#000000', seed + 40 + k)
                c.drawOval(skia.Rect(p2[0] - 30, p2[1] - 16, p2[0] + 52, p2[1] + 12), P(ch['shoe']))
        else:
            ph = 0 if walk is None else walk
            for k, side in ((0, -1), (1, 1)):
                swing = math.sin(ph * 2 * math.pi + k * math.pi) * (28 if walk is not None else 0)
                lift = max(0, math.sin(ph * 2 * math.pi + k * math.pi)) * (40 if walk is not None else 0)
                hx = side * 26 * (1 - abs(yaw) * 0.5)
                p0 = (hx, hip_y)
                p1 = (hx + swing * 0.5 + yaw * 6, hip_y * 0.5 - lift * 0.3)
                p2 = (hx + swing * 1.4, -lift * 0.5)
                _limb(c, p0, p1, p2, lw, lw - 16, mix(ch['pants'], '#000000', 0.15 * k), '#000000', seed + 40 + k)
                c.drawPath(smooth_path([(p2[0] - 24, p2[1] - 22), (p2[0] + 30 + 20 * yaw, p2[1] - 18), (p2[0] + 42 + 20 * yaw, p2[1] + 2),
                                        (p2[0] - 26, p2[1] + 4)]), P(ch['shoe']))
    # ----- torso / coat
    c.save()
    c.rotate(math.degrees(lean + stoop * 0.6))
    sway = math.sin(tq * 1.7 + 1.3) * 6 * wind + math.sin(tq * 2.3) * 2
    top_l = (-sw, sh_y - br)
    top_r = (sw, sh_y - br)
    hem_off = 0 if not sit else 0
    hw = sw * (1.35 if not child else 1.42)
    if sit:
        coat = [(-sw * 0.9, sh_y - 10 - br), (sw * 0.9, sh_y - 10 - br), (sw * 1.08, hip_y - 60), (sw * 1.0 + 120, hip_y + 30),
                (-sw * 1.1, hip_y + 34), (-sw * 1.12, hip_y - 80)]
    else:
        coat = [(-sw * 0.92, sh_y - 10 - br), (sw * 0.92, sh_y - 10 - br), (sw * 1.12, (sh_y + hip_y) / 2), (hw + sway, hem_y),
                (hw * 0.3 + sway, hem_y + 14), (-hw * 0.4 + sway, hem_y + 12), (-hw + sway, hem_y),
                (-sw * 1.12, (sh_y + hip_y) / 2)]
    cp = smooth_path(boil(coat, 1.0, seed + 50), tension=0.35)
    c.drawPath(cp, P(ch['coat']))
    _clip_path(c, cp)
    c.drawPath(cp, lin((-light_dir * -hw, 0), (light_dir * -hw, 0), [(ch['coat_hi'], 0.5), (ch['coat'], 0.0), (ch['coat_sh'], 0.9)], [0, 0.4, 1]))
    # folds
    for k in range(4):
        fx0 = -hw * 0.6 + k * hw * 0.4 + sway * 0.5
        stroke_taper(c, boil([(fx0 * 0.6, hip_y + 40), (fx0 + sway, hem_y - 20)], 1, seed + 60 + k), 1, 4, ch['coat_sh'], 0.7)
    # front opening line & buttons
    ox = yaw * sw * 0.55
    stroke_taper(c, [(ox, sh_y + 40), (ox + 4, hip_y), (ox + sway + 6, hem_y + 10)], 3, 3, ch['coat_sh'], 0.9)
    for k in range(3 if not child else 3):
        by = sh_y + 110 + k * (110 if not child else 70)
        c.drawCircle(ox - 14, by, 7 if not child else 6, P(mix(ch['coat_sh'], '#000000', 0.3)))
    if wet:
        c.drawPath(cp, P('#0a1a33', 0.35 * wet))
        for k in range(5):
            dx = -hw * 0.7 + k * hw * 0.35
            stroke_taper(c, [(dx, sh_y + 60), (dx + 3, hem_y)], 2, 1, '#9fc0e8', 0.25 * wet)
    if rim > 0:
        stroke_taper(c, [(-light_dir * -sw * 0.95, sh_y), (-light_dir * -hw, hem_y)], 6, 3, rim_c, rim)
    c.restore()
    c.drawPath(cp, P(INK, 0.9, stroke=3.2))
    c.restore()
    c.save()
    c.rotate(math.degrees(lean + stoop * 0.6))
    # collar
    col_pts = [(-sw * 0.62, sh_y - 14 - br), (-12 + ox * 0.3, sh_y + 70), (sw * 0.62, sh_y - 14 - br), (sw * 0.3, sh_y - 34 - br), (-sw * 0.3, sh_y - 34 - br)]
    c.drawPath(smooth_path(col_pts), P(ch['coat_sh']))
    # neck
    nk = skia.Rect(-26 + yaw * 14, head_y + 60, 26 + yaw * 14, sh_y - 4 - br)
    c.drawRect(nk, P(ch['skin_sh']))
    # scarf
    if ch.get('scarf'):
        sc = ch['scarf']
        ring = smooth_path(boil([(-sw * 0.72, sh_y - 26 - br), (0, sh_y - 52 - br), (sw * 0.72, sh_y - 26 - br), (sw * 0.6, sh_y + 20 - br),
                                 (0, sh_y + 34 - br), (-sw * 0.6, sh_y + 18 - br)], 1, seed + 70))
        c.drawPath(ring, P(sc))
        c.drawPath(ring, P(ch['scarf_sh'], 0.4))
        c.drawPath(ring, P(INK, 0.8, stroke=2.6))
        tail_x = -sw * 0.35 + yaw * 30
        wv = math.sin(tq * 2.1) * 10 * (0.3 + wind)
        tail = [(tail_x, sh_y + 10), (tail_x + 6 + wv * 0.5, sh_y + 120), (tail_x - 4 + wv, sh_y + (210 if not child else 150))]
        _limb(c, tail[0], tail[1], tail[2], 44 if not child else 34, 40 if not child else 30, sc, ch['scarf_sh'], seed + 72)
        for k in range(3):
            stroke_taper(c, [(tail[2][0] - 14 + k * 12, tail[2][1]), (tail[2][0] - 16 + k * 12 + wv * 0.2, tail[2][1] + 18)], 3, 2, ch['scarf_sh'])
    # ----- arms
    arm_len1 = 160 if child else 270
    arm_len2 = 140 if child else 240
    aw = 56 if child else 74
    hands = []
    for side, key in ((-1, 'L'), (1, 'R')):
        a1, a2 = arms.get(key, (8 * side * -1 + 6, 10))
        sx = side * sw * 0.98
        sy = sh_y + 20 - br
        # direction: angle measured from straight down, + rotates toward +x (facing)
        th1 = math.radians(a1)
        ex_, ey_ = sx + math.sin(th1) * arm_len1, sy + math.cos(th1) * arm_len1
        th2 = th1 + math.radians(a2)
        hx, hy = ex_ + math.sin(th2) * arm_len2, ey_ + math.cos(th2) * arm_len2
        hands.append((side, key, sx, sy, ex_, ey_, hx, hy, th2))
    # far arm first (behind), near arm after
    order = sorted(hands, key=lambda h: h[0] * (1 if yaw >= 0 else -1), reverse=True)
    for side, key, sx, sy, ex_, ey_, hx, hy, th2 in order:
        far = (side > 0) == (yaw >= 0)
        colr = mix(ch['coat'], ch['coat_sh'], 0.5) if far else ch['coat']
        _limb(c, (sx, sy), (ex_, ey_), (hx, hy), aw, aw * 0.8, colr, ch['coat_sh'], seed + 80 + side)
        c.drawOval(skia.Rect(hx - aw * 0.45, hy - aw * 0.25, hx + aw * 0.45, hy + aw * 0.25), P(ch['coat_sh']))
        _hand(c, hx, hy, -th2, 44 if child else 58, ch['skin'], ch['skin_sh'], seed + 90 + side, grip=arms.get(key + 'grip', False),
              open_=arms.get(key + 'open', 0.5))
        if sleeve_drip:
            ph = (t * 1.3 + side * 0.4) % 1
            c.drawCircle(hx, hy + 40 + ph * 120, 5, P('#cfe6ff', 0.7 * (1 - ph)))
    # ----- head
    hk = dict(yaw=yaw, seed=seed, light_dir=light_dir, rim=rim, rim_c=rim_c, wet=wet, back=back)
    hk.update(head)
    tilt = hk.pop('tilt', 0.0) + stoop * 0.4 + lean * 0.5
    draw_head(c, ch, yaw * 12, head_y - br * 0.6, 1.0, tilt=tilt, **hk)
    c.restore()
    c.restore()


# =================================================================== PROPS
def crane(c, x, y, s=1.0, rot=0.0, paper='#f3ece0', sun='#c8202a', wet=0.0, glow=0.0, seed=0, flip=False, flap=0.0):
    """Folded paper crane (orizuru), 3/4 side view, red sun painted on the near wing."""
    c.save()
    c.translate(x, y)
    c.rotate(math.degrees(rot))
    c.scale(s * (-1 if flip else 1), s)
    pap = mix(paper, '#b9b3a8', wet * 0.55)
    sh = mix(pap, '#8a8176', 0.5)
    mid = mix(pap, sh, 0.35)
    line = P('#6b5b4b', 0.75, stroke=1.6)
    if glow:
        c.drawCircle(0, -20, 170, rad((0, -20), 170, [('#ffd890', 0.5 * glow), ('#ffd890', 0)]))
    # soft contact shadow
    c.drawOval(skia.Rect(-90, 38, 90, 54), P('#000000', 0.18, blur=8))
    fl = flap * 25
    # far wing
    fw = poly([(-6, -4), (34, -122 + fl), (78, -50 + fl * 0.4), (24, 2)])
    c.drawPath(fw, P(sh)); c.drawPath(fw, line)
    # tail (right, up)
    tail = poly([(20, 6), (128, -78), (118, -60), (34, 22)])
    c.drawPath(tail, P(mid)); c.drawPath(tail, line)
    # neck (left, up) with folded head
    neck = poly([(-20, 6), (-118, -70), (-142, -64), (-124, -56), (-34, 22)])
    c.drawPath(neck, P(pap)); c.drawPath(neck, line)
    # body diamond
    body = poly([(-46, 14), (0, -14), (46, 14), (0, 40)])
    c.drawPath(body, P(mid)); c.drawPath(body, line)
    c.drawPath(poly([(0, -14), (46, 14), (0, 40)]), P(sh, 0.6))
    # near wing (big) with crease
    nw = poly([(-34, 8), (-18, -132 - fl), (44, -44 - fl * 0.4), (16, 10)])
    c.drawPath(nw, lin((-62, -120), (14, 8), [(pap, 1), (mix(pap, sh, 0.5), 1)]))
    c.drawPath(nw, line)
    stroke_taper(c, [(-8, 6), (-16, -118 - fl)], 1.2, 0.6, sh, 0.8)
    # red sun on the near wing
    cx, cy = -2, -48 - fl * 0.5
    c.drawCircle(cx, cy, 17, P(sun, 0.95 - wet * 0.15))
    c.drawCircle(cx - 4, cy - 5, 6, P('#ff8c78', 0.25))
    if wet:
        c.drawCircle(cx, cy, 21, P(sun, 0.22, blur=4))
        for k in range(4):
            c.drawCircle(-40 + k * 25, -30 + (k % 2) * 30, 3, P('#ffffff', 0.5 * wet))
    c.restore()


def bust(c, ch, x, y, s=1.0, yaw=0.45, t=0.0, seed=0, head=None, breathe=1.0, wind=0.0, light_dir=-1, rim=0.0,
         rim_c='#ffe7b8', wet=0.0, shoulder_rot=0.0, flip=False):
    """Close-up framing: head + neck + shoulders/collar/scarf. (x,y)=head centre."""
    if isinstance(ch, str):
        ch = CHARS[ch]
    head = dict(head or {})
    tq = on_twos(t)
    br = math.sin(tq * 2 * math.pi / 3.6) * 4 * breathe
    c.save()
    c.translate(x, y)
    c.scale(s * (-1 if flip else 1), s)
    child = ch['age'] in ('child', 'kid')
    sw = (150 if child else 200)
    shy = 150 - br
    c.save()
    c.rotate(math.degrees(shoulder_rot))
    c.drawPath(smooth_path([(-30 + yaw * 16, 60), (32 + yaw * 16, 60), (38 + yaw * 10, shy + 20), (-36 + yaw * 10, shy + 20)]), P(ch['skin']))
    c.drawPath(smooth_path([(-30 + yaw * 16, 60), (32 + yaw * 16, 60), (36 + yaw * 10, 110), (-32 + yaw * 10, 104)]), P(ch['skin_sh'], 0.85))
    sh = [(-sw * 0.35, shy - 10), (-sw * 0.9, shy + 20), (-sw * 1.25, shy + 90), (-sw * 1.4, shy + 420), (sw * 1.4, shy + 420),
          (sw * 1.25, shy + 90), (sw * 0.9, shy + 20), (sw * 0.35, shy - 10)]
    sh = [(px + yaw * 20 * (1 if py < shy + 60 else 0), py) for px, py in sh]
    cp = smooth_path(boil(sh, 1.0, seed + 50), tension=0.4)
    c.drawPath(cp, P(ch['coat']))
    _clip_path(c, cp)
    c.drawPath(cp, lin((-sw * 1.4 * -light_dir, 0), (sw * 1.4 * -light_dir, 0), [(ch['coat_hi'], 0.6), (ch['coat'], 0), (ch['coat_sh'], 0.95)], [0, 0.45, 1]))
    if wet:
        c.drawPath(cp, P('#0a1a33', 0.35 * wet))
    lap = [(-sw * 0.38, shy - 8), (-sw * 0.05 + yaw * 30, shy + 230), (-sw * 0.62, shy + 120), (-sw * 0.82, shy + 30)]
    c.drawPath(smooth_path(lap), P(ch['coat_sh'], 0.9))
    lap2 = [(sw * 0.38, shy - 8), (sw * 0.05 + yaw * 30, shy + 230), (sw * 0.62, shy + 120), (sw * 0.82, shy + 30)]
    c.drawPath(smooth_path(lap2), P(ch['coat_hi'], 0.55))
    c.restore()
    c.drawPath(cp, P(INK, 0.9, stroke=3.4))
    if ch.get('scarf'):
        sc = ch['scarf']
        ring = smooth_path(boil([(-sw * 0.62, shy - 30), (0, shy - 6), (sw * 0.62, shy - 30), (sw * 0.7, shy + 34), (0, shy + 64), (-sw * 0.7, shy + 34)], 1, seed + 70))
        c.drawPath(ring, P(sc))
        c.drawPath(ring, lin((0, shy - 30), (0, shy + 60), [(sc, 0), (ch['scarf_sh'], 0.6)]))
        for k in range(4):
            stroke_taper(c, [(-sw * 0.5 + k * sw * 0.32, shy - 12), (-sw * 0.45 + k * sw * 0.3, shy + 46)], 2, 3, ch['scarf_sh'], 0.6)
        c.drawPath(ring, P(INK, 0.8, stroke=2.8))
        wv = math.sin(tq * 2.1) * 10 * (0.3 + wind)
        tail = smooth_path(boil([(-sw * 0.55, shy + 30), (-sw * 0.28, shy + 34), (-sw * 0.22 + wv, shy + 330), (-sw * 0.6 + wv, shy + 330)], 1, seed + 71))
        c.drawPath(tail, P(sc))
        c.drawPath(tail, P(ch['scarf_sh'], 0.35))
        c.drawPath(tail, P(INK, 0.8, stroke=2.6))
    else:
        c.drawPath(smooth_path([(-46 + yaw * 12, shy - 14), (0 + yaw * 12, shy + 46), (46 + yaw * 12, shy - 14), (30 + yaw * 12, shy + 10), (0 + yaw * 12, shy + 20), (-30 + yaw * 12, shy + 10)]),
                   P('#e9e3d6' if ch['age'] != 'kid' else '#c9b28f'))
    c.restore()
    hk = dict(yaw=yaw, seed=seed, light_dir=light_dir, rim=rim, rim_c=rim_c, wet=wet)
    hk.update(head)
    tilt = hk.pop('tilt', 0.0)
    draw_head(c, ch, 0, -br * 0.5, 1.0, tilt=tilt, **hk)
    c.restore()

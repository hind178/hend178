"""Painted environments, props and atmospheric effects."""
import math, random
import numpy as np
import skia
from core import *
from chars import INK

MARGIN = 220  # plates are painted larger than frame for camera moves
PW, PH = W + 2 * MARGIN, H + 2 * MARGIN


# ================================================================ camera
class Cam:
    def __init__(self, z=1.0, x=0.0, y=0.0, rot=0.0, shake=0.0, t=0.0):
        self.z, self.x, self.y, self.rot, self.shake, self.t = z, x, y, rot, shake, t

    def apply(self, c, depth=1.0):
        z = self.z ** depth
        sx = sy = 0
        if self.shake:
            r = random.Random(int(self.t * 30) * 7 + int(depth * 10))
            sx, sy = r.uniform(-1, 1) * self.shake * depth, r.uniform(-1, 1) * self.shake * depth
        c.translate(W / 2 + self.x * depth + sx, H / 2 + self.y * depth + sy)
        if self.rot:
            c.rotate(self.rot)
        c.scale(z, z)
        c.translate(-W / 2, -H / 2)


def plate(c, img, cam, depth=1.0, a=1.0, blur=0):
    c.save()
    cam.apply(c, depth)
    draw_img(c, img, -MARGIN, -MARGIN, a, blur)
    c.restore()


def paint_plate(fn, *args, **kw):
    s = skia.Surface(PW, PH)
    cc = s.getCanvas()
    cc.translate(MARGIN, MARGIN)
    fn(cc, *args, **kw)
    return s.makeImageSnapshot()


# ================================================================ painterly helpers
def brush_blobs(c, x0, y0, x1, y1, colors, n=40, rmin=30, rmax=120, seed=0, a=0.25, blur=14, flat=0.5):
    r = random.Random(seed)
    for i in range(n):
        x, y = r.uniform(x0, x1), r.uniform(y0, y1)
        rx = r.uniform(rmin, rmax)
        ry = rx * r.uniform(flat * 0.6, flat * 1.4)
        cc = r.choice(colors)
        c.save()
        c.translate(x, y)
        c.rotate(r.uniform(-12, 12))
        c.drawOval(skia.Rect(-rx, -ry, rx, ry), P(cc, a * r.uniform(0.5, 1.0), blur=blur))
        c.restore()


def brush_strokes(c, x0, y0, x1, y1, colors, n=60, L=(40, 140), w=(4, 14), ang=0.0, seed=0, a=0.3):
    r = random.Random(seed)
    for i in range(n):
        x, y = r.uniform(x0, x1), r.uniform(y0, y1)
        l = r.uniform(*L)
        an = ang + r.uniform(-0.2, 0.2)
        p0 = (x, y)
        p1 = (x + math.cos(an) * l * 0.5, y + math.sin(an) * l * 0.5 + r.uniform(-4, 4))
        p2 = (x + math.cos(an) * l, y + math.sin(an) * l)
        stroke_taper(c, bezier_pts(p0, p1, p2, 6), r.uniform(*w), r.uniform(*w) * 0.3, r.choice(colors), a * r.uniform(0.5, 1))


def sky(c, top, bot, mid=None, x0=-MARGIN, y0=-MARGIN, x1=W + MARGIN, y1=H + MARGIN):
    cols = [top, mid, bot] if mid else [top, bot]
    c.drawRect(skia.Rect(x0, y0, x1, y1), lin((0, y0), (0, y1), cols))


# ================================================================ STATION (1982, night snow)
STATION_NIGHT = dict(sky_top='#0b1430', sky_mid='#1d2f57', sky_bot='#3e4f78', snow='#c9d6ee', snow_sh='#7d8fb8',
                     wood='#3a2b26', wood_hi='#5e4638', lamp='#ffcf7a', far='#24345e')


def station_far(c, pal=STATION_NIGHT, seed=1):
    """Sky, distant hills of Kyoto, faint town lights."""
    sky(c, pal['sky_top'], pal['sky_bot'], pal['sky_mid'])
    brush_blobs(c, -200, -200, W + 200, 900, [pal['sky_mid'], '#2c3f6c', '#40517c'], 30, 80, 260, seed, 0.25, 40)
    # hills
    r = random.Random(seed)
    for layer, (yb, colr, amp) in enumerate(((980, '#2a3961', 90), (1060, '#22305a', 70))):
        pts = [(-MARGIN, H + MARGIN)]
        for i in range(0, 15):
            x = -MARGIN + i * (W + 2 * MARGIN) / 14
            pts.append((x, yb - amp * (0.5 + 0.5 * math.sin(i * 0.9 + layer * 2 + seed)) - r.uniform(0, 30)))
        pts.append((W + MARGIN, H + MARGIN))
        c.drawPath(smooth_path(pts, closed=True, tension=0.4), P(colr))
        brush_blobs(c, -MARGIN, yb - amp, W + MARGIN, yb + 40, ['#3a4b78', '#1a264a'], 14, 40, 120, seed + layer, 0.25, 18)
    # town lights
    for i in range(70):
        x, y = r.uniform(-MARGIN, W + MARGIN), r.uniform(1010, 1110)
        c.drawCircle(x, y, r.uniform(1.5, 3.2), P('#ffd793', r.uniform(0.3, 0.8)))
        c.drawCircle(x, y, 9, P('#ffb85a', 0.12, blur=6))


def tracks(c, vx, vy, y_bottom, spread=700, n_sleepers=26, rail='#5b6478', snow='#c9d6ee', seed=2, closed=True):
    """Two rails converging to vanishing point (vx,vy), snow covered."""
    # ground snow
    c.drawPath(poly([(-MARGIN, vy + 10), (W + MARGIN, vy + 10), (W + MARGIN, H + MARGIN), (-MARGIN, H + MARGIN)]),
               lin((0, vy), (0, H), ['#6f80aa', snow]))
    brush_blobs(c, -MARGIN, vy, W + MARGIN, H + MARGIN, ['#b7c5e3', '#8fa0c8', '#dbe4f6'], 50, 40, 200, seed, 0.22, 24, 0.25)
    gauge = spread
    for k in range(n_sleepers):
        f = (k / n_sleepers) ** 2.1
        y = vy + (y_bottom - vy) * f
        hw = gauge * f * 0.75
        th = 4 + 30 * f
        c.drawRect(skia.Rect(vx - hw - 30 * f, y - th / 2, vx + hw + 30 * f, y + th / 2), P('#3a3230', 0.85))
        c.drawRect(skia.Rect(vx - hw - 30 * f, y - th / 2, vx + hw + 30 * f, y - th / 2 + th * 0.4), P(snow, 0.8))
    for side in (-1, 1):
        pts = [(vx, vy), (vx + side * gauge * 0.5, y_bottom)]
        stroke_taper(c, pts, 1.5, 22, rail, 1)
        stroke_taper(c, [(vx, vy - 2), (vx + side * gauge * 0.5, y_bottom - 8)], 1, 8, '#aab4cc', 0.8)
    # drifted snow on rails
    brush_blobs(c, vx - gauge * 0.6, vy + 40, vx + gauge * 0.6, y_bottom, [snow, '#e6eefc'], 25, 20, 70, seed + 3, 0.35, 8, 0.3)


def barrier(c, x, y, s=1.0, snow='#d9e3f6'):
    """Closed-line barrier: two posts, red/white crossbar, snow on top."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    for px in (-180, 180):
        c.drawRect(skia.Rect(px - 9, -150, px + 9, 0), P('#2b2a33'))
    bar = skia.Rect(-200, -130, 200, -100)
    c.drawRect(bar, P('#f1ece4'))
    for k in range(5):
        x0 = -200 + k * 80
        c.drawPath(poly([(x0, -130), (x0 + 40, -130), (x0 + 30, -100), (x0 - 10, -100)]), P('#b02a2e'))
    c.drawRect(bar, P(INK, 0.8, stroke=3))
    c.drawPath(smooth_path([(-205, -130), (-150, -146), (0, -142), (160, -148), (205, -130)]), P(snow))
    c.restore()


def bench(c, x, y, s=1.0, snow=0.8, wood='#5a4032', wood_sh='#3a281f', snow_c='#dbe4f6'):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    # legs
    for lx in (-230, 230):
        c.drawRect(skia.Rect(lx - 14, -150, lx + 14, 0), P('#2a2427'))
        c.drawRect(skia.Rect(lx - 14, -150, lx - 4, 0), P('#4a4448'))
    # seat slats
    for k in range(3):
        yy = -170 + k * 18
        c.drawRoundRect(skia.Rect(-280, yy, 280, yy + 14), 4, 4, P(wood if k % 2 == 0 else mix(wood, wood_sh, 0.4)))
    # back rest
    for lx in (-230, 230):
        c.drawRect(skia.Rect(lx - 10, -380, lx + 10, -170), P('#2a2427'))
    for k in range(3):
        yy = -370 + k * 50
        c.drawRoundRect(skia.Rect(-280, yy, 280, yy + 34), 6, 6, P(wood))
        c.drawRect(skia.Rect(-280, yy + 22, 280, yy + 34), P(wood_sh, 0.6))
        stroke_taper(c, [(-260, yy + 10), (240, yy + 12)], 1.2, 1.2, wood_sh, 0.5)
    if snow > 0:
        c.drawPath(smooth_path([(-286, -170), (-200, -186 - 10 * snow), (0, -182 - 12 * snow), (200, -188 - 8 * snow), (286, -170)]), P(snow_c, 0.95))
        c.drawPath(smooth_path([(-286, -370), (-150, -382 - 8 * snow), (100, -380 - 10 * snow), (286, -370)]), P(snow_c, 0.95))
    c.restore()


def station_clock(c, x, y, s=1.0, hh=11, mm=17.0, glow=0.0, snow=True):
    """Hanging round platform clock."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    c.drawRect(skia.Rect(-6, -190, 6, -95), P('#1e1d24'))
    if glow:
        c.drawCircle(0, 0, 220, rad((0, 0), 220, [('#ffe2a0', 0.35 * glow), ('#ffe2a0', 0)]))
    c.drawCircle(0, 0, 100, P('#1c1b22'))
    c.drawCircle(0, 0, 88, rad((-20, -30), 120, ['#fbf4e3', '#d9cfb8']))
    for i in range(60):
        a = i / 60 * 2 * math.pi
        L = 14 if i % 5 == 0 else 6
        w = 4 if i % 5 == 0 else 1.6
        c.drawLine(math.sin(a) * (80 - L), -math.cos(a) * (80 - L), math.sin(a) * 80, -math.cos(a) * 80, P('#2a2420', 1, stroke=w))
    ha = ((hh % 12) + mm / 60) / 12 * 2 * math.pi
    ma = (mm / 60) * 2 * math.pi
    c.drawLine(0, 0, math.sin(ha) * 46, -math.cos(ha) * 46, P('#1a1614', 1, stroke=8))
    c.drawLine(0, 0, math.sin(ma) * 70, -math.cos(ma) * 70, P('#1a1614', 1, stroke=5))
    c.drawCircle(0, 0, 7, P('#8a2a22'))
    c.drawCircle(-24, -30, 50, P('#ffffff', 0.12, blur=10))
    c.drawCircle(0, 0, 100, P(INK, 0.9, stroke=4))
    if snow:
        c.drawPath(smooth_path([(-70, -76), (-20, -104), (30, -104), (72, -76), (40, -88), (-30, -88)]), P('#e4ebf8'))
    c.restore()


def lamp_post(c, x, y, s=1.0, on=1.0):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    c.drawRect(skia.Rect(-8, -560, 8, 0), P('#1d1c24'))
    c.drawRect(skia.Rect(-8, -560, -2, 0), P('#3a3944'))
    c.drawPath(poly([(-40, -560), (40, -560), (24, -610), (-24, -610)]), P('#1d1c24'))
    c.drawRect(skia.Rect(-26, -560, 26, -515), P(mix('#3b3530', '#ffd78a', on)))
    c.drawPath(smooth_path([(-32, -612), (0, -630), (32, -612)]), P('#dfe7f6'))
    c.restore()


def lamp_glow(c, x, y, r=260, on=1.0, colr='#ffcf7a', flick=0.0):
    a = on * (1 - flick)
    c.drawCircle(x, y, r, add_blend(rad((x, y), r, [(colr, 0.55 * a), (colr, 0.18 * a), (colr, 0)], [0, 0.35, 1])))
    c.drawCircle(x, y, r * 0.05, add_blend(P('#fff4d6', 0.55 * a, blur=r * 0.04)))


def station_mid(c, pal=STATION_NIGHT, seed=3, vx=W * 0.80, vy=1120):
    """Platform structure: canopy, posts, wall, empty notice board."""
    # tracks on right going to the distance
    tracks(c, vx, vy, H + MARGIN, 1100, 28, seed=seed)
    barrier(c, vx + 10, vy + 180, 0.55)
    # platform slab
    pf = poly([(-MARGIN, vy - 10), (vx - 50, vy + 4), (W * 0.74, H + MARGIN), (-MARGIN, H + MARGIN)])
    c.drawPath(pf, lin((0, vy), (0, H), ['#7d8db4', '#d7e1f4']))
    brush_blobs(c, -MARGIN, vy, W * 0.7, H + MARGIN, ['#e8eef9', '#aebcdc', '#c8d4ec'], 50, 30, 150, seed + 1, 0.3, 18, 0.3)
    c.drawPath(poly([(vx - 50, vy + 4), (vx - 40, vy + 4), (W * 0.74 + 30, H + MARGIN), (W * 0.74, H + MARGIN)]), P('#e9effa', 0.95))
    c.drawPath(poly([(vx - 40, vy + 4), (vx - 36, vy + 10), (W * 0.74 + 60, H + MARGIN), (W * 0.74 + 30, H + MARGIN)]), P('#3a4060', 0.9))
    # station building (left)
    bx1 = W * 0.36
    c.drawRect(skia.Rect(-MARGIN, 620, bx1, vy + 6), P('#3b2d2a'))
    for k in range(14):
        x = -MARGIN + k * 46
        c.drawLine(x, 640, x, vy, P('#2a201d', 0.8, stroke=3))
    # windows (dark, one dim)
    for k, lit in ((0, 0.0), (1, 0.15)):
        wx = -60 + k * 210
        c.drawRect(skia.Rect(wx, 760, wx + 150, 960), P('#151a2a'))
        c.drawRect(skia.Rect(wx, 760, wx + 150, 960), P('#ffcf7a', lit))
        c.drawLine(wx + 75, 760, wx + 75, 960, P('#2a201d', 1, stroke=6))
        c.drawLine(wx, 860, wx + 150, 860, P('#2a201d', 1, stroke=6))
        c.drawRect(skia.Rect(wx, 760, wx + 150, 960), P('#2a201d', 1, stroke=8))
        c.drawRect(skia.Rect(wx - 8, 952, wx + 158, 970), P('#e3eaf7'))
    # canopy roof
    roof = poly([(-MARGIN, 560), (bx1 + 120, 600), (bx1 + 110, 640), (-MARGIN, 620)])
    c.drawPath(roof, P('#2a2228'))
    c.drawPath(smooth_path([(-MARGIN, 548), (bx1 + 40, 580), (bx1 + 130, 596), (bx1 + 120, 606), (-MARGIN, 570)]), P('#e7eef9'))
    for k in range(4):
        px = -40 + k * 150
        if px < bx1 + 100:
            c.drawRect(skia.Rect(px, 625, px + 16, vy + 30 + k * 6), P('#2a2228'))
    # notice board (blank, aged)
    c.drawRect(skia.Rect(160, 1000, 300, 1080), P('#5d4a3c'))
    c.drawRect(skia.Rect(170, 1010, 290, 1070), P('#c9bda4', 0.6))


def snow_layer(c, t, n=160, size=(1.5, 4), speed=60, drift=20, seed=0, a=0.9, blur=0, area=(0, 0, W, H), wind=0.0, colr='#f2f6ff'):
    r = random.Random(seed)
    x0, y0, x1, y1 = area
    hgt = y1 - y0
    for i in range(n):
        bx = r.uniform(x0, x1)
        by = r.uniform(y0, y1)
        sp = speed * r.uniform(0.7, 1.3)
        sz = r.uniform(*size)
        ph = r.uniform(0, 6.28)
        y = y0 + (by - y0 + t * sp) % hgt
        x = bx + math.sin(t * 0.9 + ph) * drift + wind * t * sp * 0.4
        x = x0 + (x - x0) % (x1 - x0)
        c.drawCircle(x, y, sz, P(colr, a * r.uniform(0.6, 1.0), blur=blur))


def rain_layer(c, t, n=220, L=(40, 90), speed=1900, ang=0.18, seed=0, a=0.35, w=2.0, colr='#c9daf2', area=(0, 0, W, H)):
    r = random.Random(seed)
    x0, y0, x1, y1 = area
    hgt = y1 - y0 + 200
    dx = math.sin(ang)
    for i in range(n):
        bx = r.uniform(x0 - 200, x1)
        by = r.uniform(0, hgt)
        sp = speed * r.uniform(0.85, 1.15)
        l = r.uniform(*L)
        y = y0 - 100 + (by + t * sp) % hgt
        x = bx + (y - y0) * dx
        c.drawLine(x, y, x + dx * l, y + l, P(colr, a * r.uniform(0.4, 1), stroke=w * r.uniform(0.6, 1.2)))


def mist(c, t, y0, y1, colr='#9fb0d6', a=0.25, n=10, seed=0, speed=12, size=(220, 480), blend_add=False):
    r = random.Random(seed)
    for i in range(n):
        x = r.uniform(-400, W + 400)
        y = r.uniform(y0, y1)
        rx = r.uniform(*size)
        x = -500 + ((x + t * speed * r.uniform(0.5, 1.5)) + 500) % (W + 1000)
        p = P(colr, a * r.uniform(0.5, 1), blur=rx * 0.35)
        if blend_add:
            add_blend(p)
        c.drawOval(skia.Rect(x - rx, y - rx * 0.28, x + rx, y + rx * 0.28), p)


# ================================================================ TRAIN (vintage 1962 stock)
TRAIN = dict(body='#5a2f2c', body_sh='#3b1d1b', body_hi='#7b4a42', band='#d9c7a2', roof='#2b2a2e', under='#151417',
             win_dark='#16192a', win_lit='#ffd27a')


def carriage_side(c, x, y, L=1400, Hh=420, lit=0.0, t=0.0, pal=TRAIN, ghost=0.0, seed=0, windows=None, wet=0.0,
                  passenger=None):
    """Side elevation of a passenger car. (x,y) = left end at rail height."""
    c.save()
    c.translate(x, y)
    # undercarriage + bogies
    c.drawRect(skia.Rect(20, -70, L - 20, -30), P(pal['under']))
    for bx in (160, L - 160):
        c.drawRect(skia.Rect(bx - 110, -80, bx + 110, -40), P('#222026'))
        for wx in (-60, 60):
            c.drawCircle(bx + wx, -30, 32, P('#1a191d'))
            c.drawCircle(bx + wx, -30, 32, P('#4a4850', 1, stroke=4))
            a = t * 6
            c.drawLine(bx + wx, -30, bx + wx + math.cos(a) * 26, -30 + math.sin(a) * 26, P('#4a4850', 1, stroke=4))
    # body
    top = -70 - Hh
    body = skia.RRect.MakeRectXY(skia.Rect(0, top, L, -70), 18, 18)
    c.drawRRect(body, P(pal['body']))
    c.drawRect(skia.Rect(0, top + Hh * 0.62, L, top + Hh * 0.68), P(pal['band'], 0.9))
    c.drawRect(skia.Rect(0, -110, L, -70), P(pal['body_sh']))
    # roof
    c.drawPath(smooth_path([(-6, top + 8), (L * 0.1, top - 40), (L * 0.9, top - 40), (L + 6, top + 8)], closed=True, tension=0.3), P(pal['roof']))
    for vx in range(120, int(L), 260):
        c.drawRect(skia.Rect(vx, top - 58, vx + 60, top - 38), P('#3a393f'))
    # windows
    n = 9
    ww = (L - 260) / n
    wins = []
    for i in range(n):
        wx = 130 + i * ww
        r_ = skia.Rect(wx + 10, top + 50, wx + ww - 18, top + Hh * 0.56)
        wins.append(r_)
        L_on = lit if windows is None else windows[i]
        c.drawRect(r_, P(pal['win_dark']))
        if L_on > 0:
            c.drawRect(r_, lin((0, r_.top()), (0, r_.bottom()), [('#fff0c2', L_on), (pal['win_lit'], L_on), ('#e09a4c', L_on)]))
        c.drawRect(r_, P('#1a1414', 1, stroke=7))
        c.drawLine(r_.left(), (r_.top() + r_.bottom()) / 2 - 20, r_.right(), (r_.top() + r_.bottom()) / 2 - 20, P('#1a1414', 1, stroke=5))
    # doors at ends
    for dx in (30, L - 110):
        c.drawRect(skia.Rect(dx, top + 40, dx + 80, -80), P(pal['body_sh']))
        c.drawRect(skia.Rect(dx + 14, top + 60, dx + 66, top + 160), P(pal['win_dark']))
        if lit:
            c.drawRect(skia.Rect(dx + 14, top + 60, dx + 66, top + 160), P(pal['win_lit'], lit * 0.8))
    c.drawRRect(body, P(INK, 0.9, stroke=4))
    if wet:
        c.drawRRect(body, P('#9fb6d8', 0.15 * wet))
    c.restore()
    return [skia.Rect(r_.left() + x, r_.top() + y, r_.right() + x, r_.bottom() + y) for r_ in wins]


def window_glow(c, rects, a=1.0, r=180, colr='#ffcf7a'):
    for r_ in rects:
        cx, cy = r_.centerX(), r_.centerY()
        c.drawRect(skia.Rect(r_.left() - 40, r_.top() - 30, r_.right() + 40, r_.bottom() + 60), add_blend(P(colr, 0.22 * a, blur=40)))
        # light spilling onto snow below
        c.drawOval(skia.Rect(cx - r, r_.bottom() + 230, cx + r, r_.bottom() + 330), add_blend(P(colr, 0.20 * a, blur=40)))


def locomotive_front(c, x, y, s=1.0, lamp=1.0, t=0.0, ghost=0.0):
    """Head-on view of a vintage steam locomotive. (x,y)=rail centre."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    blk, blk2 = '#1c1b21', '#2c2b33'
    # running gear / buffer beam
    c.drawRect(skia.Rect(-260, -170, 260, -90), P('#5e1c1c'))
    c.drawRect(skia.Rect(-260, -170, 260, -150), P('#7a2a26'))
    for bx in (-190, 190):
        c.drawCircle(bx, -130, 34, P('#26252b'))
        c.drawCircle(bx, -130, 34, P('#55545c', 1, stroke=4))
    # cow-catcher
    c.drawPath(poly([(-240, -90), (240, -90), (190, -10), (-190, -10)]), P(blk2))
    for k in range(9):
        xx = -200 + k * 50
        c.drawLine(xx, -88, xx * 0.82, -12, P('#45444c', 1, stroke=5))
    # boiler / smokebox
    c.drawRect(skia.Rect(-280, -560, 280, -170), P(blk))
    c.drawCircle(0, -400, 210, P(blk2))
    c.drawCircle(0, -400, 210, P('#4a4952', 1, stroke=6))
    c.drawCircle(0, -400, 160, rad((-50, -460), 260, ['#3a3942', blk]))
    for k in range(10):
        a = k / 10 * 2 * math.pi
        c.drawCircle(math.cos(a) * 185, -400 + math.sin(a) * 185, 7, P('#6a6972'))
    c.drawCircle(0, -400, 22, P('#55545c'))
    # smoke deflectors
    for sx in (-1, 1):
        c.drawPath(poly([(sx * 260, -620), (sx * 300, -620), (sx * 300, -200), (sx * 260, -180)]), P(blk2))
    # chimney
    c.drawRect(skia.Rect(-50, -700, 50, -600), P(blk))
    c.drawRect(skia.Rect(-62, -712, 62, -690), P(blk2))
    # headlamp
    c.drawRect(skia.Rect(-44, -660, 44, -610), P(blk2))
    c.drawCircle(0, -635, 30, P('#fff3cf', lamp))
    c.restore()
    # glow in screen space
    gx, gy = x, y - 635 * s
    if lamp > 0:
        c.drawCircle(gx, gy, 520 * s + 80, add_blend(rad((gx, gy), 520 * s + 80, [('#ffe6a8', 0.75 * lamp), ('#ffc871', 0.25 * lamp), ('#ffc871', 0)], [0, 0.25, 1])))
        # beam
        c.drawPath(poly([(gx - 30 * s, gy), (gx + 30 * s, gy), (gx + 900 * s + 200, gy + 2400 * s), (gx - 900 * s - 200, gy + 2400 * s)]),
                   add_blend(lin((gx, gy), (gx, gy + 2400 * s), [('#ffe2a0', 0.32 * lamp), ('#ffe2a0', 0)])))


def steam_puffs(c, x, y, t, s=1.0, n=7, colr='#e9edf6', a=0.5, rise=180, seed=0):
    r = random.Random(seed)
    for i in range(n):
        ph = (t * 0.45 + i / n) % 1.0
        px = x + r.uniform(-30, 30) * s + ph * 160 * s * r.uniform(-0.6, 1)
        py = y - ph * rise * s * 3
        rr = (50 + ph * 220) * s
        c.drawCircle(px, py, rr, P(colr, a * (1 - ph) * 0.8, blur=rr * 0.35))


# ================================================================ 1962 SCENES
def storm_sky(c, seed=5):
    sky(c, '#0a0f1c', '#2a3348', '#151d30')
    brush_blobs(c, -MARGIN, -MARGIN, W + MARGIN, 1100, ['#2a3248', '#1a2134', '#3a4258', '#11172a'], 70, 80, 300, seed, 0.35, 40, 0.4)
    brush_strokes(c, -MARGIN, 0, W + MARGIN, 900, ['#3e4862', '#252d42'], 70, (100, 300), (10, 30), 0.15, seed + 1, 0.25)


def gorge(c, seed=6, river_y=1350):
    # far cliffs
    for k, (colr, off) in enumerate((('#1c2333', 0), ('#151b28', 120))):
        pts = [(-MARGIN, H + MARGIN), (-MARGIN, 780 + off), (90, 760 + off), (260, 900 + off), (300, river_y), (W - 300, river_y),
               (W - 230, 880 + off), (W - 80, 790 + off), (W + MARGIN, 760 + off), (W + MARGIN, H + MARGIN)]
        c.drawPath(smooth_path(pts, tension=0.3), P(colr))
        brush_strokes(c, -MARGIN, 760 + off, W + MARGIN, river_y, ['#2a3246', '#0e121c'], 40, (60, 180), (6, 18), 1.4, seed + k, 0.35)
    # trees silhouettes on cliffs
    r = random.Random(seed)
    for i in range(40):
        x = r.choice([r.uniform(-MARGIN, 280), r.uniform(W - 280, W + MARGIN)])
        y = r.uniform(720, 900)
        h = r.uniform(60, 140)
        c.drawPath(poly([(x, y - h), (x + h * 0.25, y), (x - h * 0.25, y)]), P('#0c1018'))


def river(c, t, y0, colr='#2b3a4e', foam='#a9bdd6', flood=1.0, seed=7, speed=260):
    c.drawRect(skia.Rect(-MARGIN, y0, W + MARGIN, H + MARGIN), lin((0, y0), (0, H), [colr, '#141c28']))
    r = random.Random(seed)
    for i in range(70):
        y = y0 + (r.uniform(0, 1) ** 1.5) * (H + MARGIN - y0)
        L = r.uniform(60, 260) * (0.5 + (y - y0) / 600)
        x = -MARGIN + (r.uniform(0, W + 2 * MARGIN) + t * speed * (0.5 + (y - y0) / 500)) % (W + 2 * MARGIN)
        stroke_taper(c, [(x, y), (x + L * 0.5, y - 3), (x + L, y)], r.uniform(2, 6) * (0.5 + (y - y0) / 600), 1, foam, 0.35 * flood)


def trestle_bridge(c, x0, x1, deck_y, river_y, broken=0.0, t=0.0):
    """Old steel/timber trestle bridge. broken: 0..1 collapse progress (middle span drops)."""
    span_mid = (x0 + x1) / 2
    gap0, gap1 = span_mid - 230, span_mid + 230
    for px in range(int(x0), int(x1) + 1, 230):
        # piers
        drop = 0
        if gap0 - 10 < px < gap1 + 10:
            drop = ease_in(broken) * 500
        c.save()
        c.translate(px, deck_y + drop)
        c.rotate(broken * 14 * (1 if px > span_mid else -1) if drop else 0)
        c.drawPath(poly([(-40, 0), (40, 0), (70, river_y - deck_y), (-70, river_y - deck_y)]), P('#3a2f2a'))
        for k in range(4):
            yy = (river_y - deck_y) * k / 4
            c.drawLine(-50 - k * 6, yy, 50 + k * 6, yy + (river_y - deck_y) / 4, P('#5a4a40', 1, stroke=6))
            c.drawLine(50 + k * 6, yy, -50 - k * 6, yy + (river_y - deck_y) / 4, P('#5a4a40', 1, stroke=6))
        c.restore()
    # deck segments
    for sx in range(int(x0) - 230, int(x1) + 230, 230):
        mid = gap0 - 1 < sx < gap1
        drop = ease_in(broken) * 520 if mid else 0
        ang = broken * 22 * (1 if sx > span_mid - 115 else -1) if mid else 0
        c.save()
        c.translate(sx + 115, deck_y + drop)
        c.rotate(ang)
        c.drawRect(skia.Rect(-117, -24, 117, 24), P('#2b2420'))
        c.drawRect(skia.Rect(-117, -24, 117, -14), P('#5f5048'))
        # truss
        for k in range(5):
            xx = -115 + k * 46
            c.drawLine(xx, -24, xx + 23, -110, P('#4a3d36', 1, stroke=5))
            c.drawLine(xx + 23, -110, xx + 46, -24, P('#4a3d36', 1, stroke=5))
        c.drawLine(-115, -110, 115, -110, P('#4a3d36', 1, stroke=7))
        c.restore()


def lightning(c, t, x, seed=0, a=1.0):
    r = random.Random(seed)
    pts = [(x, -MARGIN)]
    y = -MARGIN
    xx = x
    while y < 1000:
        y += r.uniform(40, 110)
        xx += r.uniform(-70, 70)
        pts.append((xx, y))
    for w_, al, bl in ((26, 0.25, 18), (10, 0.6, 4), (4, 1.0, 0)):
        p = P('#e8f0ff', al * a, blur=bl, stroke=w_)
        c.drawPath(poly(pts, closed=False), add_blend(p))
    # branches
    for i in range(3):
        k = r.randint(2, len(pts) - 2)
        bx, by = pts[k]
        bp = [(bx, by)]
        for j in range(4):
            bx += r.uniform(-80, 80)
            by += r.uniform(30, 80)
            bp.append((bx, by))
        c.drawPath(poly(bp, closed=False), add_blend(P('#dfe8ff', 0.5 * a, stroke=3)))


def carriage_interior(c, pal='normal', seed=9):
    """Side wall of a 1962 carriage: wood panels, two windows, luggage rack, lamps."""
    wall = '#6b4a35' if pal == 'normal' else '#3b2f2c'
    c.drawRect(skia.Rect(-MARGIN, -MARGIN, W + MARGIN, H + MARGIN), lin((0, -MARGIN), (0, H), [mix(wall, '#000000', 0.35), wall, mix(wall, '#000000', 0.4)]))
    # ceiling
    c.drawRect(skia.Rect(-MARGIN, -MARGIN, W + MARGIN, 260), lin((0, -MARGIN), (0, 260), ['#2a2220', '#4a3a30']))
    for k in range(-1, 5):
        c.drawLine(-MARGIN + k * 360, 120, -MARGIN + k * 360 + 200, 260, P('#2a201b', 0.6, stroke=8))
    # wood panelling
    for k in range(-2, 28):
        x = k * 52
        c.drawLine(x, 260, x, H + MARGIN, P('#4a3224', 0.55, stroke=2.5))
    brush_strokes(c, -MARGIN, 260, W + MARGIN, H + MARGIN, ['#7a5a42', '#5a3c2a'], 90, (100, 400), (3, 9), math.pi / 2, seed, 0.18)
    # luggage rack
    c.drawRect(skia.Rect(-MARGIN, 330, W + MARGIN, 350), P('#c8b48a'))
    for k in range(-4, 40):
        c.drawLine(k * 30, 350, k * 30 + 8, 420, P('#9a8a6a', 0.9, stroke=2))
    c.drawRect(skia.Rect(-MARGIN, 418, W + MARGIN, 428), P('#c8b48a'))
    # windows (frames only; exterior drawn separately underneath via clip)
    return [skia.Rect(70, 540, 500, 1020), skia.Rect(600, 540, 1030, 1020)]


def seat(c, x, y, w=520, colr='#3f5a46', back_h=520, seed=0):
    """Bench seat seen from the side-front: green moquette."""
    c.drawRoundRect(skia.Rect(x - w / 2, y - back_h, x + w / 2, y - 40), 30, 30, P(colr))
    c.drawRoundRect(skia.Rect(x - w / 2, y - back_h, x + w / 2, y - back_h + 60), 30, 30, P(mix(colr, '#ffffff', 0.15)))
    for k in range(6):
        xx = x - w / 2 + 40 + k * (w - 80) / 5
        c.drawLine(xx, y - back_h + 70, xx, y - 60, P(mix(colr, '#000000', 0.3), 0.5, stroke=3))
    c.drawRoundRect(skia.Rect(x - w / 2 - 20, y - 70, x + w / 2 + 20, y + 10), 20, 20, P(mix(colr, '#ffffff', 0.08)))
    c.drawRect(skia.Rect(x - w / 2 - 20, y + 10, x + w / 2 + 20, y + 220), P('#2a2420'))
    c.drawRoundRect(skia.Rect(x - w / 2, y - back_h, x + w / 2, y - 40), 30, 30, P(INK, 0.8, stroke=3))


def hanging_lamp(c, x, y, t, on=1.0, swing=0.0):
    ang = math.sin(t * 2.2) * 0.12 * swing
    c.save()
    c.translate(x, y)
    c.rotate(math.degrees(ang))
    c.drawLine(0, 0, 0, 110, P('#1a1614', 1, stroke=4))
    c.drawPath(poly([(-50, 110), (50, 110), (30, 140), (-30, 140)]), P('#2a2420'))
    c.drawCircle(0, 160, 24, P(mix('#4a3a2a', '#fff2c8', on)))
    c.restore()
    gx = x + math.sin(ang) * 160
    gy = y + math.cos(ang) * 160
    if on > 0:
        c.drawCircle(gx, gy, 380, add_blend(rad((gx, gy), 380, [('#ffd58a', 0.45 * on), ('#ffd58a', 0)])))


def water_body(c, t, level_y, a=0.85, colr='#1d3550', hi='#7fa6cc', seed=11, choppy=1.0):
    """Rising flood water inside the carriage, with animated surface."""
    pts = [(-MARGIN, H + MARGIN)]
    for i in range(0, 41):
        x = -MARGIN + i * (W + 2 * MARGIN) / 40
        y = level_y + math.sin(x * 0.012 + t * 3.1) * 14 * choppy + math.sin(x * 0.031 - t * 4.7) * 7 * choppy
        pts.append((x, y))
    pts.append((W + MARGIN, H + MARGIN))
    path = smooth_path(pts, closed=True, tension=0.4)
    c.drawPath(path, lin((0, level_y), (0, level_y + 900), [(colr, a * 0.75), (mix(colr, '#050a14', 0.6), a)]))
    surf = pts[1:-1]
    stroke_taper(c, surf, 5, 5, hi, 0.55)
    r = random.Random(seed + int(t * 15))
    for i in range(30):
        x = r.uniform(-50, W + 50)
        y = level_y + r.uniform(-8, 14)
        c.drawOval(skia.Rect(x - 30, y - 3, x + 30, y + 3), P('#d6e8ff', 0.4))
    return path


def bubbles(c, t, x, y, n=12, seed=0, spread=120, rise=500):
    r = random.Random(seed)
    for i in range(n):
        ph = (t * r.uniform(0.4, 0.9) + r.uniform(0, 1)) % 1
        bx = x + r.uniform(-spread, spread) + math.sin(t * 5 + i) * 8
        by = y - ph * rise
        rr = r.uniform(4, 13)
        c.drawCircle(bx, by, rr, P('#cfe6ff', 0.55 * (1 - ph), stroke=2))
        c.drawCircle(bx - rr * 0.3, by - rr * 0.3, rr * 0.25, P('#ffffff', 0.6 * (1 - ph)))


def splash(c, x, y, p, s=1.0, seed=0, colr='#dbe9fb'):
    """Burst of water droplets (p:0..1 progress)."""
    r = random.Random(seed)
    for i in range(60):
        ang = r.uniform(-math.pi * 0.95, -math.pi * 0.05)
        sp = r.uniform(300, 1100) * s
        px = x + math.cos(ang) * sp * p
        py = y + math.sin(ang) * sp * p + 1200 * p * p * s
        rr = r.uniform(3, 12) * s * (1 - p * 0.5)
        c.drawCircle(px, py, rr, P(colr, 0.8 * (1 - p)))
    c.drawOval(skia.Rect(x - 400 * s * (0.3 + p), y - 200 * s * p, x + 400 * s * (0.3 + p), y + 40 * s), P('#cfe1f7', 0.5 * (1 - p), blur=20))


def glass_shards(c, x, y, p, seed=0, s=1.0):
    r = random.Random(seed)
    for i in range(26):
        ang = r.uniform(0, 2 * math.pi)
        sp = r.uniform(150, 700) * s
        px = x + math.cos(ang) * sp * p
        py = y + math.sin(ang) * sp * p + 500 * p * p
        rr = r.uniform(8, 26) * s
        rot = r.uniform(0, 6) + p * r.uniform(-8, 8)
        pts = [(px + math.cos(rot + k * 2.1) * rr * r.uniform(0.6, 1.2), py + math.sin(rot + k * 2.1) * rr * r.uniform(0.6, 1.2)) for k in range(3)]
        c.drawPath(poly(pts), P('#e6f2ff', 0.75 * (1 - p)))
        c.drawPath(poly(pts), P('#ffffff', 0.9 * (1 - p), stroke=1.5))


def suitcase(c, x, y, s=1.0, rot=0.0, colr='#7a4b2c'):
    c.save()
    c.translate(x, y)
    c.rotate(math.degrees(rot))
    c.scale(s, s)
    c.drawRoundRect(skia.Rect(-90, -60, 90, 60), 10, 10, P(colr))
    c.drawRect(skia.Rect(-90, -8, 90, 4), P(mix(colr, '#000000', 0.3)))
    c.drawRoundRect(skia.Rect(-30, -80, 30, -60), 8, 8, P('#2a1e16', 1, stroke=7))
    for bx in (-60, 60):
        c.drawRect(skia.Rect(bx - 6, -60, bx + 6, 60), P('#c9a75a'))
    c.drawRoundRect(skia.Rect(-90, -60, 90, 60), 10, 10, P(INK, 0.9, stroke=3))
    c.restore()


# ================================================================ HOMES
def tatami_room(c, warm=0.0, night=True, seed=12):
    """Haru's empty home: shoji, tatami, low table."""
    base = '#2b2a35' if night else '#d9c9a6'
    c.drawRect(skia.Rect(-MARGIN, -MARGIN, W + MARGIN, H + MARGIN), P(base))
    # shoji wall
    sh_c = '#e6dcc4' if not night else '#6f6a78'
    c.drawRect(skia.Rect(-MARGIN, 200, W + MARGIN, 1180), P(sh_c))
    if night:
        c.drawRect(skia.Rect(-MARGIN, 200, W + MARGIN, 1180), lin((0, 200), (0, 1180), [('#8a9ac8', 0.35), ('#3a3448', 0.3)]))
        brush_blobs(c, -MARGIN, 200, W + MARGIN, 1180, ['#8a9ac8', '#5a5468'], 20, 60, 200, seed, 0.2, 30)
    for k in range(-2, 40):
        x = k * 36
        c.drawLine(x, 200, x, 1180, P('#3a2e28', 0.55, stroke=1.6))
    for k in range(0, 26):
        y = 200 + k * 40
        c.drawLine(-MARGIN, y, W + MARGIN, y, P('#3a2e28', 0.5, stroke=1.6))
    for k in range(-1, 6):
        x = k * 270
        c.drawRect(skia.Rect(x - 9, 200, x + 9, 1180), P('#3a2a22'))
    c.drawRect(skia.Rect(-MARGIN, 1150, W + MARGIN, 1185), P('#3a2a22'))
    # beam
    c.drawRect(skia.Rect(-MARGIN, 160, W + MARGIN, 210), P('#3a2a22'))
    # tatami floor in perspective
    fl = poly([(-MARGIN, 1180), (W + MARGIN, 1180), (W + MARGIN, H + MARGIN), (-MARGIN, H + MARGIN)])
    c.drawPath(fl, lin((0, 1180), (0, H), ['#8f8a5c' if not night else '#4a4a3a', '#b6ad78' if not night else '#5a5844']))
    for k in range(-6, 8):
        c.drawLine(W / 2 + k * 120, 1180, W / 2 + k * 420, H + MARGIN, P('#3a3624', 0.5, stroke=3))
    for yy in (1300, 1500, 1800):
        c.drawLine(-MARGIN, yy, W + MARGIN, yy, P('#3a3624', 0.5, stroke=3))
    brush_strokes(c, -MARGIN, 1180, W + MARGIN, H + MARGIN, ['#a49c6a', '#6d6848'], 60, (100, 300), (2, 6), 0.0, seed, 0.2)


def low_table(c, x, y, s=1.0, colr='#4a2e20'):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    c.drawPath(poly([(-340, -40), (340, -40), (400, 60), (-400, 60)]), P(colr))
    c.drawPath(poly([(-340, -40), (340, -40), (400, 60), (-400, 60)]), lin((0, -40), (0, 60), [(mix(colr, '#ffffff', 0.15), 1), (colr, 1)]))
    c.drawRect(skia.Rect(-400, 60, 400, 90), P(mix(colr, '#000000', 0.35)))
    for lx in (-360, 360):
        c.drawRect(skia.Rect(lx - 18, 90, lx + 18, 200), P(mix(colr, '#000000', 0.45)))
    c.restore()


def teacup(c, x, y, s=1.0, full=1.0, steam_t=None, colr='#e9e2d2', glaze='#5b7f8a'):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    c.drawOval(skia.Rect(-56, 34, 56, 50), P('#000000', 0.25, blur=6))
    cup = smooth_path([(-50, -40), (50, -40), (42, 20), (26, 44), (-26, 44), (-42, 20)])
    c.drawPath(cup, P(colr))
    c.drawPath(cup, lin((-50, 0), (50, 0), [(colr, 0.0), ('#9a9080', 0.5)]))
    c.drawRect(skia.Rect(-48, -40, 48, -24), P(glaze, 0.85))
    c.drawOval(skia.Rect(-50, -50, 50, -30), P('#d9d2c2'))
    if full > 0:
        c.drawOval(skia.Rect(-44, -47, 44, -33), P('#8a7a3a', full))
        c.drawOval(skia.Rect(-30, -45, 0, -39), P('#e6d48a', 0.5 * full))
    c.drawPath(cup, P(INK, 0.8, stroke=2.4))
    c.restore()
    if steam_t is not None:
        for k in range(3):
            ph = (steam_t * 0.35 + k / 3) % 1
            sx = x + math.sin(steam_t * 1.4 + k * 2) * 14 * s
            sy = y - 50 * s - ph * 160 * s
            c.drawCircle(sx, sy, (12 + ph * 30) * s, P('#ffffff', 0.25 * (1 - ph), blur=10 * s))


def teapot(c, x, y, s=1.0, rot=0.0, colr='#3f3a38'):
    c.save()
    c.translate(x, y)
    c.rotate(math.degrees(rot))
    c.scale(s, s)
    body = smooth_path(ellipse_pts(0, 0, 110, 90, 24))
    c.drawPath(body, P(colr))
    c.drawPath(body, rad((-40, -40), 160, [('#6a625e', 1), (colr, 1)]))
    c.drawPath(poly([(100, -10), (190, -70), (200, -60), (110, 30)]), P(colr))
    c.drawPath(smooth_path([(-90, -60), (-150, -40), (-150, 30), (-90, 40)], closed=False), P('#2a2624', 1, stroke=12))
    c.drawOval(skia.Rect(-40, -100, 40, -80), P('#2a2624'))
    c.drawCircle(0, -104, 10, P('#2a2624'))
    c.drawPath(body, P(INK, 0.8, stroke=3))
    c.restore()


def photo_frame(c, x, y, s=1.0, rot=0.0, img_fn=None, aged=0.6):
    """Black & white photograph in a small wooden frame."""
    c.save()
    c.translate(x, y)
    c.rotate(math.degrees(rot))
    c.scale(s, s)
    c.drawRect(skia.Rect(-170, -220, 170, 220), P('#4a3426'))
    c.drawRect(skia.Rect(-150, -200, 150, 200), P('#efe8da'))
    c.drawRect(skia.Rect(-130, -180, 130, 160), P('#8a8a86'))
    if img_fn:
        c.save()
        c.clipRect(skia.Rect(-130, -180, 130, 160))
        img_fn(c)
        c.restore()
    c.drawRect(skia.Rect(-130, -180, 130, 160), P('#d6b98a', 0.25 * aged))
    c.drawRect(skia.Rect(-170, -220, 170, 220), P(INK, 0.9, stroke=4))
    c.restore()


def maryam_room(c, seed=13):
    """Warm spring evening interior with window, curtains (drawn per-frame), sill."""
    c.drawRect(skia.Rect(-MARGIN, -MARGIN, W + MARGIN, H + MARGIN), lin((0, -MARGIN), (0, H), ['#d8a46a', '#c98a52', '#8f5a36']))
    brush_blobs(c, -MARGIN, -MARGIN, W + MARGIN, H + MARGIN, ['#e8b67a', '#b9784a', '#f0c48a'], 50, 80, 260, seed, 0.18, 30)
    # wallpaper subtle pattern
    r = random.Random(seed)
    for i in range(80):
        x, y = r.uniform(-MARGIN, W + MARGIN), r.uniform(-MARGIN, 1300)
        c.drawCircle(x, y, 5, P('#f6d2a0', 0.25))
    # floor
    c.drawRect(skia.Rect(-MARGIN, 1300, W + MARGIN, H + MARGIN), lin((0, 1300), (0, H), ['#7a4a2c', '#5a341e']))
    for k in range(-3, 12):
        c.drawLine(k * 110, 1300, k * 160 - 200, H + MARGIN, P('#4a2a18', 0.4, stroke=3))


def window_view(c, x0, y0, x1, y1, t, mode='spring_evening', station=True):
    """What is seen through the window: sunset sky, rooftops, distant empty station."""
    c.save()
    c.clipRect(skia.Rect(x0, y0, x1, y1))
    c.drawRect(skia.Rect(x0, y0, x1, y1), lin((0, y0), (0, y1), ['#f3b46c', '#ffd9a0', '#f6c58c']))
    c.drawCircle(x0 + (x1 - x0) * 0.7, y0 + (y1 - y0) * 0.55, 70, add_blend(P('#fff3d0', 0.9, blur=10)))
    c.drawCircle(x0 + (x1 - x0) * 0.7, y0 + (y1 - y0) * 0.55, 240, add_blend(P('#ffcf8a', 0.35, blur=60)))
    # hills
    hy = y0 + (y1 - y0) * 0.62
    c.drawPath(smooth_path([(x0 - 50, y1), (x0 - 50, hy), (x0 + 200, hy - 50), (x0 + 420, hy - 10), (x1 + 50, hy - 60), (x1 + 50, y1)]), P('#c98a6a', 0.8))
    # rooftops
    for k in range(7):
        rx = x0 + k * (x1 - x0) / 6 - 40
        ry = hy + 40 + (k % 3) * 18
        c.drawPath(poly([(rx - 70, ry), (rx, ry - 50), (rx + 70, ry), (rx + 60, y1), (rx - 60, y1)]), P('#7a4a3a', 0.9))
    if station:
        sx = x0 + (x1 - x0) * 0.32
        sy = hy + 10
        c.drawRect(skia.Rect(sx - 80, sy - 50, sx + 60, sy + 20), P('#6a3a2e'))
        c.drawPath(poly([(sx - 100, sy - 50), (sx + 80, sy - 50), (sx + 60, sy - 75), (sx - 80, sy - 75)]), P('#4a2a24'))
        c.drawLine(sx - 300, sy + 30, sx + 400, sy + 30, P('#5a3a30', 1, stroke=4))
        c.drawLine(sx + 30, sy - 50, sx + 30, sy - 110, P('#3a2420', 1, stroke=3))
        c.drawCircle(sx + 30, sy - 120, 10, P('#3a2420'))
    # birds
    for k in range(3):
        bx = x0 + ((t * 30 + k * 160) % (x1 - x0 + 200)) - 100
        by = y0 + 120 + k * 40 + math.sin(t * 2 + k) * 10
        wf = math.sin(t * 9 + k) * 8
        c.drawPath(poly([(bx - 14, by - wf), (bx, by), (bx + 14, by - wf)], closed=False), P('#5a3a30', 0.8, stroke=2.5))
    c.restore()


def curtain(c, x, y_top, y_bot, w, t, side=1, colr='#f2e6cf', breeze=1.0, seed=0):
    pts_l = []
    n = 12
    for i in range(n + 1):
        f = i / n
        y = lerp(y_top, y_bot, f)
        sway = math.sin(t * 1.3 + f * 2.5) * 26 * f * breeze + math.sin(t * 2.1 + f * 4) * 8 * f * breeze
        pts_l.append((x + sway * side, y))
    pts_r = [(px + w * (0.75 + 0.25 * math.sin(i * 0.7 + t)) * side, py) for i, (px, py) in enumerate(pts_l)]
    path = smooth_path(pts_l + pts_r[::-1], tension=0.4)
    c.drawPath(path, P(colr, 0.92))
    _ = [stroke_taper(c, [(pts_l[i][0] + side * w * (k + 1) / 5, pts_l[i][1]) for i in range(0, n + 1, 3)], 3, 6, '#cdb894', 0.45) for k in range(4)]
    c.drawPath(path, add_blend(lin((x, 0), (x + side * w, 0), [('#ffd9a0', 0.0), ('#ffd9a0', 0.25)])))


def light_shafts(c, x, y, ang, n=4, L=1600, w=160, colr='#ffd9a0', a=0.18, t=0.0):
    for k in range(n):
        off = (k - n / 2) * w * 0.9
        aa = a * (0.6 + 0.4 * math.sin(t * 0.7 + k * 1.3))
        dx, dy = math.cos(ang), math.sin(ang)
        px, py = -dy, dx
        p0 = (x + px * off, y + py * off)
        pts = [p0, (p0[0] + px * w * 0.4, p0[1] + py * w * 0.4), (p0[0] + dx * L + px * w, p0[1] + dy * L + py * w), (p0[0] + dx * L - px * w * 0.2, p0[1] + dy * L - py * w * 0.2)]
        c.drawPath(poly(pts), add_blend(P(colr, aa, blur=30)))


def dust_motes(c, t, x0, y0, x1, y1, n=40, seed=0, colr='#fff0c8'):
    r = random.Random(seed)
    for i in range(n):
        bx, by = r.uniform(x0, x1), r.uniform(y0, y1)
        x = bx + math.sin(t * 0.3 + i) * 30
        y = by + math.cos(t * 0.25 + i * 1.7) * 25 - t * 6
        y = y0 + (y - y0) % (y1 - y0)
        c.drawCircle(x, y, r.uniform(1.5, 3.5), add_blend(P(colr, r.uniform(0.2, 0.6), blur=1.5)))


def sakura_tree(c, x, y, s=1.0, seed=0, season='spring'):
    r = random.Random(seed)
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    stroke_taper(c, [(0, 0), (10, -200), (-20, -420), (30, -620)], 70, 22, '#3a2a24')
    for k in range(5):
        a = -1.2 + k * 0.6
        stroke_taper(c, [(0, -400 - k * 40), (math.cos(a - 1.57) * 260, -520 - k * 40 + math.sin(a - 1.57) * 140)], 22, 6, '#3a2a24')
    pal = {'spring': ['#f6c6d0', '#f9dce2', '#e8a6b6', '#ffffff'], 'autumn': ['#d9773a', '#e9a24a', '#b9472a', '#f2c46a'],
           'winter': ['#e8eef9', '#c9d6ee', '#ffffff'], 'summer': ['#6a9a5a', '#4a7a44', '#8ab86a']}[season]
    if season == 'winter':
        for k in range(6):
            a = -1.4 + k * 0.55
            stroke_taper(c, [(0, -560), (math.cos(a - 1.57) * 380, -650 + math.sin(a - 1.57) * 200)], 14, 3, '#3a2a24')
        brush_blobs(c, -380, -900, 380, -520, pal, 30, 20, 70, seed, 0.5, 6, 0.4)
    else:
        brush_blobs(c, -450, -1050, 450, -430, pal, 140, 30, 110, seed, 0.55, 8, 0.7)
    c.restore()

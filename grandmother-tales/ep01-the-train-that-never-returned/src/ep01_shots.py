"""Episode 01 — The Train That Never Returned (القطار الذي لم يعد): shot timeline.
Shares the series library (characters, sets, effects, renderer) with Episodes 02 and 03.
"""
import os, sys, math, random
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, '..', '..', 'ep03-harus-last-journey', 'src')))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, '..', '..', 'ep02-the-paper-crane', 'src')))
import numpy as np
import skia
from core import *
from chars import *
from chars import _limb, _hand, _clip_path
from env import *
import shots as ep3
from shots import blink, snow_all, cached, bokeh_bg, station_plates, station_wide, train_pass, GR_NIGHT, GR_WARMNIGHT, GR_MEM
import ep02_shots as ep2
from ep02_shots import letter_paper, home_night, GR_HOME

ENV = None


def talk(T, gain=1.0):
    ep3.ENV = ENV
    return ep3.talk(T, gain)


GR_SUN = dict(tint=(1.12, 0.98, 0.84), sat=1.0, contrast=1.04, grain=0.06, vig=0.9, bloom=0.75)
GR_DAY = dict(tint=(1.02, 1.0, 1.0), sat=0.95, contrast=1.02, grain=0.05, vig=0.8, bloom=0.5)

# the son, twenty years older (same face, navy coat, beige scarf; a little grey at the temples)
CHARS['son42'] = dict(CHARS['son'], hair='#2e2c2c', hair_sh='#151414', age='young')
CHARS['passer1'] = dict(CHARS['oldman62'], coat='#5a5a62', coat_sh='#3a3a42', coat_hi='#7a7a84')
CHARS['passer2'] = dict(CHARS['father'], coat='#6a5040', coat_sh='#46342a', coat_hi='#8a6c58', mustache=None)


def sunset_far(c):
    sky(c, '#3a4a8a', '#ffb070', '#e07a6a')
    c.drawCircle(W * 0.72, 1010, 90, P('#fff0c0'))
    c.drawCircle(W * 0.72, 1010, 420, add_blend(rad((W * 0.72, 1010), 420, [('#ffd08a', 0.55), ('#ffd08a', 0)])))
    brush_strokes(c, -MARGIN, 300, W + MARGIN, 900, ['#f0a080', '#c06a7a', '#ffc890'], 50, (150, 400), (8, 24), 0.05, 2, 0.35)
    r = random.Random(1)
    for layer, (yb, colr, amp) in enumerate(((1000, '#8a5a7a', 90), (1070, '#6a4466', 70))):
        pts = [(-MARGIN, H + MARGIN)]
        for i in range(15):
            x = -MARGIN + i * (W + 2 * MARGIN) / 14
            pts.append((x, yb - amp * (0.5 + 0.5 * math.sin(i * 0.9 + layer * 2 + 1)) - r.uniform(0, 30)))
        pts.append((W + MARGIN, H + MARGIN))
        c.drawPath(smooth_path(pts, closed=True, tension=0.4), P(colr))


def day_far(c):
    sky(c, '#9fb8dc', '#eef2f8', '#cfdcee')
    brush_blobs(c, -MARGIN, -MARGIN, W + MARGIN, 900, ['#ffffff', '#dfe8f4'], 24, 80, 260, 5, 0.4, 40)
    for layer, (yb, colr, amp) in enumerate(((1000, '#b8c4d8', 90), (1070, '#9aa8c0', 70))):
        pts = [(-MARGIN, H + MARGIN)]
        for i in range(15):
            x = -MARGIN + i * (W + 2 * MARGIN) / 14
            pts.append((x, yb - amp * (0.5 + 0.5 * math.sin(i * 0.9 + layer * 2 + 1))))
        pts.append((W + MARGIN, H + MARGIN))
        c.drawPath(smooth_path(pts, closed=True, tension=0.4), P(colr))


def station(c, t, T, cam, chars_fn=None, mode='sunset', snow=False, lamp=0.0, clock_mm=40.0, clock_hh=4):
    far = cached('far_' + mode, lambda: paint_plate(sunset_far if mode == 'sunset' else (day_far if mode == 'day' else station_far)))
    _, mid = station_plates()
    plate(c, far, cam, 0.35)
    plate(c, mid, cam, 0.8)
    if mode == 'sunset':
        c.drawPaint(multiply(P('#ffc8a0', 0.35)))
    c.save()
    cam.apply(c, 0.8)
    lamp_post(c, 760, 1150, 0.85, on=lamp)
    if lamp:
        lamp_glow(c, 760, 630, 420, lamp)
    station_clock(c, 190, 700, 0.75, clock_hh, clock_mm)
    c.restore()
    c.save()
    cam.apply(c)
    bench(c, 280, 1720, 1.15, snow=0.9 if snow else 0.4)
    if chars_fn:
        chars_fn(c)
    c.restore()
    if snow:
        snow_all(c, T, near=True)


SEAT_Y = 1720 - 170 * 1.15


def haru_seated(c, t, T, head=None, arms=None, s=0.72, x=200):
    h = dict(look=(1.0, 0.0), eye_open=blink(t, 2), brow=0.5)
    h.update(head or {})
    figure(c, 'haru', x, SEAT_Y + 600 * s, s, yaw=0.45, t=t, seed=int(T * 15), sit=True,
           arms=arms or dict(L=(18, 32), R=(22, 30)), head=h)


# ------------------------------------------------------------------ shots
def b01_establish(c, t, T):
    p = ease_io(seg(t, 0, 5.3))
    cam = Cam(lerp(1.0, 1.08, p), 0, lerp(-500, 0, p), t=t)
    station(c, t, T, cam, mode='sunset')
    for k in range(6):  # birds crossing the sunset
        bx = ((t * 80 + k * 140) % 1400) - 200
        by = 500 + k * 30 + math.sin(t * 2 + k) * 10
        wf = math.sin(t * 9 + k) * 8
        c.drawPath(poly([(bx - 14, by - wf), (bx, by), (bx + 14, by - wf)], closed=False), P('#4a2a3a', 0.8, stroke=2.5))


def b02_haru_walks(c, t, T):
    cam = Cam(1.15, 80, -80, t=t)
    w = seg(t, 0, 2.54)

    def chars_fn(cc):
        figure(cc, 'haru', lerp(1000, 520, w), 1780, 0.72, yaw=-0.5, t=t, seed=int(T * 15), walk=t * 0.9, lean=0.06,
               arms=dict(L=(-6, -6), R=(6, 6)), head=dict(look=(-1, 0.2), eye_open=blink(t, 3), brow=0.4))
    station(c, t, T, cam, chars_fn, mode='sunset')


def b03_sits(c, t, T):
    cam = Cam(1.2, 120, -120, t=t)
    sit = ease_io(seg(t, 0.0, 1.6))
    day2 = t > 2.4

    def chars_fn(cc):
        if sit < 1 and not day2:
            figure(cc, 'haru', lerp(300, 200, sit), lerp(1780, SEAT_Y + 600 * 0.72, sit), 0.72, yaw=0.45, t=t, seed=int(T * 15), sit=sit > 0.5,
                   lean=0.2 * math.sin(sit * math.pi), arms=dict(L=(20, 30), R=(24, 30)), head=dict(look=(1, 0.2)))
        else:
            haru_seated(cc, t, T)
    station(c, t, T, cam, chars_fn, mode='sunset', clock_mm=40 if not day2 else 45)
    if 2.25 < t < 2.6:
        c.drawPaint(P('#ffe2b0', 0.5 * (1 - abs(t - 2.42) / 0.18)))


def b04_crane(c, t, T):
    bokeh_bg(c, t, colors=('#ffcf8a', '#ff9a7a'), seed=3, base=('#6a4a6a', '#c98a6a'))
    # wooden bench slats
    for k in range(3):
        c.drawRoundRect(skia.Rect(-50, 1250 + k * 70, W + 50, 1305 + k * 70), 10, 10, P('#6a4a36' if k % 2 == 0 else '#5a3e2c'))
    put = ease_io(seg(t, 0.2, 1.6))
    crane(c, 560, lerp(1050, 1230, put), 1.6, paper='#f3ece0', glow=0.25)
    hy = lerp(980, 1150, put) - 40 * seg(t, 1.8, 2.6)
    _limb(c, (-100, 600), (150, 900), (430, hy), 200, 170, CHARS['haru']['coat'], CHARS['haru']['coat_sh'], 2)
    _hand(c, 470, hy - 20, -1.2, 150, CHARS['haru']['skin'], CHARS['haru']['skin_sh'], 3, grip=put < 0.95, open_=0.3)
    c.drawPaint(add_blend(P('#ffb070', 0.08)))


def b05_waits(c, t, T):
    if t < 1.6:
        bokeh_bg(c, t, colors=('#ffcf8a', '#ff9a7a'), seed=4, base=('#6a4a6a', '#c98a6a'))
        bust(c, 'haru', 520, 900, 2.7, yaw=0.45, t=t, seed=int(t * 15),
             head=dict(look=(1.0, -0.1), eye_open=blink(t, 3), brow=0.6, mouth='neutral', light_dir=1, rim=0.6, rim_c='#ffc890'))
    else:
        far = cached('far_sunset', lambda: paint_plate(sunset_far))
        plate(c, far, Cam(1.0, 0, 200), 0.35)
        c.drawPaint(multiply(P('#ffc8a0', 0.3)))
        tracks(c, 540, 1050, H + 200, 1700, 30, rail='#7a6a7a', snow='#e8c8b8', seed=5)
        mist(c, T, 950, 1150, '#ffd0b0', 0.25, 8, 3, 15)


def b06_nobody_knew(c, t, T):
    cam = Cam(1.0, 0, 0, t=t)

    def chars_fn(cc):
        haru_seated(cc, t, T, head=dict(look=(1, -0.1)))
        for k, (ch, x0, dirn, sp) in enumerate((('passer1', 1100, -1, 210), ('passer2', -200, 1, 180), ('passer1', 1300, -1, 240))):
            x = x0 + dirn * sp * (t + k * 0.6)
            figure(cc, ch, x, 1900 + k * 40, 0.8 + k * 0.05, yaw=0.5 * dirn, t=t, seed=int(T * 15) + 10 + k, walk=t * 1.3 + k * 0.3,
                   arms=dict(L=(-6, -6), R=(6, 6)), head=dict(look=(dirn, 0.1), mouth='neutral'))
    station(c, t, T, cam, chars_fn, mode='sunset')


def b07_maryam_comes(c, t, T):
    cam = Cam(1.2, 100, -120, t=t)
    w = ease_out(seg(t, 0, 3.6))

    def chars_fn(cc):
        haru_seated(cc, t, T, head=dict(look=(lerp(1, 0.6, w), 0.1 if w < 0.8 else 0.4)))
        figure(cc, 'maryam', lerp(1050, 520, w), 1780, 0.68, yaw=-0.5, t=t, seed=int(T * 15) + 3, walk=t * 1.2 if w < 0.98 else None,
               arms=dict(L=(-8, 6), R=(8, -6)), head=dict(look=(-1, 0.0), brow=0.2, mouth='neutral', eye_open=blink(t, 5)))
    station(c, t, T, cam, chars_fn, mode='sunset')


def b08_why(c, t, T):
    bokeh_bg(c, t, colors=('#ffcf8a', '#ff9a7a', '#c9a0d0'), seed=5, base=('#6a4a6a', '#c98a6a'))
    bust(c, 'maryam', 540, 920, 2.8, yaw=-0.35, t=t, seed=int(t * 15),
         head=dict(look=(-0.6, 0.4), eye_open=blink(t, 4), brow=0.2, mouth='talk', mouth_open=talk(T, 1.3) * 0.5, blush=0.4, light_dir=1, rim=0.6, rim_c='#ffc890'))


def b09_my_son(c, t, T):
    bokeh_bg(c, t, colors=('#ffcf8a', '#ff9a7a'), seed=6, base=('#6a4a6a', '#c98a6a'))
    bust(c, 'haru', 520, 900, 2.7, yaw=0.4, t=t, seed=int(t * 15),
         head=dict(look=(0.6, 0.5), eye_open=blink(t, 3), brow=0.2, mouth='talk' if t > 0.9 else 'smile', mouth_open=talk(T, 1.2) * 0.5 if t > 0.9 else 0,
                   light_dir=1, rim=0.6, rim_c='#ffc890'))


def b10_twenty_years(c, t, T):
    if t < 1.5:
        bokeh_bg(c, t, colors=('#ffcf8a', '#ff9a7a'), seed=6, base=('#6a4a6a', '#c98a6a'))
        bust(c, 'haru', 520, 900, 2.7, yaw=0.4, t=t, seed=int(t * 15),
             head=dict(look=(0.3, 0.8), eye_open=0.8, brow=1.0, mouth='talk', mouth_open=talk(T, 1.2) * 0.5, tears=0.4, tear_t=t, light_dir=1, rim=0.5, rim_c='#ffc890'))
        return
    # memory, sepia: the young son walks away down the platform with his bag, 1962
    tt = t - 1.5
    far = cached('far_day', lambda: paint_plate(day_far))
    _, mid = station_plates()
    plate(c, far, Cam(1.0), 0.35)
    plate(c, mid, Cam(1.0), 0.8)
    w = seg(tt, 0, 3.6)
    figure(c, 'haru62', 230, 1850, 0.75, yaw=0.5, t=tt, seed=int(T * 15), arms=dict(L=(-6, -6), R=(30 + 30 * seg(tt, 1.0, 2.0), 20), Ropen=1),
           head=dict(look=(1, 0), brow=0.9, mouth='open' if 1.0 < tt < 2.2 else 'sad', mouth_open=0.3))
    figure(c, 'son', lerp(560, 900, w), lerp(1860, 1560, w), lerp(0.78, 0.5, w), yaw=0.4, t=tt, seed=int(T * 15) + 1, walk=tt * 1.2, back=True,
           arms=dict(L=(-6, -6), R=(10, 10)), head=dict(back=True))
    suitcase(c, lerp(640, 950, w), lerp(1440, 1320, w), lerp(0.7, 0.45, w))
    c.drawRect(skia.Rect(0, 0, W, H), rad((W / 2, H / 2), 1150, [('#f3e2c0', 0.0), ('#f3e2c0', 0.0), ('#f3e2c0', 0.85)], [0, 0.6, 1]))
    c.drawPaint(P('#ffffff', 0.6 * (1 - seg(tt, 0, 0.4))))


def b11_takes_crane(c, t, T):
    bokeh_bg(c, t, colors=('#ffcf8a', '#ff9a7a'), seed=7, base=('#6a4a6a', '#c98a6a'))
    for k in range(3):
        c.drawRoundRect(skia.Rect(-50, 1250 + k * 70, W + 50, 1305 + k * 70), 10, 10, P('#6a4a36' if k % 2 == 0 else '#5a3e2c'))
    up = ease_io(seg(t, 0.6, 1.8))
    crane(c, 560, lerp(1230, 950, up), 1.6, paper='#f3ece0', glow=0.2)
    for side in (-1, 1):
        _hand(c, 560 + side * 170, lerp(1300, 1020, up) - (1 - seg(t, 0, 0.6)) * 300, side * 2.1, 100, CHARS['maryam']['skin'], CHARS['maryam']['skin_sh'], 4 + side, grip=True)


def b12_address(c, t, T):
    bokeh_bg(c, t, colors=('#ffcf8a', '#ff9a7a'), seed=7, base=('#5a3a5a', '#a87060'))
    u = ease_io(seg(t, 0.2, 2.0))
    if u < 0.55:
        crane(c, 540, 1000, 2.8 * (1 - u * 0.6), rot=u * 1.2, flap=-u * 2)
    if u > 0.35:
        with Layer(c, seg(u, 0.35, 0.8)):
            c.save()
            c.translate(540, 1000)
            sc = lerp(0.2, 1.0, seg(u, 0.35, 1.0))
            c.scale(sc, 1.0)
            c.drawRect(skia.Rect(-380, -380, 380, 380), P('#f3ece0'))
            for a, b in (((-380, -380), (380, 380)), ((380, -380), (-380, 380)), ((0, -380), (0, 380)), ((-380, 0), (380, 0))):
                c.drawLine(*a, *b, P('#b0a690', 0.4, stroke=2))
            c.drawCircle(230, -230, 46, P('#c8202a', 0.92))
            # an old address in faded ink (abstract strokes, not legible text)
            r = random.Random(3)
            for ln in range(3):
                y = -40 + ln * 70
                x = 240
                while x > -260:
                    wdt = r.uniform(30, 70)
                    stroke_taper(c, [(x, y + r.uniform(-4, 4)), (x - wdt, y + r.uniform(-4, 4))], 4, 2, '#3a3a5a', 0.7 * seg(t, 1.8, 2.8))
                    x -= wdt + 18
            c.restore()
    for side in (-1, 1):
        hx = 540 + side * lerp(240, 390, u)
        _hand(c, hx, 1250, side * 2.4, 100, CHARS['maryam']['skin'], CHARS['maryam']['skin_sh'], 6 + side, grip=True)


def b13_writes(c, t, T):
    home_night(c, t, T)
    # desk, lamp, Maryam writing
    c.drawRect(skia.Rect(-50, 1450, W + 50, 1560), P('#5a3a26'))
    c.drawRect(skia.Rect(-50, 1560, W + 50, H + 50), P('#3a2418'))
    lamp_glow(c, 880, 1150, 600, 0.9, '#ffc070')
    c.drawPath(poly([(820, 1150), (940, 1150), (900, 1080), (860, 1080)]), P('#2a3a2a'))
    figure(c, 'maryam', 420, 1950, 1.0, yaw=0.5, t=t, seed=int(T * 15), sit=True, legs_hidden=True, lean=0.2,
           arms=dict(L=(70, 50), R=(80 + 8 * math.sin(t * 9), 40)), head=dict(look=(0.6, 0.8), brow=0.5, mouth='neutral', eye_open=blink(t, 5), tilt=0.15))
    c.drawPath(poly([(480, 1440), (900, 1440), (930, 1470), (450, 1470)]), P('#f3ece0'))


def b14_letter(c, t, T):
    c.drawPaint(lin((0, 0), (0, H), ['#3a2418', '#1a100a']))
    lamp_glow(c, 900, 200, 900, 0.8, '#ffc070')
    c.save()
    c.translate(540, 980)
    c.rotate(-4)
    c.drawRect(skia.Rect(-400, -560, 400, 560), P('#f6efe0'))
    for k in range(14):
        c.drawLine(-350, -460 + k * 70, 350, -460 + k * 70, P('#b8c4d8', 0.6, stroke=2))
    # Arabic-style handwriting, right to left, appearing as she writes (abstract, not legible)
    r = random.Random(11)
    prog = ease_io(seg(t, 0.0, 5.6))
    total = 0
    pen = (0, 0)
    for ln in range(9):
        y = -470 + ln * 70
        x = 330
        while x > -330:
            wdt = r.uniform(40, 110)
            total += 1
            if total / 70 > prog:
                break
            pts = [(x, y), (x - wdt * 0.3, y - r.uniform(0, 14)), (x - wdt * 0.6, y + 4), (x - wdt, y - r.uniform(0, 10))]
            stroke_taper(c, pts, 4, 2.5, '#1d2a5a', 0.85)
            if r.random() < 0.4:
                c.drawCircle(x - wdt * 0.5, y - 20, 3, P('#1d2a5a', 0.85))
            pen = (x - wdt, y)
            x -= wdt + r.uniform(12, 22)
    _limb(c, (pen[0] + 600, pen[1] + 900), (pen[0] + 300, pen[1] + 500), (pen[0] + 60, pen[1] + 80), 150, 120, CHARS['maryam']['coat'], CHARS['maryam']['coat_sh'], 8)
    stroke_taper(c, [(pen[0] + 70, pen[1] + 60), (pen[0], pen[1])], 12, 6, '#2a2420')
    _hand(c, pen[0] + 70, pen[1] + 70, 0.6, 90, CHARS['maryam']['skin'], CHARS['maryam']['skin_sh'], 9, grip=True)
    c.restore()


def b15_weeks(c, t, T):
    # match cuts: Haru and Maryam on the bench as autumn turns to the first snow
    k = min(2, int(t / 1.1))
    pal = [('#e3b77a', '#9a6a3a', '#f3d6a6', 'autumn'), ('#c9b8a0', '#7a6a5a', '#e0d4c4', 'autumn'), ('#c9d6ee', '#7d8fb8', '#e9eff9', 'winter')][k]
    c.drawPaint(lin((0, 0), (0, H), [pal[2], pal[0]]))
    sakura_tree(c, 880, 1300, 1.0, seed=4, season=pal[3])
    c.drawRect(skia.Rect(0, 1300, W, H), lin((0, 1300), (0, H), [pal[1], mix(pal[1], '#000000', 0.25)]))
    bench(c, 420, 1640, 1.2, snow=1.0 if k == 2 else 0.0)
    figure(c, 'haru', 330, 1640 - 170 * 1.2 + 600 * 0.75, 0.75, yaw=0.45, t=t, seed=int(T * 15), sit=True,
           arms=dict(L=(18, 30), R=(22, 28)), head=dict(look=(1.0, 0.0), eye_open=blink(t, 2), brow=0.6))
    figure(c, 'maryam', 600, 1640 - 170 * 1.2 + 330 * 0.75 + 20, 0.75, yaw=0.45, t=t, seed=int(T * 15) + 3, sit=True,
           arms=dict(L=(18, 30), R=(22, 28)), head=dict(look=(1.0, -0.1), eye_open=blink(t, 5), brow=0.5))
    crane(c, 470, 1640 - 170 * 1.2 - 20, 0.25)
    if k == 2:
        snow_all(c, T, near=False)
    fr = t % 1.1
    if t > 1.0 and fr < 0.18:
        c.drawPaint(P('#ffffff', 0.35 * (1 - fr / 0.18)))


def b16_train_arrives(c, t, T):
    c.drawPaint(lin((0, 0), (0, H), ['#0b1430', '#3e4f78']))
    far, mid = station_plates()
    plate(c, far, Cam(1.0, 0, 120), 0.35)
    c.drawRect(skia.Rect(0, 1150, W, H), lin((0, 1150), (0, H), ['#6f80aa', '#c9d6ee']))
    stop = ease_out(seg(t, 0, 3.1))
    xo = lerp(1400, -1500, stop)
    train_pass(c, T, xo, 1.0, y=1620, scale=1.0)
    steam_puffs(c, xo - 200, 1100, T, 0.8, 6, '#e9edf6', 0.4)
    mist(c, T, 1300, 1800, '#e6ecf8', 0.3, 10, 6, 30, blend_add=True)
    snow_all(c, T, near=True, dens=1.2)


def b17_man_steps(c, t, T):
    c.drawPaint(lin((0, 0), (0, H), ['#0b1430', '#2a3a66']))
    # carriage door, lit from inside
    c.drawRect(skia.Rect(0, 200, W, 1500), P(TRAIN['body']))
    c.drawRect(skia.Rect(0, 200, W, 1500), lin((0, 200), (0, 1500), [(TRAIN['body_hi'], 0.4), (TRAIN['body_sh'], 0.8)]))
    c.drawRect(skia.Rect(320, 320, 760, 1500), lin((0, 320), (0, 1500), ['#fff0c2', '#ffd27a', '#e09a4c']))
    c.drawRect(skia.Rect(320, 320, 760, 1500), P('#1a1414', 1, stroke=16))
    c.drawRect(skia.Rect(0, 1500, W, H), lin((0, 1500), (0, H), ['#8a9cc6', '#d7e1f4']))
    if t < 1.9:
        st = ease_io(seg(t, 0.2, 1.7))
        figure(c, 'son42', 540, lerp(1500, 1900, st), lerp(0.9, 1.0, st), yaw=-0.2, t=t, seed=int(T * 15), walk=t * 1.0 if st < 1 else None,
               arms=dict(L=(-8, -6), R=(6, 6)), head=dict(look=(-0.5, 0.2), brow=0.6, eye_open=blink(t, 3)), rim=0.6, rim_c='#ffd890', light_dir=1)
    else:
        bokeh_bg(c, t, colors=('#ffcf7a', '#9fb4e6'), seed=9)
        crane(c, 540, 980, 2.2, paper='#f3ece0', glow=0.35)
        _limb(c, (1300, 2000), (1000, 1500), (700, 1150), 200, 170, CHARS['son42']['coat'], CHARS['son42']['coat_sh'], 5)
        _hand(c, 650, 1110, 2.6, 140, CHARS['son42']['skin'], CHARS['son42']['skin_sh'], 6, grip=True)
    snow_all(c, T, near=True)


def b18_approach(c, t, T):
    cam = Cam(1.15, 80, -100, t=t)
    w = ease_io(seg(t, 0, 1.9))

    def chars_fn(cc):
        haru_seated(cc, t, T, head=dict(look=(1, -0.1), brow=lerp(0.5, 1.0, w), eye_open=1.0, mouth='open' if w > 0.5 else 'neutral', mouth_open=0.2))
        figure(cc, 'son42', lerp(1050, 560, w), 1830, 0.76, yaw=-0.5, t=t, seed=int(T * 15) + 6, walk=t * 1.1 if w < 1 else None,
               arms=dict(L=(-8, -6), R=(-6, -6)), head=dict(look=(-1, 0.2), brow=0.7, mouth='neutral'), rim=0.4, rim_c='#ffd890')
    station(c, t, T, cam, chars_fn, mode='night', snow=True, lamp=0.9, clock_hh=11, clock_mm=17)
    c.drawPaint(multiply(P('#6a7aaa', 0.45)))
    lamp_glow(c, 760 * 1.15 - 80, 600, 500, 0.6)


def b19_father(c, t, T):
    bokeh_bg(c, t, seed=12)
    lamp_glow(c, 150, 260, 700, 0.8)
    bust(c, 'son42', 560, 900, 2.6, yaw=-0.4, t=t, seed=int(t * 15),
         head=dict(look=(-0.7, 0.4), eye_open=blink(t, 6), brow=0.9, mouth='talk', mouth_open=talk(T, 1.2) * 0.5 if t > 1.9 else 0.0, tears=0.5 * seg(t, 2.5, 4.5),
                   tear_t=t, wet=0.6, light_dir=-1, rim=0.5, rim_c='#ffd38a'))
    snow_all(c, T)


def b20_embrace(c, t, T):
    bokeh_bg(c, t, seed=15)
    lamp_glow(c, 820, 380, 800, 0.85)
    g = ease_io(seg(t, 0.0, 1.0))
    sob = math.sin(on_twos(t) * 2 * math.pi / 1.4)
    bust(c, 'son42', lerp(760, 680, g), lerp(900, 880, g), 1.9, yaw=-0.55, t=t, seed=int(t * 15) + 2,
         head=dict(look=(-0.8, 0.3), eye_open=lerp(1, 0.0, seg(t, 0.6, 1.1)), brow=0.9, mouth='cry', mouth_open=0.15, tears=0.8, tear_t=t, tilt=-0.15 * g), breathe=1.8)
    bust(c, 'haru', lerp(330, 420, g), lerp(960, 980, g) + 6 * sob, 1.8, yaw=0.5, t=t, seed=int(t * 15),
         head=dict(look=(0.6, 0.3), eye_open=lerp(0.8, 0.0, seg(t, 0.3, 0.9)), brow=1.0, mouth='cry', mouth_open=0.25 + 0.2 * abs(sob),
                   tears=1.0, tear_t=t, wet=1.0, tilt=0.2 * g, light_dir=1, rim=0.55), breathe=3.0)
    if g > 0.05:
        ax = lerp(560, 860, g)
        _limb(c, (380, 1500), (lerp(520, 640, g), 1560), (ax, lerp(1400, 1250, g)), 150, 130, CHARS['haru']['coat'], CHARS['haru']['coat_sh'], 9)
        _hand(c, ax, lerp(1400, 1250, g), -1.9, 110, CHARS['haru']['skin'], CHARS['haru']['skin_sh'], 10, open_=0.2)
    snow_all(c, T, near=True)


def b21_next_day(c, t, T):
    cam = Cam(1.0, 0, 0, t=t)
    w = ease_out(seg(t, 0, 2.9))

    def chars_fn(cc):
        figure(cc, 'maryam', lerp(1100, 560, w), 1780, 0.68, yaw=-0.5, t=t, seed=int(T * 15) + 3, walk=t * 1.2 if w < 0.98 else None,
               arms=dict(L=(-8, 6), R=(8, -6)), head=dict(look=(-1, 0.1), brow=0.2, mouth='smile'))
    station(c, t, T, cam, chars_fn, mode='day', snow=False, clock_hh=4, clock_mm=30)
    snow_layer(c, T, 60, (2, 4), 40, 15, 3, 0.8)


def b22_empty(c, t, T):
    cam = Cam(1.25 + 0.03 * t, 120, -150, t=t)
    station(c, t, T, cam, None, mode='day', clock_hh=4, clock_mm=33)
    snow_layer(c, T, 60, (2, 4), 40, 15, 3, 0.8)


def b23_two_cranes(c, t, T):
    c.drawPaint(lin((0, 0), (0, H), ['#cfdcee', '#eef2f8']))
    for k in range(3):
        c.drawRoundRect(skia.Rect(-50, 1150 + k * 80, W + 50, 1215 + k * 80), 10, 10, P('#6a4a36' if k % 2 == 0 else '#5a3e2c'))
    c.drawPath(smooth_path([(-60, 1150), (300, 1132), (700, 1138), (W + 60, 1150), (W + 60, 1165), (-60, 1165)]), P('#eef2fb'))
    z = 1.0 + 0.05 * t
    c.save()
    c.translate(W / 2, 1100)
    c.scale(z, z)
    c.translate(-W / 2, -1100)
    crane(c, 380, 1110, 1.5, paper='#f3ece0', glow=0.2)
    crane(c, 720, 1110, 1.5, paper='#f6f0e2', flip=True, glow=0.2)
    c.restore()
    light_shafts(c, 900, -100, math.pi * 0.62, 3, 2000, 200, '#fff4d8', 0.15, T)
    snow_layer(c, T, 50, (2, 5), 40, 15, 4, 0.8)


def b24_home(c, t, T):
    # Haru's home at night: warm window, father and son at tea; pull back into the snow
    p = ease_io(seg(t, 0.8, 7.0))
    c.drawPaint(lin((0, 0), (0, H), ['#0b1430', '#2a3a66']))
    z = lerp(2.4, 1.0, p)
    c.save()
    c.translate(540, 900)
    c.scale(z, z)
    c.translate(-540, -900)
    # house facade
    c.drawRect(skia.Rect(80, 500, 1000, 1500), P('#3a2a26'))
    c.drawPath(poly([(40, 520), (1040, 520), (900, 360), (180, 360)]), P('#1c1a22'))
    c.drawPath(smooth_path([(30, 520), (540, 330), (1050, 520), (900, 380), (180, 380)]), P('#e3e8f5'))
    win = skia.Rect(280, 640, 800, 1160)
    c.save()
    c.clipRect(win)
    c.drawRect(win, lin((0, 640), (0, 1160), ['#ffd99a', '#ffb862']))
    figure(c, 'haru', 400, 1500, 0.55, yaw=0.5, t=t, seed=int(T * 15), sit=True, legs_hidden=True, arms=dict(L=(22, 30), R=(26, 28)),
           head=dict(look=(1, 0), mouth='smile', happy=ease_io(seg(t, 1, 2)), eye_open=blink(t, 3)))
    figure(c, 'son42', 680, 1500, 0.55, yaw=-0.5, t=t, seed=int(T * 15) + 1, sit=True, legs_hidden=True, arms=dict(L=(-22, -30), R=(-26, -28)),
           head=dict(look=(-1, 0), mouth='smile', eye_open=blink(t, 5)))
    teacup(c, 500, 1120, 0.6, steam_t=T)
    teacup(c, 580, 1120, 0.6, steam_t=T + 1)
    c.drawRect(skia.Rect(260, 1080, 820, 1170), P('#5a3a26'))
    c.restore()
    for k in range(-1, 8):
        c.drawLine(280 + k * 65, 640, 280 + k * 65, 1160, P('#2a1a12', 0.9, stroke=4))
    c.drawRect(win, P('#2a1a12', 1, stroke=16))
    c.drawRect(skia.Rect(win.left() - 80, win.top() - 60, win.right() + 80, win.bottom() + 300), add_blend(P('#ffb862', 0.25, blur=60)))
    c.drawRect(skia.Rect(-200, 1500, W + 200, H + 400), lin((0, 1500), (0, H), ['#8a9cc6', '#d7e1f4']))
    c.drawOval(skia.Rect(200, 1520, 880, 1700), add_blend(P('#ffb862', 0.25, blur=40)))
    c.restore()
    snow_all(c, T, near=True)
    c.drawPaint(P('#000000', ease_io(seg(t, 6.3, 7.6))))


SHOTS = [
    ('1982 - an old station in Japan', 0.00, 5.32, b01_establish, GR_SUN, 0.0),
    ('An old man named Haru', 5.32, 7.86, b02_haru_walks, GR_SUN, 0.3),
    ('Every day before sunset, the same place', 7.86, 12.68, b03_sits, GR_SUN, 0.0),
    ('A small paper crane beside him', 12.68, 15.44, b04_crane, GR_SUN, 0.0),
    ('Waiting for the last train', 15.44, 18.22, b05_waits, GR_SUN, 0.0),
    ('Nobody knew whom he waited for', 18.22, 21.64, b06_nobody_knew, GR_SUN, 0.0),
    ('Maryam approaches', 21.64, 26.88, b07_maryam_comes, GR_SUN, 0.0),
    ('"Grandpa, why do you come every day?"', 26.88, 30.20, b08_why, GR_SUN, 0.0),
    ('"I am waiting for my son"', 30.20, 32.86, b09_my_son, GR_SUN, 0.0),
    ('Twenty years ago he left (memory)', 32.86, 38.30, b10_twenty_years, GR_MEM, 0.0),
    ('Maryam takes the crane', 38.30, 41.00, b11_takes_crane, GR_SUN, 0.3),
    ('Inside: an old address', 41.00, 44.44, b12_address, GR_SUN, 0.0),
    ('She writes a letter', 44.44, 46.02, b13_writes, GR_HOME, 0.3),
    ('"Your father waits for you every day..."', 46.02, 51.18, b14_letter, GR_HOME, 0.0),
    ('Weeks pass, no reply', 51.18, 54.44, b15_weeks, GR_MEM, 0.3),
    ('A cold night: the last train', 54.44, 57.58, b16_train_arrives, GR_WARMNIGHT, 0.3),
    ('A man steps down, a paper crane in hand', 57.58, 61.24, b17_man_steps, GR_WARMNIGHT, 0.0),
    ('He comes to the old man', 61.24, 63.36, b18_approach, GR_NIGHT, 0.0),
    ('"Father, I thought you didn\'t want to see me"', 63.36, 66.62, b19_father, GR_WARMNIGHT, 0.0),
    ('Haru embraces him and weeps', 66.62, 70.44, b20_embrace, GR_WARMNIGHT, 0.0),
    ('Next day, Maryam comes', 70.44, 73.42, b21_next_day, GR_DAY, 0.5),
    ('For the first time, the bench is empty', 73.42, 76.34, b22_empty, GR_DAY, 0.0),
    ('Two paper cranes, side by side', 76.34, 81.62, b23_two_cranes, GR_DAY, 0.3),
    ('His son finally came home', 81.62, 91.00, b24_home, GR_WARMNIGHT, 0.6),
]
DURATION = 91.0

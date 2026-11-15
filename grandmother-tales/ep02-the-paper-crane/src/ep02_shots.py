"""Episode 02 — The Paper Crane (الطير الورقي): shot timeline.

Uses the shared character/set library of the series (../../ep03-harus-last-journey/src),
so Haru, Maryam, her father, the son, the cranes, the station and the clock are
the exact same models as in Episode 03.
Times are locked to the narration transcript (timing/transcript.json).
"""
import os, sys, math, random
HERE = os.path.dirname(os.path.abspath(__file__))
LIB = os.path.join(HERE, '..', '..', 'ep03-harus-last-journey', 'src')
sys.path.insert(0, os.path.abspath(LIB))
import numpy as np
import skia
from core import *
from chars import *
from chars import _limb, _hand, _clip_path
from env import *
import shots as ep3          # shared helpers (talk, blink, snow, station, grades)
from shots import blink, snow_all, cached, bokeh_bg, station_plates, station_wide, GR_NIGHT, GR_WARMNIGHT, GR_MEM, GR_FLASH

ENV = None
YELLOW = '#e3cf96'   # the crane, yellowed by twenty years


def talk(T, gain=1.0):
    ep3.ENV = ENV
    return ep3.talk(T, gain)


GR_DUSK = dict(tint=(0.98, 0.97, 1.06), sat=0.92, contrast=1.04, grain=0.06, vig=0.9, bloom=0.55)
GR_HOME = dict(tint=(1.05, 0.99, 0.92), sat=0.95, contrast=1.03, grain=0.06, vig=0.95, bloom=0.6)

CHARS['haru62'] = dict(CHARS['haru'], hair='#7d746c', hair_sh='#57504a', brow='#6a625c', mustache='#8a827a')


# ------------------------------------------------------------------ sets
def lane_sky(c):
    sky(c, '#1f2a55', '#d99a86', '#5b5a8a')
    brush_blobs(c, -MARGIN, -MARGIN, W + MARGIN, 900, ['#6a6a9a', '#8a7a9a', '#3a4472'], 26, 80, 240, 3, 0.25, 40)


def machiya_row(c, x_off, y_base, scale=1.0, seed=0, lit=0.8, dark='#2a2230'):
    """Row of old Kyoto town houses (wooden lattice fronts, tiled roofs, snow, lanterns)."""
    r = random.Random(seed)
    w = 330 * scale
    start = int(math.floor(-x_off / w)) - 1
    for k in range(start, start + int(W / w) + 3):
        rr = random.Random(seed * 1000 + k)
        x = k * w + x_off
        h = rr.uniform(330, 420) * scale
        top = y_base - h
        c.drawRect(skia.Rect(x, top, x + w - 6 * scale, y_base), P(mix(dark, '#4a3a38', rr.uniform(0, 0.4))))
        # lattice front
        for j in range(int((w - 40 * scale) / (14 * scale))):
            xx = x + 20 * scale + j * 14 * scale
            c.drawLine(xx, top + 120 * scale, xx, y_base - 10 * scale, P('#1a1418', 0.8, stroke=2.2 * scale))
        # warm window behind the lattice
        if rr.random() < lit:
            c.drawRect(skia.Rect(x + 40 * scale, top + 140 * scale, x + w - 60 * scale, top + 240 * scale), add_blend(P('#ffb862', 0.35)))
        # roof
        c.drawPath(poly([(x - 20 * scale, top + 10 * scale), (x + w + 14 * scale, top + 10 * scale), (x + w - 10 * scale, top - 50 * scale), (x + 10 * scale, top - 50 * scale)]), P('#1c1a22'))
        c.drawPath(smooth_path([(x - 24 * scale, top + 4 * scale), (x + w * 0.5, top - 64 * scale), (x + w + 18 * scale, top + 4 * scale), (x + w, top - 46 * scale), (x, top - 46 * scale)]), P('#e3e8f5'))
        # hanging lantern
        if rr.random() < 0.6:
            lx = x + w * 0.5
            ly = top + 70 * scale
            c.drawOval(skia.Rect(lx - 16 * scale, ly - 22 * scale, lx + 16 * scale, ly + 22 * scale), P('#e8a050'))
            c.drawCircle(lx, ly, 120 * scale, add_blend(rad((lx, ly), 120 * scale, [('#ffb862', 0.4), ('#ffb862', 0)])))


def lane(c, t, T, scroll=0.0):
    lane_sky(c) if False else None
    c.drawPaint(lin((0, 0), (0, H), ['#1f2a55', '#5b5a8a', '#d99a86']))
    c.drawCircle(W * 0.5, 1050, 600, add_blend(rad((W * 0.5, 1050), 600, [('#ffc79a', 0.25), ('#ffc79a', 0)])))
    machiya_row(c, -scroll * 0.35, 1150, 0.7, seed=4, lit=0.7, dark='#3a3448')
    c.drawRect(skia.Rect(0, 1150, W, H), lin((0, 1150), (0, H), ['#9aa4c8', '#e3e9f6']))
    machiya_row(c, -scroll, 1420, 1.15, seed=9, lit=0.8)
    c.drawRect(skia.Rect(0, 1420, W, H), lin((0, 1420), (0, H), ['#b8c4e0', '#eef2fb']))
    for k in range(-1, 12):
        x = (k * 140 - scroll * 1.0) % (W + 280) - 140
        c.drawOval(skia.Rect(x, 1700, x + 70, 1718), P('#8a96bc', 0.35))  # footprints


def run_pose(t, speed=1.6):
    ph = t * speed
    s = math.sin(ph * 2 * math.pi)
    return ph, dict(L=(-45 * s, 70), R=(45 * s, 70), Lgrip=True, Rgrip=True), abs(math.sin(ph * 2 * math.pi)) * 30


def home_night(c, t, T):
    room = cached('room', lambda: paint_plate(maryam_room))
    plate(c, room, Cam(1.0))
    c.drawPaint(multiply(P('#5a5f86', 0.55)))
    # night window
    c.drawRect(skia.Rect(220, 260, 860, 900), lin((0, 260), (0, 900), ['#141c3a', '#3a4672']))
    snow_layer(c, T, 60, (1.5, 3.5), 60, 10, 31, 0.8, 0, area=(220, 260, 860, 900))
    c.drawRect(skia.Rect(220, 260, 860, 900), P('#3a2618', 1, stroke=24))
    c.drawLine(540, 260, 540, 900, P('#3a2618', 1, stroke=14))
    c.drawRect(skia.Rect(190, 900, 890, 940), P('#5a3a26'))
    lamp_glow(c, 160, 520, 700, 0.85, '#ffc070')


def chest(c, x, y, s=1.0, lid=0.0):
    """Old wooden chest; lid 0 closed .. 1 open."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    c.drawRect(skia.Rect(-300, -200, 300, 120), P('#5a3a24'))
    c.drawRect(skia.Rect(-300, -200, 300, 120), lin((0, -200), (0, 120), [('#7a5236', 1), ('#3a2416', 1)]))
    for k in range(5):
        c.drawLine(-300, -150 + k * 55, 300, -150 + k * 55, P('#2a180e', 0.5, stroke=2))
    for bx in (-270, 270):
        c.drawRect(skia.Rect(bx - 14, -200, bx + 14, 120), P('#8a6a3a'))
    c.drawRect(skia.Rect(-40, -200, 40, -140), P('#b08a40'))
    c.drawRect(skia.Rect(-300, -200, 300, 120), P(INK, 0.9, stroke=4))
    # lid
    hgt = 120 * (1 - lid) - 260 * lid
    c.drawPath(poly([(-310, -200), (310, -200), (300, -200 - 120 * (1 - lid) - 10 + 0 * lid) if lid < 0.5 else (300, -200 - 300 * lid), (-300, -200 - 300 * lid) if lid >= 0.5 else (-300, -200 - 120 * (1 - lid) - 10)]),
               P('#6a4428'))
    c.restore()


def contents(c, cx, cy, s=1.0, reveal=1.0, crane_y=0.0, seed=3):
    """Top-down view of the box: photos, letters, a toy, and the crane underneath."""
    r = random.Random(seed)
    c.save()
    c.translate(cx, cy)
    c.scale(s, s)
    c.drawRect(skia.Rect(-480, -640, 480, 640), P('#3a2414'))
    c.drawRect(skia.Rect(-480, -640, 480, 640), P(INK, 1, stroke=30))
    # the yellowed crane lies under the photos
    crane(c, 40, 120 + crane_y, 1.5, rot=-0.2, paper=YELLOW, seed=1)
    items = []
    for i in range(14):
        items.append((r.uniform(-380, 380), r.uniform(-520, 520), r.uniform(-0.5, 0.5), r.choice(['photo', 'photo', 'letter', 'photo'])))
    for i, (x, y, rot, kind) in enumerate(items):
        # items covering the crane slide aside when revealed
        if abs(x - 40) < 260 and abs(y - 120) < 220:
            x += (1 - reveal) * 0 + reveal * (300 if x > 40 else -300)
        c.save()
        c.translate(x, y)
        c.rotate(math.degrees(rot))
        if kind == 'photo':
            c.drawRect(skia.Rect(-110, -140, 110, 140), P('#f0e8d8'))
            c.drawRect(skia.Rect(-95, -125, 95, 100), P(r.choice(['#8a857c', '#9a9286', '#6f6a62'])))
            if i % 3 == 0:
                bust(c, 'boy', 0, -30, 0.38, yaw=0.1, head=dict(mouth='smile', blush=0))
            elif i % 3 == 1:
                c.drawRect(skia.Rect(-95, 20, 95, 100), P('#5a5650'))
                c.drawCircle(-30, -40, 20, P('#4a4640'))
                c.drawCircle(30, -50, 26, P('#4a4640'))
            c.drawRect(skia.Rect(-95, -125, 95, 100), P('#c9a870', 0.25))
            c.drawRect(skia.Rect(-110, -140, 110, 140), P(INK, 0.6, stroke=2))
        else:
            c.drawRect(skia.Rect(-150, -90, 150, 90), P('#e8dcc2'))
            c.drawPath(poly([(-150, -90), (0, 10), (150, -90)], closed=False), P('#a89a7a', 1, stroke=3))
            c.drawRect(skia.Rect(90, -70, 130, -30), P('#3a6a8a'))
            c.drawRect(skia.Rect(-150, -90, 150, 90), P(INK, 0.6, stroke=2))
        c.restore()
    # toy wooden car
    c.drawRoundRect(skia.Rect(-420, 420, -240, 500), 20, 20, P('#a83a2a'))
    c.drawCircle(-390, 510, 22, P('#2a2420'))
    c.drawCircle(-270, 510, 22, P('#2a2420'))
    c.restore()


def letter_paper(c, x, y, s=1.0, write=1.0, unfold=1.0):
    """The unfolded crane: square sheet, fold creases, the red sun, vertical handwriting."""
    c.save()
    c.translate(x, y)
    c.scale(s * unfold + 0.001, s)
    c.drawRect(skia.Rect(-360, -360, 360, 360), P(YELLOW))
    c.drawRect(skia.Rect(-360, -360, 360, 360), rad((0, 0), 520, [('#f2e4b4', 0.6), ('#b89a5a', 0.6)]))
    for a, b in (((-360, -360), (360, 360)), ((360, -360), (-360, 360)), ((0, -360), (0, 360)), ((-360, 0), (360, 0))):
        c.drawLine(*a, *b, P('#9a8050', 0.35, stroke=2))
    c.drawCircle(220, -220, 46, P('#c8202a', 0.92))
    # vertical brush handwriting, right to left, appears with write
    r = random.Random(7)
    cols = 7
    for k in range(cols):
        cx = 150 - k * 70
        n = r.randint(5, 9)
        for j in range(n):
            if (k * 10 + j) / (cols * 10) > write:
                continue
            cy = -250 + j * 62
            stroke_taper(c, [(cx - r.uniform(5, 18), cy), (cx + r.uniform(5, 18), cy + r.uniform(-6, 6))], 5, 2, '#2a1c14', 0.85)
            stroke_taper(c, [(cx + r.uniform(-8, 8), cy - 18), (cx + r.uniform(-8, 8), cy + 22)], 4, 2, '#2a1c14', 0.85)
            if r.random() < 0.5:
                stroke_taper(c, [(cx - 14, cy + 14), (cx + 10, cy + 26)], 3, 1.5, '#2a1c14', 0.8)
    c.drawRect(skia.Rect(-360, -360, 360, 360), P(INK, 0.7, stroke=3))
    c.restore()


# ------------------------------------------------------------------ shots
def a01_run(c, t, T):
    ph, arms, bob = run_pose(t)
    lane(c, t, T, scroll=t * 700)
    figure(c, 'maryam', 470, 1800 - bob, 0.95, yaw=0.55, t=t, seed=int(t * 15), walk=ph, lean=0.18, arms=arms,
           head=dict(look=(1, 0), brow=0.5, mouth='open', mouth_open=0.3, eye_open=1.0), wind=1.0)
    ph = (t * 0.6) % 1
    c.drawCircle(700, 1080 - ph * 40, 30 + ph * 50, P('#eef2fb', 0.25 * (1 - ph), blur=20))
    snow_all(c, T, near=True)


def a02_lid(c, t, T):
    home_night(c, t, T)
    lid = ease_io(seg(t, 0.15, 1.3))
    # Maryam kneeling at the chest, seen from behind-side; light spills out as it opens
    chest(c, 560, 1600, 1.2, lid)
    c.drawRect(skia.Rect(200, 1300, 920, 1370), add_blend(P('#ffd7a0', 0.4 * lid, blur=30)))
    figure(c, 'maryam', 250, 2050, 0.95, yaw=0.6, t=t, seed=int(t * 15), sit=True, legs_hidden=True, lean=0.15,
           arms=dict(L=(90 + 30 * lid, 40), R=(95 + 40 * lid, 30)), head=dict(look=(1, 0.5), brow=0.3, mouth='neutral'))
    dust_motes(c, T, 300, 1100, 900, 1500, 30, 3, '#ffe2b0')


def a03_contents(c, t, T):
    c.drawPaint(P('#1a1210'))
    p = ease_io(seg(t, 0, 5.3))
    contents(c, 540 + 60 * math.sin(p * 1.2), 960 - 200 * p + 100, 1.15 + 0.1 * p, reveal=0.0)
    lamp_glow(c, 150, 200, 900, 0.6, '#ffc070')
    dust_motes(c, T, 0, 0, W, H, 40, 4, '#ffe2b0')


def a04_find(c, t, T):
    c.drawPaint(P('#1a1210'))
    rv = ease_io(seg(t, 0.4, 2.2))
    contents(c, 520, 900, 1.35, reveal=rv)
    # Maryam's hand moving the photos aside
    hx = lerp(560, 900, rv)
    _limb(c, (1300, 2100), (1100, 1600), (hx + 40, 1100), 150, 120, CHARS['maryam']['coat'], CHARS['maryam']['coat_sh'], 2)
    _hand(c, hx, 1060, 2.4, 95, CHARS['maryam']['skin'], CHARS['maryam']['skin_sh'], 3, open_=0.8)
    c.drawCircle(560, 1060, 500, add_blend(rad((560, 1060), 500, [('#ffd890', 0.25 * rv), ('#ffd890', 0)])))
    lamp_glow(c, 150, 200, 900, 0.6, '#ffc070')


def a05_yellow(c, t, T):
    c.drawPaint(lin((0, 0), (0, H), ['#2a1c14', '#120c0a']))
    lamp_glow(c, 200, 300, 900, 0.7, '#ffc070')
    lift = ease_io(seg(t, 0, 2.0))
    crane(c, 540, lerp(1200, 1000, lift), 2.8, rot=lerp(-0.2, 0.0, lift), paper=YELLOW, glow=0.15 + 0.2 * lift, flap=0.0)
    for side in (-1, 1):
        _hand(c, 540 + side * 260, lerp(1300, 1100, lift), side * 2.0, 120, CHARS['maryam']['skin'], CHARS['maryam']['skin_sh'], 5 + side, grip=True)
    dust_motes(c, T, 0, 300, W, 1600, 40, 5, '#ffe2b0')


def a06_sun(c, t, T):
    c.drawPaint(lin((0, 0), (0, H), ['#2a1c14', '#120c0a']))
    z = 1.0 + 0.06 * t
    c.save()
    c.translate(W / 2, H / 2)
    c.scale(z, z)
    c.translate(-W / 2, -H / 2)
    crane(c, 560, 1250, 7.0, rot=-0.12, paper=YELLOW)
    c.restore()
    c.drawCircle(W / 2, H / 2 - 40, 520, add_blend(rad((W / 2, H / 2 - 40), 520, [('#ffb090', 0.14 * seg(t, 0.5, 2.5)), ('#ffb090', 0)])))
    dust_motes(c, T, 0, 0, W, H, 30, 6, '#ffe2b0')


def a07_run_back(c, t, T):
    ph, arms, bob = run_pose(t, 1.8)
    lane(c, t, T, scroll=-t * 780)
    arms = dict(L=(-45 * math.sin(ph * 2 * math.pi), 70), R=(60, 100), Lgrip=True, Rgrip=True)
    figure(c, 'maryam', 600, 1800 - bob, 0.95, yaw=0.55, t=t, seed=int(t * 15), walk=ph, lean=0.2, arms=arms, flip=True,
           head=dict(look=(1, 0), brow=0.4, mouth='open', mouth_open=0.3), wind=1.0)
    crane(c, 600 - 150, 1180 - bob, 0.3, paper=YELLOW, flip=True)
    snow_all(c, T, near=True, dens=1.2)
    c.drawPaint(P('#0b1430', 0.25 * seg(t, 1.5, 3.0)))


def a08_offer(c, t, T):
    cam = Cam(1.25, -80, -150, t=t)
    off = ease_io(seg(t, 0.2, 1.2))

    def chars_fn(cc):
        bs = 1.15
        seat_y = 1720 - 170 * bs
        figure(cc, 'haru', 200, seat_y + 600 * 0.72, 0.72, yaw=0.45, t=t, seed=int(T * 15), sit=True,
               arms=dict(L=(18, 32), R=(22, 30)), head=dict(look=(1, 0.2), eye_open=blink(t, 2), brow=0.7))
        figure(cc, 'maryam', 520, 1790, 0.7, yaw=-0.5, t=t, seed=int(T * 15) + 3,
               arms=dict(L=(-8, 6), R=(-60 - 30 * off, -20)), head=dict(look=(-1, -0.2), brow=0.2, mouth='smile'))
        crane(cc, 520 - 230 - 60 * off, 1790 - 600 * 0.7 + 40 - 40 * off, 0.25, paper=YELLOW, flip=True)

    station_wide(c, t, T, cam, chars_fn)


def a09_haru_face(c, t, T):
    bokeh_bg(c, t, seed=8)
    lamp_glow(c, 900, 260, 700, 0.75)
    ch = ease_out(seg(t, 0.6, 1.4))
    bust(c, 'haru', 520, 900, 2.7, yaw=0.3, t=t, seed=int(t * 15),
         head=dict(look=(0.5, 0.55), eye_open=lerp(0.8, 1.05, ch) * (1 if t > 0.6 else blink(t, 3)), brow=lerp(0.4, 1.0, ch), mouth='open' if ch > 0.5 else 'neutral',
                   mouth_open=0.25 * ch, light_dir=1, rim=0.45, rim_c='#ffd38a', tears=0.4 * seg(t, 2.0, 3.5), tear_t=t))
    snow_all(c, T)


def a10_my_son(c, t, T):
    bokeh_bg(c, t, seed=8)
    lamp_glow(c, 900, 260, 700, 0.75)
    if t < 2.5:
        bust(c, 'haru', 520, 900, 2.7, yaw=0.3, t=t, seed=int(t * 15),
             head=dict(look=(0.5, 0.6), eye_open=blink(t, 4), brow=1.0, mouth='talk', mouth_open=talk(T, 1.2) * 0.55, tears=0.7, tear_t=t, wet=0.8,
                       light_dir=1, rim=0.45, rim_c='#ffd38a'))
    else:
        # trembling finger touches the red sun
        c.drawPaint(lin((0, 0), (0, H), ['#1d2a4a', '#0b1430']))
        crane(c, 520, 1150, 3.2, paper=YELLOW, glow=0.25)
        tr = math.sin(t * 40) * 4
        _limb(c, (1300, 2000), (1000, 1500), (720 + tr, 1080), 200, 170, CHARS['haru']['coat'], CHARS['haru']['coat_sh'], 4)
        _hand(c, 690 + tr, 1050, 2.2, 150, CHARS['haru']['skin'], CHARS['haru']['skin_sh'], 5, open_=0.4)
    snow_all(c, T, dens=0.7)


def a11_unfold(c, t, T):
    c.drawPaint(lin((0, 0), (0, H), ['#1d2a4a', '#0b1430']))
    lamp_glow(c, 900, 200, 800, 0.6)
    u = ease_io(seg(t, 0.5, 3.4))
    if u < 0.55:
        crane(c, 540, 1000, 3.0 * (1 - u * 0.6), rot=u * 1.2, paper=YELLOW, flap=-u * 2)
    if u > 0.35:
        with Layer(c, seg(u, 0.35, 0.8)):
            letter_paper(c, 540, 1000, 1.05, write=0.0, unfold=lerp(0.2, 1.0, seg(u, 0.35, 1.0)))
    for side in (-1, 1):
        hx = 540 + side * lerp(260, 400, u)
        _limb(c, (540 + side * 700, 2100), (540 + side * 560, 1600), (hx, 1220), 190, 160, CHARS['haru']['coat'], CHARS['haru']['coat_sh'], 20 + side)
        _hand(c, hx, 1200, side * 2.6, 140, CHARS['haru']['skin'], CHARS['haru']['skin_sh'], 22 + side, grip=True)
    snow_all(c, T, near=False, dens=0.6)


def a12_letter(c, t, T):
    c.drawPaint(lin((0, 0), (0, H), ['#1d2a4a', '#0b1430']))
    lamp_glow(c, 900, 200, 800, 0.6)
    z = 1.0 + 0.05 * t
    c.save()
    c.translate(540, 960)
    c.scale(z, z)
    c.translate(-540, -960)
    letter_paper(c, 540, 980, 1.25, write=ease_io(seg(t, 0.2, 3.8)), unfold=1.0)
    c.restore()
    snow_all(c, T, near=True, dens=0.5)


def a13_memory(c, t, T):
    """'I'll bring you the tea you love, and we'll sit and talk like before' — warm sepia memory."""
    tatami_room(c, night=False)
    lamp_glow(c, 540, 300, 900, 0.5, '#ffd9a0')
    low_table(c, 540, 1500, 1.25)
    figure(c, 'haru62', 230, 1950, 0.85, yaw=0.5, t=t, seed=int(T * 15), sit=True, legs_hidden=True,
           arms=dict(L=(22, 30), R=(26, 28)), head=dict(look=(0.9, 0.1), mouth='smile', eye_open=blink(t, 4), happy=ease_io(seg(t, 2.5, 3.2))))
    figure(c, 'son', 860, 1950, 0.85, yaw=-0.5, t=t, seed=int(T * 15) + 1, sit=True, legs_hidden=True,
           arms=dict(L=(-22, -30), R=(-26, -28)), head=dict(look=(-0.9, 0.1), mouth='talk' if 0.4 < t < 4.6 else 'smile',
                                                       mouth_open=talk(T, 1.0) * 0.5, eye_open=blink(t, 6)))
    teacup(c, 470, 1420, 1.1, steam_t=T)
    teacup(c, 640, 1420, 1.1, steam_t=T + 1)
    teapot(c, 560, 1360, 0.7)
    # soft dream vignette
    c.drawRect(skia.Rect(0, 0, W, H), rad((W / 2, H / 2), 1150, [('#f3e2c0', 0.0), ('#f3e2c0', 0.0), ('#f3e2c0', 0.85)], [0, 0.6, 1]))
    c.drawPaint(P('#ffffff', 0.7 * (1 - seg(t, 0, 0.5)) + 0.7 * seg(t, 4.5, 5.0)))


def a14_press(c, t, T):
    bokeh_bg(c, t, seed=9)
    lamp_glow(c, 880, 300, 700, 0.75)
    pr = ease_io(seg(t, 1.6, 2.8))
    bust(c, 'haru', 520, 860 + 30 * pr, 2.6, yaw=0.25, t=t, seed=int(t * 15),
         head=dict(look=(0.2, 0.8), eye_open=lerp(0.6, 0.0, pr), brow=1.0, mouth='cry', mouth_open=0.2 + 0.2 * abs(math.sin(t * 3)), tears=1.0, tear_t=t,
                   wet=1.0, tilt=0.15 * pr, light_dir=1, rim=0.5), breathe=2.6)
    # the letter pressed against his chest
    lx, ly = lerp(560, 600, pr), lerp(1650, 1380, pr)
    letter_paper(c, lx, ly, 0.42, write=1.0)
    for side in (-1, 1):
        _hand(c, lx + side * 150, ly + 40, side * 2.6, 130, CHARS['haru']['skin'], CHARS['haru']['skin_sh'], 30 + side, grip=False, open_=0.3)
    snow_all(c, T)


def a15_maryam_asks(c, t, T):
    bokeh_bg(c, t, seed=13, colors=('#ffcf7a', '#ffd8e0', '#9fb4e6'))
    lamp_glow(c, 920, 300, 700, 0.7)
    bust(c, 'maryam', 540, 920, 2.8, yaw=0.35, t=t, seed=int(t * 15),
         head=dict(look=(0.6, -0.5), eye_open=blink(t, 9), brow=0.8, mouth='talk', mouth_open=talk(T, 1.3) * 0.5 if t > 1.2 else 0.0, blush=0.35,
                   tilt=-0.06, light_dir=1, rim=0.5, rim_c='#ffd38a', wet=0.4))
    snow_all(c, T)


def a16_if_i_knew(c, t, T):
    bokeh_bg(c, t, seed=8)
    lamp_glow(c, 900, 260, 700, 0.75)
    wipe = seg(t, 0.4, 1.8)
    bust(c, 'haru', 520, 900, 2.7, yaw=0.35, t=t, seed=int(t * 15),
         head=dict(look=(0.6, 0.3), eye_open=0.3 if 0.5 < wipe < 0.95 else blink(t, 3) * 0.85, brow=1.0, mouth='talk' if t > 2.2 else 'sad',
                   mouth_open=talk(T, 1.2) * 0.5 if t > 2.2 else 0, tears=0.8 * (1 - wipe * 0.6), tear_t=t, wet=0.9, light_dir=1, rim=0.45, rim_c='#ffd38a'))
    if 0 < wipe < 1:
        hx = lerp(420, 640, wipe)
        _limb(c, (120, 2000), (180, 1450), (hx - 40, 1000), 150, 130, CHARS['haru']['coat'], CHARS['haru']['coat_sh'], 7)
        _hand(c, hx, 960, -2.2, 105, CHARS['haru']['skin'], CHARS['haru']['skin_sh'], 8, grip=True)
    snow_all(c, T)


def a17_thinking(c, t, T):
    bokeh_bg(c, t, seed=17, colors=('#9fb4e6', '#ffcf7a'))
    # memory of the 1962 train passing as a faint double exposure behind her
    with Layer(c, 0.35 * seg(t, 1.5, 3.0) * (1 - seg(t, 6.6, 8.0))):
        train_x = 1200 - (t * 500) % 3000
        c.save()
        c.translate(train_x, 820)
        c.scale(0.8, 0.8)
        carriage_side(c, 0, 0, 1420, 460, lit=0.7, t=T)
        c.restore()
        rain_layer(c, T, 80, (40, 80), 1600, 0.2, 3, 0.3, 2)
    bust(c, 'maryam', 470, 1050, 2.4, yaw=0.45, t=t, seed=int(t * 15),
         head=dict(look=(-0.6 + 0.4 * math.sin(t * 0.6), 0.6), eye_open=blink(t, 3), brow=0.7, mouth='neutral', blush=0.3, tilt=0.06), breathe=1.2)
    crane(c, 760, 1560, 0.9, paper=YELLOW, glow=0.2)
    _hand(c, 720, 1640, 2.2, 90, CHARS['maryam']['skin'], CHARS['maryam']['skin_sh'], 9, grip=True)
    snow_all(c, T, dens=0.8)


def a18_tells_father(c, t, T):
    home_night(c, t, T)
    low_table(c, 540, 1560, 1.25, '#5a3a26')
    figure(c, 'father', 820, 2050, 0.85, yaw=-0.45, t=t, seed=int(T * 15) + 2, sit=True, legs_hidden=True,
           arms=dict(L=(-30, -40), R=(-25, -35)), head=dict(look=(-0.8, 0.3), mouth='neutral', eye_open=blink(t, 3), brow=0.1))
    gest = math.sin(t * 4.0) * 25
    figure(c, 'maryam', 320, 1900, 0.85, yaw=0.5, t=t, seed=int(T * 15) + 4,
           arms=dict(L=(60 + gest, 40), R=(90 - gest, 30), Lopen=1, Ropen=1),
           head=dict(look=(1, -0.3), mouth='talk', mouth_open=0.3 + 0.3 * abs(math.sin(t * 9)), eye_open=blink(t, 6), brow=0.4))
    teacup(c, 700, 1490, 0.9, steam_t=T)


def a19_father_sees(c, t, T):
    home_night(c, t, T)
    c.drawPaint(P('#000000', 0.3))
    z = 1.0 + 0.06 * t
    c.save()
    c.translate(W / 2, H / 2)
    c.scale(z, z)
    c.translate(-W / 2, -H / 2)
    bust(c, 'father', 540, 900, 2.6, yaw=-0.25, t=t, seed=int(t * 15) if t < 0.8 else 3,
         head=dict(look=(-0.3, 0.75), eye_open=1.0 if t > 0.8 else blink(t, 2), brow=lerp(0.1, 0.9, seg(t, 0.5, 1.5)), mouth='neutral',
                   light_dir=-1, rim=0.4, rim_c='#ffc070'), breathe=0.4)
    c.restore()


def a20_where(c, t, T):
    home_night(c, t, T)
    c.drawPaint(P('#000000', 0.3))
    bust(c, 'father', 540, 900, 2.75, yaw=-0.3, t=t, seed=int(t * 15),
         head=dict(look=(-0.6, 0.6), eye_open=blink(t, 7), brow=0.9, mouth='talk', mouth_open=talk(T, 1.2) * 0.6 if t > 1.2 else 0, light_dir=-1, rim=0.4, rim_c='#ffc070'))


def a21_from_box(c, t, T):
    home_night(c, t, T)
    c.drawPaint(P('#000000', 0.2))
    bust(c, 'maryam', 540, 920, 2.7, yaw=0.3, t=t, seed=int(t * 15),
         head=dict(look=(0.5, -0.5), eye_open=blink(t, 4), brow=0.3, mouth='talk', mouth_open=talk(T, 1.3) * 0.5, blush=0.4, light_dir=-1, rim=0.35, rim_c='#ffc070'))
    crane(c, 820, 1580, 0.9, paper=YELLOW)


def a22_coat(c, t, T):
    # entrance hall: father pulls on his coat, the door opens onto the snow, he hurries out
    c.drawPaint(lin((0, 0), (0, H), ['#3a2a22', '#20160f']))
    door_open = ease_io(seg(t, 1.0, 1.8))
    c.drawRect(skia.Rect(560, 400, 980, 1800), lin((0, 400), (0, 1800), ['#141c3a', '#5a6a9a']))
    snow_layer(c, T, 80, (2, 5), 90, 20, 41, 0.9, 1, area=(560, 400, 980, 1800), wind=0.6)
    c.drawRect(skia.Rect(560, 400, 560 + 420 * (1 - door_open), 1800), P('#5a3a24'))
    c.drawRect(skia.Rect(540, 380, 1000, 1820), P('#2a180e', 1, stroke=30))
    lamp_glow(c, 200, 300, 800, 0.8, '#ffc070')
    go = ease_in(seg(t, 1.5, 2.64))
    figure(c, 'father', lerp(360, 820, go), 1880, lerp(1.0, 0.8, go), yaw=0.6, t=t, seed=int(t * 15), walk=t * 1.8 if go > 0 else None, lean=0.15 * go,
           arms=dict(L=(lerp(150, 20, seg(t, 0.0, 1.0)), lerp(-60, 20, seg(t, 0, 1))), R=(lerp(-120, 30, seg(t, 0, 1)), 30)),
           head=dict(look=(1, 0.0), brow=0.9, mouth='neutral'), wind=1.0)
    c.drawRect(skia.Rect(560, 400, 980, 1800), add_blend(P('#9fb4e6', 0.12 * door_open)))


def a23_arrive(c, t, T):
    cam = Cam(1.0, 0, 0, t=t)
    w = ease_io(seg(t, 0.0, 2.2))

    def chars_fn(cc):
        bs = 1.15
        seat_y = 1720 - 170 * bs
        figure(cc, 'haru', 200, seat_y + 600 * 0.72, 0.72, yaw=0.45, t=t, seed=int(T * 15), sit=True,
               arms=dict(L=(30, 40), R=(34, 40)), head=dict(look=(0.4, 0.6), eye_open=blink(t, 2), brow=0.8))
        figure(cc, 'maryam', 470, 1770, 0.68, yaw=0.5, t=t, seed=int(T * 15) + 3, arms=dict(L=(-8, 6), R=(8, -6)),
               head=dict(look=(1, -0.1), brow=0.3, mouth='smile'))
        figure(cc, 'father', lerp(1150, 700, w), 1860, 0.74, yaw=-0.5, t=t, seed=int(T * 15) + 6, walk=t * 1.5 if w < 1 else None,
               arms=dict(L=(-8, -6), R=(-6, -6)), head=dict(look=(-1, 0.2), brow=0.7), wind=0.6)

    station_wide(c, t, T, cam, chars_fn)


def a24_two_cranes(c, t, T):
    if t < 1.7:
        bokeh_bg(c, t, seed=12)
        lamp_glow(c, 150, 260, 700, 0.8)
        bust(c, 'father', 560, 900, 2.6, yaw=-0.4, t=t, seed=int(t * 15),
             head=dict(look=(-0.7, 0.2 + 0.4 * seg(t, 0.8, 1.6)), eye_open=blink(t, 8), brow=0.9, mouth='neutral', light_dir=-1, rim=0.5, rim_c='#ffd38a'))
    else:
        c.drawPaint(lin((0, 0), (0, H), ['#1d2a4a', '#0b1430']))
        lamp_glow(c, 900, 200, 800, 0.6)
        crane(c, 380, 1050, 1.6, paper=YELLOW, glow=0.2)
        crane(c, 720, 1060, 1.6, paper='#f3ece0', flip=True, glow=0.2)
        for side in (-1, 1):
            _hand(c, 540 + side * 360, 1180, side * 2.4, 150, CHARS['haru']['skin'], CHARS['haru']['skin_sh'], 50 + side, grip=False, open_=0.3)
    snow_all(c, T)


def a25_confess(c, t, T):
    bokeh_bg(c, t, seed=12)
    lamp_glow(c, 150, 260, 700, 0.8)
    flash = seg(t, 6.2, 6.5) * (1 - seg(t, 7.6, 8.0))
    z = 1.0 + 0.035 * t
    c.save()
    c.translate(W / 2, H / 2)
    c.scale(z, z)
    c.translate(-W / 2, -H / 2)
    bust(c, 'father', 560, 900, 2.6, yaw=-0.35, t=t, seed=int(t * 15),
         head=dict(look=(-0.7, 0.3), eye_open=blink(t, 8), brow=0.95, mouth='talk', mouth_open=talk(T, 1.3) * 0.55 if t > 1.0 else 0, tears=0.5 * seg(t, 3, 6), tear_t=t,
                   wet=0.6, light_dir=-1, rim=0.5, rim_c='#ffd38a'))
    c.restore()
    if flash > 0:
        # flash of memory: the boy at the rain-streaked carriage window, 1962
        with Layer(c, 0.75 * flash):
            c.drawPaint(lin((0, 0), (0, H), ['#1d2638', '#0d1220']))
            ep3.ext_rain_window(c, skia.Rect(140, 400, 940, 1300), T - 95, 0.3)
            bust(c, 'boy', 540, 1450, 1.6, yaw=0.3, t=t, seed=int(t * 15), head=dict(look=(0.8, -0.3), brow=0.5))
    snow_all(c, T)


def a26_haru_hope(c, t, T):
    bokeh_bg(c, t, seed=8)
    hope = ease_io(seg(t, 1.0, 5.0))
    lamp_glow(c, 900, 260, 700, 0.6 + 0.4 * hope)
    c.drawCircle(W / 2, 700, 900, add_blend(rad((W / 2, 700), 900, [('#ffd890', 0.25 * hope), ('#ffd890', 0)])))
    bust(c, 'haru', 520, 900, 2.7, yaw=0.3, t=t, seed=int(t * 15) if t > 0.6 else 1,
         head=dict(look=(0.8, 0.0), eye_open=1.05, brow=lerp(1.0, 0.5, hope), mouth='open', mouth_open=0.15, tears=0.6, tear_t=t, wet=0.8 + 0.2 * hope,
                   light_dir=1, rim=0.45 + 0.3 * hope, rim_c='#ffd38a'), breathe=0.5)
    snow_all(c, T)


def a27_truth(c, t, T):
    # pull back: the three on the platform, the clock, the empty tracks into the dark
    p = ease_io(seg(t, 0.0, 6.0))
    cam = Cam(lerp(1.35, 1.0, p), lerp(140, 0, p), lerp(-200, 0, p), t=t)

    def chars_fn(cc):
        bs = 1.15
        seat_y = 1720 - 170 * bs
        figure(cc, 'haru', 220 + 60 * p, lerp(seat_y + 600 * 0.72, 1780, ease_io(seg(t, 0, 1.0))), 0.72, yaw=0.45, t=t, seed=int(T * 15),
               sit=t < 0.5, arms=dict(L=(15, 15), R=(20, 15)), head=dict(look=(1, 0.0), brow=0.8))
        figure(cc, 'maryam', 470, 1770, 0.68, yaw=0.4, t=t, seed=int(T * 15) + 3, arms=dict(L=(-8, 6), R=(8, -6)), head=dict(look=(1, -0.2), brow=0.5))
        figure(cc, 'father', 700, 1860, 0.74, yaw=-0.45, t=t, seed=int(T * 15) + 6, arms=dict(L=(-8, -6), R=(-6, -6)), head=dict(look=(-1, 0.2), brow=0.9))

    station_wide(c, t, T, cam, chars_fn)
    c.drawPaint(P('#000000', ease_io(seg(t, 5.6, 7.3))))


SHOTS = [
    ('Run home through the snowy lane', 0.00, 1.95, a01_run, GR_DUSK, 0.0),
    ('Opening the old box', 1.95, 3.80, a02_lid, GR_HOME, 0.0),
    ('Photos, letters, childhood things', 3.80, 9.08, a03_contents, GR_HOME, 0.3),
    ('Among the photos: the crane', 9.08, 12.12, a04_find, GR_HOME, 0.0),
    ('Yellowed by the years', 12.12, 15.08, a05_yellow, GR_HOME, 0.0),
    ('The red sun is still there', 15.08, 18.64, a06_sun, GR_HOME, 0.3),
    ('She runs back to the station', 18.64, 21.66, a07_run_back, GR_DUSK, 0.0),
    ('Maryam shows Haru the crane', 21.66, 23.30, a08_offer, GR_NIGHT, 0.3),
    ("Haru's face changes", 23.30, 25.38, a09_haru_face, GR_NIGHT, 0.0),
    ('"My son painted this sun"', 25.38, 29.86, a10_my_son, GR_NIGHT, 0.0),
    ('He unfolds the crane', 29.86, 34.28, a11_unfold, GR_NIGHT, 0.0),
    ('The letter', 34.28, 38.18, a12_letter, GR_WARMNIGHT, 0.3),
    ('Memory: tea and talk like before', 38.18, 43.18, a13_memory, GR_MEM, 0.3),
    ('He presses it to his chest and weeps', 43.18, 48.14, a14_press, GR_NIGHT, 0.3),
    ('"Grandpa, why didn\'t he return?"', 48.14, 51.72, a15_maryam_asks, GR_NIGHT, 0.0),
    ('"If only I knew"', 51.72, 56.90, a16_if_i_knew, GR_NIGHT, 0.0),
    ('Maryam wonders', 56.90, 65.08, a17_thinking, GR_NIGHT, 0.4),
    ('She tells her father everything', 65.08, 68.76, a18_tells_father, GR_HOME, 0.4),
    ('Her father falls silent', 68.76, 71.72, a19_father_sees, GR_HOME, 0.0),
    ('"Where did you get this?"', 71.72, 74.70, a20_where, GR_HOME, 0.0),
    ('"From your box..."', 74.70, 79.94, a21_from_box, GR_HOME, 0.0),
    ('He takes his coat and hurries out', 79.94, 82.58, a22_coat, GR_HOME, 0.0),
    ('At the station he sees Haru', 82.58, 85.38, a23_arrive, GR_NIGHT, 0.3),
    ('His face, and the two cranes', 85.38, 88.88, a24_two_cranes, GR_NIGHT, 0.0),
    ('"Twenty years ago... I was on the same train"', 88.88, 98.82, a25_confess, GR_NIGHT, 0.0),
    ('Haru stands still: hope', 98.82, 105.40, a26_haru_hope, GR_WARMNIGHT, 0.0),
    ('The truth will be harder', 105.40, 113.00, a27_truth, GR_NIGHT, 0.4),
]
DURATION = 113.0

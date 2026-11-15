"""Episode 03 — Haru's Last Journey: shot-by-shot timeline.

Every shot = (name, start_sec, end_sec, draw_fn, grade_dict, crossfade_in_sec).
Times are locked to the narration transcript (timing/transcript.json).
draw_fn(c, t, T) : t = seconds since shot start, T = global seconds.
"""
import math, random
import numpy as np
import skia
from core import *
from chars import *
from chars import _limb, _hand, _clip_path
from env import *

# ------------------------------------------------------------------ helpers
ENV = None  # narration loudness per frame (set by render.py)


def talk(T, gain=1.0):
    """Mouth opening driven by narration loudness (lip-sync on twos)."""
    if ENV is None:
        return 0.0
    f = int(math.floor(T * 15) / 15 * FPS)
    f = max(0, min(len(ENV) - 1, f))
    return clamp(ENV[f] * gain)


def blink(t, seed=0, period=3.4):
    r = random.Random(seed)
    off = r.uniform(0, period)
    ph = ((t + off) % period)
    if ph < 0.06:
        return 0.35
    if ph < 0.16:
        return 0.0
    if ph < 0.22:
        return 0.5
    return 1.0


_cache = {}


def cached(key, fn):
    if key not in _cache:
        _cache[key] = fn()
    return _cache[key]


def snow_all(c, t, near=True, wind=0.15, dens=1.0):
    snow_layer(c, t, int(260 * dens), (1.0, 2.2), 45, 12, 1, 0.7, 0, wind=wind)
    snow_layer(c, t, int(120 * dens), (2.5, 4.5), 80, 20, 2, 0.85, 0.6, wind=wind)
    if near:
        snow_layer(c, t, int(18 * dens), (9, 16), 150, 40, 3, 0.55, 6, wind=wind)


GR_NIGHT = dict(tint=(0.93, 0.98, 1.08), sat=0.92, contrast=1.04, grain=0.06, vig=0.9, bloom=0.55)
GR_WARMNIGHT = dict(tint=(1.02, 0.98, 1.02), sat=0.95, contrast=1.04, grain=0.06, vig=0.9, bloom=0.75)
GR_FLASH = dict(tint=(0.98, 0.98, 1.0), sat=0.62, contrast=1.08, grain=0.10, vig=1.0, bloom=0.4)
GR_MEM = dict(tint=(1.05, 1.0, 0.9), sat=0.7, contrast=1.0, grain=0.08, vig=0.9, bloom=0.4)
GR_SPRING = dict(tint=(1.06, 1.0, 0.92), sat=1.02, contrast=1.02, grain=0.05, vig=0.75, bloom=0.7)


def station_plates():
    return (cached('st_far', lambda: paint_plate(station_far)),
            cached('st_mid', lambda: paint_plate(station_mid)))


def bokeh_bg(c, t, colors=('#ffcf7a', '#9fb4e6'), n=14, seed=0, base=('#101a36', '#2b3b66')):
    c.drawPaint(lin((0, 0), (0, H), list(base)))
    r = random.Random(seed)
    for i in range(n):
        x, y = r.uniform(0, W), r.uniform(0, H * 0.8)
        rr = r.uniform(40, 130)
        x += math.sin(t * 0.3 + i) * 10
        c.drawCircle(x, y, rr, add_blend(P(r.choice(colors), r.uniform(0.06, 0.18), blur=rr * 0.3)))


# ================================================================== SCENE 01
def s01_father_cu(c, t, T):
    bokeh_bg(c, t, seed=3)
    # warm lamp on the left
    lamp_glow(c, 120, 300, 700, 0.8)
    cam = Cam(1.0 + 0.04 * t, 0, 0, t=t)
    c.save()
    cam.apply(c)
    bust(c, 'father', 520, 860, 2.7, yaw=0.5, t=t, seed=int(t * 15),
         head=dict(look=(0.85, 0.1), eye_open=blink(t, 4) * 0.92, brow=0.7, mouth='talk', mouth_open=talk(T, 1.2) * 0.6,
                   light_dir=-1, rim=0.5, rim_c='#ffd38a'))
    c.restore()
    # breath vapour
    ph = (t * 0.6) % 1
    c.drawCircle(820 + ph * 120, 1080 - ph * 60, 40 + ph * 80, P('#e6eefc', 0.18 * (1 - ph), blur=30))
    snow_all(c, t)


def s01_eye(c, t, T):
    # push into the father's near eye; a moving train is reflected in the iris
    z = 1.0 + 9.0 * ease_in(seg(t, 0, 1.05))
    bokeh_bg(c, t, seed=3)
    c.save()
    c.translate(W / 2, H / 2)
    c.scale(z, z)
    c.translate(-W / 2, -H / 2)
    c.translate(-(1 - 1 / z) * 0, 0)
    # eye-centered close up: the near eye of draw_head at yaw .5 sits at (fx-sep-yaw*6, 6)= (-23,6)*s
    s = 4.6
    cx, cy = W / 2 + 23 * s, H / 2 - 6 * s
    bust(c, 'father', cx, cy, s, yaw=0.5, t=t, seed=1, head=dict(look=(0.85, 0.1), eye_open=0.95, brow=0.7, rim=0.4))
    c.restore()
    # reflection: train windows streaking across the iris (in screen space, grows with zoom)
    rr = 13 * 0.78 * 4.6 * z
    ix, iy = W / 2 + 0.85 * 17 * 0.45 * 4.6 * z, H / 2 + 4.6 * z * 0.5
    c.save()
    pth = skia.Path()
    pth.addCircle(ix, iy, rr)
    c.clipPath(pth, skia.ClipOp.kIntersect, True)
    for k in range(10):
        x = ix - rr * 2 + ((t * 2.4 * rr + k * rr * 0.45) % (rr * 4))
        c.drawRect(skia.Rect(x, iy - rr * 0.25, x + rr * 0.3, iy + rr * 0.05), add_blend(P('#ffd27a', 0.7)))
    c.restore()
    a = seg(t, 0.55, 1.05)
    c.drawPaint(P('#1a1a22', a * 0.6))


# ================================================================== SCENE 02 (1962)
def ext_rain_window(c, rect, t, flash=0.0, speed=1.0):
    c.save()
    c.clipRect(rect)
    c.drawRect(rect, lin((0, rect.top()), (0, rect.bottom()), ['#1d2638', '#0d1220']))
    # passing trees / poles
    for k in range(6):
        x = rect.left() + ((-(t * 900 * speed) + k * 260) % (rect.width() + 400)) - 200
        c.drawRect(skia.Rect(x, rect.top() + 120, x + 18, rect.bottom()), P('#070a12', 0.9))
        c.drawPath(poly([(x - 60, rect.top() + 200), (x + 9, rect.top() + 40), (x + 80, rect.top() + 200)]), P('#0a0e18', 0.9))
    if flash:
        c.drawRect(rect, add_blend(P('#cfe0ff', 0.6 * flash)))
    rain_layer(c, t, 70, (30, 70), 1500, 0.9, 5, 0.45, 2.0, '#9fb6d8', (rect.left(), rect.top(), rect.right(), rect.bottom()))
    # drops on the glass
    r = random.Random(4)
    for i in range(40):
        x = rect.left() + r.uniform(0, rect.width())
        y = rect.top() + (r.uniform(0, rect.height()) + t * r.uniform(30, 160)) % rect.height()
        c.drawCircle(x, y, r.uniform(2, 6), P('#c9dcf4', 0.5))
        c.drawLine(x, y - r.uniform(10, 50), x, y, P('#c9dcf4', 0.3, stroke=2))
    c.restore()
    c.drawRect(rect, P('#2a1e18', 1, stroke=22))
    c.drawLine(rect.left(), rect.top() + rect.height() * 0.45, rect.right(), rect.top() + rect.height() * 0.45, P('#2a1e18', 1, stroke=14))


def lightning_flash(T):
    """Global lightning schedule (sec): returns brightness 0..1."""
    v = 0.0
    for ts in (6.2, 8.4, 9.1, 10.7, 13.0, 16.4, 22.6, 33.2, 45.5, 49.6):
        d = T - ts
        if 0 <= d < 0.45:
            v = max(v, (1 - d / 0.45) * (1.0 if d > 0.08 or d < 0.03 else 0.4))
    return v


def f01_carriage(c, t, T):
    fl = lightning_flash(T)
    wins = carriage_interior(c)
    for w in wins:
        ext_rain_window(c, w, t, fl)
    rock = math.sin(t * 5.2) * 0.4 + math.sin(t * 9) * 0.2
    c.save()
    Cam(1.45 + 0.03 * t, 60, -330, t=t).apply(c)
    c.rotate(rock * 0.15)
    # passengers silhouettes in the back (other bench, nervous)
    for k, px in enumerate((150, 930)):
        bust(c, 'oldman62', px, 1120 + k * 20, 0.75, yaw=0.3 * (1 if k else -1), t=t, seed=k + 9,
             head=dict(look=(-0.5 if k else 0.6, -0.4), brow=0.9, eye_open=blink(t, k + 7)), breathe=1.5)
    seat(c, 540, 1520, 940, '#3f5a46', 560)
    # the boy (window side) and his father
    figure(c, 'oldman62', 700, 2050, 0.62, yaw=-0.35, t=t, seed=int(t * 15) + 3, sit=True,
           arms=dict(L=(-40, -60), R=(20, 30)), head=dict(look=(-0.4, -0.2), brow=0.6, eye_open=blink(t, 2)))
    look_x = 0.6 if t < 1.6 else -0.4
    figure(c, 'boy', 360, 1960, 0.66, yaw=0.4, t=t, seed=int(t * 15) + 5, sit=True,
           arms=dict(L=(30, 40), R=(30, 40)),
           head=dict(look=(look_x, -0.5), brow=0.4 + 0.4 * seg(t, 1.5, 3), eye_open=blink(t, 1), mouth='neutral'))
    c.restore()
    hanging_lamp(c, 540, 260, T, 1.0 - 0.6 * (random.Random(int(T * 15)).random() < 0.12), swing=1.0)
    if fl:
        c.drawPaint(add_blend(P('#bcd2ff', 0.35 * fl)))


def f02_bridge(c, t, T):
    fl = lightning_flash(T)
    far = cached('storm_sky', lambda: paint_plate(storm_sky))
    cam = Cam(1.06 - 0.03 * t, 0, -20 + 10 * t, t=t)
    plate(c, far, cam, 0.3)
    c.save()
    cam.apply(c, 0.6)
    if fl:
        lightning(c, t, 760, seed=int(T), a=fl)
    gorge(c)
    c.restore()
    c.save()
    cam.apply(c, 1.0)
    river(c, T, 1350, flood=1.0, speed=420)
    # bridge with the train crossing
    trestle_bridge(c, -100, 1300, 1000, 1400, 0.0)
    tx = -900 + t * 260
    for k in range(4):
        carriage_side(c, tx + k * 520, 975, 500, 170, lit=0.9, t=T, wet=1)
    steam_puffs(c, tx + 2180, 760, T, 0.6)
    c.restore()
    rain_layer(c, T, 260, (50, 110), 2200, 0.2, 1, 0.35, 2.2)
    if fl:
        c.drawPaint(add_blend(P('#c8d8ff', 0.55 * fl)))


def f03a_crack(c, t, T):
    sk = cached('storm_sky', lambda: paint_plate(storm_sky))
    cam = Cam(1.6, 0, 120, shake=18 * (1 - t), t=T)
    plate(c, sk, cam, 0.3)
    c.save()
    cam.apply(c)
    river(c, T, 1350, flood=1.0, speed=420)
    trestle_bridge(c, -100, 1300, 1000, 1400, ease_in(seg(t, 0.2, 0.95)) * 0.25)
    # timber splinters
    r = random.Random(3)
    for i in range(20):
        p = seg(t, 0.25, 0.95)
        x = 520 + r.uniform(-60, 60) + r.uniform(-300, 300) * p
        y = 980 + r.uniform(-30, 30) + (r.uniform(-200, 100) * p + 800 * p * p)
        c.drawRect(skia.Rect(x, y, x + r.uniform(10, 40), y + 6), P('#6a5a4a'))
    c.restore()
    rain_layer(c, T, 220, (50, 110), 2200, 0.2, 2, 0.35, 2.2)
    fl = lightning_flash(T)
    if fl:
        c.drawPaint(add_blend(P('#c8d8ff', 0.5 * fl)))


def f03b_tilt(c, t, T):
    tilt = 22 * ease_in(seg(t, 0, 1.0))
    c.save()
    Cam(1.35, 120, -280, shake=12, t=T).apply(c)
    c.translate(W / 2, H / 2)
    c.rotate(tilt)
    c.translate(-W / 2, -H / 2)
    flick = random.Random(int(T * 20)).random() < 0.45
    wins = carriage_interior(c, 'dark' if flick else 'normal')
    for w in wins:
        ext_rain_window(c, w, t, 0.0)
    seat(c, 540, 1520, 940, '#3f5a46', 560)
    # luggage falling from the rack
    for k, (sx, colr) in enumerate(((200, '#7a4b2c'), (620, '#4a5a6a'), (880, '#8a6a3a'))):
        p = seg(t, 0.1 + k * 0.12, 1.1)
        suitcase(c, sx + p * 160, 380 + 1100 * p * p, 1.1, p * 2.4 * (1 if k % 2 else -1), colr)
    figure(c, 'boy', 360, 1960, 0.66, yaw=0.4, t=t, seed=int(t * 15) + 5, sit=True, lean=-0.25,
           arms=dict(L=(150, 20), R=(110, 30)), head=dict(look=(0.2, -0.8), brow=1.0, eye_open=1.0, mouth='shout', mouth_open=0.8))
    c.restore()
    hanging_lamp(c, 540, 260, T * 3, 0.0 if flick else 1.0, swing=4.0)
    c.drawPaint(P('#000000', 0.35 if flick else 0.0))


def f03c_fall(c, t, T):
    sk = cached('storm_sky', lambda: paint_plate(storm_sky))
    cam = Cam(1.15, 0, 0, shake=14, t=T)
    plate(c, sk, cam, 0.3)
    c.save()
    cam.apply(c, 0.6)
    gorge(c)
    c.restore()
    c.save()
    cam.apply(c)
    river(c, T, 1350, flood=1.0, speed=420)
    trestle_bridge(c, -100, 1300, 1000, 1400, 1.0)
    p = ease_in(seg(t, 0.0, 0.7))
    c.save()
    c.translate(300, 950 + p * 520)
    c.rotate(-28 * p - 4)
    carriage_side(c, -260, 0, 560, 190, lit=0.7 * (1 - p * 0.5), t=T, wet=1)
    c.restore()
    if t > 0.62:
        splash(c, 330, 1400, seg(t, 0.62, 1.4), 1.3, seed=4)
    c.restore()
    rain_layer(c, T, 260, (50, 110), 2200, 0.2, 3, 0.35, 2.2)
    fl = lightning_flash(T)
    if fl:
        c.drawPaint(add_blend(P('#c8d8ff', 0.5 * fl)))


def flooded_interior(c, t, T, level, tilt=12, dark=0.5):
    c.save()
    c.translate(W / 2, H / 2)
    c.rotate(tilt)
    c.translate(-W / 2, -H / 2)
    wins = carriage_interior(c, 'dark')
    for w in wins:
        ext_rain_window(c, w, t, lightning_flash(T) * 0.5, 0.0)
    seat(c, 540, 1520, 940, '#2d4033', 560)
    c.restore()
    return wins


def f04_flood(c, t, T):
    flood = 1500 - 520 * ease_io(seg(t, 0, 4.0))
    flooded_interior(c, t, T, flood)
    flick = random.Random(int(T * 12)).random() < 0.3
    hanging_lamp(c, 540, 240, T * 2, 0.0 if flick else 0.85, swing=2.5)
    # window shatter + water jet
    p = seg(t, 0.2, 1.2)
    if p > 0:
        glass_shards(c, 300, 760, p, seed=5)
        jet = poly([(250, 700), (360, 700), (520, 1500), (180, 1500)])
        c.drawPath(jet, P('#9fc0e6', 0.35 * min(1, p * 3), blur=10))
    # floating luggage and boy
    for k, (sx, colr) in enumerate(((180, '#7a4b2c'), (820, '#4a5a6a'))):
        suitcase(c, sx + math.sin(t * 1.3 + k) * 30, flood - 20 + math.sin(t * 2 + k) * 8, 1.0, math.sin(t * 1.1 + k) * 0.3, colr)
    bust(c, 'boy', 560, flood - 110 + math.sin(t * 2.4) * 10, 1.1, yaw=0.2, t=t, seed=int(t * 15),
         head=dict(look=(math.sin(t * 3) * 0.8, -0.6), brow=1.0, mouth='shout', mouth_open=0.4 + 0.4 * abs(math.sin(t * 4)), wet=1.0, eye_open=1.0), wet=1.0)
    water_body(c, T, flood, 0.85)
    c.drawPaint(P('#04070f', 0.35 if flick else 0.15))
    rain_layer(c, T, 40, (20, 50), 1200, 0.5, 9, 0.25, 2)


def f05_boy_panic(c, t, T):
    lvl = 1180 - 40 * t
    c.drawPaint(lin((0, 0), (0, H), ['#0a1222', '#1d2c44']))
    hanging_lamp(c, 900, -60, T * 2, 0.6 + 0.3 * math.sin(T * 30) * (random.Random(int(T * 10)).random() < 0.3), swing=2)
    bust(c, 'boy', 540, 980 + math.sin(t * 2.6) * 18, 2.4, yaw=-0.15 + math.sin(t * 1.3) * 0.15, t=t, seed=int(t * 15),
         head=dict(look=(math.sin(t * 2.2) * 0.9, -0.4), brow=1.0, mouth='shout', mouth_open=0.3 + 0.5 * abs(math.sin(t * 3.4)),
                   wet=1.0, tears=0.6, tear_t=t), wet=1.0)
    water_body(c, T, lvl + math.sin(t * 2.6) * 18, 0.8, choppy=1.6)
    bubbles(c, T, 540, 1500, 18, 2)
    # splashes at the chin line
    for k in range(6):
        ph = (t * 1.7 + k / 6) % 1
        c.drawCircle(340 + k * 80, lvl - ph * 60, 8 * (1 - ph), P('#d6e8ff', 0.7 * (1 - ph)))


def f06_reach(c, t, T):
    # low angle: boy reaching up toward the bright window above the waterline
    c.drawPaint(lin((0, 0), (0, H), ['#2a3a58', '#0a1222']))
    # bright opening (window) at the top
    c.drawRect(skia.Rect(260, 60, 820, 420), P('#c9dcf4', 0.8))
    c.drawRect(skia.Rect(260, 60, 820, 420), P('#2a1e18', 1, stroke=24))
    light_shafts(c, 540, 200, math.pi / 2, 3, 1700, 160, '#cfe2ff', 0.18, T)
    rain_layer(c, T, 60, (30, 60), 1600, 0.2, 6, 0.4, 2, area=(260, 60, 820, 420))
    lvl = 900 + 30 * math.sin(t * 2.4)
    reach = ease_io(seg(t, 0, 1.6))
    figure(c, 'boy', 540, 2300 + 40 * math.sin(t * 2.2), 1.35, yaw=0.05, t=t, seed=int(t * 15),
           arms=dict(L=(-150 - 25 * reach, -10), R=(150 + 20 * reach, 10 + 10 * math.sin(t * 6)), Lopen=1, Ropen=1),
           head=dict(look=(0, -1), brow=1.0, mouth='shout', mouth_open=0.6, wet=1.0, tilt=-0.15), wet=1.0, legs_hidden=True)
    water_body(c, T, lvl, 0.7, colr='#1a3352', choppy=1.4)
    bubbles(c, T, 540, 1700, 24, 3, 220, 800)
    # water pushes him back down
    push = seg(t, 2.2, 3.7)
    c.drawPaint(P('#05101e', 0.25 * push))


def f07_hand(c, t, T):
    c.drawPaint(lin((0, 0), (0, H), ['#24344f', '#0b1426']))
    light_shafts(c, 620, -100, math.pi / 2 + 0.15, 3, 2000, 200, '#cfe2ff', 0.14, T)
    # boy's small forearm reaching up from the bottom
    ax = 520 + math.sin(t * 6) * 10
    _limb(c, (ax, 2000), (ax + 10, 1500), (ax + 20, 1150), 120, 100, CHARS['boy']['coat'], CHARS['boy']['coat_sh'], 1)
    _hand(c, ax + 20, 1150, math.pi, 120, CHARS['boy']['skin'], CHARS['boy']['skin_sh'], 2, open_=1.0)
    # the young man's hand comes from above and grabs the wrist
    g = ease_out(seg(t, 0.25, 0.75))
    yy = -400 + (1260 - -400) * g
    _limb(c, (760, -300), (680, yy - 380), (ax + 60, yy), 150, 130, '#4a5f8f', '#26355a', 3)
    stroke_taper(c, [(800, -300), (720, yy - 380), (ax + 100, yy - 20)], 10, 4, '#cfe0ff', 0.35)
    _hand(c, ax + 50, yy - 20, -0.2, 150, CHARS['son']['skin'], CHARS['son']['skin_sh'], 4, grip=g > 0.95)
    # droplets / bubbles
    bubbles(c, T, 540, 1700, 20, 5, 300, 900)
    if 0.7 < t < 1.1:
        c.drawCircle(ax + 40, 1250, 240 * seg(t, 0.7, 1.1), P('#e6f2ff', 0.4 * (1 - seg(t, 0.7, 1.1)), stroke=6))
    water_body(c, T, 820, 0.35, colr='#2b4a6e', choppy=1.0)


def son_pull_bg(c, t, T, lvl):
    flooded_interior(c, t, T, lvl, tilt=8)
    hanging_lamp(c, 540, 240, T * 2, 0.75, swing=2.0)


def f08_pull(c, t, T):
    lvl = 1350
    son_pull_bg(c, t, T, lvl)
    lift = ease_io(seg(t, 0.2, 3.2))
    strain = abs(math.sin(on_twos(t) * 7)) * 0.05
    # window opening upper-left with lantern light from outside
    c.drawCircle(120, 520, 520, add_blend(rad((120, 520), 520, [('#ffbf6a', 0.45), ('#ffbf6a', 0)])))
    bx, by = lerp(560, 330, lift), lerp(1250, 820, lift)
    # boy, held under the arms, lifted toward the window
    bust(c, 'boy', bx, by, 1.05, yaw=-0.35, t=t, seed=int(t * 15) + 7,
         head=dict(look=(-0.7, -0.7), brow=1.0, mouth='open', mouth_open=0.4, wet=1.0, tears=0.5, tear_t=t), wet=1.0)
    # the young man (right), waist-deep, arms up under the boy
    bust(c, 'son', 760 + 20 * strain, 1180 - 60 * lift, 1.75, yaw=-0.45, t=t, seed=int(t * 15),
         head=dict(look=(-0.8, -0.7), brow=0.9, mouth='open', mouth_open=0.3 + strain * 4, wet=1.0, tilt=-0.15), wet=1.0, breathe=2.5)
    for k, off in enumerate((-60, 40)):
        _limb(c, (700 + off, 1600), (560 + off * 0.5, lerp(1500, 1200, lift)), (bx + 60 + off * 0.8, by + 160), 120, 100,
              '#2e3c60', '#141c30', 50 + k)
        _hand(c, bx + 60 + off * 0.8, by + 150, 2.6, 80, CHARS['son']['skin'], CHARS['son']['skin_sh'], 60 + k, grip=True)
    water_body(c, T, lvl + math.sin(t * 2) * 10, 0.8, choppy=1.3)
    rain_layer(c, T, 50, (20, 50), 1200, 0.4, 9, 0.25, 2)


def f09_son_cu(c, t, T):
    c.drawPaint(lin((0, 0), (0, H), ['#1a2840', '#0b1222']))
    # warm lantern light from rescuers outside (left)
    c.drawCircle(-100, 500, 900, add_blend(rad((-100, 500), 900, [('#ffbf6a', 0.4), ('#ffbf6a', 0)])))
    drops = random.Random(int(t * 15))
    bust(c, 'son', 560, 880, 2.6, yaw=-0.35, t=t, seed=int(t * 15),
         head=dict(look=(-0.5, 0.35), brow=0.35, mouth='smile', mouth_open=0.0, wet=1.0, eye_open=blink(t, 3) if t > 1.2 else 1.0,
                   light_dir=-1, rim=0.55, rim_c='#ffcf8a'), wet=1.0)
    for i in range(10):
        x = drops.uniform(300, 800)
        y = drops.uniform(400, 1300)
        c.drawCircle(x, y, drops.uniform(2, 5), P('#e6f2ff', 0.6))
    rain_layer(c, T, 90, (40, 80), 1800, 0.25, 4, 0.3, 2.2)


def f10_rescue(c, t, T):
    # exterior: half-sunk carriage window, rescuers on a boat with lanterns
    sk = cached('storm_sky', lambda: paint_plate(storm_sky))
    cam = Cam(1.0 + 0.03 * t, 0, 0, t=t)
    plate(c, sk, cam, 0.3)
    c.save()
    cam.apply(c)
    river(c, T, 1250, flood=1.0, speed=200)
    # sunk carriage, tilted
    c.save()
    c.translate(620, 1400)
    c.rotate(-10)
    carriage_side(c, -400, 300, 1100, 520, lit=0.5, t=0, wet=1, windows=[0.6] * 9)
    c.restore()
    # open window with the boy being lifted out
    up = ease_io(seg(t, 0.4, 3.0))
    figure(c, 'boy', 560, 1500 - 260 * up, 0.55, yaw=-0.4, t=t, seed=int(t * 15), arms=dict(L=(-170, 0), R=(-160, 10), Lopen=1, Ropen=1),
           head=dict(look=(-0.6, -0.6), brow=0.9, mouth='open', mouth_open=0.4, wet=1.0), wet=1.0, legs_hidden=True)
    # rescuers' arms reaching from the boat (left)
    for k in range(2):
        rx = 240 + k * 80
        _limb(c, (rx - 180, 900 + k * 40), (rx, 1000 + k * 30), (430 + 30 * up, 1180 - 150 * up + k * 40), 70, 60, '#3a3a3a', '#1a1a1a', 30 + k)
        _hand(c, 430 + 30 * up, 1180 - 150 * up + k * 40, 1.2, 60, '#d8a880', '#b07a5a', 40 + k, grip=up > 0.5)
    # boat + lantern
    c.drawPath(poly([(-200, 1180), (300, 1180), (240, 1290), (-200, 1290)]), P('#2a1e18'))
    c.drawLine(120, 900, 120, 1180, P('#1a1410', 1, stroke=8))
    lamp_glow(c, 120, 880, 360, 0.9 + 0.1 * math.sin(T * 13))
    c.drawCircle(120, 880, 22, P('#fff0c0'))
    water_body(c, T, 1250, 0.55, colr='#22324a', choppy=1.2)
    c.restore()
    rain_layer(c, T, 240, (50, 100), 2100, 0.2, 7, 0.32, 2.2)


def f11a_pocket(c, t, T):
    c.drawPaint(lin((0, 0), (0, H), ['#1e2a40', '#0b1222']))
    c.drawCircle(-80, 300, 900, add_blend(rad((-80, 300), 900, [('#ffbf6a', 0.3), ('#ffbf6a', 0)])))
    # boy's jacket front (big) with a pocket
    coat = CHARS['boy']
    c.drawRect(skia.Rect(0, 0, W, H), P(coat['coat']))
    c.drawRect(skia.Rect(0, 0, W, H), lin((0, 0), (W, 0), [(coat['coat_hi'], 0.5), (coat['coat_sh'], 0.9)]))
    c.drawPaint(P('#0a1a33', 0.35))
    for k in range(6):
        stroke_taper(c, [(100 + k * 170, 0), (130 + k * 170, H)], 3, 6, coat['coat_sh'], 0.6)
    pk = skia.Rect(250, 1050, 830, 1500)
    c.drawRoundRect(pk, 30, 30, P(coat['coat_sh']))
    # crane goes in
    p = ease_io(seg(t, 0.2, 1.8))
    cy = 500 + p * 640
    c.save()
    c.clipRect(skia.Rect(0, 0, W, 1100 if p > 0.8 else H))
    crane(c, 540, cy, 1.9, rot=-0.3 + 0.3 * p, wet=0.4)
    c.restore()
    # flap of pocket
    c.drawRoundRect(skia.Rect(240, 1040, 840, 1150), 30, 30, P(coat['coat']))
    c.drawRoundRect(skia.Rect(240, 1040, 840, 1150), 30, 30, P(INK, 0.9, stroke=4))
    # son's hand
    hx, hy = 620 + 40 * (1 - p), cy - 140
    _limb(c, (1300, -200), (1000, hy - 300), (hx + 80, hy), 190, 170, CHARS['son']['coat'], CHARS['son']['coat_sh'], 5)
    _hand(c, hx, hy, 0.8, 150, CHARS['son']['skin'], CHARS['son']['skin_sh'], 6, grip=False, open_=0.3)
    c.drawPaint(P('#0a1a33', 0.15))
    rain_layer(c, T, 60, (40, 80), 1800, 0.25, 8, 0.25, 2.2)


def f11b_sun(c, t, T):
    # extreme close-up of the red sun on the crane wing (shallow focus)
    c.drawPaint(lin((0, 0), (0, H), ['#2a2a36', '#101420']))
    z = 1.0 + 0.08 * t
    c.save()
    c.translate(W / 2, H / 2)
    c.scale(z, z)
    c.translate(-W / 2, -H / 2)
    crane(c, 560, 1260, 7.0, rot=-0.15, wet=0.35, glow=0.0)
    c.restore()
    c.drawCircle(W / 2, H / 2, 500, add_blend(rad((W / 2, H / 2), 500, [('#ff8a6a', 0.08), ('#ff8a6a', 0)])))
    rain_layer(c, T, 30, (60, 120), 1600, 0.2, 10, 0.25, 4)


def f12_shout(c, t, T):
    sk = cached('storm_sky', lambda: paint_plate(storm_sky))
    plate(c, sk, Cam(1.1, 0, -100), 0.3)
    river(c, T, 1350, flood=1.0, speed=200)
    # rescuer holds him; boy reaching back toward the window (right)
    figure(c, 'oldman62', 300, 2150, 0.95, yaw=0.3, t=t, seed=int(t * 15) + 2, arms=dict(L=(60, 40), R=(70, 50), Lgrip=True, Rgrip=True),
           head=dict(look=(0.6, -0.2), brow=0.8, wet=1, mouth='neutral'), wet=1)
    figure(c, 'boy', 560, 1900, 0.85, yaw=0.5, t=t, seed=int(t * 15), lean=0.12,
           arms=dict(L=(120, 10), R=(100, -10), Lopen=1, Ropen=1),
           head=dict(look=(1.0, -0.1), brow=1.0, mouth='shout', mouth_open=0.7 + 0.3 * math.sin(t * 6), wet=1.0, tears=0.7, tear_t=t), wet=1.0)
    rain_layer(c, T, 280, (50, 110), 2200, 0.2, 11, 0.35, 2.2)


def f13a_smile(c, t, T):
    c.drawPaint(lin((0, 0), (0, H), ['#18233a', '#080d1a']))
    c.drawCircle(-80, 600, 800, add_blend(rad((-80, 600), 800, [('#ffbf6a', 0.32), ('#ffbf6a', 0)])))
    bust(c, 'son', 540, 900, 2.4, yaw=-0.5 + 0.25 * ease_io(seg(t, 0.3, 1.5)), t=t, seed=int(t * 15),
         head=dict(look=(-0.6, 0.1), brow=0.2, mouth='smile', mouth_open=0.1, wet=1.0, eye_open=blink(t, 6), happy=0.0,
                   rim=0.6, rim_c='#ffcf8a'), wet=1.0)
    rain_layer(c, T, 80, (40, 80), 1800, 0.25, 12, 0.3, 2.2)


def f13b_silhouette(c, t, T):
    lvl = 1250
    flooded_interior(c, t, T, lvl, tilt=8)
    c.drawPaint(P('#03060d', 0.55))
    p = ease_io(seg(t, 0, 1.9))
    c.drawCircle(620, 1000, 520, add_blend(rad((620, 1000), 520, [('#5f7fb0', 0.55), ('#5f7fb0', 0)])))
    # the young man wades away into the dark carriage
    sx = 520 + 120 * p
    s_ = 0.95 - 0.45 * p
    figure(c, 'son', sx, 2050 - 300 * p, s_, yaw=0.3, t=t, seed=int(t * 15), back=True, walk=t * 0.6,
           arms=dict(L=(-20, 10), R=(20, 10)), head=dict(back=True), wet=1.0)
    c.drawPaint(P('#03060d', 0.55 * p))
    water_body(c, T, lvl, 0.8, choppy=1.0)
    c.drawRect(skia.Rect(0, 0, W, H), rad((W / 2, 1100), 1100, [('#000000', 0.0), ('#000000', 0.75)]))


def f14_bank(c, t, T):
    sk = cached('storm_sky', lambda: paint_plate(storm_sky))
    plate(c, sk, Cam(1.0, 0, 0), 0.3)
    c.save()
    gorge(c)
    river(c, T, 1150, flood=1.0, speed=160)
    c.save()
    c.translate(620, 1180)
    c.rotate(-8)
    carriage_side(c, -200, 40, 420, 150, lit=0.0, t=0)
    c.restore()
    for k in range(5):
        lamp_glow(c, 380 + k * 90, 1150 + (k % 2) * 10, 70, 0.8 + 0.2 * math.sin(T * 5 + k))
    c.restore()
    z = 1.0 + 0.04 * t
    c.save()
    c.translate(W / 2, H / 2)
    c.scale(z, z)
    c.translate(-W / 2, -H / 2)
    bust(c, 'boy', 540, 1330, 1.55, yaw=0.12, t=t, seed=int(t * 15) + 3,
         head=dict(look=(0.0, 0.9), brow=1.0, mouth='sad', wet=1.0, tears=0.9, tear_t=t, tilt=0.12, eye_open=0.75), wet=1.0, breathe=2.0)
    # grey rescue blanket over the shoulders
    bl = smooth_path(boil([(200, 1560), (540, 1500), (880, 1560), (980, 2000), (100, 2000)], 2, int(t * 15)))
    c.drawPath(bl, P('#6a6258'))
    c.drawPath(bl, lin((0, 1500), (0, 2000), [('#8a8276', 0.6), ('#3a342e', 0.8)]))
    c.drawPath(bl, P(INK, 0.8, stroke=3))
    # hands holding the wet crane
    crane(c, 540, 1710, 0.9, wet=1.0, glow=0.35 * seg(t, 0.5, 2.5))
    for side in (-1, 1):
        _hand(c, 540 + side * 120, 1760, side * 2.2, 70, CHARS['boy']['skin'], CHARS['boy']['skin_sh'], 70 + side, grip=True)
    c.restore()
    rain_layer(c, T, 220, (40, 90), 1900, 0.15, 13, 0.3, 2.0)
    c.drawPaint(P('#ffffff', 0.85 * ease_in(seg(t, 3.0, 3.48))))


# ================================================================== SCENE 04 (1982)
def r01_haru_weep(c, t, T):
    bokeh_bg(c, t, seed=8)
    lamp_glow(c, 900, 260, 700, 0.75)
    low = ease_io(seg(t, 0.2, 2.2))
    bust(c, 'haru', 520, 880 + 60 * low, 2.6, yaw=0.3, t=t, seed=int(t * 15),
         head=dict(look=(0.0, 0.7 * low), eye_open=lerp(0.9, 0.35, low), brow=1.0, mouth='cry', mouth_open=0.25 * abs(math.sin(t * 3)),
                   tears=lerp(0.3, 1.0, low), tear_t=t, tilt=0.18 * low, wet=0.8, light_dir=1, rim=0.45, rim_c='#ffd38a'), breathe=2.2)
    snow_all(c, t, near=True)
    c.drawPaint(P('#ffffff', 0.85 * (1 - seg(t, 0, 0.5))))


def bench_scene(c, t, T, season):
    """Match-cut montage: same framing of Haru alone on the bench, different seasons."""
    pal = {'winter': ('#c9d6ee', '#7d8fb8', '#e9eff9'), 'spring': ('#f2d6dc', '#b9c79a', '#fbeef0'),
           'autumn': ('#e3b77a', '#9a6a3a', '#f3d6a6')}[season]
    c.drawPaint(lin((0, 0), (0, H), [pal[2], pal[0]]))
    sakura_tree(c, 880, 1300, 1.0, seed=4, season={'winter': 'winter', 'spring': 'spring', 'autumn': 'autumn'}[season])
    c.drawRect(skia.Rect(0, 1300, W, H), lin((0, 1300), (0, H), [pal[1], mix(pal[1], '#000000', 0.25)]))
    bench(c, 420, 1640, 1.2, snow=1.0 if season == 'winter' else 0.0)
    figure(c, 'haru', 340, 1640 - 170 * 1.2 + 600 * 0.75, 0.75, yaw=0.45, t=t, seed=int(T * 15), sit=True,
           arms=dict(L=(18, 30), R=(22, 28)), head=dict(look=(1.0, 0.0), eye_open=blink(t, 2), brow=0.6, mouth='neutral'))
    if season == 'winter':
        snow_all(c, T, near=False)
    elif season == 'spring':
        r = random.Random(1)
        for i in range(40):
            x = (r.uniform(0, W) + T * 40) % W
            y = (r.uniform(0, H) + T * 70 * r.uniform(0.6, 1.2)) % H
            c.drawOval(skia.Rect(x - 7, y - 4, x + 7, y + 4), P('#f6c6d0', 0.9))
    else:
        r = random.Random(2)
        for i in range(30):
            x = (r.uniform(0, W) + T * 50) % W
            y = (r.uniform(0, H) + T * 110 * r.uniform(0.6, 1.2)) % H
            c.save()
            c.translate(x, y)
            c.rotate(T * 90 + i * 30)
            c.drawOval(skia.Rect(-12, -6, 12, 6), P(r.choice(['#d9773a', '#b9472a', '#e9a24a'])))
            c.restore()


def m01(c, t, T):
    bench_scene(c, t, T, 'winter')


def m02(c, t, T):
    bench_scene(c, t, T, 'spring')


def m03(c, t, T):
    bench_scene(c, t, T, 'autumn')


def son_photo(c):
    c.drawPaint(lin((0, -180), (0, 160), ['#bdbab4', '#7a7874']))
    with Layer(c, 1.0):
        bust(c, 'son', 0, -40, 0.62, yaw=0.15, head=dict(mouth='smile', look=(0, 0.2)))
    c.drawPaint(P('#808080', 0.0))


def m04_photo(c, t, T):
    tatami_room(c, night=True)
    c.drawPaint(P('#0a0f20', 0.35))
    lamp_glow(c, 300, 500, 700, 0.6)
    # Haru's hands holding the photograph
    tr = 0.02 * math.sin(t * 14)  # slight tremble
    with Layer(c, 1.0) as cc:
        photo_frame(c, 540, 980 + 20 * math.sin(t), 1.9, rot=-0.05 + tr, img_fn=lambda k: _bw(k))
    for side in (-1, 1):
        _limb(c, (540 + side * 700, 2100), (540 + side * 520, 1500), (540 + side * 330, 1180), 180, 150, CHARS['haru']['coat'], CHARS['haru']['coat_sh'], 20 + side)
        _hand(c, 540 + side * 310, 1150, side * 2.6, 150, CHARS['haru']['skin'], CHARS['haru']['skin_sh'], 22 + side, grip=True)
    # a tear drops onto the glass
    p = seg(t, 1.2, 2.2)
    if 0 < p < 1:
        c.drawCircle(560, 400 + 600 * p * p, 10, P('#dff3ff', 0.9))
    if t > 2.2:
        c.drawCircle(560, 1000, 18 * seg(t, 2.2, 2.5), P('#dff3ff', 0.55))


def _bw(c):
    """Black & white rendering of the son's portrait for the photograph."""
    s = skia.Surface(260, 340)
    cc = s.getCanvas()
    cc.drawPaint(lin((0, 0), (0, 340), ['#cfcac2', '#8a8680']))
    cc.translate(130, 150)
    bust(cc, 'son', 0, 0, 0.62, yaw=0.15, head=dict(mouth='smile', look=(0, 0.2), blush=0))
    img = s.makeImageSnapshot()
    arr = img.toarray(colorType=skia.kRGBA_8888_ColorType).astype(np.float32)
    g = (arr[..., 0] * 0.3 + arr[..., 1] * 0.59 + arr[..., 2] * 0.11)
    out = arr.copy()
    out[..., 0] = np.clip(g * 1.02 + 8, 0, 255)
    out[..., 1] = np.clip(g * 0.98 + 4, 0, 255)
    out[..., 2] = np.clip(g * 0.9, 0, 255)
    bw = skia.Image.fromarray(out.astype(np.uint8), colorType=skia.kRGBA_8888_ColorType)
    c.drawImage(bw, -130, -180)


def m05_tea(c, t, T):
    tatami_room(c, night=True)
    c.drawPaint(P('#0a0f20', 0.3))
    lamp_glow(c, 540, 300, 900, 0.55)
    low_table(c, 540, 1500, 1.25)
    # Haru (seated, left) pours tea for two; the second place is empty
    figure(c, 'haru', 260, 1900, 0.85, yaw=0.5, t=t, seed=int(T * 15), sit=True, legs_hidden=True,
           arms=dict(L=(40, 50), R=(48, 40)), head=dict(look=(0.8, 0.6), brow=0.7, eye_open=0.6 + 0.4 * blink(t, 9), mouth='neutral'))
    teacup(c, 460, 1420, 1.2, full=1.0, steam_t=T)
    teacup(c, 780, 1420, 1.2, full=1.0, steam_t=T + 1.3)
    # empty cushion opposite
    c.drawOval(skia.Rect(700, 1680, 1000, 1760), P('#6a3a3a'))
    c.drawOval(skia.Rect(700, 1680, 1000, 1760), P(INK, 0.6, stroke=3))
    c.drawPaint(P('#000000', 0.6 * seg(t, 1.8, 2.26)))


def station_wide(c, t, T, cam, chars_fn=None, snow=True, warm=0.0, train_fn=None):
    far, mid = station_plates()
    plate(c, far, cam, 0.35)
    if train_fn:
        c.save()
        cam.apply(c, 0.8)
        train_fn(c)
        c.restore()
    plate(c, mid, cam, 0.8)
    c.save()
    cam.apply(c, 0.8)
    lamp_post(c, 760, 1150, 0.85)
    lamp_glow(c, 760, 630, 420, 0.9 + 0.05 * math.sin(T * 7))
    station_clock(c, 190, 700, 0.75, 11, 15.0 if T < 90.8 else 17.0)
    c.restore()
    c.save()
    cam.apply(c, 1.0)
    bench(c, 280, 1720, 1.15, snow=0.9)
    if chars_fn:
        chars_fn(c)
    c.restore()
    if snow:
        snow_all(c, T, near=True)


def trio(c, t, T, haru_yaw=0.45, mar_yaw=-0.3, fat_yaw=-0.45, turn=0.0, haru_head=None, mar_head=None, fat_head=None,
         hand=0.0, haru_stand=0.0):
    """Haru on the bench (left), Maryam between, father standing right."""
    hs = dict(look=(1.0, 0.0), eye_open=blink(t, 2), brow=0.6)
    hs.update(haru_head or {})
    ms = dict(look=(-0.6, -0.3), eye_open=blink(t, 5), brow=0.3)
    ms.update(mar_head or {})
    fs = dict(look=(-0.8, 0.2), eye_open=blink(t, 7), brow=0.7)
    fs.update(fat_head or {})
    bs = 1.15
    seat_y = 1720 - 170 * bs
    s = 0.72
    hy = seat_y + 600 * s
    if haru_stand > 0:
        figure(c, 'haru', 220 + 60 * haru_stand, lerp(hy, 1780, haru_stand), s, yaw=haru_yaw, t=t, seed=int(T * 15), sit=haru_stand < 0.5,
               arms=dict(L=(15, 15), R=(15 + 30 * haru_stand, 15)), head=hs)
    else:
        figure(c, 'haru', 200, hy, s, yaw=haru_yaw, t=t, seed=int(T * 15), sit=True,
               arms=dict(L=(18, 32), R=(22 + 40 * hand, 30 - 10 * hand)), head=hs)
    figure(c, 'maryam', 500 + 40 * hand, 1770, 0.68, yaw=mar_yaw, t=t, seed=int(T * 15) + 3,
           arms=dict(L=(-8, 6), R=(8, -6)), head=ms)
    figure(c, 'father', 700 - 150 * hand, 1860, 0.74, yaw=fat_yaw, t=t, seed=int(T * 15) + 6, lean=-0.15 * hand,
           arms=dict(L=(-8 - 55 * hand, -6 - 25 * hand), R=(-6, -6)), head=fs)


def r02_wide(c, t, T):
    cam = Cam(1.05 + 0.02 * t, 0, 30, t=t)
    hand = ease_io(seg(t, 0.6, 1.4))
    station_wide(c, t, T, cam, lambda cc: trio(cc, t, T, hand=hand, haru_head=dict(look=(0.8, 0.3), brow=1.0, tears=0.5, tear_t=t)))
    c.drawPaint(P('#000000', 0.6 * (1 - seg(t, 0, 0.35))))


def r03_hands(c, t, T):
    bokeh_bg(c, t, seed=11)
    lamp_glow(c, 200, 300, 800, 0.6)
    g = ease_io(seg(t, 0.0, 1.1))
    # Haru's old hand resting, palm down (sleeve from lower left)
    _limb(c, (-250, 1700), (150, 1380), (430, 1200), 230, 200, CHARS['haru']['coat'], CHARS['haru']['coat_sh'], 1)
    _hand(c, 470, 1190, -1.75, 190, CHARS['haru']['skin'], CHARS['haru']['skin_sh'], 2, grip=False, open_=0.15)
    for k in range(4):
        stroke_taper(c, [(560 + k * 22, 1150), (590 + k * 22, 1200)], 2.2, 0.5, CHARS['haru']['skin_sh'], 0.6)
    # father's hand comes down from the upper right and closes over it
    fx = lerp(1250, 600, g)
    fy = lerp(700, 1110, g)
    _limb(c, (1400, 300), (fx + 330, fy - 230), (fx + 60, fy - 20), 230, 200, CHARS['father']['coat'], CHARS['father']['coat_sh'], 3)
    _hand(c, fx, fy, 1.35, 210, CHARS['father']['skin'], CHARS['father']['skin_sh'], 4, grip=False, open_=0.4)
    snow_all(c, T, near=True, dens=0.6)


def r04_father_speaks(c, t, T):
    bokeh_bg(c, t, seed=12)
    lamp_glow(c, 150, 260, 700, 0.8)
    bust(c, 'father', 560, 900, 2.6, yaw=-0.4, t=t, seed=int(t * 15),
         head=dict(look=(-0.7, 0.3), eye_open=blink(t, 8), brow=0.8, mouth='talk', mouth_open=talk(T, 1.3) * 0.7, tears=0.45, tear_t=t,
                   wet=0.5, light_dir=-1, rim=0.5, rim_c='#ffd38a'))
    snow_all(c, T)


def r05_maryam(c, t, T):
    bokeh_bg(c, t, seed=13, colors=('#ffcf7a', '#ffd8e0', '#9fb4e6'))
    lamp_glow(c, 920, 300, 700, 0.7)
    up = ease_io(seg(t, 0.3, 1.5))
    bust(c, 'maryam', 540, 920, 2.8, yaw=0.35 - 0.1 * up, t=t, seed=int(t * 15),
         head=dict(look=(0.5, -0.6 * up), eye_open=blink(t, 9), brow=0.5, mouth='neutral', blush=0.35, tilt=-0.08 * up,
                   light_dir=1, rim=0.5, rim_c='#ffd38a'), breathe=1.2)
    snow_all(c, T)


def r06_haru_realise(c, t, T):
    bokeh_bg(c, t, seed=8)
    lamp_glow(c, 900, 260, 700, 0.75)
    z = 1.0 + 0.05 * t
    c.save()
    c.translate(W / 2, H / 2)
    c.scale(z, z)
    c.translate(-W / 2, -H / 2)
    real = ease_io(seg(t, 1.0, 3.5))
    bust(c, 'haru', 530, 900, 2.7, yaw=0.25, t=t, seed=int(t * 15),
         head=dict(look=(0.6, 0.6), eye_open=lerp(0.75, 1.0, real) * blink(t, 3, 4.5), brow=lerp(1.0, 0.4, real), mouth='sad' if real < 0.6 else 'neutral',
                   mouth_open=0.0, tears=0.7, tear_t=t, wet=0.9, light_dir=1, rim=0.45, rim_c='#ffd38a'))
    c.restore()
    snow_all(c, T)


def r07_twoshot(c, t, T):
    cam = Cam(1.35 + 0.06 * t, 160, -260, t=t)
    station_wide(c, t, T, cam, lambda cc: trio(cc, t, T, hand=0.0, haru_yaw=0.5,
                                               haru_head=dict(look=(0.7, 0.6), brow=0.7, tears=0.7, tear_t=t, eye_open=blink(t, 3)),
                                               mar_yaw=-0.45, mar_head=dict(look=(-0.9, -0.6), brow=0.4)))


def r08_embrace(c, t, T):
    bokeh_bg(c, t, seed=15)
    lamp_glow(c, 820, 380, 800, 0.85)
    g = ease_io(seg(t, 0.0, 1.3))
    sob = math.sin(on_twos(t) * 2 * math.pi / 1.6)
    # Maryam (right, facing left) leans into Haru's chest
    bust(c, 'maryam', lerp(720, 640, g), lerp(1180, 1150, g), 1.55, yaw=-0.55, t=t, seed=int(t * 15) + 2,
         head=dict(look=(-0.8, -0.3), eye_open=lerp(1, 0.0, seg(t, 0.8, 1.3)), brow=0.5, mouth='neutral', blush=0.5, tilt=-0.15 * g),
         breathe=1.2)
    # Haru (left, facing right) bends down, chin over her head, eyes closed, crying
    bust(c, 'haru', lerp(330, 420, g), lerp(820, 900, g) + 6 * sob, 1.75, yaw=0.5, t=t, seed=int(t * 15),
         head=dict(look=(0.6, 0.6), eye_open=lerp(0.7, 0.0, seg(t, 0.4, 1.1)), brow=1.0, mouth='cry', mouth_open=0.2 + 0.15 * abs(sob),
                   tears=1.0, tear_t=t, wet=1.0, tilt=0.35 * g, light_dir=1, rim=0.55), breathe=2.6, shoulder_rot=0.12 * g)
    # Haru's arms wrap around her back
    if g > 0.05:
        ax = lerp(560, 900, g)
        _limb(c, (380, 1500), (lerp(520, 640, g), 1600), (ax, lerp(1500, 1380, g)), 150, 130, CHARS['haru']['coat'], CHARS['haru']['coat_sh'], 9)
        _hand(c, ax, lerp(1500, 1380, g), -1.9, 110, CHARS['haru']['skin'], CHARS['haru']['skin_sh'], 10, grip=False, open_=0.2)
    snow_all(c, T, near=True)


# ================================================================== SCENE 05 — SUPERNATURAL TRAIN
def t01_clock(c, t, T):
    cam = Cam(1.0 + 0.03 * t, 0, 0)
    far, mid = station_plates()
    plate(c, far, Cam(1.8, 0, 100), 0.35, blur=10)
    mm = 15.0 + 1.0 * (t > 1.2) + 1.0 * (t > 2.2)
    station_clock(c, 540, 820, 3.3, 11, mm, glow=0.6 * seg(t, 1.0, 1.6))
    lamp_glow(c, 900, 200, 500, 0.6)
    snow_all(c, T, near=True)
    # bell ring: shock-wave rings
    for k in range(2):
        p = seg(t, 1.2 + k * 0.3, 2.4 + k * 0.3)
        if 0 < p < 1:
            c.drawCircle(540, 820, 330 + p * 500, add_blend(P('#ffe6b0', 0.35 * (1 - p), stroke=6, blur=4)))


def t02_clock_ecu(c, t, T):
    c.drawPaint(P('#1c1b22'))
    c.save()
    z = 1.0 + 0.05 * t
    c.translate(540, 960)
    c.scale(z, z)
    c.translate(-540, -960)
    tick = 16.0 + ease_out(seg(t, 0.15, 0.3))
    station_clock(c, 540, 1160, 8.5, 11, tick, glow=0.5, snow=False)
    c.restore()
    snow_all(c, T, near=True, dens=0.6)


def t03_turn(c, t, T):
    cam = Cam(1.0, 0, 0, t=t)
    turn = ease_io(seg(t, 0.2, 1.2))
    station_wide(c, t, T, cam, lambda cc: trio(cc, t, T, hand=0.0, haru_yaw=0.45, mar_yaw=lerp(-0.3, 0.6, turn), fat_yaw=lerp(-0.45, 0.55, turn),
                                               haru_head=dict(look=(1.0, -0.2), brow=0.3),
                                               mar_head=dict(look=(1.0, -0.2), brow=0.2), fat_head=dict(look=(1.0, -0.1), brow=0.4)))


def t04a_maryam(c, t, T):
    bokeh_bg(c, t, seed=16)
    # warm light growing from the right (approaching train)
    gl = seg(t, 0.2, 1.3)
    c.drawCircle(W + 100, 700, 900, add_blend(rad((W + 100, 700), 900, [('#ffd890', 0.45 * gl), ('#ffd890', 0)])))
    bust(c, 'maryam', 470, 920, 2.7, yaw=0.55, t=t, seed=int(t * 15),
         head=dict(look=(1.0, 0.0), eye_open=1.0, brow=0.2, mouth='open', mouth_open=0.2, blush=0.35, light_dir=1, rim=0.3 + 0.5 * gl, rim_c='#ffdc9a'))
    snow_all(c, T)


def track_pov(c, t, T, light=0.0, train_s=0.0, lamp=1.0, mist_a=0.4):
    far, mid = station_plates()
    c.drawPaint(lin((0, 0), (0, H), ['#0b1430', '#3e4f78']))
    plate(c, far, Cam(1.0, 0, 200), 0.35)
    # tracks straight ahead from the platform edge
    c.save()
    tracks(c, 540, 1050, H + 200, 1700, 30, seed=5)
    barrier(c, 540, 1500, 1.4)
    c.restore()
    if light > 0:
        c.drawCircle(540, 980, 300 * light, add_blend(rad((540, 980), 300 * light + 1, [('#ffe6a8', 0.9 * light), ('#ffb85a', 0)])))
        c.drawCircle(540, 980, 14 * light + 2, add_blend(P('#ffffff', min(1, light * 1.4))))
    mist(c, T, 900, 1200, '#b9c6e6', mist_a, 8, 3, 20)
    snow_all(c, T, near=True)


def t04b_pov(c, t, T):
    track_pov(c, t, T, light=ease_in(seg(t, 0.1, 1.8)) * 0.6)


def t05_emerge(c, t, T):
    # head-on approach through snow & mist: warm, peaceful
    c.drawPaint(lin((0, 0), (0, H), ['#0b1430', '#2a3a66']))
    far, mid = station_plates()
    plate(c, far, Cam(1.0, 0, 200), 0.35)
    tracks(c, 540, 1050, H + 200, 1700, 30, seed=5)
    p = ease_io(seg(t, 0.0, 2.9))
    s = lerp(0.2, 0.95, p)
    with Layer(c, 0.55 + 0.45 * p) as cc:
        locomotive_front(c, 540, 1050 + 520 * p * p * 0.8 + 20, s, lamp=1.0, t=T)
    steam_puffs(c, 540, 1050 - 700 * s, T, s * 1.6, 8, '#f2eee4', 0.45)
    mist(c, T, 800, 1400, '#c9d4ee', 0.45 * (1 - 0.5 * p), 10, 4, 15)
    mist(c, T, 1300, 1900, '#dfe6f6', 0.35, 8, 5, 10)
    barrier(c, 540, 1700, 1.6)
    snow_all(c, T, near=True, dens=1.3)


def train_pass(c, T, x_off, lit=1.0, ghost=0.0, cars=5, y=1500, scale=1.0, son=None):
    c.save()
    c.translate(0, 0)
    rects = []
    for k in range(cars):
        rx = x_off + k * 1450 * scale
        c.save()
        c.translate(rx, y)
        c.scale(scale, scale)
        rr = carriage_side(c, 0, 0, 1420, 460, lit=lit, t=T)
        c.restore()
        rects.extend([skia.Rect(rx + r_.left() * scale, y + r_.top() * scale, rx + r_.right() * scale, y + r_.bottom() * scale) for r_ in rr])
    window_glow(c, rects, lit)
    c.restore()
    return rects


def t06_pass(c, t, T):
    cam = Cam(1.0, 0, 0, t=t)
    far, mid = station_plates()
    plate(c, far, Cam(1.0, 0, 120), 0.35)
    c.drawRect(skia.Rect(0, 1150, W, H), lin((0, 1150), (0, H), ['#6f80aa', '#c9d6ee']))
    xo = 1200 - t * 650
    train_pass(c, T, xo, 1.0, y=1620, scale=1.0)
    mist(c, T, 1300, 1800, '#e6ecf8', 0.35, 10, 6, 30, blend_add=True)
    # the three silhouetted in the foreground, lit warm
    for x, ch_, s in ((140, 'haru', 0.62), (380, 'maryam', 0.62), (620, 'father', 0.62)):
        pass
    snow_all(c, T, near=True)
    c.drawRect(skia.Rect(0, 1700, W, H), lin((0, 1700), (0, H), [('#0b1430', 0.0), ('#0b1430', 0.6)]))


def son_in_window(c, rect, t, wave=0.0, smile=0.5, seed=0, s=1.0):
    c.save()
    c.clipRect(rect)
    c.drawRect(rect, lin((0, rect.top()), (0, rect.bottom()), ['#fff0c2', '#ffd27a', '#e09a4c']))
    cx = rect.centerX()
    figure(c, 'son', cx, rect.bottom() + 820 * s, 0.82 * s, yaw=-0.25, t=t, seed=seed, legs_hidden=True,
           arms=dict(L=(-20, -10), R=(lerp(10, -150, wave), lerp(10, -30, wave)), Ropen=1.0),
           head=dict(look=(-0.4, 0.15), mouth='smile', mouth_open=0.0, eye_open=blink(t, 4), brow=0.1, light_dir=1, rim=0.4, rim_c='#fff4cc'))
    c.drawRect(rect, add_blend(P('#ffdf9a', 0.18)))
    c.restore()


def t07_last_window(c, t, T):
    far, mid = station_plates()
    plate(c, far, Cam(1.3, 0, 0), 0.35, blur=6)
    c.drawPaint(P('#0b1430', 0.3))
    p = ease_out(seg(t, 0, 3.4))
    x = lerp(1100, 160, p)
    c.save()
    c.translate(x, 1550)
    c.scale(1.6, 1.6)
    rr = carriage_side(c, -1100, 0, 1420, 460, lit=1.0, t=T * 0.4, windows=[1.0] * 9)
    c.restore()
    rects = [skia.Rect(x + r_.left() * 1.6, 1550 + r_.top() * 1.6, x + r_.right() * 1.6, 1550 + r_.bottom() * 1.6) for r_ in rr]
    window_glow(c, rects[-3:], 1.0)
    son_in_window(c, rects[-1], t, 0.0, seed=int(t * 15), s=1.35)
    mist(c, T, 1400, 1900, '#e6ecf8', 0.3, 8, 7, 20, blend_add=True)
    snow_all(c, T, near=True)


def window_cu(c, t, T, wave, zoom=1.0, eyes_shine=0.0):
    c.drawPaint(lin((0, 0), (0, H), ['#0b1430', '#1d2f57']))
    rect = skia.Rect(130, 380, 950, 1500)
    c.drawRect(skia.Rect(60, 300, 1020, 1620), P(TRAIN['body']))
    c.drawRect(skia.Rect(60, 300, 1020, 1620), lin((0, 300), (0, 1620), [(TRAIN['body_hi'], 0.4), (TRAIN['body_sh'], 0.8)]))
    c.save()
    c.clipRect(rect)
    c.drawRect(rect, lin((0, rect.top()), (0, rect.bottom()), ['#fff2cc', '#ffd27a', '#e8a656']))
    dust_motes(c, T, rect.left(), rect.top(), rect.right(), rect.bottom(), 30, 2)
    bust(c, 'son', 560, 930, 2.1 * zoom, yaw=-0.3, t=t, seed=int(t * 15),
         head=dict(look=(-0.55, 0.2), mouth='smile', mouth_open=0.0, eye_open=blink(t, 2, 4.2), brow=0.15, wet=eyes_shine, light_dir=1, rim=0.5,
                   rim_c='#fff6d8', blush=0.3))
    if wave > 0:
        hx = 330 - 40 * math.sin(t * 3) * wave
        hy = lerp(1600, 980, wave)
        _limb(c, (380, 1700), (300, lerp(1650, 1250, wave)), (hx, hy), 160, 140, CHARS['son']['coat'], CHARS['son']['coat_sh'], 3)
        _hand(c, hx, hy, math.pi + 0.1 * math.sin(t * 3), 135, CHARS['son']['skin'], CHARS['son']['skin_sh'], 4, open_=1.0)
    c.drawRect(rect, add_blend(P('#ffe2a0', 0.12)))
    c.restore()
    c.drawRect(rect, P('#1a1414', 1, stroke=26))
    c.drawRect(skia.Rect(rect.left() - 60, rect.top() - 80, rect.right() + 60, rect.bottom() + 80), add_blend(P('#ffcf7a', 0.18, blur=50)))
    # snow drifting in front of the glass, lit by the window
    snow_layer(c, T, 90, (2, 5), 70, 20, 21, 0.9, 1, colr='#fff3d6')
    snow_layer(c, T, 12, (10, 16), 140, 40, 22, 0.5, 6, colr='#fff3d6')


def t08_son_cu(c, t, T):
    window_cu(c, t, T, 0.0, 1.0)


def t09_wave(c, t, T):
    window_cu(c, t, T, ease_io(seg(t, 0.4, 1.6)), 1.0)


def t10a_stand(c, t, T):
    cam = Cam(1.25, -120, -60, t=t)
    st = ease_io(seg(t, 0.1, 1.5))

    def chars_fn(cc):
        trio(cc, t, T, haru_stand=st, haru_yaw=0.5, mar_yaw=0.6, fat_yaw=0.55, haru_head=dict(look=(1, -0.1), brow=0.9, tears=0.6, tear_t=t),
             mar_head=dict(look=(1, -0.1)), fat_head=dict(look=(1, -0.1)))

    def train_fn(cc):
        train_pass(cc, T, 900 - (T - 101.38) * 120, 1.0, y=1500, scale=0.7)

    station_wide(c, t, T, cam, chars_fn, train_fn=train_fn)


def t10b_step(c, t, T):
    # Haru steps forward toward the train... and stops
    c.drawPaint(lin((0, 0), (0, H), ['#0b1430', '#3e4f78']))
    xo = 600 - (T - 101.38) * 120
    train_pass(c, T, xo, 1.0, y=1450, scale=0.85)
    c.drawRect(skia.Rect(0, 1450, W, H), lin((0, 1450), (0, H), ['#8a9cc6', '#d7e1f4']))
    step = ease_io(seg(t, 0.1, 1.0))
    stop = seg(t, 1.0, 1.4)
    figure(c, 'haru', 380 + 120 * step, 1850, 0.78, yaw=0.6, t=t, seed=int(t * 15), walk=None if step >= 1 or step <= 0 else t * 1.5,
           lean=0.12 * step * (1 - stop), arms=dict(L=(20 + 30 * step, 20), R=(40 + 50 * step * (1 - stop * 0.5), 20), Lopen=0.8, Ropen=0.8),
           head=dict(look=(1, -0.3), brow=0.9, tears=0.8, tear_t=t, mouth='sad'), light_dir=1, rim=0.7, rim_c='#ffd890')
    mist(c, T, 1450, 1900, '#e6ecf8', 0.3, 8, 7, 20, blend_add=True)
    snow_all(c, T, near=True)


def t10c_hands(c, t, T):
    c.drawPaint(lin((0, 0), (0, H), ['#2a2236', '#0b1430']))
    c.drawCircle(W, 600, 1200, add_blend(rad((W, 600), 1200, [('#ffcf7a', 0.5), ('#ffcf7a', 0)])))
    tr = math.sin(t * 38) * 6 + math.sin(t * 23) * 4
    for side, xx in ((-1, 380), (1, 700)):
        _limb(c, (xx - 200 * side * 0 - 100, 2200), (xx - 40, 1600), (xx + tr * (1 if side > 0 else -1), 1150 + tr * 0.5), 210, 180,
              CHARS['haru']['coat'], CHARS['haru']['coat_sh'], 5 + side)
        _hand(c, xx + tr, 1120 + tr * 0.5, math.pi + side * 0.2, 170, CHARS['haru']['skin'], CHARS['haru']['skin_sh'], 7 + side, open_=0.6 + 0.2 * math.sin(t * 9))
    # hands slowly close and lower: he stops himself
    snow_all(c, T, near=True)


def t11_haru_forgive(c, t, T):
    c.drawPaint(lin((0, 0), (0, H), ['#1d2a4a', '#0b1430']))
    # warm moving window light washing across his face
    for k in range(3):
        x = ((T * 120 + k * 500) % 1600) - 300
        c.drawRect(skia.Rect(x, 0, x + 260, H), add_blend(P('#ffcf7a', 0.10, blur=60)))
    c.drawCircle(W + 50, 800, 900, add_blend(rad((W + 50, 800), 900, [('#ffd890', 0.42), ('#ffd890', 0)])))
    speak = 1.80 < t < 4.2
    sm = ease_io(seg(t, 3.6, 4.8))
    bust(c, 'haru', 500, 900, 2.75, yaw=0.45, t=t, seed=int(t * 15),
         head=dict(look=(0.9, -0.15), eye_open=blink(t, 7, 4.0) * lerp(0.85, 0.7, sm), brow=lerp(1.0, 0.5, sm),
                   mouth='talk' if speak else ('smile' if sm > 0.3 else 'sad'), mouth_open=talk(T, 1.1) * 0.55 if speak else 0.0,
                   tears=1.0, tear_t=t, wet=1.0, light_dir=1, rim=0.75, rim_c='#ffd890', happy=0.0), breathe=1.8)
    snow_all(c, T)


def t12_son_forgive(c, t, T):
    window_cu(c, t, T, ease_io(seg(t, 4.0, 5.2)), 1.0 + 0.04 * t, eyes_shine=ease_io(seg(t, 0.4, 1.8)))


def t13_vanish(c, t, T):
    track_pov(c, t, T, light=0.0, mist_a=0.5)
    # train recedes into the distance, golden light fading
    p = ease_in(seg(t, 0.0, 2.6))
    s = lerp(0.55, 0.05, p)
    a = 1 - seg(t, 1.4, 2.7)
    gx, gy = 540, 1050
    with Layer(c, a):
        c.save()
        c.translate(gx, gy)
        c.scale(s, s)
        c.translate(-gx, -gy)
        rr = [skia.Rect(gx - 260 + k * 0, gy - 600, gx + 260, gy - 120) for k in range(1)]
        c.drawRect(skia.Rect(gx - 300, gy - 640, gx + 300, gy - 60), P(TRAIN['body']))
        c.drawRect(skia.Rect(gx - 220, gy - 560, gx + 220, gy - 260), P('#ffd27a'))
        c.drawRect(skia.Rect(gx - 300, gy - 640, gx + 300, gy - 60), P(INK, 1, stroke=10))
        c.restore()
        c.drawCircle(gx, gy - 300 * s, 600 * s + 60, add_blend(rad((gx, gy - 300 * s), 600 * s + 60, [('#ffd890', 0.6 * a), ('#ffd890', 0)])))
    mist(c, T, 900, 1250, '#c9d4ee', 0.55 * p, 10, 9, 20)
    snow_all(c, T, near=True, dens=1.3)


def t14a_peace(c, t, T):
    bokeh_bg(c, t, seed=8, colors=('#9fb4e6', '#c9d6ee'))
    lower = ease_io(seg(t, 0.0, 1.0))
    bust(c, 'haru', 540, 900, 2.7, yaw=0.3, t=t, seed=int(t * 15),
         head=dict(look=(0.4, 0.0), eye_open=lerp(1.0, 0.0, seg(t, 0.9, 1.2)), brow=lerp(0.6, -0.1, lower), mouth='smile', mouth_open=0.0,
                   tears=0.5 * (1 - lower), tear_t=t, wet=0.5, light_dir=-1, rim=0.25, rim_c='#cfe0ff', happy=0.0), breathe=0.7)
    snow_all(c, T, near=True, dens=0.7)


def t14b_empty(c, t, T):
    cam = Cam(1.0 + 0.02 * t, 0, 0, t=t)
    far, mid = station_plates()
    plate(c, far, cam, 0.35)
    plate(c, mid, cam, 0.8)
    c.save()
    cam.apply(c, 0.8)
    lamp_post(c, 760, 1150, 0.85)
    lamp_glow(c, 760, 630, 420, 0.85)
    station_clock(c, 190, 700, 0.75, 11, 18.0)
    c.restore()
    c.save()
    cam.apply(c)
    bench(c, 280, 1720, 1.15, snow=1.0)
    c.restore()
    snow_all(c, T, near=False, dens=0.6)


# ================================================================== SCENE 07 — A NEW FAMILY
def e01_bench_spring(c, t, T):
    c.drawPaint(lin((0, 0), (0, H), ['#cfe3f6', '#f6e3d6']))
    sakura_tree(c, 820, 1350, 1.15, seed=7, season='spring')
    c.drawRect(skia.Rect(0, 1350, W, H), lin((0, 1350), (0, H), ['#b9c79a', '#8fa26a']))
    tracks(c, 760, 1350, H + 200, 900, 20, rail='#7a6a5a', snow='#a9b98a', seed=3)
    bench(c, 380, 1700, 1.2, snow=0.0)
    r = random.Random(1)
    for i in range(50):
        x = (r.uniform(0, W) + T * 40) % W
        y = (r.uniform(0, H) + T * 60 * r.uniform(0.6, 1.2)) % H
        c.drawOval(skia.Rect(x - 7, y - 4, x + 7, y + 4), P('#f6c6d0', 0.9))
    light_shafts(c, 900, -100, math.pi * 0.62, 4, 2200, 200, '#fff0c8', 0.12, T)


def home_table(c, t, T, pour=0.0, laugh=0.0, mar_chin=0.0):
    cached_room = cached('room', lambda: paint_plate(maryam_room))
    plate(c, cached_room, Cam(1.0))
    # window on the back wall with curtains
    window_view(c, 220, 260, 860, 900, T)
    c.drawRect(skia.Rect(220, 260, 860, 900), P('#5a3a22', 1, stroke=24))
    c.drawLine(540, 260, 540, 900, P('#5a3a22', 1, stroke=14))
    c.drawRect(skia.Rect(190, 900, 890, 940), P('#7a5236'))
    crane(c, 470, 885, 0.32, seed=1)
    crane(c, 610, 885, 0.32, seed=2, flip=True, paper='#f6f0e2')
    curtain(c, 220, 230, 960, 120, T, 1)
    curtain(c, 860, 230, 960, 120, T, -1)
    light_shafts(c, 540, 600, math.pi * 0.55, 4, 1800, 220, '#ffd9a0', 0.16, T)
    # table and family
    figure(c, 'father', 860, 2050, 0.8, yaw=-0.45, t=t, seed=int(T * 15) + 2, sit=True, legs_hidden=True,
           arms=dict(L=(-30, -40), R=(-25, -35)), head=dict(look=(-0.8, 0.1), mouth='smile', eye_open=blink(t, 3), brow=-0.1))
    figure(c, 'haru', 220, 2000, 0.8, yaw=0.5, t=t, seed=int(T * 15), sit=True, legs_hidden=True,
           arms=dict(L=(30, 40), R=(35 + 10 * laugh, 35)),
           head=dict(look=(0.9, 0.2), mouth='smile' if laugh < 0.5 else 'open', mouth_open=0.3 * laugh * abs(math.sin(t * 7)),
                     eye_open=blink(t, 5), happy=laugh, brow=-0.1, tilt=-0.08 * laugh))
    figure(c, 'maryam', 560, 1980, 0.85, yaw=0.0, t=t, seed=int(T * 15) + 4, sit=True, legs_hidden=True,
           arms=dict(L=(160 * mar_chin, 140 * mar_chin), R=(-160 * mar_chin, -140 * mar_chin)),
           head=dict(look=(-0.5, 0.0), mouth='smile', eye_open=blink(t, 6), blush=0.45, brow=0.0, tilt=0.1 * mar_chin))
    low_table(c, 540, 1520, 1.25, '#6a4028')
    c.drawRect(skia.Rect(-50, 1585, W + 50, H + 50), lin((0, 1585), (0, H), ['#8a3a34', '#5a2420']))
    for k in range(9):
        c.drawLine(k * 135, 1590, k * 135 + 20, H, P('#4a1a18', 0.4, stroke=3))
    c.drawRect(skia.Rect(-50, 1585, W + 50, 1600), P('#c9a24a', 0.8))
    teapot(c, 300 + 90 * pour, 1380 - 60 * pour, 0.8, rot=-0.5 * pour)
    if pour > 0.3:
        stroke_taper(c, bezier_pts((440, 1330), (470, 1360), (480, 1420), 8), 6, 4, '#c9a24a', 0.85)
    teacup(c, 480, 1450, 0.9, full=min(1, pour * 1.3) if pour > 0 else 1.0, steam_t=T)
    teacup(c, 620, 1460, 0.9, full=1.0, steam_t=T + 1)
    teacup(c, 760, 1450, 0.9, full=1.0, steam_t=T + 2)
    dust_motes(c, T, 0, 300, W, 1500, 50, 3)


def e02a(c, t, T):
    pour = ease_io(seg(t, 2.3, 3.6)) * (1 - seg(t, 4.2, 4.7))
    home_table(c, t, T, pour=pour)
    c.drawPaint(P('#fff3d8', 0.6 * (1 - seg(t, 0, 0.6))))


def e02b(c, t, T):
    home_table(c, t, T, laugh=ease_io(seg(t, 0.2, 0.8)), mar_chin=ease_io(seg(t, 0.0, 0.6)))


def e03_cranes(c, t, T):
    cr = cached('room', lambda: paint_plate(maryam_room))
    z = 1.0 + 0.03 * t
    c.save()
    c.translate(W / 2, H / 2)
    c.scale(z, z)
    c.translate(-W / 2, -H / 2)
    window_view(c, -200, -200, W + 200, 1250, T)
    with Layer(c, 1.0, blur=8):
        c.drawRect(skia.Rect(-200, -200, W + 200, 1250), P('#ffffff', 0.0))
    c.drawRect(skia.Rect(-200, 1250, W + 200, H + 200), lin((0, 1250), (0, H), ['#8a5a36', '#5a341e']))
    c.drawRect(skia.Rect(-200, 1230, W + 200, 1300), P('#a87452'))
    crane(c, 330, 1215, 1.35, seed=1, glow=0.3)
    crane(c, 760, 1215, 1.35, seed=2, flip=True, paper='#f6f0e2', glow=0.3)
    c.restore()
    curtain(c, -40, -100, 1300, 240, T, 1)
    curtain(c, W + 40, -100, 1300, 240, T, -1)
    light_shafts(c, 700, 200, math.pi * 0.6, 4, 1900, 220, '#ffe1a8', 0.2, T)
    dust_motes(c, T, 0, 200, W, 1600, 60, 4)


def e04_hands(c, t, T):
    cr = cached('room', lambda: paint_plate(maryam_room))
    plate(c, cr, Cam(1.6, 0, 300), 1.0, blur=14)
    c.drawRect(skia.Rect(0, 1150, W, H), lin((0, 1150), (0, H), ['#7a4a2c', '#5a341e']))
    teacup(c, 540, 1180, 3.0, full=1.0, steam_t=T)
    for side in (-1, 1):
        _limb(c, (540 + side * 760, 2100), (540 + side * 520, 1550), (540 + side * 210, 1260), 220, 190, CHARS['haru']['coat'], CHARS['haru']['coat_sh'], 11 + side)
        _hand(c, 540 + side * 175, 1200, side * 2.1, 175, CHARS['haru']['skin'], CHARS['haru']['skin_sh'], 13 + side, grip=True)
    light_shafts(c, 900, 0, math.pi * 0.7, 3, 1600, 220, '#ffe1a8', 0.18, T)
    dust_motes(c, T, 0, 200, W, 1400, 40, 5)


def e05_final(c, t, T):
    # pull back from the cranes: window, curtains, family at the table, station far away
    p = ease_io(seg(t, 0.0, 5.5))
    z = lerp(3.0, 1.0, p)
    c.save()
    c.translate(540, 870)
    c.scale(z, z)
    c.translate(-540, -870)
    home_table(c, t, T, laugh=0.3 + 0.2 * math.sin(t * 0.8), mar_chin=1.0)
    c.restore()
    dust_motes(c, T, 0, 0, W, H, 40, 6)
    c.drawPaint(P('#000000', ease_io(seg(t, 4.9, 7.3))))


# ================================================================== TIMELINE
SHOTS = [
    # name,               start,  end,    fn,               grade,        xfade
    ('S01 father CU', 0.00, 2.90, s01_father_cu, GR_NIGHT, 0.0),
    ('S01 eye reflect', 2.90, 3.95, s01_eye, GR_NIGHT, 0.0),
    ('S02 carriage rain', 3.95, 7.88, f01_carriage, GR_FLASH, 0.45),
    ('S02 bridge storm', 7.88, 10.62, f02_bridge, GR_FLASH, 0.0),
    ('S02 bridge cracks', 10.62, 11.55, f03a_crack, GR_FLASH, 0.0),
    ('S02 carriage tilts', 11.55, 12.75, f03b_tilt, GR_FLASH, 0.0),
    ('S02 carriage falls', 12.75, 14.16, f03c_fall, GR_FLASH, 0.0),
    ('S02 flooding', 14.16, 18.20, f04_flood, GR_FLASH, 0.0),
    ('S02 boy panic', 18.20, 21.24, f05_boy_panic, GR_FLASH, 0.0),
    ('S02 boy reaches', 21.24, 24.96, f06_reach, GR_FLASH, 0.0),
    ('S03 hand grabs', 24.96, 27.38, f07_hand, GR_FLASH, 0.0),
    ('S03 son lifts boy', 27.38, 30.96, f08_pull, GR_FLASH, 0.0),
    ('S03 son reassures', 30.96, 34.06, f09_son_cu, GR_FLASH, 0.0),
    ('S03 rescuers', 34.06, 37.66, f10_rescue, GR_FLASH, 0.0),
    ('S03 crane in pocket', 37.66, 39.90, f11a_pocket, GR_FLASH, 0.0),
    ('S03 red sun', 39.90, 41.66, f11b_sun, dict(GR_FLASH, sat=0.85), 0.25),
    ('S03 boy cries out', 41.66, 44.40, f12_shout, GR_FLASH, 0.0),
    ('S03 son smiles', 44.40, 46.10, f13a_smile, GR_FLASH, 0.0),
    ('S03 into the dark', 46.10, 48.06, f13b_silhouette, GR_FLASH, 0.0),
    ('S03 riverbank', 48.06, 51.54, f14_bank, GR_FLASH, 0.3),
    ('S04 Haru weeps', 51.54, 54.74, r01_haru_weep, GR_NIGHT, 0.0),
    ('S04 winter wait', 54.74, 56.55, m01, GR_MEM, 0.4),
    ('S04 spring wait', 56.55, 58.00, m02, GR_MEM, 0.25),
    ('S04 autumn wait', 58.00, 59.36, m03, GR_MEM, 0.25),
    ('S04 photograph', 59.36, 62.60, m04_photo, GR_MEM, 0.35),
    ('S04 tea for two', 62.60, 64.86, m05_tea, GR_MEM, 0.35),
    ('S04 hand held (wide)', 64.86, 66.30, r02_wide, GR_NIGHT, 0.0),
    ('S04 hands CU', 66.30, 68.30, r03_hands, GR_NIGHT, 0.0),
    ('S04 father speaks', 68.30, 71.44, r04_father_speaks, GR_NIGHT, 0.0),
    ('S04 Maryam', 71.44, 74.74, r05_maryam, GR_NIGHT, 0.0),
    ('S04 Haru understands', 74.74, 79.58, r06_haru_realise, GR_NIGHT, 0.0),
    ('S04 Haru & Maryam', 79.58, 85.70, r07_twoshot, GR_NIGHT, 0.0),
    ('S04 embrace', 85.70, 88.58, r08_embrace, GR_WARMNIGHT, 0.3),
    ('S05 clock rings', 88.58, 91.20, t01_clock, GR_NIGHT, 0.0),
    ('S05 11:17', 91.20, 93.60, t02_clock_ecu, GR_NIGHT, 0.0),
    ('S05 whistle - all turn', 93.60, 95.30, t03_turn, GR_NIGHT, 0.0),
    ('S05 Maryam looks', 95.30, 96.60, t04a_maryam, GR_NIGHT, 0.0),
    ('S05 light on the tracks', 96.60, 98.48, t04b_pov, GR_WARMNIGHT, 0.0),
    ('S05 train emerges', 98.48, 101.38, t05_emerge, GR_WARMNIGHT, 0.3),
    ('S05 glowing windows', 101.38, 103.40, t06_pass, GR_WARMNIGHT, 0.0),
    ('S06 last window', 103.40, 107.20, t07_last_window, GR_WARMNIGHT, 0.0),
    ('S06 son as in 1962', 107.20, 110.28, t08_son_cu, GR_WARMNIGHT, 0.3),
    ('S06 son waves', 110.28, 113.54, t09_wave, GR_WARMNIGHT, 0.0),
    ('S06 Haru stands', 113.54, 115.26, t10a_stand, GR_WARMNIGHT, 0.0),
    ('S06 step... and stop', 115.26, 117.00, t10b_step, GR_WARMNIGHT, 0.0),
    ('S06 trembling hands', 117.00, 118.46, t10c_hands, GR_WARMNIGHT, 0.0),
    ('S06 forgive me', 118.46, 123.28, t11_haru_forgive, GR_WARMNIGHT, 0.0),
    ('S06 forgiveness', 123.28, 129.00, t12_son_forgive, GR_WARMNIGHT, 0.3),
    ('S06 train vanishes', 129.00, 131.68, t13_vanish, GR_NIGHT, 0.4),
    ('S06 Haru at peace', 131.68, 133.60, t14a_peace, GR_NIGHT, 0.0),
    ('S06 silent station', 133.60, 135.14, t14b_empty, GR_NIGHT, 0.3),
    ('S07 empty bench, spring', 135.14, 138.12, e01_bench_spring, GR_SPRING, 0.8),
    ('S07 tea together', 138.12, 142.82, e02a, GR_SPRING, 0.5),
    ('S07 stories of the son', 142.82, 145.04, e02b, GR_SPRING, 0.0),
    ('S07 two cranes', 145.04, 150.40, e03_cranes, GR_SPRING, 0.5),
    ('S07 relaxed hands', 150.40, 153.40, e04_hands, GR_SPRING, 0.5),
    ('S07 final pull-back', 153.40, 161.00, e05_final, GR_SPRING, 0.6),
]

DURATION = 161.0

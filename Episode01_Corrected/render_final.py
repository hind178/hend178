"""Episode 01 - final renderer (V6).

Renders each of the 22 narration-aligned shots as a separate 1080x1920 / 30 fps clip
(production/scenes/scene_XX.mp4), then `assemble_final.py` concatenates them and
muxes the untouched original narration into Episode_01_Final.mp4.

Identity rules honoured here:
  * Characters are ONLY the locked sprites (pixels from cleaned_original.png, with the
    V6 refined alpha in composite_v6.png). No regeneration, no redraw, no mirroring,
    no recolouring of the sprite itself.
  * Motion is limited animation: whole-sprite translation, breathing scale, gentle sway,
    walk bob, hops/nods, camera moves, depth of field, light and particle overlays.
  * Medium shots crop the sprite above the waist and anchor the crop edge below the
    frame, so Hind's suitcase is not shown in class or inside the bus.

Usage:  python render_final.py --scene 5      (one scene)
        python render_final.py --all          (every scene, sequentially)
        python render_final.py --still 5 2.0  (debug still: scene 5 at +2.0 s)
"""
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw, ImageFilter, ImageEnhance, ImageFont
import numpy as np, subprocess, math, json, functools, sys, argparse

P = Path(__file__).resolve().parent
W, H, FPS = 1080, 1920, 30
DURATION = 107.075875                       # exact narration length (ffprobe)
TOTAL_FRAMES = 3212                         # 3212/30 = 107.067 s video, audio 107.076 s
OUT = P / 'production' / 'scenes'

# --------------------------------------------------------------------------- helpers
def smooth(a):
    a = min(1.0, max(0.0, a)); return a * a * (3 - 2 * a)

def lerp(a, b, q): return a + (b - a) * q

def keyed(keys, t):
    """keys: [(t, value...), ...] -> eased interpolation (tuple)."""
    if t <= keys[0][0]: return keys[0][1:]
    for (t0, *v0), (t1, *v1) in zip(keys, keys[1:]):
        if t <= t1:
            q = smooth((t - t0) / (t1 - t0)) if t1 > t0 else 1
            return tuple(lerp(a, b, q) for a, b in zip(v0, v1))
    return keys[-1][1:]

def moving(keys, t, eps=1e-3):
    a = keyed(keys, t); b = keyed(keys, t + 1 / FPS)
    return any(abs(x - y) > eps * 0.05 for x, y in zip(a, b))

@functools.lru_cache(None)
def src_sprite(name):
    im = Image.open(P / 'characters' / name / 'composite_v6.png').convert('RGBA')
    return im.crop(im.getbbox())

@functools.lru_cache(None)
def background(name, sw, sh, blur, margin):
    im = Image.open(P / 'backgrounds' / f'{name}.png').convert('RGB')
    im = ImageOps.fit(im, (round(sw * (1 + margin)), round(sh * (1 + margin))), Image.Resampling.LANCZOS)
    if blur: im = im.filter(ImageFilter.GaussianBlur(blur))
    return im.convert('RGBA')

@functools.lru_cache(None)
def vignette():
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((x - W / 2) / (W * .62)) ** 2 + ((y - H * .46) / (H * .62)) ** 2)
    a = np.clip((d - .55) / .6, 0, 1) ** 1.6 * 150
    return Image.fromarray(a.astype(np.uint8), 'L')

@functools.lru_cache(None)
def mote_sprite(r):
    im = Image.new('L', (r * 4, r * 4)); ImageDraw.Draw(im).ellipse((r, r, 3 * r, 3 * r), fill=255)
    im = im.filter(ImageFilter.GaussianBlur(r * .6))
    out = Image.new('RGBA', im.size, (255, 236, 190, 0)); out.putalpha(im); return out

@functools.lru_cache(None)
def light_band():
    w, h = 520, H * 2
    x = np.arange(w, dtype=np.float32); a = np.exp(-((x - w / 2) / (w / 5)) ** 2) * 46
    band = Image.new('RGBA', (w, h), (255, 226, 170, 0)); band.putalpha(Image.fromarray(np.tile(a, (h, 1)).astype(np.uint8)))
    return band.rotate(-18, Image.Resampling.BICUBIC, expand=True)

FONT_AR = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
FONT_EN = '/usr/share/fonts/truetype/freefont/FreeSerif.ttf'

@functools.lru_cache(None)
def name_card(ar, en):
    """Cream name plate in the style of references/approved_group.png."""
    fa = ImageFont.truetype(FONT_AR, 54, layout_engine=ImageFont.Layout.RAQM)
    fe = ImageFont.truetype(FONT_EN, 46)
    pad, gap = 40, 8
    ba = fa.getbbox(ar, direction='rtl', language='ar'); be = fe.getbbox(en)
    w = max(ba[2] - ba[0], be[2] - be[0]) + 2 * pad
    h = (ba[3] - ba[1]) + (be[3] - be[1]) + 2 * pad + gap
    im = Image.new('RGBA', (w + 30, h + 30)); d = ImageDraw.Draw(im)
    sh = Image.new('RGBA', im.size); ImageDraw.Draw(sh).rounded_rectangle((18, 22, w + 12, h + 16), 26, fill=(60, 35, 20, 110))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(7)))
    d.rounded_rectangle((10, 10, w + 10, h + 10), 26, fill=(250, 241, 226, 255), outline=(196, 160, 118, 255), width=5)
    d.rounded_rectangle((20, 20, w, h), 20, outline=(222, 196, 160, 255), width=2)
    d.text((10 + w / 2, 10 + pad - ba[1]), ar, font=fa, fill=(52, 34, 26), anchor='ma', direction='rtl', language='ar')
    d.text((10 + w / 2, 10 + pad + (ba[3] - ba[1]) + gap), en, font=fe, fill=(70, 48, 36), anchor='ma')
    return im

@functools.lru_cache(None)
def end_title():
    f = ImageFont.truetype(FONT_AR, 92, layout_engine=ImageFont.Layout.RAQM)
    im = Image.new('RGBA', (W, 260)); d = ImageDraw.Draw(im)
    d.text((W / 2, 130), 'يتبع...', font=f, fill=(250, 238, 214, 255), anchor='mm', direction='rtl', language='ar')
    glow = im.filter(ImageFilter.GaussianBlur(14)); out = Image.new('RGBA', im.size)
    out.alpha_composite(glow); out.alpha_composite(glow); out.alpha_composite(im); return out

def grade_lut(warm=0.0, bright=1.0, lift=0):
    r = [min(255, max(0, int((i * bright + lift) * (1 + .05 * warm)))) for i in range(256)]
    g = [min(255, max(0, int((i * bright + lift) * (1 + .012 * warm)))) for i in range(256)]
    b = [min(255, max(0, int((i * bright + lift) * (1 - .06 * warm)))) for i in range(256)]
    return r + g + b

# --------------------------------------------------------------------------- actors
def A(name, keys, crop=1.0, walk=False, blur=0, hops=(), nods=(), shake=(), phase=0.0, shadow=True):
    """keys: [(t_rel, x, y, h)], x/y = bottom-centre anchor (0..1 of frame), h = full-body
    height as a fraction of frame height. crop<1 keeps only the top part of the body."""
    return dict(name=name, keys=keys, crop=crop, walk=walk, blur=blur, hops=hops, nods=nods, shake=shake, phase=phase, shadow=shadow and crop >= 1)

def card(ar, en, x, y, t): return dict(ar=ar, en=en, x=x, y=y, t=t)

# Shot list. Cuts sit inside measured narration pauses (ffmpeg silencedetect, -35 dB),
# event timings come from the Whisper word timestamps in production/narration_transcript_whisper.json.
SHOTS = [
 dict(t=(0.0, 6.6), bg='bus_stop_clean', fade_in=.6, motes=True,
      note='Hind sets off on the 5-day university trip expecting to spend it alone',
      cam=[(0, 1.0, .50, .56), (6.6, 1.10, .44, .60)],
      actors=[A('Hind', [(0, .18, .90, .44), (3.4, .40, .90, .44)], walk=True)],
      cards=[card('هند', 'Hind', .72, .50, .5)]),
 dict(t=(6.6, 14.6), bg='campus_walk_clean', bgblur=1.5, motes=True, grade=dict(warm=.3, bright=.93), xfade=.35,
      note='A girl who was not even one of her close friends changed all her expectations',
      cam=[(0, 1.0, .52, .56), (8.0, 1.42, .55, .40)],
      actors=[A('Loreen', [(0, .55, .87, .42)])]),
 dict(t=(14.6, 17.65), bg='university_clean', bgblur=4, motes=True,
      note='Hind was in her third year at university',
      cam=[(0, 1.0, .5, .5), (3.05, 1.05, .5, .48)], bgpan=(0, -.02),
      actors=[A('Hind', [(0, .50, 1.03, 1.10)], crop=.5)]),
 dict(t=(17.65, 23.55), bg='institute_clean', motes=True,
      note='Top of her institute, she entered the college directly in the second year',
      cam=[(0, 1.12, .38, .55), (5.9, 1.12, .58, .55)],
      actors=[A('Hind', [(0, .26, .89, .40), (5.9, .62, .89, .40)], walk=True)]),
 dict(t=(23.55, 28.1), bg='computer_lab_clean', bgblur=4, grade=dict(warm=-.2, bright=.97),
      note='So she had little time to get to know her classmates',
      cam=[(0, 1.0, .5, .5), (4.55, 1.07, .55, .46)], bgpan=(.015, -.015),
      actors=[A('Hind', [(0, .60, 1.03, 1.05)], crop=.5)]),
 dict(t=(28.1, 35.0), bg='university_clean', motes=True,
      note='In the third year the university organised a 5-day scientific trip out of the city',
      cam=[(0, 1.15, .46, .48), (2.2, 1.15, .50, .46), (6.9, 1.55, .80, .45)]),
 dict(t=(35.0, 38.45), bg='campus_garden_clean', bgblur=4, grade=dict(warm=-.5, bright=.9, sat=.78),
      note="But Hind's two friends decided not to go",
      cam=[(0, 1.14, .45, .47), (3.45, 1.0, .5, .5)],
      actors=[A('Hind', [(0, .42, 1.03, 1.05)], crop=.5)]),
 dict(t=(38.45, 44.1), bg='campus_walk_clean', motes=True,
      note='Among the girls going were Loreen and her friend Lizette',
      cam=[(0, 1.05, .5, .55), (5.65, 1.1, .5, .55)],
      actors=[A('Loreen', [(0, -.18, .88, .42), (2.7, .34, .88, .42)], walk=True),
              A('Lizette', [(0, 1.25, .88, .42), (3.2, 1.25, .88, .42), (4.75, .68, .88, .42)], walk=True, phase=1.3)],
      cards=[card('لورين', 'Loreen', .30, .30, 3.55), card('ليزيت', 'Lizette', .70, .26, 4.83)]),
 dict(t=(44.1, 50.45), bg='campus_garden_clean', motes=True,
      note='The two were inseparable',
      cam=[(0, 1.05, .5, .56), (6.35, 1.0, .5, .56)],
      actors=[A('Loreen', [(0, .44, .72, .26), (6.35, .38, .93, .45)], walk=True),
              A('Lizette', [(0, .60, .72, .26), (6.35, .66, .93, .45)], walk=True, phase=1.1)]),
 dict(t=(50.45, 53.9), bg='university_clean', motes=True,
      note='The whole college talked about their friendship',
      cam=[(0, 1.3, .5, .58), (3.45, 1.0, .5, .52)],
      actors=[A('Loreen', [(0, .43, .80, .27)]), A('Lizette', [(0, .57, .80, .27)], phase=1.4)]),
 dict(t=(53.9, 61.55), bg='campus_garden_clean', motes=True,
      note='Her relationship with Hind was only that of classmates; Hind never imposes herself',
      cam=[(0, 1.0, .5, .55), (7.65, 1.12, .40, .50)],
      actors=[A('Loreen', [(0, .70, .70, .25)], blur=1.6, phase=.4),
              A('Lizette', [(0, .84, .70, .25)], blur=1.6, phase=1.9),
              A('Hind', [(0, .30, 1.10, .62)], shadow=False)]),
 dict(t=(61.55, 65.9), bg='bus_stop_clean', grade=dict(warm=-.3, bright=.92, sat=.85), xfade=.3,
      note='She prepared herself to spend most of the trip alone',
      cam=[(0, 1.28, .45, .62), (4.35, 1.0, .5, .56)],
      actors=[A('Hind', [(0, .42, .84, .34)])]),
 dict(t=(65.9, 71.9), bg='university_clean', motes=True,
      note='At the university gate, Loreen welcomes her with great joy',
      cam=[(0, 1.08, .42, .56), (6.0, 1.1, .55, .56)],
      actors=[A('Hind', [(0, .02, .88, .40), (2.3, .30, .88, .40)], walk=True),
              A('Lizette', [(0, 1.3, .84, .38), (2.9, 1.3, .84, .38), (4.6, .86, .84, .38)], walk=True, phase=1.7),
              A('Loreen', [(0, 1.2, .89, .41), (2.4, 1.2, .89, .41), (4.2, .62, .89, .41)], walk=True, hops=(4.5, 5.15))]),
 dict(t=(71.9, 76.5), bg='university_clean', bgblur=4, motes=True,
      note='"Hind! You are coming too? I am so happy to see you!"',
      cam=[(0, 1.0, .5, .5), (4.6, 1.06, .56, .47)], bgpan=(0, -.02),
      actors=[A('Hind', [(0, .25, 1.04, 1.0)], crop=.5, phase=.6),
              A('Loreen', [(0, .75, 1.03, 1.08)], crop=.5, hops=(.34, 2.68, 3.05))]),
 dict(t=(76.5, 79.2), bg='bus_stop_clean', motes=True,
      note='As they boarded the bus, Loreen said...',
      cam=[(0, 1.05, .5, .56), (2.7, 1.12, .56, .50)],
      actors=[A('Lizette', [(0, .78, .92, .38), (2.7, .66, .70, .20)], walk=True, phase=.8),
              A('Loreen', [(0, .58, .95, .40), (2.7, .58, .72, .21)], walk=True, phase=.3),
              A('Hind', [(0, .30, .99, .42), (2.7, .48, .74, .22)], walk=True)]),
 dict(t=(79.2, 82.45), bg='bus_interior_clean', bgblur=3, lightbands=True, busshake=True,
      note='"Each time we swap seats: once I sit next to Hind..."',
      cam=[(0, 1.0, .5, .5), (3.25, 1.04, .5, .5)], bgpan=(.02, 0),
      actors=[A('Hind', [(0, .30, 1.04, .98)], crop=.5, phase=.5),
              A('Loreen', [(0, .71, 1.03, 1.04)], crop=.5, nods=(.5, 1.8))]),
 dict(t=(82.45, 84.3), bg='bus_interior_clean', bgblur=3, lightbands=True, busshake=True,
      note='"...and once Lizette sits next to her"',
      cam=[(0, 1.02, .5, .5), (1.85, 1.04, .5, .5)], bgpan=(.02, 0),
      actors=[A('Hind', [(0, .30, 1.04, .98)], crop=.5, phase=.5),
              A('Lizette', [(0, 1.25, 1.03, 1.02), (.55, .71, 1.03, 1.02)], crop=.5, phase=1.2)]),
 dict(t=(84.3, 91.2), bg='bus_interior_clean', bgblur=4, lightbands=True, busshake=True,
      note='Hind, surprised: "No Loreen, you two are close friends, it is fine for me to sit alone"',
      cam=[(0, 1.0, .5, .5), (6.9, 1.08, .5, .45)], bgpan=(.025, 0),
      actors=[A('Hind', [(0, .50, 1.03, 1.30)], crop=.45, shake=((2.15, .55),))]),
 dict(t=(91.2, 93.2), bg='bus_interior_clean', bgblur=4, lightbands=True, busshake=True,
      note='But Loreen refused',
      cam=[(0, 1.0, .5, .5), (2.0, 1.06, .5, .46)], bgpan=(.02, 0),
      actors=[A('Loreen', [(0, .50, 1.03, 1.34)], crop=.45, nods=(1.0,), shake=((1.2, .45),))]),
 dict(t=(93.2, 99.9), bg='bus_interior_clean', bgblur=3, lightbands=True, busshake=True, grade=dict(warm=.6, bright=1.02),
      note='From that moment Hind began to discover a side of Loreen she had never known',
      cam=[(0, 1.0, .5, .52), (6.7, 1.14, .5, .44)], bgpan=(.03, 0),
      actors=[A('Hind', [(0, .33, 1.04, 1.0)], crop=.5, phase=.5),
              A('Loreen', [(0, .69, 1.03, 1.05)], crop=.5, phase=2.0)]),
 dict(t=(99.9, 102.9), bg='hotel_exterior_clean', xfade=.5, motes=True,
      note='But what Loreen did when they reached the hotel...',
      cam=[(0, 1.0, .5, .55), (3.0, 1.15, .40, .55)], grade_keys=[(0, .3, 1.0), (3.0, .9, .86)]),
 dict(t=(102.9, DURATION), bg='hotel_lobby_clean', xfade=.3, motes=True, grade=dict(warm=.6, bright=.95),
      note='...made Hind realise it was not just courtesy  (cliffhanger)',
      cam=[(0, 1.0, .5, .55), (4.18, 1.22, .45, .50)],
      actors=[A('Lizette', [(0, .76, .80, .36)], phase=1.5),
              A('Hind', [(0, .28, .81, .36)], phase=.4),
              A('Loreen', [(0, .52, .82, .37)], phase=2.4)],
      fade_out=(2.6, 3.6), end_title=2.85),
]

# --------------------------------------------------------------------------- render
def actor_layer(a, t, S):
    x, y, h = keyed(a['keys'], t)
    src = src_sprite(a['name'])
    hh = h * H * S
    full_w = src.width * hh / src.height
    ch = max(1, round(src.height * a['crop']))
    part = src.crop((0, 0, src.width, ch)) if a['crop'] < 1 else src
    # breathing: tiny vertical scale around the feet
    br = .006 * math.sin(2 * math.pi * t / 3.4 + a['phase'] * 2.1)
    tw = max(1, round(full_w * (1 - br * .4))); th = max(1, round(hh * a['crop'] * (1 + br)))
    im = part.resize((tw, th), Image.Resampling.LANCZOS if th < part.height else Image.Resampling.BICUBIC)
    if a['blur']: im = im.filter(ImageFilter.GaussianBlur(a['blur'] * S))
    ang = .35 * math.sin(2 * math.pi * t / 5.3 + a['phase'])
    dx = dy = 0.0
    if a['walk'] and moving(a['keys'], t):
        step = t * 2.0 * math.pi * 1.9 + a['phase']
        dy -= abs(math.sin(step)) * .012 * hh
        ang += 1.1 * math.sin(step)
    for th0 in a['hops']:                       # joyful hop
        q = (t - th0) / .42
        if 0 <= q <= 1: dy -= math.sin(math.pi * q) * .035 * hh
    for tn in a['nods']:                        # nod / emphatic dip
        q = (t - tn) / .5
        if 0 <= q <= 1: dy += math.sin(math.pi * q) * .012 * hh; ang += 1.2 * math.sin(math.pi * q)
    for ts, d in a['shake']:                    # side-to-side "no"
        q = (t - ts) / d
        if 0 <= q <= 1: dx += math.sin(q * 3 * 2 * math.pi) * (1 - q) * .018 * W * S
    pad = 40
    big = Image.new('RGBA', (im.width + 2 * pad, im.height + pad)); big.alpha_composite(im, (pad, pad // 2))
    big = big.rotate(ang, Image.Resampling.BICUBIC, center=(big.width / 2, big.height - pad / 2))
    px = x * W * S + dx - big.width / 2
    py = y * H * S + dy - big.height + pad / 2
    return big, (round(px), round(py)), (x * W * S, y * H * S, hh)

def shot_frame(i, t_abs):
    s = SHOTS[i]; t0, t1 = s['t']; t = t_abs - t0
    zmax = max(k[1] for k in s['cam']); S = min(1.5, max(1.0, zmax))
    sw, sh = round(W * S), round(H * S)
    margin = .06
    bgim = background(s['bg'], sw, sh, s.get('bgblur', 0) * S, margin)
    pan = s.get('bgpan', (0, 0)); q = smooth(t / (t1 - t0))
    ox = round((bgim.width - sw) / 2 + pan[0] * q * sw); oy = round((bgim.height - sh) / 2 + pan[1] * q * sh)
    canvas = bgim.crop((ox, oy, ox + sw, oy + sh))
    actors = s.get('actors', [])
    layers = [actor_layer(a, t, S) + (a,) for a in actors]
    shadow = Image.new('L', (sw, sh)); d = ImageDraw.Draw(shadow)
    for im, pos, (fx, fy, hh), a in layers:
        if a['shadow']:
            d.ellipse((fx - hh * .14, fy - hh * .012, fx + hh * .14, fy + hh * .016), fill=110)
    if any(a['shadow'] for a in actors):
        sh_l = shadow.filter(ImageFilter.GaussianBlur(9 * S))
        canvas = Image.composite(Image.new('RGBA', (sw, sh), (45, 30, 22, 255)), canvas, sh_l.point(lambda v: v * .55))
    for im, pos, _, a in sorted(layers, key=lambda z: z[2][1]):
        paste_clip(canvas, im, pos)
    # camera
    z, cx, cy = keyed(s['cam'], t)
    if s.get('busshake'):
        cy += .0012 * math.sin(t * 2 * math.pi * 7.3) + .0008 * math.sin(t * 2 * math.pi * 3.1)
    cw, chh = W * S / z, H * S / z
    cw, chh = min(cw, sw), min(chh, sh)
    left = min(max(cx * sw - cw / 2, 0), sw - cw); top = min(max(cy * sh - chh / 2, 0), sh - chh)
    frame = canvas.transform((W, H), Image.Transform.EXTENT, (left, top, left + cw, top + chh), Image.Resampling.BICUBIC)
    # overlays
    if s.get('lightbands'):
        b = light_band(); period = 1.7
        for k in range(2):
            ph = ((t + k * period / 2) % period) / period
            frame.alpha_composite(b, (round(-b.width + ph * (W + b.width)), -H // 3))
    if s.get('motes'):
        rng = np.random.default_rng(i * 7 + 3)
        for k in range(26):
            px0, py0, sp, r, ph = rng.random(), rng.random(), .01 + .02 * rng.random(), int(3 + 6 * rng.random()), rng.random() * 6.28
            mx = (px0 + .02 * math.sin(t * .7 + ph)) * W; my = ((py0 - sp * t) % 1.0) * H
            al = .35 + .35 * math.sin(t * 1.3 + ph)
            m = mote_sprite(r); mm = m.copy(); mm.putalpha(m.getchannel('A').point(lambda v, al=al: int(v * max(0, al))))
            frame.alpha_composite(mm, (round(mx), round(my)))
    for c in s.get('cards', []):
        q = (t - c['t']) / .35
        if q > 0:
            im = name_card(c['ar'], c['en']); k = smooth(q); sc = .85 + .15 * k
            im2 = im.resize((round(im.width * sc), round(im.height * sc)), Image.Resampling.BICUBIC)
            im2.putalpha(im2.getchannel('A').point(lambda v, k=k: int(v * k)))
            frame.alpha_composite(im2, (round(c['x'] * W - im2.width / 2), round(c['y'] * H - im2.height / 2 + (1 - k) * 30)))
    frame = frame.convert('RGB')
    g = dict(s.get('grade', {}))
    if 'grade_keys' in s:
        warm, bright = keyed(s['grade_keys'], t); g.update(warm=warm, bright=bright)
    if g.get('sat', 1) != 1: frame = ImageEnhance.Color(frame).enhance(g['sat'])
    frame = frame.point(grade_lut(warm=.25 + g.get('warm', 0), bright=g.get('bright', 1)))
    frame = Image.composite(Image.new('RGB', (W, H), (20, 12, 10)), frame, vignette())
    if s.get('fade_in') and t < s['fade_in']:
        frame = Image.blend(Image.new('RGB', (W, H), (12, 9, 10)), frame, smooth(t / s['fade_in']))
    if s.get('fade_out'):
        a0, a1 = s['fade_out']
        if t > a0: frame = Image.blend(frame, Image.new('RGB', (W, H), (14, 11, 14)), .88 * smooth((t - a0) / (a1 - a0)))
    if s.get('end_title') is not None and t > s['end_title']:
        k = smooth((t - s['end_title']) / .6); et = end_title().copy()
        et.putalpha(et.getchannel('A').point(lambda v, k=k: int(v * k)))
        fr = frame.convert('RGBA'); fr.alpha_composite(et, (0, round(H * .44))); frame = fr.convert('RGB')
    return frame

def paste_clip(canvas, im, pos):
    x, y = pos; l, t_ = max(0, -x), max(0, -y)
    r, b = min(im.width, canvas.width - x), min(im.height, canvas.height - y)
    if l >= r or t_ >= b: return
    canvas.alpha_composite(im.crop((l, t_, r, b)), (x + l, y + t_))

def frame_at(i, t_abs):
    f = shot_frame(i, t_abs)
    s = SHOTS[i]; xf = s.get('xfade', 0)
    if i > 0 and xf and t_abs - s['t'][0] < xf:
        f = Image.blend(shot_frame(i - 1, t_abs), f, smooth((t_abs - s['t'][0]) / xf))
    return f

def frame_range(i):
    a = round(SHOTS[i]['t'][0] * FPS)
    b = TOTAL_FRAMES if i == len(SHOTS) - 1 else round(SHOTS[i]['t'][1] * FPS)
    return a, b

def render_scene(i):
    OUT.mkdir(parents=True, exist_ok=True)
    a, b = frame_range(i); out = OUT / f'scene_{i + 1:02}.mp4'
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
           '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', '-r', str(FPS),
           '-g', '60', '-threads', '1', '-x264-params', 'log-level=error', str(out)]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for n in range(a, b):
        p.stdin.write(frame_at(i, n / FPS).tobytes())
    p.stdin.close(); assert p.wait() == 0
    print(f'scene {i + 1:02}: frames {a}-{b - 1} ({(b - a) / FPS:.3f}s) -> {out.name}', flush=True)

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--scene', type=int); ap.add_argument('--all', action='store_true')
    ap.add_argument('--still', nargs=2); ap.add_argument('--plan', action='store_true'); args = ap.parse_args()
    if args.plan or args.all:
        plan = [dict(scene=k + 1, start=s['t'][0], end=s['t'][1], frames=list(frame_range(k)), background=s['bg'],
                     characters=[a['name'] for a in s.get('actors', [])], event=s['note']) for k, s in enumerate(SHOTS)]
        (P / 'production' / 'final_shot_plan.json').write_text(json.dumps(dict(fps=FPS, size=[W, H], duration=DURATION,
            total_frames=TOTAL_FRAMES, timing='aligned to narration pauses + Whisper word timestamps', shots=plan), ensure_ascii=False, indent=1))
    if args.still:
        k, dt = int(args.still[0]) - 1, float(args.still[1])
        frame_at(k, SHOTS[k]['t'][0] + dt).save(P / 'production' / f'still_{k + 1:02}_{dt:.2f}.jpg', quality=92)
    if args.scene: render_scene(args.scene - 1)
    if args.all:
        for k in range(len(SHOTS)): render_scene(k)

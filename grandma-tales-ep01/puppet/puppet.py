#!/usr/bin/env python3
"""My Grandmother's Tales — Ep01 · 2.5D puppet test (5 s, 1080x1920, 30 fps).

The approved artwork of Hind is the puppet. Nothing is redrawn:
  1. segmentation -> character layer (RGBA) + background plate (silhouette filled in)
  2. eye pass      -> eyelid slides the original lash line down (blinks), gaze shifts, smile warp
  3. deformation   -> head turn about the neck, breathing, hijab / skirt sway, bag pendulum
  4. layers        -> background (parallax 0.5), Hind (1.0), foreground flowers (1.8)
  5. light & lens  -> drifting leaf dapple, warm rim light, rack focus, tilt-shift band, grade
Frames are piped to ffmpeg (H.264, yuv420p, 30 fps).
"""
import os, sys, subprocess, math
import numpy as np, cv2
from rembg import remove, new_session
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
A = lambda *p: os.path.join(HERE, *p)
W, H, FPS, DUR = 1080, 1920, 30, 5.0
N = int(FPS * DUR)

def ss(x): x = np.clip(x, 0, 1); return x * x * (3 - 2 * x)
def seg(t, a, b): return float(np.clip((t - a) / (b - a), 0, 1))
def eio(x): return 4 * x ** 3 if x < .5 else 1 - (-2 * x + 2) ** 3 / 2
def pulse(t, a, b): return math.sin(math.pi * seg(t, a, b))

# ---------------------------------------------------------------- 1. layers
src = cv2.imread(A('assets/hind_approved.png'), cv2.IMREAD_COLOR)          # BGR 1199x1312
h0, w0 = src.shape[:2]
os.makedirs(A('work'), exist_ok=True)
cut_p = A('work/hind_cut.png')
if not os.path.exists(cut_p):
    s = new_session('isnet-general-use')
    remove(Image.open(A('assets/hind_approved.png')).convert('RGB'), session=s, alpha_matting=True,
           alpha_matting_foreground_threshold=240, alpha_matting_background_threshold=15, alpha_matting_erode_size=8).save(cut_p)
alpha = np.array(Image.open(cut_p))[..., 3].astype(np.float32) / 255
char = np.dstack([src.astype(np.float32) / 255, alpha])                    # straight alpha, BGR + A

bg_p = A('work/bg_plate.png')
if not os.path.exists(bg_p):
    m = (alpha > .04).astype(np.uint8) * 255
    m = cv2.dilate(m, np.ones((31, 31), np.uint8))
    # inpaint at half size (fast, the background is soft bokeh anyway), then blend back
    sm = cv2.resize(src, None, fx=.5, fy=.5, interpolation=cv2.INTER_AREA)
    mm = cv2.resize(m, (sm.shape[1], sm.shape[0]), interpolation=cv2.INTER_NEAREST)
    fill = cv2.inpaint(sm, mm, 9, cv2.INPAINT_TELEA)
    fill = cv2.GaussianBlur(fill, (0, 0), 6)
    fill = cv2.resize(fill, (w0, h0), interpolation=cv2.INTER_CUBIC)
    k = cv2.GaussianBlur(m.astype(np.float32) / 255, (0, 0), 6)[..., None]
    cv2.imwrite(bg_p, (src * (1 - k) + fill * k).astype(np.uint8))
bg = cv2.imread(bg_p).astype(np.float32) / 255

# foreground: the pink flowers from the artwork's own lower-left corner, used as a near layer
fl_p = A('work/flowers.png')
if not os.path.exists(fl_p):
    crop = Image.open(A('assets/hind_approved.png')).convert('RGB').crop((0, 820, 170, h0))
    remove(crop, session=new_session('isnet-general-use')).save(fl_p)
flowers = np.array(Image.open(fl_p)).astype(np.float32) / 255              # RGBA (RGB order)
flowers = np.dstack([flowers[..., 2], flowers[..., 1], flowers[..., 0], flowers[..., 3]])
fl_h, fl_w = flowers.shape[:2]

YY, XX = np.mgrid[0:h0, 0:w0].astype(np.float32)

# ---------------------------------------------------------------- 2. face rig (orig px)
def parab(p0, p1, p2):
    c = np.polyfit([p0[0], p1[0], p2[0]], [p0[1], p1[1], p2[1]], 2)
    return lambda x: np.polyval(c, x)
EYES = [  # inner, top, outer, bottom
    dict(inner=(460, 301), top=(433, 276), outer=(402, 309), bot=(432, 319)),
    dict(inner=(512, 280), top=(533, 256), outer=(557, 281), bot=(533, 294)),
]
for e in EYES:
    e['U'] = parab(e['inner'], e['top'], e['outer'])
    e['L'] = parab(e['inner'], e['bot'], e['outer'])
    e['x0'], e['x1'] = min(e['inner'][0], e['outer'][0]), max(e['inner'][0], e['outer'][0])
    e['cx'], e['cy'] = (e['x0'] + e['x1']) / 2, (e['top'][1] + e['bot'][1]) / 2
SKIN = src[283:290, 474:482].reshape(-1, 3).mean(0) / 255               # nose-bridge skin
LID = SKIN * np.array([.93, .95, .97])
MOUTH = [(472, 362, -1), (541, 343, 1)]                                     # corners, side

def face_pass(img, blink, gx, gy, smile):
    """img: float BGRA (orig size). Returns new image with lids, gaze and smile applied."""
    out = img.copy()
    x0, x1, y0, y1 = 380, 580, 230, 380
    sub = img[y0:y1, x0:x1]
    yy, xx = YY[y0:y1, x0:x1].copy(), XX[y0:y1, x0:x1].copy()
    sx, sy = xx.copy(), yy.copy()
    fill = np.zeros(xx.shape, np.float32)
    lid_rgb = np.zeros(xx.shape + (3,), np.float32)
    lines = []
    for e in EYES:
        U, L = e['U'](xx), e['L'](xx)
        inside_x = (xx > e['x0'] - 2) & (xx < e['x1'] + 2)
        # gaze: shift the iris inside the eye opening
        r = ((xx - e['cx']) / ((e['x1'] - e['x0']) * .55)) ** 2 + ((yy - e['cy']) / 22) ** 2
        wg = np.clip(1 - r, 0, 1) ** 1.5 * ((yy > U - 1) & (yy < L + 1))
        sx -= gx * wg; sy -= gy * wg
        if blink > .002:
            d = (np.clip(blink * (L - U) * 1.08, 0, None) + 1.5 * blink) * inside_x   # lid travel per column
            Nl = U + d                                                               # lid edge
            top = U - 3 - 11 * blink                                                 # lid starts just above the lash root
            lid = (yy >= top) & (yy < Nl) & (d > .3)
            fade = np.clip((yy - top) / 6, 0, 1)
            fill = np.maximum(fill, lid.astype(np.float32) * fade)
            ys = np.clip((U - 18).astype(int), 0, h0 - 1)
            col = img[ys, np.clip(xx.astype(int), 0, w0 - 1), :3]
            col = cv2.GaussianBlur(col, (0, 0), 4)
            k = np.clip((yy - top) / np.maximum(Nl - top, 1), 0, 1)[..., None]
            # rounded lid: a soft highlight over the eyeball, a shadowed crease at the top, darker toward the corners
            ex = (xx - e['cx']) / ((e['x1'] - e['x0']) * .5)
            dome = np.exp(-(ex ** 2) * 1.6 - ((k[..., 0] - .45) / .35) ** 2)[..., None]
            crease = np.exp(-((k[..., 0] - .06) / .08) ** 2)[..., None]
            corner = np.clip(np.abs(ex) - .55, 0, 1)[..., None]
            shaded = col * (1 - .1 * k ** 2 - .16 * crease - .18 * corner) + .07 * dome * np.float32([.85, .92, 1.0])
            lid_rgb = np.where(lid[..., None], shaded, lid_rgb)
            lines.append((e, blink))
    for (mx, my, side) in MOUTH:
        g = np.exp(-((xx - mx) ** 2 + (yy - my) ** 2) / (2 * 13 ** 2))
        sx -= side * smile * .5 * g; sy += smile * g                          # corners up & out
    # remap only the sub-window (maps are absolute coords into the full image)
    sub_w = cv2.remap(img, sx.astype(np.float32), sy.astype(np.float32), cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    if fill.max() > 0:
        f = cv2.GaussianBlur(fill, (0, 0), 1.0)[..., None]
        lid_img = np.dstack([cv2.GaussianBlur(lid_rgb, (0, 0), 1.2), sub_w[..., 3:4]])
        sub_w = sub_w * (1 - f) + lid_img * f
        # the closing lash line along the lid edge, lashes pointing down (drawn 4x, then reduced: soft and thin)
        S4 = 4
        m = np.zeros(((y1 - y0) * S4, (x1 - x0) * S4), np.uint8)
        for e, bl in lines:
            xs = np.linspace(e['x0'], e['x1'], 40)
            Ue, Le = e['U'](xs), e['L'](xs)
            ye = Ue + (np.clip(bl * (Le - Ue) * 1.08, 0, None) + 1.5 * bl)
            pts = np.stack([(xs - x0) * S4, (ye - y0) * S4], 1).astype(np.int32)
            th = int(S4 * (1.6 + 1.6 * bl))
            cv2.polylines(m, [pts], False, 255, th, cv2.LINE_AA)
            if bl > .6:
                out_side = 1 if e['outer'][0] > e['inner'][0] else -1
                for i in range(6):
                    u = .3 + i * .12; xi = e['inner'][0] + (e['outer'][0] - e['inner'][0]) * u
                    yi = float(e['U'](xi) + np.clip(bl * (e['L'](xi) - e['U'](xi)) * 1.08, 0, None) + 1.5 * bl)
                    ln = (5 + 4 * u) * bl
                    p0 = (int((xi - x0) * S4), int((yi - y0) * S4))
                    p1 = (int((xi + out_side * ln * .6 - x0) * S4), int((yi + ln * .8 - y0) * S4))
                    cv2.line(m, p0, p1, 255, S4, cv2.LINE_AA)
        if m.any():
            ma = cv2.resize(m, (x1 - x0, y1 - y0), interpolation=cv2.INTER_AREA).astype(np.float32)[..., None] / 255
            lash_col = np.float32([.07, .08, .11, 1])
            sub_w = sub_w * (1 - ma * .92) + lash_col * ma * .92
    out[y0:y1, x0:x1] = sub_w
    return out

# ---------------------------------------------------------------- 3. body deformation (dst -> src)
def soft_ellipse(cx, cy, rx, ry, fall):
    d = np.sqrt(((XX - cx) / rx) ** 2 + ((YY - cy) / ry) ** 2)
    return 1 - ss((d - 1) * min(rx, ry) / fall)
W_HEAD = soft_ellipse(478, 300, 165, 195, 95).astype(np.float32)
W_TORSO = np.exp(-(((XX - 470) / 230) ** 2 + ((YY - 600) / 200) ** 2)).astype(np.float32)
W_DRAPE_L = (ss((360 - XX) / 120) * ss((YY - 380) / 200) * np.clip((YY - 380) / 560, 0, 1)).astype(np.float32)
W_DRAPE_R = (ss((XX - 620) / 50) * ss((740 - XX) / 40) * ss((YY - 480) / 120) * np.clip((YY - 480) / 420, 0, 1)).astype(np.float32)
W_SUIT = ((XX > 300) & (XX < 560) & (YY > 1010)).astype(np.float32)
W_SUIT = cv2.GaussianBlur(W_SUIT, (0, 0), 12)
W_SKIRT = (np.clip((YY - 790) / 520, 0, 1) * (1 - W_SUIT)).astype(np.float32)
W_BAG = cv2.GaussianBlur(((XX > 590) & (XX < 780) & (YY > 820) & (YY < 1130)).astype(np.float32), (0, 0), 10)
PIV_HEAD = np.array([492, 455], np.float32); PIV_BAG = np.array([640, 835], np.float32)

def rot_disp(th, piv, tx=0, ty=0):
    c, s = math.cos(th), math.sin(th)
    px, py = XX - piv[0], YY - piv[1]
    return (c * px - s * py + piv[0] + tx) - XX, (s * px + c * py + piv[1] + ty) - YY

def body_maps(t, P):
    dx = np.zeros_like(XX); dy = np.zeros_like(YY)
    hx, hy = rot_disp(P['head_th'], PIV_HEAD, P['head_tx'], P['head_ty'])
    dx += W_HEAD * hx; dy += W_HEAD * hy
    dy += W_TORSO * (-2.6 * P['breath']); dx += W_TORSO * (XX - 470) * .004 * P['breath']
    wind = P['wind']
    dx += W_DRAPE_L * (3.5 * math.sin(2 * math.pi * .55 * t) * 1 + 2.5 * wind * np.sin(2 * math.pi * 1.1 * t - YY * .012))
    dx += W_DRAPE_R * (2.5 * math.sin(2 * math.pi * .6 * t + 1) + 2.0 * wind * np.sin(2 * math.pi * 1.2 * t - YY * .014))
    dx += W_SKIRT * (2.2 * np.sin(2 * math.pi * .5 * t - YY * .009) + 1.8 * wind * np.sin(2 * math.pi * 1.0 * t - YY * .016))
    bx, by = rot_disp(P['bag_th'], PIV_BAG)
    dx += W_BAG * bx; dy += W_BAG * by
    return (XX - dx).astype(np.float32), (YY - dy).astype(np.float32)                       # inverse (small-displacement approximation)

# ---------------------------------------------------------------- 4. timeline
BLINKS = [1.05, 3.35, 4.55]
def blink_at(t):
    b = 0.0
    for bt in BLINKS:
        u = (t - bt) / .22
        if 0 <= u <= 1: b = max(b, math.sin(math.pi * u) ** .7)
    return b

def params(t):
    look = ss(seg(t, 1.45, 2.25)) - ss(seg(t, 3.55, 4.35))            # 0 = up-right (original), 1 = toward the bus/camera
    hope = ss(seg(t, 3.7, 4.7))
    sigh = pulse(t, 2.5, 3.4)
    br = math.sin(2 * math.pi * t / 2.6 - .6) * .8 + sigh * 1.2
    return dict(
        head_th=math.radians(-2.2 * look + .5 * math.sin(t * 1.3) + .9 * hope), head_tx=-3 * look + 1.5 * hope, head_ty=1.5 * look - .8 * br * .3 - 1.5 * hope,
        breath=br, wind=.4 + .6 * pulse(t, 1.8, 3.8),
        bag_th=math.radians(.9 * math.sin(2 * math.pi * .45 * t + .5)),
        blink=blink_at(t), gx=-4.2 * look + 1.2 * hope, gy=1.2 * look - .8 * hope,
        smile=-1.6 * look * (1 - hope) + 2.2 * hope,
    )

# camera: slow push-in and drift toward her face; background and foreground move with parallax
C0 = np.array([468., 668.]); S0 = 1920 / h0 * 1.045
def cam(t):
    u = eio(seg(t, 0, 5))
    s = S0 * (1 + .075 * u)
    c = C0 + np.array([14, -70]) * u + np.array([3 * math.sin(t * .8), 2 * math.sin(t * .6)])
    return s, c
def affine(s, c):
    return np.float32([[s, 0, W / 2 - s * c[0]], [0, s, H / 2 - s * c[1]]])

# ---------------------------------------------------------------- 5. light & lens
rng = np.random.default_rng(7)
DAP = cv2.resize(rng.random((18, 18)).astype(np.float32), (w0 * 2, h0 * 2), interpolation=cv2.INTER_CUBIC)
DAP = cv2.GaussianBlur(DAP, (0, 0), 25); DAP = (DAP - DAP.min()) / (DAP.max() - DAP.min())
def dapple(t):
    ox, oy = int(140 + 60 * t), int(90 + 25 * t)
    return DAP[oy:oy + h0, ox:ox + w0]

EDGE = None
def rim(a):
    er = cv2.erode((a > .5).astype(np.uint8), np.ones((9, 9), np.uint8)).astype(np.float32)
    e = np.clip(a - cv2.GaussianBlur(er, (0, 0), 3), 0, 1)
    side = np.clip(1.2 - (XX / w0) * 1.2 - (YY / h0) * .4, 0, 1)            # warm light from the upper left
    return e * side

def premul_over(dst, rgba):
    a = rgba[..., 3:4]; return dst * (1 - a) + rgba[..., :3] * a

def blur_levels(img, sig):
    return [img] + [cv2.GaussianBlur(img, (0, 0), s) for s in sig]

def tiltshift(img, center, half, maxs):
    lv = blur_levels(img, [maxs * .35, maxs * .7, maxs])
    y = np.arange(H, dtype=np.float32)
    d = np.clip((np.abs(y - center) - half) / (H * .32), 0, 1) ** 1.2 * 3   # 0..3 level index
    out = np.zeros_like(img)
    for i in range(4):
        w = np.clip(1 - np.abs(d - i), 0, 1)[:, None, None]
        out += lv[i] * w
    return out

def grade(img):
    img = np.clip(img, 0, 1)
    l = img @ np.float32([.114, .587, .299])
    img = l[..., None] + (img - l[..., None]) * 1.08
    img = img * np.float32([.96, 1.0, 1.05])                                   # warm (BGR)
    img = img * (1 + .12) / (1 + .12 * img / (img + .6))
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    v = 1 - .28 * ss((np.sqrt(((xx / W - .5) * .9) ** 2 + (yy / H - .48) ** 2) - .32) / .45)
    return np.clip(img * v[..., None], 0, 1)
VIG = None

# ---------------------------------------------------------------- render
def frame(t):
    P = params(t)
    face = face_pass(char, P['blink'], P['gx'], P['gy'], P['smile'])
    mx, my = body_maps(t, P)
    ch = cv2.remap(face, mx, my, cv2.INTER_CUBIC, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    ch[..., 3] = np.clip(ch[..., 3], 0, 1)
    # light: dapple on the ground plate, softer on Hind, warm rim on her silhouette
    dp = dapple(t)[..., None]
    b = bg * (.9 + .2 * dp)
    # background crowd: tiny sway of the blurred students
    sway = np.zeros_like(XX)
    sway += 1.6 * math.sin(2 * math.pi * .7 * t) * ss((300 - XX) / 80) * ss((YY - 320) / 60) * ss((800 - YY) / 60)
    sway += 1.4 * math.sin(2 * math.pi * .6 * t + 2) * ss((XX - 850) / 80) * ss((YY - 340) / 60) * ss((820 - YY) / 60)
    b = cv2.remap(b, XX - sway, YY, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    rgb = ch[..., :3] * (.96 + .08 * dp)
    r = rim(ch[..., 3])[..., None]
    rgb = rgb + r * np.float32([.18, .42, .62]) * (.7 + .3 * math.sin(t * 1.7))
    ch = np.dstack([rgb, ch[..., 3]])
    # rack focus: Hind starts soft, the lens finds her by ~1.1 s
    rf = 1 - ss(seg(t, .25, 1.1))
    if rf > .01:
        k = 6 * rf
        pm = np.dstack([ch[..., :3] * ch[..., 3:4], ch[..., 3:4]])
        pm = cv2.GaussianBlur(pm, (0, 0), k)
        ch = np.dstack([pm[..., :3] / np.maximum(pm[..., 3:4], 1e-4), pm[..., 3:4]])
    s, c = cam(t)
    M = affine(s, c)
    Mb = affine(S0 + (s - S0) * .5, C0 + (c - C0) * .5)
    bo = cv2.warpAffine(b, Mb, (W, H), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REFLECT)
    bo = cv2.GaussianBlur(bo, (0, 0), 1.2 + 1.2 * (1 - rf))                  # background stays a step softer than her
    co = cv2.warpAffine(ch, M, (W, H), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    co[..., 3] = np.clip(co[..., 3], 0, 1)
    # gentle sharpening of the upscaled character
    shp = co[..., :3] + .35 * (co[..., :3] - cv2.GaussianBlur(co[..., :3], (0, 0), 1.6))
    img = premul_over(bo, np.dstack([np.clip(shp, 0, 1), co[..., 3:4]]))
    # near layer: out-of-focus flowers entering the lower-left corner (parallax 1.8x)
    fs = s * 1.9
    fc = np.array([fl_w * .62, fl_h * .55]) + (c - C0) * 1.8 * np.array([1, 1]) / 1.9
    Mf = np.float32([[fs, 0, -40 - fs * (fc[0] - fl_w * .62) + 2 * math.sin(t * 1.4)], [0, fs, H - fl_h * fs + 120 - fs * (fc[1] - fl_h * .55)]])
    fo = cv2.warpAffine(flowers, Mf, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    pm = np.dstack([fo[..., :3] * fo[..., 3:4], fo[..., 3:4]])
    pm = cv2.GaussianBlur(pm, (0, 0), 16)
    img = img * (1 - pm[..., 3:4]) + pm[..., :3]
    # warm sun bloom from the upper left, breathing slowly
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    glow = np.exp(-(((xx + 120) / 700) ** 2 + ((yy + 150) / 800) ** 2)) * (.16 + .04 * math.sin(t * 1.1))
    img = 1 - (1 - img) * (1 - glow[..., None] * np.float32([.45, .75, 1.0]))
    # tilt-shift band on her face/hands; the top and bottom of the frame melt away
    fy = M[1, 0] * 0 + M[1, 1] * 520 + M[1, 2]
    img = tiltshift(img, fy, H * .27, 9)
    return grade(img)

def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    out = args[0] if args else A('output/Miniature_Test.mp4')
    stills = '--stills' in sys.argv
    os.makedirs(os.path.dirname(out), exist_ok=True)
    if stills:
        for t in [1.08, 1.16, 2.9]:
            cv2.imwrite(A(f'work/f_{t:.2f}.jpg'), (frame(t) * 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 92]); print('still', t, flush=True)
        return
    ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                           '-vf', 'noise=alls=3:allf=t', '-c:v', 'libx264', '-preset', 'slow', '-crf', '15', '-pix_fmt', 'yuv420p', '-r', str(FPS),
                           '-movflags', '+faststart', '-an', out], stdin=subprocess.PIPE)
    for i in range(N):
        f = frame(i / FPS)
        ff.stdin.write((f * 255 + .5).astype(np.uint8).tobytes())
        if i % 15 == 0: print(f'frame {i}/{N}', flush=True)
    ff.stdin.close(); ff.wait()
    print(out)

if __name__ == '__main__':
    main()

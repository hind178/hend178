"""Core 2D drawing toolkit (Skia raster) for Episode 03.

Everything is drawn as vector/raster paint strokes on a 1080x1920 canvas.
Hand-drawn feel comes from: animating "on twos" (pose updates every 2nd
frame), line boil (outline jitter re-seeded every 2 frames), soft painted
gradients, brush-blob backgrounds and a paper-grain pass in post.
"""
import math, random
import numpy as np
import skia

W, H = 1080, 1920
FPS = 30


# ---------------------------------------------------------------- colour
def hexc(h, a=1.0):
    h = h.lstrip('#')
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return skia.Color(r, g, b, int(max(0, min(1, a)) * 255))


def rgb(c):
    if isinstance(c, str):
        h = c.lstrip('#')
        return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))
    return c


def mix(c1, c2, t):
    a, b = rgb(c1), rgb(c2)
    t = max(0.0, min(1.0, t))
    return '#%02x%02x%02x' % tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def col(c, a=1.0):
    if isinstance(c, str):
        return hexc(c, a)
    r, g, b = c[:3]
    return skia.Color(int(r), int(g), int(b), int(max(0, min(1, a)) * 255))


# ---------------------------------------------------------------- easing
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def lerp(a, b, t):
    return a + (b - a) * t


def smooth(t):
    t = clamp(t)
    return t * t * (3 - 2 * t)


def ease_io(t):
    t = clamp(t)
    return 0.5 - 0.5 * math.cos(math.pi * t)


def ease_out(t):
    t = clamp(t)
    return 1 - (1 - t) ** 3


def ease_in(t):
    t = clamp(t)
    return t ** 3


def seg(t, a, b):
    """0..1 progress of t inside [a,b]."""
    if b <= a:
        return 1.0 if t >= b else 0.0
    return clamp((t - a) / (b - a))


def on_twos(t):
    """Quantise local time to 15 drawings per second (animation on twos)."""
    return math.floor(t * 15) / 15.0


# ---------------------------------------------------------------- paints
def P(c, a=1.0, blur=0.0, stroke=0.0, cap=True, aa=True):
    p = skia.Paint(AntiAlias=aa, Color=col(c, a))
    if stroke:
        p.setStyle(skia.Paint.kStroke_Style)
        p.setStrokeWidth(stroke)
        if cap:
            p.setStrokeCap(skia.Paint.kRound_Cap)
            p.setStrokeJoin(skia.Paint.kRound_Join)
    if blur > 0:
        p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    return p


def lin(p0, p1, colors, pos=None, alpha=1.0):
    cs = [col(c, alpha) if not isinstance(c, tuple) or len(c) != 2 else col(c[0], c[1] * alpha) for c in colors]
    sh = skia.GradientShader.MakeLinear([skia.Point(*p0), skia.Point(*p1)], cs, pos)
    p = skia.Paint(AntiAlias=True)
    p.setShader(sh)
    return p


def rad(c, r, colors, pos=None, alpha=1.0):
    cs = [col(c_, alpha) if not isinstance(c_, tuple) or len(c_) != 2 else col(c_[0], c_[1] * alpha) for c_ in colors]
    sh = skia.GradientShader.MakeRadial(skia.Point(*c), max(1, r), cs, pos)
    p = skia.Paint(AntiAlias=True)
    p.setShader(sh)
    return p


def add_blend(p):
    p.setBlendMode(skia.BlendMode.kPlus)
    return p


def screen(p):
    p.setBlendMode(skia.BlendMode.kScreen)
    return p


def multiply(p):
    p.setBlendMode(skia.BlendMode.kMultiply)
    return p


# ---------------------------------------------------------------- paths
def smooth_path(pts, closed=True, tension=0.5):
    """Catmull-Rom through points -> cubic Bezier skia.Path."""
    path = skia.Path()
    n = len(pts)
    if n < 2:
        return path
    path.moveTo(*pts[0])
    rng = range(n if closed else n - 1)
    for i in rng:
        p0 = pts[(i - 1) % n] if (closed or i > 0) else pts[i]
        p1 = pts[i]
        p2 = pts[(i + 1) % n]
        p3 = pts[(i + 2) % n] if (closed or i + 2 < n) else p2
        k = tension / 3.0 * 2
        c1 = (p1[0] + (p2[0] - p0[0]) * k / 2, p1[1] + (p2[1] - p0[1]) * k / 2)
        c2 = (p2[0] - (p3[0] - p1[0]) * k / 2, p2[1] - (p3[1] - p1[1]) * k / 2)
        path.cubicTo(*c1, *c2, *p2)
    if closed:
        path.close()
    return path


def poly(pts, closed=True):
    path = skia.Path()
    path.moveTo(*pts[0])
    for p in pts[1:]:
        path.lineTo(*p)
    if closed:
        path.close()
    return path


def boil(pts, amt, seed):
    """Line boil: re-jitter control points per drawing (on twos)."""
    r = random.Random(seed)
    return [(x + r.uniform(-amt, amt), y + r.uniform(-amt, amt)) for x, y in pts]


def ellipse_pts(cx, cy, rx, ry, n=24, rot=0.0):
    out = []
    cr, sr = math.cos(rot), math.sin(rot)
    for i in range(n):
        a = 2 * math.pi * i / n
        x, y = rx * math.cos(a), ry * math.sin(a)
        out.append((cx + x * cr - y * sr, cy + x * sr + y * cr))
    return out


def stroke_taper(c, pts, w0, w1, color, a=1.0, blur=0):
    """Variable width ink stroke (brush-pen look) along a polyline."""
    if len(pts) < 2:
        return
    n = len(pts)
    left, right = [], []
    for i in range(n):
        x, y = pts[i]
        if i == 0:
            dx, dy = pts[1][0] - x, pts[1][1] - y
        elif i == n - 1:
            dx, dy = x - pts[i - 1][0], y - pts[i - 1][1]
        else:
            dx, dy = pts[i + 1][0] - pts[i - 1][0], pts[i + 1][1] - pts[i - 1][1]
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        t = i / (n - 1)
        w = lerp(w0, w1, t) * (0.55 + 0.45 * math.sin(math.pi * t)) if n > 2 else lerp(w0, w1, t)
        left.append((x + nx * w / 2, y + ny * w / 2))
        right.append((x - nx * w / 2, y - ny * w / 2))
    c.drawPath(smooth_path(left + right[::-1], closed=True, tension=0.4), P(color, a, blur))


def bezier_pts(p0, p1, p2, n=12):
    out = []
    for i in range(n):
        t = i / (n - 1)
        x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0]
        y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]
        out.append((x, y))
    return out


# ---------------------------------------------------------------- surfaces
def new_surface(w=W, h=H):
    return skia.Surface(w, h)


def snapshot(surf):
    return surf.makeImageSnapshot()


def to_np(img):
    return img.toarray(colorType=skia.kRGBA_8888_ColorType)


def from_np(arr):
    return skia.Image.fromarray(np.ascontiguousarray(arr), colorType=skia.kRGBA_8888_ColorType)


def draw_img(c, img, x=0, y=0, a=1.0, blur=0, w=None, h=None, blend=None):
    p = skia.Paint(AntiAlias=True)
    p.setAlphaf(clamp(a))
    if blur > 0:
        p.setImageFilter(skia.ImageFilters.Blur(blur, blur))
    if blend is not None:
        p.setBlendMode(blend)
    if w is None:
        c.drawImage(img, x, y, skia.SamplingOptions(skia.FilterMode.kLinear), p)
    else:
        c.drawImageRect(img, skia.Rect.MakeXYWH(x, y, w, h), skia.SamplingOptions(skia.FilterMode.kLinear), p)


class Layer:
    """Offscreen layer helper: with Layer(c, alpha, blur) as c2: ..."""

    def __init__(self, c, alpha=1.0, blur=0.0, blend=None):
        self.c, self.alpha, self.blur, self.blend = c, alpha, blur, blend

    def __enter__(self):
        p = skia.Paint()
        p.setAlphaf(clamp(self.alpha))
        if self.blur > 0:
            p.setImageFilter(skia.ImageFilters.Blur(self.blur, self.blur))
        if self.blend is not None:
            p.setBlendMode(self.blend)
        self.c.saveLayer(None, p)
        return self.c

    def __exit__(self, *a):
        self.c.restore()


# ---------------------------------------------------------------- textures
_rng_np = np.random.default_rng(7)


def value_noise(w, h, scale, seed=0, octaves=4):
    rng = np.random.default_rng(seed)
    out = np.zeros((h, w), np.float32)
    amp, tot = 1.0, 0.0
    for o in range(octaves):
        s = max(2, int(scale / (2 ** o)))
        gw, gh = w // s + 3, h // s + 3
        g = rng.random((gh, gw)).astype(np.float32)
        import cv2
        up = cv2.resize(g, (gw * s, gh * s), interpolation=cv2.INTER_CUBIC)[:h, :w]
        out += up * amp
        tot += amp
        amp *= 0.5
    return out / tot


_PAPER = None


def paper_grain():
    global _PAPER
    if _PAPER is None:
        n1 = value_noise(W, H, 6, 11, 2)
        n2 = value_noise(W, H, 180, 12, 3)
        fib = _rng_np.random((H, W)).astype(np.float32)
        _PAPER = (0.55 * n1 + 0.30 * n2 + 0.15 * fib).astype(np.float32)
    return _PAPER


_VIG = None


def vignette():
    global _VIG
    if _VIG is None:
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        dx = (xx - W / 2) / (W * 0.62)
        dy = (yy - H / 2) / (H * 0.60)
        d = np.sqrt(dx * dx + dy * dy)
        _VIG = np.clip(1.0 - 0.55 * np.clip(d - 0.45, 0, 1) ** 1.6, 0, 1).astype(np.float32)
    return _VIG


def grade(arr, frame, tint=(1.0, 1.0, 1.0), sat=1.0, contrast=1.0, lift=0.0, grain=0.06, vig=1.0, bloom=0.0):
    """Post: colour grade + bloom + vignette + animated paper grain."""
    import cv2
    a = arr[..., :3].astype(np.float32) / 255.0
    if bloom > 0:
        small = cv2.resize(a, (W // 6, H // 6), interpolation=cv2.INTER_AREA)
        br = np.clip(small - 0.62, 0, 1) * 2.2
        br = cv2.GaussianBlur(br, (0, 0), 9)
        br = cv2.resize(br, (W, H), interpolation=cv2.INTER_LINEAR)
        a = 1 - (1 - a) * (1 - np.clip(br * bloom, 0, 1))
    if sat != 1.0:
        g = a.mean(axis=2, keepdims=True)
        a = g + (a - g) * sat
    if contrast != 1.0:
        a = (a - 0.5) * contrast + 0.5
    a = a * np.array(tint, np.float32) + lift
    if vig:
        v = vignette()
        a *= (1 - vig + vig * v)[..., None]
    if grain:
        pg = paper_grain()
        sh = (frame // 2) % 4
        pg = np.roll(pg, sh * 37, axis=1)
        a *= (1 - grain) + grain * 2 * pg[..., None]
    a = np.clip(a, 0, 1)
    out = np.empty((H, W, 3), np.uint8)
    out[:] = (a * 255 + 0.5).astype(np.uint8)
    return out

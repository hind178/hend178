# Original sound design & score for Episode 01 (procedurally synthesised — no third-party audio).
# Produces build/bed.wav (music + ambience + SFX) and output mix with the untouched narration.
import json, subprocess, numpy as np, wave, os
SR = 44100
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DUR = 115.9575
N = int(DUR * SR) + 1
rng = np.random.default_rng(7)
t = np.arange(N) / SR

def env_lin(keys):
    """piecewise-linear gain envelope from [(time, gain), ...]"""
    ks = sorted(keys)
    return np.interp(t, [k[0] for k in ks], [k[1] for k in ks])

def lowpass(x, fc):
    a = np.exp(-2 * np.pi * fc / SR); y = np.empty_like(x); acc = 0.0
    # vectorised one-pole via lfilter-like recursion using cumulative trick (chunked for speed)
    from math import isfinite
    out = np.zeros_like(x); s = 0.0
    for i in range(0, len(x), 4096):
        seg = x[i:i + 4096]; o = np.empty_like(seg)
        for j, v in enumerate(seg):
            s = a * s + (1 - a) * v; o[j] = s
        out[i:i + 4096] = o
    return out

def fft_filter(x, lo, hi):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    m = ((f >= lo) & (f <= hi)).astype(float)
    # soft edges
    m = movavg(m, 64)
    return np.fft.irfft(X * m, n=len(x))

def pink(n):
    w = rng.standard_normal(n); X = np.fft.rfft(w); f = np.fft.rfftfreq(n, 1 / SR); f[0] = 1
    return np.fft.irfft(X / np.sqrt(f), n=n)

def movavg(x, k):
    c = np.cumsum(np.concatenate([[0.0], x]))
    y = (c[k:] - c[:-k]) / k
    pad = k // 2
    return np.concatenate([np.full(pad, y[0]), y, np.full(len(x) - len(y) - pad, y[-1])])

def norm(x):
    return x / (np.max(np.abs(x)) + 1e-9)

# ---------------------------------------------------------------- MUSIC
def piano(freq, dur, vel=0.5):
    n = int(dur * SR); tt = np.arange(n) / SR
    tone = np.zeros(n)
    for h, a in [(1, 1), (2, 0.45), (3, 0.22), (4, 0.12), (5, 0.06), (6, 0.03)]:
        tone += a * np.sin(2 * np.pi * freq * h * tt * (1 + 0.0004 * h * h)) * np.exp(-tt * (1.3 + h * 0.9))
    att = np.minimum(1, tt / 0.006)
    return tone * att * vel

def pad(freqs, dur, vel=0.3):
    n = int(dur * SR); tt = np.arange(n) / SR
    x = np.zeros(n)
    for fq in freqs:
        for d in (-0.15, 0.0, 0.17):
            x += np.sin(2 * np.pi * (fq + d) * tt + rng.random() * 6) * 0.33
            x += 0.18 * np.sin(2 * np.pi * (fq * 2 + d) * tt)
    a = np.minimum(1, tt / 1.2) * np.minimum(1, (dur - tt) / 1.2)
    return x * a * vel / len(freqs)

def place(buf, sig, at):
    i = int(at * SR); j = min(len(buf), i + len(sig))
    if i < len(buf): buf[i:j] += sig[: j - i]

note = lambda m: 440 * 2 ** ((m - 69) / 12)
music = np.zeros(N)
bpm = 72; beat = 60 / bpm
# warm nostalgic progression: Am - F - C - G (and Dm - Bb for suspense)
prog = [[57, 60, 64], [53, 57, 60], [48, 55, 64], [55, 59, 62]]
bar = beat * 4
tcur = 0.4
i = 0
while tcur < 105.8:
    ch = prog[i % 4]
    sparse = tcur < 15.0
    warm = (38.0 <= tcur < 57.5) or (79.0 <= tcur < 105.5)
    # left-hand root
    place(music, piano(note(ch[0] - 12), 3.5, 0.38), tcur)
    # arpeggio
    pattern = [0, 1, 2, 1, 2, 1, 0, 2] if not sparse else [0, 2, 1]
    step = bar / len(pattern)
    for k, idx in enumerate(pattern):
        vel = 0.22 if sparse else 0.26
        place(music, piano(note(ch[idx] + 12), 2.2, vel + (0.06 if warm else 0)), tcur + k * step + rng.random() * 0.01)
    # melody notes on top in warm section
    if warm:
        mel = [76, 74, 72, 74][i % 4]
        place(music, piano(note(mel), 3.0, 0.2), tcur + beat * 0.02)
        place(music, pad([note(n) for n in ch], bar + 1.0, 0.28), tcur)
    elif tcur >= 14.0:
        place(music, pad([note(n) for n in ch], bar + 1.0, 0.13), tcur)
    tcur += bar; i += 1
# suspense (100.3 → end): low drone + tremolo on Dm(add b6) + heartbeat-like pulse
sus = np.zeros(N)
for fq in [note(38), note(45), note(50), note(53), note(58)]:
    place(sus, pad([fq], 10.5, 0.5), 105.6)
trem = 0.6 + 0.4 * np.sin(2 * np.pi * 5.5 * t)
sus *= trem
for k in range(8):
    place(sus, piano(note(38), 0.8, 0.5) * 0.8, 108.5 + k * 0.62)
# final suspended note at the cliffhanger
place(sus, piano(note(46), 2.5, 0.7) + piano(note(53), 2.5, 0.5) + piano(note(56), 2.5, 0.45), 113.4)
music_env = env_lin([(0, 0), (0.5, 0.8), (15, 1.0), (38, 1.15), (57.5, 1.0), (79, 1.2), (104.5, 1.1), (106.0, 0.0), (116, 0.0)])
music = music * music_env + sus * env_lin([(0, 0), (105.4, 0), (106.2, 1.0), (116, 1.0)])
# simple room reverb (multi-tap feedback delays)
def reverb(x, mix=0.25):
    y = x.copy()
    for d, g in [(0.031, 0.5), (0.047, 0.45), (0.071, 0.4), (0.113, 0.33), (0.173, 0.26), (0.241, 0.2), (0.367, 0.14)]:
        k = int(d * SR); y[k:] += x[:-k] * g
    return x * (1 - mix) + norm(y) * np.max(np.abs(x)) * mix
music = reverb(music, 0.35)

# ---------------------------------------------------------------- AMBIENCES
def murmur(level=1.0, seed=1):
    r = np.random.default_rng(seed)
    base = fft_filter(pink(N), 250, 2600)
    # syllabic modulation of several talkers
    m = np.zeros(N)
    for k in range(6):
        rate = 2.5 + r.random() * 3
        m += np.clip(np.sin(2 * np.pi * rate * t + r.random() * 6) + 0.3 * np.sin(2 * np.pi * 0.3 * t + k), 0, None)
    return norm(base * (0.4 + m / 6)) * level

crowd = murmur(1.0, 3)
indoor = fft_filter(murmur(1.0, 5), 200, 1600)
room = norm(fft_filter(pink(N), 60, 900))
engine = norm(fft_filter(pink(N), 25, 160) + 0.4 * np.sin(2 * np.pi * 42 * t) * (1 + 0.2 * np.sin(2 * np.pi * 0.5 * t)))
road = norm(fft_filter(pink(N), 80, 1400))
wind = norm(fft_filter(pink(N), 150, 900) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.15 * t)))

def birds():
    b = np.zeros(N); r = np.random.default_rng(9)
    for at in np.arange(0.8, 100, 1.7):
        at += r.random()
        n = int(0.09 * SR); tt = np.arange(n) / SR
        f0 = 2600 + r.random() * 1500
        chirp = np.sin(2 * np.pi * (f0 * tt + 9000 * tt * tt * (1 if r.random() > 0.5 else -1))) * np.hanning(n)
        for rep in range(1 + int(r.random() * 3)):
            place(b, chirp * 0.6, at + rep * 0.12)
    return b
bird = birds()

# scene-based gains: (start, end, crowd, indoor, room, engine, road, wind, birds)
SC = [
    (0.0, 4.5, 0, 0.09, 0.03, 0, 0, 0, 0), (4.5, 9.3, 0, 0.03, 0.04, 0, 0, 0, 0), (9.3, 41.0, 0, 0.09, 0.03, 0, 0, 0, 0),
    (41.0, 45.1, 0, 0.03, 0.04, 0, 0, 0, 0), (45.1, 54.0, 0, 0, 0.04, 0, 0, 0, 0.03), (54.0, 57.9, 0, 0, 0.03, 0, 0, 0, 0),
    (57.9, 79.0, 0, 0, 0.035, 0, 0, 0, 0.03), (79.0, 82.6, 0.06, 0, 0, 0.03, 0, 0, 0), (82.6, 86.5, 0, 0.13, 0.03, 0, 0, 0, 0),
    (86.5, 92.5, 0, 0.09, 0.03, 0, 0, 0, 0), (92.5, 105.9, 0.07, 0, 0, 0, 0, 0.02, 0), (105.9, 112.3, 0.14, 0, 0, 0, 0, 0.03, 0.04),
    (112.3, 116.0, 0.03, 0, 0, 0, 0, 0.06, 0),
]
def lane(idx):
    keys = []
    for s in SC:
        if s[2 + idx] is None: continue
    g = np.zeros(N)
    for s in SC:
        a, b = int(s[0] * SR), int(s[1] * SR); g[a:b] = s[2 + idx]
    # 0.35 s crossfades between scenes
    return movavg(g, int(0.35 * SR))
amb = crowd * lane(0) + indoor * lane(1) + room * lane(2) + engine * lane(3) + road * lane(4) + wind * lane(5) + bird * lane(6)

# ---------------------------------------------------------------- SFX
sfx = np.zeros(N)
def step(vel=0.3):
    n = int(0.07 * SR); tt = np.arange(n) / SR
    return fft_filter(np.pad(rng.standard_normal(n) * np.exp(-tt * 70), (0, 2048)), 120, 2500)[:n] * vel
walks = [(7.2, 9.3, 0.95, 0.09), (11.2, 14.6, 0.9, 0.05), (41.0, 45.1, 0.85, 0.1), (58.5, 60.3, 0.95, 0.09), (63.5, 65.0, 1.1, 0.09),
         (79.0, 82.6, 0.95, 0.08), (92.5, 95.4, 0.85, 0.07), (105.9, 108.0, 0.9, 0.05)]
for a, b, sp, v in walks:
    k = a
    while k < b:
        place(sfx, step(v), k); k += 1 / (2 * sp)
lug = norm(fft_filter(pink(int(1.8 * SR)), 300, 3000)) * 0.05
lug *= np.minimum(1, np.arange(len(lug)) / (0.2 * SR))
place(sfx, lug, 11.3); place(sfx, lug * 0.8, 0.3)
def hiss(dur, vel):
    n = int(dur * SR); tt = np.arange(n) / SR
    return fft_filter(rng.standard_normal(n), 1800, 9000) * np.exp(-tt * 3) * np.minimum(1, tt / 0.03) * vel
def thud(vel):
    n = int(0.25 * SR); tt = np.arange(n) / SR
    return fft_filter(np.pad(rng.standard_normal(n) * np.exp(-tt * 25), (0, 4096)), 40, 400)[:n] * vel
def whoosh(dur, vel):
    n = int(dur * SR); tt = np.arange(n) / SR
    return fft_filter(rng.standard_normal(n), 300, 4000) * np.sin(np.pi * tt / dur) ** 2 * vel
# doors (click + creak), bed scrape, mattress thump, fabric rustle
for at in (58.1, 63.2):
    place(sfx, thud(0.25), at); place(sfx, hiss(0.5, 0.03), at + 0.05)
scrape = fft_filter(rng.standard_normal(int(1.4 * SR)), 150, 1200) * 0.06
place(sfx, scrape * np.hanning(len(scrape)), 45.3)
place(sfx, thud(0.45), 48.35); place(sfx, whoosh(0.8, 0.05), 47.3)
place(sfx, whoosh(0.9, 0.06), 60.3)
for at in (51.9, 54.2, 61.6): place(sfx, whoosh(0.5, 0.04), at)
place(sfx, whoosh(1.4, 0.1), 112.3)
# reception desk bell
n = int(1.6 * SR); tt = np.arange(n) / SR
bell = (np.sin(2 * np.pi * 2093 * tt) + 0.5 * np.sin(2 * np.pi * 5230 * tt) + 0.3 * np.sin(2 * np.pi * 3140 * tt)) * np.exp(-tt * 2.6) * 0.06
place(sfx, bell, 1.0)
# ---------------------------------------------------------------- MIX
def read_narration():
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', os.path.join(ROOT, 'assets/audio/narration.mp3'), '-f', 's16le', '-ac', '1', '-ar', str(SR), '-'], capture_output=True).stdout
    x = np.frombuffer(raw, np.int16).astype(np.float64) / 32768
    out = np.zeros(N); out[:min(N, len(x))] = x[:N]; return out
voice = read_narration()
# duck the bed under speech (voice itself untouched)
k = int(0.05 * SR)
vrms = np.sqrt(np.maximum(movavg(voice ** 2, k), 0))
duck = 1 - 0.45 * np.clip(vrms / 0.05, 0, 1)
duck = movavg(duck, int(0.25 * SR))
music_n = norm(music) * 0.16
bed = (music_n + amb * 0.9 + sfx) * duck
mix = voice + bed
peak = np.max(np.abs(mix))
if peak > 0.98:
    bed *= (0.98 - np.max(np.abs(voice))) / max(1e-6, np.max(np.abs(bed)))
    mix = voice + bed
def write(path, x):
    st = np.stack([x, x], axis=1)
    with wave.open(path, 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(st, -1, 1) * 32767).astype(np.int16).tobytes())
os.makedirs(os.path.join(ROOT, 'build'), exist_ok=True)
write(os.path.join(ROOT, 'build', 'mix.wav'), mix)
write(os.path.join(ROOT, 'build', 'bed.wav'), bed)
print('mix written; peak', float(np.max(np.abs(mix))), 'voice peak', float(np.max(np.abs(voice))))

"""Procedural sound design + score for Episode 03, mixed under the narration.

All sounds are synthesised (no third-party samples): rain, thunder, water,
metal creak, train rhythm, whistle, clock bell, wind, birdsong, tea pouring,
piano and string pads.  The bed is ducked whenever the narrator speaks.
python3 audio.py out_mix.wav out_bed.wav
"""
import sys, os, subprocess
import numpy as np
from scipy import signal

SR = 44100
DUR = 161.0
N = int(SR * DUR)
rng = np.random.default_rng(3)
HERE = os.path.dirname(os.path.abspath(__file__))
VO = os.path.join(os.path.dirname(HERE), 'assets', 'audio', 'voiceover.mp3')


def T(t):
    return int(t * SR)


def env_ar(n, a, r):
    e = np.ones(n)
    na, nr = int(a * SR), int(r * SR)
    if na:
        e[:na] = np.linspace(0, 1, na)
    if nr:
        e[-nr:] *= np.linspace(1, 0, nr)
    return e


def lp(x, f, o=2):
    b, a = signal.butter(o, f / (SR / 2), 'low')
    return signal.lfilter(b, a, x)


def hp(x, f, o=2):
    b, a = signal.butter(o, f / (SR / 2), 'high')
    return signal.lfilter(b, a, x)


def bp(x, f1, f2, o=2):
    b, a = signal.butter(o, [f1 / (SR / 2), f2 / (SR / 2)], 'band')
    return signal.lfilter(b, a, x)


def place(buf, x, t, g=1.0):
    i = T(t)
    if i >= len(buf):
        return
    j = min(len(buf), i + len(x))
    buf[i:j] += x[:j - i] * g


def noise(sec):
    return rng.standard_normal(int(sec * SR))


_IR = {}


def reverb(x, size=2.5, wet=0.35):
    if size not in _IR:
        n = int(size * SR)
        ir = rng.standard_normal(n) * np.exp(-np.linspace(0, 7, n))
        ir = lp(ir, 6000)
        _IR[size] = ir / np.sqrt(np.sum(ir ** 2))
    w = signal.fftconvolve(x, _IR[size])[:len(x)]
    return x * (1 - wet) + w * wet


def segment_gain(t0, t1, fi=1.0, fo=1.0):
    g = np.zeros(N)
    a, b = T(t0), T(t1)
    g[a:b] = 1
    nfi, nfo = int(fi * SR), int(fo * SR)
    if nfi:
        g[a:a + nfi] *= np.linspace(0, 1, min(nfi, b - a))[:len(g[a:a + nfi])]
    if nfo:
        g[max(a, b - nfo):b] *= np.linspace(1, 0, b - max(a, b - nfo))
    return g


# ------------------------------------------------------------------ instruments
def note_freq(n):
    names = {'C': -9, 'C#': -8, 'D': -7, 'D#': -6, 'E': -5, 'F': -4, 'F#': -3, 'G': -2, 'G#': -1, 'A': 0, 'A#': 1, 'B': 2}
    p, o = n[:-1], int(n[-1])
    return 440.0 * 2 ** ((names[p] + (o - 4) * 12) / 12)


def piano(n, dur=3.5, vel=0.6):
    f = note_freq(n) if isinstance(n, str) else n
    t = np.arange(int(dur * SR)) / SR
    x = np.zeros_like(t)
    for h in range(1, 9):
        fh = f * h * (1 + 0.0004 * h * h)
        if fh > 12000:
            break
        x += np.sin(2 * np.pi * fh * t) * (0.6 ** (h - 1)) * np.exp(-t * (1.2 + 0.7 * h))
    att = np.minimum(1, t / 0.004)
    hammer = lp(rng.standard_normal(len(t)), 2500) * np.exp(-t * 60) * 0.05
    return (x * att + hammer) * vel * 0.25


def pad(notes, dur, att=2.0, rel=2.5, bright=1800, vol=0.12):
    t = np.arange(int(dur * SR)) / SR
    x = np.zeros_like(t)
    for n in notes:
        f = note_freq(n)
        for d in (-0.12, 0.0, 0.13):
            ph = rng.uniform(0, 1)
            fd = f * 2 ** (d / 12)
            vib = 1 + 0.003 * np.sin(2 * np.pi * 5.2 * t + ph * 6)
            x += signal.sawtooth(2 * np.pi * fd * t * vib + ph * 6) * 0.33
    x = lp(x, bright, 2)
    return x * env_ar(len(t), att, rel) * vol / max(1, len(notes))


def bell(f, dur=4.0, vol=0.4):
    t = np.arange(int(dur * SR)) / SR
    x = np.zeros_like(t)
    for r, a, d in ((0.5, 0.6, 1.2), (1.0, 1.0, 1.6), (1.19, 0.5, 2.2), (1.56, 0.4, 2.8), (2.0, 0.35, 3.5), (2.74, 0.2, 5), (3.76, 0.12, 7)):
        x += np.sin(2 * np.pi * f * r * t) * a * np.exp(-t * d)
    return x * np.minimum(1, t / 0.002) * vol * 0.3


def whistle(dur=3.0, vol=0.4):
    """Old steam whistle: chord of three pipes, breathy, slight pitch bend."""
    t = np.arange(int(dur * SR)) / SR
    bend = 1 - 0.03 * np.exp(-t * 4)
    x = np.zeros_like(t)
    for f in (466.0, 554.0, 698.0):
        for h, a in ((1, 1.0), (2, 0.35), (3, 0.12)):
            x += np.sin(2 * np.pi * f * h * t * bend + 0.2 * np.sin(2 * np.pi * 5 * t)) * a
    breath = bp(rng.standard_normal(len(t)), 400, 3000) * 0.25
    e = env_ar(len(t), 0.25, 1.0)
    return (x * 0.18 + breath) * e * vol


def clack(vol=0.3):
    t = np.arange(int(0.25 * SR)) / SR
    x = bp(rng.standard_normal(len(t)), 150, 1800) * np.exp(-t * 30)
    x += np.sin(2 * np.pi * 95 * t) * np.exp(-t * 22) * 0.6
    return x * vol


def thunder(dur=5.0, vol=0.6):
    n = noise(dur)
    x = lp(n, 160, 2) * 3 + lp(n, 900, 1) * 0.4
    t = np.arange(len(n)) / SR
    e = (1 - np.exp(-t * 18)) * np.exp(-t * 0.9) * (1 + 0.5 * np.sin(2 * np.pi * 0.7 * t + 1))
    crack = hp(noise(dur), 1500) * np.exp(-t * 14) * 0.5
    return (x * e + crack) * vol


def creak(dur=1.2, vol=0.4):
    t = np.arange(int(dur * SR)) / SR
    f = 120 + 60 * np.sin(2 * np.pi * 1.3 * t) + 30 * t
    ph = np.cumsum(f) / SR * 2 * np.pi
    x = signal.sawtooth(ph) * (0.5 + 0.5 * (np.sin(2 * np.pi * 31 * t) > 0.6))
    x = bp(x, 200, 2500)
    return x * env_ar(len(t), 0.05, 0.4) * vol


def crash(dur=3.0, vol=0.8):
    t = np.arange(int(dur * SR)) / SR
    x = lp(noise(dur), 3000) * np.exp(-t * 2.5)
    x += np.sin(2 * np.pi * 55 * t) * np.exp(-t * 4) * 1.5
    x += hp(noise(dur), 2500) * np.exp(-t * 6) * 0.6
    return x * vol


def splash(dur=2.5, vol=0.6):
    t = np.arange(int(dur * SR)) / SR
    x = bp(noise(dur), 300, 5000) * np.exp(-t * 2.2) * (1 - np.exp(-t * 40))
    return x * vol


def bird(vol=0.15):
    d = rng.uniform(0.12, 0.3)
    t = np.arange(int(d * SR)) / SR
    f0 = rng.uniform(2800, 4200)
    f = f0 + rng.uniform(600, 1500) * np.sin(np.pi * t / d) * rng.choice([1, -1])
    x = np.sin(np.cumsum(2 * np.pi * f / SR)) * np.sin(np.pi * t / d) ** 2
    return x * vol


def pour(dur=2.0, vol=0.3):
    t = np.arange(int(dur * SR)) / SR
    n = noise(dur)
    f = 900 + 500 * t / dur
    x = np.zeros_like(t)
    for k in range(0, len(t), 2048):
        seg = n[k:k + 2048]
        ff = f[min(k, len(f) - 1)]
        x[k:k + len(seg)] = bp(seg, ff * 0.7, ff * 1.6)
    gurgle = np.sin(2 * np.pi * (300 + 80 * np.sin(2 * np.pi * 9 * t)) * t) * 0.15
    return (x + gurgle) * env_ar(len(t), 0.1, 0.4) * vol


# ------------------------------------------------------------------ build the bed
def build():
    sfx = np.zeros(N)
    mus = np.zeros(N)
    amb = np.zeros(N)

    # ---- snowy-night wind (1982 scenes)
    wind = lp(noise(DUR), 500, 2)
    wmod = 0.6 + 0.4 * np.sin(2 * np.pi * np.arange(N) / SR * 0.11)
    wind = wind * wmod
    wg = segment_gain(0, 3.95, 0.5, 0.6) + segment_gain(51.5, 54.8, 1.0, 0.5) + segment_gain(64.8, 135.3, 0.6, 1.5)
    amb += wind * wg * 0.18

    # ---- 1962 storm: rain, train rhythm, thunder, creak, crash, water
    rain = hp(noise(DUR), 900, 2) * 0.5 + bp(noise(DUR), 200, 1200) * 0.3
    rg = segment_gain(3.7, 51.6, 0.6, 0.6)
    rg[T(14.2):T(37.6)] *= 0.55  # inside / under water: muffled
    amb += rain * rg * 0.22
    for k in range(int((10.6 - 4.0) / 0.42)):
        tt = 4.0 + k * 0.42
        place(sfx, clack(0.22), tt)
        place(sfx, clack(0.16), tt + 0.12)
    for ts, v in ((6.2, 0.5), (8.4, 0.7), (9.1, 0.5), (10.7, 0.6), (13.0, 0.5), (16.4, 0.45), (22.6, 0.3), (33.2, 0.4), (45.5, 0.4), (49.6, 0.35)):
        place(sfx, thunder(5, v), ts + 0.15)
    place(sfx, creak(1.4, 0.45), 10.55)
    place(sfx, creak(1.0, 0.35), 11.4)
    place(sfx, crash(3.0, 0.55), 11.6)
    place(sfx, splash(3, 0.7), 13.35)
    place(sfx, hp(noise(0.6), 3000) * np.exp(-np.arange(int(0.6 * SR)) / SR * 9) * 0.35, 14.35)  # glass
    water = lp(noise(DUR), 700) * (0.7 + 0.3 * np.sin(2 * np.pi * np.arange(N) / SR * 0.4))
    wtr = segment_gain(13.5, 48.2, 0.5, 1.5)
    amb += water * wtr * 0.30
    # underwater bubbles 21-27
    for k in range(40):
        tt = 21.3 + rng.uniform(0, 5.8)
        d = 0.08
        t = np.arange(int(d * SR)) / SR
        f = rng.uniform(300, 900) * (1 + 3 * t)
        place(sfx, np.sin(np.cumsum(2 * np.pi * f / SR)) * np.exp(-t * 40) * 0.12, tt)
    # riverbank: steady rain
    # ---- score
    # opening: a few slow piano notes + low pad (A minor)
    for tt, n in ((0.3, 'A3'), (1.4, 'E4'), (2.4, 'C5')):
        place(mus, piano(n, 3.5, 0.5), tt)
    place(mus, pad(['A2', 'E3'], 4.2, 1.0, 1.0, 900, 0.10), 0.0)
    # storm: restrained low drone + pulses
    place(mus, pad(['D2', 'A2', 'F3'], 10.5, 1.5, 1.5, 700, 0.16), 3.9)
    for k in range(10):
        place(mus, lp(noise(0.6), 120) * np.exp(-np.arange(int(0.6 * SR)) / SR * 8) * 0.5, 4.0 + k * 1.03)
    place(mus, pad(['D2', 'G#2', 'D3'], 10.5, 1.0, 2.5, 600, 0.17), 14.0)
    place(mus, pad(['C2', 'G2', 'D#3'], 13, 1.5, 2.0, 700, 0.14), 24.5)
    # the crane motif (gentle, hopeful): 37.6 - 48
    for tt, n in ((38.0, 'E5'), (38.8, 'G5'), (39.6, 'A5'), (40.8, 'E5'), (44.6, 'C5'), (45.6, 'B4'), (46.6, 'A4')):
        place(mus, piano(n, 4, 0.45), tt)
    place(mus, pad(['A2', 'E3', 'C4'], 14, 2.0, 3.5, 1400, 0.12), 37.6)
    # 1982 truth: soft piano arpeggios + strings, with space
    prog = [(['A2', 'E3', 'A3', 'C4'], 51.6), (['F2', 'C3', 'A3', 'C4'], 55.0), (['C3', 'G3', 'C4', 'E4'], 59.4), (['G2', 'D3', 'B3', 'D4'], 62.6),
            (['A2', 'E3', 'A3', 'C4'], 66.5), (['F2', 'C3', 'A3', 'F4'], 71.4), (['D3', 'A3', 'D4', 'F4'], 74.8), (['E2', 'B2', 'G#3', 'E4'], 79.6),
            (['A2', 'E3', 'C4', 'A4'], 84.0)]
    for notes, t0 in prog:
        for k, n in enumerate(notes):
            place(mus, piano(n, 4.5, 0.38), t0 + k * 0.55)
        place(mus, pad(notes[:3], 4.6, 1.5, 2.0, 1300, 0.08), t0)
    place(mus, pad(['A3', 'C4', 'E4'], 3.0, 0.4, 2.2, 2000, 0.12), 86.3)  # embrace swell
    # montage spring birds, autumn leaves, tea pour
    for k in range(6):
        place(sfx, bird(0.08), 56.6 + rng.uniform(0, 1.3))
    place(sfx, bp(noise(1.3), 1500, 6000) * 0.05, 58.0)
    place(sfx, pour(1.4, 0.18), 62.9)
    # clock bell at 11:17, tick
    place(sfx, reverb(bell(523.0, 5, 0.6), 3.0, 0.45), 88.75)
    place(sfx, reverb(bell(392.0, 5, 0.5), 3.0, 0.45), 89.75)
    place(sfx, bp(noise(0.05), 2000, 6000) * 0.4, 91.4)
    # silence before the whistle, then the distant whistle
    place(sfx, reverb(lp(whistle(2.8, 0.55), 2500), 3.5, 0.6), 93.65)
    place(sfx, reverb(lp(whistle(2.0, 0.25), 1500), 3.5, 0.7), 97.0)
    # gentle railway rhythm while the train passes
    for k in range(int((131.0 - 98.5) / 0.9)):
        tt = 98.5 + k * 0.9
        g = min(1.0, (tt - 98.5) / 3) * max(0.0, min(1.0, (131.0 - tt) / 3))
        place(sfx, lp(clack(0.12 * g), 900), tt)
        place(sfx, lp(clack(0.09 * g), 900), tt + 0.18)
    # the emotional theme (F major), swelling at the forgiveness
    theme = [('C5', 101.4), ('F5', 102.4), ('E5', 103.4), ('C5', 104.6), ('A4', 106.0), ('G4', 107.2), ('A4', 108.3), ('C5', 109.4),
             ('D5', 110.6), ('C5', 112.0), ('A4', 113.6), ('F4', 115.3), ('G4', 116.6), ('A4', 118.5), ('C5', 120.3), ('F5', 123.3),
             ('E5', 124.6), ('D5', 125.8), ('C5', 127.0), ('A4', 128.4), ('F4', 129.8)]
    for n, tt in theme:
        place(mus, piano(n, 4.0, 0.5), tt)
    chords = [(['F2', 'C3', 'A3'], 98.5, 5), (['D2', 'A2', 'F3'], 103.5, 4), (['A#2', 'F3', 'D4'], 107.5, 4), (['C3', 'G3', 'E4'], 111.5, 4),
              (['F2', 'C3', 'A3'], 115.5, 4), (['D2', 'A2', 'F3'], 118.5, 4.8), (['A#2', 'F3', 'D4', 'F4'], 123.3, 4), (['C3', 'G3', 'E4', 'C5'], 127.3, 3.5),
              (['F2', 'C3', 'A3', 'F4'], 129.0, 6.0)]
    for notes, t0, d in chords:
        place(mus, pad(notes, d + 1.5, 1.5, 2.0, 1800, 0.16), t0)
    # far whistle, fading as the train vanishes
    place(sfx, reverb(lp(whistle(2.0, 0.12), 1200), 3.5, 0.8), 129.6)
    # ---- final scene: warm room, birdsong, tea pouring, delicate piano (C major)
    room = lp(noise(DUR), 300) * 0.05
    amb += room * segment_gain(135.1, 161, 1.0, 3.0)
    for k in range(40):
        place(sfx, bird(0.05 + 0.04 * rng.random()), 135.3 + rng.uniform(0, 21))
    place(sfx, pour(2.2, 0.3), 140.6)
    place(sfx, bp(noise(0.06), 1500, 5000) * 0.15, 142.9)  # cup set down
    endp = [('E5', 135.3), ('G5', 136.3), ('C6', 137.6), ('B5', 139.0), ('G5', 140.4), ('A5', 142.0), ('G5', 143.4), ('E5', 145.2),
            ('D5', 146.8), ('E5', 148.4), ('G5', 150.2), ('C5', 152.2), ('E5', 154.0), ('D5', 155.6), ('C5', 157.4)]
    for n, tt in endp:
        place(mus, piano(n, 4.5, 0.36), tt)
    for notes, t0 in ((['C3', 'G3', 'E4'], 135.2), (['A2', 'E3', 'C4'], 139.2), (['F2', 'C3', 'A3'], 143.2), (['G2', 'D3', 'B3'], 147.2),
                      (['C3', 'G3', 'E4'], 151.2), (['F2', 'C3', 'A3'], 154.2), (['C3', 'G3', 'C4', 'E4'], 157.0)):
        place(mus, pad(notes, 5.0, 1.5, 2.5, 1500, 0.09), t0)

    mus = reverb(mus, 2.8, 0.35)
    sfx = reverb(sfx, 1.2, 0.15)
    bed = mus * 2.4 + sfx * 0.85 + amb * 0.85
    # final fade with picture
    bed *= np.clip((160.6 - np.arange(N) / SR) / 2.2, 0, 1)
    return bed


def load_vo():
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', VO, '-ac', '1', '-ar', str(SR), '-f', 's16le', '-'], capture_output=True, check=True).stdout
    v = np.frombuffer(raw, np.int16).astype(np.float64) / 32768
    out = np.zeros(N)
    out[:min(N, len(v))] = v[:N]
    return out


def main(mix_path, bed_path):
    bed = build()
    vo = load_vo()
    # ducking: narration envelope (fast attack, slow release)
    e = np.abs(vo)
    e = lp(e, 4, 1)
    e = np.clip(e / (np.percentile(e[e > 1e-4], 90) + 1e-9), 0, 1)
    duck = 1 - 0.55 * e
    # keep the bed clearly below the voice: target bed RMS ~ 18 dB under the VO RMS
    vr = np.sqrt(np.mean(vo[vo != 0] ** 2))
    br = np.sqrt(np.mean(bed ** 2))
    bed = bed / br * vr * 10 ** (-17 / 20)
    bedd = bed * duck
    mix = vo + bedd
    mix = mix / np.max(np.abs(mix)) * 0.89
    import scipy.io.wavfile as wf
    wf.write(mix_path, SR, (np.stack([mix, mix], 1) * 32767).astype(np.int16))
    wf.write(bed_path, SR, (np.stack([bedd, bedd], 1) / np.max(np.abs(bedd)) * 0.7 * 32767).astype(np.int16))
    print('VO rms dB %.1f  bed rms dB %.1f' % (20 * np.log10(vr), 20 * np.log10(np.sqrt(np.mean(bedd ** 2)))))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])

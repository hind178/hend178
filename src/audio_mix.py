"""Procedural score + ambience + SFX under the UNCHANGED master narration.

Everything is synthesised (no downloaded samples): soft felt-piano, warm pad,
neighbourhood ambience (birds, distant traffic, room tone, dusk crickets),
footsteps, car passes, brakes, crowd, ambulance siren, door, ball, small thuds.
Narration stays dominant: the bed is side-chain ducked by the voice envelope.
python audio_mix.py  ->  episode_01/audio/mix.wav"""
import os, sys, math
import numpy as np
import soundfile as sf
from scipy import signal
sys.path.insert(0, os.path.dirname(__file__))
import shotlist as SL

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
AUD = os.path.join(ROOT, 'episode_01', 'audio')
SR = 48000
rng = np.random.default_rng(1)


def load_narr():
    import subprocess
    tmp = os.path.join(AUD, 'narr48k.wav')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', os.path.join(AUD, 'narration.mp3'), '-ac', '1', '-ar', str(SR), tmp], check=True)
    x, _ = sf.read(tmp)
    return x


def T(t):
    return int(t * SR)


def bp(x, lo, hi, order=2):
    sos = signal.butter(order, [lo, hi], 'bandpass', fs=SR, output='sos')
    return signal.sosfilt(sos, x)


def lp(x, f, order=2):
    return signal.sosfilt(signal.butter(order, f, 'lowpass', fs=SR, output='sos'), x)


def hp(x, f, order=2):
    return signal.sosfilt(signal.butter(order, f, 'highpass', fs=SR, output='sos'), x)


def env_adsr(n, a=0.01, r=0.3):
    e = np.ones(n)
    na, nr = min(n, T(a)), min(n, T(r))
    e[:na] = np.linspace(0, 1, na)
    if nr:
        e[-nr:] *= np.linspace(1, 0, nr)
    return e


def db(x):
    return 10 ** (x / 20)


class Track:
    def __init__(self, n):
        self.x = np.zeros((n, 2))

    def add(self, t, sig, gain_db=0.0, pan=0.0):
        i = T(t)
        if i >= len(self.x):
            return
        sig = sig[:len(self.x) - i] * db(gain_db)
        l, r = math.cos((pan + 1) * math.pi / 4), math.sin((pan + 1) * math.pi / 4)
        self.x[i:i + len(sig), 0] += sig * l * 1.414
        self.x[i:i + len(sig), 1] += sig * r * 1.414


# ------------------------------------------------------------------ instruments
def piano(freq, dur, vel=0.6):
    n = T(dur + 1.8)
    t = np.arange(n) / SR
    s = np.zeros(n)
    for k, amp in enumerate((1.0, 0.45, 0.22, 0.12, 0.06, 0.03), 1):
        f = freq * k * math.sqrt(1 + 0.0004 * k * k)
        decay = 1.6 + 0.9 * k
        s += amp * np.sin(2 * np.pi * f * t) * np.exp(-t * decay * (freq / 440) ** 0.3)
    hammer = lp(rng.normal(0, 1, n), 2500) * np.exp(-t * 60) * 0.08
    s = (s + hammer) * env_adsr(n, 0.004, 0.6)
    rel = np.ones(n); cut = T(dur)
    rel[cut:] = np.exp(-(np.arange(n - cut) / SR) * 4)
    return lp(s * rel * vel, 3200)


def pad(freqs, dur, bright=900):
    n = T(dur)
    t = np.arange(n) / SR
    s = np.zeros(n)
    for f in freqs:
        for det in (-0.12, 0.0, 0.11):
            ph = rng.uniform(0, 6.28)
            s += signal.sawtooth(2 * np.pi * f * (1 + det / 100) * t + ph) * 0.3
    s = lp(s, bright, 2)
    e = np.minimum(1, np.minimum(t / 2.5, (dur - t) / 2.5).clip(0))
    return s * e / len(freqs) * 0.6


def note(n):  # midi -> Hz
    return 440 * 2 ** ((n - 69) / 12)


# chords (midi)
C_WARM = [[57, 64, 69, 72], [53, 60, 65, 69], [48, 55, 64, 67], [55, 62, 67, 71]]       # Am F C G (gentle)
C_PROM = [[53, 60, 65, 69], [48, 55, 64, 67], [57, 64, 69, 72], [52, 59, 64, 68]]       # F C Am E
C_DARK = [[57, 60, 64, 69], [53, 57, 60, 65], [50, 57, 62, 65], [52, 56, 59, 64]]       # Am F Dm E
C_END = [[57, 60, 64, 69], [50, 53, 57, 62], [53, 57, 60, 64], [52, 56, 59, 64]]


def score(N):
    tr = Track(N)
    # (start, end, chords, beat_seconds, melody density, gain)
    secs = [(0.0, 41.7, C_WARM, 2.6, 0.6, -17), (41.7, 86.4, C_PROM, 2.4, 0.5, -18),
            (86.4, 88.3, None, 0, 0, 0), (90.3, 131.6, C_DARK, 3.2, 0.25, -20),
            (131.6, 170.9, C_DARK, 3.0, 0.35, -19), (170.9, 190.85, C_END, 3.6, 0.3, -17)]
    for st, en, ch, bt, dens, g in secs:
        if ch is None:
            continue
        t = st; i = 0
        r = np.random.default_rng(int(st))
        while t < en - 0.5:
            c = ch[i % len(ch)]
            dur = bt * 2
            tr.add(t, pad([note(m - 12) for m in c[:3]], min(dur + 1.0, en - t + 1.0), 700), g - 7)
            # broken chord arpeggio, felt piano
            for k, m in enumerate([c[0] - 12, c[1], c[2], c[3]]):
                tt = t + k * bt / 2
                if tt < en:
                    tr.add(tt, piano(note(m), bt * 0.9, 0.35 + 0.1 * r.random()), g, pan=-0.3 + 0.2 * k)
            if r.random() < dens:
                m = c[r.integers(1, 4)] + 12
                tr.add(t + bt * 0.75, piano(note(m), bt, 0.3), g - 1, pan=0.25)
            t += dur; i += 1
    # held low note after the brakes (tension), final resolving chord
    tr.add(88.4, pad([note(45), note(52)], 3.0, 400), -24)
    tr.add(186.5, pad([note(57 - 12), note(60), note(64)], 4.3, 600), -22)
    return tr.x


# ------------------------------------------------------------------ sfx
def footsteps(t0, t1, rate=1.9, gain=-26, soft=False, run=False):
    out = []
    t = t0
    while t < t1:
        n = T(0.09)
        s = bp(rng.normal(0, 1, n), 150 if soft else 300, 1800 if soft else 3500) * np.exp(-np.arange(n) / SR * (55 if not soft else 40))
        out.append((t, s, gain + rng.uniform(-2, 1)))
        t += 1 / (rate * (1.7 if run else 1.0)) + rng.uniform(-0.03, 0.03)
    return out


def car_pass(dur=3.0, closest=0.5, big=False):
    n = T(dur)
    t = np.arange(n) / SR
    tc = closest * dur
    d = np.sqrt(((t - tc) * 9.0) ** 2 + 4.0)
    amp = 1 / d
    eng = signal.sawtooth(2 * np.pi * (55 if big else 75) * t * (1 - 0.04 * np.tanh((t - tc) * 3))) * 0.3
    s = lp(rng.normal(0, 1, n), 1200 if big else 1800) + eng
    s = s * amp
    return s / (np.abs(s).max() + 1e-9) * env_adsr(n, 0.3, 0.6)


def brakes(dur=1.4):
    n = T(dur); t = np.arange(n) / SR
    f = 2300 + 250 * np.sin(2 * np.pi * 7 * t) - 400 * t
    sq = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.6 + np.sin(2 * np.pi * np.cumsum(f * 1.5) / SR) * 0.25
    sq += bp(rng.normal(0, 1, n), 1500, 6000) * 0.5
    e = np.minimum(1, t / 0.05) * np.exp(-np.maximum(0, t - 0.9) * 6)
    return sq * e


def crowd(dur, density=6, gain=1.0):
    n = T(dur); t = np.arange(n) / SR
    s = bp(rng.normal(0, 1, n), 250, 2200) * (0.4 + 0.3 * np.abs(np.sin(t * 2.1)))
    # formant-like voice bursts (no words)
    for _ in range(int(density * dur)):
        st = rng.uniform(0, dur - 0.6); L = rng.uniform(0.25, 0.7)
        m = T(L); tt = np.arange(m) / SR
        f0 = rng.uniform(150, 320) * (1 + 0.15 * np.sin(tt * rng.uniform(3, 8)))
        v = signal.sawtooth(2 * np.pi * np.cumsum(f0) / SR) * env_adsr(m, 0.05, 0.15)
        v = bp(v, rng.uniform(500, 900), rng.uniform(1500, 2800))
        i = T(st); s[i:i + m] += v * rng.uniform(0.5, 1.2)
    return s * gain / (np.abs(s).max() + 1e-9)


def siren(dur, approach=True):
    n = T(dur); t = np.arange(n) / SR
    f = 750 + 400 * (0.5 + 0.5 * signal.sawtooth(2 * np.pi * t / 1.6, 0.5))
    dop = 1 + (0.03 if approach else -0.03) * (1 - t / dur)
    s = signal.square(2 * np.pi * np.cumsum(f * dop) / SR) * 0.4 + np.sin(2 * np.pi * np.cumsum(f * dop) / SR) * 0.6
    s = lp(s, 3500)
    amp = (t / dur) if approach else (1 - t / dur) ** 1.5
    return s * (0.15 + 0.85 * amp)


def door(dur=0.9):
    n = T(dur); t = np.arange(n) / SR
    f = 380 + 120 * np.sin(t * 9)
    cr = np.sin(2 * np.pi * np.cumsum(f) / SR) * (0.3 + 0.7 * (rng.random(n) > 0.6)) * 0.25
    cr = bp(cr, 300, 2500) * env_adsr(n, 0.05, 0.3)
    clunk = lp(rng.normal(0, 1, T(0.12)), 400) * np.exp(-np.arange(T(0.12)) / SR * 30)
    out = np.zeros(n + T(0.12)); out[:n] += cr; out[:T(0.12)] += clunk * 0.8
    return out


def thud(dur=0.25, f=180):
    n = T(dur); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * f * t * np.exp(-t * 6)) * np.exp(-t * 22) + lp(rng.normal(0, 1, n), 800) * np.exp(-t * 40) * 0.4)


def birds(dur, rate=0.8):
    n = T(dur); s = np.zeros(n)
    for _ in range(int(rate * dur)):
        st = rng.uniform(0, dur - 1); k = rng.integers(2, 6)
        for j in range(k):
            m = T(rng.uniform(0.05, 0.12)); tt = np.arange(m) / SR
            f = rng.uniform(2800, 4200) + rng.uniform(-1500, 1500) * tt / tt[-1]
            ch = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * tt / tt[-1])
            i = T(st + j * 0.14)
            if i + m < n:
                s[i:i + m] += ch * rng.uniform(0.3, 0.8)
    return s


def crickets(dur):
    n = T(dur); t = np.arange(n) / SR
    s = np.sin(2 * np.pi * 4300 * t) * (np.sin(2 * np.pi * 28 * t) > 0.3) * (np.sin(2 * np.pi * 0.7 * t) > -0.2)
    s2 = np.sin(2 * np.pi * 3900 * t) * (np.sin(2 * np.pi * 24 * t + 1) > 0.4) * (np.sin(2 * np.pi * 0.55 * t + 2) > 0)
    return (s + s2 * 0.7) * 0.3


def ambience(N):
    tr = Track(N)
    for s in SL.SHOTS:
        sid, t0, t1, st, mood = s[:5]
        d = t1 - t0 + 0.4
        if st == 'street':
            traffic = lp(rng.normal(0, 1, T(d)), 350) * 3
            tr.add(t0, traffic * env_adsr(T(d), 0.2, 0.2), -36)
            if mood in ('warm_morning', 'warm_noon'):
                tr.add(t0, birds(d), -36, pan=rng.uniform(-0.6, 0.6))
            if mood in ('late_cool',):
                tr.add(t0, lp(rng.normal(0, 1, T(d)), 600) * env_adsr(T(d), 0.3, 0.3), -40)   # wind
        elif st == 'house':
            room = lp(rng.normal(0, 1, T(d)), 200)
            tr.add(t0, room * env_adsr(T(d), 0.2, 0.2), -42)
            if mood == 'interior_warm':
                tr.add(t0, birds(d, 0.3), -46, pan=0.6)
            if mood == 'dusk':
                tr.add(t0, crickets(d), -44, pan=-0.3)
        else:
            tr.add(t0, lp(rng.normal(0, 1, T(d)), 250) * env_adsr(T(d), 0.3, 0.3), -42)
    return tr.x


def sfx(N):
    tr = Track(N)
    sh = {s[0]: (s[1], s[2]) for s in SL.SHOTS}
    def at(sid, dt=0.0):
        return sh[sid][0] + dt
    # walking / running
    for sid, a, b, kw in (('S05', 0, 3.4, dict(soft=True)), ('S11', 0, 1.8, dict(soft=True)), ('S12', 0.4, 5.0, {}),
                          ('S13', 0, 4.9, {}), ('S14', 0, 3.2, {}), ('S20', 1.4, 3.0, {}), ('S22', 0, 1.3, {}),
                          ('S40', 0, 2.9, dict(run=True)), ('S41', 1.0, 2.5, dict(soft=True)), ('S42', 0, 1.9, dict(soft=True)),
                          ('S43', 0, 1.7, dict(soft=True)), ('S44', 0, 3.0, {}), ('S48', 0, 2.8, dict(run=True, soft=True))):
        for t, s, g in footsteps(at(sid, a), at(sid, b), **kw):
            tr.add(t, s, g, pan=rng.uniform(-0.2, 0.2))
    # doors
    tr.add(at('S12', 0.1), door(), -24, 0.3); tr.add(at('S41', 0.1), door(), -22, -0.2)
    # play: ball bounces, giggle-free (no extra voices)
    tr.add(at('S06', 0.4), thud(0.2, 220), -26); tr.add(at('S06', 1.4), thud(0.2, 220), -26)
    tr.add(at('S27', 0.85), thud(0.3, 140), -24)      # rabbit lands softly
    # kitchen sizzle
    tr.add(at('S09'), hp(rng.normal(0, 1, T(4.0)), 3000) * 0.3 * env_adsr(T(4.0), 0.5, 0.8), -30)
    # cars
    for sid, dt, dur, big, g, pan in (('S01', 0.5, 4.5, False, -30, -0.5), ('S13', 0.0, 5.0, False, -28, 0.3), ('S14', 0.5, 4.5, False, -26, 0.4),
                                      ('S15', 0.1, 2.5, False, -24, -0.4), ('S15', 1.4, 2.5, True, -26, 0.5), ('S24', 0.0, 2.0, True, -18, 0.0),
                                      ('S38', 0.0, 1.2, False, -26, -0.6), ('S38', 1.1, 1.2, False, -26, 0.6), ('S38', 2.3, 1.2, True, -26, -0.5)):
        tr.add(at(sid, dt), car_pass(dur, 0.5, big), g, pan)
    # THE accident: brakes + impact-free silence, then shouting (no graphic sound)
    tr.add(at('S25', 0.15), brakes(1.6), -14, 0.1)
    tr.add(at('S26'), crowd(9.5, 5, 1.0), -24, 0.0)
    tr.add(at('S28'), crowd(10.0, 4, 0.8), -27, 0.0)
    tr.add(at('S29', 0.1), crowd(2.0, 3, 1.0), -24, 0.2)
    tr.add(at('S30'), crowd(19.0, 2, 0.6), -31, 0.0)
    tr.add(at('S33', 0.2), bp(rng.normal(0, 1, T(2.8)), 200, 900) * 0.4 * env_adsr(T(2.8), 0.3, 0.6), -28)   # tomato rolls
    # heartbeat under Hind's eyes
    for k in range(4):
        tr.add(at('S35', 0.3 + k * 0.72), thud(0.18, 60), -24); tr.add(at('S35', 0.5 + k * 0.72), thud(0.18, 55), -28)
    # ambulance arrives / leaves
    tr.add(at('S36'), siren(3.6, True), -22, -0.4)
    tr.add(at('S37'), siren(3.2, False), -22, 0.5)
    return tr.x


def main():
    narr = load_narr()
    N = len(narr) + T(0.2)
    n = np.zeros(N); n[:len(narr)] = narr
    music = score(N)
    amb = ambience(N)
    fx = sfx(N)
    # side-chain duck the music/ambience with the voice envelope
    v = np.abs(n)
    venv = signal.sosfilt(signal.butter(1, 3, 'lowpass', fs=SR, output='sos'), v)
    venv = venv / (venv.max() + 1e-9)
    duck = 1 - 0.45 * np.clip(venv * 4, 0, 1)
    bed = (music + amb) * duck[:, None] + fx * (1 - 0.25 * np.clip(venv * 4, 0, 1))[:, None]
    # final fade (last 3 s) for the bed; narration untouched
    tail = T(3.0)
    bed[-tail:] *= np.linspace(1, 0, tail)[:, None]
    out = bed + np.stack([n, n], 1)
    pk = np.abs(out).max()
    if pk > 0.98:
        out *= 0.98 / pk
    sf.write(os.path.join(AUD, 'mix.wav'), out, SR, subtype='PCM_24')
    sf.write(os.path.join(AUD, 'music_stem.wav'), music, SR, subtype='PCM_16')
    sf.write(os.path.join(AUD, 'sfx_ambience_stem.wav'), amb + fx, SR, subtype='PCM_16')
    print('MIX OK', out.shape[0] / SR, 's')


if __name__ == '__main__':
    main()

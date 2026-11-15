"""Episode 01 sound design + score (series synth instruments), mixed under the narration.
python3 audio_ep01.py out_mix.wav out_bed.wav
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, '..', '..', 'ep03-harus-last-journey', 'src')))
import numpy as np
import audio as A

A.DUR = 91.0
A.N = int(A.SR * A.DUR)
A.VO = os.path.join(os.path.dirname(HERE), 'assets', 'audio', 'voiceover.mp3')
from audio import *  # noqa


def build():
    N, SR, rng = A.N, A.SR, A.rng
    sfx, mus, amb = np.zeros(N), np.zeros(N), np.zeros(N)
    ta = np.arange(N) / SR
    sg = A.segment_gain
    # evening station: soft breeze, distant birds at sunset
    breeze = A.lp(A.noise(A.DUR), 450, 2) * (0.6 + 0.4 * np.sin(2 * np.pi * ta * 0.1))
    amb += breeze * (sg(0, 44.5, 1.0, 0.5) + sg(51.0, 91, 0.5, 2.0)) * 0.16
    for k in range(14):
        place(sfx, bird(0.05), rng.uniform(0.5, 20))
    # footsteps (Haru, passers-by, Maryam, the son)
    for t0, t1, st in ((5.4, 7.8, 0.6), (18.4, 21.5, 0.42), (21.7, 25.0, 0.45), (57.8, 59.3, 0.6), (61.3, 63.2, 0.55), (70.5, 73.2, 0.45)):
        tt = t0
        while tt < t1:
            place(sfx, A.lp(A.noise(0.1), 1100) * np.exp(-np.arange(int(0.1 * SR)) / SR * 35) * 0.18, tt)
            tt += st
    # paper and pen
    for tt in (13.2, 38.9, 41.2, 42.0, 42.8):
        place(sfx, A.hp(A.noise(0.35), 2500) * np.exp(-np.arange(int(0.35 * SR)) / SR * 9) * 0.12, tt)
    pen = A.bp(A.noise(5.0), 2500, 7000) * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 3.1 * np.arange(int(5 * SR)) / SR))) * 0.04
    place(sfx, pen, 45.6)
    # the cold night: wind, the last train arriving and stopping
    wind = A.lp(A.noise(A.DUR), 500, 2)
    amb += wind * sg(54.3, 70.6, 0.6, 0.8) * 0.2
    place(sfx, A.reverb(A.lp(A.whistle(2.6, 0.5), 2500), 3.5, 0.55), 54.5)
    for k in range(12):
        tt = 54.6 + k * (0.3 + k * 0.03)
        g = 1 - k / 12
        place(sfx, A.lp(A.clack(0.16 * g), 1200), tt)
        place(sfx, A.lp(A.clack(0.12 * g), 1200), tt + 0.15)
    place(sfx, A.bp(A.noise(1.6), 2000, 6000) * np.hanning(int(1.6 * SR)) * 0.12, 57.0)  # brakes hiss
    # next day: calm snow, birds; home: room tone, tea
    for k in range(6):
        place(sfx, bird(0.04), rng.uniform(70.6, 81))
    amb += A.lp(A.noise(A.DUR), 280) * 0.06 * sg(81.6, 91, 1.0, 2.0)
    place(sfx, pour(1.4, 0.2), 83.0)
    # ---- score: warm, nostalgic (C major / A minor), the theme of waiting
    theme = [('E5', 0.4), ('G5', 1.4), ('A5', 2.4), ('G5', 3.6), ('E5', 5.4), ('D5', 6.6), ('C5', 7.9), ('E5', 9.4), ('D5', 10.8), ('A4', 12.4),
             ('C5', 13.8), ('D5', 15.4), ('E5', 17.0), ('G4', 18.6), ('A4', 20.2)]
    for n, tt in theme:
        place(mus, piano(n, 4.0, 0.42), tt)
    for notes, t0 in ((['C3', 'G3', 'E4'], 0.0), (['A2', 'E3', 'C4'], 5.3), (['F2', 'C3', 'A3'], 10.6), (['G2', 'D3', 'B3'], 15.4), (['C3', 'G3', 'E4'], 18.2)):
        place(mus, pad(notes, 6.0, 2.0, 2.5, 1500, 0.09), t0)
    # Maryam: lighter, curious
    for n, tt in (('C5', 22.0), ('E5', 22.8), ('G5', 23.6), ('A5', 25.0), ('G5', 27.2), ('E5', 29.0)):
        place(mus, piano(n, 3.0, 0.36), tt)
    # "I'm waiting for my son... he left angry" - minor, tender
    for n, tt in (('A4', 30.6), ('C5', 31.8), ('E5', 33.2), ('D5', 34.6), ('C5', 36.0), ('B4', 37.4), ('A4', 38.8)):
        place(mus, piano(n, 4.0, 0.42), tt)
    place(mus, pad(['A2', 'E3', 'C4'], 9.0, 2.0, 2.5, 1300, 0.11), 30.2)
    # the letter: hopeful
    for n, tt in (('G4', 41.2), ('C5', 42.4), ('E5', 43.6), ('D5', 45.0), ('E5', 46.4), ('G5', 47.8), ('F5', 49.2), ('E5', 50.6)):
        place(mus, piano(n, 4.0, 0.4), tt)
    place(mus, pad(['C3', 'G3', 'E4'], 10.0, 2.0, 2.5, 1500, 0.10), 41.0)
    # weeks without a reply: sparse
    for n, tt in (('E4', 51.4), ('D4', 52.8)):
        place(mus, piano(n, 4.0, 0.34), tt)
    # the return: swell, then the embrace
    place(mus, pad(['F2', 'C3', 'A3'], 6.0, 2.5, 1.5, 1200, 0.12), 54.4)
    for n, tt in (('C5', 61.4), ('F5', 62.6), ('E5', 63.6), ('C5', 65.0), ('A4', 66.4), ('C5', 67.4), ('F5', 68.4), ('A5', 69.4)):
        place(mus, piano(n, 4.0, 0.46), tt)
    for notes, t0 in ((['F2', 'C3', 'A3'], 60.4), (['D2', 'A2', 'F3'], 63.3), (['A#2', 'F3', 'D4'], 66.5), (['F2', 'C3', 'A3', 'F4'], 68.4)):
        place(mus, pad(notes, 4.5, 1.2, 2.0, 1800, 0.15), t0)
    # resolution: the bench is empty, two cranes, home
    for n, tt in (('E5', 71.0), ('G5', 72.4), ('C6', 74.0), ('B5', 76.4), ('G5', 77.8), ('A5', 79.6), ('G5', 81.8), ('E5', 83.6),
                  ('D5', 85.2), ('C5', 87.0)):
        place(mus, piano(n, 4.5, 0.4), tt)
    for notes, t0 in ((['C3', 'G3', 'E4'], 70.4), (['A2', 'E3', 'C4'], 74.4), (['F2', 'C3', 'A3'], 78.4), (['G2', 'D3', 'B3'], 82.0), (['C3', 'G3', 'C4', 'E4'], 85.4)):
        place(mus, pad(notes, 5.0, 1.5, 2.5, 1500, 0.10), t0)
    mus = A.reverb(mus, 2.8, 0.35)
    sfx = A.reverb(sfx, 1.2, 0.15)
    bed = mus * 2.4 + sfx * 0.85 + amb * 0.85
    bed *= np.clip((90.6 - ta) / 2.0, 0, 1)
    return bed


A.build = build
if __name__ == '__main__':
    A.main(sys.argv[1], sys.argv[2])

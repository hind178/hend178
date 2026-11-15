"""Episode 02 sound design + score, built from the series' synth instruments
(../../ep03-harus-last-journey/src/audio.py) and mixed under the narration.
python3 audio_ep02.py out_mix.wav out_bed.wav
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, '..', '..', 'ep03-harus-last-journey', 'src')))
import numpy as np
import audio as A

A.DUR = 113.0
A.N = int(A.SR * A.DUR)
A.VO = os.path.join(os.path.dirname(HERE), 'assets', 'audio', 'voiceover.mp3')
from audio import *  # noqa  (instruments & helpers)


def build():
    N, SR, rng = A.N, A.SR, A.rng
    sfx, mus, amb = np.zeros(N), np.zeros(N), np.zeros(N)
    t_axis = np.arange(N) / SR
    sg = A.segment_gain
    # winter wind outside; muted inside the house
    wind = A.lp(A.noise(A.DUR), 500, 2) * (0.6 + 0.4 * np.sin(2 * np.pi * t_axis * 0.13))
    out = sg(0, 2.0, 0.2, 0.3) + sg(18.6, 65.2, 0.4, 0.6) + sg(79.9, 113, 0.6, 2.0)
    amb += wind * out * 0.2
    room = A.lp(A.noise(A.DUR), 280) * 0.06
    amb += room * (sg(1.9, 18.7, 0.3, 0.3) + sg(65.0, 80.0, 0.3, 0.3))
    # running footsteps in snow
    for t0, t1, step in ((0.0, 1.95, 0.31), (18.7, 21.6, 0.28)):
        tt = t0
        while tt < t1:
            place(sfx, A.lp(A.noise(0.12), 900) * np.exp(-np.arange(int(0.12 * SR)) / SR * 30) * 0.25, tt)
            tt += step
    # chest lid creak, paper rustles
    place(sfx, A.creak(1.0, 0.25), 2.2)
    for tt in (4.2, 5.6, 7.0, 9.5, 10.4, 11.0, 12.3, 18.7, 30.2, 31.2, 32.4, 33.2, 45.8):
        place(sfx, A.hp(A.noise(0.35), 2500) * np.exp(-np.arange(int(0.35 * SR)) / SR * 9) * 0.12, tt)
    # door opens: gust of wind
    place(sfx, A.bp(A.noise(1.6), 300, 3000) * np.hanning(int(1.6 * SR)) * 0.35, 80.9)
    # distant memory of the 1962 train (Maryam wondering, father's confession)
    for k in range(10):
        place(sfx, A.lp(A.clack(0.08), 700), 58.5 + k * 0.45)
    place(sfx, A.reverb(A.lp(A.whistle(2.0, 0.08), 1200), 3.5, 0.8), 61.0)
    for ts in (95.1, 96.4):
        place(sfx, A.thunder(3.0, 0.15), ts)
    # ---- score: a gentle music-box/piano theme of discovery, then tension
    open_ = [('A4', 0.2), ('C5', 0.9), ('E5', 1.6)]
    disc = [('E5', 9.2), ('G5', 9.9), ('A5', 10.6), ('C6', 11.6), ('B5', 13.0), ('A5', 14.4), ('E5', 15.3), ('G5', 16.4), ('A5', 17.4)]
    for n, tt in open_ + disc:
        place(mus, piano(n, 3.5, 0.45), tt)
    place(mus, pad(['A2', 'E3', 'C4'], 7.0, 2.0, 2.0, 1400, 0.09), 3.6)
    place(mus, pad(['F2', 'C3', 'A3'], 9.0, 1.5, 2.5, 1400, 0.10), 9.0)
    # recognition and the letter: tender, F major / D minor
    let = [('C5', 25.6), ('A4', 26.6), ('F4', 27.6), ('G4', 28.8), ('A4', 30.2), ('C5', 31.6), ('D5', 33.0), ('C5', 34.6), ('A4', 36.0),
           ('F5', 38.4), ('E5', 39.4), ('C5', 40.4), ('D5', 41.6), ('C5', 42.8), ('A4', 44.4), ('G4', 45.8), ('F4', 47.2)]
    for n, tt in let:
        place(mus, piano(n, 4.0, 0.42), tt)
    for notes, t0, d in ((['F2', 'C3', 'A3'], 21.6, 4), (['D2', 'A2', 'F3'], 25.4, 4.5), (['A#2', 'F3', 'D4'], 29.8, 4.5),
                         (['F2', 'C3', 'A3', 'F4'], 34.2, 4), (['C3', 'G3', 'E4'], 38.2, 5), (['D2', 'A2', 'F3', 'A3'], 43.2, 5)):
        place(mus, pad(notes, d + 1.2, 1.2, 2.0, 1700, 0.12), t0)
    # questions and wondering: sparse, unresolved
    for n, tt in (('A4', 48.4), ('E4', 50.2), ('D5', 52.0), ('C5', 54.4), ('B4', 56.0), ('E4', 57.6), ('F4', 60.0), ('G#4', 62.6)):
        place(mus, piano(n, 4.0, 0.36), tt)
    place(mus, pad(['A2', 'E3'], 9.0, 2.0, 2.0, 900, 0.10), 48.0)
    place(mus, pad(['F2', 'B2', 'G#3'], 8.5, 1.5, 2.0, 900, 0.11), 56.9)
    # father's silence and haste: low pulse
    place(mus, pad(['D2', 'A2'], 15.0, 1.0, 2.0, 600, 0.12), 68.7)
    for k in range(16):
        place(mus, A.lp(A.noise(0.5), 120) * np.exp(-np.arange(int(0.5 * SR)) / SR * 8) * 0.35, 79.9 + k * 0.62)
    # confession: dark strings, held breath at "the same train"
    place(mus, pad(['D2', 'A2', 'F3'], 10.5, 2.0, 1.5, 800, 0.14), 88.6)
    place(mus, pad(['C#2', 'G#2', 'E3'], 3.0, 0.2, 1.5, 700, 0.14), 97.6)
    # hope (major lift) then the ominous last line
    for n, tt in (('A4', 99.4), ('C#5', 100.6), ('E5', 101.8), ('A5', 103.3)):
        place(mus, piano(n, 4.0, 0.4), tt)
    place(mus, pad(['A2', 'E3', 'C#4'], 6.5, 2.5, 1.5, 1600, 0.12), 98.8)
    place(mus, pad(['D2', 'A2', 'F3', 'G#3'], 7.5, 1.0, 3.0, 800, 0.14), 105.4)
    place(mus, piano('D3', 6.0, 0.5), 108.4)
    place(sfx, A.reverb(A.lp(A.whistle(2.4, 0.06), 900), 3.5, 0.9), 109.0)
    mus = A.reverb(mus, 2.8, 0.35)
    sfx = A.reverb(sfx, 1.2, 0.15)
    bed = mus * 2.4 + sfx * 0.85 + amb * 0.85
    bed *= np.clip((112.6 - t_axis) / 2.0, 0, 1)
    return bed


A.build = build
if __name__ == '__main__':
    A.main(sys.argv[1], sys.argv[2])

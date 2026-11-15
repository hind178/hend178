"""Generate timing/timing_sheet.csv and timing/timing_sheet.md from SHOTS + transcript."""
import json, os, sys, csv
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import shots
tr = json.load(open(os.path.join(ROOT, 'timing', 'transcript.json')))
words = [w for s in tr for w in s['words']]
rows = []
for i, (name, a, b, fn, gr, xf) in enumerate(shots.SHOTS):
    line = ''.join(w[2] for w in words if a <= (w[0] + w[1]) / 2 < b).strip()
    rows.append(dict(n=i + 1, shot=name, start=f'{a:.2f}', end=f'{b:.2f}', frame_in=int(round(a * 30)), frame_out=int(round(b * 30)) - 1,
                     frames=int(round(b * 30)) - int(round(a * 30)), transition=f'dissolve {xf:.2f}s' if xf else 'cut', narration=line, fn=fn.__name__))
with open(os.path.join(ROOT, 'timing', 'timing_sheet.csv'), 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
md = ['# Episode 03 — Haru\'s Last Journey · timing sheet', '', '30 fps · 1080×1920 · total %.2f s (%d frames). Times locked to the narration (word timestamps in transcript.json).' % (shots.DURATION, round(shots.DURATION * 30)), '',
      '| # | Shot | In (s) | Out (s) | Frames | Transition | Narration (Iraqi Arabic) |', '|---|---|---|---|---|---|---|']
for r in rows:
    md.append(f"| {r['n']} | {r['shot']} | {r['start']} | {r['end']} | {r['frame_in']}–{r['frame_out']} | {r['transition']} | {r['narration']} |")
md += ['', '## Sound cues (src/audio.py)', '',
       '| Time (s) | Cue |', '|---|---|',
       '| 0–3.9 | Snow wind, three slow piano notes (A minor), low pad |',
       '| 3.9–10.6 | Rain, train wheel rhythm, thunder on each lightning flash, restrained low drone and pulses |',
       '| 10.6–14.4 | Metal creak, structural crash, river splash, glass |',
       '| 14–48 | Rushing water, muffled rain, bubbles (21–27), dark string pads |',
       '| 37.6–48 | Crane motif: gentle piano (E–G–A) |',
       '| 51.6–88 | Soft piano arpeggios + strings with space; spring birds 56.6, leaves 58, tea pour 62.9 |',
       '| 88.75, 89.75 | Station clock bell (two strikes), tick at 91.4 |',
       '| 93.65, 97.0 | Distant steam whistle (reverberant) |',
       '| 98.5–131 | Soft railway rhythm; emotional theme in F major, swell at forgiveness (118–129) |',
       '| 129.6 | Last faint whistle; then silence with wind only |',
       '| 135–161 | Warm room tone, birdsong, tea pouring 140.6, delicate C-major piano, fade with picture |',
       '', 'Bed level ≈ 18–20 dB below the narration, with extra ducking while the narrator speaks.']
open(os.path.join(ROOT, 'timing', 'timing_sheet.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
print(len(rows), 'shots')

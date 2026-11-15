"""Build timing/timing_sheet.md + .csv for Episode 02."""
import json, os, sys, csv
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import ep02_shots as S
words = [w for s in json.load(open(os.path.join(ROOT, 'timing', 'transcript.json'))) for w in s['words']]
rows = []
for i, (name, a, b, fn, gr, xf) in enumerate(S.SHOTS):
    rows.append(dict(n=i + 1, shot=name, start=f'{a:.2f}', end=f'{b:.2f}', frame_in=round(a * 30), frame_out=round(b * 30) - 1,
                     transition=f'dissolve {xf:.2f}s' if xf else 'cut',
                     narration=''.join(w[2] for w in words if a <= (w[0] + w[1]) / 2 < b).strip(), fn=fn.__name__))
with open(os.path.join(ROOT, 'timing', 'timing_sheet.csv'), 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
md = ["# Episode 02 — The Paper Crane · timing sheet", "", "30 fps · 1080×1920 · %.2f s (%d frames)." % (S.DURATION, round(S.DURATION * 30)), "",
      "| # | Shot | In (s) | Out (s) | Frames | Transition | Narration |", "|---|---|---|---|---|---|---|"]
md += [f"| {r['n']} | {r['shot']} | {r['start']} | {r['end']} | {r['frame_in']}–{r['frame_out']} | {r['transition']} | {r['narration']} |" for r in rows]
open(os.path.join(ROOT, 'timing', 'timing_sheet.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
print(len(rows), 'shots')

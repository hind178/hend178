"""QC: contact sheet of every scene at start/middle/end (or of rendered clips with --clips)."""
import sys; from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import render_final as R
from PIL import Image, ImageDraw
scenes = [int(a) for a in sys.argv[1].split(',')] if len(sys.argv) > 1 else range(1, len(R.SHOTS) + 1)
tw, th = 216, 384; scenes = list(scenes)
sheet = Image.new('RGB', (tw * 3 + 60, th * len(scenes)), 'white'); d = ImageDraw.Draw(sheet)
for r, k in enumerate(scenes):
    t0, t1 = R.SHOTS[k - 1]['t']
    for c, q in enumerate((.04, .5, .96)):
        t = t0 + (t1 - t0) * q
        sheet.paste(R.frame_at(k - 1, t).resize((tw, th)), (60 + c * tw, r * th))
    d.text((4, r * th + 4), f'{k:02}', fill='black')
out = Path(sys.argv[2]) if len(sys.argv) > 2 else R.P / 'production' / 'qc_sheet.jpg'
sheet.save(out, quality=88); print(out)

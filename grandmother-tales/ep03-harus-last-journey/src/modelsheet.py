import sys, numpy as np, cv2
from core import *
from chars import *
s = new_surface(); c = s.getCanvas()
c.drawPaint(lin((0,0),(0,H),['#f2ead9','#e2d6bf']))
F = skia.Font(skia.Typeface("DejaVu Sans"), 28)
names=['haru','maryam','father','son','boy']
for i,n in enumerate(names):
    x = 120 + i*210
    c.drawString(n, x-40, 50, F, P('#333333'))
    draw_head(c, n, x, 200, 0.8, yaw=0.45, seed=i, blush=0.3)
    draw_head(c, n, x, 430, 0.8, yaw=-0.2, seed=i+5, mouth='smile', blush=0.3, happy=0.0)
xs=[140,330,540,770,960]
for i,n in enumerate(names):
    figure(c, n, xs[i], 1450, 0.58, yaw=0.4, seed=i, arms=dict(L=(-8,6),R=(8,-6)))
bust(c, 'haru', 270, 1650, 0.75, yaw=0.35, head=dict(brow=1, tears=0.9, tear_t=0.4, wet=0.8, mouth='sad'))
bust(c, 'son', 780, 1650, 0.75, yaw=-0.35, head=dict(mouth='smile', wet=0.3))
crane(c, 540, 1600, 0.6)
crane(c, 540, 1800, 0.6, wet=1, flip=True)
arr = to_np(snapshot(s))
cv2.imwrite(sys.argv[1], cv2.cvtColor(grade(arr,0,grain=0.04,vig=0.3), cv2.COLOR_RGB2BGR))

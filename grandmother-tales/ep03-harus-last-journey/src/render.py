"""Render Episode 03.

  python3 render.py preview  out.png  t1 t2 ...   -> contact sheet of given seconds
  python3 render.py video    out_dir  [workers]   -> silent picture segments + concat
"""
import sys, os, math, subprocess, json
import numpy as np
import cv2

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from core import *
import shots

VO = os.path.join(ROOT, 'assets', 'audio', 'voiceover.mp3')


def load_env():
    """Per-frame narration loudness (0..1) for lip-sync."""
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', VO, '-ac', '1', '-ar', '16000', '-f', 's16le', '-'],
                         capture_output=True, check=True).stdout
    a = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
    hop = 16000 // FPS
    n = len(a) // hop + 1
    env = np.array([np.sqrt(np.mean(a[i * hop:(i + 1) * hop] ** 2) + 1e-9) for i in range(n)])
    env = np.clip((env - 0.01) / 0.09, 0, 1)
    return env


def shot_at(T):
    for i, s in enumerate(shots.SHOTS):
        if s[1] <= T < s[2]:
            return i
    return len(shots.SHOTS) - 1


def render_shot(i, T):
    name, a, b, fn, gr, xf = shots.SHOTS[i]
    surf = new_surface()
    c = surf.getCanvas()
    c.clear(skia.ColorBLACK)
    fn(c, T - a, T)
    arr = to_np(snapshot(surf))
    return grade(arr, int(T * FPS), **gr)


def render_frame(f):
    T = f / FPS
    i = shot_at(T)
    out = render_shot(i, T)
    name, a, b, fn, gr, xf = shots.SHOTS[i]
    if xf > 0 and i > 0 and T - a < xf:
        prev = render_shot(i - 1, T)
        k = smooth((T - a) / xf)
        out = (prev.astype(np.float32) * (1 - k) + out.astype(np.float32) * k).astype(np.uint8)
    return out


def preview(path, times):
    shots.ENV = load_env()
    tiles = []
    for T in times:
        img = render_frame(int(T * FPS))
        img = cv2.resize(img, (270, 480), interpolation=cv2.INTER_AREA)
        cv2.putText(img, '%.2f' % T, (6, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 0), 1)
        tiles.append(img)
    cols = min(6, len(tiles))
    rows = (len(tiles) + cols - 1) // cols
    sheet = np.zeros((rows * 480, cols * 270, 3), np.uint8)
    for k, im in enumerate(tiles):
        r, cc = divmod(k, cols)
        sheet[r * 480:(r + 1) * 480, cc * 270:(cc + 1) * 270] = im
    cv2.imwrite(path, cv2.cvtColor(sheet, cv2.COLOR_RGB2BGR))


def worker(args):
    f0, f1, out = args
    shots.ENV = load_env()
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '%dx%d' % (W, H), '-r', str(FPS),
                          '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '14', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    for f in range(f0, f1):
        p.stdin.write(render_frame(f).tobytes())
        if f % 60 == 0:
            print('frame', f, flush=True)
    p.stdin.close()
    p.wait()
    return out


def video(out_dir, workers=4):
    from multiprocessing import Pool
    os.makedirs(out_dir, exist_ok=True)
    N = int(round(shots.DURATION * FPS))
    chunk = 150
    jobs = [(f, min(N, f + chunk), os.path.join(out_dir, 'seg_%05d.mp4' % f)) for f in range(0, N, chunk)]
    jobs = [j for j in jobs if not os.path.exists(j[2])]
    with Pool(workers) as pool:
        for r in pool.imap_unordered(worker, jobs):
            print('done', r, flush=True)
    segs = sorted(x for x in os.listdir(out_dir) if x.startswith('seg_'))
    with open(os.path.join(out_dir, 'list.txt'), 'w') as fh:
        for s in segs:
            fh.write("file '%s'\n" % s)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', os.path.join(out_dir, 'list.txt'), '-c', 'copy',
                    os.path.join(out_dir, 'picture.mp4')], check=True)


if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'preview':
        preview(sys.argv[2], [float(x) for x in sys.argv[3:]])
    elif mode == 'video':
        video(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 4)

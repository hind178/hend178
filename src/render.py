"""Render frames of episode_01/story.blend shot by shot (resumable).

python render.py --out DIR [--mode mid|all|first-last] [--step 2 --offset 1] [--pct 50]
                 [--samples 8] [--shots S01,S02]
Only the set used by a shot is enabled (others excluded from the view layer),
persistent data keeps the BVH between frames of a shot."""
import sys, os, json, argparse, time
sys.path.insert(0, os.path.dirname(__file__))
import bpy
import shotlist as SL

ap = argparse.ArgumentParser()
ap.add_argument('--out', required=True)
ap.add_argument('--mode', default='all')
ap.add_argument('--step', type=int, default=1)
ap.add_argument('--offset', type=int, default=0)
ap.add_argument('--pct', type=int, default=50)
ap.add_argument('--samples', type=int, default=8)
ap.add_argument('--shots', default='')
ap.add_argument('--blend', default=os.path.join(os.path.dirname(__file__), '..', 'episode_01', 'story.blend'))
args = ap.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else sys.argv[1:])

bpy.ops.wm.open_mainfile(filepath=os.path.abspath(args.blend))
sc = bpy.context.scene
sc.render.resolution_percentage = args.pct
sc.cycles.samples = args.samples
sc.render.use_persistent_data = True
sc.render.image_settings.file_format = 'PNG'
sc.render.image_settings.color_depth = '8'
SETS = {'street': 'ENV_Street', 'house': 'ENV_House', 'hospital': 'ENV_Hospital'}
os.makedirs(args.out, exist_ok=True)


def layer_coll(name, lc=None):
    lc = lc or bpy.context.view_layer.layer_collection
    if lc.name == name:
        return lc
    for c in lc.children:
        r = layer_coll(name, c)
        if r:
            return r


want = set(args.shots.split(',')) if args.shots else None
t_all = time.time(); n = 0
for s in SL.SHOTS:
    sid = s[0]
    if want and sid not in want:
        continue
    f0, f1 = SL.frames(s)
    if args.mode == 'mid':
        fr = [(f0 + f1) // 2]
    elif args.mode == 'first-last':
        fr = [f0, (f0 + f1) // 2, f1]
    else:
        fr = [f for f in range(f0, f1 + 1) if (f - 1) % args.step == args.offset % args.step]
    fr = [f for f in fr if not os.path.exists(os.path.join(args.out, f'f_{f:05d}.png'))]
    if not fr:
        continue
    for k, v in SETS.items():
        lc = layer_coll(v)
        if lc:
            lc.exclude = (k != s[3])
    for f in fr:
        sc.frame_set(f)
        sc.render.filepath = os.path.join(args.out, f'f_{f:05d}.png')
        t = time.time()
        bpy.ops.render.render(write_still=True)
        n += 1
        print(f'RENDERED {sid} f{f} {time.time() - t:.1f}s total {n} frames {time.time() - t_all:.0f}s', flush=True)
print('RENDER DONE', n)

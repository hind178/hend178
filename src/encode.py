"""Encode episode_01/final.mp4 from rendered frames + mixed audio.

Missing frames (progressive render: even frames first) are filled by holding the
previous rendered frame, so the film is always complete at 30 fps.
Grade: warm & slightly saturated before the accident, cooler/desaturated after.
python encode.py [--frames DIR] [--out PATH]"""
import os, sys, subprocess, argparse, shutil
sys.path.insert(0, os.path.dirname(__file__))
import shotlist as SL

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
ap = argparse.ArgumentParser()
ap.add_argument('--frames', default=os.path.join(ROOT, 'episode_01', 'frames'))
ap.add_argument('--out', default=os.path.join(ROOT, 'episode_01', 'final.mp4'))
ap.add_argument('--audio', default=os.path.join(ROOT, 'episode_01', 'audio', 'mix.wav'))
a = ap.parse_args()

seq = os.path.join(a.frames, '_seq')
shutil.rmtree(seq, ignore_errors=True); os.makedirs(seq)
last = None; held = 0
for f in range(1, SL.LAST_FRAME + 1):
    p = os.path.join(a.frames, f'f_{f:05d}.png')
    if os.path.exists(p):
        last = p
    else:
        held += 1
        if last is None:   # look ahead for the first available
            for g in range(f, SL.LAST_FRAME + 1):
                q = os.path.join(a.frames, f'f_{g:05d}.png')
                if os.path.exists(q):
                    last = q; break
    os.symlink(last, os.path.join(seq, f'{f:05d}.png'))
print(f'frames: {SL.LAST_FRAME}, held (not yet rendered): {held}')

dur = SL.LAST_FRAME / SL.FPS
sat = "if(lt(t,86.4),1.10,if(lt(t,120),1.0-0.18*(t-86.4)/33.6,0.80))"
vf = (f"scale=1080:1920:flags=lanczos,unsharp=5:5:0.45:5:5:0.0,"
      f"eq=saturation='{sat}':eval=frame,"
      f"colorbalance=rs=0.02:bs=-0.02:enable='lt(t,86.4)',"
      f"colorbalance=rs=-0.025:bs=0.035:enable='gte(t,120)',"
      f"fade=t=in:st=0:d=0.8,fade=t=out:st={dur - 3.0:.3f}:d=3.0,format=yuv420p")
cmd = ['ffmpeg', '-v', 'error', '-y', '-framerate', '30', '-i', os.path.join(seq, '%05d.png'), '-i', a.audio,
       '-vf', vf, '-c:v', 'libx264', '-preset', 'slow', '-crf', '19', '-profile:v', 'high', '-pix_fmt', 'yuv420p',
       '-r', '30', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-t', f'{dur:.3f}', '-movflags', '+faststart', a.out]
subprocess.run(cmd, check=True)
shutil.rmtree(seq)
print('ENCODED', a.out)

"""Render Episode 01 using the shared series renderer.
  python3 render_ep01.py preview out.png t1 t2 ...
  python3 render_ep01.py video out_dir [workers]
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.abspath(os.path.join(HERE, '..', '..', 'ep03-harus-last-journey', 'src')))
import ep01_shots
import render as R                       # ../../ep03-harus-last-journey/src/render.py
R.shots = ep01_shots
R.VO = os.path.join(os.path.dirname(HERE), 'assets', 'audio', 'voiceover.mp3')
if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'preview':
        R.preview(sys.argv[2], [float(x) for x in sys.argv[3:]])
    else:
        R.video(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 3)

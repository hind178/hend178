"""Vertical cover image (1080x1920): the sisters at the curb, moments before the promise.
python cover.py  -> episode_01/cover.png"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import bpy
import shotlist as SL

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
bpy.ops.wm.open_mainfile(filepath=os.path.join(ROOT, 'episode_01', 'story.blend'))
sc = bpy.context.scene
shot = next(s for s in SL.SHOTS if s[0] == 'S18')
f0, f1 = SL.frames(shot)
sc.frame_set(f1 - 10)
for lc in bpy.context.view_layer.layer_collection.children['ENVIRONMENTS'].children:
    lc.exclude = lc.name not in ('ENV_Street', 'PROPS', 'CARS')
sc.render.resolution_percentage = 100
sc.cycles.samples = 48
sc.render.filepath = os.path.join(ROOT, 'episode_01', 'cover.png')
bpy.ops.render.render(write_still=True)
print('COVER OK')

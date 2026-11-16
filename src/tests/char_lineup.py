"""Turnaround/lineup preview of Hind & Huda. Usage: python char_lineup.py out.png [engine] [angle]"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import bpy
from lib import util as U, character as C

out = sys.argv[1]
eng = sys.argv[2] if len(sys.argv) > 2 else 'CYCLES'
ang = float(sys.argv[3]) if len(sys.argv) > 3 else 0.0
U.reset_scene()
sc = bpy.context.scene
hu = C.build(C.HUDA); hu.arm.location = (-0.24, 0, 0)
hi = C.build(C.HIND); hi.arm.location = (0.22, 0, 0)
rb = C.build_rabbit()
rb.location = (0.42, -0.1, 0)
U.plane('floor', 20, 20, mat_=U.mat('floor', (0.5, 0.42, 0.35), rough=0.8))
U.plane('wall', 20, 6, (0, 2, 0), (math.pi / 2, 0, 0), mat_=U.mat('wall', (0.7, 0.62, 0.5)))
sun = bpy.data.objects.new('sun', bpy.data.lights.new('sun', 'SUN')); sc.collection.objects.link(sun)
sun.data.energy = 3.5; sun.rotation_euler = (0.9, 0.2, -0.6); sun.data.color = (1, 0.9, 0.78)
w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True
w.node_tree.nodes['Background'].inputs[0].default_value = (0.5, 0.6, 0.75, 1)
w.node_tree.nodes['Background'].inputs[1].default_value = 0.8
cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); sc.collection.objects.link(cam)
d = 3.6
cam.location = (d * math.sin(ang), -d * math.cos(ang), 0.75)
cam.rotation_euler = (math.radians(88), 0, ang)
cam.data.lens = 50
sc.camera = cam
if len(sys.argv) > 4:   # face close-up
    cam.location = (0.22 + 0.9 * math.sin(ang), -0.9 * math.cos(ang), 0.93); cam.data.lens = 60
    if sys.argv[4] == 'huda':
        cam.location = (-0.24 + 0.9 * math.sin(ang), -0.9 * math.cos(ang), 1.08)
sc.render.engine = eng
sc.render.resolution_x, sc.render.resolution_y = 540, 960
if eng == 'CYCLES':
    sc.cycles.samples = 24; sc.cycles.use_denoising = True
sc.render.filepath = out
bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=out.replace('.png', '.blend'))

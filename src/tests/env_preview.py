"""Environment + render-engine timing preview.  python env_preview.py outdir ENGINE"""
import sys, os, math, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import bpy
from lib import util as U, character as C, env as E, look as L, anim as A

out, eng = sys.argv[1], sys.argv[2]
U.reset_scene()
root = bpy.context.scene.collection
E.build_street(root); E.build_house(root); E.build_hospital(root); E.build_props(root)
cars = U.coll('CARS', root)
taxi = E.build_car('taxi', 'taxi', (0.95, 0.45, 0.08), cars); taxi.location = (6, 2.0, 0)
amb = E.build_car('amb', 'ambulance', (1, 1, 1), cars); amb.location = (-8, 5.2, 0)
hu = C.build(C.HUDA); hi = C.build(C.HIND)
A.pose(hu, 1, root=(-3.4, -0.6, E.SIDE_Z), root_rot=math.pi * 0.85)
A.pose(hi, 1, A.HOLD_RABBIT, root=(-2.8, -0.75, E.SIDE_Z), root_rot=math.pi * 0.9)
A.expr(hu, 1, 'gentle'); A.expr(hi, 1, 'sad')
L.setup_render(eng, (540, 960), samples=8 if eng == 'CYCLES' else 32)
L.apply_mood(1, 'warm_morning')
cam = L.camera('CAM'); bpy.context.scene.camera = cam
shots = {
    'street': ((-1.0, -2.6, 1.2), (-2.5, 2.0, 1.2), 30),
    'shop':   ((-2.0, -1.2, 1.2), (0.0, 9.5, 1.4), 28),
    'living': ((E.HOUSE_O.x + 4.8, 0.6, 1.3), (E.HOUSE_O.x + 2.0, 4.0, 0.6), 24),
    'kitchen': ((E.HOUSE_O.x + 8.2, 0.8, 1.5), (E.HOUSE_O.x + 7.2, 4.6, 0.9), 24),
    'hospital': ((E.HOSP_O.x - 1.0, -2.8, 1.6), (E.HOSP_O.x + 0.6, 0.8, 0.7), 26),
}
sc = bpy.context.scene
for nm, (eye, tgt, lens) in shots.items():
    d = L.aim(cam, eye, tgt); cam.data.lens = lens; cam.data.dof.focus_distance = d
    if nm in ('living', 'kitchen'):
        L.apply_mood(1, 'interior_warm')
    if nm == 'hospital':
        L.apply_mood(1, 'hospital')
    sc.render.filepath = os.path.join(out, f'env_{nm}_{eng}.png')
    t = time.time(); bpy.ops.render.render(write_still=True); print('TIME', nm, eng, round(time.time() - t, 1), flush=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out, 'env_preview.blend'))

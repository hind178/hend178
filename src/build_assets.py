"""Build and LOCK the reusable assets for the series.

  shared_assets/hind.blend   Hind rig + meshes + rabbit + reusable actions
  shared_assets/huda.blend   Huda rig + meshes + reusable actions
  shared_assets/adults.blend Mother, Neighbour, Shopkeeper, crowd (same rig)
  shared_assets/environments.blend  street+shop, house, hospital, vehicles, props
Run: python build_assets.py"""
import sys, os, json, math
sys.path.insert(0, os.path.dirname(__file__))
import bpy
from lib import util as U, character as C, anim as A, env as E

OUT = os.path.join(U.ROOT, 'shared_assets')

ADULTS = [
    C.adult('Mother', 'mother', cloth=(0.42, 0.1, 0.13), cloth2=(0.85, 0.78, 0.66), seed=21),
    C.adult('Neighbour', 'abaya', cloth=(0.03, 0.03, 0.035), cloth2=(0.035, 0.035, 0.04), skin=(0.66, 0.46, 0.34), seed=22, H=1.6),
    C.adult('Shopkeeper', 'man', cloth=(0.78, 0.76, 0.7), hair=(0.22, 0.2, 0.18), hair_style='short_male', male=True, H=1.72, skin=(0.62, 0.42, 0.3), seed=23),
    C.adult('Man1', 'man', cloth=(0.45, 0.47, 0.5), hair_style='short_male', male=True, H=1.75, seed=24),
    C.adult('Man2', 'man', cloth=(0.42, 0.3, 0.2), hair_style='short_male', male=True, H=1.7, skin=(0.6, 0.4, 0.28), seed=25),
    C.adult('Man3', 'man', cloth=(0.85, 0.85, 0.82), hair_style='short_male', male=True, H=1.78, seed=26),
    C.adult('Woman1', 'abaya', cloth=(0.03, 0.03, 0.035), cloth2=(0.04, 0.04, 0.045), seed=27, H=1.6),
    C.adult('Woman2', 'abaya', cloth=(0.05, 0.04, 0.05), cloth2=(0.3, 0.12, 0.2), seed=28, H=1.58),
]


def store_meta(ch):
    ch.arm['dims'] = json.dumps(ch.dims)
    ch.arm['spec'] = json.dumps({k: v for k, v in ch.spec.items()})
    ch.arm['mouth'] = ch.mouth.name


def reusable_actions(ch):
    """Bake canonical cycles as named Actions (fake user) for Episode 2+."""
    acts = {}
    def bake(name, fn):
        ch.arm.animation_data_clear()
        if ch.mouth.data.shape_keys.animation_data:
            ch.mouth.data.shape_keys.animation_data_clear()
        C.reset_pose(ch)
        fn()
        act = ch.arm.animation_data.action
        act.name = f'{ch.name}_{name}'; act.use_fake_user = True
        acts[name] = act
    H = ch.spec['H']
    bake('walk_cycle', lambda: A.walk(ch, 1, 32, [(0, 0), (0, -0.42 * H * 2)]))
    bake('run_cycle', lambda: A.walk(ch, 1, 20, [(0, 0), (0, -0.75 * H * 2)], run=True))
    bake('wave', lambda: (A.pose(ch, 1), A.wave(ch, 1, 36, 'L')))
    bake('idle_breathe', lambda: (A.pose(ch, 1), A.breathe(ch, 1, 90)))
    bake('blink', lambda: [A.kb(ch, 'lid.' + s, f, rot=(v, 0, 0)) for s in 'LR'
                           for f, v in ((1, C.LID_OPEN), (3, C.LID_CLOSED), (6, C.LID_OPEN))])
    bake('sit_floor', lambda: A.pose(ch, 1, A.SIT_FLOOR))
    bake('kneel', lambda: A.pose(ch, 1, A.KNEEL))
    bake('pinky_promise', lambda: A.pose(ch, 1, A.PINKY_OUT_R))
    ch.arm.animation_data_clear()
    C.reset_pose(ch)
    return acts


def save(path, keep_colls):
    """Write only the given collections (and their dependencies) to path."""
    bpy.data.libraries.write(path, set(keep_colls), fake_user=True, compress=True)


def main():
    os.makedirs(OUT, exist_ok=True)
    U.reset_scene()
    hind = C.build(C.HIND); store_meta(hind)
    rab = C.build_rabbit('Rabbit')
    reusable_actions(hind)
    rab.users_collection[0].name = 'PROP_Rabbit'
    acts = [a for a in bpy.data.actions if a.name.startswith('Hind_')]
    bpy.data.libraries.write(os.path.join(OUT, 'hind.blend'),
                             {hind.coll, rab.users_collection[0], *acts}, fake_user=True, compress=True)
    huda = C.build(C.HUDA); store_meta(huda)
    reusable_actions(huda)
    acts = [a for a in bpy.data.actions if a.name.startswith('Huda_')]
    bpy.data.libraries.write(os.path.join(OUT, 'huda.blend'), {huda.coll, *acts}, fake_user=True, compress=True)
    adults = []
    for sp in ADULTS:
        ch = C.build(sp); store_meta(ch); adults.append(ch)
    bpy.data.libraries.write(os.path.join(OUT, 'adults.blend'), {a.coll for a in adults}, fake_user=True, compress=True)
    root = U.coll('ENVIRONMENTS')
    E.build_street(root); E.build_house(root); E.build_hospital(root); E.build_props(root)
    cars = U.coll('CARS', root)
    for nm, kind, col in (('Taxi', 'taxi', (0.95, 0.45, 0.08)), ('Sedan', 'sedan', (0.82, 0.8, 0.74)),
                          ('Sedan2', 'sedan', (0.35, 0.12, 0.1)), ('Van', 'van', (0.2, 0.35, 0.65)),
                          ('Ambulance', 'ambulance', (1, 1, 1))):
        o = E.build_car(nm, kind, col, cars); o.location = (0, 0, -80)
    bpy.data.libraries.write(os.path.join(OUT, 'environments.blend'), {root}, fake_user=True, compress=True)
    print('ASSETS OK')


if __name__ == '__main__':
    main()

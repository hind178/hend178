"""V6 matte refinement. RGB pixels are copied unchanged from cleaned_original.png;
alpha = min(cleaned alpha, local ISNet matte of references/approved_group.png).
This can only REMOVE leftover wall/floor pixels; it never adds or recolours anything."""
from pathlib import Path
import numpy as np, json, hashlib
from PIL import Image, ImageFilter
P = Path(__file__).resolve().parents[1]
OFFSETS = {'Hind': (535, 22), 'Loreen': (957, 13), 'Lizette': (165, 15)}  # exact pixel match in approved_group.png
M = Image.open(P/'production/group_matte_isnet_general.png').convert('L').filter(ImageFilter.MaxFilter(3))
M = np.asarray(M).astype(np.float32)/255
out = {}
for c, (ox, oy) in OFFSETS.items():
    src = np.asarray(Image.open(P/f'characters/{c}/cleaned_original.png')).copy()
    g = np.asarray(Image.open(P/'references/approved_group.png').convert('RGB'))
    h, w = src.shape[:2]
    opaque = src[..., 3] == 255
    assert (g[oy:oy+h, ox:ox+w][opaque] == src[..., :3][opaque]).all(), f'{c}: offset mismatch'
    m = np.clip((M[oy:oy+h, ox:ox+w]-0.15)/0.6, 0, 1)*255
    src[..., 3] = np.minimum(src[..., 3], m).astype(np.uint8)
    dst = P/f'characters/{c}/composite_v6.png'
    Image.fromarray(src).save(dst)
    out[str(dst.relative_to(P))] = hashlib.sha256(dst.read_bytes()).hexdigest()
(P/'production/composite_v6_lock.json').write_text(json.dumps(out, indent=2))
print(out)

from pathlib import Path
import json, hashlib
root=Path(__file__).resolve().parent
manifest=json.loads((root/'identity_lock.json').read_text())
for name, expected in manifest.items():
    assert hashlib.sha256((root/name).read_bytes()).hexdigest()==expected, f'Changed identity asset: {name}'
print(f'Verified {len(manifest)} locked assets')

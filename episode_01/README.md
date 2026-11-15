# حكايات جدتي — My Grandmother's Tales
## Story: Stay Here, I'll Be Back · Episode 01: The Promise

Vertical 9:16 · 1080×1920 · 30 fps · 190.87 s · locked to the master narration (190.85 s).

### Deliverables
| Path | What |
|---|---|
| `episode_01/final.mp4` | H.264 (High) + AAC 192k, faststart |
| `episode_01/cover.png` | Vertical cover image (1080×1920) |
| `episode_01/story.blend` | Full animated scene: 55 shots, camera markers, warm→cool lighting arc |
| `episode_01/scene_map.md` | Timestamped shot list / scene map with the Arabic narration per shot |
| `episode_01/audio/narration.mp3` | Master narration (unchanged) |
| `shared_assets/hind.blend` | Hind (5) rig + meshes + white rabbit + reusable actions |
| `shared_assets/huda.blend` | Huda (7) rig + meshes + reusable actions |
| `shared_assets/adults.blend` | Mother, Neighbour, Shopkeeper, crowd — same rig |
| `shared_assets/environments.blend` | Street + grocery shop, family house, hospital, vehicles, props |
| `shared_assets/textures/` | Procedural textures (Huda's dress print, carpet, tabouk brick, tiles) |
| `src/` | All executable Python source |

### Rebuild everything
Requires Blender as a Python module (`pip install bpy==5.2.4`, Python 3.13), numpy, scipy, soundfile, FFmpeg.
```bash
cd src
python build_assets.py        # characters, rigs, actions, environments -> shared_assets/*.blend
python build_story.py         # episode_01/story.blend + scene_map.md
python render.py -- --out ../episode_01/frames --step 2 --offset 0 --pct 50 --samples 6   # pass 1 (even frames)
python render.py -- --out ../episode_01/frames --step 2 --offset 1 --pct 50 --samples 6   # pass 2 (fill to true 30 fps)
python audio_mix.py           # score + ambience + SFX under the narration -> audio/mix.wav
python encode.py              # -> episode_01/final.mp4
```

### Source map
- `src/lib/character.py` – one procedural builder for every character: sculpted head (lathe + shape function),
  eyeballs with iris shader, rotating eyelids + lashes, brows, mouth with shape keys (smile/sad/open/oh/cry),
  hair shells (Huda's side-swept bob + white clip; Hind's straight bangs + black fuzzy headpiece with gold pins),
  outfits from the photograph, finger/little-finger bones.
- `src/lib/anim.py` – reusable animation: poses, walk/run cycle, blinks, breathing, expressions, talk, wave, sobbing.
- `src/lib/env.py` – Iraqi neighbourhood (yellow tabouk brick houses, black/yellow curbs, power lines, roof water tanks,
  palms), the grocery shop, house interior (doshak cushions, carpet, CRT TV, kitchen), hospital room, cars/van/ambulance.
- `src/lib/look.py` – render settings, sun/sky moods (warm → tense → cool → dusk), cameras.
- `src/shotlist.py` – the 55-shot timeline (cuts on detected narration pauses).
- `src/build_story.py` – stages and animates every shot; `src/render.py`, `src/audio_mix.py`, `src/encode.py`.

### Notes on how it was made
- Narration was transcribed locally (Whisper-small via sherpa-onnx) and segmented with FFmpeg `silencedetect`;
  every cut sits on a pause of the grandmother's voice.
- No GPU was available: Eevee needs OpenGL, so rendering uses Cycles on CPU at 540×960 with OIDN denoising,
  upscaled (Lanczos) to 1080×1920.
- The accident is never shown: brakes, crowd, a rolling tomato and the torn bag carry it. The hospital scene contains
  no medical detail and Huda's recovery is not revealed.
- All music and sound effects are synthesised in `audio_mix.py`; the narration is used unchanged and ducks the bed.

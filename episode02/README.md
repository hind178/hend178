# Episode 02 — بداية صداقة جميلة
Continuation of Episode 01 using the same rigs/engine (copied into `src/`).
- `tools/script.json`: narration locked to 28 timed lines (pause detection on the master audio).
- `node src/build_backgrounds.js` (new: hotel corridor, room day/night, restaurant, sweets shop, night street, amusement park).
- `node src/render.js shots 1 4` — per-shot render with resume (`build/shots/NN.mp4`; finished shots are skipped).
- `python3 src/audio/sound_design.py` — score/ambience/SFX under the untouched narration.
- Final pass: tilt-shift miniature blur (top/bottom mask) + grade via FFmpeg → `output/Episode_02_Final.mp4`.

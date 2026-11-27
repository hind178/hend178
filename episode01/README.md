# My Grandmother's Tales — Episode 01: سفرة ما چانت بالحسبان

Code-generated 2D animated short (1080×1920, 30 fps, H.264 + AAC), synced to the original narration.

## Pipeline
1. `python3 tools/align.py` — aligns the script to the narration via pause detection → shot timing.
2. `python3 tools/envelope.py` — narration loudness per frame (lip-sync for quoted dialogue).
3. `node src/build_backgrounds.js` / `node src/build_extras.js` — cached backdrops & background-student sprites.
4. `node src/render.js stills <t…>` — quality-gate stills; `node src/render.js video 1` — full render (4 parallel Chromium workers → FFmpeg).
5. `python3 src/audio/sound_design.py` — original score, ambiences & SFX, ducked under the untouched narration.
6. `node src/cover.js` — Instagram cover.

## Reusable for Episodes 02–03
`src/characters/{hind,loreen,lizette}.js` + `rig.js`: articulated rigs (shoulder/elbow FK with forearm foreshortening, 4 hand poses,
blink, eye-look, squint, brows, mouth/lip-sync, head turn & tilt, breathing, walk cycle, sitting, skirt/hair/scarf sway).

# حكايات جدتي — My Grandmother's Tales
## Episode 02 · The Paper Crane (الطير الورقي)

Maryam finds the yellowed crane in her father's old box. Haru recognises his son's red sun and reads the hidden letter. Her father comes to the station and admits he was on the same train. The episode ends where Episode 03 begins.

Vertical 9:16, 1080×1920, 30 fps, H.264 + AAC, 113 s, timed to the supplied narration.

| Path | What it is |
|---|---|
| `render/ep02_the_paper_crane.mp4` | Final video (full resolution) |
| `render/ep02_the_paper_crane_mobile.mp4` | Lighter 720p version |
| `src/ep02_shots.py` | The 27-shot timeline |
| `src/render_ep02.py` | Renderer (preview and full video) |
| `src/audio_ep02.py` | Sound design and score, mixed under the narration |
| `timing/` | Timing sheet (`.md` and `.csv`) and word-level transcript |
| `assets/audio/` | Original narration, final mix, music and effects without the voice |

The characters, sets, effects and renderer are shared with Episode 03 (`../ep03-harus-last-journey/src`), so both episodes use the same models.

```bash
python3 src/render_ep02.py preview check.png 5 30 90
python3 src/render_ep02.py video build/ 3
python3 src/audio_ep02.py build/mix.wav build/bed.wav
ffmpeg -i build/picture.mp4 -i build/mix.wav -c:v libx264 -crf 21 -c:a aac -b:a 192k out.mp4
```

These are code-generated 2D animations, not hand-drawn frame by frame. See the Episode 03 README for the pipeline and its limits.

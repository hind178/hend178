Identity-locked Episode 01 revision. Run python render_animatic.py for a limited preview. Read CLAUDE_NEXT.md for unresolved work. Original narration unchanged. No final animation claimed.

V3: cleaned masks, empty bus background, and 5-second identity/compositing test.

V4: new empty hotel lobby, updated final shot and identity hash verification.

V5: 13-shot storyboard, clean full-resolution backgrounds, two-person bus framing, and source renderer for limited motion. Full static storyboard is available separately; full motion render not completed. See CLAUDE_NEXT.md.

V6 (final): `Episode_01_Final.mp4` — 1080×1920, 30 fps, 3212 frames, 107.076 s, original narration untouched.
Pipeline: `python verify_identity.py` → `python render_final.py --all` (22 separately rendered scenes in
`production/scenes/`, not committed — reproducible) → `python assemble_final.py` (concat + narration + validation,
report in `production/final_validation.json`). Shot timing is aligned to measured narration pauses and Whisper word
timestamps (`production/narration_transcript_whisper.json`, plan in `production/final_shot_plan.json`).
`Episode_01_Final.ar.srt` is a reviewed Arabic subtitle sidecar (not burned in). QC sheet: `production/qc_contact.py`.

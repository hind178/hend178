# Identity-locked revision
Use ONLY characters/<name>/approved_original.png as the canonical image. These are cutouts from references/approved_group.png. The unverified_assets directory contains old angles, poses and expressions; do not use them until individually checked against the canonical image. Do not overwrite canonical images.
The renderer is a limited animatic, not articulated animation. Its timings are approximate. Hind carries a suitcase in the canonical image; create verified suitcase-free and seated poses before classroom/bus production. Loreen has crossed arms; do not pretend she is gesturing.
Remaining: clean residual mask edges, create verified articulated layers and seated/walking poses, replace low-resolution interior and mountain backgrounds, align Arabic narration, add licensed audio if available, and render 1080x1920 at 30fps. Do not use paid APIs or regenerate identities. Inspect actual renders.

## V3 update
Use cleaned_original.png for compositing; approved_original.png remains the immutable reference. The alpha masks were manually cleaned in selected areas; small residual edges may remain. The new backgrounds/bus_interior_clean.png is a full-resolution empty bus set; use it only after creating verified seated poses and foreground seat masks. Do not place standing full-body cutouts on seats. render_test.py generates a 5-second 1080x1920/30fps camera-only identity test. It is silent and not an animation or narration synchronization test. No verified new poses, final audio alignment, or full episode render yet.

## V4 update
Added a full-resolution empty hotel lobby and used it for the final cliffhanger preview. No generated replacement characters are approved. Run `python verify_identity.py` before rendering; it verifies the exact six canonical/cleaned sprite files against their V3 bytes. It does not verify new poses visually. Mountain road and classroom still use low-resolution references; seated poses, articulation, timing verification and final render remain incomplete. Do not use the rejected generated bus scenes. The lobby preview is a static composite, not a final shot.

## V5 handoff
`render_v5.py` uses the six locked sprites, high-resolution bus and lab backgrounds, 13 editorial shots, subtle whole-sprite sway and camera motion. `preview_concat.txt` and `shot_previews/` reproduce the complete static storyboard with the original narration. The moving render was interrupted at 70 seconds by the execution time limit; do not present it as a completed video. The separate full storyboard MP4 is a timing preview, not animation. The bus inserts are upper-body crops, not verified seated poses; the lab is empty to avoid showing a suitcase in class. Hotel exterior replaces the low-resolution mountain road as an editorial transition. No licensed music supplied; original narration only. Remaining: create verified seated and articulated poses, align the actual Arabic narration, add cleared sound effects/music, and render and inspect full motion at 1080x1920/30fps. Do not regenerate the identities. Run verify_identity.py before and after.

## V6 status
Done: full 22-shot motion render at 1080x1920/30fps synced to the real narration; edge remnants removed with a
min(alpha, ISNet matte) refinement (`characters/*/composite_v6.png`, made by `production/make_composite_sprites.py`;
RGB pixels identical to cleaned_original, hashes in `production/composite_v6_lock.json`). Locked V3 files untouched.
Still limited animation (whole-sprite motion only: walk bob, breathing, sway, hops, nods, camera, DOF, light).
Not done / would need new approved art: articulated limbs, lip-sync, blinks, true seated poses (bus uses
waist-up medium shots), music/SFX (none licensed).

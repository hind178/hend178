#!/bin/sh
# One command: renders the 5-second test and all preview stills into output/.
set -e
LIB=${LIB:-/root/lemo-opuscar}
export LIB
HERE=$(cd "$(dirname "$0")" && pwd)
[ -f "$LIB/core/render/video.mjs" ] || { echo "set LIB to the Lemo-Opuscar library folder"; exit 1; }
# software-WebGL hosts: point at a matching headless shell if playwright's own is missing
# export PLAYWRIGHT_CHROME=/path/to/chrome-headless-shell
mkdir -p "$HERE/out" "$HERE/output"
cd "$LIB"
node core/render/video.mjs "$HERE" --fps 30 --workers 3 --size 1080x1920 --out "$HERE/out/video.mp4"
# final H.264 MP4: 1080×1920, 30 fps, no audio, no watermark
ffmpeg -y -loglevel error -i "$HERE/out/video.mp4" -c:v libx264 -preset slow -crf 16 -pix_fmt yuv420p -r 30 -movflags +faststart -an "$HERE/output/Miniature_Style_Test.mp4"
P="node $HERE/tools/png.mjs $HERE"
$P "$HERE/output/Hind_Preview.png"       --t 4.9 --q mode=hind    --size 1080x1920
$P "$HERE/output/Loreen_Preview.png"     --t 4.9 --q mode=loreen  --size 1080x1920
$P "$HERE/output/Lizette_Preview.png"    --t 4.9 --q mode=lizette --size 1080x1920
$P "$HERE/output/Group_Preview.png"      --t 5   --q mode=group   --size 1080x1920
$P "$HERE/output/University_Diorama.png" --t 0   --q mode=diorama --size 1920x1080

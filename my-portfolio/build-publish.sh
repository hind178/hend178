#!/usr/bin/env bash
# يجهّز مجلد publish/ بملفات الموقع فقط (المرحلة 08 من الدليل).
# التشغيل: bash build-publish.sh   — من داخل مجلد my-portfolio
set -euo pipefail
cd "$(dirname "$0")"
rm -rf publish publish.zip
mkdir -p publish/assets/fonts
cp index.html project.html 404.html style.css publish/
cp assets/*.webp assets/favicon.svg publish/assets/
cp assets/fonts/*.woff2 assets/fonts/OFL-LICENSE.txt publish/assets/fonts/
(cd publish && zip -qr ../publish.zip .)
echo "publish/ جاهز:"; find publish -type f | sort; du -sh publish publish.zip

#!/usr/bin/env bash
# يجهّز مجلد publish/ بملفات الموقع فقط (المرحلة 08 من الدليل).
# التشغيل: bash build-publish.sh   — من داخل مجلد my-portfolio
set -euo pipefail
cd "$(dirname "$0")"
rm -rf publish publish.zip
mkdir -p publish/assets/fonts
cp ./*.html style.css site.js publish/
cp -r en publish/
cp assets/*.webp assets/favicon.svg publish/assets/
cp assets/fonts/*.woff2 assets/fonts/OFL-LICENSE.txt publish/assets/fonts/
(cd publish && zip -qr ../publish.zip .)
echo "publish/ جاهز:"; find publish -type f | sort; du -sh publish publish.zip

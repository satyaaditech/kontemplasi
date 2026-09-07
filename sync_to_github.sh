#!/usr/bin/env bash
set -e

# Sync markdown and images from ~/share/renungan to ~/kontemplasi/renungan
SRC="/home/satyaaditech/share/renungan"
DEST="/home/satyaaditech/kontemplasi/renungan"

mkdir -p "$DEST"
rsync -av --include="*.md" --include="*.png" --include="*.jpg" --include="*.jpeg" --include="*.webp" --exclude="*" "$SRC/" "$DEST/"

# Rebuild index.html
python3 /home/satyaaditech/kontemplasi/build_pustaka.py

# Git commit and push
cd /home/satyaaditech/kontemplasi
if [[ -n $(git status -s) ]]; then
    git add .
    git commit -m "Auto-update Pustaka Penyiswaan: $(date '+%Y-%m-%d %H:%M')"
    git push origin main
    echo "Pustaka updated and pushed to GitHub successfully."
else
    echo "No changes to commit."
fi

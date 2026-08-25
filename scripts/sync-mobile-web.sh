#!/usr/bin/env bash
set -euo pipefail

# Sync the canonical mobile-web bundle into the Android app assets.
# Usage: from repo root: bash scripts/sync-mobile-web.sh

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="${ROOT}/mobile-web/"
DST="${ROOT}/android-app/app/src/main/assets/"

if [[ ! -d "${SRC}" ]]; then
  echo "Source bundle not found at ${SRC}" >&2
  exit 1
fi

mkdir -p "${DST}"
rsync -av --delete "${SRC}" "${DST}"

echo "Synced mobile-web into ${DST}"

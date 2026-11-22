#!/usr/bin/env bash
# Assemble a userdata installer from the public forks and a locally built H700 binary.
set -euo pipefail
if [ "$#" -ne 3 ]; then
    echo "Usage: prepare-kit.sh BUNDLES_CHECKOUT BUILT_EMULATIONSTATION NEW_KIT_DIRECTORY" >&2
    exit 2
fi
here=$(cd "$(dirname "$0")" && pwd)
bundles=$(cd "$1" && pwd)
binary=$2
dest=$3
tools_sha=5942f8a9681d0cfcb52f4658f56d32b367bdcd69
source_sha=4215ca1eb833688a7b34f8f0b2c026584b9110b9
unit=units/07-es-api-events/install
[ -f "$binary" ] && [ ! -e "$dest" ] || { echo "Supply a built binary and a new kit directory" >&2; exit 1; }
python3 - "$binary" <<'PY'
from pathlib import Path
import sys
with Path(sys.argv[1]).open('rb') as stream:
    header=stream.read(20)
if len(header)!=20 or header[:6]!=b'\x7fELF\x02\x01' or int.from_bytes(header[18:20],'little')!=183:
    sys.exit("Expected an AArch64 ELF executable")
PY
mkdir "$dest"
trap 'rm -rf -- "$dest"' EXIT
git -C "$bundles" archive "$tools_sha:$unit" | tar -x -C "$dest"
cp "$binary" "$dest/payload/emulationstation"
cp "$here/resume/emulatorlauncher" "$dest/resume-emulatorlauncher"
ES_COMMIT="$source_sha" bash "$dest/build/make-manifest.sh"
trap - EXIT

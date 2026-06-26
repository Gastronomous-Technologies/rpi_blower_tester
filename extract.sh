#!/bin/bash
#
# Extract a blower-tester release bundle on a fixture Pi.
#
# Copy this script next to the rpi_blower_tester*.zip, then run it. The bundle's
# files are extracted INTO THIS DIRECTORY (no sub-folder). Works even without
# `unzip` installed (falls back to python3), and restores the executable bits.
#
# Usage:
#   ./extract.sh [bundle.zip] [--install]
#     bundle.zip   the bundle to extract (auto-detected if omitted)
#     --install    after extracting, run install.sh + reboot

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$HERE"

ZIP=""
DO_INSTALL=false
for arg in "$@"; do
    case "$arg" in
        --install) DO_INSTALL=true ;;
        *) ZIP="$arg" ;;
    esac
done

# Auto-detect the bundle if not given (newest matching zip next to this script).
if [ -z "$ZIP" ]; then
    ZIP=$(ls -t rpi_blower_tester*.zip 2>/dev/null | head -1 || true)
fi
if [ -z "$ZIP" ] || [ ! -f "$ZIP" ]; then
    echo "Error: no bundle found. Usage: ./extract.sh <bundle.zip>" >&2
    exit 1
fi
ZIP="$(cd "$(dirname "$ZIP")" && pwd)/$(basename "$ZIP")"   # absolute

echo "Extracting $(basename "$ZIP") into this directory ..."
if command -v unzip >/dev/null 2>&1; then
    unzip -o "$ZIP" -d "$HERE"
elif command -v python3 >/dev/null 2>&1; then
    python3 -m zipfile -e "$ZIP" "$HERE"
elif command -v bsdtar >/dev/null 2>&1; then
    bsdtar -C "$HERE" -xf "$ZIP"
else
    echo "Error: need 'unzip', 'python3', or 'bsdtar' to extract." >&2
    exit 1
fi

if [ ! -f "$HERE/install.sh" ]; then
    echo "Error: install.sh not found after extraction - is this the right bundle?" >&2
    exit 1
fi

# python3's zipfile extractor drops the executable bit, so restore it.
for f in install.sh uninstall.sh power_on_dut.sh rpi_blower_tester; do
    [ -f "$HERE/$f" ] && chmod +x "$HERE/$f"
done

echo ""
echo "Extracted into $HERE"

if [ "$DO_INSTALL" = true ]; then
    echo "Running installer..."
    sudo ./install.sh
    echo "Install done - rebooting."
    sudo reboot
else
    echo "Next:"
    echo "  sudo ./install.sh && sudo reboot"
fi

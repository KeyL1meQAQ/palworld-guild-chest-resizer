#!/usr/bin/env bash
# Sets up the Python environment for the Guild Chest Resizer.
# Safe to re-run; skips anything already done.
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

python_bin="$(command -v python3 || command -v python || true)"
if [ -z "$python_bin" ]; then
    echo "Python 3.9+ not found on PATH." >&2
    exit 1
fi

if [ ! -x "$root/venv/bin/python" ]; then
    echo "Creating virtual environment..."
    "$python_bin" -m venv "$root/venv"
else
    echo "Virtual environment already present."
fi
venv_py="$root/venv/bin/python"

echo "Installing palworld-save-tools (pinned)..."
"$venv_py" -m pip install --quiet --disable-pip-version-check -r "$root/requirements.txt"

pkg="$("$venv_py" -c 'import os,palworld_save_tools;print(os.path.dirname(palworld_save_tools.__file__))')"
echo "Patching palworld_save_tools for Palworld 0.6 at: $pkg"
cp -f "$root/patches/palsav.py" "$pkg/palsav.py"
cp -f "$root/patches/rawdata/"*.py "$pkg/rawdata/"

# Upstream zao/ooz only publishes Windows x64 binaries, so there is nothing to fetch
# here. Build ooz yourself and point PALWORLD_OOZ_DLL_PATH at the shared library, or
# drop it in as ooz/libooz.so and it will be picked up automatically.
if [ ! -e "$root/ooz/libooz.so" ] && [ -z "${PALWORLD_OOZ_DLL_PATH:-}" ]; then
    cat <<'EOF'

NOTE: no libooz found.
Oodle-compressed ("PlM") saves - anything from Palworld 0.6 onward - cannot be read
without it. Upstream publishes Windows builds only, so on Linux/macOS:

    git clone https://github.com/zao/ooz && cd ooz
    cmake -B build -DCMAKE_BUILD_TYPE=Release && cmake --build build

then copy the resulting shared library to ooz/libooz.so here, or export
PALWORLD_OOZ_DLL_PATH=/path/to/libooz.so

Older zlib ("PlZ") saves work without it.
EOF
fi

echo
echo "Setup complete. Try:"
echo "    ./venv/bin/python guild_chest.py list"

#!/usr/bin/env python3
"""Download libooz.dll from the upstream zao/ooz release into ooz/.

The binary is deliberately NOT redistributed with this project: zao/ooz publishes no
license at all, so shipping a copy would be a rights problem. Fetching it from the
upstream release on demand — the way a package manager pulls from its own registry —
avoids that. Same approach as quadrantbs/palworld-hostfix-toolkit.

Upstream only publishes Windows x64 builds. On Linux/macOS, build ooz yourself and
point PALWORLD_OOZ_DLL_PATH at the resulting shared library.
"""

import io
import pathlib
import sys
import urllib.request
import zipfile

OOZ_VERSION = "0.2.4"
RELEASE_URL = (
    f"https://github.com/zao/ooz/releases/download/v{OOZ_VERSION}/"
    f"bun-{OOZ_VERSION}-x64-Release.zip"
)
EXPECTED_SHA256 = "473d94ec899e00e30e4b360c3e9d3b8e949d5a3ae6e962b0f090ba439249c7d7"

DEST_DIR = pathlib.Path(__file__).resolve().parent / "ooz"


def main():
    dll_path = DEST_DIR / "libooz.dll"
    if dll_path.exists() and "--force" not in sys.argv:
        print(f"Already present: {dll_path} (use --force to re-download)")
        return

    print(f"Downloading {RELEASE_URL}")
    with urllib.request.urlopen(RELEASE_URL) as resp:
        archive_bytes = resp.read()

    DEST_DIR.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(io.BytesIO(archive_bytes)) as zf:
        names = [n for n in zf.namelist() if n.lower().endswith("libooz.dll")]
        if not names:
            raise SystemExit(f"libooz.dll not in archive; contents: {zf.namelist()}")
        payload = zf.read(names[0])

    import hashlib

    digest = hashlib.sha256(payload).hexdigest()
    if digest != EXPECTED_SHA256:
        raise SystemExit(
            f"Checksum mismatch for libooz.dll!\n"
            f"  expected {EXPECTED_SHA256}\n  got      {digest}\n"
            "Refusing to install. Upstream may have re-published the release."
        )

    dll_path.write_bytes(payload)
    print(f"Extracted {dll_path}")
    print(f"SHA256 verified: {digest}")


if __name__ == "__main__":
    main()

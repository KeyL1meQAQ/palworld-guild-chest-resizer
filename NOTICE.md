# Third-party components

## palworld-save-tools — MIT

<https://github.com/cheahjs/palworld-save-tools> by Jun Siang Cheah. Installed as a
pinned dependency (`palworld-save-tools==0.24.0`). The files in `patches/` are modified
copies of files from this project.

```
MIT License

Copyright (c) 2024 Jun Siang Cheah

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## palworld-hostfix-toolkit — MIT

<https://github.com/quadrantbs/palworld-hostfix-toolkit>. The contents of `patches/`
(the `PlM`/Oodle support in `palsav.py` and the Palworld 0.6 `rawdata/` struct parsers)
come from this project's `patched_palworld_save_tools/` directory. The on-demand
`libooz` fetch approach is also taken from it.

```
MIT License

Copyright (c) 2026

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## ooz / libooz — NOT redistributed

<https://github.com/zao/ooz> is a clean-room open-source reimplementation of Oodle
Kraken **decompression**. It is *not* Epic Games' or RAD Game Tools' proprietary code,
and this project contains no Oodle compressor.

**Upstream publishes no license.** Because of that, `libooz.dll` is deliberately not
included in this repository or in any release archive. `fetch_ooz.py` downloads it
from the upstream GitHub release at setup time and verifies its SHA256. If you
redistribute this project, do not add the binary — leave the fetch step in place.

Nothing here bundles, links against, or reimplements Oodle *compression*. Edited saves
are written with zlib, which Palworld still accepts.

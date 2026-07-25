<#
Sets up the Python environment for the Guild Chest Resizer.
Safe to re-run; skips anything already done.
#>
$ErrorActionPreference = "Stop"
$root = $PSScriptRoot

$python = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $python) { $python = (Get-Command py -ErrorAction SilentlyContinue).Source }
if (-not $python) {
    throw "Python not found on PATH. Install Python 3.9+ from https://python.org and re-run."
}

if (-not (Test-Path "$root\venv\Scripts\python.exe")) {
    "Creating virtual environment..."
    & $python -m venv "$root\venv"
} else {
    "Virtual environment already present."
}
$venvPy = "$root\venv\Scripts\python.exe"

"Installing palworld-save-tools (pinned)..."
& $venvPy -m pip install --quiet --disable-pip-version-check -r "$root\requirements.txt"
if ($LASTEXITCODE -ne 0) { throw "pip install failed" }

$pkg = & $venvPy -c "import os,palworld_save_tools;print(os.path.dirname(palworld_save_tools.__file__))"
"Patching palworld_save_tools for Palworld 0.6 at: $pkg"
Copy-Item "$root\patches\palsav.py"      "$pkg\palsav.py" -Force
Copy-Item "$root\patches\rawdata\*.py"   "$pkg\rawdata\"  -Force

"Fetching libooz.dll (Oodle decompressor, not redistributed - see NOTICE.md)..."
& $venvPy "$root\fetch_ooz.py"
if ($LASTEXITCODE -ne 0) { throw "could not obtain libooz.dll" }

""
"Setup complete. Try:"
"    .\run.ps1 list"

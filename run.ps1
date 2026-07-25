<#
Convenience wrapper so you don't have to remember the venv path.

    .\run.ps1 list
    .\run.ps1 resize 358
    .\run.ps1 resize 358 --save "C:\path\to\Level.sav"
#>
$ErrorActionPreference = "Stop"
$venvPy = "$PSScriptRoot\venv\Scripts\python.exe"
if (-not (Test-Path $venvPy)) { throw "venv missing - run .\setup.ps1 first" }
& $venvPy "$PSScriptRoot\guild_chest.py" @args
exit $LASTEXITCODE

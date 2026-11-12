param(
    [string]$Python = 'python',
    [string]$OutputDir = (Join-Path $PSScriptRoot 'release')
)
$ErrorActionPreference = 'Stop'
& (Join-Path $PSScriptRoot 'build-windows.ps1') -Python $Python
if ($LASTEXITCODE -ne 0) { throw 'Windows build failed.' }
& $Python -B (Join-Path $PSScriptRoot 'release_package.py') --exe (Join-Path $PSScriptRoot 'dist/ModelRoom.exe') --output $OutputDir
if ($LASTEXITCODE -ne 0) { throw 'Release packaging failed.' }

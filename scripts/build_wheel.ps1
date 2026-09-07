# Build a platform wheel with bundled ofd-cli.

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

& "$PSScriptRoot\build_ofd_cli.ps1"
$env:OFD2PDF_REQUIRE_BIN = "1"
Remove-Item -Recurse -Force dist, build -ErrorAction SilentlyContinue
uv run python -m build --wheel
Write-Host "Wheels in dist/:"
Get-ChildItem dist

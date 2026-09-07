# Build ofd-cli and install into src/ofd2pdf/bin (+ vendor/bin for local use).

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$VendorSrc = Join-Path $Root "vendor\ofd-utility"
$PkgBin = Join-Path $Root "src\ofd2pdf\bin"
$VendorBin = Join-Path $Root "vendor\bin"
$Manifest = Join-Path $VendorSrc "Cargo.toml"
$Repo = if ($env:OFD_UTILITY_REPO) { $env:OFD_UTILITY_REPO } else { "https://github.com/ofd-utility/ofd-utility.git" }

if (-not (Test-Path $Manifest)) {
    Write-Host "Cloning ofd-utility..."
    New-Item -ItemType Directory -Force -Path (Join-Path $Root "vendor") | Out-Null
    git clone --depth 1 $Repo $VendorSrc
}

Write-Host "Building ofd-cli (release)..."
cargo build --release --manifest-path $Manifest -p ofd-cli

New-Item -ItemType Directory -Force -Path $PkgBin | Out-Null
New-Item -ItemType Directory -Force -Path $VendorBin | Out-Null

$ExeWin = Join-Path $VendorSrc "target\release\ofd-cli.exe"
$ExeUnix = Join-Path $VendorSrc "target\release\ofd-cli"
if (Test-Path $ExeWin) {
    $Src = $ExeWin
    $Name = "ofd-cli.exe"
} else {
    $Src = $ExeUnix
    $Name = "ofd-cli"
}

Copy-Item $Src (Join-Path $PkgBin $Name) -Force
Copy-Item $Src (Join-Path $VendorBin $Name) -Force

# Drop the other platform's leftover name so wheels stay clean.
if ($Name -eq "ofd-cli.exe") {
    Remove-Item (Join-Path $PkgBin "ofd-cli") -ErrorAction SilentlyContinue
} else {
    Remove-Item (Join-Path $PkgBin "ofd-cli.exe") -ErrorAction SilentlyContinue
}

Write-Host "Installed: $(Join-Path $PkgBin $Name)"
Write-Host "Installed: $(Join-Path $VendorBin $Name)"

#!/usr/bin/env bash
# Build ofd-cli and install into src/ofd2pdf/bin (+ vendor/bin for local use).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENDOR_SRC="${ROOT}/vendor/ofd-utility"
PKG_BIN="${ROOT}/src/ofd2pdf/bin"
VENDOR_BIN="${ROOT}/vendor/bin"
MANIFEST="${VENDOR_SRC}/Cargo.toml"
OFD_UTILITY_REPO="${OFD_UTILITY_REPO:-https://github.com/ofd-utility/ofd-utility.git}"

if [[ ! -f "${MANIFEST}" ]]; then
  echo "Cloning ofd-utility..."
  mkdir -p "${ROOT}/vendor"
  git clone --depth 1 "${OFD_UTILITY_REPO}" "${VENDOR_SRC}"
fi

echo "Building ofd-cli (release)..."
cargo build --release --manifest-path "${MANIFEST}" -p ofd-cli

mkdir -p "${PKG_BIN}" "${VENDOR_BIN}"

if [[ -f "${VENDOR_SRC}/target/release/ofd-cli.exe" ]]; then
  SRC="${VENDOR_SRC}/target/release/ofd-cli.exe"
  NAME="ofd-cli.exe"
else
  SRC="${VENDOR_SRC}/target/release/ofd-cli"
  NAME="ofd-cli"
fi

cp -f "${SRC}" "${PKG_BIN}/${NAME}"
cp -f "${SRC}" "${VENDOR_BIN}/${NAME}"
chmod +x "${PKG_BIN}/${NAME}" "${VENDOR_BIN}/${NAME}" 2>/dev/null || true

# Drop the other platform's leftover name so wheels stay clean.
if [[ "${NAME}" == "ofd-cli.exe" ]]; then
  rm -f "${PKG_BIN}/ofd-cli"
else
  rm -f "${PKG_BIN}/ofd-cli.exe"
fi

echo "Installed: ${PKG_BIN}/${NAME}"
echo "Installed: ${VENDOR_BIN}/${NAME}"

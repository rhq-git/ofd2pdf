#!/usr/bin/env bash
# Build a platform wheel with bundled ofd-cli.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT}"

bash "${ROOT}/scripts/build_ofd_cli.sh"
export OFD2PDF_REQUIRE_BIN=1
rm -rf dist build
python -m build --wheel
echo "Wheels in dist/:"
ls -la dist/

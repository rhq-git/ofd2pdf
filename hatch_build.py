"""Hatchling build hook: mark wheels as platform-specific when ofd-cli is bundled."""

from __future__ import annotations

import os
import sysconfig
from pathlib import Path

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


def _platform_tag() -> str:
    # e.g. win-amd64 -> win_amd64, macosx-14.0-arm64 -> macosx_14_0_arm64
    return sysconfig.get_platform().replace("-", "_").replace(".", "_")


class CustomBuildHook(BuildHookInterface):
    """Attach platform tags when ``src/ofd2pdf/bin/ofd-cli*`` is present."""

    PLUGIN_NAME = "ofd2pdf-bin"

    def initialize(self, version: str, build_data: dict) -> None:
        bin_dir = Path(self.root) / "src" / "ofd2pdf" / "bin"
        binaries = [bin_dir / "ofd-cli", bin_dir / "ofd-cli.exe"]
        present = [p for p in binaries if p.is_file()]

        require = os.environ.get("OFD2PDF_REQUIRE_BIN", "").lower() in {
            "1",
            "true",
            "yes",
        }
        if require and not present:
            raise RuntimeError(
                "OFD2PDF_REQUIRE_BIN=1 but no ofd-cli found in src/ofd2pdf/bin. "
                "Run scripts/build_ofd_cli.sh (or .ps1) first."
            )

        if present:
            # Ship one wheel per OS/arch that works for all supported CPython versions.
            build_data["pure_python"] = False
            build_data["infer_tag"] = False
            build_data["tag"] = f"py3-none-{_platform_tag()}"

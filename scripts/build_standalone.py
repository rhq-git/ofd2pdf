#!/usr/bin/env python3
"""Build a standalone ofd2pdf binary with PyInstaller (onefile)."""

from __future__ import annotations

import os
import platform
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PKG_BIN = ROOT / "src" / "ofd2pdf" / "bin"


def ofd_cli_path() -> Path:
    names = ("ofd-cli.exe", "ofd-cli") if sys.platform == "win32" else ("ofd-cli", "ofd-cli.exe")
    for name in names:
        path = PKG_BIN / name
        if path.is_file():
            return path
    raise SystemExit(
        f"Missing ofd-cli in {PKG_BIN}. Run scripts/build_ofd_cli.sh|.ps1 first."
    )


def main() -> None:
    os.chdir(ROOT)
    cli = ofd_cli_path()
    # Dest path inside the onefile extract dir must match package_bin_dir().
    datas = f"{cli}{os.pathsep}ofd2pdf/bin"

    system = platform.system().lower()
    machine = platform.machine().lower()
    # PyInstaller appends .exe on Windows when needed.
    name = f"ofd2pdf-{system}-{machine}"

    dist = ROOT / "dist" / "standalone"
    work = ROOT / "build" / "pyinstaller"
    dist.mkdir(parents=True, exist_ok=True)

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--onefile",
        "--name",
        name,
        "--distpath",
        str(dist),
        "--workpath",
        str(work),
        "--paths",
        str(ROOT / "src"),
        "--add-data",
        datas,
        "--hidden-import",
        "PIL._tkinter_finder",
        str(ROOT / "src" / "ofd2pdf" / "__main__.py"),
    ]
    print("+", " ".join(cmd))
    subprocess.check_call(cmd)
    out = dist / name
    if not out.exists() and sys.platform == "win32":
        out = dist / f"{name}.exe"
    print(f"Built: {out}")


if __name__ == "__main__":
    main()

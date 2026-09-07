"""Thin wrapper around the ofd-cli executable from ofd-utility."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

_PAGE_RE = re.compile(
    r"^(?P<prefix>.+)_doc(?P<doc>\d+)_page(?P<page>\d+)\.(?P<ext>png|jpg|jpeg|bmp|tiff|gif|webp)$",
    re.IGNORECASE,
)


class OfdCliError(RuntimeError):
    """Raised when ofd-cli cannot be found or exits with an error."""


def ofd_cli_names() -> tuple[str, ...]:
    """Preferred executable names for the current platform."""
    if sys.platform == "win32":
        return ("ofd-cli.exe", "ofd-cli")
    return ("ofd-cli", "ofd-cli.exe")


def package_bin_dir() -> Path:
    """Directory that ships with the installed / frozen package."""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / "ofd2pdf" / "bin"
    return Path(__file__).resolve().parent / "bin"


def find_ofd_cli(explicit: str | Path | None = None) -> Path:
    """Locate ``ofd-cli`` / ``ofd-cli.exe``.

    Search order:
    1. ``explicit`` argument
    2. ``OFD_CLI`` environment variable
    3. Bundled package ``ofd2pdf/bin`` (wheel / PyInstaller)
    4. Project ``vendor/bin`` / ``bin`` (local development)
    5. ``PATH``
    """
    candidates: list[Path] = []
    names = ofd_cli_names()

    if explicit:
        candidates.append(Path(explicit))

    env = os.environ.get("OFD_CLI")
    if env:
        candidates.append(Path(env))

    pkg_bin = package_bin_dir()
    for name in names:
        candidates.append(pkg_bin / name)

    here = Path(__file__).resolve()
    search_roots = [here.parents[2] if len(here.parents) > 2 else here.parent]
    search_roots.extend([Path.cwd(), *Path.cwd().parents[:3]])
    for root in search_roots:
        for name in names:
            candidates.append(root / "vendor" / "bin" / name)
            candidates.append(root / "bin" / name)

    for name in names:
        which = shutil.which(name)
        if which:
            candidates.append(Path(which))

    seen: set[Path] = set()
    for path in candidates:
        try:
            resolved = path.resolve()
        except OSError:
            continue
        if resolved in seen:
            continue
        seen.add(resolved)
        if resolved.is_file():
            return resolved

    raise OfdCliError(
        "找不到 ofd-cli 可执行文件。请安装带二进制的平台 wheel "
        "（pip install ofd2pdf），或运行 scripts/build_ofd_cli 构建后放入 "
        "src/ofd2pdf/bin，或设置环境变量 OFD_CLI。"
        " 参考: https://github.com/ofd-utility/ofd-utility"
    )


def run_ofd_cli(
    args: list[str],
    *,
    cli_path: str | Path | None = None,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    """Run ofd-cli with the given arguments."""
    exe = find_ofd_cli(cli_path)
    cmd = [str(exe), *args]
    kwargs: dict = {
        "check": False,
        "capture_output": True,
        "text": True,
        "encoding": "utf-8",
        "errors": "replace",
    }
    # Avoid flashing a console window when invoked from GUI apps on Windows.
    if sys.platform == "win32":
        kwargs["creationflags"] = getattr(subprocess, "CREATE_NO_WINDOW", 0)

    try:
        completed = subprocess.run(cmd, **kwargs)
    except OSError as exc:
        raise OfdCliError(f"无法启动 ofd-cli: {exc}") from exc

    if check and completed.returncode != 0:
        detail = (completed.stderr or completed.stdout or "").strip()
        raise OfdCliError(
            f"ofd-cli 执行失败 (exit={completed.returncode}): {' '.join(cmd)}"
            + (f"\n{detail}" if detail else "")
        )
    return completed


def render_ofd(
    ofd_path: Path,
    out_dir: Path,
    *,
    dpi: float = 150.0,
    image_format: str = "png",
    prefix: str = "page",
    cli_path: str | Path | None = None,
) -> list[Path]:
    """Render OFD pages to images via ``ofd-cli render`` and return sorted paths."""
    ofd_path = Path(ofd_path).resolve()
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if not ofd_path.is_file():
        raise FileNotFoundError(f"OFD 文件不存在: {ofd_path}")

    fmt = image_format.lower().lstrip(".")
    run_ofd_cli(
        [
            "render",
            str(ofd_path),
            str(out_dir),
            "--dpi",
            str(dpi),
            "--format",
            fmt,
            "--prefix",
            prefix,
        ],
        cli_path=cli_path,
    )
    return list_rendered_pages(out_dir, prefix=prefix, image_format=fmt)


def _ext_aliases(image_format: str) -> set[str]:
    fmt = image_format.lower().lstrip(".")
    if fmt in {"jpg", "jpeg"}:
        return {"jpg", "jpeg"}
    return {fmt}


def list_rendered_pages(
    out_dir: Path,
    *,
    prefix: str = "page",
    image_format: str | None = None,
) -> list[Path]:
    """Collect rendered page images sorted by document then page index."""
    out_dir = Path(out_dir)
    pages: list[tuple[int, int, Path]] = []
    allowed_ext = _ext_aliases(image_format) if image_format else None

    for path in out_dir.iterdir():
        if not path.is_file():
            continue
        match = _PAGE_RE.match(path.name)
        if not match:
            continue
        if match.group("prefix") != prefix:
            continue
        if allowed_ext is not None and match.group("ext").lower() not in allowed_ext:
            continue
        pages.append((int(match.group("doc")), int(match.group("page")), path))

    pages.sort(key=lambda item: (item[0], item[1]))
    if not pages:
        raise OfdCliError(f"未在目录中找到渲染结果: {out_dir}")
    return [path for _, _, path in pages]


def ofd_info(ofd_path: Path, *, cli_path: str | Path | None = None) -> str:
    """Return text output of ``ofd-cli info``."""
    completed = run_ofd_cli(["info", str(Path(ofd_path).resolve())], cli_path=cli_path)
    return (completed.stdout or completed.stderr or "").strip()

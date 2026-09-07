"""ofd2pdf — convert OFD (GB/T 33190) files to PDF via ofd-cli."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .converter import convert_ofd_to_pdf, images_to_pdf
from .ofd_cli import OfdCliError, find_ofd_cli, ofd_info, render_ofd

__version__ = "0.2.0"

__all__ = [
    "OfdCliError",
    "__version__",
    "convert_ofd_to_pdf",
    "find_ofd_cli",
    "images_to_pdf",
    "main",
    "ofd_info",
    "render_ofd",
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ofd2pdf",
        description="调用 ofd-cli 将 OFD 渲染为图片后合成为 PDF。",
    )
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    parser.add_argument("ofd", type=Path, nargs="?", help="输入的 .ofd 文件路径")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="输出 PDF 路径（默认与输入同名，扩展名为 .pdf）",
    )
    parser.add_argument(
        "--dpi",
        type=float,
        default=150.0,
        help="渲染分辨率，默认 150",
    )
    parser.add_argument(
        "--format",
        choices=["png", "jpg", "jpeg", "bmp", "tiff", "webp"],
        default="png",
        help="中间页图片格式，默认 png",
    )
    parser.add_argument(
        "--ofd-cli",
        type=Path,
        default=None,
        help="ofd-cli / ofd-cli.exe 路径（也可用环境变量 OFD_CLI）",
    )
    parser.add_argument(
        "--keep-images",
        action="store_true",
        help="保留中间页图片",
    )
    parser.add_argument(
        "--images-dir",
        type=Path,
        default=None,
        help="中间页图片输出目录（默认使用临时目录）",
    )
    parser.add_argument(
        "--info",
        action="store_true",
        help="仅打印 ofd-cli info，不转换",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.ofd is None:
        parser.error("请提供 OFD 文件路径（或使用 -V 查看版本）")

    try:
        find_ofd_cli(args.ofd_cli)

        if args.info:
            print(ofd_info(args.ofd, cli_path=args.ofd_cli))
            return

        pdf = convert_ofd_to_pdf(
            args.ofd,
            args.output,
            dpi=args.dpi,
            image_format=args.format,
            keep_images=args.keep_images,
            images_dir=args.images_dir,
            cli_path=args.ofd_cli,
        )
        print(f"已生成: {pdf}")
    except (OfdCliError, FileNotFoundError, OSError) as exc:
        print(f"错误: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()

"""Convert OFD documents to PDF by rendering pages then assembling images."""

from __future__ import annotations

import tempfile
from pathlib import Path

from PIL import Image

from .ofd_cli import OfdCliError, render_ofd


def images_to_pdf(
    image_paths: list[Path],
    pdf_path: Path,
    *,
    dpi: float = 150.0,
) -> Path:
    """Assemble ordered page images into a multi-page PDF."""
    if not image_paths:
        raise OfdCliError("没有可写入 PDF 的页面图片")

    pdf_path = Path(pdf_path)
    pdf_path.parent.mkdir(parents=True, exist_ok=True)

    opened: list[Image.Image] = []
    try:
        for path in image_paths:
            img = Image.open(path)
            # PDF backend expects RGB / grayscale modes.
            if img.mode in ("RGBA", "LA", "P"):
                img = img.convert("RGB")
            elif img.mode not in ("RGB", "L", "1"):
                img = img.convert("RGB")
            opened.append(img)

        first, *rest = opened
        first.save(
            pdf_path,
            "PDF",
            resolution=float(dpi),
            save_all=bool(rest),
            append_images=rest,
        )
    finally:
        for img in opened:
            img.close()

    return pdf_path.resolve()


def convert_ofd_to_pdf(
    ofd_path: str | Path,
    pdf_path: str | Path | None = None,
    *,
    dpi: float = 150.0,
    image_format: str = "png",
    keep_images: bool = False,
    images_dir: str | Path | None = None,
    cli_path: str | Path | None = None,
) -> Path:
    """Convert an OFD file to PDF.

    Pipeline:
    1. Call ``ofd-cli render`` to rasterize each page.
    2. Merge page images into a single PDF with Pillow.
    """
    ofd_path = Path(ofd_path).resolve()
    if not ofd_path.is_file():
        raise FileNotFoundError(f"OFD 文件不存在: {ofd_path}")

    if pdf_path is None:
        pdf_path = ofd_path.with_suffix(".pdf")
    else:
        pdf_path = Path(pdf_path)

    if images_dir is not None:
        out_dir = Path(images_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        pages = render_ofd(
            ofd_path,
            out_dir,
            dpi=dpi,
            image_format=image_format,
            cli_path=cli_path,
        )
        result = images_to_pdf(pages, pdf_path, dpi=dpi)
        if not keep_images:
            for page in pages:
                page.unlink(missing_ok=True)
        return result

    with tempfile.TemporaryDirectory(prefix="ofd2pdf-") as tmp:
        out_dir = Path(tmp)
        pages = render_ofd(
            ofd_path,
            out_dir,
            dpi=dpi,
            image_format=image_format,
            cli_path=cli_path,
        )
        # Copy pages out of temp if keep_images requested without images_dir.
        if keep_images:
            persist = pdf_path.parent / f"{pdf_path.stem}_pages"
            persist.mkdir(parents=True, exist_ok=True)
            persisted: list[Path] = []
            for page in pages:
                dest = persist / page.name
                dest.write_bytes(page.read_bytes())
                persisted.append(dest)
            return images_to_pdf(persisted, pdf_path, dpi=dpi)
        return images_to_pdf(pages, pdf_path, dpi=dpi)

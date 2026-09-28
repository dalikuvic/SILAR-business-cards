#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

import pymupdf
from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject, NumberObject, RectangleObject

MM_TO_PT = 72 / 25.4
PAGE_W_MM = 91
PAGE_H_MM = 61
BLEED_MM = 3

PAGE_W_PT = PAGE_W_MM * MM_TO_PT
PAGE_H_PT = PAGE_H_MM * MM_TO_PT
TRIM_LEFT_PT = BLEED_MM * MM_TO_PT
TRIM_BOTTOM_PT = BLEED_MM * MM_TO_PT
TRIM_RIGHT_PT = (PAGE_W_MM - BLEED_MM) * MM_TO_PT
TRIM_TOP_PT = (PAGE_H_MM - BLEED_MM) * MM_TO_PT

CARDS = [
    ("SILAR_Mohamed_Ali_recto.svg", "SILAR_Mohamed_Ali_recto.pdf"),
    ("SILAR_Abdellatif_recto.svg", "SILAR_Abdellatif_recto.pdf"),
]

BOX_TOLERANCE_PT = 0.01


def run_inkscape(svg_path: Path, pdf_path: Path) -> None:
    subprocess.run(
        [
            "inkscape",
            str(svg_path),
            "--export-type=pdf",
            f"--export-filename={pdf_path}",
            "--export-area-page",
            "--export-text-to-path",
        ],
        check=True,
        capture_output=True,
        text=True,
    )


def set_pdf_boxes(pdf_path: Path) -> None:
    reader = PdfReader(str(pdf_path))
    if len(reader.pages) != 1:
        raise ValueError(f"{pdf_path.name}: expected 1 page, got {len(reader.pages)}")

    page = reader.pages[0]

    media = RectangleObject([0, 0, PAGE_W_PT, PAGE_H_PT])
    trim = RectangleObject([TRIM_LEFT_PT, TRIM_BOTTOM_PT, TRIM_RIGHT_PT, TRIM_TOP_PT])
    bleed = RectangleObject([0, 0, PAGE_W_PT, PAGE_H_PT])

    page.mediabox = media
    page.trimbox = trim
    page.bleedbox = bleed
    page.cropbox = media
    page.artbox = trim

    page_obj = page.get_object()
    page_obj[NameObject("/Rotate")] = NumberObject(0)

    writer = PdfWriter()
    writer.add_page(page)
    with pdf_path.open("wb") as f:
        writer.write(f)


def verify_pdf(pdf_path: Path) -> dict:
    reader = PdfReader(str(pdf_path))
    if len(reader.pages) != 1:
        raise ValueError(f"{pdf_path.name}: expected 1 page, got {len(reader.pages)}")
    page = reader.pages[0]

    boxes = {
        "MediaBox": [float(v) for v in page.mediabox],
        "TrimBox": [float(v) for v in page.trimbox],
        "BleedBox": [float(v) for v in page.bleedbox],
    }
    expected_boxes = {
        "MediaBox": [0.0, 0.0, PAGE_W_PT, PAGE_H_PT],
        "TrimBox": [TRIM_LEFT_PT, TRIM_BOTTOM_PT, TRIM_RIGHT_PT, TRIM_TOP_PT],
        "BleedBox": [0.0, 0.0, PAGE_W_PT, PAGE_H_PT],
    }

    for box_name, current in boxes.items():
        expected = expected_boxes[box_name]
        for i, (cur_value, exp_value) in enumerate(zip(current, expected)):
            if abs(cur_value - exp_value) > BOX_TOLERANCE_PT:
                raise ValueError(
                    f"{pdf_path.name}: {box_name}[{i}]={cur_value}pt "
                    f"does not match expected {exp_value}pt"
                )

    doc = pymupdf.open(str(pdf_path))
    pix = doc[0].get_pixmap(alpha=True, dpi=144)
    alpha = pix.samples[3::4]
    min_alpha = int(min(alpha)) if alpha else 255
    max_alpha = int(max(alpha)) if alpha else 255

    transparent_pixels = sum(1 for a in alpha if a == 0)
    total_pixels = len(alpha)
    if transparent_pixels == 0:
        raise ValueError(f"{pdf_path.name}: expected transparency, but page is fully opaque")

    doc.close()

    return {
        "file": pdf_path.name,
        "page_count": len(reader.pages),
        "boxes_pt": boxes,
        "expected_page_pt": [round(PAGE_W_PT, 3), round(PAGE_H_PT, 3)],
        "alpha_min": min_alpha,
        "alpha_max": max_alpha,
        "transparent_pixel_ratio": (transparent_pixels / total_pixels) if total_pixels else 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate print PDFs from SVGs.")
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="Skip generation and only verify existing PDFs.",
    )
    args = parser.parse_args()

    root = Path(__file__).resolve().parent.parent

    if not args.verify_only:
        for svg_name, pdf_name in CARDS:
            svg_path = root / svg_name
            pdf_path = root / pdf_name
            if not svg_path.exists():
                raise FileNotFoundError(svg_path)
            run_inkscape(svg_path, pdf_path)
            set_pdf_boxes(pdf_path)

    results = []
    for _, pdf_name in CARDS:
        pdf_path = root / pdf_name
        if not pdf_path.exists():
            raise FileNotFoundError(pdf_path)
        results.append(verify_pdf(pdf_path))

    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()

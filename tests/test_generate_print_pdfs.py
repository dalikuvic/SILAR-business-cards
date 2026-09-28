import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import pymupdf
from pypdf import PdfReader, PdfWriter
from pypdf.generic import RectangleObject


SCRIPT_PATH = Path(__file__).resolve().parent.parent / "scripts" / "generate_print_pdfs.py"
SPEC = importlib.util.spec_from_file_location("generate_print_pdfs", SCRIPT_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class GeneratePrintPDFsTests(unittest.TestCase):
    def test_main_verify_only_mode_calls_verify(self):
        with mock.patch.object(MODULE, "verify_pdf", return_value={"ok": True}) as verify_mock, \
             mock.patch.object(MODULE, "run_inkscape") as inkscape_mock, \
             mock.patch.object(MODULE, "set_pdf_boxes") as boxes_mock, \
             mock.patch("sys.argv", ["generate_print_pdfs.py", "--verify-only"]):
            MODULE.main()

        self.assertEqual(verify_mock.call_count, len(MODULE.CARDS))
        inkscape_mock.assert_not_called()
        boxes_mock.assert_not_called()

    def test_main_generate_mode_calls_generate_and_verify(self):
        with mock.patch.object(MODULE, "verify_pdf", return_value={"ok": True}) as verify_mock, \
             mock.patch.object(MODULE, "run_inkscape") as inkscape_mock, \
             mock.patch.object(MODULE, "set_pdf_boxes") as boxes_mock, \
             mock.patch("sys.argv", ["generate_print_pdfs.py"]):
            MODULE.main()

        self.assertEqual(inkscape_mock.call_count, len(MODULE.CARDS))
        self.assertEqual(boxes_mock.call_count, len(MODULE.CARDS))
        self.assertEqual(verify_mock.call_count, len(MODULE.CARDS))

    def test_verify_pdf_fails_when_boxes_are_wrong(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_pdf = Path(tmp) / "broken.pdf"

            doc = pymupdf.open()
            page = doc.new_page(width=MODULE.PAGE_W_PT, height=MODULE.PAGE_H_PT)
            page.draw_rect(
                pymupdf.Rect(20, 20, 80, 80),
                color=(0, 0.5, 0),
                fill=(0, 0.5, 0),
            )
            doc.save(str(tmp_pdf))
            doc.close()

            reader = PdfReader(str(tmp_pdf))
            pdf_page = reader.pages[0]
            pdf_page.mediabox = RectangleObject([0, 0, 200, 120])
            pdf_page.trimbox = RectangleObject([10, 10, 190, 110])
            pdf_page.bleedbox = RectangleObject([0, 0, 200, 120])

            writer = PdfWriter()
            writer.add_page(pdf_page)
            with tmp_pdf.open("wb") as f:
                writer.write(f)

            with self.assertRaises(ValueError):
                MODULE.verify_pdf(tmp_pdf)

    def test_verify_pdf_fails_when_page_is_fully_opaque(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_pdf = Path(tmp) / "opaque.pdf"

            doc = pymupdf.open()
            page = doc.new_page(width=MODULE.PAGE_W_PT, height=MODULE.PAGE_H_PT)
            page.draw_rect(
                pymupdf.Rect(0, 0, MODULE.PAGE_W_PT, MODULE.PAGE_H_PT),
                color=(1, 1, 1),
                fill=(1, 1, 1),
            )
            doc.save(str(tmp_pdf))
            doc.close()

            reader = PdfReader(str(tmp_pdf))
            pdf_page = reader.pages[0]
            pdf_page.trimbox = RectangleObject(
                [MODULE.TRIM_LEFT_PT, MODULE.TRIM_BOTTOM_PT, MODULE.TRIM_RIGHT_PT, MODULE.TRIM_TOP_PT]
            )
            pdf_page.bleedbox = RectangleObject([0, 0, MODULE.PAGE_W_PT, MODULE.PAGE_H_PT])
            writer = PdfWriter()
            writer.add_page(pdf_page)
            with tmp_pdf.open("wb") as f:
                writer.write(f)

            with self.assertRaises(ValueError):
                MODULE.verify_pdf(tmp_pdf)


if __name__ == "__main__":
    unittest.main()

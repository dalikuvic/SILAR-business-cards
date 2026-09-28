import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest import mock

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
        source_pdf = Path(__file__).resolve().parent.parent / "SILAR_Mohamed_Ali_recto.pdf"
        with tempfile.TemporaryDirectory() as tmp:
            tmp_pdf = Path(tmp) / "broken.pdf"
            reader = PdfReader(str(source_pdf))
            page = reader.pages[0]
            page.mediabox = RectangleObject([0, 0, 200, 120])

            writer = PdfWriter()
            writer.add_page(page)
            with tmp_pdf.open("wb") as f:
                writer.write(f)

            with self.assertRaises(ValueError):
                MODULE.verify_pdf(tmp_pdf)


if __name__ == "__main__":
    unittest.main()

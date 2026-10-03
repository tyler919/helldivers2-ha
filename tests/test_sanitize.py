"""Run: python3 -m unittest discover -s tests"""
import importlib.util
import pathlib
import unittest

_PATH = pathlib.Path(__file__).parent.parent / "custom_components" / "helldivers2" / "sanitize.py"
_spec = importlib.util.spec_from_file_location("sanitize", _PATH)
sanitize = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sanitize)
strip_markup = sanitize.strip_markup


class StripMarkupTest(unittest.TestCase):
    def test_game_markup_is_removed_cleanly(self):
        msg = "<i=3>NEW MAJOR ORDER</i>\n\nDefend <i=1>GATRIA</i> and <i=1>WASAT</i>."
        self.assertEqual(strip_markup(msg), "NEW MAJOR ORDER\n\nDefend GATRIA and WASAT.")

    def test_unclosed_tag_payload_loses_angle_brackets(self):
        out = strip_markup("News <img src=x onerror=alert(document.cookie)")
        self.assertNotIn("<", out)
        self.assertNotIn(">", out)

    def test_no_angle_brackets_survive_any_shape(self):
        for payload in [
            "<script>alert(1)</script>",
            "<<img src=x onerror=alert(1)>>",
            "<i=1>ok</i><svg/onload=alert(1)",
            "a > b < c",
            "<scr<script>ipt>alert(1)</script>",
        ]:
            out = strip_markup(payload)
            self.assertNotIn("<", out, payload)
            self.assertNotIn(">", out, payload)

    def test_empty(self):
        self.assertEqual(strip_markup(None), "")
        self.assertEqual(strip_markup(""), "")


if __name__ == "__main__":
    unittest.main()

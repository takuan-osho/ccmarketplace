import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from server import Translator

CUT_OFF_CHARS = 40


class FakeTranslator(Translator):
    """Answers every request with a fixed reply, cut off at the token limit when the input is long."""

    def _post(self, path, body, timeout=600):
        text = body["messages"][0]["content"]
        cut = len(text) > CUT_OFF_CHARS
        return {"choices": [{"finish_reason": "length" if cut else "stop", "message": {"content": "訳" + text[:5]}}]}


class TruncationTest(unittest.TestCase):
    def setUp(self):
        self.tr = FakeTranslator("http://127.0.0.1:1", "token")

    def test_cut_off_line_keeps_the_original(self):
        long_line = "This is a long single-line paragraph that the model cuts off."
        out, warnings, stats = self.tr.translate(long_line)
        self.assertEqual(out, long_line)
        self.assertTrue(any("cut off" in w for w in warnings))
        self.assertGreaterEqual(stats["truncated"], 1)

    def test_short_lines_are_translated(self):
        out, _, _ = self.tr.translate("Short line.\nAnother one.")
        self.assertEqual(out, "訳Short")  # whole mode: one request; the fake keeps the first 5 characters

    def test_only_the_cut_off_line_is_kept(self):
        text = "Short line.\n" + "x" * 30 + " a long line that the model cuts off here."
        out, _, _ = self.tr.translate(text, mode="line")
        first, second = out.split("\n")
        self.assertEqual(first, "訳Short")
        self.assertEqual(second, text.split("\n")[1])


if __name__ == "__main__":
    unittest.main()

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


class EchoTranslator(Translator):
    """Answers every request with "T:" and the input."""

    def _post(self, path, body, timeout=600):
        return {"choices": [{"finish_reason": "stop", "message": {"content": "T:" + body["messages"][0]["content"]}}]}


class LineModeTest(unittest.TestCase):
    def setUp(self):
        self.tr = EchoTranslator("http://127.0.0.1:1", "token")

    def test_indentation_is_kept(self):
        text = "- Item\n\n    ```sh\n    ls\n    ```\n\n    Indented prose."
        out, _, _ = self.tr.translate(text, mode="line")
        self.assertIn("\n    ```sh\n    ls\n    ```\n", out)
        self.assertIn("\n    T:Indented prose.", out)

    def test_non_latin_prose_is_translated(self):
        for text in ("日本語の文です。", "Это русский текст."):
            with self.subTest(text=text):
                out, _, _ = self.tr.translate(text, src="ja", tgt="en", mode="line")
                self.assertEqual(out, "T:" + text)


class EmptyTranslator(Translator):
    """Answers every request with an empty translation."""

    def _post(self, path, body, timeout=600):
        return {"choices": [{"finish_reason": "stop", "message": {"content": "<|plamo:tag|>"}}]}


class EmptyTranslationTest(unittest.TestCase):
    def test_empty_translation_keeps_the_original(self):
        text = "Important explanation.\nDo not delete your data."
        out, warnings, _ = EmptyTranslator("http://127.0.0.1:1", "token").translate(text)
        self.assertEqual(out, text)
        self.assertTrue(any("empty translation" in w for w in warnings))


if __name__ == "__main__":
    unittest.main()

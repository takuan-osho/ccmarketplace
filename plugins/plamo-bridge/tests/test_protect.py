"""Tests for protect.py. Run from the plugin root: python3 -m unittest discover -s tests (pytest also works)."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from protect import protect, restore

CASES = [
    "Run `npm test` in /Users/x/proj/src/a.py now.",
    "See https://example.com/a?b=1&c=2, then edit src/x.ts:12 and ./lib/y.py.",
    "```python\nprint('hi')  # /tmp/a.txt\n```\nAfter the block.",
    "````md\n```js\nx\n```\n````\ntail",
    "Unclosed fence:\n```sh\nls -la",
    "Use ``a `tick` b`` carefully; file config.toml and ~/.cache/x/y.md.",
    "plain prose only, no code.",
    "Edit foo/bar.ts:10:5 (see https://a.b/c).",
]


class ProtectTest(unittest.TestCase):
    def test_roundtrip(self):
        for t in CASES:
            with self.subTest(t=t):
                m, r = protect(t)
                self.assertEqual(restore(m, r), t)

    def test_masks_code_and_paths(self):
        m, r = protect("Edit `foo()` in /a/b.py:3 via https://x.io/p.")
        for s in ("foo()", "/a/b.py:3", "https://x.io/p"):
            self.assertNotIn(s, m)
        self.assertIn("Edit", m)
        self.assertIn("via", m)
        self.assertTrue(any("https://x.io/p" in v for v in r.values()))

    def test_fence_is_single_placeholder(self):
        m, r = protect("a\n```py\nx=1\n\ny=2\n```\nb")
        self.assertEqual(m.count("[[X"), 1)
        self.assertNotIn("x=1", m)
        self.assertTrue(next(iter(r.values())).startswith("```py"))

    def test_prose_not_masked(self):
        _m, r = protect("The build and/or the tests failed. I/O is slow.")
        self.assertEqual(r, {})

    def test_placeholder_shaped_text_is_kept(self):
        for t in ("Use `[[X0]]` as the placeholder.", "Literal [[X0]] in prose, and `code`.", "```\n[[X1]]\n```"):
            with self.subTest(t=t):
                m, r = protect(t)
                self.assertEqual(restore(m, r), t)

    def test_indented_fences_are_one_placeholder(self):
        for t in ('  ~~~sh\n  echo "Do not translate this literal"\n  ~~~', "- Item\n\n    ```sh\n    ls\n    ```\n"):
            with self.subTest(t=t):
                m, r = protect(t)
                self.assertEqual(len(r), 1)
                self.assertNotIn("echo", m)
                self.assertEqual(restore(m, r), t)

    def test_no_nested_placeholders(self):
        t = "The ` character:\n\n```sh\necho hello\n```\n\nUse ` carefully."
        m, r = protect(t)
        self.assertFalse(any("[[" in v for v in r.values()))
        self.assertEqual(restore(m, r), t)

    def test_blockquoted_fence_is_protected(self):
        t = '> ~~~sh\n> echo "Do not translate this literal"\n> ~~~\n\nAfter.'
        m, r = protect(t)
        self.assertNotIn("echo", m)
        self.assertIn("After.", m)
        self.assertEqual(restore(m, r), t)

    def test_url_trailing_punct_kept_outside(self):
        m, r = protect("Visit https://a.io/x.")
        self.assertEqual(restore(m, r), "Visit https://a.io/x.")
        self.assertTrue(m.endswith("."))


if __name__ == "__main__":
    unittest.main()

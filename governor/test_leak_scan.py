"""Layer-0 tests for leak_scan's username detector. Deterministic, stdlib-only.

The username pattern is built from THIS machine's identity, so a test that
used the real one would pass or fail depending on who ran it. Every case here
builds the pattern from a fixed name and runs it through the same `git grep`
path the scanner uses — the plant-a-known-bad rule (L0002): a detector is
trusted only after it has been watched firing."""

import os
import shutil
import subprocess
import tempfile
import unittest

import leak_scan

NAME = "ann"


def _repo(files):
    d = tempfile.mkdtemp()
    subprocess.run(["git", "-C", d, "init", "-q"], check=True)
    for name, content in files.items():
        with open(os.path.join(d, name), "w", encoding="utf-8") as fh:
            fh.write(content)
    subprocess.run(["git", "-C", d, "add", "-A"], check=True)
    return d


class TestUsernamePattern(unittest.TestCase):
    def setUp(self):
        self.pat = leak_scan.username_pattern(NAME)
        self.d = _repo({
            "words.md": "planning the annex; a banner\n",
            "leak.md": "ssh " + NAME + "@host and /home/" + NAME + "\n",
            "edge.md": NAME + " at line start\nand at line end " + NAME + "\n",
        })

    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)

    def _hits(self):
        return leak_scan._git_grep(self.d, self.pat, [])

    def test_substring_of_a_word_is_not_a_hit(self):
        """The 20-HIGH false-positive class: username inside an ordinary word."""
        self.assertFalse([h for h in self._hits() if h.startswith("words.md")])

    def test_bare_username_fires(self):
        """Planted known-bad. If this stops firing, the detector is dead."""
        self.assertTrue([h for h in self._hits() if h.startswith("leak.md")])

    def test_line_boundaries_count_as_boundaries(self):
        hits = [h for h in self._hits() if h.startswith("edge.md")]
        self.assertEqual(len(hits), 2)

    def test_pattern_is_posix_ere(self):
        r"""git grep -E has no \b/\s/\d (L0002); the pattern must not lean on them.

        RAW strings, deliberately: as plain strings "\b" was a BACKSPACE byte,
        so this assertion checked for the wrong character and could never fail
        on a real \b — a dead guard against dead patterns (found 2026-10-05
        from CI's SyntaxWarnings)."""
        for dead in (r"\b", r"\s", r"\d", r"\w"):
            self.assertNotIn(dead, self.pat)
        for pat, _ in leak_scan.HIGH_PATTERNS:
            for dead in (r"\s", r"\d", r"\w"):
                self.assertNotIn(dead, pat, f"dead ERE escape in HIGH pattern {pat!r}")


class TestDashEncodedPath(unittest.TestCase):
    """kit 2.7.0 (horde brief hypersaw-004): the scan sees the dash-encoded home
    path by SHAPE, not only through the literal username of this machine.
    Plants assembled so this file never trips a leak gate itself."""
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        subprocess.run(["git", "init", "-q", self.tmp], check=True)
        real = "/tmp/c/" + "-" + "Users" + "-somebody-Documents-x/a"
        with open(os.path.join(self.tmp, "t.md"), "w") as fh:
            fh.write(f"one {real}\ntwo -" + "Users" + "-<user>-Documents\nthree a multi-home-office plan\n")
        subprocess.run(["git", "-C", self.tmp, "add", "-A"], check=True)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_shape_fires_placeholder_and_prose_do_not(self):
        hits = [f for f in leak_scan.scan_repo(self.tmp) if f[1] == "dash-encoded home path"]
        self.assertEqual([h[2].split(":")[1] for h in hits], ["1"])


if __name__ == "__main__":
    unittest.main()

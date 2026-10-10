"""Layer-0 tests for currency.py — the deterministic half of /retrofit.

The property that matters most is the LAST test: a repo at the kit version
with every requirement present yields an empty delta. That is the K1 gate
("re-running the retrofit is a no-op"), and it is what makes the migration
safe to run repeatedly on 46 repos.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

import currency

_KIT = os.path.dirname(os.path.abspath(__file__))


def _touch(root, rel, body="x", exe=False):
    p = os.path.join(root, rel)
    os.makedirs(os.path.dirname(p) or root, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(body)
    if exe:
        os.chmod(p, 0o755)
    return p


def _full_baseline(root):
    """Everything REQUIREMENTS['2.0.0'] asks for."""
    for f in ("CLAUDE.md", "ROADMAP.md", "DECISIONS.md", "INDEX.md", "LIBRARY.md"):
        _touch(root, f)
    # Declare whatever the kit's CURRENT version is, never a hardcoded one:
    # pinning "2.0.0" here made every one of these tests fail the moment 2.1.0
    # shipped, which is the test asserting the kit never moves rather than
    # asserting the property under test.
    _touch(root, "project.manifest.json",
           json.dumps({"kit_version": currency.kit_version(_KIT)}))
    os.makedirs(os.path.join(root, "traces"), exist_ok=True)
    # A REAL gate, not a stub: 2.2.0 asserts the gate FIRES on planted
    # identity paths, so a `leak_gate() { :; }` placeholder now correctly
    # reads as behind. The fixture's verify is autonomous's own leak_gate,
    # lifted verbatim, so the fixture is current for the same reason a real
    # repo is.
    real = os.path.join(_KIT, "..", "harness", "verify")
    with open(real, encoding="utf-8") as fh:
        _touch(root, "verify", fh.read(), exe=True)
    # 2.4.0: kit gates are VENDORED, so a current fixture carries .kit/ and its
    # MANIFEST. Installed from the kit rather than hand-built, for the same
    # reason real repos do it that way — a hand-built copy is the thing 2.4.0
    # exists to stop.
    sys.path.insert(0, _KIT)
    import kit_sync
    kit_sync.install(root)
    subprocess.run(["git", "init", "-q", root], check=True)   # leak_gate uses git grep
    _touch(root, ".github/workflows/ci.yml", "name: ci")
    # 2.9.0: a full baseline carries the Stop shim, so its requirement is MET
    # here and the n/a list in the tests below stays about what each test means.
    _touch(root, ".claude/hooks/stop-gate.sh", 'exec bash "$CLAUDE_PROJECT_DIR/.kit/stop-gate.sh"\n')
    _touch(root, ".claude/settings.json", json.dumps({"hooks": {"Stop": [{"hooks": [
        {"type": "command", "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/stop-gate.sh"}]}]}}))
    _touch(root, ".gitattributes", "* text=auto eol=lf")
    # 2.5.0 asks whether .gitattributes is TRACKED, not merely on disk — an
    # untracked one reaches no clone and no CI. The fixture must therefore
    # stage its files to represent a real current repo; before this it did
    # not, and the new check caught the fixture rather than the code, which
    # is the check working.
    subprocess.run(["git", "-C", root, "add", "-A"], check=True,
                   capture_output=True)


class TestVersionOrdering(unittest.TestCase):
    def test_pre_sorts_below_everything(self):
        self.assertLess(currency.parse_version("pre-2.0.0"), currency.parse_version("0.0.1"))
        self.assertLess(currency.parse_version(None), currency.parse_version("2.0.0"))

    def test_semver_compares_numerically_not_lexically(self):
        self.assertGreater(currency.parse_version("2.10.0"), currency.parse_version("2.9.0"))


class TestChangelogParse(unittest.TestCase):
    def test_reads_the_real_changelog(self):
        entries = currency.changelog_entries(_KIT)
        self.assertTrue(entries)
        self.assertEqual(entries[0][0], "2.0.0")

    def test_every_changelog_version_has_a_requirements_row(self):
        """The prose in CHANGELOG.md is the explanation; REQUIREMENTS is the
        gate. A version present in one and absent from the other means the
        retrofit will silently skip that migration."""
        for ver, *_ in currency.changelog_entries(_KIT):
            self.assertIn(ver, currency.REQUIREMENTS,
                          f"CHANGELOG {ver} has no REQUIREMENTS row")


class TestReport(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_empty_repo_is_behind_by_everything(self):
        r = currency.report(self.tmp, _KIT)
        self.assertEqual(r["declared"], "pre-2.0.0")
        self.assertFalse(r["current"])
        # every non-tool-only CHANGELOG entry, not a fixed count — the point
        # is "behind by everything", which grows as the kit does
        # Computed currency (2.6.0) lists a version only when one of ITS
        # requirements is unmet, so entries with no requirements of their own
        # never appear — "behind by everything" now means every version that
        # actually asks for something.
        # 2.9.0 is the exception by design: its requirement applies to a repo
        # WITH a ./verify, which an empty repo lacks (it is already behind on
        # 2.0.0 for that), so it reads n/a (listed below), not behind twice.
        # Any other version turning n/a here should fail this test.
        expected = [v for v, reqs in currency.REQUIREMENTS.items()
                    if reqs and v not in currency.TOOL_ONLY and v != "2.9.0"]
        self.assertEqual(len(r["behind"]), len(expected))
        self.assertEqual(r.get("not_applicable"), ["closing gate wired to the kit's"])
        # the baseline entry is the one with real requirements
        base = next(b for b in r["behind"] if b["version"] == "2.0.0")
        self.assertEqual(len(base["missing"]), len(currency.REQUIREMENTS["2.0.0"]))

    def test_no_remote_makes_CI_not_applicable_but_visible(self):
        """resume-workshop, 2026-09-28: local-only by ratified decision (client
        PII), it read BEHIND forever on a workflow that could never run.
        n/a is not a silent pass: it is listed, and rendered even when CURRENT."""
        _full_baseline(self.tmp)
        os.remove(os.path.join(self.tmp, ".github", "workflows", "ci.yml"))
        r = currency.report(self.tmp, _KIT)
        self.assertTrue(r["current"])
        self.assertEqual(r["not_applicable"], ["CI workflow"])
        self.assertIn("n/a here: CI workflow", currency.render(r))

    def test_a_remote_without_CI_still_reads_behind(self):
        _full_baseline(self.tmp)
        os.remove(os.path.join(self.tmp, ".github", "workflows", "ci.yml"))
        subprocess.run(["git", "-C", self.tmp, "remote", "add", "origin",
                        "https://example.invalid/x.git"], check=True)
        r = currency.report(self.tmp, _KIT)
        self.assertFalse(r["current"])
        self.assertIn("CI workflow", next(b for b in r["behind"] if b["version"] == "2.0.0")["missing"])

    def test_a_folder_git_cannot_read_keeps_the_CI_requirement(self):
        """Uncertainty is not exemption: absence never reads as compliance."""
        self.assertIs(currency._present(self.tmp, ".github/workflows", "ci-if-remote"), False)

    def test_undeclared_but_complete_repo_is_CURRENT(self):
        """Antiphon's shape: full harness, no kit_version. THIS TEST WAS
        INVERTED on 2026-08-18 and the inversion is the point of 2.6.0.

        It used to assert that such a repo is BEHIND, because currency was
        DECLARED and never inferred. That rule cost 24 repos a second retrofit
        in one day — every one of them satisfying every requirement while
        holding a stale string. Currency is now computed from the tree, so a
        repo that meets the bar IS current, whatever its manifest says or does
        not say. The old rule's real concern — that silence must not read as
        compliance — is preserved by construction: silence proves nothing
        here, the CHECKS do, and an incomplete repo still reads behind."""
        _full_baseline(self.tmp)
        _touch(self.tmp, "project.manifest.json", json.dumps({"survey": {}}))
        r = currency.report(self.tmp, _KIT)
        self.assertTrue(r["current"])
        self.assertEqual(r["behind"], [])
        self.assertEqual(r["declared"], "pre-2.0.0")   # provenance, not a gate

    def test_a_missing_baseline_item_reads_behind_whatever_is_declared(self):
        """Was: 'declared current but missing items is reported as drift'.
        autonomous on 2026-08-17 declared 2.0.0 with no CLAUDE.md, and the old
        model needed a special `declared_but_missing` channel to say so —
        because `current` was computed from the string and could disagree with
        the tree. Computed currency (2.6.0) collapses that: there is no
        declaration to contradict, so a missing requirement is simply an unmet
        requirement and the repo is BEHIND. Drift stops being a category."""
        _full_baseline(self.tmp)
        os.remove(os.path.join(self.tmp, "CLAUDE.md"))
        r = currency.report(self.tmp, _KIT)
        self.assertFalse(r["current"])
        self.assertIn("CLAUDE.md", [m for b in r["behind"] for m in b["missing"]])

    @unittest.skipIf(os.name == "nt", "NTFS has no exec bit: os.access(X_OK) is true for "
                     "every file, so the property under test does not exist here. "
                     "The Mac and ubuntu CI run it.")
    def test_verify_must_be_executable_not_just_present(self):
        """The Write tool does not set the exec bit (retrofit gotcha,
        2026-07-12). A verify that exists but cannot run is not a verify."""
        _full_baseline(self.tmp)
        os.chmod(os.path.join(self.tmp, "verify"), 0o644)
        r = currency.report(self.tmp, _KIT)
        self.assertFalse(r["current"])
        self.assertIn("./verify", [m for b in r["behind"] for m in b["missing"]])

    def test_tool_only_bump_does_not_put_the_fleet_behind(self):
        """2.0.1 changed /retrofit, not what a repo must contain. A repo at
        2.0.0 must read CURRENT, or the checker manufactures 46 rows of
        'behind by nothing you can act on' — noise that gets the tool ignored."""
        _full_baseline(self.tmp)   # declares the current kit version
        r = currency.report(self.tmp, _KIT)
        self.assertTrue(r["current"])
        self.assertEqual(r["behind"], [])

    def test_current_and_complete_is_a_noop(self):
        """THE K1 GATE. Re-running the retrofit on a current repo must find
        nothing to do."""
        _full_baseline(self.tmp)
        r = currency.report(self.tmp, _KIT)
        self.assertTrue(r["current"])
        self.assertEqual(r["behind"], [])
        self.assertEqual(r["declared_but_missing"], [])


if __name__ == "__main__":
    unittest.main()


class TestVendoredGateDashForm(unittest.TestCase):
    """kit 2.7.0 (horde brief hypersaw-004): the vendored leak_gate catches the
    dash-encoded home path Claude Code uses for session folders, and lets the
    placeholder form and ordinary hyphenated prose through. Plants are
    ASSEMBLED: a literal here would trip every leak gate that greps this file."""
    def test_dash_form_fires_placeholder_and_prose_do_not(self):
        tmp = tempfile.mkdtemp()
        try:
            subprocess.run(["git", "init", "-q", tmp], check=True)
            real = "/tmp/c/" + "-" + "Users" + "-alice-Documents-x/a"
            _touch(tmp, "plant.md", f"one {real}\ntwo -" + "Users" + "-<user>-Documents\n"
                   "three a multi-home-office plan\n")
            r = subprocess.run(["bash", "-c", ". " + os.path.join(_KIT, "vendor", "kit-gates.sh")
                                + "; HARNESS_DIR=.harness; leak_gate"],
                               cwd=tmp, capture_output=True, text=True)
            self.assertEqual(r.returncode, 1)
            self.assertIn("plant.md:1:", r.stderr)
            self.assertNotIn("plant.md:2:", r.stderr)
            self.assertNotIn("plant.md:3:", r.stderr)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


class TestClosingGateRequirement(unittest.TestCase):
    """2.9.0 (Decision 92): a repo with a ./verify must carry the kit's closing
    gate, wired. Each state below was a real repo on the day it shipped."""
    SHIM = 'exec bash "$CLAUDE_PROJECT_DIR/.kit/stop-gate.sh"\n'
    WIRED = json.dumps({"hooks": {"Stop": [{"matcher": "", "hooks": [
        {"type": "command", "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/stop-gate.sh"}]}]}})

    def test_states(self):
        with tempfile.TemporaryDirectory() as root:
            self.assertEqual(currency._closing_gate(root), "na")          # no ./verify at all
            _touch(root, "verify", "#!/bin/sh\n", exe=True)
            self.assertIs(currency._closing_gate(root), False)            # verify, no gate (20 repos)
            _touch(root, ".claude/hooks/stop-gate.sh", "[ -f .harness/dirty ] && exit 2\nexit 0\n")
            _touch(root, ".claude/settings.json", self.WIRED)
            self.assertIs(currency._closing_gate(root), False)            # its own copy (32 repos)
            _touch(root, ".claude/hooks/stop-gate.sh", self.SHIM)
            self.assertIs(currency._closing_gate(root), True)
            _touch(root, ".claude/settings.json", '{"hooks": {}}')
            self.assertIs(currency._closing_gate(root), False)            # a shim nothing invokes
            _touch(root, ".claude/settings.json", "{not json")
            self.assertIs(currency._closing_gate(root), False)

    def test_the_template_satisfies_it(self):
        self.assertIs(currency._closing_gate(os.path.join(_KIT, "..", "harness")), True)


class TestVendoredContractCheck(unittest.TestCase):
    """K6 (Decision 86): the contract check rides kit_integrity so every
    ./verify runs it without being edited. Observe mode reports and never
    changes the exit code; deny mode is the plant that proves it can fire."""
    def _run(self, files, mode=None):
        tmp = tempfile.mkdtemp()
        try:
            subprocess.run(["git", "init", "-q", tmp], check=True)
            sys.path.insert(0, _KIT)
            import kit_sync
            kit_sync.install(tmp)
            for name, body in files.items():
                _touch(tmp, name, body)
            env = dict(os.environ)
            env.pop("KIT_CONTRACT_MODE", None)
            if mode:
                env["KIT_CONTRACT_MODE"] = mode
            r = subprocess.run(["bash", "-c", ". .kit/kit-gates.sh; kit_integrity"],
                               cwd=tmp, capture_output=True, text=True, env=env)
            return r.returncode, r.stderr
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    _UNVERSIONED = {"project.manifest.json": '{"composite": {"contract": "C.md"}}',
                    "C.md": "# contract\n"}

    def test_observe_reports_but_passes(self):
        rc, err = self._run(self._UNVERSIONED)
        self.assertEqual(rc, 0)
        self.assertIn("contract (observe: would fail", err)

    def test_deny_fires_on_the_plant(self):
        rc, err = self._run(self._UNVERSIONED, mode="deny")
        self.assertEqual(rc, 1)
        self.assertIn("C.md declares no contract-version", err)

    def test_missing_contract_file_is_named(self):
        rc, err = self._run({"project.manifest.json": '{"composite": {"contract": "gone.md"}}'},
                            mode="deny")
        self.assertEqual(rc, 1)
        self.assertIn("gone.md", err)

    def test_versioned_contract_and_non_composite_are_silent(self):
        for files in ({"project.manifest.json": '{"composite": {"contract": "C.md"}}',
                       "C.md": "contract-version: 1.2.0\n"},
                      {"project.manifest.json": '{"name": "x"}'}, {}):
            rc, err = self._run(files, mode="deny")
            self.assertEqual((rc, "contract" in err), (0, False), files)


class TestProbeLeavesHarnessAlone(unittest.TestCase):
    """juce-rag 2026-08-18: the gate-fires probe runs the target's ./verify,
    whose record() overwrote .harness/last-verify.json with the probe's exit 1
    and deleted .harness/dirty — a red Stop hook for a PASSING check. The
    probe must restore both, byte for byte, including 'absent'."""

    def test_green_record_and_dirty_flag_survive_the_probe(self):
        with tempfile.TemporaryDirectory() as root:
            _full_baseline(root)
            hd = os.path.join(root, ".harness")
            os.makedirs(hd)
            green = b'{"target":"fast","exit":0,"git":"abc","at":"t"}'
            with open(os.path.join(hd, "last-verify.json"), "wb") as fh:
                fh.write(green)
            with open(os.path.join(hd, "dirty"), "wb") as fh:
                fh.write(b"1")
            currency._GATE_CACHE.clear()
            self.assertTrue(currency._gate_report(root)["posix"])   # gate fired (exit 1)
            with open(os.path.join(hd, "last-verify.json"), "rb") as fh:
                self.assertEqual(fh.read(), green)                 # ...and left no trace
            self.assertTrue(os.path.exists(os.path.join(hd, "dirty")))

    def test_absent_record_stays_absent(self):
        with tempfile.TemporaryDirectory() as root:
            _full_baseline(root)
            currency._GATE_CACHE.clear()
            currency._gate_report(root)
            self.assertFalse(os.path.exists(os.path.join(root, ".harness", "last-verify.json")))


class TestForeignPlantIsInvisible(unittest.TestCase):
    """mind-lathe, 2026-08-18: the probe plants INSIDE the target tree, so a
    concurrent `./verify fast` there read the plant and reported a leak in a
    file that vanished seconds later. The gate must be blind to a plant it
    does not own, and must still see the one it does."""

    def setUp(self):
        self.root = tempfile.mkdtemp()
        _full_baseline(self.root)
        self.plant = ".kit-currency-plant-99999.md"
        with open(os.path.join(self.root, self.plant), "w") as fh:
            fh.write("x " + "/" + "Users" + "/nobody/secret\n")   # assembled, never literal

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def _verify(self, own=None):
        env = dict(os.environ)
        env.pop("KIT_LEAK_PLANT", None)
        if own:
            env["KIT_LEAK_PLANT"] = own
        return subprocess.run(currency.verify_cmd(), cwd=self.root, env=env,
                              capture_output=True, text=True)

    def test_unowned_plant_does_not_red_a_concurrent_verify(self):
        # The assertion is that the gate never NAMES the foreign plant. Exit
        # code is not usable here: the baseline fixture's verify is the kit
        # template, which exits 1 with NOT IMPLEMENTED by design. (Checked on
        # a real repo separately: autonomous exits 0 with a foreign plant.)
        r = self._verify()
        self.assertNotIn(self.plant, r.stderr + r.stdout)

    def test_owned_plant_still_fires(self):
        r = self._verify(own=self.plant)
        self.assertIn(self.plant, r.stderr + r.stdout)
        self.assertNotEqual(r.returncode, 0)


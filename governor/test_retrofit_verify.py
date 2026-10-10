"""retrofit_verify must DISPUTE a false notice, not only VERIFY a true one — a
verifier that cannot say no reads exactly like one that always says yes
(L0002/L0005). Fixture: two temp repos registered under a temp registry, one
genuinely current, one declaring a version it does not meet; notices for
both, plus one from a repo the registry has never heard of."""
import json, os, re, shutil, subprocess, sys, tempfile, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, HERE)
import retrofit_verify as rv  # noqa: E402

KIT_VERSION = open(os.path.join(ROOT, "kit", "VERSION")).read().strip()


def _git_repo(path):
    os.makedirs(path)
    subprocess.run(["git", "init", "-q", path], check=True)


def _put(path, text):
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


class RetrofitVerify(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        # A genuinely current repo, built the way test_currency builds one
        # (real leak_gate lifted from harness/verify, so 2.2.0's gate-fires
        # check passes) — NOT autonomous itself, whose ./verify would re-run
        # this test file from inside the check.
        self.truth = os.path.join(self.tmp, "truth")
        _git_repo(self.truth)
        for f in ("CLAUDE.md", "ROADMAP.md", "DECISIONS.md", "INDEX.md", "LIBRARY.md"):
            _put(os.path.join(self.truth, f), "x\n")
        os.makedirs(os.path.join(self.truth, "traces"))
        os.makedirs(os.path.join(self.truth, ".github", "workflows"))
        _put(os.path.join(self.truth, ".github", "workflows", "ci.yml"), "name: ci\n")
        _put(os.path.join(self.truth, ".gitattributes"), "* text=auto eol=lf\n")
        shutil.copy(os.path.join(ROOT, "harness", "verify"), os.path.join(self.truth, "verify"))
        os.chmod(os.path.join(self.truth, "verify"), 0o755)
        # 2.4.0: a current repo carries VENDORED kit gates. Installed with the
        # real tool rather than hand-assembled here — a hand-built copy of kit
        # mechanism is precisely what 2.4.0 exists to stop, and a fixture is not
        # exempt from the rule it is testing.
        sys.path.insert(0, os.path.join(ROOT, "kit"))
        import kit_sync
        kit_sync.install(self.truth)
        with open(os.path.join(self.truth, "project.manifest.json"), "w") as fh:
            json.dump({"kit_version": KIT_VERSION}, fh)
        # 2.9.0: a current repo with a ./verify carries the closing gate, wired.
        # Copied from the harness template for the same reason as above: the
        # template is what a real retrofit installs.
        for rel in (os.path.join(".claude", "hooks", "stop-gate.sh"),
                    os.path.join(".claude", "settings.json")):
            os.makedirs(os.path.dirname(os.path.join(self.truth, rel)), exist_ok=True)
            shutil.copy(os.path.join(ROOT, "harness", rel), os.path.join(self.truth, rel))
        # 2.5.0: a current repo has .gitattributes TRACKED, not just present.
        # This fixture builds a repo by hand, so it has to stage like a real
        # one — the same correction the currency fixture needed.
        subprocess.run(["git", "-C", self.truth, "add", "-A"], check=True,
                       capture_output=True)
        self.liar = os.path.join(self.tmp, "liar")
        _git_repo(self.liar)
        with open(os.path.join(self.liar, "project.manifest.json"), "w") as fh:
            json.dump({"kit_version": KIT_VERSION}, fh)   # declares, has nothing
        self.registry = {"rules": [            # sweep.resolve shape: rules, not projects
            {"project": self.truth},
            {"project": self.liar},
        ]}
        self.mail = os.path.join(self.tmp, "mail", "_rvtest")
        os.makedirs(self.mail)
        self._notice("truth", "truth.md")
        self._notice("liar", "lie.md")
        self._notice("ghost", "ghost.md")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _notice(self, sender, fname):
        with open(os.path.join(self.mail, "retrofit-" + fname), "w") as fh:
            fh.write(f"---\nid: {sender}-retrofit-{KIT_VERSION}\nfrom: {sender}\n"
                     f"to: autonomous\nstatus: filed\nball: provider\nfiled: 2026-08-18\n"
                     f"re: retrofit to kit {KIT_VERSION}\n---\nclaimed done.\n")

    def _run(self, dry):
        res = rv.verify_all(self.registry, dry=dry, mail_root=os.path.join(self.tmp, "mail"))
        return {r["sender"]: r for r in res}

    def test_true_verified_lie_disputed_unknown_unresolvable(self):
        r = self._run(dry=True)
        self.assertEqual(r["truth"]["verdict"], "verified")
        self.assertEqual(r["liar"]["verdict"], "disputed")
        # Under computed currency there is no declaration to contradict, so the
        # note names the UNMET REQUIREMENTS instead of a mismatched string —
        # which is the more useful thing to have said all along.
        self.assertIn("unmet", r["liar"]["note"])
        self.assertEqual(r["ghost"]["verdict"], "unresolvable")

    def test_stamp_flips_frontmatter_keeps_body_and_is_idempotent(self):
        self._run(dry=False)
        with open(os.path.join(self.mail, "retrofit-lie.md")) as fh:
            lie = fh.read()
        self.assertRegex(lie, r"(?m)^status: disputed$")
        self.assertRegex(lie, r"(?m)^ball: none$")
        self.assertIn("claimed done.", lie)               # filer's words intact
        self.assertIn("autonomous verification", lie)
        self.assertEqual(self._run(dry=False), {})        # already judged → skipped

    def test_kit_sync_receipt_verified_on_a_synced_repo(self):
        """A sync receipt claims only that the VENDORED MECHANISM is current —
        narrower than a retrofit notice. `truth` is vendored but BEHIND on
        substance, so judging a sync receipt by full currency would wrongly
        dispute it. That distinction is the test."""
        with open(os.path.join(self.mail, "kit-sync-current.md"), "w") as fh:
            fh.write(f"---\nid: truth-kit-sync-{KIT_VERSION}\nfrom: truth\nto: autonomous\n"
                     f"status: filed\nball: provider\nre: kit_sync\n---\nclaimed.\n")
        with open(os.path.join(self.mail, "kit-sync-lie.md"), "w") as fh:
            fh.write(f"---\nid: liar-kit-sync-{KIT_VERSION}\nfrom: liar\nto: autonomous\n"
                     f"status: filed\nball: provider\nre: kit_sync\n---\nclaimed.\n")
        # Key by FILE, not sender: each sender has both a retrofit notice and a
        # sync receipt here, and a sender-keyed dict silently keeps whichever
        # sorted last — which is how this test first "failed" against correct code.
        r = {os.path.basename(x["file"]): x for x in
             rv.verify_all(self.registry, dry=True, mail_root=os.path.join(self.tmp, "mail"))}
        self.assertEqual(r["kit-sync-current.md"]["verdict"], "verified")
        self.assertEqual(r["kit-sync-lie.md"]["verdict"], "disputed")
        self.assertIn("absent", r["kit-sync-lie.md"]["note"])

    def test_receipt_naming_another_directory_is_disputed(self):
        """A `.`-relative run launched from the wrong cwd syncs some other repo
        and still reports `current`. The receipt records the path it ACTUALLY
        wrote, so the mismatch is detectable instead of silent (Residuum,
        2026-08-18, where nothing in the receipt could show what went wrong)."""
        with open(os.path.join(self.mail, "kit-sync-elsewhere.md"), "w") as fh:
            fh.write(f"---\nid: truth-kit-sync-{KIT_VERSION}\nfrom: truth\nto: autonomous\n"
                     f"status: filed\nball: provider\nrepo_path: {self.liar}\n"
                     f"re: kit_sync\n---\nclaimed.\n")
        r = {os.path.basename(x["file"]): x for x in
             rv.verify_all(self.registry, dry=True, mail_root=os.path.join(self.tmp, "mail"))}
        row = r["kit-sync-elsewhere.md"]
        self.assertEqual(row["verdict"], "disputed")
        self.assertIn("targeted another directory", row["note"])

    def test_a_notice_is_judged_against_its_own_claim_not_the_latest_kit(self):
        """babysynth closed correctly at 2.4.1 and was disputed the moment 2.5.0
        shipped. A notice claims a version; being behind a release that POSTDATES
        the claim is news, not a defect — otherwise every kit bump false-disputes
        every repo that had just finished."""
        older = "2.4.1"
        with open(os.path.join(self.mail, "retrofit-older.md"), "w") as fh:
            fh.write(f"---\nid: truth-retrofit-{older}\nfrom: truth\nto: autonomous\n"
                     f"status: filed\nball: provider\nre: retrofit\n---\nclaimed.\n")
        # `truth` declares the CURRENT kit version, so it satisfies 2.4.1 and more;
        # what matters is that a claim of 2.4.1 is not disputed for 2.5.0 existing.
        r = {os.path.basename(x["file"]): x for x in
             rv.verify_all(self.registry, dry=True, mail_root=os.path.join(self.tmp, "mail"))}
        row = r["retrofit-older.md"]
        self.assertNotIn("BEHIND at or below", row["note"])

    def test_a_tree_exceeding_its_claim_is_not_disputed(self):
        """Was: 'a repo that ADVANCED past its claim'. Computed currency (2.6.0)
        removed the declaration, so there is no longer a string to advance —
        but the property it protected still matters and is still asserted: a
        notice claiming an OLD version verifies when the tree meets more than
        it claimed. Three separate bugs lived in the gap this test guards
        (stale string, postdated release, advanced declaration); all three
        were symptoms of gating on a claim instead of reading the tree."""
        old = "2.0.0"
        with open(os.path.join(self.mail, "retrofit-advanced.md"), "w") as fh:
            fh.write(f"---\nid: truth-retrofit-{old}\nfrom: truth\nto: autonomous\n"
                     f"status: filed\nball: provider\nre: retrofit\n---\nclaimed.\n")
        r = {os.path.basename(x["file"]): x for x in
             rv.verify_all(self.registry, dry=True, mail_root=os.path.join(self.tmp, "mail"))}
        row = r["retrofit-advanced.md"]
        self.assertEqual(row["verdict"], "verified")
        self.assertIn("meets every requirement through", row["note"])

    def test_dry_run_writes_nothing(self):
        f = os.path.join(self.mail, "retrofit-lie.md")
        with open(f) as fh:
            before = fh.read()
        self._run(dry=True)
        with open(f) as fh:
            self.assertEqual(before, fh.read())


if __name__ == "__main__":
    unittest.main()

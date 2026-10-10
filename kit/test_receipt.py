"""The verify receipt (kit 2.9.0, horde brief hypersaw-010 P1): `gate` makes
the record say whether each gate ran, skipped or failed, and how much it
judged; `record` stores that beside the tree fingerprint."""
import json
import os
import shutil
import subprocess
import tempfile
import unittest

_GATES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor", "kit-gates.sh")


def run(script, strict=False):
    """Run `script` as a verify would: kit gates sourced, then record."""
    tmp = tempfile.mkdtemp()
    try:
        subprocess.run(["git", "init", "-q", tmp], check=True)
        body = (("set -euo pipefail\n" if strict else "") + "HARNESS_DIR=.harness; mkdir -p .harness\n"
                f". {_GATES}\nok=0\n{script}\nrecord fast $ok\n")
        r = subprocess.run(["bash", "-c", body], cwd=tmp, capture_output=True, text=True)
        with open(os.path.join(tmp, ".harness", "last-verify.json"), encoding="utf-8") as fh:
            rec = json.load(fh)                       # must be valid JSON, always
        prev = os.path.join(tmp, ".harness", "prev-verify.json")
        return r, rec, os.path.isfile(prev), os.listdir(os.path.join(tmp, ".harness"))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


class TestReceipt(unittest.TestCase):
    def test_ran_skipped_failed_and_counts(self):
        r, rec, _, files = run(
            "gate unit true || ok=1\n"
            "gate parity bash -c 'echo KIT-GATE cases=12' || ok=1\n"
            "gate san bash -c 'echo \"KIT-GATE skipped: no \\\"clang\\\" here\"' || ok=1\n"
            "gate lint false || ok=1\n")
        self.assertEqual(rec["exit"], 1)
        self.assertEqual(rec["gates"], [
            {"name": "unit", "result": "ran"},
            {"name": "parity", "result": "ran", "cases": 12},
            {"name": "san", "result": "skipped", "reason": "no clang here"},
            {"name": "lint", "result": "failed"}])
        self.assertEqual(len(rec["tree"]), 40)
        self.assertEqual([f for f in files if f.startswith("receipt.")], [])   # temp file consumed

    def test_floor_fails_an_empty_or_short_corpus(self):
        # horde: the parity gate that exited 0 on "0/0 scenarios".
        for out in ("echo KIT-GATE cases=0", "echo KIT-GATE cases=4", "true"):
            r, rec, _, _ = run(f"gate --min-cases 5 parity bash -c '{out}' || ok=1\n")
            self.assertEqual((rec["exit"], rec["gates"][0]["result"]), (1, "failed"), out)
            self.assertIn("its floor is 5", r.stderr)

    def test_floor_met_passes_and_a_skip_is_not_a_floor_failure(self):
        _, rec, _, _ = run("gate --min-cases 5 parity bash -c 'echo KIT-GATE cases=5' || ok=1\n"
                           "gate --min-cases 5 san bash -c 'echo KIT-GATE skipped: no compiler' || ok=1\n")
        self.assertEqual(rec["exit"], 0)
        self.assertEqual([g["result"] for g in rec["gates"]], ["ran", "skipped"])

    def test_strict_shell_still_writes_the_failing_line(self):
        # Under `set -e -o pipefail` a failing gate must still reach the receipt.
        r, rec, _, _ = run("gate lint false || ok=1\n", strict=True)
        self.assertEqual(rec["gates"], [{"name": "lint", "result": "failed"}])

    def test_unwrapped_verify_records_an_empty_receipt(self):
        _, rec, _, _ = run("true\n")
        self.assertEqual((rec["exit"], rec["gates"]), (0, []))

    def test_gate_output_passes_through_and_names_are_sanitised(self):
        r, rec, _, _ = run("gate 'we\"ird name' bash -c 'echo hello; echo oops >&2' || ok=1\n")
        self.assertIn("hello", r.stdout)
        self.assertIn("oops", r.stdout)                 # stderr is folded into stdout
        self.assertEqual(rec["gates"][0]["name"], "we_ird_name")

    def test_hostile_reports_never_make_the_record_unreadable(self):
        # Review, 2026-10-10: `cases=007`, a tab, a CR or a colour code in a
        # reason wrote invalid JSON, and an unreadable record then read as green.
        # run() json.loads the record, so reaching the asserts is the test.
        _, rec, _, _ = run(
            "gate a bash -c 'echo KIT-GATE cases=007' || ok=1\n"
            "gate b bash -c 'printf \"KIT-GATE skipped: no\\tcompiler\\r\\n\"' || ok=1\n"
            "gate c bash -c 'printf \"KIT-GATE skipped: \\033[31mred\\033[0m caf\\303\\251\\n\"' || ok=1\n"
            "gate d bash -c 'echo KIT-GATE cases=99999999999999999999' || ok=1\n")
        self.assertEqual(rec["gates"][0], {"name": "a", "result": "ran", "cases": 7})
        self.assertEqual(rec["gates"][1], {"name": "b", "result": "skipped", "reason": "nocompiler"})
        self.assertEqual(rec["gates"][2]["result"], "skipped")
        self.assertEqual(rec["gates"][3]["result"], "ran")          # 20 digits: not a count we accept

    def test_a_skip_line_does_not_switch_the_floor_off(self):
        r, rec, _, _ = run("gate --min-cases 50 p bash -c 'echo KIT-GATE cases=3; echo KIT-GATE skipped: partly' || ok=1\n")
        self.assertEqual((rec["exit"], rec["gates"][0]["result"]), (1, "failed"))

    def test_a_function_gate_keeps_its_variables_and_a_background_child_does_not_hang(self):
        import time
        t = time.time()
        _, rec, _, _ = run("f() { SEEN=yes; sleep 5 & }\ngate fn f || ok=1\n[ \"${SEEN:-}\" = yes ] || ok=1\n")
        self.assertEqual(rec["exit"], 0)
        self.assertLess(time.time() - t, 4)

    def test_bare_failing_gate_under_set_e_still_reaches_the_receipt(self):
        # No `|| ok=1`: the script dies at the gate, but the line was written first.
        tmp = tempfile.mkdtemp()
        try:
            subprocess.run(["git", "init", "-q", tmp], check=True)
            body = f"set -e\nHARNESS_DIR=.harness; mkdir -p .harness\n. {_GATES}\ngate lint false\n"
            r = subprocess.run(["bash", "-c", body + "echo not-reached"], cwd=tmp, capture_output=True, text=True)
            self.assertNotIn("not-reached", r.stdout)
            lines = [open(os.path.join(tmp, ".harness", f)).read() for f in os.listdir(os.path.join(tmp, ".harness"))
                     if f.endswith(".tmp")]
            self.assertEqual([json.loads(l) for l in lines], [{"name": "lint", "result": "failed"}])
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_tree_changed_while_verify_ran_is_recorded(self):
        _, rec, _, _ = run("gate a bash -c 'echo x > made-during-verify.txt' || ok=1\n")
        self.assertEqual(len(rec["tree_start"]), 40)
        self.assertNotEqual(rec["tree_start"], rec["tree"])
        _, rec, _, _ = run("gate a true || ok=1\n")
        self.assertEqual(rec["tree_start"], rec["tree"])

if __name__ == "__main__":
    unittest.main()

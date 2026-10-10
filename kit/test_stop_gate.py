"""The closing gate's verdict table (kit 2.9.0, horde brief hypersaw-009).

The table is the contract: (name, setup, env, hook input, expected exit), where
0 lets the session stop and 2 blocks it. Every row runs the REAL vendored
`stop-gate.sh` in a scratch repository whose "verify" is the real `record`.
Ported from horde's `tools/stop_gate_check.py` (16 rows, their PR #1029) and
extended with what a content fingerprint makes exact: deletions, a reverted
edit, a default branch that is not `main`, a repo with no remote.

Three controls keep the table honest. A gate that never blocks must get every
block row wrong; a gate that always blocks must get every allow row wrong (so
the allow rows are pinned too, which is the direction a blocking gate fails
in); and the gate as it stood before 2.9.0 must get exactly the tree-state
rows wrong. A table that a broken gate can pass proves nothing.

Rows marked REVIEW came from a fresh-context review on 2026-10-10 that broke
the first version: a stale record blocked a session that had only pulled, the
gate ran from whatever directory the session was in, and five mutations of
the gate passed the table as it then stood.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

_KIT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _KIT)
import kit_sync  # noqa: E402

GATE = open(os.path.join(_KIT, "vendor", "stop-gate.sh"), encoding="utf-8").read()
NEVER_BLOCKS = "#!/usr/bin/env bash\ncat >/dev/null\nexit 0\n"
ALWAYS_BLOCKS = "#!/usr/bin/env bash\ncat >/dev/null\nexit 2\n"
# The project-owned gate every scaffolded repo carried until 2.9.0, verbatim in
# behaviour: two tests, and `exit 0` when neither file exists.
BEFORE = r'''#!/usr/bin/env bash
set -uo pipefail
INPUT=$(cat)
ACTIVE=$(printf '%s' "$INPUT" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("stop_hook_active",False))' 2>/dev/null || echo "False")
[ "$ACTIVE" = "True" ] && exit 0
[ -f .harness/dirty ] && exit 2
if [ -f .harness/last-verify.json ]; then
  EXIT=$(python3 -c 'import json; print(json.load(open(".harness/last-verify.json")).get("exit",0))' 2>/dev/null || echo 0)
  [ "$EXIT" != "0" ] && exit 2
fi
exit 0
'''
_GIT = ["git", "-c", "user.email=t@example.invalid", "-c", "user.name=t", "-c", "commit.gpgsign=false"]


def sh(repo, *cmd, **kw):
    return subprocess.run(list(cmd), cwd=repo, capture_output=True, text=True, **kw)


def write(repo, rel, body):
    with open(os.path.join(repo, rel), "w", encoding="utf-8") as fh:
        fh.write(body)


def commit(repo, msg):
    sh(repo, *_GIT, "add", "-A")
    sh(repo, *_GIT, "commit", "-q", "-m", msg)


def verify(repo, code=0):
    """What `./verify fast` does at its end: the kit's real record()."""
    sh(repo, "bash", "-c", f"HARNESS_DIR=.harness; mkdir -p .harness; . .kit/kit-gates.sh; record fast {code}")


def new_repo(branch="main", remote=True, origin_head=True, ignore_harness=True, git=True):
    repo = os.path.realpath(tempfile.mkdtemp(prefix="stopgate-"))
    if not git:      # a folder that is not a repository at all
        os.makedirs(os.path.join(repo, ".kit"))
        for f in ("kit-gates.sh", "stop-gate.sh"):
            shutil.copy(os.path.join(_KIT, "vendor", f), os.path.join(repo, ".kit", f))
        return repo
    sh(repo, "git", "init", "-q", "-b", branch, ".")
    kit_sync.install(repo)
    write(repo, ".gitignore", (".harness/\n" if ignore_harness else "") + "ignored.log\n")
    os.makedirs(os.path.join(repo, "sub"))
    write(repo, "a.txt", "one\n")
    write(repo, "b.txt", "two\n")
    write(repo, "sub/c.txt", "three\n")
    commit(repo, "init")
    if remote:   # a remote-tracking ref is all the gate reads; no network
        sh(repo, "git", "update-ref", f"refs/remotes/origin/{branch}", "HEAD")
        if origin_head:   # most real clones have NO origin/HEAD; see the rows below
            sh(repo, "git", "symbolic-ref", "refs/remotes/origin/HEAD", f"refs/remotes/origin/{branch}")
    return repo


# --- setups: each leaves the repo in the state its row names ------------------
def s_clean(r): pass
def s_edit(r): write(r, "a.txt", "edited\n")
def s_new(r): write(r, "new.txt", "x\n")
def s_commit(r): s_edit(r); commit(r, "work")
def s_verified(r): s_edit(r); verify(r)
def s_verified_committed(r): s_edit(r); verify(r); commit(r, "work")
def s_edit_after(r): verify(r); s_edit(r)
def s_new_after(r): verify(r); s_new(r)
def s_commit_after(r): verify(r); s_edit(r); commit(r, "unverified")
def s_red(r): verify(r, 1)
def s_dirty(r): verify(r); write(r, ".harness/dirty", "t\n")
def s_ignored_after(r): verify(r); write(r, "ignored.log", "noise\n")
def s_deleted_after(r): verify(r); os.remove(os.path.join(r, "b.txt"))
def s_reverted(r): verify(r); write(r, "a.txt", "edited\n"); write(r, "a.txt", "one\n")
def s_plant_after(r): verify(r); write(r, ".kit-currency-plant-123", "probe\n")


def _worktree(r):
    sh(r, *_GIT, "worktree", "add", "-q", ".claude/worktrees/agent-1", "-b", "w1")


def s_nested_worktree_after(r):   # a sub-agent's worktree appears, then commits
    verify(r); _worktree(r)
    wt = os.path.join(r, ".claude", "worktrees", "agent-1")
    write(wt, "n.txt", "x\n"); commit(wt, "sub-agent work")


def s_nested_worktree_then_edit(r):
    verify(r); _worktree(r); s_edit(r)


def _old_record(r):   # a record from a kit before 2.9.0: no fingerprint
    os.makedirs(os.path.join(r, ".harness"), exist_ok=True)
    write(r, ".harness/last-verify.json", '{"target":"fast","exit":0,"git":"abc","ts":"t"}\n')


def s_old_record_clean(r): _old_record(r)
def s_old_record_edit(r): _old_record(r); s_edit(r)


def s_pulled(r):   # verified on a branch, PR merged, back on the default branch
    s_edit(r); verify(r); sh(r, *_GIT, "stash", "-u")


def s_stale_record_then_edit(r):
    s_pulled(r); write(r, "b.txt", "new work\n")


def s_red_then_corrupt(r):   # a failed run whose record is not valid JSON
    verify(r, 1)
    write(r, ".harness/last-verify.json", '{"target":"fast","exit":1,"gates":[{"cases":007}]}\n')


def s_feature_branch_checkout(r):   # a clean, pushed branch nobody verified HERE
    sh(r, *_GIT, "checkout", "-q", "-b", "feature")
    s_edit(r); commit(r, "feature work")
    sh(r, "git", "update-ref", "refs/remotes/origin/feature", "HEAD")


def s_add_fails(r):
    """`git add` dies (a required content filter whose program is missing, the
    Git LFS shape). The fingerprint must FAIL, not fall back to hashing the
    untouched index: that hash never changes, so every later edit would pass."""
    write(r, ".gitattributes", "*.dat filter=kitmissing\n")
    write(r, "x.dat", "payload\n")
    sh(r, "git", "config", "filter.kitmissing.clean", "kit-no-such-filter-program")
    sh(r, "git", "config", "filter.kitmissing.required", "true")
    verify(r); s_edit(r)


def s_unreadable_tmp(r):   # the fingerprint itself cannot be taken
    verify(r); s_edit(r)


def s_unknown_tree(r):   # a record copied from another clone
    verify(r)
    p = os.path.join(r, ".harness", "last-verify.json")
    with open(p, encoding="utf-8") as fh:
        d = json.load(fh)
    d["tree"] = "0" * 40
    write(r, ".harness/last-verify.json", json.dumps(d))


DENY = {"KIT_STOP_GATE_MODE": "deny"}
T = "tree"   # rows the pre-2.9.0 gate gets wrong
TABLE = [
    # name, setup, repo kwargs, env, hook input, want, tag
    ("clean tree, no record", s_clean, {}, DENY, {}, 0, ""),
    ("tracked edit, no record", s_edit, {}, DENY, {}, 2, T),
    ("new file, no record", s_new, {}, DENY, {}, 2, T),
    ("commit made, no record", s_commit, {}, DENY, {}, 2, T),
    ("edit, then verify", s_verified, {}, DENY, {}, 0, ""),
    ("edit, verify, then commit the same bytes", s_verified_committed, {}, DENY, {}, 0, ""),
    ("shell edit after verify, no marker", s_edit_after, {}, DENY, {}, 2, T),
    ("shell new file after verify, no marker", s_new_after, {}, DENY, {}, 2, T),
    ("unverified edit committed after verify", s_commit_after, {}, DENY, {}, 2, T),
    ("red record", s_red, {}, DENY, {}, 2, ""),
    ("dirty marker", s_dirty, {}, DENY, {}, 2, ""),
    ("dirty marker, already blocked once this cycle", s_dirty, {}, DENY, {"stop_hook_active": True}, 0, ""),
    ("ignored file written after verify", s_ignored_after, {}, DENY, {}, 0, ""),
    # horde's LIMIT row: file times cannot see a deletion; a fingerprint does.
    ("file deleted after verify", s_deleted_after, {}, DENY, {}, 2, T),
    ("edit after verify, reverted to the verified bytes", s_reverted, {}, DENY, {}, 0, ""),
    ("a foreign currency probe's plant appears after verify", s_plant_after, {}, DENY, {}, 0, ""),
    # Not every repo ignores .claude/worktrees/; the fingerprint must not care.
    ("a sub-agent's nested worktree appears and commits after verify", s_nested_worktree_after, {}, DENY, {}, 0, ""),
    ("nested worktree appears AND the lead edits after verify", s_nested_worktree_then_edit, {}, DENY, {}, 2, T),
    ("pre-2.9.0 record without a fingerprint, clean tree", s_old_record_clean, {}, DENY, {}, 0, ""),
    ("pre-2.9.0 record without a fingerprint, then an edit", s_old_record_edit, {}, DENY, {}, 2, T),
    ("record names a tree this clone never had, clean tree", s_unknown_tree, {}, DENY, {}, 0, ""),
    # REVIEW: no local work is never a block, whatever an old record says.
    ("REVIEW stale record, tree back at the default branch (pull, stash)", s_pulled, {}, DENY, {}, 0, ""),
    ("REVIEW stale record, then new unverified work", s_stale_record_then_edit, {}, DENY, {}, 2, T),
    # REVIEW: an unreadable record of a failed run used to read as green.
    ("REVIEW red run whose record is not valid JSON", s_red_then_corrupt, {}, DENY, {}, 2, "corrupt"),
    # REVIEW: the hook starts wherever the session's cwd is.
    ("REVIEW from a subdirectory: verified tree", s_verified, {"cwd": "sub"}, DENY, {}, 0, ""),
    ("REVIEW from a subdirectory: red record", s_red, {"cwd": "sub"}, DENY, {}, 2, "cwd"),
    ("REVIEW from a subdirectory: shell edit elsewhere in the repo", s_edit_after, {"cwd": "sub"}, DENY, {}, 2, T),
    # REVIEW: most clones have no origin/HEAD; the main/master fallback is the path the fleet takes.
    ("REVIEW no origin/HEAD, clean", s_clean, {"origin_head": False}, DENY, {}, 0, ""),
    ("REVIEW no origin/HEAD, commit made, no record", s_commit, {"origin_head": False}, DENY, {}, 2, T),
    ("REVIEW .harness is not gitignored, edit then verify", s_verified, {"ignore_harness": False}, DENY, {}, 0, ""),
    ("REVIEW not a repository at all", s_clean, {"git": False}, DENY, {}, 0, ""),
    ("REVIEW the tree cannot be fingerprinted", s_unreadable_tmp, {"tmpdir": "/nonexistent-kit-tmp"}, DENY, {}, 2, T),
    ("REVIEW git add fails outright, then an edit", s_add_fails, {}, DENY, {}, 2, T),
    # Ruled as it stands (it matches horde's own fix); each event carries
    # clean/pushed so the rule can be revisited with data.
    ("a clean, pushed branch that was never verified here", s_feature_branch_checkout, {}, DENY, {}, 2, T),
    ("OBSERVE: never-verified is logged too", s_feature_branch_checkout, {}, {}, {}, 0, ""),
    ("default branch is master, clean", s_clean, {"branch": "master"}, DENY, {}, 0, ""),
    ("default branch is master, commit made, no record", s_commit, {"branch": "master"}, DENY, {}, 2, T),
    ("no remote, clean", s_clean, {"remote": False}, DENY, {}, 0, ""),
    ("no remote, uncommitted edit, no record", s_edit, {"remote": False}, DENY, {}, 2, T),
    # Decision 84: the tree test logs by default; the two older tests keep blocking.
    ("OBSERVE: shell edit after verify is logged, not blocked", s_edit_after, {}, {}, {}, 0, ""),
    ("OBSERVE: dirty marker still blocks", s_dirty, {}, {}, {}, 2, ""),
]


def run_tables(bodies):
    """{impl: {row name: (exit code, events logged, stderr)}}.

    Each row's repository is built ONCE and every gate implementation is run
    against that same state: no gate writes inside the repo (pinned by
    test_nothing_is_written_under_dot_git), and building the state is most of
    the cost. Each run gets its own event log."""
    got = {k: {} for k in bodies}
    for name, setup, kw, env, inp, _want, _tag in TABLE:
        kw = dict(kw)
        cwd, tmpdir = kw.pop("cwd", ""), kw.pop("tmpdir", None)
        repo = new_repo(**kw)
        try:
            setup(repo)
            for impl, body in bodies.items():
                fleet = tempfile.mkdtemp(prefix="fleet-")
                try:
                    hook = os.path.join(repo, ".kit", "stop-gate.sh")
                    if body != GATE:          # the real gate is already installed, byte for byte
                        hook = os.path.join(fleet, "hook.sh")
                        write(fleet, "hook.sh", body)
                    e = {k: v for k, v in os.environ.items() if k != "KIT_STOP_GATE_MODE"}
                    e.update(KIT_FLEET_DIR=fleet, **env)
                    if tmpdir:
                        e["TMPDIR"] = tmpdir
                    r = subprocess.run(["bash", hook], cwd=os.path.join(repo, cwd), input=json.dumps(inp),
                                       capture_output=True, text=True, env=e)
                    events, log = [], os.path.join(fleet, "events.jsonl")
                    if os.path.isfile(log):
                        with open(log, encoding="utf-8") as fh:
                            events = [json.loads(l) for l in fh]
                    got[impl][name] = (r.returncode, events, r.stderr)
                finally:
                    shutil.rmtree(fleet, ignore_errors=True)
        finally:
            shutil.rmtree(repo, ignore_errors=True)
    return got


class TestStopGateTable(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.all = run_tables({"real": GATE, "never": NEVER_BLOCKS, "always": ALWAYS_BLOCKS,
                              "before": BEFORE})
        cls.real = cls.all["real"]

    def test_every_row(self):
        wrong = [f"{n}: want {w}, got {self.real[n][0]} {self.real[n][2][:200]}"
                 for n, _s, _k, _e, _i, w, _t in TABLE if self.real[n][0] != w]
        self.assertEqual(wrong, [])

    def test_observe_logs_a_verdict_and_no_file_names(self):
        code, events, _ = self.real["OBSERVE: shell edit after verify is logged, not blocked"]
        self.assertEqual(code, 0)
        self.assertEqual(len(events), 1)
        ev = events[0]
        self.assertEqual((ev["gate"], ev["event"], ev["why"], ev["files"], ev["clean"]),
                         ("stop-gate", "would-deny", "changed-after-verify", 1, False))
        self.assertNotIn("a.txt", json.dumps(ev))          # positions, never content

    def test_observe_event_tells_a_clean_pushed_checkout_from_unverified_work(self):
        # The reader of the observe week needs this to judge a would-deny.
        _, events, _ = self.real["OBSERVE: never-verified is logged too"]
        self.assertEqual(len(events), 1)
        ev = events[0]
        self.assertEqual((ev["why"], ev["clean"], ev["pushed"]), ("never-verified", True, True))

    def test_deny_names_the_files(self):
        self.assertIn("b.txt", self.real["file deleted after verify"][2])
        self.assertIn("a.txt", self.real["REVIEW from a subdirectory: shell edit elsewhere in the repo"][2])

    def test_nothing_is_written_under_dot_git(self):
        # The fingerprint uses a throwaway object store: an untracked file must
        # not be copied into .git/objects on every Stop (review, 2026-10-10).
        repo = new_repo()
        try:
            verify(repo)
            def loose():
                return sorted(f for _d, _s, fs in os.walk(os.path.join(repo, ".git", "objects")) for f in fs)
            before = loose()
            write(repo, "big-untracked.bin", "x" * 4096)
            subprocess.run(["bash", ".kit/stop-gate.sh"], cwd=repo, input="{}", text=True, capture_output=True,
                           env=dict(os.environ, KIT_FLEET_DIR=os.path.join(repo, "nofleet")))
            verify(repo)
            self.assertEqual(loose(), before)
        finally:
            shutil.rmtree(repo, ignore_errors=True)

    def test_control_a_gate_that_never_blocks_fails_every_block_row(self):
        got = self.all["never"]
        wrong = {n for n, _s, _k, _e, _i, w, _t in TABLE if got[n][0] != w}
        self.assertEqual(wrong, {n for n, _s, _k, _e, _i, w, _t in TABLE if w == 2})

    def test_control_a_gate_that_always_blocks_fails_every_allow_row(self):
        got = self.all["always"]
        wrong = {n for n, _s, _k, _e, _i, w, _t in TABLE if got[n][0] != w}
        self.assertEqual(wrong, {n for n, _s, _k, _e, _i, w, _t in TABLE if w == 0})

    def test_control_the_gate_before_this_change_fails_the_rows_this_change_is_for(self):
        # The tree rows, plus the two older-test holes the review found: a
        # corrupt red record read as green, and a record not found from a
        # subdirectory.
        got = self.all["before"]
        wrong = {n for n, _s, _k, _e, _i, w, _t in TABLE if got[n][0] != w}
        self.assertEqual(wrong, {n for n, _s, _k, _e, _i, _w, t in TABLE if t in (T, "corrupt", "cwd")})


class TestShimDoesNotFailOpen(unittest.TestCase):
    """A shim whose target is missing must block once, not exit 127 (which
    Claude Code treats as a non-blocking error: the gate silently off)."""
    SHIM = os.path.join(_KIT, "..", "harness", ".claude", "hooks", "stop-gate.sh")

    def _run(self, inp):
        tmp = tempfile.mkdtemp()
        try:
            return subprocess.run(["bash", self.SHIM], cwd=tmp, input=json.dumps(inp), text=True,
                                  capture_output=True, env=dict(os.environ, CLAUDE_PROJECT_DIR=tmp)).returncode
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_missing_gate_blocks_then_releases(self):
        self.assertEqual(self._run({"stop_hook_active": False}), 2)
        self.assertEqual(self._run({"stop_hook_active": True}), 0)

    def test_shim_runs_the_vendored_gate(self):
        repo = new_repo()
        try:
            s_edit_after(repo)
            r = subprocess.run(["bash", self.SHIM], cwd=repo, input="{}", text=True, capture_output=True,
                               env=dict(os.environ, CLAUDE_PROJECT_DIR=repo, KIT_STOP_GATE_MODE="deny"))
            self.assertEqual(r.returncode, 2)
            self.assertIn("a.txt", r.stderr)
        finally:
            shutil.rmtree(repo, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()

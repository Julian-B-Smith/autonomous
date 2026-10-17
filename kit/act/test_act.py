"""Layer-0 tests for the harness-owned actions (Phase A0, Decision 96).

Two layers. The CONTRACTS (`checks.py`) are pure, so every refusal is a
planted case here, one per incident that earned it. The COMMANDS run end to
end against a local bare git remote and a fake `gh` on PATH that keeps PR
state in a JSON file, so nothing touches GitHub or the network. The gate the
ratification set ("each refusal fires on a planted case") is these tests.
"""
import json, os, shutil, stat, subprocess, sys, tempfile, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, ".."))
import checks  # noqa: E402

GOOD = {"exit": 0, "tree": "a" * 40}


def _save(path, obj):
    with open(path, "w") as fh:
        json.dump(obj, fh)
BASE = {"branch": "feat", "default": "main", "pr_states": ["OPEN"], "record": GOOD,
        "tree_now": "a" * 40, "clean": True, "has_verify": True}


class TestPushContract(unittest.TestCase):
    def v(self, **kw):
        return checks.push(dict(BASE, **kw))

    def test_verified_branch_passes(self):
        self.assertEqual(self.v()[0], True)
        self.assertEqual(self.v(pr_states=[])[0], True)            # no PR yet

    def test_refusals(self):
        cases = {
            "force": dict(force=True),
            "deletes": dict(deletes=True),
            "default branch (Decision 96: PRs only)": dict(branch="main"),
            "PR already merged (the #47 incident)": dict(pr_states=["MERGED"]),
            "PR closed": dict(pr_states=["CLOSED"]),
            "no record": dict(record=None),
            "red record (horde's printed-not-tested push)": dict(record={"exit": 1, "tree": "a" * 40}),
            "uncommitted changes": dict(clean=False),
            "tree changed after verify": dict(tree_now="b" * 40),
            "pre-2.9 record naming another commit": dict(record={"exit": 0, "head_matches": False}),
            "no verify, but uncommitted changes": dict(has_verify=False, clean=False),
        }
        for name, kw in cases.items():
            ok, why = self.v(**kw)
            self.assertFalse(ok, name)
            self.assertTrue(why, name)

    def test_merged_plus_open_is_still_pushable(self):
        # A branch reused after a merge with a NEW open PR on it is live.
        self.assertTrue(self.v(pr_states=["MERGED", "OPEN"])[0])

    def test_pre_2_9_record_naming_this_commit_and_no_verify_repo(self):
        self.assertTrue(self.v(record={"exit": 0, "head_matches": True})[0])
        ok, why = self.v(has_verify=False, record=None)
        self.assertTrue(ok)
        self.assertIn("no ./verify", why)


class TestPrOpenContract(unittest.TestCase):
    F = dict(BASE, base="main", head_pushed=True, existing_open=None,
             body="> Origin: autonomous resident, 2026-10-17, Decision 96.\n\nBody.")

    def v(self, **kw):
        return checks.pr_open(dict(self.F, **kw))

    def test_good_pr_passes(self):
        self.assertTrue(self.v()[0])

    def test_refusals(self):
        cases = {
            "already open": dict(existing_open="https://github.com/o/r/pull/1"),
            "non-default base without --stack": dict(base="other"),
            "--stack onto a base whose PR merged (horde's 8-second race)":
                dict(base="other", stack=True, stack_base_state=None),
            "not pushed": dict(head_pushed=False),
            "no origin line": dict(body="Fixes things.\n\nOrigin: buried below"),
            "red record": dict(record={"exit": 1}),
        }
        for name, kw in cases.items():
            self.assertFalse(self.v(**kw)[0], name)

    def test_stack_onto_an_open_base_passes(self):
        self.assertTrue(self.v(base="other", stack=True, stack_base_state="OPEN")[0])


class TestPrCloseContract(unittest.TestCase):
    F = {"author": "me", "me": "me", "head": "kit-2.9.1-sync", "prefixes": ("kit-",),
         "superseded_by": "https://github.com/o/r/pull/9", "state": "OPEN"}

    def test_good_close_passes(self):
        self.assertTrue(checks.pr_close(self.F)[0])

    def test_refusals(self):
        for name, kw in {"not open": dict(state="MERGED"), "someone else's PR": dict(author="you"),
                         "a branch this kit did not make": dict(head="feature/x"),
                         "no replacement link": dict(superseded_by="#9")}.items():
            self.assertFalse(checks.pr_close(dict(self.F, **kw))[0], name)


# --- end to end: real git, a local bare remote, a fake gh --------------------
FAKE_GH = r'''#!/usr/bin/env python3
import json, os, sys
P = os.environ["FAKE_GH_STATE"]
s = json.load(open(P))
a = sys.argv[1:]
def opt(name, default=None):
    return a[a.index(name) + 1] if name in a else default
def save():
    json.dump(s, open(P, "w"))
def jq(rows, expr):
    if expr == ".[].state": return "\n".join(r["state"] for r in rows)
    if expr == ".[].number": return "\n".join(str(r["number"]) for r in rows)
    if expr == ".[0].url": return rows[0]["url"] if rows else ""
    if expr == ".[0].state": return rows[0]["state"] if rows else ""
    raise SystemExit("fake gh: unsupported jq " + expr)
if a[:2] == ["repo", "view"]:
    print(s["default"]); sys.exit(0)
if a[:2] == ["api", "user"]:
    print(s["me"]); sys.exit(0)
if a[:2] == ["pr", "list"]:
    rows = [p for p in s["prs"] if p["head"] == opt("--head")]
    st = opt("--state", "open")
    if st != "all": rows = [p for p in rows if p["state"] == st.upper()]
    print(jq(rows, opt("--jq"))); sys.exit(0)
if a[:2] == ["pr", "create"]:
    n = len(s["prs"]) + 1
    url = "https://github.com/o/r/pull/%d" % n
    s["prs"].append({"number": n, "head": opt("--head"), "base": opt("--base"), "state": "OPEN",
                     "url": url, "author": s["me"], "body": open(opt("--body-file")).read()})
    save(); print(url); sys.exit(0)
if a[:2] == ["pr", "view"]:
    p = next(p for p in s["prs"] if str(p["number"]) == a[2])
    print(json.dumps({"author": {"login": p["author"]}, "headRefName": p["head"], "state": p["state"]}))
    sys.exit(0)
if a[:2] == ["pr", "close"]:
    p = next(p for p in s["prs"] if str(p["number"]) == a[2])
    p["state"] = "CLOSED"; p["comment"] = opt("--comment"); save(); sys.exit(0)
raise SystemExit("fake gh: unsupported " + " ".join(a))
'''
GIT = ["git", "-c", "user.email=t@example.invalid", "-c", "user.name=t", "-c", "commit.gpgsign=false"]
VERIFY = '#!/usr/bin/env bash\ncd "$(dirname "$0")"; HARNESS_DIR=.harness; mkdir -p .harness\n. .kit/kit-gates.sh\nrecord fast 0\n'


class Fixture:
    """A repo with a vendored kit and a ./verify, its bare `origin`, a fake gh."""

    def __init__(self, verify=True):
        self.root = os.path.realpath(tempfile.mkdtemp(prefix="act-"))
        self.remote = os.path.join(self.root, "origin.git")
        self.repo = os.path.join(self.root, "repo")
        self.bin = os.path.join(self.root, "bin")
        self.state = os.path.join(self.root, "gh.json")
        self.fleet = os.path.join(self.root, "fleet")
        os.makedirs(self.bin); os.makedirs(self.fleet)
        with open(os.path.join(self.bin, "gh"), "w") as fh:
            fh.write(FAKE_GH)
        os.chmod(os.path.join(self.bin, "gh"), 0o755)
        _save(self.state, {"default": "main", "me": "me", "prs": []})
        subprocess.run(["git", "init", "-q", "--bare", "-b", "main", self.remote], check=True)
        subprocess.run(["git", "clone", "-q", self.remote, self.repo], check=True, capture_output=True)
        import kit_sync
        kit_sync.install(self.repo)
        self.write(".gitignore", ".harness/\n")
        self.write("a.txt", "one\n")
        if verify:
            self.write("verify", VERIFY, exe=True)
        self.git("checkout", "-q", "-b", "main")
        self.git("add", "-A"); self.git("commit", "-q", "-m", "init")
        self.git("push", "-q", "origin", "main")
        self.git("remote", "set-head", "origin", "main")
        self.env = dict(os.environ, PATH=self.bin + os.pathsep + os.environ["PATH"],
                        FAKE_GH_STATE=self.state, KIT_FLEET_DIR=self.fleet)

    def write(self, rel, body, exe=False):
        p = os.path.join(self.repo, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w") as fh:
            fh.write(body)
        if exe:
            os.chmod(p, os.stat(p).st_mode | stat.S_IXUSR)

    def git(self, *a):
        return subprocess.run(GIT + list(a), cwd=self.repo, capture_output=True, text=True)

    def verify(self):
        subprocess.run(["./verify"], cwd=self.repo, check=True, capture_output=True)

    def act(self, *a):
        return subprocess.run([sys.executable, os.path.join(HERE, "act.py"), *a], cwd=self.repo,
                              capture_output=True, text=True, env=self.env)

    def remote_head(self, br):
        out = subprocess.run(["git", "ls-remote", self.remote, f"refs/heads/{br}"],
                             capture_output=True, text=True).stdout.split()
        return out[0] if out else None

    def gh(self):
        with open(self.state) as fh:
            return json.load(fh)

    def events(self):
        p = os.path.join(self.fleet, "events.jsonl")
        if not os.path.isfile(p):
            return []
        with open(p) as fh:
            return [json.loads(l) for l in fh]

    def close(self):
        shutil.rmtree(self.root, ignore_errors=True)


class TestCommands(unittest.TestCase):
    def setUp(self):
        self.f = Fixture()
        self.f.git("checkout", "-q", "-b", "feat")
        self.body = os.path.join(self.f.root, "body.md")
        with open(self.body, "w") as fh:
            fh.write("> Origin: test, 2026-10-17, Decision 96.\n\nBody.\n")

    def tearDown(self):
        self.f.close()

    def commit_verified(self, text="two\n"):
        self.f.write("a.txt", text)
        self.f.verify()                                   # verify, THEN commit, as agents do
        self.f.git("commit", "-qam", "work")

    def test_verified_push_then_pr(self):
        self.commit_verified()
        r = self.f.act("push")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.f.remote_head("feat"), self.f.git("rev-parse", "HEAD").stdout.strip())
        r = self.f.act("pr-open", "--title", "t", "--body-file", self.body)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual([(p["head"], p["base"]) for p in self.f.gh()["prs"]], [("feat", "main")])
        ev = [e for e in self.f.events() if e.get("event") == "act"]
        self.assertEqual([(e["verb"], e["verdict"]) for e in ev], [("push", "ok"), ("pr-open", "ok")])
        self.assertNotIn("a.txt", json.dumps(ev))         # positions and verdicts, never content

    def test_push_refused_after_the_prs_merge(self):
        self.commit_verified(); self.f.act("push")
        st = self.f.gh(); st["prs"].append({"number": 1, "head": "feat", "state": "MERGED",
                                            "url": "u", "author": "me"})
        _save(self.f.state, st)
        before = self.f.remote_head("feat")
        self.commit_verified("three\n")
        r = self.f.act("push")
        self.assertEqual(r.returncode, 3, r.stderr)
        self.assertIn("already MERGED", r.stderr)
        self.assertEqual(self.f.remote_head("feat"), before)          # nothing left the machine

    def test_push_refused_when_the_tree_changed_after_verify(self):
        self.f.write("a.txt", "two\n"); self.f.verify()
        self.f.write("a.txt", "two, then a shell edit\n")
        self.f.git("commit", "-qam", "unverified")
        r = self.f.act("push")
        self.assertEqual(r.returncode, 3)
        self.assertIn("tree changed", r.stderr)
        self.assertIsNone(self.f.remote_head("feat"))

    def test_push_refused_on_red_and_on_the_default_branch(self):
        self.f.write("a.txt", "two\n")
        self.f.write(".harness/last-verify.json", '{"exit": 1, "tree": ""}')
        self.f.git("commit", "-qam", "w")
        self.assertEqual(self.f.act("push").returncode, 3)
        self.f.git("checkout", "-q", "main")
        r = self.f.act("push")
        self.assertEqual(r.returncode, 3)
        self.assertIn("default branch", r.stderr)

    def test_pr_open_refusals_end_to_end(self):
        self.commit_verified()
        with open(self.body, "w") as fh:
            fh.write("No origin here.\n")
        self.assertEqual(self.f.act("pr-open", "--title", "t", "--body-file", self.body).returncode, 3)
        with open(self.body, "w") as fh:
            fh.write("> Origin: test.\n")
        r = self.f.act("pr-open", "--title", "t", "--body-file", self.body)   # not pushed yet
        self.assertEqual(r.returncode, 3)
        self.assertIn("not pushed", r.stderr)
        self.assertEqual(self.f.gh()["prs"], [])

    def test_pr_close_only_our_batch_prs(self):
        st = self.f.gh()
        st["prs"] = [{"number": 1, "head": "kit-2.7.0-sync", "state": "OPEN", "url": "u1", "author": "me"},
                     {"number": 2, "head": "kit-2.7.0-sync", "state": "OPEN", "url": "u2", "author": "you"},
                     {"number": 3, "head": "feature", "state": "OPEN", "url": "u3", "author": "me"}]
        _save(self.f.state, st)
        new = "https://github.com/o/r/pull/9"
        self.assertEqual(self.f.act("pr-close", "1", "--superseded-by", new).returncode, 0)
        self.assertEqual(self.f.act("pr-close", "2", "--superseded-by", new).returncode, 3)
        self.assertEqual(self.f.act("pr-close", "3", "--superseded-by", new).returncode, 3)
        self.assertEqual([p["state"] for p in self.f.gh()["prs"]], ["CLOSED", "OPEN", "OPEN"])
        self.assertIn(new, self.f.gh()["prs"][0]["comment"])


class TestBatch(unittest.TestCase):
    """`act batch` end to end over a one-repo registry: steps applied, verify
    run, pushed and opened through the contracts, the older batch PR closed."""

    def test_plan_to_pr(self):
        f = Fixture()
        try:
            # The fixture repo on its default branch has an old-template gate,
            # and an open PR from an older batch to supersede.
            import steps
            old = subprocess.run(["git", "show", "722318c:harness/.claude/hooks/stop-gate.sh"],
                                 cwd=os.path.join(HERE, "..", ".."), capture_output=True, text=True).stdout
            if not old:
                self.skipTest("old template not in this clone's history")
            os.makedirs(os.path.join(f.repo, ".claude", "hooks"))
            f.write(".claude/hooks/stop-gate.sh", old, exe=True)
            f.write(".claude/settings.json", json.dumps({"permissions": {"deny": []}, "hooks": {
                "Stop": [{"hooks": [{"type": "command", "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/stop-gate.sh"}]}]}}))
            f.git("add", "-A"); f.git("commit", "-qm", "harness"); f.git("push", "-q", "origin", "main")
            st = f.gh(); st["prs"].append({"number": 1, "head": "kit-old-sync", "state": "OPEN",
                                           "url": "https://github.com/o/r/pull/1", "author": "me"})
            _save(f.state, st)
            reg = os.path.join(f.root, "registry.json")
            _save(reg, {"rules": [{"project": f.repo}]})
            plan = os.path.join(f.root, "plan.json")
            _save(plan, {"id": "test", "branch": "kit-test-sync", "supersedes": ["kit-old-sync"],
                         "steps": ["kit_sync", "closing_gate", "deny_rules"], "title": "kit test",
                         "commit_message": "kit test\n", "origin": "> **Origin.** test batch, Decision 96."})
            env = dict(f.env, KIT_ACT_REGISTRY=reg, KIT_ACT_DIR=os.path.join(f.root, "act"))
            r = subprocess.run([sys.executable, os.path.join(HERE, "act.py"), "batch", plan, "--open"],
                               cwd=f.root, capture_output=True, text=True, env=env, timeout=300)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            prs = f.gh()["prs"]
            self.assertEqual([(p["head"], p["state"]) for p in prs],
                             [("kit-old-sync", "CLOSED"), ("kit-test-sync", "OPEN")])
            self.assertTrue(prs[1]["body"].startswith("> **Origin.**"))
            self.assertIn("pull/2", prs[0]["comment"])
            # What the branch carries: the shim and the deny rules.
            show = lambda p: subprocess.run(["git", "show", f"kit-test-sync:{p}"], cwd=f.remote,
                                            capture_output=True, text=True).stdout
            self.assertIn(".kit/stop-gate.sh", show(".claude/hooks/stop-gate.sh"))
            self.assertTrue(set(steps.DENY) <= set(json.loads(show(".claude/settings.json"))["permissions"]["deny"]))
            # A second run finds the branch already on the remote and does nothing.
            r = subprocess.run([sys.executable, os.path.join(HERE, "act.py"), "batch", plan, "--open"],
                               cwd=f.root, capture_output=True, text=True, env=env, timeout=300)
            self.assertIn("already on remote", r.stdout)
            self.assertEqual(len(f.gh()["prs"]), 2)
        finally:
            f.close()

    def test_template_deny_list_matches_the_batch_step(self):
        import steps
        with open(os.path.join(HERE, "..", "..", "harness", ".claude", "settings.json")) as fh:
            s = json.load(fh)
        self.assertTrue(set(steps.DENY) <= set(s["permissions"]["deny"]))


if __name__ == "__main__":
    unittest.main()

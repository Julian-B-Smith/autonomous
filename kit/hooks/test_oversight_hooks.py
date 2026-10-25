"""Layer-0 tests for the O0.5 hooks (Decision 84). Each hook is run exactly as
Claude Code runs it — JSON on stdin — against a scratch fleet dir, so nothing
here touches the real event log or settings."""
import json, os, shutil, subprocess, sys, tempfile, unittest

HERE = os.path.dirname(os.path.abspath(__file__))


def run(hook, payload, env):
    return subprocess.run([sys.executable, os.path.join(HERE, hook)], input=json.dumps(payload),
                          text=True, capture_output=True, env=env, timeout=30)


class OversightHooks(unittest.TestCase):
    def setUp(self):
        self.fleet = tempfile.mkdtemp()
        self.repo = tempfile.mkdtemp()
        subprocess.run(["git", "init", "-q", self.repo], check=True)
        for f, body in (("DECISIONS.md", "# Decisions\n"), ("verify", "#!/bin/sh\n")):
            open(os.path.join(self.repo, f), "w").write(body)
        subprocess.run(["git", "-C", self.repo, "add", "-A"], check=True)
        subprocess.run(["git", "-C", self.repo, "-c", "user.email=t@t", "-c", "user.name=t",
                        "commit", "-q", "-m", "init"], check=True)
        self.env = dict(os.environ, KIT_FLEET_DIR=self.fleet)

    def tearDown(self):
        shutil.rmtree(self.fleet, ignore_errors=True)
        shutil.rmtree(self.repo, ignore_errors=True)

    def events(self):
        p = os.path.join(self.fleet, "events.jsonl")
        return [json.loads(l) for l in open(p)] if os.path.exists(p) else []

    # gate-change ----------------------------------------------------------------
    def test_editing_a_gate_without_a_rationale_is_logged_would_deny_and_not_blocked(self):
        r = run("gate-change.py", {"cwd": self.repo, "tool_input": {"file_path": os.path.join(self.repo, "verify")}}, self.env)
        self.assertEqual((r.returncode, r.stdout), (0, ""))          # observe: never blocks
        self.assertEqual([e["event"] for e in self.events()], ["would-deny"])

    def test_a_GATE_CHANGE_line_in_the_tree_lifts_it(self):
        with open(os.path.join(self.repo, "DECISIONS.md"), "a") as fh:
            fh.write("12. GATE-CHANGE: verify gains a check\n")
        run("gate-change.py", {"cwd": self.repo, "tool_input": {"file_path": os.path.join(self.repo, "verify")}}, self.env)
        self.assertEqual([e["event"] for e in self.events()], ["gate-change-ok"])

    def test_a_non_gate_file_is_not_the_gates_business(self):
        run("gate-change.py", {"cwd": self.repo, "tool_input": {"file_path": os.path.join(self.repo, "README.md")}}, self.env)
        self.assertEqual(self.events(), [])

    # config-guard ---------------------------------------------------------------
    def test_disabling_all_hooks_is_logged_and_observe_mode_lets_it_through(self):
        cfg = os.path.join(self.fleet, "settings.json")
        json.dump({"disableAllHooks": True}, open(cfg, "w"))
        r = run("config-guard.py", {"source": "project_settings", "file_path": cfg}, self.env)
        self.assertEqual(r.returncode, 0)
        ev = [e for e in self.events() if e["event"] == "would-deny"]
        self.assertEqual(ev[0]["gate"], "config-guard")

    def test_a_harmless_settings_change_is_only_recorded(self):
        cfg = os.path.join(self.fleet, "settings.json")
        json.dump({"env": {"X": "1"}}, open(cfg, "w"))
        run("config-guard.py", {"source": "project_settings", "file_path": cfg}, self.env)
        self.assertEqual([e["event"] for e in self.events()], ["config-change"])

    # hook-selftest --------------------------------------------------------------
    def test_a_configured_kit_hook_that_is_gone_is_named_once(self):
        cfg = os.path.join(self.fleet, "settings.json")
        json.dump({"hooks": {"SessionStart": [{"hooks": [
            {"type": "command", "command": 'f="$HOME/Documents/Claude/autonomous/kit/hooks/no-such-hook.py"; [ -x "$f" ] && python3 "$f" || true'}]}]}},
            open(cfg, "w"))
        r = run("hook-selftest.py", {}, dict(self.env, KIT_SETTINGS_PATH=cfg))
        self.assertIn("no-such-hook.py", r.stdout)
        self.assertEqual([e["event"] for e in self.events()], ["hook-count", "hook-missing"])

    def test_every_gate_starts_in_observe(self):
        modes = json.load(open(os.path.join(HERE, "gate_modes.json")))
        self.assertEqual({k: v for k, v in modes.items() if not k.startswith("_")},
                         {"hook-selftest": "observe", "config-guard": "observe", "gate-change": "observe"})



class TestRepoName(unittest.TestCase):
    def test_a_worktree_is_filed_under_its_main_repo(self):
        import fleet_events as fe
        with tempfile.TemporaryDirectory() as root:
            main = os.path.join(os.path.realpath(root), "myrepo")
            os.makedirs(main)
            git = ["git", "-C", main, "-c", "user.email=t@example.invalid", "-c", "user.name=t"]
            subprocess.run(["git", "init", "-q", main], check=True)
            subprocess.run(git + ["commit", "-q", "--allow-empty", "-m", "i"], check=True)
            wt = os.path.join(os.path.realpath(root), "agent-abc123")
            subprocess.run(git + ["worktree", "add", "-q", wt], check=True, capture_output=True)
            self.assertEqual(fe.repo_name(wt), "myrepo")
            self.assertEqual(fe.repo_name(main), "myrepo")
            self.assertEqual(fe.repo_name(os.path.join(root, "not-a-repo")), "not-a-repo")


class TestDistilleryDailyHook(unittest.TestCase):
    """The hook starts distillery's daily sweep detached and returns at once,
    and costs nothing on a day it already ran (Decision 101)."""
    HOOK = os.path.join(HERE, "distillery-daily-async.sh")

    def setUp(self):
        self.d = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.d, "distillery", "bin"))
        self.marker = os.path.join(self.d, "ran")
        daily = os.path.join(self.d, "distillery", "bin", "daily")
        with open(daily, "w") as fh:
            fh.write("import time\ntime.sleep(2)\nopen(%r, 'w').write('x')\n" % self.marker)
        os.chmod(daily, 0o755)
        self.env = dict(os.environ, DISTILLERY_HOME=os.path.join(self.d, "distillery"),
                        DISTILLERY_DAILY_HOME=os.path.join(self.d, "state"))

    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)

    def test_starts_the_sweep_detached(self):
        import time
        t = time.time()
        r = subprocess.run(["bash", self.HOOK], env=self.env, capture_output=True, timeout=10)
        self.assertEqual(r.returncode, 0)
        self.assertLess(time.time() - t, 1.5)          # the session never waits on the sweep
        for _ in range(50):
            if os.path.exists(self.marker):
                break
            time.sleep(0.1)
        self.assertTrue(os.path.exists(self.marker))

    def test_does_nothing_on_a_day_it_already_ran(self):
        import time
        os.makedirs(os.path.join(self.d, "state"))
        with open(os.path.join(self.d, "state", "last-run"), "w") as fh:
            fh.write(time.strftime("%Y-%m-%d") + "\n")
        subprocess.run(["bash", self.HOOK], env=self.env, timeout=10)
        time.sleep(2.5)
        self.assertFalse(os.path.exists(self.marker))

    def test_absent_distillery_is_a_no_op(self):
        env = dict(self.env, DISTILLERY_HOME=os.path.join(self.d, "nope"))
        self.assertEqual(subprocess.run(["bash", self.HOOK], env=env, timeout=10).returncode, 0)

if __name__ == "__main__":
    unittest.main()

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


if __name__ == "__main__":
    unittest.main()

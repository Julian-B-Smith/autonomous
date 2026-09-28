"""The session boundary must not lie about state, and must not block on
bookkeeping. Both properties have burned this fleet already."""
import datetime
import json
import os
import time
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import registry  # noqa: E402
import state     # noqa: E402


def _repo():
    d = tempfile.mkdtemp()
    subprocess.run(["git", "init", "-q", d], check=True, capture_output=True)
    with open(os.path.join(d, "f.txt"), "w") as fh:
        fh.write("x\n")
    subprocess.run(["git", "-C", d, "add", "-A"], check=True, capture_output=True)
    subprocess.run(["git", "-C", d, "-c", "user.email=t@t", "-c", "user.name=t",
                    "commit", "-qm", "init"], check=True, capture_output=True)
    return d


class State(unittest.TestCase):
    def setUp(self):
        self.repo = _repo()

    def tearDown(self):
        shutil.rmtree(self.repo, ignore_errors=True)

    def test_a_verify_result_from_another_commit_is_reported_stale(self):
        """The whole declared-vs-effective family in one line: a recorded green
        from a different commit says NOTHING about HEAD, and repeating its
        colour would be the exact error the kit exists to prevent."""
        os.makedirs(os.path.join(self.repo, ".harness"))
        with open(os.path.join(self.repo, ".harness", "last-verify.json"), "w") as fh:
            json.dump({"target": "fast", "exit": 0, "git": "deadbee", "ts": "t"}, fh)
        v = state.gather(self.repo)["verify"]
        self.assertTrue(v["stale"])
        self.assertIn("DIFFERENT commit", v["note"])

    def test_newest_decisions_are_by_NUMBER_not_file_position(self):
        """This repo appends before a marker, so the file tail is decision 18
        while the repo is at 66. Showing the tail to someone catching up looks
        like an answer and is not one."""
        with open(os.path.join(self.repo, "DECISIONS.md"), "w") as fh:
            fh.write("1. **First**\n60. **Newest**\n2. **Second**\n")
        tail = state.gather(self.repo)["decisions_tail"]
        self.assertTrue(any("Newest" in t for t in tail))

    def _file(self, name, text):
        with open(os.path.join(self.repo, name), "w", encoding="utf-8") as fh:
            fh.write(text)

    def test_closed_gate_prose_is_not_the_current_phase(self):
        """resume-workshop brief, fixture 1: a bolded closed-gate paragraph
        containing "active" above the real in-progress heading."""
        self._file("ROADMAP.md", "## Phase 1 — Intake\n\n**Gate: MET.** `./verify fast` green with "
                   "the validator active.\n\n## Phase 7 — First real client *(in progress; operator work)*\n")
        self.assertTrue(state._current_phase(self.repo).startswith("## Phase 7"))

    def test_the_kit_template_heading_is_not_a_phase(self):
        """"Invariants under active protection" sits in a dozen roadmaps."""
        self._file("ROADMAP.md", "## Invariants under active protection\n\n## M0 — Port · **IN PROGRESS**\n")
        self.assertIn("M0", state._current_phase(self.repo))
        self._file("ROADMAP.md", "## Invariants under active protection\n\n## M0 — Port\n")
        self.assertIsNone(state._current_phase(self.repo))
        self.assertIn("none marked", state.render(state.gather(self.repo)))

    def test_a_bullet_marks_the_phase_only_explicitly_and_never_when_done(self):
        self._file("ROADMAP.md", "- **D3 — The analyst.** **\u2190 current phase.** Fan-out.\n")
        self.assertIn("D3", state._current_phase(self.repo))
        self._file("ROADMAP.md", "- **Status:** DONE 2026-09-21. Was: in-progress, phase gate.\n"
                   "- **Status:** in-progress (an intake brief)\n")
        self.assertIsNone(state._current_phase(self.repo))

    def test_list_items_inside_a_decision_are_not_decisions(self):
        """resume-workshop brief, fixture 2: ### D-041..D-043 headings, a
        numbered list 1.-4. inside D-042's body."""
        self._file("DECISIONS.md", "# Decisions\n\n### D-041 — a\n\nbody\n\n### D-042 — b\n\n"
                   "1. one\n2. two\n3. three\n4. four\n\n### D-043 — c\n")
        self.assertEqual([d.split(" —")[0] for d in state._decisions_tail(self.repo)],
                         ["### D-041", "### D-042", "### D-043"])

    def test_numbered_line_entries_still_work_and_dates_are_not_ids(self):
        """This repo's own style — `79. **…**` under a plain title — must keep
        working; a date heading must never be read as entry 2026."""
        self._file("DECISIONS.md", "# Decisions\n\n## 2026-08-01 — context\n\n79. **newest**\n"
                   "12. **older**\n78. **middle**\n")
        self.assertEqual([d.split(".")[0] for d in state._decisions_tail(self.repo)], ["12", "78", "79"])

    def test_stale_reflections_are_flagged_for_graduate_or_drop(self):
        old = (datetime.date.today() - datetime.timedelta(days=40)).isoformat()
        new = datetime.date.today().isoformat()
        with open(os.path.join(self.repo, "REFLECTIONS.md"), "w") as fh:
            fh.write(f"- [{old}] ancient question\n- [{new}] fresh one\n")
        r = state.gather(self.repo)["reflections"]
        self.assertEqual(len(r["entries"]), 2)
        self.assertEqual(len(r["stale"]), 1)
        self.assertIn("ancient", r["stale"][0]["text"])

    def test_no_auditor_means_no_audit_line_not_a_none(self):
        """Absence of an auditor is not staleness: the line is omitted."""
        self.assertNotIn("last audit", state.render(state.gather(self.repo)))

    def test_auditor_with_no_report_renders_none_and_stale(self):
        os.makedirs(os.path.join(self.repo, ".claude", "agents"))
        open(os.path.join(self.repo, ".claude", "agents", "auditor.md"), "w").write("# auditor\n")
        s = state.gather(self.repo)
        self.assertTrue(s["audit"]["stale"])
        self.assertIn("last audit: none", state.render(s))

    def test_a_stale_report_says_so_and_a_fresh_one_does_not(self):
        os.makedirs(os.path.join(self.repo, "docs", "audits"))
        open(os.path.join(self.repo, "project.manifest.json"), "w").write(
            json.dumps({"auditor": {"agent": "auditor", "cadence_days": 7}}))
        p = os.path.join(self.repo, "docs", "audits", "2026-09-01-repo-audit.md")
        open(p, "w").write("# audit\n")
        os.utime(p, (time.time() - 10 * 86400, time.time() - 10 * 86400))
        out = state.render(state.gather(self.repo))
        self.assertIn("10 days ago", out); self.assertIn("STALE", out)
        os.utime(p, None)
        self.assertNotIn("STALE", state.render(state.gather(self.repo)))

    def test_render_says_so_when_no_session_has_ever_closed(self):
        out = state.render(state.gather(self.repo))
        self.assertIn("has not closed a session yet", out)


class Registry(unittest.TestCase):
    def setUp(self):
        self.repo = _repo()
        self.reg = tempfile.mkdtemp()
        os.environ["KIT_SESSION_REGISTRY"] = self.reg

    def tearDown(self):
        shutil.rmtree(self.repo, ignore_errors=True)
        shutil.rmtree(self.reg, ignore_errors=True)
        os.environ.pop("KIT_SESSION_REGISTRY", None)

    def _hook(self, name, payload, cwd=None):
        """Run a session hook exactly as Claude Code does: JSON on stdin."""
        hook = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "hooks", name)
        return subprocess.run([sys.executable, hook], input=payload, text=True,
                              capture_output=True, cwd=cwd or self.repo,
                              env=dict(os.environ, KIT_SESSION_REGISTRY=self.reg), timeout=30)

    def test_start_hook_opens_a_record_with_the_facts_it_was_built_against(self):
        out = self._hook("session-open.py", json.dumps(
            {"session_id": "abc-1", "cwd": self.repo, "source": "startup"}))
        self.assertEqual(out.returncode, 0)
        self.assertIn("session record: abc-1", out.stdout)
        row = registry.list_open()[0]
        for k in ("path", "head_at_open", "branch_at_open", "doctrine_sha",
                  "kit_version", "commands_sha"):
            self.assertIn(k, row)
        self.assertFalse(row["path"].startswith("/Users/"))   # ~-relative, never identity

    def test_a_resumed_session_refreshes_its_record_not_a_second_one(self):
        self._hook("session-open.py", json.dumps({"session_id": "abc-2", "cwd": self.repo}))
        first = registry.list_open()[0]["opened_at"]
        self._hook("session-open.py", json.dumps(
            {"session_id": "abc-2", "cwd": self.repo, "source": "resume"}))
        rows = registry.list_open()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["opened_at"], first)
        self.assertIn("refreshed_at", rows[0])

    def test_end_hook_records_a_dirty_tree_as_dirty(self):
        self._hook("session-open.py", json.dumps({"session_id": "abc-3", "cwd": self.repo}))
        with open(os.path.join(self.repo, "wip.txt"), "w") as fh:
            fh.write("unfinished\n")
        out = self._hook("session-close.py", json.dumps(
            {"session_id": "abc-3", "cwd": self.repo, "reason": "prompt_input_exit"}))
        self.assertEqual((out.returncode, out.stdout), (0, ""))
        self.assertEqual(registry.list_open(), [])
        with open(os.path.join(self.reg, "closed", "abc-3.json")) as fh:
            closed = json.load(fh)
        self.assertIn("dirty: 1 file", closed["close_state"]["summary"])
        self.assertEqual(closed["close_state"]["end_reason"], "prompt_input_exit")

    def test_hooks_fail_open_and_silent_on_garbage(self):
        for name in ("session-open.py", "session-close.py"):
            out = self._hook(name, "not json at all")
            self.assertEqual((out.returncode, out.stdout), (0, ""), name)
        self.assertEqual(registry.list_open(), [])

    def test_sweep_closes_only_rows_past_the_line_and_says_why(self):
        registry.open_session(self.repo, "old", at="2026-09-01T00:00:00Z")
        registry.open_session(self.repo, "new")
        swept = registry.sweep_stale(12, "swept at O0 install")
        self.assertEqual(swept, ["old"])
        self.assertEqual([r["session_id"] for r in registry.list_open()], ["new"])
        with open(os.path.join(self.reg, "closed", "old.json")) as fh:
            self.assertIn("unclean", json.load(fh)["close_state"]["summary"])

    def test_open_list_close_roundtrip(self):
        self.assertTrue(registry.open_session(self.repo, "s1")["ok"])
        self.assertEqual(len(registry.list_open()), 1)
        self.assertTrue(registry.close_session("s1")["ok"])
        self.assertEqual(registry.list_open(), [])

    def test_two_sessions_in_one_repo_are_two_rows_not_a_collision(self):
        """Keyed by session_id, not repo: a fleet job and the human working in
        the same repo must be legible, not overwrite each other."""
        registry.open_session(self.repo, "s1")
        registry.open_session(self.repo, "s2")
        self.assertEqual(len(registry.list_open()), 2)

    def test_a_stale_row_for_this_repo_is_visible_to_the_next_session(self):
        registry.open_session(self.repo, "crashed")
        stale = registry.stale_rows_for(self.repo, session_id="new")
        self.assertEqual([r["session_id"] for r in stale], ["crashed"])

    def test_an_unconfigured_registry_never_blocks(self):
        """Bookkeeping that can stop work is worse than no bookkeeping."""
        os.environ["KIT_SESSION_REGISTRY"] = os.path.join(self.reg, "nope", "deeper")
        r = registry.open_session(self.repo, "s1")
        self.assertIn("ok", r)              # returns a verdict, never raises
        self.assertEqual(registry.close_session("s1").get("ok"), True)

    def test_the_machine_label_is_overridable(self):
        """The macOS default hostname embeds the owner's name
        ("Julians-MacBook-Air"), which is fine locally and is a personal-identity
        leak once this store is a shared repo. The promotion step sets a neutral
        label; this pins that the override actually takes."""
        os.environ["KIT_SESSION_MACHINE"] = "mac"
        try:
            registry.open_session(self.repo, "s1")
            self.assertEqual(registry.list_open()[0]["machine"], "mac")
        finally:
            os.environ.pop("KIT_SESSION_MACHINE", None)

    def test_the_row_carries_no_content_and_no_user_identity(self):
        """It is the one sanctioned cross-repo write precisely because it
        carries nothing worth reading — and it may live in a synced repo."""
        registry.open_session(self.repo, "s1")
        row = registry.list_open()[0]
        self.assertEqual(set(row), {"repo", "session_id", "machine", "opened_at"})
        self.assertNotIn(os.path.expanduser("~"), json.dumps(row))


if __name__ == "__main__":
    unittest.main()


class Boards(unittest.TestCase):
    def test_only_the_standards_repo_publishes(self):
        """Two sessions racing on one artifact turned every boundary into a
        publish conflict (2026-09-02). The guard is in code so no session has to
        remember it: from any other repo the renderer says NOT-PUBLISHER."""
        import render_registry
        here = os.getcwd()
        foreign = tempfile.mkdtemp()
        subprocess.run(["git", "init", "-q", foreign], check=True, capture_output=True)
        try:
            os.chdir(foreign)
            self.assertFalse(render_registry.is_publisher())
        finally:
            os.chdir(here)
            shutil.rmtree(foreign, ignore_errors=True)
        self.assertTrue(render_registry.is_publisher())   # run from kit/session in autonomous

    def test_threads_board_ignores_its_own_clock(self):
        """The stamp now carries HH:MM, so a byte-compare would say CHANGED on
        every routine tick and republish forever — the cry-wolf the Session
        Board already fixed once (2026-08-31). Only content counts."""
        import render_registry, render_threads
        root = tempfile.mkdtemp()
        try:
            page = render_threads.render()
            new, d = render_registry.changed(page, root=root, marker=render_threads.MARKER)
            self.assertTrue(new)                           # no marker yet: changed
            render_registry.record(d, root=root, marker=render_threads.MARKER)
            later = page.replace("as of <b>", "as of <b>1999-01-01 00:00 UTC", 1)
            self.assertFalse(render_registry.changed(later, root=root, marker=render_threads.MARKER)[0])
            self.assertTrue(render_registry.changed(page + "<p>new thread</p>", root=root,
                                                    marker=render_threads.MARKER)[0])
        finally:
            shutil.rmtree(root, ignore_errors=True)

    def test_session_ages_alone_are_not_a_change(self):
        """An hourly routine must not republish a page whose only difference is
        that every open session is a little older."""
        import render_registry
        a = '<tr class=""><td class="num">39.2h</td></tr>'
        b = '<tr class=""><td class="num">40.1h</td></tr>'
        stale = '<tr class="stale"><td class="num">40.1h</td></tr>'
        self.assertEqual(render_registry._significant(a), render_registry._significant(b))
        self.assertNotEqual(render_registry._significant(a), render_registry._significant(stale))

    def test_the_two_boards_keep_separate_markers(self):
        """One shared marker would let a Threads change mark the Session Board
        as published, and the next Session change would compare against the
        wrong page."""
        import render_registry, render_threads
        root = tempfile.mkdtemp()
        try:
            render_registry.record("aaa", root=root)
            render_registry.record("bbb", root=root, marker=render_threads.MARKER)
            self.assertEqual(sorted(os.listdir(root)), [".board-render", ".threads-render"])
        finally:
            shutil.rmtree(root, ignore_errors=True)

    def test_an_unconfirmed_publish_is_offered_again_not_forgotten(self):
        """Recording at render time let a failed publish read as published
        forever (found on the first live run, 2026-09-26). Until the caller
        confirms, the board stays CHANGED; after confirm, UNCHANGED."""
        import boards
        root, out = tempfile.mkdtemp(), tempfile.mkdtemp()
        try:
            first = boards.run(out, "test", root=root)
            self.assertEqual({v for _, v, _, _ in first}, {"CHANGED"})
            self.assertTrue(all(p and os.path.exists(p) for _, _, p, _ in first))
            again = boards.run(out, "test", root=root)           # nobody confirmed
            self.assertEqual({v for _, v, _, _ in again}, {"CHANGED"})
            for name, _, _, _ in again:
                self.assertTrue(boards.confirm(out, name, root=root))
            self.assertFalse(boards.confirm(out, "session-board", root=root))  # nothing pending
            for f in os.listdir(out):
                os.remove(os.path.join(out, f))
            settled = boards.run(out, "test", root=root)
            self.assertEqual({v for _, v, _, _ in settled}, {"UNCHANGED"})
            self.assertEqual(os.listdir(out), [])          # nothing to publish, nothing written
            with open(os.path.join(root, "boards.log")) as fh:
                self.assertEqual(len(fh.read().splitlines()), 5)   # 3 runs + 2 confirms
        finally:
            shutil.rmtree(root, ignore_errors=True)
            shutil.rmtree(out, ignore_errors=True)

    def test_threads_board_renders_every_section(self):
        import render_threads
        page = render_threads.render()
        for label in ("overdue", "obligations open", "answered, unread"):
            self.assertIn(label, page)
        self.assertIn("as of", page)


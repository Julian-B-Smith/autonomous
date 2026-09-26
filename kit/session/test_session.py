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


"""Layer-0 tests for ball_scan. Deterministic, stdlib-only.

Every case here is a bug that real fleet data produced on the first run. The
module's whole value is that it is READ — so each of these is really a test
against false positives, since a section that cries wolf gets skipped and then
it might as well not exist.
"""

import datetime
import os
import shutil
import tempfile
import unittest

import ball_scan

TODAY = datetime.date(2026, 8, 9)


def _fm(d, name, **kw):
    body = "---\n" + "".join(f"{k.replace('_', '-')}: {v}\n" for k, v in kw.items()) + "---\n"
    p = os.path.join(d, name)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(body)
    return p


class TestThreadResolution(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.box = os.path.join(self.tmp, "integrations", "peer")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def scan(self):
        return ball_scan.scan_repo(self.tmp, "me", TODAY)

    def test_terminal_status_closes_thread_regardless_of_dates(self):
        """antiphon-001 reported 12d overdue while CLOSED: its ratification
        carried the same date as the response it closed, so the tiebreak picked
        the wrong file. Closure is monotonic and must beat date ordering."""
        _fm(self.box, "brief.md", id="x-1", ball="provider",
            status="filed", respond_by="2026-07-01", filed="2026-07-01")
        _fm(self.box, "response.md", id="x-1", ball="consumer",
            status="responded", responded="2026-07-28")
        _fm(self.box, "ratification.md", id="x-1", ball="none",
            status="closed", responded="2026-07-28")
        self.assertEqual(self.scan(), [])

    def test_a_status_that_explains_itself_still_closes_the_thread(self):
        """HYPERSAW notice terminal-status-exact-match, 2026-09-20: a file that
        closes a thread and says why (`closed — all three answers taken`) left
        the thread open forever, because the whole line was compared to the
        terminal set. 11 files across FOUNDATIONS, Orrery and Tonality carried
        that shape on the day it was fixed. Only the first word is the state."""
        _fm(self.box, "brief.md", id="x-2", ball="provider",
            status="filed", respond_by="2026-07-01", filed="2026-07-01")
        _fm(self.box, "response.md", id="x-2", ball="consumer",
            status="closed — all three answers taken", responded="2026-07-28")
        self.assertEqual(self.scan(), [])

    def test_prose_containing_a_terminal_word_does_not_close_it(self):
        """The first-word rule is deliberate: `open — not closed until you
        confirm` must stay open. A substring or startswith test would close it."""
        _fm(self.box, "brief.md", id="x-3", ball="me",
            status="open — not closed until you confirm",
            respond_by="2026-07-01", filed="2026-07-01")
        self.assertEqual([t["id"] for t in self.scan()], ["x-3"])

    def test_punctuation_glued_to_the_state_word_is_still_the_state(self):
        _fm(self.box, "brief.md", id="x-4", ball="provider",
            status="filed", respond_by="2026-07-01", filed="2026-07-01")
        _fm(self.box, "response.md", id="x-4", ball="none",
            status="shipped—see PR #12", responded="2026-07-28")
        self.assertEqual(self.scan(), [])

    def test_overdue_only_when_ball_is_ours(self):
        """A respond-by binds whoever HOLDS the ball. Once we answer and it
        moves, that date is satisfied — not breached. Without this guard every
        answered thread in the fleet reported overdue forever."""
        _fm(self.box, "brief.md", id="x-2", ball="provider",
            status="filed", respond_by="2026-07-01", filed="2026-07-01")
        _fm(self.box, "response.md", id="x-2", ball="consumer",
            status="responded", responded="2026-07-05")
        (row,) = self.scan()
        self.assertFalse(row["ours"])
        self.assertIsNone(row["days_overdue"])

    def test_overdue_when_ball_is_ours(self):
        _fm(self.box, "brief.md", id="x-3", ball="provider",
            status="filed", respond_by="2026-07-24", filed="2026-07-01")
        (row,) = self.scan()
        self.assertTrue(row["ours"])
        self.assertEqual(row["days_overdue"], 16)

    def test_informational_note_does_not_mask_a_live_ask(self):
        """FOUNDATIONS filed an informational note (ball: none) 34 seconds
        after a real proposal (ball: provider). Latest-file-wins let the note
        hide the ask. Only files that ASSERT a ball may determine who holds it."""
        prop = _fm(self.box, "proposal.md", id="x-4", ball="provider",
                   status="proposed", filed="2026-08-09")
        note = _fm(self.box, "note.md", id="x-4", ball="none",
                   status="informational", filed="2026-08-09")
        os.utime(prop, (1, 1_000_000))
        os.utime(note, (1, 2_000_000))          # note is strictly newer
        (row,) = self.scan()
        self.assertTrue(row["ours"], "the ball: none note must not mask the ask")
        self.assertEqual(row["status"], "proposed")

    def test_same_day_mtime_breaks_the_tie(self):
        """Exchange dates have DAY resolution and a live channel turns around
        inside a day; filename order is not a substitute for sequence."""
        resp = _fm(self.box, "response.md", id="x-5", ball="consumer",
                   status="responded", responded="2026-08-09")
        prop = _fm(self.box, "proposal.md", id="x-5", ball="provider",
                   status="proposed", filed="2026-08-09")
        os.utime(resp, (1, 1_000_000))
        os.utime(prop, (1, 2_000_000))          # proposal filed AFTER the response
        (row,) = self.scan()
        self.assertTrue(row["ours"])

    def test_all_none_balls_is_not_an_obligation(self):
        _fm(self.box, "note.md", id="x-6", ball="none", status="informational",
            filed="2026-08-09")
        self.assertEqual(self.scan(), [])

    def test_malformed_respond_by_is_not_an_obligation(self):
        _fm(self.box, "brief.md", id="x-7", ball="provider", status="filed",
            respond_by="soon", filed="2026-07-01")
        (row,) = self.scan()
        self.assertIsNone(row["days_overdue"])

    def test_non_exchange_markdown_ignored(self):
        _fm(self.box, "README.md", title="not an exchange", status="filed")
        self.assertEqual(self.scan(), [])


class TestBallOwnership(unittest.TestCase):
    def test_provider_and_own_name_are_ours(self):
        self.assertTrue(ball_scan._ball_is_ours("provider", "autonomous"))
        self.assertTrue(ball_scan._ball_is_ours("audiology", "audiology"))
        self.assertTrue(ball_scan._ball_is_ours("orrery", "synthetic-worlds/Orrery"))

    def test_unknown_value_is_not_claimed(self):
        """Under-claiming is safe; silently absorbing another project's
        obligation is not."""
        self.assertFalse(ball_scan._ball_is_ours("consumer", "autonomous"))
        self.assertFalse(ball_scan._ball_is_ours("someone-else", "autonomous"))
        self.assertFalse(ball_scan._ball_is_ours("none", "autonomous"))
        self.assertFalse(ball_scan._ball_is_ours("", "autonomous"))


class TestAnnotatedBallValues(unittest.TestCase):
    """Real mailboxes annotate the field: `ball: consumer (ratify B23 locally)`,
    `ball: none (F2 opens on their schedule)`. Whole-string matching made every
    annotated value unrecognized — and for `provider (...)` that is an
    obligation ON US reported as not ours, a false negative in the one check
    whose job is not losing work."""

    def test_bare_tokens_still_work(self):
        self.assertTrue(ball_scan._ball_is_ours("provider", "autonomous"))
        self.assertFalse(ball_scan._ball_is_ours("consumer", "autonomous"))

    def test_annotated_provider_is_still_ours(self):
        self.assertTrue(ball_scan._ball_is_ours(
            "provider (please review the fixtures)", "autonomous"))

    def test_annotated_none_is_not_a_claim(self):
        self.assertFalse(ball_scan._ball_is_ours(
            "none (F2 opens on FOUNDATIONS' schedule; nothing owed)", "autonomous"))

    def test_annotated_repo_name_is_ours(self):
        self.assertTrue(ball_scan._ball_is_ours(
            "FOUNDATIONS (the deliverable is a linkable core)",
            "synthetic-worlds/FOUNDATIONS"))

    def test_annotated_none_does_not_mask_a_live_ask(self):
        """The claimant filter must strip the same way, or `none (...)` counts
        as a claim and can win the recency tiebreak over a real one."""
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp, True)
        box = os.path.join(tmp, "integrations", "peer")
        ask = _fm(box, "proposal.md", id="y-1", ball="provider",
                  status="proposed", filed="2026-08-09")
        note = _fm(box, "note.md", id="y-1", ball="none (nothing owed either way)",
                   status="informational", filed="2026-08-09")
        os.utime(ask, (1, 1_000_000))
        os.utime(note, (1, 2_000_000))
        (row,) = ball_scan.scan_repo(tmp, "me", TODAY)
        self.assertTrue(row["ours"])


if __name__ == "__main__":
    unittest.main()


class TestResponsesAwaiting(unittest.TestCase):
    """The delivery gap (Decision 53/54): a response lands in the PROVIDER's
    tree, so a consumer reading only its own mailbox cannot tell an answered
    brief from an ignored one. distillery filed against a stale premise for
    five days because of this."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.me = os.path.join(self.tmp, "distillery")
        self.them = os.path.join(self.tmp, "autonomous")
        os.makedirs(self.me)
        os.makedirs(self.them)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _paths(self):
        return [self.me, self.them]

    def test_response_in_provider_tree_is_surfaced_to_the_consumer(self):
        box = os.path.join(self.them, "integrations", "distillery")
        _fm(box, "brief.md", id="d-1", ball="provider", status="filed",
            filed="2026-08-01")
        _fm(box, "response.md", id="d-1", ball="consumer", status="responded",
            responded="2026-08-10")
        got = ball_scan.responses_awaiting("distillery", self._paths(), TODAY)
        self.assertEqual([(g["id"], g["in_repo"]) for g in got],
                         [("d-1", "autonomous")])

    def test_thread_still_on_the_provider_is_not_ours(self):
        """Un-answered means THEY owe US. It must not appear as our obligation
        — over-claiming here would put another repo's work on our list."""
        box = os.path.join(self.them, "integrations", "distillery")
        _fm(box, "brief.md", id="d-2", ball="provider", status="filed",
            filed="2026-08-01")
        self.assertEqual(ball_scan.responses_awaiting("distillery", self._paths(), TODAY), [])

    def test_closed_thread_is_not_surfaced(self):
        box = os.path.join(self.them, "integrations", "distillery")
        _fm(box, "brief.md", id="d-3", ball="provider", status="filed", filed="2026-08-01")
        _fm(box, "response.md", id="d-3", ball="consumer", status="responded",
            responded="2026-08-10")
        _fm(box, "ratify.md", id="d-3", ball="none", status="closed",
            ratified="2026-08-11")
        self.assertEqual(ball_scan.responses_awaiting("distillery", self._paths(), TODAY), [])

    def test_other_repos_channels_are_ignored(self):
        """THE SCOPE RULE. A channel between two OTHER repos must never appear
        — agents in several projects warned the human about one brief in a
        repo none of them could touch (2026-08-17)."""
        box = os.path.join(self.them, "integrations", "hypersaw")
        _fm(box, "brief.md", id="h-1", ball="provider", status="filed", filed="2026-08-01")
        _fm(box, "response.md", id="h-1", ball="consumer", status="responded",
            responded="2026-08-10")
        self.assertEqual(ball_scan.responses_awaiting("distillery", self._paths(), TODAY), [])

    def test_our_own_mailbox_is_not_double_reported(self):
        """scan_repo already covers it; counting it twice inflates the list."""
        box = os.path.join(self.me, "integrations", "peer")
        _fm(box, "brief.md", id="d-4", ball="provider", status="filed", filed="2026-08-01")
        self.assertEqual(ball_scan.responses_awaiting("distillery", self._paths(), TODAY), [])


class TestFrontmatterLies(unittest.TestCase):
    """A sweep fixes instances; a gate fixes the class. The manual sweep that
    closed this bug caught 21 of 23 — and one miss was HYPERSAW's own brief, on
    the very thread reporting the bug (hypersaw-001 round 2)."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.box = os.path.join(self.tmp, "integrations", "peer")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_opening_brief_left_claiming_the_ball_is_flagged(self):
        b = _fm(self.box, "brief.md", id="z-1", ball="provider", status="filed",
                filed="2026-08-01")
        r = _fm(self.box, "response.md", id="z-1", ball="consumer",
                status="responded", responded="2026-08-10")
        os.utime(b, (1, 1_000_000)); os.utime(r, (1, 2_000_000))
        got = ball_scan.frontmatter_lies(self.tmp)
        self.assertEqual([g["file"] for g in got], ["integrations/peer/brief.md"])

    def test_a_live_hand_back_is_NOT_flagged(self):
        """THE FALSE-POSITIVE GUARD. A thread bounces: the consumer ratifies and
        hands the ball back with a new ask. That provider-ball is current, not
        stale. Flagging it would report a live obligation as a lie and get the
        gate switched off."""
        b = _fm(self.box, "brief.md", id="z-2", ball="provider", status="filed",
                filed="2026-08-01")
        r = _fm(self.box, "response.md", id="z-2", ball="consumer",
                status="responded", responded="2026-08-10")
        h = _fm(self.box, "ratification.md", id="z-2", ball="provider",
                status="refined", filed="2026-08-18")
        os.utime(b, (1, 1_000_000)); os.utime(r, (1, 2_000_000)); os.utime(h, (1, 3_000_000))
        got = [g["file"] for g in ball_scan.frontmatter_lies(self.tmp)]
        self.assertIn("integrations/peer/brief.md", got)
        self.assertNotIn("integrations/peer/ratification.md", got)

    def test_unanswered_thread_is_clean(self):
        _fm(self.box, "brief.md", id="z-3", ball="provider", status="filed",
            filed="2026-08-01")
        self.assertEqual(ball_scan.frontmatter_lies(self.tmp), [])

    def test_answered_by_pointing_at_a_missing_file_is_not_proof(self):
        """Assert the EFFECTIVE state: the answer must exist on disk, not merely
        be claimed by a field."""
        _fm(self.box, "brief.md", id="z-4", ball="provider", status="filed",
            filed="2026-08-01", answered_by="nope.md")
        self.assertEqual(ball_scan.frontmatter_lies(self.tmp), [])


class CitesMissing(unittest.TestCase):
    """INTEGRATIONS: the resident affirms cites: at intake. A gate that cannot
    fire reads exactly like one that passes (L0002), so the planted-bad case
    comes first."""
    def setUp(self):
        import tempfile
        self.tmp = tempfile.mkdtemp()
        self.box = os.path.join(self.tmp, "integrations", "peer")
        os.makedirs(self.box)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _w(self, name, fm):
        with open(os.path.join(self.box, name), "w") as fh:
            fh.write("---\n" + fm + "\n---\nbody\n")

    def test_triaged_thread_without_cites_fires(self):
        self._w("brief-001.md", "id: peer-001\nstatus: responded\nball: consumer")
        self.assertEqual([b["id"] for b in ball_scan.cites_missing(self.tmp)], ["peer-001"])

    def test_untriaged_brief_is_not_yet_a_duty(self):
        self._w("brief-002.md", "id: peer-002\nstatus: filed\nball: provider")
        self.assertEqual(ball_scan.cites_missing(self.tmp), [])

    def test_cites_none_satisfies_the_gate_by_design(self):
        self._w("brief-003.md", "id: peer-003\nstatus: responded\nball: consumer\ncites: none")
        self.assertEqual(ball_scan.cites_missing(self.tmp), [])

    def test_filed_with_prose_is_still_untriaged(self):
        """Same first-word rule on the intake side: `filed — awaiting triage`
        is filed, so no cites: duty has fallen due yet."""
        self._w("brief-005.md", "id: peer-005\nstatus: filed — awaiting triage\nball: provider")
        self.assertEqual(ball_scan.cites_missing(self.tmp), [])

    def test_answers_are_not_intake(self):
        self._w("response-004.md", "id: peer-004\nstatus: responded\nball: consumer")
        self.assertEqual(ball_scan.cites_missing(self.tmp), [])


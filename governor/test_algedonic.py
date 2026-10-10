"""The landing check's decision (horde brief hypersaw-010): a PR GitHub shows as
merged counts as landed only if its merge commit is on the default branch."""
import datetime
import unittest

import algedonic

NOW = datetime.datetime(2026, 10, 10, 12, 0, 0)


def pr(num, base, when="2026-10-09T10:00:00Z", oid="c0ffee", head=None):
    return {"number": num, "baseRefName": base, "mergedAt": when, "headRefOid": head,
            "mergeCommit": {"oid": oid} if oid else None}


class TestUnlanded(unittest.TestCase):
    def _run(self, prs, statuses=None):
        asked = []

        def status_of(oid):
            asked.append(oid)
            return (statuses or {}).get(oid, "ahead")
        return algedonic.unlanded(prs, "main", status_of, NOW), asked

    def test_merge_into_default_is_landed_and_costs_no_call(self):
        got, asked = self._run([pr(1, "main")])
        self.assertEqual((got, asked), ({}, []))

    def test_stacked_pr_whose_base_already_merged_is_reported(self):
        # horde's race: #2 merged into branch `stack`, which had already merged.
        got, _ = self._run([pr(2, "stack", oid="aaa")], {"aaa": "ahead"})
        self.assertEqual(got, {"stack": [2]})

    def test_stacked_pr_whose_base_later_reached_default_is_landed(self):
        for st in ("behind", "identical"):
            got, _ = self._run([pr(3, "stack", oid="bbb")], {"bbb": st})
            self.assertEqual(got, {}, st)

    def test_diverged_and_missing_commit_are_not_landed(self):
        got, _ = self._run([pr(4, "stack", oid="d"), pr(6, "stack", oid=None)], {"d": "diverged"})
        self.assertEqual(got, {"stack": [4, 6]})

    def test_a_compare_that_cannot_be_asked_is_unknown_not_unlanded(self):
        # Review, 2026-10-10: a rate-limited compare was printed as PAIN.
        def boom(_oid):
            raise RuntimeError("rate limited")
        with self.assertRaises(RuntimeError):
            algedonic.unlanded([pr(5, "stack", oid="u")], "main", boom, NOW)

    def test_adapter_turns_any_gh_failure_into_none(self):
        real = algedonic._gh
        try:
            def fail(*_a):
                raise RuntimeError("gh pr list… timed out")
            algedonic._gh = fail
            self.assertIsNone(algedonic.unlanded_merges("x", "main"))
        finally:
            algedonic._gh = real

    def test_outside_the_window_is_not_reported(self):
        got, asked = self._run([pr(7, "stack", when="2026-09-01T00:00:00Z")])
        self.assertEqual((got, asked), ({}, []))

    def test_unreadable_merge_date_is_skipped_not_fatal(self):
        got, _ = self._run([{"number": 8, "baseRefName": "stack"}])
        self.assertEqual(got, {})

    def test_head_carried_by_a_later_catch_up_is_landed(self):
        # bulwark #9-11, live 2026-10-10: the merge commit never reached main,
        # the head did (a catch-up PR merged the branches). Landed.
        got, _ = self._run([pr(9, "m1", oid="m", head="h")], {"m": "diverged", "h": "behind"})
        self.assertEqual(got, {})

    def test_many_prs_into_one_branch_are_one_group(self):
        got, _ = self._run([pr(n, "main2", oid=f"o{n}") for n in (3, 1, 2)])
        self.assertEqual(got, {"main2": [1, 2, 3]})


if __name__ == "__main__":
    unittest.main()

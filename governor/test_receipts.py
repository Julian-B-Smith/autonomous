import unittest

import receipts


def rec(gates, exit=0, **kw):
    return dict({"target": "fast", "exit": exit, "gates": gates}, **kw)


class TestFindings(unittest.TestCase):
    def test_all_ran_is_silent(self):
        self.assertEqual(receipts.findings(rec([{"name": "a", "result": "ran", "cases": 5}])), [])

    def test_skip_is_named_with_its_reason(self):
        f = receipts.findings(rec([{"name": "san", "result": "skipped", "reason": "no compiler"}]))
        self.assertEqual(f, ["san: skipped (no compiler)"])

    def test_zero_cases_is_the_empty_corpus(self):
        f = receipts.findings(rec([{"name": "parity", "result": "ran", "cases": 0}]))
        self.assertEqual(f, ["parity: ran and judged 0 cases"])

    def test_tree_that_changed_while_verify_ran(self):
        f = receipts.findings(rec([{"name": "a", "result": "ran"}], tree="b" * 40, tree_start="a" * 40))
        self.assertEqual(len(f), 1)
        self.assertIn("changed WHILE verify ran", f[0])
        same = rec([{"name": "a", "result": "ran"}], tree="a" * 40, tree_start="a" * 40)
        self.assertEqual(receipts.findings(same), [])
        unknown = rec([{"name": "a", "result": "ran"}], tree="a" * 40, tree_start="")
        self.assertEqual(receipts.findings(unknown), [])       # unwrapped verify: nothing to compare

    def test_red_or_missing_record_is_not_judged_here(self):
        self.assertEqual(receipts.findings(rec([{"name": "a", "result": "skipped"}], exit=1)), [])
        self.assertEqual(receipts.findings(None), [])

    def test_pre_2_9_record_without_gates_is_silent(self):
        self.assertEqual(receipts.findings({"target": "fast", "exit": 0}), [])


if __name__ == "__main__":
    unittest.main()

"""The plan map's checks, each with its must-fail control (Decision 97; horde
brief hypersaw-016's proposed contract tests, adapted to kit.plan/0).

A scratch repo holds a ROADMAP, a DECISIONS file and a small plan. The good
plan must be green on every check; each control breaks ONE thing and must turn
exactly the check it targets red."""
import copy, json, os, shutil, subprocess, sys, tempfile, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import plan as P  # noqa: E402

ROADMAP = """# R

## Parallel track — Kit v2

- **Phase X — Exploration.** text
- **K0 — Kit version.** text
- **K1 — Retrofit.** text
- **A0 — Actions.** text
- **A. S4 freshness** text
"""
DECISIONS = "# D\n\n2. **Second.**\n1. **First.**\n"
GOOD = {
    "format": "kit.plan/0", "title": "t", "targets": ["k1"],
    "verified": {"date": "2026-10-17", "roadmap_commit": "HEAD", "decisions_max": 2},
    "parts": [
        {"id": "k0", "title": "Kit version", "status": "closed", "what": "w", "rows": ["K0"], "adrs": [1],
         "basis": ["D1"], "code": ["src/a.txt"]},
        {"id": "kv2", "title": "Kit v2", "status": "in progress", "what": "w",
         "rows": ["Parallel track — Kit v2"], "basis": ["R:Parallel track — Kit v2"]},
        {"id": "x", "title": "Explore", "status": "planned", "what": "w", "rows": ["X"]},
        {"id": "k1", "title": "Retrofit", "status": "ruled", "what": "w", "rows": ["K1"], "adrs": [2],
         "basis": ["D2"], "needs": ["k0", "kv2"], "needs_inferred": ["x"]},
    ]}
QUEUE = {"format": "kit.queue/0", "items": [
    {"id": "q1", "question": "?", "raised": "2026-10-17", "recommendation": "yes", "blocks": ["k1"], "lands_in": "DECISIONS"}]}


class Repo:
    def __init__(self, plan=GOOD, queue=QUEUE, commit=True):
        self.root = os.path.realpath(tempfile.mkdtemp(prefix="plan-"))
        self.d = os.path.join(self.root, "plan")
        os.makedirs(self.d); os.makedirs(os.path.join(self.root, "src"))
        for rel, body in (("ROADMAP.md", ROADMAP), ("DECISIONS.md", DECISIONS), ("src/a.txt", "a\n")):
            open(os.path.join(self.root, rel), "w").write(body)
        self.write(plan, queue)
        subprocess.run(["git", "init", "-q", self.root], check=True)
        if commit:
            self.commit()

    def write(self, plan, queue=QUEUE):
        with open(os.path.join(self.d, "parts.json"), "w") as fh:
            json.dump(plan, fh)
        with open(os.path.join(self.d, "queue.json"), "w") as fh:
            json.dump(queue, fh)
        P.build(self.d)

    def commit(self):
        subprocess.run(["git", "-C", self.root, "add", "-A"], check=True)
        subprocess.run(["git", "-C", self.root, "-c", "user.email=t@example.invalid", "-c", "user.name=t",
                        "commit", "-q", "-m", "plan"], check=True)

    def red(self):
        return [n for n, ok, _ in P.check(self.d) if not ok]

    def close(self):
        shutil.rmtree(self.root, ignore_errors=True)


def mutate(f):
    plan = copy.deepcopy(GOOD)
    f(plan)
    return plan


class TestChecks(unittest.TestCase):
    def setUp(self):
        self.r = Repo()

    def tearDown(self):
        self.r.close()

    def test_good_plan_is_green(self):
        self.assertEqual(self.r.red(), [])

    def control(self, want, plan=None, queue=QUEUE):
        self.r.write(plan if plan is not None else GOOD, queue)
        self.assertEqual(self.r.red(), want)

    def test_1_a_row_that_does_not_exist(self):
        self.control([1], mutate(lambda p: p["parts"][0]["rows"].append("K9")))

    def test_1_a_decision_that_does_not_exist(self):
        self.control([1], mutate(lambda p: p["parts"][0]["adrs"].append(7)))

    def test_1_a_basis_file_that_does_not_exist(self):
        self.control([1], mutate(lambda p: p["parts"][0]["basis"].append("file:nope.txt")))

    def test_2_a_cycle(self):
        self.control([2], mutate(lambda p: p["parts"][0].setdefault("needs", []).append("k1")))

    def test_3_a_status_outside_the_vocabulary(self):
        # With a basis, so that only the vocabulary is wrong.
        self.control([3], mutate(lambda p: p["parts"][2].update(status="done-ish", basis=["D1"])))

    def test_3_an_edge_to_a_part_that_does_not_exist(self):
        self.control([3], mutate(lambda p: p["parts"][3]["needs"].append("nope")))

    def test_4_a_hand_edited_generated_table(self):
        path = os.path.join(self.r.d, "PLAN.md")
        open(path, "a").write("| `k9` hand-added | closed |\n")
        self.assertEqual(self.r.red(), [4])

    def test_4_a_hand_edited_map(self):
        path = os.path.join(self.r.d, "plan-map.html")
        s = open(path).read()
        open(path, "w").write(s.replace('"status": "ruled"', '"status": "closed"', 1))
        self.assertEqual(self.r.red(), [4])

    def test_5_a_status_change_with_no_new_record(self):
        # brief lesson 2: an agent "closed" a decision on its own reading.
        self.control([5], mutate(lambda p: p["parts"][3].update(status="closed")))

    def test_5_the_same_change_with_a_new_record_is_green(self):
        self.control([], mutate(lambda p: p["parts"][3].update(status="closed", basis=["D2", "D1"])))

    def test_5_a_non_planned_status_that_cites_nothing(self):
        self.control([5], mutate(lambda p: p["parts"][2].update(status="ruled")))

    def test_6_a_code_path_that_matches_no_file(self):
        self.control([6], mutate(lambda p: p["parts"][0]["code"].append("src/gone")))

    def test_7_a_queue_item_blocking_an_unknown_part(self):
        q = copy.deepcopy(QUEUE); q["items"][0]["blocks"] = ["nope"]
        self.control([7], queue=q)

    def test_7_a_queue_item_without_a_recommendation(self):
        q = copy.deepcopy(QUEUE); del q["items"][0]["recommendation"]
        self.control([7], queue=q)


class TestComputed(unittest.TestCase):
    def test_critical_path_uses_cited_edges_and_lists_ties(self):
        # k1 needs k0 (closed: not counted) and kv2 (cited); x is inferred and
        # must not decide the path.
        ln, chains = P.critical_paths(GOOD)["k1"]
        self.assertEqual((ln, chains), (2, [["kv2", "k1"]]))
        tied = mutate(lambda p: p["parts"][3]["needs"].append("x"))
        ln, chains = P.critical_paths(tied)["k1"]
        self.assertEqual((ln, sorted(chains)), (2, [["kv2", "k1"], ["x", "k1"]]))

    def test_a_part_further_along_than_its_prerequisite_is_reported(self):
        plan = mutate(lambda p: p["parts"][3].update(status="built"))
        self.assertEqual(len(P.ahead_of_prerequisites(plan)), 1)
        self.assertEqual(P.ahead_of_prerequisites(GOOD), [])

    def test_row_citations(self):
        self.assertTrue(P.row_exists(ROADMAP, "Parallel track — Kit v2"))   # a heading
        self.assertTrue(P.row_exists(ROADMAP, "X"))                         # **Phase X —
        self.assertTrue(P.row_exists(ROADMAP, "A. S4 freshness"))
        self.assertTrue(P.row_exists(ROADMAP, "A"))                         # **A. is a label
        self.assertFalse(P.row_exists("- **A0 — Actions.**", "A"))          # but not **A0
        self.assertFalse(P.row_exists(ROADMAP, "K"))

    def test_build_is_deterministic(self):
        r = Repo(commit=False)
        try:
            first = open(os.path.join(r.d, "plan-map.html")).read() + open(os.path.join(r.d, "PLAN.md")).read()
            P.build(r.d)
            again = open(os.path.join(r.d, "plan-map.html")).read() + open(os.path.join(r.d, "PLAN.md")).read()
            self.assertEqual(first, again)
        finally:
            r.close()

    def test_this_repos_own_plan_is_green(self):
        # autonomous is the module's first instance; its plan is held to the
        # same checks as any repo's.
        res = P.check(os.path.join(HERE, "..", "..", "plan"))
        self.assertEqual([m for _, ok, m in res if not ok], [])


if __name__ == "__main__":
    unittest.main()

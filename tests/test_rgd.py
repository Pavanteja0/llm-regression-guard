import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from rgd.compare import compare
from rgd.evalrun import accuracy, load, run_eval
from rgd.model import RuleModel
from rgd.report import render_html

ROOT = os.path.dirname(os.path.dirname(__file__))


def run(name):
    return run_eval(RuleModel(load(os.path.join(ROOT, "prompts", name))), load(os.path.join(ROOT, "data", "golden.json")))


class T(unittest.TestCase):
    def test_golden_size(self):
        self.assertEqual(len(load(os.path.join(ROOT, "data", "golden.json"))["cases"]), 38)

    def test_same_prompt_is_ok(self):
        d = compare(run("v1.json"), run("v1.json"))
        self.assertEqual(d["status"], "ok")
        self.assertEqual(d["regressions"], [])

    def test_bad_prompt_is_flagged(self):
        d = compare(run("v1.json"), run("v2_bad.json"))
        self.assertEqual(d["status"], "critical")
        self.assertTrue(d["regressions"])

    def test_good_prompt_improves(self):
        d = compare(run("v1.json"), run("v2_good.json"))
        self.assertGreater(d["delta"], 0)
        self.assertEqual(d["status"], "ok")

    def test_thresholds_configurable(self):
        base, new = run("v1.json"), run("v2_bad.json")
        d = compare(base, new, warn=0.5, crit=0.9)
        self.assertEqual(d["status"], "ok")

    def test_flips_are_listed(self):
        base = [{"id": "a", "pass": True, "expected": "x"}, {"id": "b", "pass": False, "expected": "x"}]
        new = [{"id": "a", "pass": False, "expected": "x"}, {"id": "b", "pass": True, "expected": "x"}]
        d = compare(base, new)
        self.assertEqual(d["regressions"], ["a"])
        self.assertEqual(d["improvements"], ["b"])

    def test_html_escapes(self):
        d = compare(run("v1.json"), run("v1.json"))
        self.assertNotIn("<script>", render_html(d, "<script>", "v2"))


if __name__ == "__main__":
    unittest.main()

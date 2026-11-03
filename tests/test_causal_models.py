# Copyright (C) 2026 KARMENLOOP Official Team
# SPDX-License-Identifier: AGPL-3.0-only
import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import causal_models as causal


def graph(a="state", b="decision"):
    return {"variables": {a: "context", b: "outcome"},
            "relations": [{"from": a, "to": b, "relation": "conditions"}],
            "predictions": [{"intervention": "Change the context", "expected": "Recheck the dependent decision",
                             "falsifier": "The decision is independent of this context"}]}


def mapping():
    return {"variables": {"state": "conditions", "decision": "recommendation"},
            "rationale": "The target decision also depends on changing context",
            "prediction": "Changing context invalidates old support",
            "falsifier": "The unchanged conclusion has independent support"}


class CausalTests(unittest.TestCase):
    def test_renamed_variables_can_match_without_shared_words(self):
        result = causal.match(graph(), graph("conditions", "recommendation"), mapping())
        self.assertTrue(result["compatible"])
        self.assertEqual(result["status"], "structurally_compatible")

    def test_reversed_relation_rejects_superficially_similar_analogy(self):
        target = graph("conditions", "recommendation")
        target["relations"][0].update({"from": "recommendation", "to": "conditions"})
        result = causal.match(graph(), target, mapping())
        self.assertFalse(result["compatible"])
        self.assertIn("directed_relations_not_preserved", result["issues"])

    def test_role_difference_needs_revised_hypothesis(self):
        target = graph("conditions", "recommendation")
        target["variables"]["conditions"] = "outcome"
        self.assertIn("variable_roles_differ", causal.match(graph(), target, mapping())["issues"])

    def test_mapping_cannot_merge_cause_and_effect(self):
        item = mapping()
        item["variables"]["decision"] = "conditions"
        self.assertIn("mapping_merges_distinct_variables", causal.match(graph(), graph("conditions", "recommendation"), item)["issues"])

    def test_missing_source_or_target_variable_is_visible(self):
        for variables, expected in [({"state": "conditions"}, "source_variables_not_exactly_covered"),
                                    ({"state": "absent", "decision": "recommendation"}, "target_variable_missing")]:
            item = mapping(); item["variables"] = variables
            self.assertIn(expected, causal.match(graph(), graph("conditions", "recommendation"), item)["issues"])

    def test_declared_model_without_mapping_cannot_probe(self):
        self.assertEqual(causal.match(graph(), None, None)["status"], "mapping_required")

    def test_legacy_experience_remains_compatible(self):
        self.assertIsNone(causal.match(None, graph(), None)["compatible"])

    def test_explicit_mapping_requires_a_source_model(self):
        result = causal.match(None, graph("conditions", "recommendation"), mapping())
        self.assertFalse(result["compatible"])
        self.assertIn("source_causal_model_missing", result["issues"])

    def test_duplicate_and_dangling_edges_rejected(self):
        for change in (lambda g: g["relations"].append(copy.deepcopy(g["relations"][0])),
                       lambda g: g["relations"][0].update({"to": "missing"})):
            item = graph(); change(item)
            with self.assertRaises(ValueError): causal.graph_check(item)

    def test_prediction_requires_observable_falsifier(self):
        item = graph(); item["predictions"][0]["falsifier"] = ""
        with self.assertRaises(ValueError): causal.graph_check(item)


if __name__ == "__main__":
    unittest.main()

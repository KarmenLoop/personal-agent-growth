#!/usr/bin/env python3
# Copyright (C) 2026 KARMENLOOP Official Team
# SPDX-License-Identifier: AGPL-3.0-only
"""Check host-proposed causal analogies; structural agreement is not causal proof."""
import unicodedata

import capability_ledger as store


def label(value):
    store.text(value, "relation or role", 200)
    return " ".join(unicodedata.normalize("NFKC", value).casefold().split())


def fields(item, names):
    store.require(isinstance(item, dict) and set(item) == set(names), "Invalid causal fields")


def graph_check(graph):
    fields(graph, ("variables", "relations", "predictions"))
    variables = graph["variables"]
    store.require(isinstance(variables, dict) and 1 <= len(variables) <= 32, "Invalid causal variables")
    for key, role in variables.items():
        store.identifier(key)
        label(role)
    relations = graph["relations"]
    store.require(isinstance(relations, list) and 1 <= len(relations) <= 64, "Invalid causal relations")
    edges = set()
    for edge in relations:
        fields(edge, ("from", "to", "relation"))
        store.identifier(edge["from"]); store.identifier(edge["to"])
        store.require(edge["from"] in variables and edge["to"] in variables,
                      "Causal relation names a missing variable")
        key = (edge["from"], edge["to"], label(edge["relation"]))
        store.require(key not in edges, "Duplicate causal relation")
        edges.add(key)
    predictions = graph["predictions"]
    store.require(isinstance(predictions, list) and 1 <= len(predictions) <= 8,
                  "Testable causal predictions required")
    for prediction in predictions:
        fields(prediction, ("intervention", "expected", "falsifier"))
        for value in prediction.values():
            store.text(value, "causal prediction", 1000)
    return edges


def mappings_check(mappings, target):
    store.require(isinstance(mappings, dict) and 1 <= len(mappings) <= 50,
                  "Invalid causal mappings")
    store.require(target is not None, "Causal mappings need a target graph")
    for experience_id, mapping in mappings.items():
        store.identifier(experience_id)
        fields(mapping, ("variables", "rationale", "prediction", "falsifier"))
        store.require(isinstance(mapping["variables"], dict) and
                      1 <= len(mapping["variables"]) <= 32, "Invalid variable mapping")
        for source, destination in mapping["variables"].items():
            store.identifier(source)
            store.identifier(destination)
        for key in ("rationale", "prediction", "falsifier"):
            store.text(mapping[key], key, 2000)


def match(source, target, mapping):
    """Report failed conditions instead of silently falling back to matching words."""
    if source is None:
        if mapping is not None:
            return {"status": "incompatible", "compatible": False,
                    "issues": ["source_causal_model_missing"],
                    "scope": "An explicit analogy cannot be validated against a source without a causal graph"}
        return {"status": "legacy_labels", "compatible": None, "issues": [],
                "scope": "No source causal graph; legacy heuristic only"}
    source_edges = graph_check(source)
    if target is None or mapping is None:
        return {"status": "mapping_required", "compatible": False,
                "issues": ["target_graph_or_mapping_missing"],
                "scope": "A source model needs an explicit target analogy before probing"}
    target_edges = graph_check(target)
    mappings_check({"mapping": mapping}, target)
    variables = mapping["variables"]
    issues = []
    if set(variables) != set(source["variables"]):
        issues.append("source_variables_not_exactly_covered")
    if len(set(variables.values())) != len(variables):
        issues.append("mapping_merges_distinct_variables")
    if any(v not in target["variables"] for v in variables.values()):
        issues.append("target_variable_missing")
    if not issues:
        if any(label(source["variables"][s]) != label(target["variables"][t])
               for s, t in variables.items()):
            issues.append("variable_roles_differ")
        missing = sorted((variables[a], variables[b], relation)
                         for a, b, relation in source_edges
                         if (variables[a], variables[b], relation) not in target_edges)
        if missing:
            issues.append("directed_relations_not_preserved")
    else:
        missing = []
    return {"status": "structurally_compatible" if not issues else "incompatible",
            "compatible": not issues, "issues": issues, "missing_relations": missing,
            "mapping": mapping, "source_predictions": source["predictions"],
            "scope": "Host-declared roles and directed relations agree; conditions, causality and usefulness still need actual tests"}

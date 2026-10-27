---
id: exp-regression-repair-20261027-en
type: experience
project: koder-markdown-learning
tags: [domain/software, workflow/regression, workflow/packaging]
status: active
created: 2026-10-27
updated: 2026-10-27
sources: [https://github.com/KarmenLoop/personal-agent-growth/blob/v0.4.3/docs/evidence/koder-skip-audit-20261027.json, https://github.com/KarmenLoop/personal-agent-growth/blob/v0.4.2/docs/evidence/koder-regression-repair-20261027.json, https://github.com/KarmenLoop/personal-agent-growth/blob/v0.4.2/docs/release-0.4.2-acceptance.en.md]
---
# Repair inherited failures without changing the goal · 0.4.3

[中文](regression-repair.md)

## Scenario

A new learning subsystem passes its focused tests, while the product suite has failures also present in its baseline. A user requests all failures fixed. The baseline comparison remains useful evidence of origin; the requested completion criterion now includes the inherited failures.

## Method

Preserve the old result. For each failing or cancelled test, record its name, reached stage, input/source identity, environment, cause hypothesis, smallest distinguishing check, repair, and fresh result. Split a root failure from the tests cancelled behind it. Keep one immutable receipt per attempt, including unsuccessful repairs.

Classify a failure before changing anything:

| Evidence | Next action | Required protection |
|---|---|---|
| Real behavior violates the contract | Repair the product and replay the triggering task | Retain negative cases and unrelated regression checks |
| Fixture models the wrong user action or environment | Correct that fixture and explain the mismatch | Do not replace the actual effect with a simulated pass |
| Expected version/content disagrees with intentional shipped behavior | Compare source, current documentation, and actual output | Preserve all substantive content and safety assertions |
| Setup blocks later checks | Repair setup; rerun the cancelled checks | Cancellation is not a pass or a business assertion failure |
| Packaging depends on the developer checkout | Materialize required files and use a fresh isolated extraction | Reject links that still point to the checkout |
| Optional platform/service is unavailable | Inspect the skip condition and supply available prerequisites; otherwise retain a named blocker | Do not count it as accepted or fabricate the missing host |

A test change is acceptable when the product contract already calls for the new behavior and the old test exercised something else. It is not acceptable merely because the new assertion passes. A deadline must remain meaningful. Shared expensive setup may run once per fresh suite, but each destructive test uses its own copy; never reuse an old package to save time.

Check evidence references in both Markdown links and front matter. If a compact package omits a cited document, use its immutable release-tag URL; a repository-relative path that works only in the full checkout is not a usable installed source.

## Why it helps

The Koder repair separated several mechanisms that looked similar in a red summary. Native readline read `process.env.TERM` even with a virtual TTY. A setup test selected a similarly named switch instead of the completion row. Model context budgeting counted internal tool registry fields that the provider never sends. A local archive contained nested directory links, so one extractor could see the old checkout while another omitted those entries. A passing local command did not establish an independently installable package.

These are conditional observations from the recorded macOS/Node environment. They do not justify globally forcing terminals, stripping validation constraints, or trusting a package from another runtime.

## Counterexamples and limits

- Changing a workflow from execution to planning is valid only if the test is actually a planning scenario. Execution tasks retain artifact and test-result gates.
- Compacting tools may omit schema annotations and local registry metadata from the model projection. Tool names, property names, required fields, validation constraints, and execution permissions remain intact in their owning layers.
- Slower end-to-end execution can be the cost of testing the complete package. Compare work and coverage before calling it a performance regression or gain.
- A zero-failure suite with explicit skips does not prove native Windows execution, a paid model interaction, or an absent service integration.
- This repair is an engineering regression result, not a new multi-arm PPC efficiency trial. Do not invent general/domain/composed runs that did not happen.

## Reusable steps

1. Read current context and latest node. Freeze the baseline identities and original failures.
2. Predict a discriminating result, execute it, and retain raw output.
3. Repair the identified mechanism; replay the failing scenario and a meaningful counterexample.
4. Reconcile original test names with the new suite. Account for split files, formerly cancelled cases, and added regressions; do not silently drop a failure.
5. Freeze the final candidate, hash tracked and new source files, build a fresh package, and run the complete configured suite without concurrent edits.
6. Verify source identity stayed unchanged. Report pass/fail/cancel/skip totals and named exclusions separately. If another defect appears, preserve this run and restart the relevant repair loop.
7. Build the public distribution from the accepted public commit; verify its exact bytes after download. A private product patch and a public Skill release have separate ownership and license scopes.
8. Store the applied lesson in Markdown with source links, scope, and the next reuse condition. In the next related task, load it before choosing fixture, budget, or package strategy.

## Audit skipped checks before closing a regression

Use this section when the requested acceptance includes skipped checks. Read each test body as well as its skip predicate. Record its original name, required capability, missing input, authority to supply it, command, reached assertion, result, and remaining scope. Give every original skip an entry even when several share one cause. A prepared script remains `NOT_RUN`; a test-runner skip remains `SKIP` until an actual run reaches its assertions.

1. **Separate policy, setup, and platform.** A provider deliberately held unavailable has a different boundary from an unset Core path or a missing Windows host. Fixing a condition must not silently reverse a product decision.
2. **Identify compatible inputs.** A service that starts is not necessarily the service version required by the tests. Inspect required routes and contracts, hash the selected sources, and install missing dependencies in an owned environment. Record the initial failed setup rather than replacing its receipt.
3. **Keep offline contracts useful.** If a held provider case already uses an offline transport, retain the real adapter, CLI tools, and wire assertions through an existing test seam. First prove the public entry still refuses the provider with zero transport calls. Require an explicit offline transport; never fall through to a live request. Report adapter coverage separately from cloud-provider acceptance.
4. **Verify an apparently stale expectation.** Compare source, current documentation, a counterexample, and actual transport/projection output. In the recorded shared-memory case, task history synchronized correctly but remained scoped to its conversation. The corrected test first proves that isolation, then uses the real explicit-note and sync commands before cross-project reuse. Do not remove a scope filter just to satisfy an old positive assertion.
5. **Exercise platform behavior on that platform.** Four Windows guard tests use stubbed child-process results even when running on Windows. Keep them, and separately invoke the actual ACL helper, independently read back Windows ACLs, verify nonempty-directory refusal without mutation, and run the actual fallback. A platform override, cross-compilation, or a hosted public installer test cannot replace these checks.
6. **Freeze and reconcile.** Run the configured complete suite after focused repairs. Bind source and dependency identities before and after it. Reconcile every original skipped name to a reached result or a concrete blocker. Nested tests becoming discoverable can change the total; explain that arithmetic. Carry unresolved rows into the next checkpoint.

Contact the user only when the missing prerequisite actually requires them, such as restoring a remote connection. Continue independent work while waiting; do not repeat password attempts, ask for secrets, or turn elapsed time into approval. A partial evidence release may document the blocker, but its package checks must not be presented as full product acceptance.

The reusable lesson is to restore the intended observation, not to minimize a skip counter. Load this section before choosing how to enable optional integration or platform coverage. The [21-case audit](../docs/release-0.4.3-acceptance.en.md) records both completed checks and the remaining device boundary.

## Related links

[Fresh acceptance and failure reconciliation](../docs/release-0.4.2-acceptance.en.md) · [Markdown retrieval contract](markdown-learning.en.md) · [Recursive experiments](recursive-improvement.en.md)

# How decisions and learning connect · 0.4.4

[中文](reasoning.zh-CN.md) · [Architecture](architecture.en.md) · [Decision map](diagrams/reasoning.en.svg)

## 1. Start with purpose and consequences

There is no context-free answer to whether something is good. Establish who benefits, the desired outcome, constraints, and consequences of error before choosing criteria. Explaining, predicting, selecting an option, and delivering an artifact require different acceptance tests.

A decision card records the question, user goal, observations, hypotheses, opposing evidence, unknowns, options, quality criteria, cost, choice, next action, expected observation, and revision condition. It records a concise, inspectable rationale and observable actions, not hidden model chain of thought.

## 2. Choose a useful level of decomposition

Expand the object into components, relations, inputs, transformations, outputs, constraints, and failure modes. Continue when a subquestion can distinguish options, explain a failure, or change the next action. Stop when further detail only adds terminology.

For “why does an engine move?”, first identify the engine type. A reciprocating internal-combustion example prompts questions about fuel and air intake, combustion converting chemical energy into heat, expanding gas doing work on a piston, the connecting rod and crankshaft transmitting motion, and exhaust and cooling sustaining the cycle. Each arrow needs a checkable mechanism. This is a questioning example, not a specific engine's engineering specification; electric motors and other engines need different causal graphs.

An explanation can stop when the mechanism is clear enough. A design task must also verify materials, loads, controls, and operating constraints. Purpose determines depth; unlimited decomposition is not the goal.

## 3. Separate evidence, explanation, and value

| Category | Example | Next action |
|---|---|---|
| Observation | Checker exits 2 at read_archive | Preserve the path and raw error |
| Explanation | A moved path may explain it; archive corruption is not established | Inspect actual files and mappings |
| Prediction | Correct location should permit consistency inspection | Record before making the correction |
| Value judgment | Recovery matters before timing optimization | Apply user goals and fixed quality criteria |
| Unknown | A second host has not run the task | Retain NOT_RUN rather than extrapolating |

Resolve source conflicts by date, originality, object, and method, not page count. Reposts and summaries of one original are one source. Public statements can support a sourced hypothesis about a person's working method; reputation, tone, or school background do not establish their internal thoughts.

## 4. Research, experiment, act, or ask

Identify the missing information, which action different answers would change, whether current files/tools can supply it, the smallest discriminating test, and whether its cost is justified. This is a prioritization method, not a license to present subjective scores as measured probabilities.

Verify public facts independently. Test repeatable technical uncertainty at small scale. Act when prerequisites are met. Ask only about user-owned tradeoffs, added authority, or budget decisions. While an answer is pending, continue independent work and retain the dependent branch as unresolved. Initiative means useful options and completed work, not frequent popups.

## 5. Preparation, remediation, and review

| Stage | Purpose | Method | Evidence of value |
|---|---|---|---|
| Preparation | Reduce uncertainty in the next action | Work backward from use, consult primary sources, predict | Later work actually uses the knowledge and changes action |
| Rehearsal | Expose failure cheaply | Isolated copy or read-only variation | A discrepancy changes the production plan |
| Remediation | Repair an observed gap | Preserve failure, distinguish causes, learn or revise | Retest the original task without deleting failure history |
| Review | Test transfer and boundaries | Change path, order, edge condition, or task | Valid cases work, counterexamples fail appropriately |

Unused preparation stays a candidate. Repeating an old answer is not a passed review. A repeated failure reopens the existing issue instead of creating another indistinguishable lesson.

## 6. End-to-end example: reviewing a handoff package

This reconstruction explains mechanisms observed in historical acceptance. See [validation](validation.md) and the [recursive trial](recursive-improvement-trial.md); it is not a new Agent execution in this publication.

1. **Goal:** a recipient can continue checking the package after relocation. Acceptance includes archive consistency, readable resources, and operation after moving.
2. **Initial judgment:** resources inside the package that are currently readable may be enough. Preserve this prediction first.
3. **Gap discovery:** ZIP/manifest inspection establishes consistent content, not the behavior of Markdown references and symbolic links at another location.
4. **Preparation:** study relative references, absolute symbolic links, and directory links for this specific use.
5. **Probe:** move an isolated copy, make the former location unavailable, and read the references. An absolute link fails; a later directory-link variation exposes an indirect dependency.
6. **Changed judgment:** readable now does not imply portable; a target appearing within the package does not rule out indirect dependencies. Reopen dependent acceptance items.
7. **Remediation:** repair the checking method, preserve both failures and input identities, rerun originals and variations.
8. **Contact:** the repair is within scope and needs no user choice. Complete it and explain the change in the result without creating another chat.
9. **Skill adjustment:** add separate archive/readability/relocation checks to a candidate, preserve rollback, and adopt only within the tested scope.
10. **Continuation:** the next host reads the newest revision, reuses the checker, and writes back variation results. Schedule later work only when spaced review has a purpose.

The repairs close specific gaps: an exit code becomes a version-bound stage result; an isolated report becomes a retrievable review; a changed rule receives a retest; a path list becomes evidence of actual reading.

## 7. Turn experience into meta-capability

One task teaches how to check a kind of package. The outer loop asks why evaluation layers are repeatedly confused, why retrieval is excessive, or why proposals only add prompt text. Abstract the mechanism into a hypothesis, test it in another domain, and regress previously successful tasks.

The full-task study paired software handoff acceptance with NASA data analysis. Batching helped archive work, while scientific conversion needed a different domain tool. Shared methods concerned input attribution, independent checking, charging failures to the whole task, and concise delivery. The composition used fewer tokens but more time, motivating a subsequent focus on repair cost rather than tool-call counts. See the [cross-domain report](cross-domain-trial.md).

## 8. Business, person, and event research

Entrepreneurship is a method example: clarify the domain, constraints, and deliverable, then proactively inspect current companies, funding, and primary product sources. Funding is a capital signal, not direct proof of paid demand or profit. Compare users, triggering situations, substitutes, acquisition, and unit-economics hypotheses, then design falsifiable interviews or small tests.

For people, distinguish their public statements, observed decisions, third-party evaluations, and system inference. Proposed cognitive frameworks need sources and counterexamples. For events, establish chronology, causes, process, outcomes, participants, and gaps. Causal claims need alternative explanations; value judgments identify affected parties and time horizons.

Across domains the structure remains purpose → decomposition → evidence → hypothesis → discriminating test → decision → observation → revision. Domain knowledge fills the content rather than replacing the loop.

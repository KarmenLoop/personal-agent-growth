# Complete Markdown learning contract · 0.4.4

[中文](markdown-learning.zh-CN.md) · [All template source files](../templates/learning/README.md) · [Storage boundaries](architecture.en.md#storage)

This page defines daily, weekly, project, behavior, and experience records. A host can follow the public skill to read and write these Markdown files. Native APIs, automatic injection, and due-work processing exist in the separate Koder candidate and are not generally released. Pseudocode here is not an installed command.

## 1. Root and final layout

An explicit root takes priority over `KODER_LEARNING_ROOT`; the separate Koder candidate defaults to `~/.koder/learning/`. Give every participating host the same resolved absolute root. Windows can prefer D: then C:, and macOS can use the Desktop or another chosen location. Choose and record the binding once rather than guessing it each turn.

```text
learning/
├── policy.md
├── index.md
├── daily/YYYY-MM-DD.md
├── weekly/YYYY-Www.md
├── weekly/YYYY-Www-consolidation.md
├── projects/<project-id>/
│   ├── memory.md
│   ├── context.md
│   ├── nodes/YYYY-MM-DD-HHMM.md
│   ├── summary.md
│   └── experience.md
├── experience/<exp-id>.md
├── research/<research-id>.md
└── user/
    ├── profile.md
    ├── behavior-log/YYYY-MM-DD.md
    ├── tags.md
    └── preview.md
```

Dates use the timezone in `policy.md`. ISO weeks use the ISO week-year, including year boundaries. If two nodes share a minute, append `-02`, `-03`, and select the newest by revision and sequence rather than overwriting. Research holds unverified material; experience holds retrievable conclusions. Both are Markdown. Uninstantiated distribution templates are excluded from retrieval.

## 2. Markdown format

```yaml
---
id: exp-2026-10-27-01
type: experience
project: null
tags: [domain/python, workflow/evidence-attribution]
status: active
created: 2026-10-27
updated: 2026-10-27
sources: []
revision: 1
validation: untested
---
```

IDs are stable and unique. A folder name alone does not establish project identity. Standard status is `active / done / deprecated`; keep additional review state in `review_status`. Sources identify paths/URLs, original record IDs, hashes, and referenced revisions for mutable documents. Prefer stable `#e-...` anchors. Line numbers can drift and should be bound to a source hash.

Types include memory, context, node, summary, experience, daily, weekly, consolidation, profile, behavior, tags, preview, index, policy, research, and project-experience. Preserve empty section headings, mark unknowns, and never invent facts. Replace placeholders, allocate a new ID, and remove `template: true` before treating a template as a record.

## 3. Project lifecycle

| Action | Read | Write | Completion condition |
|---|---|---|---|
| Create | Current goal, policy, project binding | Memory, context, initial node, index | Stable ID, scope, acceptance |
| Decide | Constraints and evidence | Memory facts/decisions, reason in node | Current user instruction takes priority; retain replaced sources |
| Pause | Artifacts and unresolved issues | New node and refreshed context | Blocker, attempts, executable next action |
| Resume | **Context + newest node**, then memory | Actual read set and progress | Check revision, input identity, writer |
| Complete | Current acceptance evidence | Summary, project/global experience, index done | Outcome met with checkable sources |
| Reopen | New facts and summary validity | Context/node/index; summary pending review | Do not inject stale completion as current truth |

Memory contains durable facts, constraints, decisions, critical paths, and prohibitions, not unstructured chat. Context contains current progress, hypotheses, questions, and next steps. Nodes preserve attempts and failures. Fill the summary only at completion and do not use an old summary to resume an active project.

## 4. Daily → weekly → next-Monday consolidation

Daily reports cover observed work, learning, reflection, changed thinking, and next actions. Add nodes for active or paused projects, update behavior/tags/profile where supported, and link new experience. Missing coverage is unknown, not evidence that the user did no work. A repeated trigger without new facts should not rewrite reports.

Weekly close reads all available daily reports in that ISO week, lists coverage and gaps, then extracts patterns, weaknesses, useful methods, and default-strategy candidates. The following Monday reads that report and actual adoption evidence, records applied/still-weak findings and review results, and updates the preparation preview. Improvements without application evidence remain unverified.

Start/end/idle events process only due work. Catch up after offline periods in bounded batches with a durable remaining range. The separate Koder candidate caps each batch at 366 dates and uses in-process due checks. The public skill requires a real host event or scheduler. The fixed cadence is daily/weekly semantics, not a universal minute interval.

## 5. Behavior evidence, not impressions

| Signal | Observable evidence | Use |
|---|---|---|
| Intent | User wording, timestamped goal/scope changes | Domain and planning |
| Interaction pace | Short/long instructions, interruptions, explicit `--yes` use | Collaboration; never added authority |
| Corrections | Repeated corrections, diff acceptance, rollbacks and reasons | Workflow gaps; attribute agent errors separately |
| Tool preference | Explicit use or rejection of shell/editor/browser/MCP | Default paths and preparation |
| Domain footprint | Current language, framework, task vocabulary | Domain tags, not inferred professional identity |
| Decision style | Explicit preference for action, alternatives, or confirmation | Planning granularity |
| Completion quality | Requested tests/docs/commits and pause reasons | Acceptance and experience |
| Time pattern | Authorized session activity and observed duration | Review timing; silence does not prove availability |

Each observation carries `event_id, observed_at, source, scope, signal, tag, direction, outcome, supersedes`, with facts distinguished from interpretation. Record physical state, habits, or language ability only when task-related and provided or observably authorized. Avoid derogatory personality labels and inferred private attributes. Corrections outrank statistics. Withdrawing a source requires dependent tags, plans, and summaries to be recomputed or downgraded.

## 6. Calculable scores and promotion

Tags use `domain / workflow / collab`. Deduplicate by original event, not summary count. Exclude future dates, withdrawn sources, out-of-scope collection, and retellings. Keep opposing signals explicitly rather than silently canceling them.

Let `N=count_30d`, `C=min(N/10,1)`. `R` sums daily-presence weights over seven local dates, from 7/28 today to 1/28 six days ago, at most once per date. `S` uses independently verified outcomes attributable to the strategy; without them it is null. These are transparent project heuristics, not psychometric measurements.

```python
def evaluate_tag(tag, now, policy, logs, projects):
    # Resolve active source revisions before counting anything.
    events = valid_unique_evidence(logs, tag, now, within_days=30)
    support = [e for e in events if e.direction == "support"]
    oppose = [e for e in events if e.direction == "oppose"]
    N, O = len(support), len(oppose)
    D = len(set(e.local_date(policy.timezone) for e in support))
    C = min(N / 10, 1.0)
    # Each local date contributes at most once; today has weight 7/28.
    R = sum((7 - age) / 28 for age in range(7)
            if any(e.age_in_local_days(now) == age for e in support))
    outcomes = independently_verified_outcomes(events, tag)
    S = successes(outcomes) / len(outcomes) if outcomes else None
    score = .5*C + .3*R + .2*S if S is not None else (.5*C + .3*R)/.8
    if N == 0:
        confidence = 0.0
    elif N < 3 or D < 2:
        confidence = min(.69, .2 + .1*N + .1*D)
    else:
        confidence = min(.95, .7 + .15*min((N-3)/7, 1)
                         + .1*min((D-2)/3, 1))
    confidence *= N/(N+O) if N+O else 0
    conflict = same_day_opposition(events) or explicit_unresolved_correction(events)
    stale = days_since_last_support(support, now) >= 14
    durable = five_consecutive_workdays(support, policy.calendar) or \
              three_independent_done_projects(support, projects)
    stable = score >= .6 and confidence >= .7 and durable and not conflict and not stale
    state = "conflict" if conflict else "stale" if stale else "stable" if stable else "observing"
    return {"score": score, "confidence": confidence, "state": state,
            "count_30d": N, "days": D, "oppositions": O,
            "success_rate": S, "evidence": [e.anchor for e in events]}
```

At least three observations over two days are needed for unopposed confidence to reach 0.7. A stable preference additionally needs score≥0.6, confidence≥0.7, and five consecutive configured working days or three independent completed projects. Fourteen days without reinforcement makes it stale. Same-day opposition enters the profile's pending-confirmation section and planning uses neutral defaults. Explicit preferences take effect within their scope immediately, separately from inferred tags; statistics never grant authority.

Each tag stores numbers, algorithm version, calculation time, evidence anchors, and state. Preview selects weekly concepts, repository conventions, and checks from strong domains and observed gaps. Frequent TypeScript use does not imply the user can only work in TypeScript.

## 7. Retrieval and context budget

```python
def project_packet(root, project_id, task, token_limit=4000):
    policy = read_md(root / "policy.md")
    if not policy.enabled:
        return None
    with writer_or_snapshot_guard(root):
        context = read_md(root / "projects" / project_id / "context.md")
        node = read_latest_valid_node(root, project_id)  # revision, then timestamp/sequence
        memory = read_md(root / "projects" / project_id / "memory.md")
        verify_project_id_revisions_and_sources(context, node, memory)
        if has_unresolved_manual_conflict(context, node, memory):
            return explicit_conflict_without_overwriting()
        required = [context, node, mandatory_non_decision_sections(memory)]
        if count_tokens(required) > token_limit:
            return required_context_overflow()  # never silently drop a constraint
        decisions = decision_section(memory)
        if fits(required + [decisions], token_limit):
            required += [decisions]
        else:
            notice = require_paged_read_before_memory_write(memory.id, memory.sha256)
            if not fits(required + [notice], token_limit):
                return required_context_overflow()
            required += [notice]  # original decisions stay unchanged on disk
        hits = search_markdown(root / "experience", id=task.experience_id,
                               tags=task.domain_tags, keywords=task.keywords)
        eligible = [x for x in hits if scope_matches(x, task)
                    and sources_current(x) and x.status != "deprecated"
                    and x.validation in ("local", "reused")]
        ranked = rank(eligible, domain_match=True, failure_match=True,
                      evidence_strength=True, recency=True, deterministic_ties=True)
        packet = fit_optional(required, ranked, limit=token_limit, top_n=5)
        if context.project_status == "done":
            packet += fit_current_verified_summary(root, project_id, remaining(packet))
        if task.is_planning or task.is_monday_consolidation:
            packet += fit_preview_and_due_reports(root, remaining(packet))
        return packet_with_source_paths_revisions_hashes_and_purpose(packet)
```

Context and the latest node are mandatory for recovery. Required memory constraints cannot be displaced by optional experience. Filter validity and scope before ranking by domain and failure mechanism, then select up to five entries. Load summary only when the project is done and its sources remain current. Daily/weekly/preview material is for planning and consolidation, not blanket injection.

Keep source paths, hashes/revisions, and adoption reasons. Experience can be injected in full or as scenario plus repeatable steps, while preserving scope, counterexamples, and invalidation conditions. The packet targets 2–4k tokens and fails explicitly if required content cannot fit within 4k. Actual token counting and host injection remain separately verifiable implementations of this protocol.

The repaired Koder candidate explicitly defers an oversized decision section, with its document ID and current hash, rather than dropping it silently. Read `learning_read open` pages by following `next` until null before a native memory write. Partial pages or a previous version do not satisfy this guard. Goals, criteria, constraints, critical paths and prohibitions still have to fit. After any failed pack read, reconcile and read a successful fresh pack before dependent writes. This is a runtime contract; the portable Skill alone does not install it.

## 8. Reuse operations

| Operation | Behavior | Constraint |
|---|---|---|
| Open by ID | Scan metadata or a rebuildable index; read original MD | Stale index falls back to original files |
| List by tag | Filter sources/scope, rank relevance/confidence/recency | Weak evidence does not drive strong planning |
| Keyword search | Titles, sections, body, optionally rg | A vector store is optional; caches are not another truth source |
| Link | Bidirectional project/experience references | Resolve relative to the current document |
| Merge | New entry preserves sources; old entries deprecated + superseded_by | Update index; keep old links |
| Export | Identify full original MD or selected sections and sources | Exclude private profiles, credentials, raw chat from publication |
| Research | Primary websites/GitHub, question, date, sources, summary, limits | Start untested; actual use permits local/reused status |

Suggested API responsibilities cover project create/update, node writing, daily/weekly/Monday close, experience open/search/merge, observation/tag recomputation, and packet construction. Native candidate command names are described in [compatibility](compatibility.en.md); installing the public skill does not promise these commands.

## 9. Writes, conflicts, and migration

Use one current writer per project, recheck revisions before commit, write the new node/evidence before context/index, and read back. If the host has no atomic multi-file transaction, use a recoverable Markdown journal with target, old hashes, staged files, and commit phase. Recovery checks actual files instead of trusting a completed label. Concurrency requires independent tests; a writer convention alone is not a lock.

When learning is disabled, do not inject, automatically observe, or permit learning-tool writes. Re-enable by reading existing Markdown rather than refilling it from a hidden old profile. Old SQLite/JSON stores remain historical inputs or experiment receipts. Follow the architecture's migration procedure, check knowledge/nodes/sources and the new entry point, and avoid two mutable profiles.

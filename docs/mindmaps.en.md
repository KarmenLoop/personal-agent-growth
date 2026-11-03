# Detailed mind maps and diagrams · 0.7.0

[English](mindmaps.en.md) · [中文](mindmaps.zh-CN.md)

Fourteen diagrams per language: four detailed mind maps plus architecture, scheduling, handoff, calendar flow, Windows skip auditing, Windows Agent recovery, capability evidence, adaptive unfamiliar-domain learning, and evidence-based judgment. Each language uses the same branch topology. These diagrams describe responsibilities and contracts; they do not establish that every host implements them. Check [compatibility](compatibility.en.md) for evidence. Open SVG files to zoom; Mermaid sources are editable.

## Complete capability tree

137 nodes, including conditions, artifacts, and failure continuations.

[SVG](diagrams/system.en.svg) · [Mermaid](diagrams/system.en.mmd)

![Complete capability tree](diagrams/system.en.svg)

## Architecture and data flow

[SVG](diagrams/architecture.en.svg) · [Mermaid](diagrams/architecture.en.mmd)

![Architecture and data flow](diagrams/architecture.en.svg)

## Causal judgment and revision

92 nodes, including conditions, artifacts, and failure continuations.

[SVG](diagrams/reasoning.en.svg) · [Mermaid](diagrams/reasoning.en.mmd)

![Causal judgment and revision](diagrams/reasoning.en.svg)

## Memory and user evidence

92 nodes, including conditions, artifacts, and failure continuations.

[SVG](diagrams/memory.en.svg) · [Mermaid](diagrams/memory.en.mmd)

![Memory and user evidence](diagrams/memory.en.svg)

## Two recursive levels and cost

92 nodes, including conditions, artifacts, and failure continuations.

[SVG](diagrams/recursion.en.svg) · [Mermaid](diagrams/recursion.en.mmd)

![Two recursive levels and cost](diagrams/recursion.en.svg)

## Real wakeup and stopping

[SVG](diagrams/continuation.en.svg) · [Mermaid](diagrams/continuation.en.mmd)

![Real wakeup and stopping](diagrams/continuation.en.svg)

## Cross-tool recovery sequence

[SVG](diagrams/handoff.en.svg) · [Mermaid](diagrams/handoff.en.mmd)

![Cross-tool recovery sequence](diagrams/handoff.en.svg)

## Daily/weekly learning and corrections

[SVG](diagrams/cadence.en.svg) · [Mermaid](diagrams/cadence.en.mmd)

![Daily/weekly learning and corrections](diagrams/cadence.en.svg)

## Reading order

Start with the capability tree, follow architecture arrows, inspect one decision path, then locate its memory writes and next trigger. For experiments, trace a proposal through frozen evidence and composition before inspecting outer-loop promotion. The [architecture analysis](architecture.en.md) and [worked reasoning example](reasoning.en.md) explain why these transitions exist.

## Regenerate the diagrams

`tools/render_diagrams.mjs` uses development-only Mermaid and Playwright packages, plus Chromium. The checked render used Mermaid 11.4.1. Pass absolute package directories; no dependency is added to the Python runtime:

```sh
node tools/render_diagrams.mjs --mermaid-dir /path/to/node_modules/mermaid --playwright /path/to/node_modules/playwright --browser /path/to/chromium
```

After editing a source, regenerate both languages, inspect the output, and update the corresponding hashes in `publication.json`. The renderer writes source/output hashes and dimensions to `docs/diagrams/render-manifest.json`; `scripts/check_publication.py` rejects drift. Font and browser versions can change layout, so retain the actual generated artifacts.

## Windows skipped-check audit

[SVG](diagrams/windows-audit.en.svg) · [Mermaid](diagrams/windows-audit.en.mmd)

![Windows skipped-check audit](diagrams/windows-audit.en.svg)

## Windows Agent recovery

[SVG](diagrams/windows-agent.en.svg) · [Mermaid](diagrams/windows-agent.en.mmd)

![Windows Agent recovery](diagrams/windows-agent.en.svg)

[Worked continuation guide](windows-agent-continuation.en.md)

## Learning, teaching, and real application

111 nodes connect diagnosis, preparation, counterexamples, independent teaching, Markdown evidence, real scheduling, PPC and rollback.

[SVG](diagrams/capability-learning.en.svg) · [Editable Mermaid](diagrams/capability-learning.en.mmd)

![Capability curriculum](diagrams/capability-learning.en.svg)

## Adaptive learning across unfamiliar fields

This 56-node, 77-connection map follows problem recovery, mechanism retrieval, analogy checks, action choice, real host execution, scoped feedback, and later reuse. Return paths show where new evidence changes a plan and where a changed experience snapshot must be read again. The actual execution boundary separates a recorded start from the host action. Unknown effects return to reconciliation rather than an automatic retry.

[SVG](diagrams/adaptive-learning.en.svg) · [Editable Mermaid](diagrams/adaptive-learning.en.mmd) · [Executable tutorial](adaptive-learning.en.md)

![Adaptive unfamiliar-domain learning](diagrams/adaptive-learning.en.svg)

## Evidence-based judgment

A 12-node, 14-edge decision flow separates user choices from technical claims, checks contrary evidence, and supports retaining, revising, withdrawing or suspending a conclusion. [Protocol](../references/evidence-based-judgment.en.md).

[SVG](diagrams/evidence-judgment.en.svg) · [Mermaid](diagrams/evidence-judgment.en.mmd)

![Evidence-based judgment](diagrams/evidence-judgment.en.svg)

## Held-out tasks, complete costs and causal transfer

The integrated flow has 50 nodes and 62 connections: strategy freezing, independent task release, real Agent runs, source/target causal checks, native usage, overlapping clocks, independent grading and scoped adoption. It preserves failed and unmetered attempts. [Tutorial](measured-learning.en.md).

[SVG](diagrams/measured-learning.en.svg) · [Mermaid](diagrams/measured-learning.en.mmd)

![Measured learning flow](diagrams/measured-learning.en.svg)

# Learning science and curriculum design · 0.7.0

[中文](learning-science.zh-CN.md) · [Documentation index](index.en.md) · [Architecture](architecture.en.md)

Research date: **November 3, 2026**. This document explains the educational ideas behind the capability-learning design, their limits, and how to test the resulting Agent behavior. It does not report a new learning experiment or establish that these methods improve every model.

## 1. What changes when model weights stay frozen

Personal Agent Growth changes the instructions, tools, retrieval, external memory, evaluation, and scheduling around an existing model. It does not fine-tune the model or update its weights through reinforcement learning. A successful review can make a useful procedure easier to find and apply in a later session. That is an observable system improvement; it is not evidence of biological memory consolidation or an unmeasured increase in the model's intelligence.

The design draws on human learning research, official curricula, and university teaching guidance. Each translation into Agent behavior is an engineering hypothesis. It must survive a real task, a new variation, an appropriate regression check, and an accounting of time and cost.

“Learn, understand deeply, master, teach, and deliver” describes a useful ambition. It is not a single ladder. Explanation, causal reasoning, execution, transfer, teaching, and judgment need separate evidence. A fluent explanation does not prove execution. A completed task does not prove teaching. Practice starts with small, inspectable actions; an Agent need not claim mastery before trying them.

## 2. A curriculum is a dependency structure

School stages offer ideas for organizing increasing complexity. They are not labels for the user's intelligence, and they are not a claim that a model develops like a child. The table is this project's synthesis, not a curriculum copied from one country.

| Educational emphasis | Unit of learning | Practice begins with | Evidence for greater complexity |
|---|---|---|---|
| Primary: observation, vocabulary, examples, basic operations | Identify an object, its inputs and outputs, units, and a non-example | Read an actual artifact, perform a small calculation, or try an authorized reversible action | Correctly handle a changed simple example and identify what remains unknown |
| Lower secondary: relationships, variables, models, experiments | Connect prerequisites and predict the effect of changing a condition | Compare two inputs or methods and inspect their results | Explain which evidence supports the difference and consider an alternative explanation |
| Upper secondary: formalization, composition, counterexamples | Combine skills, inspect assumptions, quantify error where possible | Complete a multistep task and handle an exception | Meet the criteria on an unseen task and identify when the method fails |
| University: disciplinary methods, literature, research design | Read primary sources, compare methods, define a reproducible study | Reproduce a useful method and produce a reusable result | Provide reproducible artifacts, quality/time/cost comparisons, and limits |
| Teaching and professional practice: present throughout | Explain to a specific audience, diagnose misunderstanding, deliver and maintain work | Have a learner solve a new problem; read back the delivered artifact | Verify learning and operational delivery separately |

Decomposition stops when a unit is observable, testable, and relevant to the next decision. Breaking every task into ever smaller fragments can increase overhead while hiding the whole task. The curriculum must return to integration and actual delivery.

## 3. Compare mechanisms, not national rankings

| Education system | Mechanism documented by the official source | Adaptation for this project | What the source does not establish |
|---|---|---|---|
| Singapore | A problem-solving framework connecting concepts, skills, processes, attitudes, and metacognition | Organize preparation around a task; record the strategy selected and the observation that would change it | That a national test result proves one teaching method caused it, or that an Agent inherits human attitudes [E07] |
| Finland | Subject teaching alongside transversal competencies and multidisciplinary learning | Keep domain prerequisites while testing whether a method transfers to another setting | That interdisciplinary projects replace all subject knowledge [E08] |
| Estonia | General competencies and formative assessment, with distinct expectations for basic and upper-secondary education | Use specific feedback to select the next practice task; retain the earlier attempt | That a broad framework establishes the current content of every school or every law [E09] |
| Japan | Knowledge and skills; thinking, judgment and expression; learning orientation, with observation and experimentation | Track execution and judgment separately, and compare predictions with observations | That knowing facts alone establishes sound judgment; the official report also describes remaining learning difficulties [E10] |

These mechanisms are complementary candidates. We do not rank countries as universally strongest or infer educational causation from PISA scores.

At university level, [MIT's backward-design guidance](https://tll.mit.edu/teaching-resources/course-design/backward-design/) begins with intended outcomes and acceptable evidence before selecting activities. [CMU's learning principles](https://www.cmu.edu/teaching/principles/learning.html) distinguish component skills, integration, and knowing when to apply them. [Harvard Project Zero's Teaching for Understanding](https://pz.gse.harvard.edu/projects/teaching-for-understanding) emphasizes flexible use in unfamiliar contexts. Together, they motivate an outcome contract, a prerequisite graph, and a separate transfer check—not a list of courses the Agent must finish.

## 4. Mechanism → action → evidence → next step

The following behaviors are original engineering adaptations. Sources support the educational ideas, not the success of our implementation.

| Mechanism | Concrete Agent behavior | Evidence required | If it fails |
|---|---|---|---|
| Backward design [E11] | Define the deliverable, acceptance observations, constraints, and budget before selecting reading | A result checked against the original criteria | Narrow the gap or repair the deliverable; do not rewrite the criteria to fit it |
| Prior-knowledge diagnosis [E12] | Try one bounded prerequisite task; distinguish conceptual, strategy, input, tool, environment, and permission problems | Raw output supporting the diagnosis | Repair the relevant layer and retest; an unavailable tool is not proof of a knowledge deficit |
| Retrieval practice [E01–E02] | Produce a testable prediction, then retrieve and compare relevant experience in a fresh session | What was loaded, what was recalled, the source used, and the resulting behavior | Repair retrieval or the lesson; never hide mandatory constraints to simulate a closed-book test |
| Spaced review [E01] | Revisit a lesson on a later relevant task or a real scheduled trigger; check freshness and applicability | Actual event identity and time, source version, and a new result | Mark stale evidence and choose a targeted review; a date in a file is not a wakeup |
| Self-explanation [E03, E06, E15] | State a concise mechanism, assumptions, example, and boundary, then test a prediction or counterexample | Correct observations beyond a polished explanation | Record the contradiction and change the mechanism; more prose is not remediation |
| Mastery and formative feedback [E09, E12] | Repair a specific prerequisite, then try a new equivalent problem and the integrated task | New-task evidence and the complete deliverable | Keep the original failure, select a different intervention, or stop at the budget |
| Cognitive apprenticeship [E04] | Start with an observable demonstration and gradually remove hints and templates | A new session completes a different input with recorded assistance | Identify the missing step, restore only the necessary support, and retest |
| Metacognition [E07, E12] | Record a prediction before action; compare it with the return and revise the plan | Timestamped prediction, observation, and changed decision | Inspect the mismatch and revise the method instead of claiming it was expected |
| Transfer [E08, E13] | Match the mechanism and prerequisites, then test a different domain, tool, or input distribution | An independently checked target task and a negative-transfer check | Narrow the experience's scope or reject it for that target |
| Teaching [E06, E14] | Explain to a defined learner, give an unseen exercise, inspect the learner's response, and address the misunderstanding | Actual learner performance without the answer; label human and Agent learners separately | Revise the explanation or exercise; a tutorial alone leaves teaching unverified |
| Judgment [E10, E12] | Compare alternatives, decisive uncertainties, consequences, and the value of another check | The original decision criteria, rejected alternatives, and reasons for a later change | Gather information that could change the decision, or expose the unresolved choice |

“Visible thinking” here means concise, inspectable claims, assumptions, predictions, decisions, and tool evidence. It does not require exposing a model's hidden chain of thought.

## 5. Feynman, explanation, and their limits

Richard Feynman was a physicist and teacher. His [preface to the Lectures](https://www.feynmanlectures.caltech.edu/I_91.html) describes lectures as part of a course that also included discussion and laboratory work, and discusses limitations of the teaching effort. It does not establish a universal four-step psychological law.

[Caltech's current teaching-to-learn guidance](https://ctlo.caltech.edu/aboutctlo/whoweserve/undergraduates/learning-resources/learning/power-of-teaching) recommends explaining without notes, locating gaps, returning to the material, and engaging a real audience. The page attributes its adaptation to other learning resources. We retain that provenance rather than crediting every step to Feynman.

Explanation is a diagnostic tool, not automatic proof of learning. In a [2026 preregistered study](https://onlinelibrary.wiley.com/doi/10.1002/acp.70174), 208 participants learned fictional facts. The reported comparison did not find a learning-strategy advantage for self-explanation over rereading, either immediately or after a two-week delay. Correct inferences were associated with performance. This result concerns that task and does not show that all explanation is ineffective. We reviewed the abstract and relevant background, not the complete methods and analysis.

For an Agent, the practical rule is to test whether explaining changes the quality of the next action. Retain it when useful; shorten or replace it when it adds cost without improving the result.

## 6. Six dimensions of capability evidence

| Dimension | An acceptable observation | Insufficient evidence |
|---|---|---|
| Explanation | A correct, audience-appropriate account that survives a concrete question | Fluency, length, or jargon |
| Causal reasoning | A prediction and a test that discriminate relevant alternatives | A plausible story written after the result |
| Execution | An authorized real action, artifact, and readback against the criteria | A plan, mock, or submitted request |
| Transfer | Correct application under a meaningful change of context | Renaming the original example |
| Teaching | A learner independently completes a new relevant task | The teacher writes both the lesson and the answer |
| Judgment | A decision made against explicit criteria, with uncertainty and revision conditions | Confidence without supporting observations |

Evidence needs a task and criterion ID, scope, input and artifact identity, source and environment versions, actual time, executor, reviewer, assistance, and answer-exposure status. Self-report, tool validation, independent Agent review, and human feedback are different evidence types.

Contradictory or stale evidence must remain visible. A capability proven on one project is not automatically general. A display stage summarizes the available evidence; it must not overwrite these dimensions or block a useful low-risk practice task.

## 7. One connected task

Consider a request for a verifiable quality report on an unfamiliar CSV dataset. The following is a design example, not a claim that this experiment has run.

1. **Define the result.** Establish the decision the report supports, required statistics, missing-value rules, output format, and budget. If the user only needs a report, do not force an unrelated teaching exercise.
2. **Recover and diagnose.** Read current project context and its latest node, then relevant experience. If empty strings and numeric zero have unclear meanings, record a semantic gap rather than guessing a user preference.
3. **Prepare with a purpose.** Read the data dictionary or authoritative format documentation. State the expected missing and duplicate counts for a small input before executing a check.
4. **Use the mismatch.** If the result differs, inspect parsing, types, and filters. Preserve the failed observation, repair the specific cause, and try a new format and a counterexample. Then run against the complete dataset and read back the report.
5. **Compare improvements.** A general proposal could fix the measurement contract before analysis; a domain proposal could improve CSV encoding and missing-value handling. Run each against the same frozen input and conditions. Evaluate complete quality, elapsed time, and cost. A candidate cannot win by changing its own checker.
6. **Test reuse.** Give a fresh session the Skill, the same memory root, and a different dataset. Observe whether it finds and correctly applies the experience. A retrieval failure requires a retrieval repair, not an unsupported claim about conceptual weakness.
7. **Test teaching when needed.** Have another Agent or a person use the lesson on an unseen input. Label who learned and what they completed. Otherwise, leave that capability dimension unverified while delivering the report.
8. **Review on a meaningful trigger.** A source change, repeated error, or later relevant task can justify review. A scheduled review needs an actual host binding and trigger receipt. Without one, it remains pending for a later session.

## 8. Evaluation and implementation consequences

Keep knowledge and experience conclusions in Markdown. Machine-readable metadata can support retrieval; a derived index must remain rebuildable. Raw tool receipts may be linked from Markdown without becoming a second store of conflicting learning conclusions.

Before an activity, freeze its target, input identity, expected observation, failure continuation, resource budget, and stopping rule. Afterward, distinguish success, failure, invalid execution, and not run. An infrastructure failure may invalidate an experiment; it cannot count as a capability pass.

Compare the whole task. Quality includes semantic correctness, source fidelity, exception handling, reproducibility, and usefulness for the requested purpose. Report task execution and optimization overhead separately, including failed attempts. Time spent on research, coordination, and human assistance must not disappear from a speed claim. Unknown token usage or monetary cost remains unknown.

A new strategy must preserve the frozen acceptance criteria and pass appropriate prior-capability regression. If a useful finding survives only within one project or one tool, retain that scope. Two successful domains are evidence for those domains, not proof of universal expertise.

For daily and weekly review, select an actionable change from a real failure or prediction error. If there is no new evidence, retain the existing state. Rewriting a reflection is not itself progress.

## 9. Sources and access record

All sources below were checked on November 3, 2026. “Indexed text” means text returned by search for the official URL; it does not mean the complete document was downloaded. Access problems were retained rather than bypassed.

| ID | Source | Material reviewed and access |
|---|---|---|
| E01 | [IES / WWC, Organizing Instruction and Study to Improve Student Learning (2007)](https://ies.ed.gov/ncee/wwc/PracticeGuide/1) | Official recommendations page opened; evidence ratings differ across recommendations |
| E02 | [Karpicke & Roediger, The Critical Importance of Retrieval for Learning, Science (2008)](https://doi.org/10.1126/science.1152408) | Original article abstract; human vocabulary-learning experiment |
| E03 | [Chi et al., Self-Explanations, Cognitive Science (1989)](https://onlinelibrary.wiley.com/doi/abs/10.1207/s15516709cog1302_1) | Original article abstract; mechanics examples and subsequent problem solving |
| E04 | [Collins, Brown & Holum, Cognitive Apprenticeship (1991)](https://www.aft.org/ae/winter1991/collins_brown_holum) | Authors' article, including methods and their limits |
| E05 | [Feynman, Preface to The Feynman Lectures on Physics (1963)](https://www.feynmanlectures.caltech.edu/I_91.html) | Volume I page body; a Volume III attempt first returned a JavaScript notice |
| E06 | [Caltech CTLO, The Power of Teaching](https://ctlo.caltech.edu/aboutctlo/whoweserve/undergraduates/learning-resources/learning/power-of-teaching) | Official guidance and its attribution |
| E07 | [Singapore MOE, Primary Mathematics Syllabus](https://www.moe.gov.sg/-/media/files/primary/mathematics_syllabus_primary_1_to_6-) and [Secondary Mathematics Syllabus (2020)](https://www.moe.gov.sg/-/media/files/secondary/syllabuses/maths/2020-express_na-maths_syllabuses.pdf) | Official indexed framework text; direct retrieval required a robot check |
| E08 | [Finnish National Agency for Education, Core Curriculum for Basic Education](https://www.oph.fi/en/education-and-qualifications/national-core-curriculum-primary-and-lower-secondary-basic-education) | Official page body |
| E09 | [Estonia Ministry of Education and Research, General Education](https://hm.ee/en/education-research-and-youth-affairs/general-education/general-education-estonia) | Official page describing the framework introduced in 2014; not a current legal audit |
| E10 | [Japan NIER, Science Education at the Stage of Compulsory Education in Japan (2021)](https://www.nier.go.jp/English/educationjapan/pdf/20210623-02.pdf) | Official PDF, especially pages 16–18 |
| E11 | [MIT Teaching + Learning Lab, Backward Design](https://tll.mit.edu/teaching-resources/course-design/backward-design/) | Official indexed text; direct retrieval returned HTTP 502 |
| E12 | [CMU Eberly Center, Learning Principles](https://www.cmu.edu/teaching/principles/learning.html) | Official page body |
| E13 | [Harvard Project Zero, Teaching for Understanding](https://pz.gse.harvard.edu/projects/teaching-for-understanding) | Official indexed text; direct retrieval returned HTTP 502 |
| E14 | [Harvard Project Zero, Visible Thinking](https://pz.gse.harvard.edu/projects/visible-thinking) | Official indexed text |
| E15 | [Harders & Ebersbach, No Causal Self-Explanation Effect for Factual Knowledge (2026)](https://onlinelibrary.wiley.com/doi/10.1002/acp.70174) | Original article abstract and relevant background; no full methods or analysis review claimed |

## 10. Independent implementation and attribution

The capability evidence model, task transitions, and evaluation interfaces are an original synthesis for this project's architecture. Retrieval practice, cognitive apprenticeship, formative assessment, and other cited ideas are not our inventions. This document summarizes and links to them; it does not import third-party code, textbooks, course assessments, or figures.

If implementation later incorporates an open-source component, record its project, version, license, imported files, and modifications. Public access alone is not permission to redistribute educational material. Independent implementation and clear attribution are compatible requirements.

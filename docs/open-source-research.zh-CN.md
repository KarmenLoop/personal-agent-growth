# 0.6.1 开源 Agent 研究与互操作设计

[English](open-source-research.en.md) · 简体中文

核查日期：2026-11-03（Asia/Shanghai）。状态：**官方源码/文档研究完成；未安装这些项目，未执行任何第三方 Agent，未验证与 PAG 的真实集成。** 本文描述候选设计；其中契约字段用于讨论适配器边界，不宣称现有 CLI 已实现这些 API。

## 结论与实施选择

本轮建议保持 personal-agent-growth 的独立实现：Markdown 是长期知识、课程进度与经验的唯一真相源；模型权重固定；运行时 adapter 只交换显式任务包、操作回执与产物引用。下列项目贡献的是可研究的机制与可选协议入口，不是本项目已获得的能力。不要一次引入十套框架，更不要把增加提示词长度、后台会话数量或检查次数当作进步。

优先原创实现三个小契约：**能力证据卡 → 受约束的实验运行收条 → 可撤销的经验晋升**。先保证判定真实，再增加后台编排。外部框架只作为可替换的执行/评估适配器；没有宿主执行回执时，能力状态保持 planned / unavailable，不能写 verified。

## 逐项研究与选择

### 1. LangGraph：任务恢复与跨会话记忆必须分开

- 核实机制：checkpointer 存同一 thread 的图状态，store 存跨 thread 的应用知识。官方文档特别指出 InMemorySaver 重启丢失；“有 checkpoint API”不等于已经持久化。[Persistence](https://docs.langchain.com/oss/python/langgraph/persistence)、[Checkpointers](https://docs.langchain.com/oss/python/langgraph/checkpointers)。
- 对 PAG：context + 最新 node 负责当前任务恢复；memory / experience 负责长期知识。adapter 要交付同一 memory-root 身份、revision、输入内容哈希，恢复前检查，不只复用聊天标题。
- 失效条件：恢复时重复外部副作用、并行覆盖旧 revision、把内存实现冒充跨进程恢复。只在已知可重放动作上自动重试；对未知提交结果先读回。
- 建议验收：完成一次有副作用的动作，在回执写前/后分别中断；重启实际 Agent 后不得重复该副作用；同一经验在另一新会话可检索，并准确引用原 Markdown。
- 当前选择：原理参考；本轮不引入 LangGraph DB 作为第二真相源，也不增加 LangSmith 云依赖。
- 许可：MIT，已读原件。[LICENSE](https://github.com/langchain-ai/langgraph/blob/3c916d750575b22c464790e9774494d810ccd322/LICENSE)。

### 2. Letta Code：后台复盘与记忆整理，但不能沿用旧部署认知

- 当前项目迁移：letta-ai/letta 的 README 指向 letta-ai/letta-code；旧 V1 server 留在 archive 分支。[官方迁移说明](https://github.com/letta-ai/letta/blob/main/README.md)。
- 核实机制：MemFS 用 Git 保存可编辑记忆；dreaming 用后台 subagent 复查会话、整合经验；可再由一个 Agent 审查改动；官方描述允许修改 memory/skills/prompts/harness mods。[Memory & dreaming](https://docs.letta.com/configuration/memory)、[当前 README](https://github.com/letta-ai/letta-code/blob/9df436cffa588f45aadef86f34d43fb8f3008c40/README.md)。
- 对 PAG：复盘先生成候选差异，只有来源有效、无冲突、可迁移证据足够才更新现行经验。记忆整理和能力晋升分开，避免“写过经验 = 已学会”。
- 实际限制：当前 README 明确 native Windows 自动反思默认关闭；安装 wheel 不支持 Windows ARM64；默认 Letta Cloud，需明确 local 选择。因此不可直接宣称适配我们已测的 Windows ARM64 VM，也不可默认把本地用户记忆迁往云。
- 建议验收：后台候选包含一条真实新结论、一条过时偏好、一条不具证据的推断；只合并新结论，过时偏好保留修订缘由，推断保持观察中。关闭宿主后的唤醒需另外由宿主真实执行证明。
- 当前选择：研究低干扰复盘、记忆版本、mods 差异；不移植其人格宣传，不迁移用户数据库，不默认安装常驻服务。
- 许可：Apache-2.0，已读条款与文件标识。[LICENSE](https://github.com/letta-ai/letta-code/blob/9df436cffa588f45aadef86f34d43fb8f3008c40/LICENSE)。

### 3. DSPy：明确模块目标与可调参数，限制为提示词/示例优化

- 核实机制：program + metric + input samples；可优化指令、few-shot 示例，也支持 fine-tuning。官方将 BootstrapFinetune 和 BetterTogether 与提示词优化区分，不能把所有 DSPy 优化都叫“冻结权重”。[优化器官方源文档](https://github.com/stanfordnlp/dspy/blob/c8176a8fa65e9772d9d44a33f464f4271c97b806/docs/docs/learn/optimization/optimizers.md)。
- 对 PAG：每个技能模块写输入/输出/约束/失败模式；改进限定于 instruction、example-selection、tool-schema、retrieval-policy、planning-policy。模型标识与参数快照固定。对 hosted model 只能记录请求模型及 provider revision，不能证明供应商内部权重永久不变。
- 失效条件：优化目标只计格式/关键词，少样本过拟合，示例带入验收答案；模块级得分上升但完整任务变差。
- 建议验收：同模型同任务预算，用未优化 baseline、通用改法、领域改法、组合改法四组输出；训练/开发任务用于修改，封存任务只作最后评估，不读其答案来写候选。
- 当前选择：参考签名与分模块优化；不引入 BootstrapFinetune、权重蒸馏或 RL；不承诺框架文档中的时间/价格适用于本项目。
- 许可：MIT。[LICENSE](https://github.com/stanfordnlp/dspy/blob/c8176a8fa65e9772d9d44a33f464f4271c97b806/LICENSE)。

### 4. GEPA：最贴近现有 Propose–Probe–Compose 的可读反馈与互补候选

- 核实机制：使用执行轨迹与文本反馈提出提示词更新，以候选集合保留不同任务上的优势，能组合互补候选；当前接口把 evaluate、reflective dataset、proposal、adapter state 分离。[论文 v2](https://arxiv.org/abs/2507.19457v2)、[官方接口](https://github.com/gepa-ai/gepa/blob/8c7b697a71977980afc7537dac0881e784eef99f/src/gepa/core/adapter.py)。
- 对 PAG：失败不能只保留一个分数，应保留工具错误、产物缺陷、规则违反和资源瓶颈；通用候选 G 与领域候选 D 独立试跑后生成组合 C，再跑 C，不能假设两个有用改动相加仍有用。
- 与用户“不看标准答案”一致的做法：候选作者可看真实执行错误与可公开任务约束；不注入封存标准答案。评估者仍需要固定 rubric、可验证事实/属性、真实交付检查，否则“不看答案”会退化成自我赞同。
- 不照搬：论文是在特定任务与模型上得出结果；不把其 35x 等数字写成本项目提升。不要求公开或保存模型私有隐藏推理；用可观察 tool traces、产物和简明决策理由足以做缺陷归因。
- 建议验收：同一任务4组的完整质量、工作时间/端到端时间、token/实际计费、回滚/副作用分别保存；若 C 破坏已有能力即拒合并，即使某个局部分数更好。
- 当前选择：原理参照与可选实验 adapter；自研候选状态机，不直接复制优化器源码或宣布发明 GEPA。
- 许可：MIT。[LICENSE](https://github.com/gepa-ai/gepa/blob/8c7b697a71977980afc7537dac0881e784eef99f/LICENSE)。

### 5. OpenHands：宿主、执行器、调度器的职责不能混为一个 Skill

- 当前核实：主仓现在描述 Agent Canvas；实际 Agent Server/工具/事件属于 software-agent-sdk，定时与 webhook/run history 属于 automation。主仓支持选择本机、VM、容器或远端 backend，并使用 ACP 接入不同 Agent。[当前 README 与仓库边界](https://github.com/OpenHands/OpenHands/blob/7f6c52f8ea7187249dfe1b363a4c1efbfa9a6bc6/README.md)。
- 对 PAG：Skill 决定何时值得预习/复习；host adapter 执行并证明何时唤醒；runner 执行任务；receipt verifier 判定是否完成。写一个 schedule.md 不构成调度生效。
- 失效条件：网页显示 scheduled 被当成真正触发，转发给第二 Agent 后认为完成，多个聊天窗口写同一工作目录发生竞争。
- 建议验收：record host automation ID + native event ID + scheduled/actual times + run ID；从真实 event 恢复同 memory root，产物读取成功才闭环。多对话共享知识、独立工作区、写入冲突可检测。
- 当前选择：借鉴控制面/执行面分离；不默认部署全套 Canvas 或连外部渠道。对方 README 标注无 sandbox 时 Agent 能读写宿主文件，本项目不能因“框架开源”自动提升权限。
- 许可：本次核查主仓 MIT；其他子仓和依赖要分别检查，不能由主仓许可证覆盖全部生态。[LICENSE](https://github.com/OpenHands/OpenHands/blob/7f6c52f8ea7187249dfe1b363a4c1efbfa9a6bc6/LICENSE)。

### 6. mini-swe-agent：用最小基线检测脚手架到底有没有增益

- 核实机制：当前主线 v2；模型、environment、Agent 相互分离；线性历史，shell 动作独立执行，轨迹可以直接审查。[官方 README](https://github.com/SWE-agent/mini-swe-agent/blob/04d809ceab9df28f9adaed044884180159172930/README.md)。
- 对 PAG：对新教育/思考流程保留一个短流程 baseline。复杂控制器若在任务质量相等时显著更慢更贵，应缩短或按任务分流；不能为展示“智慧”强行每次走完整教学链。
- 不照搬：bash-only 不适合所有 GUI、Windows 或文档场景；环境能力必须真实探测；不把训练用途变成我们的 RL。
- 建议验收：用同一真实缺陷修复任务与同一解释/教学任务做最小 baseline；记录总调用和实际完成质量，避免只比较 Agent 核心代码行数。
- 当前选择：比较对象与简化思想，不替换 Koder/Cursor/Codex 的实际运行身份。
- 许可：MIT，文件实际是 LICENSE.md（最初 LICENSE 返回404，随后定位正确文件）。[LICENSE.md](https://github.com/SWE-agent/mini-swe-agent/blob/04d809ceab9df28f9adaed044884180159172930/LICENSE.md)。

### 7. Inspect：可重启评估与全任务资源统计

- 核实机制：独立 task/solver/scorer；eval-set 支持恢复未完成的评估；日志保存执行信息；限制可区分端到端时间与工作时间，并记录 token/费用。官方指出并行等待会使 working time 低估，不能用它替代 wall time。[日志](https://inspect.aisi.org.uk/eval-logs.html)、[eval-set](https://inspect.aisi.org.uk/eval-sets.html)、[限制](https://inspect.aisi.org.uk/setting-limits.html)。
- 对 PAG：执行者和判分者分开；完整任务作为统计单位，失败尝试成本也进总账；复盘/备课消耗同样计入，不把修复者时间隐藏成免费。
- 有意不采用的默认：eval-set 有清理失败运行日志功能；PAG 要保留失败台账，不能让一次后来成功抹掉原始失败。Inspect 的 .eval/JSON 日志可作原始附件，不能成为 Markdown 以外不可见的知识真相源。
- 建议验收：中断后的恢复不重复成功样本；失败/取消/超时/未知各自统计；费用未知写 null + 原因，不写0。任何评分改动保留版本及历史，不覆盖以前结果。
- 当前选择：原理与可选 external evaluator；本轮不安装200多个评估、不因通过某数据集就声称通用精通。
- 许可：MIT。[LICENSE](https://github.com/UKGovernmentBEIS/inspect_ai/blob/706b4c5d6a3af83150ae3fc66ddf84b6bc37f50f/LICENSE)。

### 8. promptfoo：固定判据与配对比较，谨防平均分掩盖硬失败

- 核实机制：确定性断言、模型评分、自定义指标、轨迹检查、latency/cost 指标；文档区分加权得分与必须每项通过，支持规则分组。[Assertions & metrics](https://www.promptfoo.dev/docs/configuration/expected-outputs/)。
- 对 PAG：引用正确性、文件真实存在、来源一致、权限、保留用户约束是硬门；表达清晰度等是软分；两个集合不能一个平均分抵消。成本和时延要有独立字段。
- 失效条件：AI 自己改 evaluator 来放过当前输出；模型 judge 偏爱冗长；cached 响应被计作新 Agent 实跑；框架运行在本地不表示远程模型调用不出机。
- 建议验收：加入格式全对但内容错误、非常简短但关键约束丢失、旧缓存回执、工具调用成功但产物错误等受控反例；盲评方法固定，随机对调候选显示顺序。
- 当前选择：参考分层判据；不引入生产攻击扫描，不拿通用 red-team 标签作为任务质量。
- 许可：MIT。[LICENSE](https://github.com/promptfoo/promptfoo/blob/f2b012e3c9f9ffb7b23edf4cf88ea63febf72f5a/LICENSE)。

### 9. MCP Python SDK：统一发现/调用接口，不赋予额外能力

- 核实机制：标准 tools/resources/prompts，server/client 与 stdio/Streamable HTTP 等 transport；当前 README 是 Python3.11+ 的 v2 文档路径，不能沿用旧 API 片段。[README](https://github.com/modelcontextprotocol/python-sdk/blob/d7845c073a2b9ba5ab2817ecf93d3e45ef24cd14/README.md)、[协议安全实践](https://modelcontextprotocol.io/specification/latest/basic/security_best_practices)。
- 对 PAG：可暴露 learning.read、learning.search、learning.checkpoint、learning.record_evidence，宿主决定真实可用接口。MCP 只是协议；schedule 能力与权限必须由真实 server capability 和调用回执确定。
- 建议验收：严格路径范围、大小上限、revision 对比写；未知工具拒绝，读工具不能触发写；外部网页和工具描述不能覆盖用户约束。跨宿主读取同一 Markdown 字节，并在恢复后写回 revision。
- 当前选择：记录互操作契约，支持可选 MCP adapter；先保留无第三方依赖的 CLI/file 路径，不让安装整个SDK变成使用Skill前提。
- 许可：MIT。[LICENSE](https://github.com/modelcontextprotocol/python-sdk/blob/d7845c073a2b9ba5ab2817ecf93d3e45ef24cd14/LICENSE)。

### 10. AutoGen：保留不采用的证据，避免靠知名度选型

- 当前 README 明确 no longer maintained/archived 并建议新项目选择 Microsoft Agent Framework；同次 GitHub repository API 的 archived=false，二者状态不一致。应写“README 宣布停止维护、API归档标志未同步”，而不是擅自抹平冲突。[README](https://github.com/microsoft/autogen/blob/d07c667a3239ea4ab7af62a53b0f4ff205a1f23d/README.md)。
- 许可不能只看GitHub summary：代码 LICENSE-CODE 为MIT，根LICENSE为CC-BY-4.0文本。[代码许可](https://github.com/microsoft/autogen/blob/d07c667a3239ea4ab7af62a53b0f4ff205a1f23d/LICENSE-CODE)、[根许可](https://github.com/microsoft/autogen/blob/d07c667a3239ea4ab7af62a53b0f4ff205a1f23d/LICENSE)。
- 可研究层次：core message transport / higher-level AgentChat / extensions 分层。
- 当前选择：历史参照，不新增运行依赖。其后继项目仅记录为后续候选，本次没有做完整许可证/运行验收，不能宣布已接入。

## 原创接口建议：先实现可检验的小边界

以下接口由 PAG 独立设计，是建议契约，不是已存在API。Markdown文首元数据保存结构化字段，正文保留解释；JSON只作传输/派生视图，删除JSON后应可从Markdown重建。

### A. CapabilityCard：把“不会”拆成可处理的原因

```yaml
id: cap-domain-task-name
scope: project/example
stage: unknown | reproduces | explains | transfers | teaches | delivers
status: untested | verified | needs_review | unavailable
prerequisites: [cap-...]
gap_kind: knowledge | procedure | tool | environment | authorization | evidence
evidence: [{path: runs/run-id.md, sha256: "...", claim: "..."}]
valid_for: {tool: "...", platform: "...", versions: ["..."]}
review_due: "actual date or null"
```

stage 是多维能力摘要而不是自动直线升级：能操作不一定能教；能解释不一定能实操；“精通”只在已声明的任务分布和环境内成立。环境或权限缺失不能靠更多自我提示解决；应先选替代路径或定位真正缺口。

### B. RunReceipt：真实实验与能力证据的连接点

```yaml
id: run-...
task_id: ...
candidate_id: baseline | general | domain | composed
actor: {host: "...", agent: "...", model: "...", session_id: "..."}
inputs: [{path: "...", sha256: "..."}]
memory: {root_identity: "...", read_revision: 7, written_revision: 8}
trigger: {kind: user | native_schedule | continuation, host_event_id: null}
started: ...
ended: ...
execution: {status: passed | failed | cancelled | unknown, exit_code: null}
artifacts: [{path: "...", sha256: "..."}]
quality: {rubric_version: "...", hard_gates: [], dimensions: {}, assessor: "..."}
usage: {wall_seconds: null, working_seconds: null, model_tokens: null, money: null, currency: null, unknown_reason: "..."}
follow_up: {decision: keep | repair | rehearse | review | reject, evidence: "..."}
```

工具层回执与模型自述分开保存；exit0、self_score、写了总结都不足以证明实操成功。只保存可观察调用/结果与简洁决策说明，不要求获取私有隐藏思维链。

### C. CandidatePatch：可调的是壳，不能修改成绩标准

```yaml
candidate_id: ...
kind: general | domain | composed
parent_version: ...
change_surface: prompt | skill | tool-description | retrieval | scheduler-policy | runner
hypothesis: ...
expected_improvement: ...
scope: ...
patch_sha256: ...
protected: [user_constraints, evidence_history, rubric, permission_boundary, held_out_tasks]
probe_runs: [...]
decision: proposed | rejected | provisional | adopted | reverted
```

shell/runner 改动实际提高权限或改变外部副作用时，仍需遵守已有用户授权；“AI可调整脚手架”不等于可以绕过宿主许可。纯计划不触碰调度器；实际调度变更必须有宿主读回。

### D. 数据流与合并门

1. 真实需求 → 查同域经验/当前上下文 → 记录可检验缺口与第一判断。
2. 若有知识/方法缺口，检索可信源 → 写来源卡 → 通过一个微任务检验理解 → 写有限课程计划。
3. 用同任务约束写G、D两种假设；每种只改一个可归因主因，baseline保持。
4. 对B/G/D分别实跑；观察完整产物与失败；有互补收益才提出C；C另跑，不复用两边分数伪造。
5. 开发任务用于改候选；封存任务隔离，只让独立评估者核验；原有能力回归始终保留。
6. 同一任务硬门全部通过后，比较质量-耗时-成本：先质量不回退，再在同等质量下看速度/成本。若只提高质量却更慢更贵，透明呈现取舍，不编造全面提升。
7. 将采纳候选写入versioned Skill；经验条目标明适用范围、负例、证据和复习条件；新会话必须能实际调用。
8. 下一实际任务验证迁移；迁移失败降级或回滚，不继续把provisional称mastered。

## 项目筛选规则与退出条件

每个候选都回答：它补哪个可复现缺口？官方源码在哪里？许可证按文件是否清楚？是否与 Markdown 真相源冲突？是否默认联网/上传？当前平台是否支持？如何卸载与撤销？哪一条真实测试可以判失败？

硬拒绝：许可证/源码不清；要求偷偷迁移记忆；必须训练权重；只有营销演示没有可观察接口；用删失败记录换“干净指标”；没有任务边界地永久后台跑。

先做最小adapter，最多引入一个不可替代运行依赖。若同样功能能由现有工具可靠完成且无可测收益，不新增框架。维护活跃/星数只作背景，不能替代能力、兼容、许可与成本证据。

## 具体实验建议（非执行记录）

- 领域A：修复一个独立小工具的真实输入边界缺陷，交付补丁、正反例、回归结果与安装可用性。迁移题换一种输入编码或不同调用方，检查它是否理解因果而非背测试。
- 领域B：针对公开官方文档写一个中文操作教程，另一独立Agent只看教程完成任务并产出文件。课程讲解、事实来源、用户可操作性与实际执行成功分别打分。
- 每领域B/G/D/C同一冻结任务输入与工具预算；若G在两个领域都有效才扩大为通用经验，D仍限定领域。
- 计划至少2个真实任务用于初步探测，但2个任务不能证明跨所有领域精通或显著提速；记录样本数、波动、全部失败和人工帮助。没有实际计费回执时只报token和时间，不换算“节省成本”。
- 复习到期要由真实时钟与宿主事件触发，教材文件中的日期变化不算唤醒。教学成功要看学习者新题/实操，不看老师自评。

## 一次完整的采用与回退示例

以下是**设计示例，尚未执行**。目标是修复“后台复盘写出一条经验，但下次新会话未使用”的缺口，任务成功标准是新会话完成同类任务并正确引用原文件，时间与成本记录完整。

1. **发现与定位**：先核本项目失败回执，确认源文件存在、检索未命中；查 Letta Code 的记忆整合方法与 LangGraph 的 checkpoint/store 区别。把资料记录为研究来源，不直接安装服务。
2. **提出可证伪改法**：G 为“所有经验写明适用条件和负例”；D 为“本项目 Windows 交接经验加入平台/权限标签”。固定 baseline、memory revision、冻结任务、公开 rubric 与最大实验预算；检查现有授权涵盖隔离本地文件试验。若需要新远端服务或付费账号，再请求该具体额外权限。
3. **准入试验**：在各自隔离的副本执行 B/G/D，保留原始输出与完整质量、耗时、token；新会话读取同一套 Markdown 契约。遇到 Letta Windows ARM64 分发不支持时，将该第三方运行适配器记为 unavailable；这不是我们提议的记忆规则已失败，也不能伪造其运行结果。可继续用已支持的现有宿主测试独立规则。
4. **形成组合**：若 G 改善来源归属、D 改善召回且回归无损，再生成 C。C 必须另跑一次新会话，不能把两条正例拼成它的成绩。
5. **真实失败后的回退**：假设 C 造成过期经验优先于用户新指令，立即拒绝 C，恢复此前版本；保留 C 的失败回执，经验标 needs_review，记录冲突规则修复方向。不得调低“尊重当前指令”的硬门来使 C 合格。
6. **沉淀与下一步**：只有实际通过的 G 或 D 可在它被测过的范围内 provisional 采用；尚未测试跨领域迁移，不写“通用精通”。下次真实任务记录引用行为；复习日期只是计划，宿主调度真实绑定和触发回执是另外的验收。

这条链的收益来自能归因、能拒绝和能撤销；没有收益的框架接入应停止，不让接入成本变成继续堆功能的理由。

## “纯自研”的具体表达

可以准确表述“核心编排、Markdown知识契约、能力证据模型、晋升/回滚与评估流程由团队独立实现，并引用公开研究与开源协议”。不能把参考论文写成我们的原创理论，也不能实际调用开源框架后宣称零第三方。

若只研究机制：保留引用，不复制源码、品牌、整篇文档。若以后真实引入依赖/复制片段：固定版本、保留该许可证/版权/NOTICE和改动说明，记录依赖清单。本报告不是对全部未来组合的法律兼容性结论；团队现有AGPL主许可不抹除第三方许可。当前没有新增第三方运行依赖。

## 核查回执与局限

实际通过GitHub连接器读取10个主项目的README与许可证，并在随后取得的main commit上再次读取相同文件，blob SHA全部相同（20/20）；另核实Letta旧仓迁移声明与DSPy/GEPA特定接口文档。只报告已读资料；没有运行第三方安装命令、没有复制第三方实现到本项目。

实际失败与修正：mini-swe-agent LICENSE 404后读LICENSE.md成功；mini architecture旧URL不可访问，使用官方README而不杜撰页面内容；DSPy docs跳转只显示Continue，改读官方仓库同路径源码；Inspect旧limits URL重定向无正文，跟随官方目录到setting-limits成功。

| 项目 | 核查 commit | 回读文件 blob SHA（Git对象ID，不是文件SHA256） |
|---|---|---|
| langchain-ai/langgraph | `3c916d750575b22c464790e9774494d810ccd322` | README.md: `97c31e9cb4d8fe56be8d768ce3eb5e22400e897e`<br>LICENSE: `fc0602feecdd6748623c852ab534e1ca612673c7` |
| letta-ai/letta-code | `9df436cffa588f45aadef86f34d43fb8f3008c40` | README.md: `6b09e6cf359981d7c2a6c225a6fa1b8617a8435b`<br>LICENSE: `e72f5de5dd5610ee3fee7feb791ebff246cc931e` |
| stanfordnlp/dspy | `c8176a8fa65e9772d9d44a33f464f4271c97b806` | README.md: `f92d3311e085fed87af6c724b2d43e2076b57cc6`<br>LICENSE: `be3f5c0e3fc7e6b0e7c9dddd9db313ab15bfa62b` |
| gepa-ai/gepa | `8c7b697a71977980afc7537dac0881e784eef99f` | README.md: `365edf3d878f6996259cfc95c401547825fdc65b`<br>LICENSE: `a2d71aed19ccc43d94b9c3afe6430da9b2277f32` |
| OpenHands/OpenHands | `7f6c52f8ea7187249dfe1b363a4c1efbfa9a6bc6` | README.md: `d2c59eb5c77b9afed050b5a2e28b79317f7fab18`<br>LICENSE: `f6f60f52368bcc96f82fbe59ec65049c2c3af9db` |
| SWE-agent/mini-swe-agent | `04d809ceab9df28f9adaed044884180159172930` | README.md: `7db1d82dfa92eaa00adeb10c8681677a9e6ec639`<br>LICENSE.md: `503821c9dbe06f13a48e54088eb6cd203adb407f` |
| UKGovernmentBEIS/inspect_ai | `706b4c5d6a3af83150ae3fc66ddf84b6bc37f50f` | README.md: `0a035b0ca7039767517be2e50a60e1b034a3c1d4`<br>LICENSE: `72fc87742ef8a944fab4f28fe6231696c62f2fa4` |
| promptfoo/promptfoo | `f2b012e3c9f9ffb7b23edf4cf88ea63febf72f5a` | README.md: `2a56017c2609e3a92d7d5539147c9c7e620a3420`<br>LICENSE: `af3fa111d9303b3041d225fb851534e50a4bbec2` |
| modelcontextprotocol/python-sdk | `d7845c073a2b9ba5ab2817ecf93d3e45ef24cd14` | README.md: `50ea0ed227b72de82917d67d678d1d24783ab2e9`<br>LICENSE: `3d48435454b105021b4f777c11b6b07d8d2ffea3` |
| microsoft/autogen | `d07c667a3239ea4ab7af62a53b0f4ff205a1f23d` | README.md: `042b9df197a220ec7072a116d694cd497ec332ad`<br>LICENSE-CODE: `9e841e7a26e4eb057b24511e7b92d42b257a80e5` |

所有框架的有效性能、真实互通、后台唤醒与多平台行为仍需本项目单独执行验收。本轮研究成果不能计入这些能力的PASS。

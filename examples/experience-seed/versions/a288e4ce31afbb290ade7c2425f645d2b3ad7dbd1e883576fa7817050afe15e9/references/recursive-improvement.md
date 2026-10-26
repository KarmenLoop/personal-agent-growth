# Propose–Probe–Compose 与双层递归

在用户启用本模式后应用于每个新任务。读取宿主实际提供的工具和执行能力，再按本协议运行。没有可运行的执行方时保存未执行状态；文件准备、模拟回执和比较程序本身均不算 Agent 实跑。

## 固定什么、允许改什么

固定模型标识、可见采样配置、任务输入、预算和本轮验收依据。全程不调用训练、微调、梯度、参数更新或强化学习接口。云模型通常不暴露权重哈希：记录可见模型配置与供应商版本，不声称独立证明了服务端权重恒定；版本未知或运行中变更时不能把差异全部归因于外壳。

可变部分限于用户授权的外壳目录：求解提示词、候选生成提示词、工具代码与接口描述、上下文整理、经验检索和路由、停止与恢复策略。宿主的系统指令、用户权限、账户凭据、预算上限、验收程序和本轮输入保持在候选外。修改候选生成器也要经过后面的跨任务验证；它不能替自己改变验收门槛。

用户启用此模式即授权 Agent 在这些组件内提出、修改、试跑、选择、启用和回滚，无需为每条运行规则再询问。把授权根目录与当前版本写入任务状态。

| 可调整组件 | 从何种瓶颈出发 | 需要观察什么 |
|---|---|---|
| 提示词、技能选择、任务解析规则 | 反复误解、遗漏步骤、重复提示 | 相同目标的行动和产物是否改善 |
| 工具实现、调用接口、批处理和缓存 | 重复启动、冗余 I/O、低效工具链 | 调用数、输入归属、缓存失效与错误传播 |
| 上下文、记忆检索、摘要与路由 | 读太多无关资料、丢失决定、恢复错误 | 有效读取、遗漏、跨回合恢复及成本 |
| 分工、串并行、重试与停止规则 | 等待浪费、重复执行、任务互相覆盖 | 完整轨迹、共享写入、失败恢复及总开销 |
| 后续调度、预习与复习策略 | 无收益唤醒、学而不用、同错重犯 | 实际触发、实际应用、错误复现与解决 |
| 提案生成器、比较与组合策略 | 改法雷同、只堆提示、迁移失效 | 下述任务组合的真实结果与回归 |

调整宿主自建的工作规则、工具包装和插件配置时同样遵循本协议。运行外壳中有些内容也叫 system prompt 或 guardrail，只有项目自行拥有、用户授权可编辑的文件才属于候选；当前会话更高优先级指令和安全限制不因文件命名而成为可改组件。预算可在总额度内重新分配；未来唤醒通过宿主正式接口真实登记并核验。只有涉及新的用户取舍、权限范围或预算上限时才联系用户。

记录可观察的行动轨迹：读了什么、工具输入、返回与失败、公开的简短决策依据、输入输出身份及下一步。无需记录模型隐藏推理。

## 第一层：把一个任务做好

一次用户任务只有一个实验协调者。原版和两个候选是同一实验的执行叶子，继承实验 ID 与剩余额度；它们执行已冻结的方案，不再次生成三路实验。这样两层递归不会在每个子任务中指数展开。

1. **恢复基线。** 从任务状态和经验库读取当前有效版本、适用领域与失败教训。保存模型配置、输入哈希、外壳文件快照、已有授权和可观察指标。基线包括上个任务已接受的改动，不每次退回初始版本。
2. **Propose：先写两份改法。** `general` 针对可迁移的短板，例如证据归属、无效工具调用或恢复错误；`domain` 针对本任务领域，例如归档批量检查或专业资料检索。每份包含观察依据、具体修改、预期效果、可能退步之处、适用条件和否决条件。两份都从同一基线派生，避免第二份偷用第一份结果。没有已证实短板时明确标为探索假设，仍实测，不能虚构失败。
3. **冻结试验。** 保存两份完整候选、任务输入和验收程序，再运行 `scripts/compare_trials.py freeze <experiment>`。冻结后改动这些文件就是新一轮，保留上一轮记录。先写预测再执行；事后形成的解释另行追加。
4. **Probe：三路实跑。** 原版、通用候选、领域候选分别完成同一个有用任务。使用新上下文或清晰隔离的执行目录、相同可用工具与预算；每路只加载自己的候选。保留原始工具回执和产物。执行顺序轮换，缓存、登录、网络和机器负载差异需要记录。候选出错时保留原尝试；修复消耗本轮预算，不把修复前失败移除。
5. **比轨迹与产物。** 候选不能负责给自己打最终分。由固定验收程序和负责验收的宿主核对行动、输入归属及产物，再保存 `evaluation.json`。运行 `compare_trials.py compare <experiment>` 检查记录完整性并按预先规则比较。脚本不能从 JSON 自称证明 Agent 身份；宿主仍需核实原始执行。
6. **Compose：有用才组合采用。** 所有必要质量约束通过，且修复了原版真实失败或指定指标超过预设最小改善量，才可成为候选胜者。更快但质量不合格的版本拒绝。两份都有效时先启用一个经过测试的完整版本；组合两份需要另跑组合版，不能把两个单独通过等同于组合通过。平局、缺证据和信号冲突时继续使用原版。
7. **回到用户任务。** 在当前授权范围使用选定的产物，记录先前判断、触发改判的证据和后继。外部发送、部署、删除等副作用只执行一次；双路比较使用隔离副本或可重复的只读阶段，不重复真实付款或发布。

默认一个任务最多两轮候选实验；开始前按任务成本记录实际轮数、工具次数、时间或 token 上限。超出已批准预算时交付当前最好结果与未验证候选。新实验不能递归地给自己无限扩预算；这些上限不替代宿主实际的执行限制。

### Compose 的执行契约

先逐项对齐三路轨迹中的“观察 → 原动作 → 候选动作 → 结果 → 代价”。`compose-plan.json` 的每个决定写 `component`、`source`（baseline/general/domain/new）、`action`（keep/drop/rewrite）、`reason` 和实际 Probe `evidence` 路径。没有收益的候选可以全部舍弃；Compose 不要求强行把两份内容拼接。对存在冲突、先后依赖或失败的新组合，退回最佳已测版本。

将后继完整外壳放在 `arms/composed/`，用 `freeze-compose` 在执行前绑定三路原证据、组合决定、组合验收适配器和组合快照。适配器沿用原任务、质量条件、模型配置与指标，仅允许改变执行路径以检查组合版；不能换一套更容易的验收依据。新 Agent 实跑后，保存 `runs/composed/run.json` 与 `composition-evaluation.json`，两者都附 `composition_sha256`。后者与原 `evaluation.json` 结构相同，`arms` 仅含 `composed`。

再次 `compare` 时同时核对组合证据。组合版必须通过原质量约束，对原版确有收益，且指定指标不比最佳已合格候选差，才允许 `record --activate composed`。已冻结但未实际执行的组合不能采用。原版和两份候选的记录保留。

## 不看标准答案，怎样判定

不向求解器、改进器或评估器提供预写的答案、隐藏测试标签或事后补的成功条件。使用本轮开始前固定、可观察的约束：

| 信号 | 用法 | 结论范围 |
|---|---|---|
| 输入输出身份、结构与约束 | 哈希、schema、资源引用、数量守恒、必需字段、执行退出状态 | 验证具体约束，不把格式正确等同于内容正确 |
| 环境反馈 | 实际工具结果、编译器、运行时、用户已给定的接受条件 | 与该环境和任务绑定 |
| 变式关系 | 搬迁路径、置换等价输入、去重、往返恢复、同一结果复用 | 检查关系是否保持，无需答案标签 |
| 独立重用 | 另一个执行方使用产物完成新任务 | 比只复述报告强，但仍需检查实际产物 |
| 开放问题 | 盲化候选名称、按固定维度复核来源和遗漏；交换呈现顺序 | 判断有分歧时保持未决，不靠文风或自评分升级 |

同一模型的多次赞同不是独立真值。完全没有可验证反馈的任务，不宣称“质量已提升”；经验以待验证假设入库。本模式不保证每个任务都产生有效改动。

## 效率要算哪笔账

先选指标及单位，再取数：成功率、有效产物、工具调用/进程数、token、费用、耗时分别记录。计时比较至少三次，使用相同任务的配对重复；单次快慢不作为稳定加速证据。模型调用量不可见就写未知。

完整任务从执行方启动计到最后产物交付与退出，包括读记忆、模型回合、工具、失败重试、报告生成和自检。不要把最后一次成功的工具时间当作 Agent 总耗时。不同领域分别留样本和质量检查，不能用平均质量掩盖一个领域的失败，也不能把快任务的收益抵消另一个任务超过事先允许范围的退步。三次重复只支持本次探索性比较，不能据此宣称稳定的普遍加速。

预算给计算、交付、自检和宿主结束回执都留出时间。产物已存在但执行回合被截断时，保留产物和中断原因，不能补写一次正常结束；未返回的原生用量保持未知。确需修改截止时间或任务输出约束时，另建冻结实验，所有策略使用同一新条件，不能只延长落后策略的时间或把两轮结果混算。报告只保留完成判断所需的证据，原始轨迹另存，避免重复抄写经验库。

宿主能导出原生用量时保存原始事件，再统计输入、缓存输入、输出和总 token；缓存输入通常已包含在输入量内，不能重复相加。共享缓存的命中率会随顺序变化，保留各次命中量并轮换顺序。token 减少不直接等于账单金额减少；订阅费用或供应商实际计费不可见时金额用 null。准备候选、试跑失败、组合复验和后续复用分别记账；无法取得协调者的消耗时，已测总和只是下界。

在 `plan.json` 增加 `performance_guards` 可冻结次级资源约束，例如 `{"release_tokens": 0.15, "analysis_wall_seconds": 0.20}` 表示对应任务的 token 中位数最多增加 15%、耗时中位数最多增加 20%。每路验收行保存同名 `guard_samples` 原始测量数组，长度等于 `samples`；包含耗时时至少三次。未知、缺样本或超界的版本不能采用，即使主指标改善或修复了其他质量缺陷。组合版也受同一组约束。阈值由任务价值在试跑前确定，不能看完结果再放宽。

同时保存 UTC 开始/结束时间与单调计时读数。宿主休眠或时钟调整可能使两者不一致；无法解释差异时保留两种原始值，对该耗时样本填 null，不自行扣掉等待，也不认定它属于策略退步。明确为 null 的候选资源样本使该候选保持未决，不妨碍其他证据完整的候选比较；基线资源未知则对应比较均不能升级。不要删掉异常样本后把剩余两次叫作三次重复。

区分三种成本：选定版本执行任务的成本、生成两份改法和三路试跑等优化开销、后续任务的实际复用成本。局部进程从三次变一次，不等于 Agent 总成本下降三分之二。记录预计回本次数时标明预测；积累后续任务的实际数据后再计算累计净收益。总成本字段缺失时，脚本只给指定指标的比较，不输出“整体效率提升”。

## 第二层：让后续所有任务受益

每个任务结束时把接受、无效、失败和未决经验都入库。每条记录保留触发条件、因果假设、所改组件、冻结基线、三路轨迹、验收结果、实际成本、反例、适用范围、失效条件和回滚版本。按领域和失败机制索引；新任务只读取相关经验。

另写 `reflection.json`，将经验整理成可用于生成下一轮改法的操作：`trigger`、`bottleneck`、`intervention`、`evidence`、`observed_result`、`scope`、`invalid_when`、`next_probe`。区分实证经验与新假设，保留无效改法和新增的回归风险。`record` 把该反思及哈希、两份原提案、比较结果和组合决定保存到经验卡。`select` 返回相关经验卡路径，宿主必须读卡并在下一份 proposal 中说明采用或拒绝的依据；仅列出路径不算形成元能力。

`compare_trials.py record <experiment> --library <private-library> --expected-revision N` 保存经验。加 `--activate general` 或 `--activate domain` 时仅启用该任务领域下已通过的完整快照；先用 `select --library <private-library> --domain <domain>` 读取当前修订。该命令写的是受管经验库，不会改宿主全局 system prompt、安装目录或启动后台服务。更新后回读 library revision 与版本哈希；外部宿主必须实际读取返回路径才算复用。

跨任务层不能止于归档：根据多个任务中的重复失败，提出对**候选生成器、经验检索、领域路由或预算分配策略**的修改，再在任务组合上比较原策略与两份候选。至少覆盖两个不同任务；提升为通用规则时再覆盖两个领域并包含原先成功任务的回归。开发中已经看过的案例与新的迁移案例分别标记。策略改动仍遵守同一个冻结模型和验收锚点，不继续增加第三层无限递归。

跨任务实验在 `plan.json` 中设 `layer: harnessing`，`portfolio` 至少列两个不同的 `task_id`，各自写 `domain` 与 `role`（development/transfer/regression），必须包含新迁移任务和已有成功任务回归。全局推广再设 `promotion: cross-domain`，至少覆盖两个领域；程序在冻结时核对这些声明，宿主和固定验收器负责检查各任务真实运行证据。外层可使用单独领域键，例如 `meta:archive-workflows`，保管提案生成、工具匹配和 Compose 策略版本；内层用当前领域键保管执行外壳，避免相互覆盖。

当前脚本保管按领域及策略键划分的完整版本；跨领域经验只作为下一轮候选来源，尚不自动替换全部领域。通用候选的名字表示意图，不表示已经证明普适。跨领域推广由宿主执行上述任务组合试验并保存各任务证据；不能用一次本地通过换取全局启用。

库采用一个写入方、显式修订号和不可变快照。接续任务先查原状态再加载版本。新版本失败时按记录选择前一完整快照，在新修订中记录回退原因；保留失败版本与轨迹。冻结输入或原始回执缺失时停止升级，实际用户任务仍可用已验证基线继续。

采用后的实际复习与迁移观察也要回到索引。独立核验后写 review JSON：`observation_id`、`domain`、实际使用的 `active_sha256`、`lesson`、`limitations`、`next_probe`，以及 `evidence`（本机绝对文件路径到 SHA-256 的映射）。用 `observe --library <library> --review <json> --expected-revision N` 追加不可变观察并增加修订号。它核对证据和当前版本，不替代宿主的真实性与语义验收，不会擅自采用另一个版本。后续 `select` 返回 `experiences` 和 `observations`，两者都按相关性读取。历史经验不因复习失败而被抹去。

## 文件契约与使用

每个实验使用独立目录：

```text
experiment/
  plan.json
  proposals/general.md, domain.md
  arms/baseline/, general/, domain/  # 三个完整外壳快照
  inputs/                           # 同一份只读任务材料
  evaluator.py                      # 本轮冻结的验收逻辑
  frozen.json                       # freeze 生成
  runs/<arm>/run.json                # 实际执行身份、轨迹和输出引用
  evaluation.json                   # 独立验收方生成
  compose-plan.json                  # 组件保留、舍弃、改写及 Probe 证据
  arms/composed/                    # 可选，组合后的完整快照
  compose-frozen.json               # freeze-compose 生成
  composition-evaluation.json       # 组合版实跑后的独立验收
  reflection.json                   # 给下一轮提案使用的经验与反例
```

`plan.json` 的必要字段：`experiment_id`、`task_id`、`domain`、`model_config`、`quality_checks`、`metric`、`min_relative_gain`、`samples`、`max_candidate_cost`、`inputs`、`evaluator`。`model_config` 保存宿主可见配置，并包含 `training: false`。`inputs` 是相对文件路径列表；`evaluator` 是验收程序相对路径。两个 proposal 文件应非空。计时指标以 `wall_seconds` 命名。

每路 `run.json` 保存相同的 `model_config`、`frozen_sha256`、`executor`（`kind: agent`、真实宿主和会话 ID）、`trace`、`host_receipt`、`artifacts`。后面三项引用均在本实验内；原始回执必须非空。宿主无法导出原始事件时，把协调方实际观察与执行方声明分开记录，不能伪造导出文件。

`evaluation.json` 顶层保存 `frozen_sha256`、`reviewer`、`optimization_cost` 与 `arms`。`arms` 按 baseline/general/domain 分组，每路包含 `run_sha256`、`evidence_sha256`、`checks`、`metric_samples`、`evidence`。`evidence_sha256` 必须逐项覆盖该路 run 中的 `trace`、`host_receipt` 和全部 `artifacts`，格式为相对文件路径到 SHA-256 的映射；`run_sha256` 绑定该路 run.json。`checks` 的键与 plan 的质量条件完全一致，值为 true / false / null；`metric_samples` 是实测非负有限数数组。`evidence` 引用实际验收输出。`optimization_cost` 无法测量时用 null，不能用 0 代替未知。宿主适配器生成这些文件；比较器只检查契约和归属，不替代语义验收。

```sh
python3 scripts/compare_trials.py freeze /path/to/experiment
# 真实执行原版与两份候选，然后保存独立验收
python3 scripts/compare_trials.py compare /path/to/experiment
# 组合改变组件时，先保存 compose-plan.json、适配器和完整快照，再冻结并实际复验
python3 scripts/compare_trials.py freeze-compose /path/to/experiment
# 保存组合版真实 run.json 与 composition-evaluation.json 后再次比较
python3 scripts/compare_trials.py compare /path/to/experiment
python3 scripts/compare_trials.py record /path/to/experiment \
  --library /path/to/private-experience --expected-revision 0 --activate composed
python3 scripts/compare_trials.py select \
  --library /path/to/private-experience --domain offline-package-check
# 只有该次采用仍是当前版本时，才能按记录回退；先读取当前库修订号
python3 scripts/compare_trials.py rollback --library /path/to/private-experience \
  --experiment-id experiment-id --expected-revision 1 --reason "Observed regression"
```

Windows 使用 `py -3 -X utf8`。退出 0 表示记录有效（可能没有胜者），退出 2 表示记录缺失、发生漂移或调用失败；成功退出本身不表示改进有效。`record` 没有 `--activate` 时只保存经验。

机制参考：[Harness² 官方仓库](https://github.com/google-research/harness2) 与 [原论文](https://arxiv.org/abs/2610.14224)。此 skill 独立实现其 Propose–Probe–Compose 和双层经验反馈思路；额外使用固定质量约束、组合复验、修订检查及回滚。没有集成上游运行器，也不沿用其基准成绩作为本项目验收。

<!-- Copyright (C) 2026 KARMENLOOP Official Team
SPDX-License-Identifier: AGPL-3.0-only -->

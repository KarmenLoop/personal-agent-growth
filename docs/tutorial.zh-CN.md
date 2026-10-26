# 从安装到预习、复习与跨工具接续 · 0.4.1

[English](tutorial.en.md) · [安装](install.zh-CN.md) · [判断方法](reasoning.zh-CN.md)

本教程给出可执行的验收任务：**检查当前发布包，生成可复用交接验收卡，再让第二宿主在搬迁后复用它。** 这里是教程，不把尚未执行的步骤写成运行结果。使用真实包；反例只在独立测试副本中创建。

## 1. 准备三个位置

确定 `<SKILL>`、`<LEARNING>`、`<TASK>` 的绝对路径，分别保存技能、私人 Markdown 知识、输入与原始回执。新项目 ID 例如 `handoff-review`。不要把真实用户记录提交到公开 GitHub。

先读取 SKILL 和 [Markdown 协议](../references/markdown-learning.md)。按[模板](../templates/learning/README.md)建立 policy、index、project memory/context/初始节点。填入目标、约束、验收条件、writer；只在真实观察后填写结果。

## 2. 先保存判断和预测

给 Agent：

> 完成当前发布包交接验收。先读项目 context、最新 node 和 memory，记录实际读取身份。预测当前 ZIP/manifest 是否一致，以及这一结果能证明什么、不能证明什么。接收方需要搬迁后继续使用；列出决定性的未知，先查格式与引用规则，再实际检查。产物为验收卡、命令/输出/退出码、输入哈希、当前结论和下一复习动作。可自行解决的问题先完成，只在需要我取舍时联系。

有效的预习问题是“检查器的退出 2 属于哪一阶段”“相对资源如何从当前文件解析”，而不是无用途地总结全部工具文档。预习结果附来源、适用范围及下次验证。

## 3. 实际执行并保留失败

在真实工具中运行，替换占位符：

```sh
python3 -B <SKILL>/scripts/verify_handoff.py \
  --archive <TASK>/inputs/personal-agent-growth-0.4.1.zip \
  --manifest <TASK>/inputs/manifest.json
```

Windows 用 `py -3 -B -X utf8`。保存完整命令、stdout/stderr、退出码、UTC 与单调耗时（宿主支持时）、输入/程序哈希。退出 0=一致，1=已检查发现不一致，2=未完成检查；它不认证发布者，也不证明所有资源实际可用。

另复制到受控目录，删去测试副本的一个输入，再调用检查器。预期是未完成检查而非归档内容不合格。保留这次尝试，恢复正确输入后重新核对原包。不要改发布原件。

## 4. 补课与改变判断

将观察对照预测。若错误是路径不存在，就补路径映射；若引用只在旧位置有效，就补搬迁检查。把“原判断—新证据—改判—方法修改—复测”写入 node。只有长期有效事实进 memory。

验收卡包含对象版本、环境、到达阶段、原始证据和结论边界。若只是 ZIP 一致，卡片不能写“第二工具可继续运行”。写入候选经验，validation 起初 untested；实际应用后改 local，并保留反例与失效条件。

## 5. 停顿和换工具

原宿主刷新 context，新增 node，列出下一步“从新位置复用验收卡与检查器”，保存所有产物身份，将 writer 交给接收方并增修订。第二宿主使用同一个 LEARNING/TASK：

> 从同一学习根目录恢复 handoff-review。先读 context 与最新 node，再读 memory；核对当前修订与 writer。实际复用上一轮产物，把隔离副本移动到新位置，并确认旧位置不可继续供应测试资源。执行有意义的复习变式，记录真实读取集、新结果、判断是否变化和下一动作。写回原目录，不另建一份状态。

核对接收方真实 Agent 回合、文件哈希、工具返回和新修订。两个 Python 测试进程可以验证文件协议，但不能替代这一步的真实 Agent 行为。若设备不可用，保留待恢复位置，不编造完成。

## 6. 日周闭环与后续调整

当天日报链接两个节点、知识变化与失败原因。周结读取整周日报，找重复问题；次周一检查经验是否真正用于后续工作，并更新 preview。若经验未再使用，只标待验证。

有具体未来用途时，请宿主登记一次有期限和轮次的复习，实际回读绑定。收到真实事件后执行并复核；通过则停止，失败则明确一次补课动作。调度与通知遵循已有联系偏好。不能通过保存一个计划宣称已经定时运行。

## 7. 启用双层递归

在新实验目录提出 general/domain 两份改法；固定模型配置、输入、质量与预算。基线和两候选分别完成整个任务，而非只运行检查器。保存原生回执、完整产物、质量、耗时、token 与未知费用。组合改了组件就独立复跑。

```sh
python3 -B <SKILL>/scripts/compare_trials.py freeze <EXPERIMENT>
python3 -B <SKILL>/scripts/compare_trials.py compare <EXPERIMENT>
python3 -B <SKILL>/scripts/compare_trials.py freeze-compose <EXPERIMENT>
python3 -B <SKILL>/scripts/compare_trials.py compare <EXPERIMENT>
```

这些命令需要事先准备的真实文件契约与运行结果，不会启动 Agent 或替你构造成功记录。完整格式、record/select/observe/rollback 见[递归协议](../references/recursive-improvement.md)。原始 JSON 实验作为证据，学习结论写入 MD 经验并链接来源。外层换领域与原任务回归后才推广生成/路由策略。

<a id="adapter"></a>
## 8. 既有五工具交接适配器（独立可选模式）

此模式用于已有 SQLite 检查点工作流，根目录与 Markdown 学习区分开。先创建 workspace，再运行：

```sh
python3 <SKILL>/scripts/host.py --root <PRIVATE-STATE> --workspace <PROJECT> --install-host codex install
python3 <SKILL>/scripts/host.py --root <PRIVATE-STATE> --workspace <PROJECT> --install-host cursor install
```

它只新增该项目 `.codex/config.toml` 或 `.cursor/mcp.json` 的对应条目，已有同名条目则拒绝。重载宿主，按其要求授权，确认五工具可见：

| 工具 | 输入要点 | 作用 |
|---|---|---|
| growth_start | task_id、goal、acceptance | 创建 durable task 与当前 writer |
| growth_read | task_id | 恢复状态并核对现存产物哈希 |
| growth_checkpoint | expected_revision、phase、next_action、artifacts、observation | 当前 writer 提交新检查点 |
| growth_handoff | expected_revision、target_host | 证据有效时移交 writer |
| growth_export | task_id | 导出私有 JSON 交接文件 |

在 Codex 创建 task，实际做一步，checkpoint；handoff 到 cursor 后，让 Cursor read、核对、继续并 checkpoint。旧 writer 写入被拒绝，陈旧修订要求重新读；产物变更则 evidence_current=false，先复核再交接。

直接命令行检查可用 `host.py --root ... --workspace ... --host-id cursor call growth_read --input request.json`，其中 request 为 `{"task_id":"your-task-id"}`。这验证存储/接口，不证明 Cursor 模型已消费工具。schedule 字段保持 not_registered，适配器本身不调度。

## 9. 完成时应该得到什么

应有：带来源的验收卡、真实命令输出、预测差异、复测结果、一个可恢复项目包、带边界经验、实际读取集，以及确有未来用途时的宿主绑定回执。没有取得的 Agent、设备或调度层证据明确为 NOT_RUN。只有目标与当前验收证据一致，才写 summary 并标 done。

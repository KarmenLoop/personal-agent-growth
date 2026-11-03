# 能力学习使用教程 · 0.6.1

[English](capability-learning.en.md) · [运行协议](../references/capability-learning.md) · [教育研究](learning-science.zh-CN.md)

本轮在现有 Skill 上新增可执行的能力证据账本。工具使用 Python 3.11+ 标准库，无 pip 依赖；不会自动安装私有 Koder 学习 API，也不代替真实 Agent 或启动后台任务。

## 绑定同一份记忆

明确选择现有学习根目录，各宿主绑定同一个物理位置。两份名称相同的复制目录不算共用记忆。新增目录与原日、周、项目、用户记忆并存：

```text
learning/
  projects/<project-id>/context.md
  projects/<project-id>/nodes/...
  experience/...
  capabilities/<capability-id>/
    capability.md
    attempts/000001.md
    attempts/000002.md
  evidence/<task-id>/...
```

能力语义只存 Markdown；`status` 每次从当前文件重建，输出 JSON 只是报告，不是第二套可写状态。临时文件和排他锁只处理事务。原始产物可以是代码、数据和命令输出，Markdown 记录其路径及 SHA-256。

重要回执使用不可变副本。证据文件变了，状态读取会拒绝沿用旧验收；不要把下一步会覆盖的项目摘要作为不可变证据。

## 建立真实学习任务

在 Skill 目录执行，macOS/Linux 示例：

```sh
python3 -B scripts/capability_ledger.py init \
  --root /absolute/path/to/learning \
  --id release-verification \
  --goal '验证交接包并教会另一执行者复用检查方法' \
  --domain software-release
python3 -B scripts/capability_ledger.py status \
  --root /absolute/path/to/learning --id release-verification
```

Windows 改用 `py -3 -B -X utf8`，换成实际 D: 或 C: 根目录；命令放在一行，或使用 PowerShell 的续行语法。先核实选中的 Python 至少为 3.11。该工具不请求提升权限。

初始化不会授予能力。先保存预测，再读直接需要的资料，随后执行小而真实的任务。记录通过前，由另一个负责的执行者检查产物。同一个操作者填写两个身份字符串不证明独立审阅。

## 写入观察

观察文件使用 **JSON 形式的 YAML 1.2 文首元数据**。这是标准库可读取的受限格式，不支持任意 YAML 写法。下面必须替换为实际数据；时间使用 UTC，不得早于初始化或晚于真实当前时间。

```markdown
---
{
  "id": "apply-release-01",
  "kind": "apply",
  "task_id": "release-task-01",
  "executor": "真实宿主/真实会话",
  "reviewer": null,
  "outcome": "unknown",
  "observed_at": "2026-11-03T08:00:00Z",
  "summary": "执行输出已保存，内容还待独立检查。",
  "artifacts": [{"path": "evidence/release-task-01/result.txt", "sha256": "替换为真实64位小写sha256"}],
  "cost": {"wall_seconds": null, "tokens": null, "usd": null}
}
---
## 实际情况
实际命令、观察结果、限制、下一项检查。
```

macOS 用 `shasum -a 256`，Linux 用 `sha256sum`，Windows 用 `Get-FileHash -Algorithm SHA256` 计算实际哈希。示例不能原样通过。费用和用量缺失就保留 `null`，不估成零；每条观察只记互不重叠的增量成本，同一次执行覆盖多个维度时不得重复加入整场会话成本。

```sh
python3 -B scripts/capability_ledger.py record \
  --root /absolute/path/to/learning --id release-verification \
  --observation /absolute/path/to/observation.md --expected-revision 0
```

下一次写入前重新读 `status` 并使用当前修订号。被拒绝的写入不增加修订。陈旧写入必须先核对当前事实再提交，不盲目循环重试。事件 ID 不重复，失败历史不删除。

## 各维度的实际条件

| kind | 写通过前必须审阅的证据 | 额外字段 |
|---|---|---|
| `explain` | 来源支持的解释、机制与假设 | 无 |
| `apply` | 真实工具执行和可用产物 | 无 |
| `counterexample` | 条件改变、事先预测及实际结果 | 无 |
| `transfer` | 新任务中的实际复用 | `source_attempt` 指向先前通过的 apply；task_id 不同 |
| `teach` | 教材和另一个执行者独立完成的产物 | `learner`、不同的 `learner_task_id`、`learner_artifacts` |
| `deliver` | 完整用户目标，而非局部子测试 | 无 |
| `recall` | 真实时间间隔后的闭卷提取与检查 | `source_attempt`、`no_answer_visible: true`；至少24小时 |
| `regression` | 原能力在原有条件下仍通过 | 无 |

工具检查一致性，不能判断概念是否正确。即使格式通过，审阅者仍须拒绝没有根据的内容。`pass` 必须有不同 reviewer 和非空且哈希吻合的产物；教学时学习者必须区别于教师及审阅者，任务与产物哈希也须不同。哈希无法证明学习者真的看过教材，要另留宿主/工具回执。

这些维度不代表通用智力。没有教学证据不妨碍先交付有用任务；完整范围内验收要求相应维度均满足，没到真实复习时间不能用单元测试的模拟时钟变成通过。

## 复习、补课和真实唤醒

```sh
python3 -B scripts/capability_ledger.py due --root /absolute/path/to/learning
```

失败提出补课，未知提出核验；通过按初始1/3/7天策略提出复习。这是可解释的工程启发式，不是已证明适合所有模型的最优间隔。内部初始化 API 可设更严格的初始策略，CLI 不会看到结果后改政策；改变政策需新能力标识。

结果始终标明 `scheduler_registered: false`。宿主按[自主接续协议](../references/autonomous-continuation.md)登记已授权的未来任务，把实际调度 ID 和读回结果写入项目 node；唤醒后重新读账本，只处理有实际收益的到期工作。不为已完成或不活跃项目无限轮询，到期时间也不代表用户空闲或工具已获权限。

`due` 遇到坏记录会明确列出错误并返回非零码，同时可列出其他有效工作。修复或保留断点，不能静默跳过后把剩余文件称为全部完成。

## 教学与跨会话接续

教师 A 保存方法、预测、来源、命令、反例和产物。学习者 B 以同一根目录、当前 context/最新 node、教材及**新输入**开始，独立完成并留下自己的产物。审阅者 C 检查两者，记录误解和修改，再追加 teach 通过或失败。这只验证这份教材与任务，不代表已获得通用教学能力。

宿主身份、真实读取、命令退出和产物验收各自留证；不要将 A 的成品直接粘到 B 提示中冒充学习。结束会话后从同一物理根重新打开，可检查恢复。完结后按原契约回写项目 node、日报与候选经验，不另建一份冲突画像。

## 与旧能力的关系

可选 SQLite 适配器仍只管理旧交接状态；PPC JSON 仍绑定实验；两者不成为用户画像的新真相源。Markdown 经验继续作为语义知识库。新增工具不引入网络客户端、模型训练、自动依赖安装、凭据、提权或权限绕过。

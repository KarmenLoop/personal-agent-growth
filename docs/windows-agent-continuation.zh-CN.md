# Windows Koder CLI 接续教程 · 0.4.4

[English](windows-agent-continuation.en.md) · [通用安装与卸载](install.zh-CN.md) · [Markdown 学习模式](markdown-learning.zh-CN.md)

## 先确认运行条件

本教程的原生命令针对带 Markdown 学习模块的独立 Koder CLI 候选。仅安装本 Skill 不会给其他版本增加 `learning` 命令。先运行 `koder version`、`koder learning status --json` 和 `koder skills list --query personal-agent-growth --json`；缺少命令时，按 [Skill 协议](../references/markdown-learning.md)读写文件，并明确缺少原生接入，不能声称原生行为已验证。

在普通 PowerShell 窗口运行，不需要以管理员启动 Agent。有效权限以本次令牌为准；管理员账户的非提升令牌与独立标准账户分别记录。模型服务需已按 Koder 自身设置完成配置，凭据不写入 Skill、任务文件或经验库。

安装本 Skill 的具体下载、哈希核对和卸载步骤见通用安装指南。Koder 当前候选默认配置目录为 `%USERPROFILE%\.koder-cli`，可用 `KODER_CLI_HOME` 指定；将核验后的 Skill 目录放到该配置目录的 `skills\personal-agent-growth`。学习根默认是 `%USERPROFILE%\.koder\learning`，与聊天运行时存储职责分开。

## 两个会话使用同一记忆

在两个会话各自设置相同的 `KODER_LEARNING_ROOT`。不要复制成两份学习目录。以下示例项目名和工作区可以改，跨会话项目 ID 必须保持一致。

```powershell
$env:KODER_LEARNING_ROOT = Join-Path $env:USERPROFILE '.koder\learning'
$WorkA = Join-Path $env:USERPROFILE 'Projects\review-a'
$WorkB = Join-Path $env:USERPROFILE 'Projects\review-b'
New-Item -ItemType Directory -Force -Path $WorkA, $WorkB | Out-Null
koder learning init --timezone Asia/Shanghai --json
koder learning project review-demo -w $WorkA --goal '完成任务并留下可恢复的检查依据' --json
koder learning project review-demo -w $WorkB --json
```

将真实任务写入第一工作区的 `task-a.txt`，包括完成标准、可操作范围和下一会话用途。让 Agent 先恢复记忆、按需读取 Skill 与资料、保存预测，再完成工作；停顿前用 `learning_write` 写决定、经验候选和带实际路径的节点。

```powershell
[Console]::InputEncoding = [Console]::OutputEncoding = $OutputEncoding = New-Object System.Text.UTF8Encoding($false)
Get-Content -LiteralPath (Join-Path $WorkA 'task-a.txt') -Raw -Encoding UTF8 |
  koder run --stdin --new --session review-a --lang zh --skill personal-agent-growth --learning-project review-demo -w $WorkA
```

第一会话结束后，在第二工作区写简短的 `task-b.txt`：要求恢复同一项目、检查上一阶段原始产物、把经验用于新的交付物、调整下一步。不要粘贴旧聊天、预期答案或完整知识库。新会话仍需要正常的工具授权。

```powershell
[Console]::InputEncoding = [Console]::OutputEncoding = $OutputEncoding = New-Object System.Text.UTF8Encoding($false)
Get-Content -LiteralPath (Join-Path $WorkB 'task-b.txt') -Raw -Encoding UTF8 |
  koder run --stdin --new --session review-b --lang zh --skill personal-agent-growth --learning-project review-demo -w $WorkB
koder learning resume review-demo --json
```

`--new` 创建独立对话；同一个学习根与项目 ID 负责文件接续。检查 `projects/review-demo/context.md`、最新 `nodes/*.md`、`memory.md` 和经验条目，结合工具读取记录与前后哈希判断是否确实共用。同样的文字或一条“已恢复”回复不能代替证据。

## 中断如何处理

- 命令结果未知：保留原调用和回执，先只读核查影响。不要换工具或新会话重放未核实操作。
- 回合预算耗尽：检查已完成的产物，将剩余任务缩小后接续；不重复已通过检查，不把自动生成节点当成已写完经验。
- 必需的学习能力不可用：明确指定 `--learning-project` 后，不应在缺少学习工具时静默继续。修复版会在发送模型请求前停止；检查 `koder memory diagnose --json` 与 `koder learning status --json`，恢复已验证的存储后再续原项目，不新建空库替代，也不绕过 ACL 校验。
- 测试输入需要额外权限：区分输入制备与被测动作。本次文件链接由独立制备步骤创建，拒绝链接的守卫仍由普通令牌执行。该结果不能证明普通用户能够创建链接。
- 自动摘要含协议思考块：使用包含摘要修复的候选；保留原始回执，对当前恢复说明做有来源的纠正，不抹除历史失败。

- 经验参数错误：`learning_read open` 使用文首 ID；将返回的来源对象放入 `evidence` 数组，解释性文字放进 `why`、`steps` 或 `pitfalls`。写后读回确认；工具报错不能视为经验已保存。

原生记忆 API 与通用文件工具的范围不同。项目绑定不会自动授权读取另一个工作区。必要时走宿主支持的授权流程，或由已有权限的协调器交接明确列出的少量原始产物，保存源路径与哈希，由接收 Agent 独立核验副本。学习库始终保留一个物理根目录，报告中单独说明产物运输，不称为跨设备同步。避免递归列出整个学习目录。

- 来源哈希过期：decision/checkpoint 会更新 memory/context。写完后重新读取不可变节点，再引用到经验或完结记录；依赖前一步的写入必须顺序执行。完结操作会在改动任何文件前拒绝引用自身可变的 memory/context。

- 决策历史过长：成功项目包可返回 `deferredReads` 和 `LEARNING_MEMORY_READ_REQUIRED`。用 `learning_read open` 读取指定 memory ID，顺序跟随 `next` 到 null 后再写入；约束留在包内，历史完整留盘。项目包失败不能用随便读取某个节点代替。

## 复习与后续

对应 Koder 候选提供显式 `--harness learning-review` 收尾配置，只开放具名文件与记忆工具，不提供 Shell、目录搜索、浏览器和对外操作。执行与对账完成后，剩余工作是复核回执、修正交付物、保存经验时可选用；仍保留 16 步与原权限，不能运行新检查。环境参数应从命名启动回执取得，不扫描安装目录。普通发行版可能尚不包含此配置。

复习应重新检查原始输出和产物，再应用到有实际用途的新交付物。由新证据修正下一步，保存适用条件。没有明确待执行工作时不创建定时任务；本教程的手动会话接续不证明应用关闭后自动运行。


写完 checkpoint 后显式读取项目包，核对新修订号和最新节点。长工作区文件按字节分页，沿 nextOffset 读到 null，不用无变化修改检查看不到的正文。清单只能声明交接来源，执行结论要有实际输出和完成回执。发现旧经验错误时新建候选，用 supersedes 保留废弃关系和原来源。

![真实 Agent 接续与证据边界](diagrams/windows-agent.zh-CN.svg)

[可编辑图源](diagrams/windows-agent.zh-CN.mmd) · [接续经验](../references/windows-agent-continuation.md)

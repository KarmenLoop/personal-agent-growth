# 兼容性、实测证据与未完成项 · 0.4.1

[English](compatibility.en.md) · [当前发布验收](release-0.4.1-acceptance.zh-CN.md)

“能读取 Skill”“工具测试通过”“Agent 实际采用”“跨设备可用”“无新消息唤醒”是五类不同结论。本表按原始对象、版本和执行方式区分；新版文档不把旧行为实测自动升级为所有宿主全部通过。

| 能力 | 已观察结果 | 证据与限制 |
|---|---|---|
| 原生 Codex 唤醒 | 历史 2 次真实事件，执行、改频、回读、恢复复习、暂停均有记录 | [维护者报告](validation.md)；不证明应用关闭或关机后运行 |
| 同 Mac Cursor 文件恢复 | 修订 1→2、3→4、5→6；独立搬迁与引用检查发现两类缺陷后修复 | [历史报告](validation.md)；未替本次 0.4.1 做全新行为实测 |
| 0.4.0 可选适配器 | 已发布五工具 CLI/MCP、writer/修订/哈希检查 | [源代码](../scripts/host.py)；既有教程记载 live Codex read 与单独 MCP 客户端交接，不混称 Cursor 模型运行 |
| Windows 安装与文件共用 | 历史 Windows Server 2025，PowerShell 5.1/7，D 盘及 C 盘中文空格路径 | [原记录](windows-install-verification.md)；独立测试进程，不是桌面 Agent |
| Windows Koder → Cursor Agent | 尚缺原设备完整运行回执；原设备当前不可用的历史断点保留 | NOT_RUN/待设备恢复；用户口头“OK”未替代实际回执 |
| 内层 PPC | 真 Agent 对比原版、通用、领域及组合；之后变式复用并 observe 回写 | [原实测](recursive-improvement-trial.md)；检查器进程数不是总成本 |
| 跨领域元能力 | 24 个真实 Codex CLI 回合，两个领域，质量与资源约束检查 | [完整任务报告](cross-domain-trial.zh-CN.md)；token -5.9%，耗时 +7.4%，无普遍加速结论 |
| 经验种子搬迁 | 历史完整包安装、搬迁、加载、工具重用和卸载保留记忆 | [交付报告](delivery-acceptance.md)；导出快照做了路径适配，未新增 Agent 行为试验 |
| Markdown 日周学习 | 公开契约、16 类双语模板、评分与检索协议已提供 | 原生自动 API 与注入见下方独立候选；公开 Skill 本身不是常驻运行器 |
| 本次双语文档与图 | 当前文件、链接、渲染、包与工具检查 | [0.4.1 验收](release-0.4.1-acceptance.zh-CN.md)；不增加宿主行为结论 |

## 独立 Koder Markdown 候选

读取当前保留的测试输出与收条后生成[公开精简证据](evidence/koder-markdown-candidate-20261027.json)。源提交 `fa854e88f5a7325399f9a2f32950848737cdf1d9`，macOS arm64。私人源码与完整原始轨迹没有上传。

- 学习专项：30/30 通过。覆盖项目恢复、经验检索、纠正传播、失效总结、溢出、同分钟节点、日周补结、真实子进程中断和并发写入。
- 全量候选：1454 tests，1388 pass、31 fail、14 cancelled、21 skipped。原基线 1425 tests，1358 pass、31 fail、15 cancelled、21 skipped。候选独有未通过测试名称为 0，仍然不是全绿。整文件超时改变发现数量，不能用总数差当新增用例数。
- 五阶段实际进程：初始化 935 ms、首轮 4777 ms、新进程恢复 2198 ms、完结 297 ms、新项目复用 533 ms。不同阶段工作量不同，不能推导加速。
- 真实 60000 ms 空闲回调在观察到的 61815 ms 中更新日报；只证明程序打开时的进程内计时。
- 提供方为脚本化验收，实际经过原生工具链，但未请求付费/远程模型；不证明自主归纳质量，token/费用未知。

候选覆盖 `learning init/status/project/checkpoint/resume/open/search/experience/complete/observe/decision/tick/daily/weekly/consolidate/on/off`，原生 `learning_read/learning_write`，Markdown 事务、读集、4000 token 上限及日周到期处理。这是候选能力清单，不是安装本 Skill 后即可使用的命令说明。

## 如何升级结论

要宣称 Windows Agent 接续，需恢复原任务而非新建模拟：找到原目录和回执，真实 Koder 读取/写入，再由 Cursor 真实模型回合读同一修订、完成复习并写回，检查双方产物与读集。设备未恢复时该支路保持待验，不阻止独立文档发布。

要宣称跨设备，共享内容身份、同步冲突、路径映射和各端权限都要实测。要宣称无人新消息运行，必须保存真实宿主触发及执行/验收/停止回执。要宣称效率上涨，需完整任务质量、耗时、原生用量和优化开销，不能只数工具调用。

公开证据摘要包含来源哈希与范围，但不是公开的完整私有轨迹。仓库工具测试可以独立复跑；维护者的历史设备行为报告与可复现测试分别理解。

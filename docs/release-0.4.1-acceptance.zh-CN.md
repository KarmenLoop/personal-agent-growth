# 发布验收 · 0.4.1

[English](release-0.4.1-acceptance.en.md) · [兼容性](compatibility.zh-CN.md) · [本地命令与回执](evidence/release-0.4.1-local.json)

## 验收范围与结果

2026 年 10 月 27 日，本地文档与分发验收完成，两处实测输入错误已纠正并保留。这里验收公开 Skill、文档、图示及真实文件操作。修正后的实现提交 52caa11 已通过三种托管系统。后续文档提交补入这些收条，其检查链接保留在拉取请求中。

| 检查 | 实际结果 |
|---|---|
| Python 回归 | macOS arm64 / Python 3.12.14，48 项通过 |
| 核心安装包 | 59 个文件，123 项 ZIP/manifest 检查全部通过 |
| Skill 格式 | quick_validate.py 返回 Skill is valid；PyYAML 仅供开发校验器使用 |
| 双语文档 | 21 对中英文文档，核对本地路径和章节锚点 |
| 学习模板 | 每种语言 16 类，共 32 个含必要元数据的 Markdown 模板 |
| 新图示 | Mermaid 11.4.1 与真实 Chromium 渲染 16 个 SVG，保留源文件和输出哈希 |
| 原有内嵌图 | 7 个 Mermaid 代码块全部解析通过 |
| 目视核对 | 已检查中文能力总图、中文架构图、英文递归改进图 |
| 完整离线包 | 安装至含中文与空格的目录，迁移后从另一工作目录读取两个实际索引的经验版本 |
| 拒绝场景 | 已存在目录、被改动的 Skill、不存在的经验领域、重复执行安装命令均被拒绝 |
| 卸载 | 经验、任务与 Markdown 学习测试文件保留，只移除未改动 Skill 或发现入口 |
| macOS 教程 | 实际执行 Bash 命令；使用隔离路径及本地 file:// 安装包传输 |

每种语言的总图包含 137 个节点，三个专题图各含 92 个节点。图示说明架构，不是 Agent 智慧提升的验收证据。本地回执有 21 条：20 次实际启动的命令与 1 次启动路径错误。预期拒绝码与异常失败分开记录，两处纠正没有从记录中删除。

## 保留的错误与修正

- 首次迁移读取使用了种子索引中不存在的 scientific-data-analysis 领域，工具正确拒绝。随后改读实际存在的 offline-package-check；没有编造兜底经验，也没有为此改产品。
- 实测脚本误用了 /usr/bin/unlink，本机实际位置为 /bin/unlink。改正可执行文件路径后完成移除；安装教程原本就按 PATH 调用 unlink。
- Windows 检查器仍残留 0.3.3 文件名与固定文件/检查数量，现已按当前 manifest 和 0.4.1 教程修正。PowerShell 5.1 和 7 随后均通过两类安装根目录，实际任务见下表。
- 图示渲染发现引号实体、时序语法分隔符及两处标题裁切，已修源文件、重新渲染全部 16 张、更新哈希并目视抽查。
- 合入此前未发布的 0.4.1 实验与打包工作时，保留 GitHub 0.4.0 已发布的宿主适配器。

## GitHub 跨系统实际结果

| 系统或 Shell | 结果 | 实际运行 |
|---|---|---|
| Ubuntu 24.04、macOS 26 Intel、Windows Server 2025 | 各自 48 项测试、核心构建/123 项检查、文档检查全部通过 | [修正后的实现检查](https://github.com/KarmenLoop/personal-agent-growth/actions/runs/40387260224) |
| Windows PowerShell 5.1.26100.33648、PowerShell 7.6.7 | 默认 D 盘及自定义 C 盘中文空格路径全部通过 | [安装与共享文件检查](https://github.com/KarmenLoop/personal-agent-growth/actions/runs/40387005475) |

Windows 收条记录三个不同进程推进修订 1→2→3、实际共享文件身份、拒绝过期写入、拒绝重复安装及卸载保留记忆。这是**测试进程，不是 Agent**。CI 用当前本地构建替换下载传输，没有访问正式 Release 下载地址。详见 [CI 摘要](evidence/release-0.4.1-ci.json)与[带原始产物哈希的 Windows 摘要](evidence/release-0.4.1-windows.json)。

[首轮 CI](https://github.com/KarmenLoop/personal-agent-growth/actions/runs/40387006023) 有一项 Windows 失败：测试把 RUNNER~1 短路径与解析后的完整路径按文字比较。现改为 samefile 核实真实索引目录，快照与篡改检查全部保留。旧失败没有删除；这是测试可移植性修正，不代表经验加载器返回了错误目录。

正式产物及上传后下载回执见 [v0.4.1](https://github.com/KarmenLoop/personal-agent-growth/releases/tag/v0.4.1)。RELEASE-VERIFICATION.json 记录发布提交、下载哈希、包检查及真实网络安装结果；该文件缺失时不能认为这些发布后检查已完成。它位于 ZIP 外，避免压缩包哈希自引用。

## 本轮未证明的能力

本次发布没有重新执行原生 Codex、Cursor、Koder 模型回合，没有补齐原生 Windows 桌面 Agent、跨设备同步或应用关闭后的系统唤醒验收，也不证明所有领域的效率上涨。独立 Koder 候选仍有 31 项全量测试失败，其私有产品实现不在公开包内。历史 Agent 实测按原日期保留于[兼容性](compatibility.zh-CN.md)和[跨领域结果](cross-domain-trial.zh-CN.md)。

本地安装使用本地构建产物，不等于 GitHub 网络下载通过。发布校验回执单独标识经过下载复核的最终包。ZIP 与 manifest 一致只证明内容一致，不等于独立签名认证。公开回执替换了私人路径前缀，分别保留原始输出和脱敏输出的哈希。

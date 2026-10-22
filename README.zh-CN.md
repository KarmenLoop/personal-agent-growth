# Personal Agent Growth · 智能体任务复盘

[English](README.md) | 简体中文

让下一次工作有明确的起点，而不只是聊天总结。任务状态、证据、更正和一个可执行的下一步保存在共享私有目录里，由接手的宿主真实读取。

[下载 v0.3.3](https://github.com/KarmenLoop/personal-agent-growth/releases/tag/v0.3.3) · [教程](docs/tutorial.zh-CN.md) · [反馈问题](https://github.com/KarmenLoop/personal-agent-growth/issues)

## 用途与范围

这是用于任务复盘与交接的可移植技能，并附离线包检查工具。技能正文和四份工作参考目前为中文，公开安装与使用指南提供中英文。

![智能体任务复盘流程示意](docs/images/workflow-v0.3.3.svg)

*v0.3.3 的流程示意，非应用截图或运行验收。*

## 开始使用

下载技能 ZIP 与 manifest.json，解压到新的规范技能目录，再通过宿主支持的技能发现路径关联一次。技能目录和私有任务记录分开保存。

选择两个宿主都能解析到同一物理位置的私有任务目录，交接前记录 writer 与 state_revision。Python 3.11+ 只用于可选的离线检查，读取 Markdown 不需要 Python。

## 第一次有用的任务

明确加载 SKILL.md，审阅一份合成任务产物，保存实际检查结果，更正一个错误假设，并留下具体复查动作。切换宿主前确认文件已经保存。

接手宿主读取当前修订，并在新的检查中使用前一份产物。定时执行需要真实支持的后端及对应任务授权；安装不会创建定时器或跨设备同步。

## 常见问题

**它会重新训练模型吗？** 不会。它整理可复用任务记录与复查方法，不改变模型权重或服务商账号。

## 文档与许可证

[下载到实践的使用指南](docs/tutorial.zh-CN.md) · [LICENSE](LICENSE)

AGPL-3.0-only. 许可证条件以原文为准，再分发时保留包内法律文件。 [KarmenLoop](https://karmenloop.com).

# Personal Agent Growth

[English](README.md) · [中文](README.zh-CN.md) · **v0.4.0**

任务换工具后，下一步仍然清楚。内置 Python 适配器在私有 SQLite 中保存检查点、核对关联文件，并在已配置的宿主间转交写入责任。

![检查点与交接流程](docs/images/workflow-v0.4.0.svg)

交接保留目标、当前版本、观察结果、产物哈希和下一步。接收宿主读取同一条记录；旧写入者或已变化的产物会被拒绝，避免悄悄覆盖交接状态。

下载 [v0.4.0 包](https://github.com/KarmenLoop/personal-agent-growth/releases/tag/v0.4.0)，安装 Python 3.11+，按[中文教程](docs/tutorial.zh-CN.md)配置。包内仍保留离线归档校验器。

本项目提供持久本地任务状态，不是自主代理运行时，不会注册定时器、联系他人、执行下一步或跨设备同步数据库。这些动作需要另外获得授权的宿主完成。真实 Codex 回合已读取保存的交接；Cursor 已发现工具，模型回合受本机登录和额度限制，仍未验收。

[AGPL-3.0](LICENSE) · [KarmenLoop](https://karmenloop.com)

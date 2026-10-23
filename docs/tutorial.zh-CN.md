# Personal Agent Growth v0.4.0 教程

[English](tutorial.en.md) · [中文](tutorial.zh-CN.md)

下载并解压当前版本，使用 Python 3.11+。任务数据放在技能与仓库之外。两个工具在本机使用同一个私有数据根目录和相同工作区文件。

```sh
python /path/to/scripts/host.py --root /private/task-state --workspace /path/to/project --install-host codex install
python /path/to/scripts/host.py --root /private/task-state --workspace /path/to/project --install-host cursor install
```

重载各宿主、批准特定服务，确认发现五个 `growth_*` 工具。配置存在不等于已验收。

在 Codex 调用 `growth_start`，填写 `task_id`、`goal` 和 `acceptance`。实际完成项目中的一步，再用当前 `expected_revision`、阶段、观察、下一步及工作区内产物路径调用 `growth_checkpoint`。适配器核对已有文件，不会替你制造证据。

用当前版本和 `target_host: cursor` 调用 `growth_handoff`。在 Cursor 中使用同一任务 ID 调用 `growth_read`，检查写入者、下一步和 `evidence_current`。原宿主仍可读取，但不能继续更新。接收宿主完成工作后，用最新版本提交新检查点；`growth_export` 可导出私有交接 JSON。

不使用模型也可检查：

```sh
python /path/to/scripts/host.py --root /private/task-state --workspace /path/to/project --host-id cursor call growth_read --input request.json
```

`request.json` 内容为 `{"task_id":"your-task-id"}`。进程重启不会丢失检查点；旧版本写入需要先重读，产物缺失或变化需要重新验收后再交接。不要覆盖数据库来清除冲突。备份前停止写入，再复制私有目录。

调度状态明确保留 `not_registered`，没有创建唤醒任务。本机跨宿主状态不代表跨设备同步。macOS 上真实 Codex 读取与独立 MCP 客户端交接已通过；Cursor 工具发现已通过，认证后的模型回合及 Windows/Linux 原生操作尚未验收。

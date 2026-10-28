# 复杂思维导图与流程图 · 0.4.4

[English](mindmaps.en.md) · [中文](mindmaps.zh-CN.md)

中英文各十张：四张详细思维导图，以及架构、调度、交接、日周、Windows 跳过核查与 Agent 接续图。两种语言保持相同分支结构。图示说明责任与协议，不代表每个宿主都已实现；实际范围以[兼容性](compatibility.zh-CN.md)为准。SVG 可放大，Mermaid 源文件可编辑。

## 完整能力树

137 个节点，包含触发条件、产物和失败后继。

[SVG](diagrams/system.zh-CN.svg) · [Mermaid](diagrams/system.zh-CN.mmd)

![完整能力树](diagrams/system.zh-CN.svg)

## 架构与数据流

[SVG](diagrams/architecture.zh-CN.svg) · [Mermaid](diagrams/architecture.zh-CN.mmd)

![架构与数据流](diagrams/architecture.zh-CN.svg)

## 因果判断与改判

92 个节点，包含触发条件、产物和失败后继。

[SVG](diagrams/reasoning.zh-CN.svg) · [Mermaid](diagrams/reasoning.zh-CN.mmd)

![因果判断与改判](diagrams/reasoning.zh-CN.svg)

## 记忆体系与用户证据

92 个节点，包含触发条件、产物和失败后继。

[SVG](diagrams/memory.zh-CN.svg) · [Mermaid](diagrams/memory.zh-CN.mmd)

![记忆体系与用户证据](diagrams/memory.zh-CN.svg)

## 双层递归与完整成本

92 个节点，包含触发条件、产物和失败后继。

[SVG](diagrams/recursion.zh-CN.svg) · [Mermaid](diagrams/recursion.zh-CN.mmd)

![双层递归与完整成本](diagrams/recursion.zh-CN.svg)

## 真实唤醒与停止

[SVG](diagrams/continuation.zh-CN.svg) · [Mermaid](diagrams/continuation.zh-CN.mmd)

![真实唤醒与停止](diagrams/continuation.zh-CN.svg)

## 跨工具接续时序

[SVG](diagrams/handoff.zh-CN.svg) · [Mermaid](diagrams/handoff.zh-CN.mmd)

![跨工具接续时序](diagrams/handoff.zh-CN.svg)

## 日周学习与纠正传播

[SVG](diagrams/cadence.zh-CN.svg) · [Mermaid](diagrams/cadence.zh-CN.mmd)

![日周学习与纠正传播](diagrams/cadence.zh-CN.svg)

## 阅读顺序

先看完整能力树，再沿架构箭头进入一个判断分支，找到它写入的记忆与下一触发。实验从提案走到冻结证据、组合复验，再看外层推广。每条转换的原因见[架构剖析](architecture.zh-CN.md)与[完整判断案例](reasoning.zh-CN.md)。

## 重新生成图示

`tools/render_diagrams.mjs` 使用开发阶段的 Mermaid、Playwright 和 Chromium。本次实际渲染版本为 Mermaid 11.4.1。参数使用依赖包的绝对目录，不给 Python 运行时增加依赖：

```sh
node tools/render_diagrams.mjs --mermaid-dir /path/to/node_modules/mermaid --playwright /path/to/node_modules/playwright --browser /path/to/chromium
```

修改源文件后重新生成两种语言，检查输出，再更新 publication.json 的对应哈希。渲染器会把源文件/输出哈希和尺寸写入 docs/diagrams/render-manifest.json；scripts/check_publication.py 会拒绝内容漂移。字体和浏览器版本可能改变排版，应保留实际生成产物。

## Windows 跳过核查

[SVG](diagrams/windows-audit.zh-CN.svg) · [Mermaid](diagrams/windows-audit.zh-CN.mmd)

![Windows 跳过核查](diagrams/windows-audit.zh-CN.svg)

## Windows Agent 恢复

[SVG](diagrams/windows-agent.zh-CN.svg) · [Mermaid](diagrams/windows-agent.zh-CN.mmd)

![Windows Agent 恢复](diagrams/windows-agent.zh-CN.svg)

[接续实操教程](windows-agent-continuation.zh-CN.md)

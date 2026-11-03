# 计量学习反馈库

[English](README.md) · [实际验收](../../release-0.7.0-acceptance.zh-CN.md)

这是从 0.7.0 真实研究整理的可搬迁 Markdown 库，包含两份冻结提案及四条任务级反馈；两份提案都没有启用为全局默认。`harmful` 表示指定任务中整个候选包出现资源退步，不代表源经验本身错误。

`evidence/analysis.json` 是公开路径脱敏衍生文件；每条 Markdown 绑定的是该衍生文件的真实字节。原始与公开身份保留在研究导出中，不能冒充未脱敏原始日志或新盲测。

将整个目录复制到任务局部记忆根后，可读取来源、观察及反例：

```sh
python3 -B /path/to/personal-agent-growth/scripts/experience_transfer.py retrieve --root /path/to/copied-library --query /path/to/copied-library/requests/query.md
```

创建、写入反馈、检索的实际 CLI 回执在 `operations.json`。工具落盘与检索不等于后续 Agent 已经采用，也不证明提效。旧经验和原失败保持原样。

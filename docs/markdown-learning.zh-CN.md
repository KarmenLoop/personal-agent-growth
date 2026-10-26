# Markdown 学习记忆完整契约 · 0.4.2

[English](markdown-learning.en.md) · [全部模板原文](../templates/learning/README.md) · [架构边界](architecture.zh-CN.md#storage)

本页规定日、周、项目、用户行为与经验的统一文件契约。公开 Skill 可由宿主依此读写 Markdown；原生 API、自动上下文注入和到期处理在独立 Koder 候选中实现，尚未正式合入发布。不能把本页伪代码当成已安装命令。

## 1. 根目录与最终布局

根目录显式参数优先，其次 `KODER_LEARNING_ROOT`，独立 Koder 候选默认 `~/.koder/learning/`。跨工具使用时将解析后的同一个绝对路径交给各宿主。Windows 可选 D 盘优先、无 D 盘选 C 盘；Mac 可用桌面或用户自选位置。路径选择只做一次并记录到宿主配置，不在每轮猜测。

```text
learning/
├── policy.md
├── index.md
├── daily/YYYY-MM-DD.md
├── weekly/YYYY-Www.md
├── weekly/YYYY-Www-consolidation.md
├── projects/<project-id>/
│   ├── memory.md
│   ├── context.md
│   ├── nodes/YYYY-MM-DD-HHMM.md
│   ├── summary.md
│   └── experience.md
├── experience/<exp-id>.md
├── research/<research-id>.md
└── user/
    ├── profile.md
    ├── behavior-log/YYYY-MM-DD.md
    ├── tags.md
    └── preview.md
```

日期使用 `policy.md` 明确的时区。ISO 周使用周所属年份，例如跨年那一周不按日历年简单拼接。节点同一分钟碰撞时追加 `-02`、`-03`，按修订与序号选择最新节点，不能覆盖。`research` 是待验证研究材料，`experience` 是可检索结论；两者均为 Markdown。模板保存在分发包中，未实例化模板不参与检索。

## 2. 所有 Markdown 的格式

```yaml
---
id: exp-2026-10-27-01
type: experience
project: null
tags: [domain/python, workflow/evidence-attribution]
status: active
created: 2026-10-27
updated: 2026-10-27
sources: []
revision: 1
validation: untested
---
```

`id` 稳定且唯一；`project` 不能只从文件夹名猜同一项目。标准状态为 `active / done / deprecated`，补充检查状态放 `review_status`，避免把“待复核”错写完成。`sources` 使用可定位的路径/URL、原始记录 ID 和哈希；可变文件引用还保存所引用修订。推荐稳定的 `#e-...` 证据锚点；单独行号会随编辑漂移，应同时绑定源哈希。

类型包含 memory、context、node、summary、experience、daily、weekly、consolidation、profile、behavior、tags、preview、index、policy、research、project-experience。缺内容时保留小节标题，写未知或待补，不编造事实。`template: true` 的源模板必须先替换占位符，赋新 ID 并移除模板标记后才能作为记录。

## 3. 项目生命周期

| 动作 | 必读 | 必写 | 通过条件 |
|---|---|---|---|
| 创建 | 当前目标、policy、项目绑定 | memory、context、初始 node、index | 稳定 ID、范围、验收条件明确 |
| 重要决定 | 当前约束、相关证据 | memory 的事实/决定，node 的变化原因 | 用户新指令优先，保留被替代决定来源 |
| 停顿 | 当前产物、未决问题 | 新 node、刷新 context | 卡点、已试方案、下一动作可执行 |
| 恢复 | **context + 最新 node**，再 memory | 实际 read_set 和新进度 | 核对修订、输入身份及 writer |
| 完结 | 当前验收证据 | summary、项目 experience、全局经验、index done | 目标已达成，来源可复核 |
| 重新打开 | 新事实、旧 summary 的适用性 | context/node/index；summary 标待复核 | 不把过期完成摘要继续注入 |

memory 留长期事实、约束、决定、关键路径与禁忌，不塞整段聊天。context 留当前进度、假设、未决与下一步。节点留过程和失败；summary 仅完结时写满，恢复进行中项目不使用旧 summary 作为当前真相。

## 4. 日报 → 周报 → 次周一巩固

日报整理当天可观察事实、学习、反思、自我思路变化及下期动作。对有活动或停顿的项目补节点，必要时更新行为记录、标签、画像，并链接新经验。没有覆盖数据时标 coverage unknown，不推断用户没有工作。重复触发无新事实时不重复改写。

周结读取该 ISO 周全部已有日报，列出覆盖与缺失，再提炼重复模式、短板、有效方法与默认策略候选。次周一读取上周周报及真实落地证据，写 consolidation：已落地、仍弱、复习结果、本周预习重点，并更新 preview。没有应用证据的“改进”保持待验证。

启动、结束或空闲时只处理已到期工作；离线后按批次补结，保存剩余范围，避免每次重复第一批。独立 Koder 候选每批上限 366 日期，使用进程内到期检查；公开 Skill 需宿主提供真实事件或调度。固定的是日周语义节奏，不是固定每几分钟唤醒。

## 5. 用户行为：采集证据，不写印象

| 信号 | 可记录证据 | 可用于什么 |
|---|---|---|
| 任务意图 | 用户原话、改目标或加范围的时间与会话 ID | 领域与规划 |
| 交互节奏 | 短指令/长说明、打断与明确的 `--yes` 使用 | 沟通方式；不自动扩大授权 |
| 纠错模式 | 同类纠正、接受 diff、回滚及其原因 | 流程短板；Agent 错误单独归因 |
| 工具偏好 | 明确采用或拒绝的 shell/编辑器/浏览器/MCP | 默认路径和预习 |
| 领域足迹 | 当前仓库语言、框架、任务关键词 | 领域标签；不推断职业身份 |
| 决策风格 | 直接干、要对比、要确认等原话 | 规划粒度 |
| 完成质量 | 要求测试、文档、提交或停顿原因 | 任务验收与经验 |
| 时间模式 | 已授权会话内活跃时段与可观察时长 | 合适复习时机；沉默不等于空闲 |

行为条目包含 `event_id, observed_at, source, scope, signal, tag, direction, outcome, supersedes`；用户可见正文注明事实与解释。身体状态、习性或语言能力仅在任务相关且用户提供或可授权观察时记录；不对人格下贬义标签，不推断隐私属性。用户纠正优先于统计，撤销来源应使依赖标签、规划与摘要重新计算或降级。

## 6. 可计算评分与升降级

标签分 `domain / workflow / collab`。去重以原始事件而非摘要数量为准；未来时间、撤回来源、越界采集及重复转述不计数。相反信号记录 `oppose`，不会偷偷抵消后消失。

`N=count_30d`，`C=min(N/10,1)`；`R` 是近 7 个本地日期的存在信号加权，今天至第 6 天权重分别为 7/28…1/28，每日最多一次；`S` 只来自可独立验证且确与该策略有关的结果，无结果为 null。下列规则是本项目的透明启发式，不是心理测量模型。

```python
def evaluate_tag(tag, now, policy, logs, projects):
    # Resolve active source revisions before counting anything.
    events = valid_unique_evidence(logs, tag, now, within_days=30)
    support = [e for e in events if e.direction == "support"]
    oppose = [e for e in events if e.direction == "oppose"]
    N, O = len(support), len(oppose)
    D = len(set(e.local_date(policy.timezone) for e in support))
    C = min(N / 10, 1.0)
    # Each local date contributes at most once; today has weight 7/28.
    R = sum((7 - age) / 28 for age in range(7)
            if any(e.age_in_local_days(now) == age for e in support))
    outcomes = independently_verified_outcomes(events, tag)
    S = successes(outcomes) / len(outcomes) if outcomes else None
    score = .5*C + .3*R + .2*S if S is not None else (.5*C + .3*R)/.8
    if N == 0:
        confidence = 0.0
    elif N < 3 or D < 2:
        confidence = min(.69, .2 + .1*N + .1*D)
    else:
        confidence = min(.95, .7 + .15*min((N-3)/7, 1)
                         + .1*min((D-2)/3, 1))
    confidence *= N/(N+O) if N+O else 0
    conflict = same_day_opposition(events) or explicit_unresolved_correction(events)
    stale = days_since_last_support(support, now) >= 14
    durable = five_consecutive_workdays(support, policy.calendar) or \
              three_independent_done_projects(support, projects)
    stable = score >= .6 and confidence >= .7 and durable and not conflict and not stale
    state = "conflict" if conflict else "stale" if stale else "stable" if stable else "observing"
    return {"score": score, "confidence": confidence, "state": state,
            "count_30d": N, "days": D, "oppositions": O,
            "success_rate": S, "evidence": [e.anchor for e in events]}
```

至少 3 条证据、2 天支持后，未被反证折减的 confidence 才能达 0.7。稳定偏好还需要 score≥0.6、confidence≥0.7，以及连续 5 个配置工作日或 3 个独立完结项目同向支持。14 天无强化降为 stale；同日冲突写入 profile 待确认，规划用中性默认。明确偏好单独保存并立即在其范围内生效，不必等待统计投票；统计不能产生额外执行权限。

tags.md 的每项保存数值、算法版本、计算时刻、证据锚点及状态。preview 依据高置信领域与已观察薄弱点选本周知识、仓库惯例和检查清单。不要从“经常用 TypeScript”推断“只能做 TypeScript”。

## 7. 读取优先级与注入上限

```python
def project_packet(root, project_id, task, token_limit=4000):
    policy = read_md(root / "policy.md")
    if not policy.enabled:
        return None
    with writer_or_snapshot_guard(root):
        context = read_md(root / "projects" / project_id / "context.md")
        node = read_latest_valid_node(root, project_id)  # revision, then timestamp/sequence
        memory = read_md(root / "projects" / project_id / "memory.md")
        verify_project_id_revisions_and_sources(context, node, memory)
        if has_unresolved_manual_conflict(context, node, memory):
            return explicit_conflict_without_overwriting()
        required = [context, node, mandatory_constraints_and_decisions(memory)]
        if count_tokens(required) > token_limit:
            return required_context_overflow()  # never silently drop a constraint
        hits = search_markdown(root / "experience", id=task.experience_id,
                               tags=task.domain_tags, keywords=task.keywords)
        eligible = [x for x in hits if scope_matches(x, task)
                    and sources_current(x) and x.status != "deprecated"
                    and x.validation in ("local", "reused")]
        ranked = rank(eligible, domain_match=True, failure_match=True,
                      evidence_strength=True, recency=True, deterministic_ties=True)
        packet = fit_optional(required, ranked, limit=token_limit, top_n=5)
        if context.project_status == "done":
            packet += fit_current_verified_summary(root, project_id, remaining(packet))
        if task.is_planning or task.is_monday_consolidation:
            packet += fit_preview_and_due_reports(root, remaining(packet))
        return packet_with_source_paths_revisions_hashes_and_purpose(packet)
```

context 与最新 node 是恢复必读；memory 的强约束和当前决定不能被可选经验挤掉。按领域、失败机制检索经验，先过滤有效性与范围再 top-N，默认最多 5 条。只在项目 done 且来源仍有效时读 summary。日周与 preview 在规划/巩固用途时加载，不每轮读全库。

注入应保留引用路径、哈希/修订和采用理由。调用经验可以注入全文，也可只注入“场景 + 可复制步骤”，但不得遗漏适用范围、反例和失效条件。包预算 2–4k tokens；4k 上限装不下必要项时返回明确冲突。这里只提供协议伪代码，宿主的实际 token 计数和注入接口要单独验证。

## 8. 读写与复用操作契约

| 操作 | 行为 | 约束 |
|---|---|---|
| 按 ID 打开 | 扫 metadata 或可重建索引，读取原 MD | 索引过期则回到原文件 |
| 按标签 | 来源与范围过滤后按关联、置信、近期排序 | 低置信不强规划 |
| 按关键词 | 标题、小节与正文检索，可用 rg | 不必上向量库；检索缓存不是另一真相源 |
| 链接 | 项目与经验互链 | 相对路径按当前 MD 位置解析 |
| 合并 | 新条目保留各来源，旧项 deprecated + superseded_by | 更新 index，不硬删旧链接 |
| 导出 | 明示采用的原 MD 或小节及来源 | 公开前剔除私人画像、凭据和原始聊天 |
| 自学 | 检索一手网站/GitHub，记问题、日期、来源、摘要、限制 | 先为 untested，实用验证后才 local/reused |

建议 API 责任包括 create/update project、write node、daily close、weekly close、Monday consolidate、open/search/merge experience、observe/recompute tags、build packet。独立候选 CLI 名称见[候选范围](compatibility.zh-CN.md)；公开 Skill 没有承诺这些原生命令已经安装。

## 9. 写入、冲突与迁移

同一项目只有一个当前 writer，提交前再次核对修订，先写新节点和证据再更新 context/index，并回读。宿主没有原子多文件事务时用可恢复 Markdown journal 记录目标、旧哈希、新文件和提交阶段；恢复时核对实际文件，不凭一条“已完成”覆盖他人的更新。并发实现须单独实测；单纯约定 writer 不是锁。

停用学习时不注入、不自动观察、不允许学习工具写入；恢复时读取现有 MD，不从旧隐藏画像回填。旧 SQLite/JSON 系统只作历史来源或实验回执。迁移按架构文档执行，切换前检查知识、节点、来源与新入口，不双写两个可变画像。

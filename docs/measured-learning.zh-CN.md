# 先测量策略，再决定是否采用

[English](measured-learning.en.md) · [详细协议](../references/measured-learning.md) · [架构图源码](diagrams/measured-learning.zh-CN.mmd)

![计量学习架构](diagrams/measured-learning.zh-CN.svg)

本教程对应 **0.7.0**：策略冻结与带种子排程、完整任务成本记录、显式因果映射。离线步骤只需 Python 3.11+ 与标准库。从仓库根目录在 macOS/Linux shell 运行；Windows 使用等效的已授权 shell 与 Python 路径。无需适配器、全局画像、网络调用或依赖安装。

**下文全部夹具都是合成示例。** 运行它们只能核验文件契约和算术，不执行 Agent，不认证未见任务，不计量服务商实收费用，也不证明策略收益。唯一真实 CLI 调用在下文单独列出，须具备实际授权环境。

## 1. 定义比较，再冻结策略

选一个新的任务局部根目录。示例生成 Markdown，首段使用 JSON 对象作为 front matter；辅助程序不接受任意 YAML 语法。元数据中的路径相对这个根目录；使用稳定的 ASCII ID、精确路径拼写，不使用符号链接。既有不可覆盖记录不要改写；需要时使用新的研究、运行或尝试身份。

示例含两路、各三次重复。真实研究须在发布目标**之前**保存原质量标准、收益门槛、完整资源预算、停止条件、可见模型/推理强度/传输与权限。通用改法、领域改法按既有 [PPC 协议](../references/recursive-improvement.md)分别验证；修改组合后另做实跑。这个两路文件演示本身不满足那些采用门槛。

<!-- demo:setup -->
```sh
PAG_REPO="$PWD"
PAG_DEMO="${PAG_DEMO:-$(mktemp -d "${TMPDIR:-/tmp}/pag-measured.XXXXXX")}"
PAG_MODEL="${PAG_MODEL:-protocol-demo-no-model}"
export PAG_REPO PAG_DEMO PAG_MODEL
python3 -B - <<'PYCODE'
from pathlib import Path
import json, os
root = Path(os.environ["PAG_DEMO"])
root.mkdir(parents=True, exist_ok=True)
with (root / ".tutorial-root").open("x", encoding="utf-8") as f:
    f.write("Synthetic protocol demonstration; no Agent outcomes.\n")
for name in ("evidence", "requests", "private", "prompts"):
    (root / name).mkdir()
def md(path, metadata, body):
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("x", encoding="utf-8") as f:
        f.write("---\n" + json.dumps(metadata, indent=2) + "\n---\n\n" + body + "\n")
for arm, text in {
    "baseline": "Read input/task.md and the supplied data. Produce the requested artifact in output/. Check it before delivery.",
    "candidate": "Read input/task.md and the supplied data. State the quantity being measured, check overlapping intervals and unknown values, then produce and verify the artifact in output/."
}.items():
    folder = root / "strategy" / arm
    folder.mkdir(parents=True)
    (folder / "SKILL.md").write_text("# Synthetic " + arm + "\n\n" + text + "\n", encoding="utf-8")
md("plan.md", {
    "id": "synthetic-study", "type": "blind-plan",
    "arms": {"baseline": "strategy/baseline", "candidate": "strategy/candidate"},
    "model_config": {"model": os.environ["PAG_MODEL"], "training": False,
                     "reasoning_effort": "low", "transport": "default"},
    "repetitions": 3, "seed": 20261104, "deadline_seconds": 120,
    "metric": "native_tokens"
}, """Synthetic development protocol, not a held-out benefit study.
Unit: one task x one repetition x one arm; each attempt has a fresh context.
Quality: original external artifact criteria must all pass; no candidate rubric edits.
Example gain rule: at least 10% lower native-token total over all repetitions
for each task, with complete usage coverage and no quality loss; retain paired detail.
Time guard: no more than 10% higher complete-task time. Unknown coverage is inconclusive.
Budget: six invocations at most, each with an Agent-process limit of
120 seconds and 12 commands plus grading up to 30 seconds. The host enforces
a 1,200-second study envelope, including 300 seconds for setup/review and other
controller overhead; record actual overhead separately. Monetary budget is unknown until
real billing is available; apply the host's authorized spending cap before any call.
Stop on permission/input/strategy drift, exhausted budget, or unresolved effects.
Keep every failed/cancelled attempt. Retries need a new attempt ID and retained cost.
The helper stores these prose rules; independent review must enforce them.""")
print(root)
PYCODE
python3 -B scripts/blind_trials.py freeze --root "$PAG_DEMO" \
  --file "$PAG_DEMO/plan.md" > "$PAG_DEMO/evidence/freeze.json"
```

`blind-trials/synthetic-study/frozen.md` 保存计划哈希与各路策略目录清单。它是内容冻结，不是签名记录或访问控制。独立作者何时接收、何时发布目标，另保留真实宿主证据。冻结策略中不能加入答案、已暴露目标的专用修复、凭据或私有验收程序。`model_config` 只声明可见配置，不能据此声称已认证服务端权重身份。

## 2. 冻结后发布目标，保存带种子的顺序

下一段有意创建 **development 开发任务**：教程读者能看到输入、来源与验收器。真正的 holdout 应由独立作者从真实失败或新的适用任务中组织，有来源记录，且在发布前不向策略作者和执行者暴露。只有实际满足这些条件才使用 `role: "holdout"`；历史重放与保留变式分别记录。

验收器是接受 `--output`、`--public`、`--report` 的 Python 程序。runner 单独启动它，限制 30 秒，并保存 stdout、stderr、退出码。合成算术精确检查只是演示接口；真实验收仍要检查原任务的实质标准及相关轨迹。

<!-- demo:release -->
```sh
python3 -B - <<'PYCODE'
from pathlib import Path
import hashlib, json, os
root = Path(os.environ["PAG_DEMO"])
public = root / "public" / "window-demo"
public.mkdir(parents=True)
(public / "task.md").write_text(
    "# Synthetic interval task\n\nRead input/windows.json. Write output/occupancy.json with exactly "
    "the integer keys union_seconds and naive_sum_seconds. Intervals share one "
    "monotonic clock; endpoints are half-open. Do not claim measured billing or inference time.\n",
    encoding="utf-8")
(public / "windows.json").write_text(json.dumps([[0, 5], [4, 9]]) + "\n", encoding="utf-8")
(root / "private" / "provenance.md").write_text(
    "# Synthetic fixture\n\nAuthored for this tutorial after strategy freeze. The input and evaluator "
    "are visible in the tutorial; this is development evidence, not a real failure-derived holdout.\n",
    encoding="utf-8")
(root / "private" / "evaluate.py").write_text("""import argparse, json
from pathlib import Path
p = argparse.ArgumentParser()
p.add_argument("--output", type=Path, required=True)
p.add_argument("--public", type=Path, required=True)
p.add_argument("--report", type=Path, required=True)
a = p.parse_args()
try:
    value = json.loads((a.output / "occupancy.json").read_text(encoding="utf-8"))
    ok = (isinstance(value, dict) and set(value) == {"union_seconds", "naive_sum_seconds"}
          and all(type(v) is int for v in value.values())
          and value == {"union_seconds": 9, "naive_sum_seconds": 10})
    detail = "Exact synthetic artifact check"
except (OSError, ValueError) as error:
    ok, detail = False, str(error)
a.report.write_text(json.dumps({"verdict": "pass" if ok else "fail", "detail": detail}) + "\\n", encoding="utf-8")
raise SystemExit(0 if ok else 1)
""", encoding="utf-8")
def ref(path):
    return {"path": path, "sha256": hashlib.sha256((root / path).read_bytes()).hexdigest()}
meta = {"id": "window-demo", "type": "blind-task", "domain": "interval-audit",
        "role": "development", "public_dir": "public/window-demo",
        "evaluator": ref("private/evaluate.py"), "provenance": ref("private/provenance.md")}
(root / "target.md").write_text("---\n" + json.dumps(meta, indent=2) +
    "\n---\n\nSynthetic released target; no novelty or Agent-benefit claim.\n", encoding="utf-8")
PYCODE
python3 -B scripts/blind_trials.py release --root "$PAG_DEMO" \
  --id synthetic-study --file "$PAG_DEMO/target.md" > "$PAG_DEMO/evidence/release.json"
python3 -B scripts/blind_trials.py schedule --root "$PAG_DEMO" \
  --id synthetic-study > "$PAG_DEMO/evidence/schedule.json"
```

排程包含六项：每个任务/重复块都有两路，种子打乱块顺序及各块内路序。保存并遵守该顺序。再次执行 `schedule` 不会运行任务，也不会注册调度器。生成排程时，策略、已发布输入或绑定的验收器/来源发生变化会被拒绝；不能原地修好文件再沿用旧冻结。

用于诊断的目标转为开发证据，保留失败，以未暴露的保留任务验证下一次 holdout 主张。一次任务里的多个断言或命令不构成独立重复。所有尝试都计入预算，包括重试和取消。

## 3. 准备真实请求，再使用已授权 CLI

下一段仅为保存的排程中下一项准备**一份请求**，核对冻结、发布记录、模型配置和目录清单，并把证据链接写入 Markdown 正文，不启动进程。runner 自身不会把请求自动关联到冻结研究，也不执行全局排程约束；宿主须保存这次核对并审阅后续每份请求。前一项记录完成后，设置 `PAG_RUN_INDEX=1`（再依次为 2 等）重新运行本段。确需重试时保持排程索引，设置 `PAG_ATTEMPT=2`，保留第一次尝试；重试也必须在预定总预算内。

<!-- demo:request -->
```sh
python3 -B - <<'PYCODE'
from pathlib import Path
import hashlib, json, os
root = Path(os.environ["PAG_DEMO"])
def read_md(path):
    lines = path.read_text(encoding="utf-8").splitlines()
    return json.loads("\n".join(lines[1:lines.index("---", 1)]))
def ref(path):
    return {"path": path, "sha256": hashlib.sha256((root / path).read_bytes()).hexdigest()}
schedule = json.loads((root / "evidence/schedule.json").read_text(encoding="utf-8"))
frozen = read_md(root / "blind-trials/synthetic-study/frozen.md")
assert schedule["model_config"] == frozen["plan"]["model_config"]
assert schedule["frozen_sha256"] == ref("blind-trials/synthetic-study/frozen.md")["sha256"]
run_index = int(os.environ.get("PAG_RUN_INDEX", "0"))
assert 0 <= run_index < len(schedule["runs"])
run = schedule["runs"][run_index]  # Advance only after preserving the preceding result.
attempt = int(os.environ.get("PAG_ATTEMPT", "1"))
assert attempt >= 1
released = read_md(root / ("blind-trials/synthetic-study/tasks/" + run["task_id"] + ".md"))
assert released["frozen_sha256"] == schedule["frozen_sha256"]
assert run["public_dir"] == released["task"]["public_dir"]
strategy = frozen["plan"]["arms"][run["arm"]]
for relative, expected in ((strategy, frozen["strategies"][run["arm"]]),
                           (run["public_dir"], released["public_inventory"])):
    actual = {p.relative_to(root / relative).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in (root / relative).rglob("*") if p.is_file()}
    assert actual == expected
prompt_path = "prompts/" + run["id"] + "-a" + str(attempt) + ".txt"
(root / prompt_path).write_text(
    "Read skill/SKILL.md, then input/task.md. Do the task using only assigned inputs. "
    "Save the requested artifact under output/. Report checks and unknowns. "
    "Do not seek private graders, other arms, past answers, or external effects.\n", encoding="utf-8")
trial_id = run["id"] + "-a" + str(attempt)
spec = {"id": trial_id, "type": "agent-trial-request", "task_id": run["task_id"],
        "arm": run["arm"], "replicate": run["replicate"], "attempt": attempt,
        "public_dir": run["public_dir"], "strategy_dir": strategy, "prompt": ref(prompt_path),
        "evaluator": released["task"]["evaluator"], "model_config": schedule["model_config"],
        "deadline_seconds": frozen["plan"]["deadline_seconds"], "max_commands": 12,
        "codex_binary": os.environ.get("PAG_CODEX", "codex")}
path = root / "requests" / (trial_id + ".md")
body = ("Prepared request only; no Agent has been started.\n"
        + "Freeze SHA-256: " + schedule["frozen_sha256"] + "\n"
        + "Released target SHA-256: " + ref("blind-trials/synthetic-study/tasks/" + run["task_id"] + ".md")["sha256"] + "\n"
        + "Schedule SHA-256: " + ref("evidence/schedule.json")["sha256"] + "\n")
with path.open("x", encoding="utf-8") as f:
    f.write("---\n" + json.dumps(spec, indent=2) + "\n---\n\n" + body)
(root / "evidence/next-request.txt").write_text(str(path) + "\n", encoding="utf-8")
print(path)
print("No Agent started; host authorization and protected evaluation are still required.")
PYCODE
```

真实运行前，以实际获准的模型和新目标另建研究；默认 `protocol-demo-no-model` 有意使用非模型标签。各路保持可见模型、推理强度、权限、指定输入、策略加载规则、二进制版本与传输一致。先检查本机 CLI 的 `exec --help` 是否支持 `run_agent_trial.py` 构造的参数，包括 `--ignore-user-config`；保存帮助、版本及实际命令。复用 CLI 现有登录，不复制认证文件，不改全局设置，不用本地伪响应冒充 Agent 证据。

**执行前须独立保护验收器。** 名为 `private/` 的目录和 `workspace-write` 不会让文件不可读。`blind_trials.py` 只核验验收器在 public 目录之外，且字节不与公开输入相同。宿主必须提供并核验真实读取边界，例如分别受控的验收身份/服务与获准的隔离读取环境，同时让 controller 能实际执行验收。每次只交付该路策略和公开输入；阻止读取其他路、答案、验收器/报告及旧尝试，并审阅真实工具/访问轨迹。本地 runner 无法提供该边界时，停在请求准备阶段，使用获准隔离宿主，不能称为盲测。

以下命令仅用于**已经授权并完成保护**的研究，会启动真实 Codex 调用，可能产生费用：

```sh
PAG_REQUEST="$(cat "$PAG_DEMO/evidence/next-request.txt")"
python3 -B scripts/run_agent_trial.py --root "$PAG_DEMO" \
  --request "$PAG_REQUEST" > "$PAG_DEMO/evidence/actual-run.json" \
  2> "$PAG_DEMO/evidence/actual-run.stderr"
PAG_EXIT=$?
printf '%s\n' "$PAG_EXIT" > "$PAG_DEMO/evidence/actual-run.exit"
```

runner 把指定输入复制到 `agent-work/<id>/input`，策略复制到 `skill`，可选的策略 `memory/` 复制到 `learning/`。提示词明确要求读取 `skill/SKILL.md`。调用参数使用新的 ephemeral CLI 上下文，关闭无关的自动 Skill、apps、plugins、memories 与 multi-agent 上下文，不更改全局配置。进程期限最多 3,600 秒、命令上限最多 100。命令上限检测已经开始的超额命令，不是保证超额命令从未启动的前置审批门。

检查 `agent-runs/<id>/runner.json`、`events.jsonl`、`timeline.jsonl`、`stderr.txt`、存在时的 `final.txt`、`measurement.json`、实际生成时的 `grade.json` 以及验收器输出。进程退出、`grader_exit_code`、报告内容、输入/策略完整性、成本记录成功分别验收。runner 返回 JSON 或零码不等于质量通过。缺失产物仍记缺失。停止本地调用后，远端工作、费用或外部效果可能未知；重试前先核实，不能借试次提示词新增联网、联系或部署权限。

## 4. 导入原生使用量和时钟，不重复计数

真实 runner 已生成绑定哈希的 `cost-request.md` 与不可覆盖的 `trial-costs/<id>.md`。独立采集的调用可使用同一精确字段：`id`、`type: "task-cost-request"`、`task_id`、`arm`、`replicate`、`attempt`、`model_config`，以及 `events`、`timeline`、`measurement` 的 `{path, sha256}` 引用。保留原生事件原始字节，不从后写摘要重建缺失使用量或时钟。

`timeline.jsonl` 每个事件一行，含从零开始的 `event_index` 与相对 **Agent 进程启动**的单调 `offset_seconds`。measurement 含 `elapsed_seconds`、`agent_start_offset`、`agent_elapsed_seconds`、整数 `exit_code` 及可选 `phase_spans`。阶段区间相对**完整试次开始**，使用 `preparation`、`agent`、`research`、`retry`、`grading`、`review`、`delivery`。保留时钟原点与采集方式。重连、失败回合、未关闭命令时钟与使用量错误继续可见；无效事件流应拒绝，不能猜补成合法格式。

以下可运行夹具使用**虚构的原生形状事件和时钟**，包括一次失败回合，仅测试解析，不能混入真实资源总额。

<!-- demo:cost -->
```sh
python3 -B - <<'PYCODE'
from pathlib import Path
import hashlib, json, os
root = Path(os.environ["PAG_DEMO"])
folder = root / "evidence" / "synthetic-cost"
folder.mkdir()
events = [
    {"type": "thread.started", "thread_id": "synthetic-not-a-provider-receipt"},
    {"type": "turn.started"},
    {"type": "item.started", "item": {"id": "one", "type": "command_execution"}},
    {"type": "item.started", "item": {"id": "two", "type": "command_execution"}},
    {"type": "item.completed", "item": {"id": "one", "type": "command_execution"}},
    {"type": "item.completed", "item": {"id": "two", "type": "command_execution"}},
    {"type": "turn.completed", "usage": {"input_tokens": 100, "cached_input_tokens": 40,
                                        "output_tokens": 20, "reasoning_output_tokens": 8}},
    {"type": "turn.started"}, {"type": "error", "message": "Synthetic reconnect failure"},
    {"type": "turn.failed"}
]
offsets = [0, 0.1, 1, 2, 4, 5, 6, 6.5, 7, 8]
(folder / "events.jsonl").write_text("".join(json.dumps(e) + "\n" for e in events), encoding="utf-8")
(folder / "timeline.jsonl").write_text("".join(json.dumps({"event_index": i, "offset_seconds": t}) + "\n"
                                               for i, t in enumerate(offsets)), encoding="utf-8")
measurement = {"elapsed_seconds": 12, "agent_start_offset": 1,
               "agent_elapsed_seconds": 9, "exit_code": 1,
               "phase_spans": [{"phase": "preparation", "start": 0, "end": 1},
                               {"phase": "agent", "start": 1, "end": 10},
                               {"phase": "research", "start": 2, "end": 6},
                               {"phase": "grading", "start": 10, "end": 12}]}
(folder / "measurement.json").write_text(json.dumps(measurement) + "\n", encoding="utf-8")
def ref(name):
    path = "evidence/synthetic-cost/" + name
    return {"path": path, "sha256": hashlib.sha256((root / path).read_bytes()).hexdigest()}
spec = {"id": "synthetic-cost-a1", "type": "task-cost-request", "task_id": "synthetic-cost-task",
        "arm": "baseline", "replicate": 1, "attempt": 1,
        "model_config": {"model": "protocol-demo-no-model", "training": False},
        "events": ref("events.jsonl"), "timeline": ref("timeline.jsonl"),
        "measurement": ref("measurement.json")}
(root / "cost-request.md").write_text("---\n" + json.dumps(spec, indent=2) +
    "\n---\n\nSYNTHETIC parser fixture, not native execution or billing evidence.\n", encoding="utf-8")
PYCODE
python3 -B scripts/task_costs.py --root "$PAG_DEMO" \
  --request "$PAG_DEMO/cost-request.md" > "$PAG_DEMO/evidence/synthetic-cost-record.json"
```

检查 `evidence/synthetic-cost-record.json` 或对应 Markdown。下表只是该夹具对应的数值，不是 Agent 实测结果：

| 数量 | 正确解释 |
|---|---|
| 输入 100，其中缓存输入 40；输出 20，其中推理明细 8 | 已知总量 **120**，不是 168。缓存已在输入中，推理明细已在输出中。 |
| 一次完成后又发生错误和失败回合 | 保留 120 为已知小计；`coverage` 为 `partial_or_unavailable`。失败尝试未返回的使用量未知。 |
| 命令区间 `[1,4]` 与 `[2,5]` | 已观察命令并集 **4 秒**，不是 6 秒。 |
| Agent 9 秒，完整试次 12 秒 | 两者嵌套，不能相加为 21 秒，也不能把工具/研究另加到父区间。 |
| 未归因 Agent 时间 5 秒 | 可能含模型、网络与宿主开销；`model_inference_seconds` 保持 `null`。 |
| 没有账单回执 | `billed_usd` 保持 `null`，意为未知而非免费。token 和账号额度变化不等于实收费用。 |

runner 的计时窗口从输入/策略装配开始，到外部验收完成为止，不含更早的研究/工具/来源开发以及更晚的规范化、审阅或发布。另记开销账本，保留实际起止、命令与回执，把对任务有用的预习、检索和修复计入比较总边界。大量实际任务工作在窗口外时，不能把 runner 窗口称为完整用户任务。`controller_total_seconds` 包含 controller 规范化时间，也包含已测窗口，不能与后者相加。

重叠使用区间并集，父窗口外使用不重叠增量。共享的研究准备/来源/工具/发布成本单列，不对每一路反复整额计费。保留每次尝试及计量覆盖。哈希绑定证明内容身份，不认证提供者；有真实账单时另与提供者回执核对。辅助程序没有费用导入器或模型推理时间估算器。

## 5. 写明来源机制、目标图和显式映射

因果映射提出试验，不证明真实因果、用途或权限。经验保留原标签与证据，可选 `causal_model` 增加 `variables`、有向 `relations` 与 `predictions`。查询以 `causal_context` 提供同形图，并用**来源经验 ID** 索引 `causal_mappings`。每个映射精确包含 `variables`、`rationale`、`prediction`、`falsifier`。

来源变量必须恰好全部覆盖，不同来源变量不能合并。目标变量须存在，声明的角色相同，每条来源关系须保持方向与关系标签。ID 可以不同。角色/关系标签是规范化后的精确匹配，不是自动推断的语义等价。预测要写可观察干预和反证，仍须实际核验。仅查询 facts 可以把未知条件写成 `null`；来源必要条件和已观察条件须为布尔值。未知或冲突的前提会阻止试用。

下一段先实际计算并哈希一个微型来源算术产物，再保存**假设**，不虚构独立审阅者或 Agent 使用。目标的领域、问题结构与机制标签均不同，只由显式映射关联。反向查询保留一个旧标签，使被拒项仍能出现在检索列表。第三份查询保留图结构，但否定必要条件。

<!-- demo:causal -->
```sh
python3 -B - <<'PYCODE'
from pathlib import Path
import hashlib, json, os
root = Path(os.environ["PAG_DEMO"])
def md(path, metadata, body):
    with (root / path).open("x", encoding="utf-8") as f:
        f.write("---\n" + json.dumps(metadata, indent=2) + "\n---\n\n" + body + "\n")
# Controlled integer-second arithmetic, independent of the helper's interval code.
source_intervals = [[0, 4], [2, 6]]
source = {"scope": "synthetic stdlib arithmetic, no Agent", "intervals": source_intervals,
          "sum_seconds": sum(b-a for a, b in source_intervals),
          "union_seconds": len(set().union(*(set(range(a, b)) for a, b in source_intervals)))}
path = "evidence/source-arithmetic.json"
(root / path).write_text(json.dumps(source) + "\n", encoding="utf-8")
source_ref = {"path": path, "sha256": hashlib.sha256((root / path).read_bytes()).hexdigest()}
model = {"variables": {"stages": "input intervals", "wall": "elapsed measurement"},
         "relations": [{"from": "stages", "to": "wall", "relation": "determines union"}],
         "predictions": [{"intervention": "Overlap two same-clock intervals",
                          "expected": "Union is smaller than their duration sum",
                          "falsifier": "The metric is aggregate worker time, not elapsed occupancy"}]}
md("experience-candidate.md", {
    "id": "synthetic-union", "type": "mechanism-experience", "source_task_id": "synthetic-build-source",
    "domain": "build-timing", "problem_structure": ["overlapping-stages"],
    "mechanisms": ["interval-union"],
    "required_conditions": {"same clock": True, "elapsed metric": True},
    "exceptions": ["Aggregate worker time may legitimately add overlapping durations."],
    "intervention": "Use the interval union for elapsed time, not the duration sum.",
    "explanation": "Overlapping portions occupy the same elapsed seconds.",
    "validation": "hypothesis", "executor": "tutorial/stdlib", "reviewer": None,
    "artifacts": [source_ref], "causal_model": model
}, "Synthetic sourced candidate. Arithmetic is checked; Agent usefulness is untested.")
target = {"variables": {"bookings": "input intervals", "occupied": "elapsed measurement"},
          "relations": [{"from": "bookings", "to": "occupied", "relation": "determines union"}],
          "predictions": [{"intervention": "Overlap two bookings on the same clock",
                           "expected": "Occupied seconds are less than summed booking seconds",
                           "falsifier": "The actual requirement counts person-seconds"}]}
mapping = {"variables": {"stages": "bookings", "wall": "occupied"},
           "rationale": "Both are half-open same-clock intervals with elapsed union as the quantity.",
           "prediction": "For [0,5) and [4,9), union is 9 while sum is 10.",
           "falsifier": "A person-seconds or separate-clock requirement rejects this use."}
query = {"id": "synthetic-occupancy-query", "type": "transfer-query", "task_id": "synthetic-occupancy-target",
         "domain": "room-occupancy", "problem_structure": ["room-bookings"],
         "mechanisms": ["occupied-seconds"], "facts": {"same clock": True, "elapsed metric": True},
         "keywords": [], "causal_context": target, "causal_mappings": {"synthetic-union": mapping}}
md("target-query.md", query, "No shared labels; explicit mapping proposes a hypothesis.")
reverse = json.loads(json.dumps(query))
reverse["id"] = "synthetic-reversed-query"
reverse["problem_structure"] = ["overlapping-stages"]  # Keep the rejected row visible via a legacy label.
reverse["causal_context"]["relations"][0].update({"from": "occupied", "to": "bookings"})
md("reversed-query.md", reverse, "Counterexample: relation direction is reversed; reject the analogy.")
conflict = json.loads(json.dumps(query))
conflict["id"] = "synthetic-condition-conflict"
conflict["facts"]["same clock"] = False
md("condition-conflict.md", conflict, "A matching graph cannot override a contradicted prerequisite.")
PYCODE
python3 -B scripts/experience_transfer.py add --root "$PAG_DEMO" \
  --experience "$PAG_DEMO/experience-candidate.md" > "$PAG_DEMO/evidence/experience-added.json"
python3 -B scripts/experience_transfer.py retrieve --root "$PAG_DEMO" \
  --query "$PAG_DEMO/target-query.md" > "$PAG_DEMO/evidence/mapped-query.json"
python3 -B scripts/experience_transfer.py retrieve --root "$PAG_DEMO" \
  --query "$PAG_DEMO/reversed-query.md" > "$PAG_DEMO/evidence/reversed-query.json"
python3 -B scripts/experience_transfer.py retrieve --root "$PAG_DEMO" \
  --query "$PAG_DEMO/condition-conflict.md" > "$PAG_DEMO/evidence/condition-conflict.json"
```

检查候选行：

| 查询 | 应有的协议决策 |
|---|---|
| `target-query.md` | `causal_match.status: structurally_compatible`，没有共同标签，`eligible_for_probe: true`。只表示条件允许做有限试验，不是采用许可。 |
| `reversed-query.md` | `compatible: false`，包含 `directed_relations_not_preserved`，`eligible_for_probe: false`，拒绝类比。 |
| `condition-conflict.md` | 图可以相符，但 `same clock` 冲突且 `eligible_for_probe: false`。图不能推翻实际前提。 |

缺来源模型、角色不符、来源变量合并或关系未覆盖也会阻止因果匹配。没有模型时保留旧标签检索的有限语义，领域相同本身不准入候选。检查 `errors`、全部相关负反馈与跨领域反例，不能只看排序分。同领域有害反馈可阻止试用；外领域有害反馈须审查适用性。JSON 输出是派生视图，不可覆盖的 Markdown 经验与观察日志继续作为语义记录。扩展旧经验时新增有来源的候选，绑定旧记录实际路径/哈希，不覆盖原件。

## 6. 先执行后续核验，再写观察记录

下一段使用标准库集合执行目标算术，先保存实际结果，再准备观察。尽管合成算术返回 9 而不是简单求和的 10，对 **Agent 迁移收益**仍记 `inconclusive`。新目标 task ID 与来源不同。这是可执行的实际后续证据记录示例，不是 Agent 迁移成功示例。

<!-- demo:followup -->
```sh
python3 -B - <<'PYCODE'
from pathlib import Path
import hashlib, json, os
root = Path(os.environ["PAG_DEMO"])
intervals = json.loads((root / "public/window-demo/windows.json").read_text(encoding="utf-8"))
result = {"scope": "actual execution of a synthetic stdlib arithmetic check; no Agent",
          "intervals": intervals, "sum_seconds": sum(b-a for a, b in intervals),
          "union_seconds": len(set().union(*(set(range(a, b)) for a, b in intervals)))}
path = "evidence/target-arithmetic.json"
with (root / path).open("x", encoding="utf-8") as f:
    f.write(json.dumps(result) + "\n")
assert result["union_seconds"] == 9 and result["sum_seconds"] == 10
observation = {"id": "synthetic-followup-01", "type": "transfer-observation",
    "task_id": "synthetic-occupancy-target", "domain": "room-occupancy",
    "conditions": {"same clock": True, "elapsed metric": True}, "outcome": "inconclusive",
    "adaptation": "Applied the union calculation only in this controlled arithmetic check.",
    "finding": "Actual synthetic calculation returned union 9 and sum 10; no Agent used this lesson, so Agent transfer benefit is unknown.",
    "executor": "tutorial/stdlib", "reviewer": None,
    "artifacts": [{"path": path, "sha256": hashlib.sha256((root / path).read_bytes()).hexdigest()}]}
with (root / "followup.md").open("x", encoding="utf-8") as f:
    f.write("---\n" + json.dumps(observation, indent=2) + "\n---\n\n"
            "The arithmetic ran before this record was authored. Reversed mapping and the condition conflict remain rejected.\n")
print(json.dumps(result))
PYCODE
python3 -B scripts/experience_transfer.py status --root "$PAG_DEMO" \
  --id synthetic-union > "$PAG_DEMO/evidence/before-followup.json"
python3 -B scripts/experience_transfer.py observe --root "$PAG_DEMO" \
  --id synthetic-union --observation "$PAG_DEMO/followup.md" \
  --expected-revision 0 > "$PAG_DEMO/evidence/after-followup.json"
```

本例只有一个写入者，追加前 revision 为 0。共享使用时先读 `status`，审阅 `revision` 并提交该值。遇到过期 revision，应重读并解决观察意图，不能盲目重交。被拒映射和失败条件与后续正面证据一并保留，不能把这条算术记录改叫 `helpful` 来暗示 Agent 学会了。

真实目标须由已授权 Agent 实际读取经验，采用/调整/拒绝它，必要时执行任务，保留产物及相关宿主轨迹。记录预测、最强反例、条件变化与观察结果。`helpful` 要求不同的声明审阅者及已核验产物，但声明身份本身不认证独立性。拒绝经验也可提供有用证据；一段拒绝理由或预测文字仍不等于执行结果。

## 7. 按全部试次决定，保留回退

先独立验收质量，再核对每个已排任务/重复及全部尝试。失败、取消、缺使用量、已暴露目标和配置不可比项都留在报告中。不要挑最快一次，不把断言数当任务数，不删除失败成本。按冻结指标、收益门槛和质量/资源护栏，在任务层比较成对重复；当前辅助程序不自动提供统计比较，也不自动关联冻结、runner、验收与账单。

分别报告质量、原生 token 及覆盖、完整任务时间、准备/修复/审阅开销和实际费用覆盖。未知或不可比可使收益主张变为无法判定。两路都正确不证明改进；token 更少不证明实收费用更低。候选未达预定收益或任何护栏时，保留原策略与候选失败证据。

限定范围采用前继续通过既有 PPC 组合与回归门槛，保存启用版本和回退路径。组合变化或修复已暴露目标后，须重新冻结并使用未暴露保留任务，才能提出新的 holdout 主张。后续任务必须实际加载并使用、调整或拒绝经验，留存结果；未来计划本身不增加迁移证据。把下一项有用工作写回既有 Markdown context/项目 node；宿主调度另行处理。

<!-- Copyright (C) 2026 KARMENLOOP Official Team. SPDX-License-Identifier: AGPL-3.0-only -->

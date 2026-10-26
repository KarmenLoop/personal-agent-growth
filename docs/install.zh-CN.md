# 完整安装、升级与卸载说明 · 0.4.1

[English](install.md) · [实际教程](tutorial.zh-CN.md) · [完整离线包](../开始使用.md)

## 1. 选对交付物与位置

发布页有两种附件：核心 `personal-agent-growth-0.4.1.zip` 含 Skill、双语协议、模板和工具；**完整交付包**另含全部源代码、测试、经验种子、双语长文和图源，适合离线保存。核心包中未附带的长文链接指向版本化 GitHub 文档。需要完整经验库和离线教程时，使用完整包及其中的安装器。

需要已正常使用的宿主账号、可读写的本地目录和 Python 3.11+；工具只用标准库，无需 pip。Mac 先执行 `python3 --version`，Windows 执行 `py -3 --version`。没有 Python 时可先读取 Markdown，但不能声称已运行工具。安装器不创建账号、后台进程、定时任务或跨设备同步。

推荐技能根目录 Mac 为 `~/Desktop/AgentKnowledge`，Windows 有 D 盘用 D、否则 C；无写权限则改用户目录。私人 Markdown 根目录另设为 `AgentKnowledge/learning`，或明确与 Koder 共用 `~/.koder/learning`。已有知识库继续使用，不以新空库覆盖。

```text
AgentKnowledge/
  skills/personal-agent-growth/   技能原件
  downloads/0.4.1/                发布附件
  learning/                      私人 Markdown 知识
  tasks/                         运行材料、实验与原始回执
  experience/                    完整包可选历史种子，与当前画像分开
```

## 2. macOS 核心包安装

在 Terminal 执行完整代码块。已有技能或发现入口时停止，先按升级流程处理。下载的 manifest 与 ZIP 校验用于检查一致性，不构成独立发布者签名。

```bash
(
  set -e
  GrowthRoot="$HOME/Desktop/AgentKnowledge"
  GrowthSkillsRoot="$HOME/.agents/skills"
  SkillDir="$GrowthRoot/skills/personal-agent-growth"
  SkillEntry="$GrowthSkillsRoot/personal-agent-growth"
  ReleaseDir="$GrowthRoot/downloads/0.4.1"
  ReleaseUrl="https://github.com/KarmenLoop/personal-agent-growth/releases/download/v0.4.1"
  if [ -e "$SkillDir" ] || [ -L "$SkillDir" ] || [ -e "$SkillEntry" ] || [ -L "$SkillEntry" ]; then
    echo "An installation already exists. Follow the update section." >&2
    exit 1
  fi
  mkdir -p "$ReleaseDir" "$GrowthRoot/skills" "$GrowthRoot/tasks" "$GrowthSkillsRoot"
  curl --fail --location --retry 2 --max-time 90 "$ReleaseUrl/personal-agent-growth-0.4.1.zip" -o "$ReleaseDir/personal-agent-growth-0.4.1.zip"
  curl --fail --location --retry 2 --max-time 90 "$ReleaseUrl/manifest.json" -o "$ReleaseDir/manifest.json"
  python3 - "$ReleaseDir" <<'PY'
import hashlib, json, pathlib, sys
p = pathlib.Path(sys.argv[1])
m = json.loads((p / 'manifest.json').read_text(encoding='utf-8'))
assert m['archive']['name'] == 'personal-agent-growth-0.4.1.zip'
assert hashlib.sha256((p / m['archive']['name']).read_bytes()).hexdigest() == m['archive']['sha256'], 'ZIP checksum mismatch'
print('Archive hash matches the supplied manifest')
PY
  unzip -q "$ReleaseDir/personal-agent-growth-0.4.1.zip" -d "$GrowthRoot/skills"
  python3 -B "$SkillDir/scripts/verify_handoff.py" --archive "$ReleaseDir/personal-agent-growth-0.4.1.zip" --manifest "$ReleaseDir/manifest.json"
  ln -s "$SkillDir" "$SkillEntry"
  test -f "$SkillEntry/SKILL.md"
  printf 'Skill: %s\nDiscovery entry: %s\nTask memory: %s\n' "$SkillDir" "$SkillEntry" "$GrowthRoot/tasks"
)
```

应看到哈希一致、验包 PASS/退出 0 和三个路径。失败后保留输出；解压已完成但入口未建好时，检查原件，勿反复覆盖。

## 3. Windows 核心包安装

使用 PowerShell 5.1 或 7，不用 CMD。默认路径可按需修改。UTF-8 参数保留，尤其是中文、含空格路径和重定向输出。

```powershell
& {
  $ErrorActionPreference = 'Stop'
  $GrowthRoot = if (Test-Path -LiteralPath 'D:\') { 'D:\AgentKnowledge' } else { 'C:\AgentKnowledge' }
  $GrowthSkillsRoot = Join-Path $env:USERPROFILE '.agents\skills'
  $SkillDir = Join-Path $GrowthRoot 'skills\personal-agent-growth'
  $SkillEntry = Join-Path $GrowthSkillsRoot 'personal-agent-growth'
  $ReleaseDir = Join-Path $GrowthRoot 'downloads\0.4.1'
  $ReleaseUrl = 'https://github.com/KarmenLoop/personal-agent-growth/releases/download/v0.4.1'
  if ((Test-Path -LiteralPath $SkillDir) -or (Get-Item -LiteralPath $SkillEntry -Force -ErrorAction SilentlyContinue)) {
    throw 'An installation already exists. Follow the update section.'
  }
  New-Item -ItemType Directory -Force -Path $ReleaseDir, (Join-Path $GrowthRoot 'skills'), (Join-Path $GrowthRoot 'tasks'), $GrowthSkillsRoot | Out-Null
  $ZipPath = Join-Path $ReleaseDir 'personal-agent-growth-0.4.1.zip'
  $ManifestPath = Join-Path $ReleaseDir 'manifest.json'
  Invoke-WebRequest -UseBasicParsing -Uri "$ReleaseUrl/personal-agent-growth-0.4.1.zip" -OutFile $ZipPath
  Invoke-WebRequest -UseBasicParsing -Uri "$ReleaseUrl/manifest.json" -OutFile $ManifestPath
  $Manifest = Get-Content -LiteralPath $ManifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
  if ($Manifest.archive.name -ne 'personal-agent-growth-0.4.1.zip') { throw 'Unexpected archive name.' }
  if ((Get-FileHash -LiteralPath $ZipPath -Algorithm SHA256).Hash -ne $Manifest.archive.sha256) {
    throw 'ZIP checksum mismatch. Nothing has been extracted.'
  }
  Expand-Archive -LiteralPath $ZipPath -DestinationPath (Join-Path $GrowthRoot 'skills')
  py -3 -B -X utf8 (Join-Path $SkillDir 'scripts\verify_handoff.py') --archive $ZipPath --manifest $ManifestPath
  if ($LASTEXITCODE -ne 0) { throw 'Package verification failed; inspect the output.' }
  New-Item -ItemType Junction -Path $SkillEntry -Target $SkillDir | Out-Null
  if (-not (Test-Path -LiteralPath (Join-Path $SkillEntry 'SKILL.md'))) { throw 'Discovery entry is unreadable.' }
  Write-Output "Skill: $SkillDir"
  Write-Output "Discovery entry: $SkillEntry"
  Write-Output "Task memory: $(Join-Path $GrowthRoot 'tasks')"
}
```

检查安装结果可再次运行：

```powershell
$GrowthRoot = if (Test-Path -LiteralPath 'D:\') { 'D:\AgentKnowledge' } else { 'C:\AgentKnowledge' }
py -3 -B -X utf8 (Join-Path $GrowthRoot 'skills\personal-agent-growth\scripts\verify_handoff.py') --archive (Join-Path $GrowthRoot 'downloads\0.4.1\personal-agent-growth-0.4.1.zip') --manifest (Join-Path $GrowthRoot 'downloads\0.4.1\manifest.json')
if ($LASTEXITCODE -ne 0) { throw 'Verification did not pass.' }
```

Junction 需要支持目录联接的文件系统；没有权限时可将解压的完整文件夹直接放到发现目录。Finder 替身或 Windows `.lnk` 不是文件系统链接。Windows 实际命令验收与桌面 Agent 行为分别记录，见[验收范围](compatibility.zh-CN.md)。

## 4. 手动安装、项目级使用与其他环境

从 [v0.4.1](https://github.com/KarmenLoop/personal-agent-growth/releases/tag/v0.4.1)下载名称准确的附件与对应 manifest。GitHub 自动生成的 Source code ZIP 与安装附件用途不同。解压整个文件夹到 `.agents/skills/personal-agent-growth`；应直接看到 `SKILL.md`，不要多套一层目录。

用户级与项目级入口二选一；项目级使用 `<project>/.agents/skills`。Linux 可用 Mac 步骤，把根目录改成 `$HOME/AgentKnowledge`。WSL、SSH、云端各有自己的文件系统、账号与权限；相同路径字符串不会自动共享数据。跨设备先配置获准传输/挂载并保存路径映射。

## 5. 确认宿主真实读取

Codex/Cursor 支持 Agent Skills 的版本可发现 `.agents/skills`；重新打开宿主或项目并选择技能。以当前界面为准。找不到时用绝对路径显式读取：

> 读取 <技能绝对路径>/SKILL.md，报告声明版本 0.4.1、解析后路径，以及本任务所需 reference/script 是否可读。私人学习根目录为 <绝对路径>。按 Markdown 协议恢复当前项目，说明实际读取的 context、最新 node 与来源修订。此次安装检查不创建定时任务。

目录存在、自动发现、自动选择、实际执行是不同证据。显式读取可用于工作，但应如实标记。接下来按[完整教程](tutorial.zh-CN.md)完成有产物的预习与复习。

## 6. 共用记忆与可选 MCP

两个宿主读取同一真实目录、同一项目 ID 与最新修订；原 writer 完成写入、保留产物并交还责任，接收方核对后再写。只读一份复制件不算共享。Markdown 学习按[记忆契约](markdown-learning.zh-CN.md)运行。

既有 `scripts/host.py` 是独立可选的 SQLite 交接适配器，提供五个 `growth_*` 工具。配置、批准和真实模型使用分别验证；它不实现日周 Markdown 系统。使用方法见[教程中的适配器章节](tutorial.zh-CN.md#adapter)。不要让两套可写状态控制同一项目进度。

## 7. 未来复习与通知

有间隔复习、等待新输入等用途时，再授权当前宿主登记真实调度。保存任务、下一动作、期限、轮次、责任方与绑定 ID；回读后端，收到真实事件后执行并核验，完成后停止。只在用户需要决定时主动联系，不发送无变化的例行通知。

宿主无调度接口时保存“未登记”，不能把一个 Markdown 计划写成已安排。进程内空闲回调、人工继续和关闭应用后的 OS 唤醒属于不同层次。[调度规则](../references/autonomous-continuation.md)说明完整链路。

## 8. 完整离线包与经验种子

完整包中运行 `python3 -B tools/check_delivery.py .`，再按[开始使用](../开始使用.md)安装到一个新根目录。安装器保留分发副本、复制经验种子并建立空 tasks；不会创建发现入口或自动启动任务。经验库历史方法需符合当前用途，不能冒充当前用户画像或新运行。

独立 Koder 候选的 `learning` 命令不在本 Skill 安装范围。当前公开版提供协议、模板和工具；候选产品的原生自动注入仍受它自己的验收限制。

## 9. 升级、回滚与卸载

升级前结束当前写入，暂停会读取旧文件的绑定并核实。分别备份技能和记忆，在新的版本目录下载/验包，比较个性化修改后切换技能入口。保留现有 learning/tasks，不把新的经验种子索引覆盖到活跃库。新对话核对路径与版本，再恢复一个任务。

回滚只恢复已知可用的技能版本，保留新产生的事实、失败与较新任务修订，先确认兼容性再继续。不要拿旧记忆备份覆盖当前真相。

卸载前先通过宿主停止相关调度，若配置过 MCP，备份配置后仅移除 `personal_agent_growth` 这一条并重载宿主。删除技能文件不会注销后端任务或 MCP 配置。

Mac 先运行 `readlink "$HOME/.agents/skills/personal-agent-growth"` 确认目标，再用 `unlink "$HOME/.agents/skills/personal-agent-growth"` 删除这一链接。Windows 确认显示目标正是待移除技能后执行：

```powershell
$SkillEntry = Join-Path $env:USERPROFILE '.agents\skills\personal-agent-growth'
$Entry = Get-Item -LiteralPath $SkillEntry -Force
if ($Entry.LinkType -ne 'Junction') { throw 'This is not the expected junction. Inspect it first.' }
Write-Output $Entry.Target
cmd /c rmdir "$SkillEntry"
if ($LASTEXITCODE -ne 0) { throw 'The junction was not removed.' }
```

以上只移除发现入口，保留原件和记忆。完整包安装器可进一步核对并移除未修改的技能：`python3 -B <root>/distribution/tools/local_install.py uninstall --root <root>`；遇到新增或修改文件会拒绝，保留 experience、tasks、distribution 和安装收条。手动安装先把原件移出发现目录，私人记忆由用户自行决定是否另行删除。

## 10. 故障定位

| 现象 | 检查和处理 |
|---|---|
| 找不到技能 | 文件夹层级、实际运行用户/系统、权限、重载；显式读取作为备用 |
| 已有安装 | 读取原版本并升级，勿强制覆盖 |
| 中文输出失败 | `py -3 -X utf8`，明确 UTF-8 解码 |
| 下载 HTML/哈希不符 | 核对附件名称与版本，不跳过校验 |
| 两个工具进度不同 | 核对解析路径、ID、修订、writer 和产物哈希 |
| 有计划但没有唤醒 | 查后端登记、绑定、真实事件和宿主状态 |
| Windows PS5 模块异常 | PS7 下启动 PS5 的子进程可清掉子进程 PSModulePath，使其重建；不改全局变量 |
| 低置信标签驱动规划 | 读取证据链与算法版本，降级标签并检查依赖计划 |

安装目录依据 [Agent Skills 规范](https://agentskills.io/specification)、[Cursor Skills 文档](https://cursor.com/docs/skills)与宿主实际能力核对。保留 [LICENSE](../LICENSE) 与 [NOTICE](../NOTICE)。发布验收与历史证据见[兼容性](compatibility.zh-CN.md)。

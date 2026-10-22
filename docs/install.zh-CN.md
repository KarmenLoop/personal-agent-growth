# 完整安装说明

[English guide](install.md) · 适用版本：**0.3.3** · 宿主文档核对日期：2026 年 10 月 21 日。

本说明覆盖：安装 → 宿主识别 → 初始化私人记忆 → 第一次实际任务 → Codex / Cursor 接续复习 → 可选定时唤醒 → 更新、回滚与卸载。按自己系统选择安装命令即可，不需要先下载源码或配置开发环境。

## 1. 安装前准备

需要已能正常使用的本地 Codex 或 Cursor，且当前版本支持 Skills、能读取所选目录。继续使用宿主原有的模型账号和文件、工具权限；这个 skill 没有单独的账号或 API Key。

安装时需要联网下载 GitHub 发布包。macOS 命令使用“终端”及 `curl`、`shasum`、`unzip`；Windows 使用 **PowerShell 5.1 或更高版本**。只有运行附带的离线验包程序或执行 Python 任务时，才需要 **Python 3.11 或更高版本**。读取 skill 本身不需要 Python，也不需要 Node、Docker 或 `pip install`。

推荐目录：

| 用途 | macOS | Windows |
|---|---|---|
| 知识库根目录 | `~/Desktop/AgentKnowledge`，即桌面 | 有 D 盘：`D:\AgentKnowledge`；否则：`C:\AgentKnowledge` |
| 技能原件 | `<根目录>/skills/personal-agent-growth` | `<根目录>\skills\personal-agent-growth` |
| 发布包与清单 | `<根目录>/downloads/0.3.3` | `<根目录>\downloads\0.3.3` |
| 私人任务记忆 | `<根目录>/tasks/<任务ID>` | `<根目录>\tasks\<任务ID>` |
| 宿主发现入口 | `~/.agents/skills/personal-agent-growth` | `%USERPROFILE%\.agents\skills\personal-agent-growth` |

当前 Codex 和 Cursor 的官方文档都列出了 `.agents/skills`。下面为两者建立**同一个入口，指向同一份技能原件**：Mac 使用符号链接，Windows 使用目录联接（Junction）。无需再向 `.cursor/skills` 或 `.codex/skills` 重复复制同名 skill，避免选中不同版本。

可在运行前修改 `GrowthRoot`，选择自己的位置。如果 D 盘或 C 盘根目录不可写，可改为 `C:\Users\<你的用户名>\AgentKnowledge` 等可写目录，不必修改整个磁盘的权限。

## 2. macOS 安装

打开“终端”，复制下面**整个代码块**并执行。命令会下载固定版本、核对 ZIP 和 manifest 的 SHA-256、解压并创建发现入口。检测到已有安装就停止，不覆盖原件。

```bash
(
  set -eu
  GrowthRoot="$HOME/Desktop/AgentKnowledge"
  GrowthSkillsRoot="$HOME/.agents/skills"
  SkillDir="$GrowthRoot/skills/personal-agent-growth"
  SkillEntry="$GrowthSkillsRoot/personal-agent-growth"
  ReleaseDir="$GrowthRoot/downloads/0.3.3"
  ReleaseUrl="https://github.com/KarmenLoop/personal-agent-growth/releases/download/v0.3.3"

  if [ -e "$SkillDir" ] || [ -L "$SkillDir" ] || [ -e "$SkillEntry" ] || [ -L "$SkillEntry" ]; then
    echo "An installation already exists. Follow the update section instead."
    exit 1
  fi

  mkdir -p "$ReleaseDir" "$GrowthRoot/skills" "$GrowthRoot/tasks" "$GrowthSkillsRoot"
  curl --fail --location --retry 2 --max-time 90 "$ReleaseUrl/personal-agent-growth-0.3.3.zip" -o "$ReleaseDir/personal-agent-growth-0.3.3.zip"
  curl --fail --location --retry 2 --max-time 90 "$ReleaseUrl/manifest.json" -o "$ReleaseDir/manifest.json"

  printf '%s  %s\n' '5c385b2cb0cee07d4f713c9734e02abe262c4b96905f618543731b81a9d8a76a' "$ReleaseDir/personal-agent-growth-0.3.3.zip" | shasum -a 256 -c -
  printf '%s  %s\n' '88be0aa807dc971bfa4f15c105d98abf521eedc3a386001ec17ebc45be36f765' "$ReleaseDir/manifest.json" | shasum -a 256 -c -

  unzip -q "$ReleaseDir/personal-agent-growth-0.3.3.zip" -d "$GrowthRoot/skills"
  ln -s "$SkillDir" "$SkillEntry"
  test -f "$SkillEntry/SKILL.md"
  printf 'Skill: %s\nDiscovery entry: %s\nTask memory: %s\n' "$SkillDir" "$SkillEntry" "$GrowthRoot/tasks"
)
```

正常结果：两条校验结果以 `OK` 结尾，随后输出 `Skill`、`Discovery entry` 和 `Task memory` 三个路径。变量只在这个代码块内有效，后续例子会自行指定路径。

解压后的技能原件包含以下 **8 个文件**：

```text
personal-agent-growth/
├── SKILL.md
├── references/
│   ├── task-record.md
│   ├── learning-and-contact.md
│   ├── autonomous-continuation.md
│   └── shared-memory.md
├── scripts/
│   └── verify_handoff.py
├── LICENSE
└── NOTICE
```

## 3. Windows 安装

打开 **PowerShell**，不要使用 CMD。复制并执行整个代码块。它自动优先选择 D 盘，没有 D 盘则使用 C 盘；如需自选位置，先修改 `$GrowthRoot`。

```powershell
& {
  $ErrorActionPreference = 'Stop'
  $GrowthRoot = if (Test-Path -LiteralPath 'D:\') { 'D:\AgentKnowledge' } else { 'C:\AgentKnowledge' }
  $GrowthSkillsRoot = Join-Path $env:USERPROFILE '.agents\skills'
  $SkillDir = Join-Path $GrowthRoot 'skills\personal-agent-growth'
  $SkillEntry = Join-Path $GrowthSkillsRoot 'personal-agent-growth'
  $ReleaseDir = Join-Path $GrowthRoot 'downloads\0.3.3'
  $ReleaseUrl = 'https://github.com/KarmenLoop/personal-agent-growth/releases/download/v0.3.3'

  if ((Test-Path -LiteralPath $SkillDir) -or (Test-Path -LiteralPath $SkillEntry)) {
    throw 'An installation already exists. Follow the update section instead.'
  }

  New-Item -ItemType Directory -Force -Path $ReleaseDir, (Join-Path $GrowthRoot 'skills'), (Join-Path $GrowthRoot 'tasks'), $GrowthSkillsRoot | Out-Null
  $ZipPath = Join-Path $ReleaseDir 'personal-agent-growth-0.3.3.zip'
  $ManifestPath = Join-Path $ReleaseDir 'manifest.json'
  Invoke-WebRequest -UseBasicParsing -Uri "$ReleaseUrl/personal-agent-growth-0.3.3.zip" -OutFile $ZipPath
  Invoke-WebRequest -UseBasicParsing -Uri "$ReleaseUrl/manifest.json" -OutFile $ManifestPath

  if ((Get-FileHash -LiteralPath $ZipPath -Algorithm SHA256).Hash -ne '5c385b2cb0cee07d4f713c9734e02abe262c4b96905f618543731b81a9d8a76a') {
    throw 'ZIP checksum mismatch. Nothing has been extracted.'
  }
  if ((Get-FileHash -LiteralPath $ManifestPath -Algorithm SHA256).Hash -ne '88be0aa807dc971bfa4f15c105d98abf521eedc3a386001ec17ebc45be36f765') {
    throw 'Manifest checksum mismatch. Nothing has been extracted.'
  }

  Expand-Archive -LiteralPath $ZipPath -DestinationPath (Join-Path $GrowthRoot 'skills')
  New-Item -ItemType Junction -Path $SkillEntry -Target $SkillDir | Out-Null
  if (-not (Test-Path -LiteralPath (Join-Path $SkillEntry 'SKILL.md'))) {
    throw 'The discovery entry cannot read SKILL.md.'
  }
  Write-Output "Skill: $SkillDir"
  Write-Output "Discovery entry: $SkillEntry"
  Write-Output "Task memory: $(Join-Path $GrowthRoot 'tasks')"
}
```

正常结果会输出三个安装路径，技能原件同样应有上面的 8 个文件。Junction 需要支持目录联接的本地文件系统和相应写入权限。如果解压成功但创建联接失败，技能原件已经存在；检查入口位置，或改用下面的手动安装，不要反复覆盖解压。

安装和卸载命令已在真实 Windows Server 2025 上，通过 PowerShell 5.1、7 两套环境验收，覆盖默认 D 盘和 C 盘中文、含空格路径。共享记忆由独立测试进程实际恢复和写回；没有将其冒充为 Windows 桌面 Agent 行为实测。详见 [真实验收结果与边界](windows-install-verification.md)。

## 4. 手动安装、项目级安装及其他环境

### 不使用命令安装

1. 打开 [v0.3.3 发布页](https://github.com/KarmenLoop/personal-agent-growth/releases/tag/v0.3.3)，下载名为 `personal-agent-growth-0.3.3.zip` 和 `manifest.json` 的附件。不要把 GitHub 自动生成的“Source code”压缩包当成这个安装包。
2. 使用上面命令中的 SHA-256 校验方法或自己的校验工具，对比：

   | 文件 | SHA-256 |
   |---|---|
   | `personal-agent-growth-0.3.3.zip` | `5c385b2cb0cee07d4f713c9734e02abe262c4b96905f618543731b81a9d8a76a` |
   | `manifest.json` | `88be0aa807dc971bfa4f15c105d98abf521eedc3a386001ec17ebc45be36f765` |

3. 解压，将**整个** `personal-agent-growth` 文件夹放入当前用户的 `.agents/skills`。结果必须是 `.agents/skills/personal-agent-growth/SKILL.md`，中间不要再套一层同名目录。
4. 单独创建 `AgentKnowledge/tasks` 保存私人任务记忆。这种手动方案的技能原件直接位于 `.agents/skills`，后续检查命令应使用这个实际路径。
5. Mac 的 Finder 选择“前往 → 前往文件夹”，输入 `~/.agents/skills`；Windows 资源管理器地址栏输入 `%USERPROFILE%\.agents\skills`。不存在时先创建目录。Finder 的“替身”和 Windows 的 `.lnk` 快捷方式不能替代前面命令创建的文件系统链接。

本仓库是独立 skill，没有 Cursor 插件市场清单；不要假定 Cursor 的“从 GitHub 导入插件”能直接安装这个仓库。

### 只让一个项目使用

运行安装代码块前，把 `GrowthSkillsRoot` 改成该项目的绝对 `.agents/skills` 路径，再在 Codex / Cursor 中打开该项目。同一个 skill 在用户级和项目级二选一放置，避免重复入口。私人记忆放在公开仓库之外，或明确排除版本控制。

### Linux、WSL、SSH 与云端

Linux 可沿用 Mac 命令，将根目录改成 `$HOME/AgentKnowledge`，并确认有 `curl`、`unzip`、`shasum`；如果使用 `sha256sum`，把 `shasum -a 256 -c -` 改成 `sha256sum -c -`。

WSL、SSH 有各自的用户目录和权限。Windows 安装成功不代表 WSL 已经安装；共享 `/mnt/d` 等路径前，先核实执行环境里确实挂载并可读写。云端 Agent 也不能仅凭聊天里的桌面或 D 盘路径访问本地文件。跨设备需要另外配置获准的同步、传输或挂载方式，并保存路径映射。

## 5. 检查 Codex / Cursor 是否真正读到

在每个宿主里开启一个新对话。Codex 有 Skills 界面时选中该 skill；CLI / IDE 可使用 `/skills` 或 `$` 技能提及。Cursor 可用 `/` 搜索技能名，或在支持的位置用 `@` 附加。具体入口以当前版本界面为准。

没有显示时，检查发现目录，重新打开项目或重启宿主。也可以直接给出 `SKILL.md` 的绝对路径让 Agent 读取；这应记录为“显式加载”，不能当作已验证自动匹配。

将下面两处占位符替换成实际绝对路径后发送：

> 读取 <技能目录>/SKILL.md，以及本次任务需要的引用文件。报告技能目录解析后的真实路径、声明版本、4 份 reference 和 scripts/verify_handoff.py 是否可读。本次任务的私人记录放在 <任务目录>。这次安装检查不要创建定时任务。

预期应看到 `0.3.3`、正确的真实路径、所有资源可读。文件存在只是安装层验证，后面的实际任务才检查有没有真正使用技能。

### 可选：运行附带的验包程序

先运行 Mac 的 `python3 --version` 或 Windows 的 `py -3 --version`，确认使用 Python 3.11+。没有合适版本时，可从 [Python 官网](https://www.python.org/downloads/) 安装受支持版本，再重新打开终端。不需要安装 pip 依赖。

Mac 默认路径：

```bash
python3 "$HOME/Desktop/AgentKnowledge/skills/personal-agent-growth/scripts/verify_handoff.py" \
  --archive "$HOME/Desktop/AgentKnowledge/downloads/0.3.3/personal-agent-growth-0.3.3.zip" \
  --manifest "$HOME/Desktop/AgentKnowledge/downloads/0.3.3/manifest.json"
echo "Exit code: $?"
```

Windows 默认 D / C 盘选择：

```powershell
$GrowthRoot = if (Test-Path -LiteralPath 'D:\') { 'D:\AgentKnowledge' } else { 'C:\AgentKnowledge' }
py -3 -X utf8 (Join-Path $GrowthRoot 'skills\personal-agent-growth\scripts\verify_handoff.py') --archive (Join-Path $GrowthRoot 'downloads\0.3.3\personal-agent-growth-0.3.3.zip') --manifest (Join-Path $GrowthRoot 'downloads\0.3.3\manifest.json')
Write-Output "Exit code: $LASTEXITCODE"
```

自选位置或手动安装请改成实际路径。正常应为 **PASS、退出码 0、31 项检查**。退出码 1 表示检查发现问题，2 表示检查未完成；Python 本身没启动时，不能给安装包下结论。该程序验证 ZIP 与所给 manifest 的一致性，不验证发布者身份，也不证明 Agent 行为。详见 [manifest 说明](manifest.md)。

Windows 调用验包程序时保留 `-X utf8`，从其他进程调用时也一样。Python 3.11 默认的重定向输出编码可能无法表示中文路径，导致写出 JSON 前出现 `UnicodeEncodeError`。读取保存的 JSON 或子进程输出时明确使用 UTF-8；任务记忆文件也应明确采用 UTF-8，不依赖不同 PowerShell 版本的默认编码。

## 6. 初始化私人记忆，完成第一次实际任务

为当前任务选一个目录，例如：

- Mac：`~/Desktop/AgentKnowledge/tasks/install-review`。
- Windows：`D:\AgentKnowledge\tasks\install-review`，无 D 盘则用 C 盘。
- 传给两个宿主时使用同一个**完整绝对路径**，将 `~` 展开成实际用户路径。

建议结构：

```text
tasks/install-review/
├── task.md                 # 目标、范围、完成标准、当前索引
├── state.json              # 任务 ID、修订、阶段、writer、下一步
├── memory/
│   ├── preferences.json    # 用户明确表达的偏好及来源
│   └── lessons.md          # 证据、改判、适用范围
└── evidence/               # 实际命令、输出、输入身份和结果
```

Agent 按任务需要创建或复用这些记录，小任务可以更精简。安装本身不会自动导入聊天历史，也不会自动生成完整个人画像。

替换路径后，发送下面的首次任务：

> 使用 <技能目录> 的 Personal Agent Growth，任务记忆放在 <任务目录>。完成一次有实际用途的安装复习：先记录你预测哪些资源可用及其理由；再读取已安装 skill 和引用文件，有 Python 条件时实际运行附带的发布包检查程序。保存真实命令、退出码、输出和输入文件身份。资源或环境假设失败时，先判断原因，针对缺口补课、修正并重新验证，记录什么证据改变了判断。创建或复用 task.md、state.json 和证据索引。记录我的偏好：能自己解决就先完成，只有必须我决定时才联系我；不要编造我的个人属性。给下一宿主留下具体的复习动作。这次安装复习不创建自动化。

完成后检查实际输出、学习变化和下一步。Python 暂不可用时，可以先完成文件与资源检查，并准确记录未完成的验包部分。

## 7. 让 Cursor / Codex 接手续做与复习

切换前，让原宿主完成当前写入、保存产物，将 `writer` 交给接收方并递增 `state_revision`。两边必须读取同一个实际任务目录。这是协作写入规则，当前 skill 不提供数据库锁或自动同步服务。

在接收方发送：

> 读取 <技能目录>/SKILL.md，从 <任务目录> 的实际文件恢复任务。先报告 task_id、state_revision、writer、解析后的任务目录和下一动作。根据之前的预测、错误与经验完成待办复习，实际复用已有检查程序或产物，保存新输出，说明是否需要改变之前的判断，并写回同一份状态。写入前再次读取修订号；如果其他执行方已经推进，保留新事实并先处理交接，不能覆盖。不要另建一份记忆，也不要为了接续额外开无用对话。

验收看三点：**读到了当前修订、复用了原有产物、把新结果写回同一目录**。需要进一步检查是否只是在重复旧聊天时，可以在真实交还责任后写入一条有用的新决定或反例，再让接收方按新修订复习；不要为演示而制造无意义工作。

冲突处理和证据归属见 [共享记忆规则](../references/shared-memory.md)。

## 8. 可选：授权一次未来的自主复习

复制 skill 不会自动创建定时器。只有需要间隔复习、等待外部结果或新输入时，才安排未来唤醒；眼下能做的工作直接完成。

替换任务路径后，可发送以下授权：

> 请针对 <任务目录>，使用当前宿主支持的正式调度接口，在我当前时区的明天上午 9 点进行一次复习。先检查有没有已有绑定，最多允许 2 轮自动运行，登记后 48 小时到期。保存目标、复习动作、完成标准、期限和调度责任方；实际登记后回读配置，记录后端 ID。收到真实宿主触发时，从最新状态恢复、执行复习并留存证据，根据结果调整或结束后续。完成后实际暂停或删除调度并核实。普通问题自行解决，只有需要我做决定时才问我，不发送例行进度通知。

宿主有通知设置时要实际设置，不能认为提示词一定能关闭通知。调度接口不可用时，保存原因和“尚未登记”的下一步，不能声称已经后台运行。

完整验收链应是：**登记并回读 → 真实宿主事件 → 恢复状态 → 实际执行 → 结果验证 → 调整或停止后端**。计划文件或单独的 `ACTIVE` 状态不能替代这条链。已有实测覆盖 Codex 原生唤醒，没有建立 Cursor 原生调度或关闭应用后运行的结论；当前能力要在实际宿主核实。详见 [自主接续规则](../references/autonomous-continuation.md)。

## 9. 更新、回滚和卸载

### 更新 skill

1. 先完成或暂停正在写入的任务；有调度会使用待替换文件时，先暂停该绑定，记录当前责任方与修订。
2. 分别备份技能原件和任务记忆。用户改写过的 skill 连同改动依据一并保留。
3. 将目标新版本及对应 manifest 下载到新的版本目录，使用**该版本**的校验值。本文两个 SHA-256 只适用于 **0.3.3**。
4. 在暂存目录解压，检查版本、资源和验包结果；比较本地改动后再决定如何合并。
5. 将旧技能目录改名备份，把新 `personal-agent-growth` 目录放到原来的技能路径。发现入口可保持不变，单独的 `tasks` 不动。
6. 在新对话里确认加载路径、版本，再复习一个现有任务；需要恢复暂停的调度时，通过宿主接口实际恢复并回读。

手动安装的原件就是 `.agents/skills/personal-agent-growth`。有意保留多份副本时，每份都要更新、检查。开发者也可以使用 Git clone，但更新前应检查本地修改与目标修订，不要用破坏性的 reset 丢掉个人改动。

### 回滚

暂停受影响的写入和调度，保留失败候选与证据，将备份技能恢复到同一路径，再核实加载版本。任务记忆里的新事实应保留，先检查兼容性，不用旧备份直接覆盖较新的状态。

### 卸载

1. 先通过宿主暂停或删除本任务绑定的调度，并回读确认。删文件不会自动注销定时器。
2. 删除发现入口。推荐 Mac 布局可用下面命令，它只删除符号链接：

   ```bash
   if [ -L "$HOME/.agents/skills/personal-agent-growth" ]; then
     unlink "$HOME/.agents/skills/personal-agent-growth"
   else
     echo "No symbolic link removed. Inspect the installed directory first."
   fi
   ```

   Windows 先确认是 Junction，再使用非递归删除命令：

   ```powershell
   $SkillEntry = Join-Path $env:USERPROFILE '.agents\skills\personal-agent-growth'
   $Entry = Get-Item -LiteralPath $SkillEntry -Force
   if ($Entry.LinkType -ne 'Junction') { throw 'This is not the expected junction. Inspect it first.' }
   cmd /c rmdir "$SkillEntry"
   if ($LASTEXITCODE -ne 0) { throw 'The junction was not removed.' }
   ```

3. 重新打开宿主。技能原件与私人记忆可以继续保留或归档。手动直接放入发现目录的安装，则把整个技能文件夹移出发现目录；只有确实不需要时才删除私人记忆。

## 10. 常见问题

| 问题 | 处理 |
|---|---|
| 看不到技能 | 检查 `.agents/skills/personal-agent-growth/SKILL.md` 的层级、实际执行环境和访问权限；重开宿主，必要时显式读取。 |
| 出现两个同名技能 | 查看各入口的真实路径与版本，确认后移走旧入口。 |
| 提示已有安装 | 先查看原版本，按更新流程处理，不强制覆盖。 |
| 联接或链接创建失败 | 检查文件系统、可写位置和残留入口；必要时采用直接文件夹安装。 |
| 下载成 HTML 或哈希不符 | 下载发布页里名称准确的附件，重新校验，不跳过不一致。 |
| 没有 Python 或版本偏低 | 安装 Python 3.11+ 或明确指定对应解释器；读取 Markdown 不受影响。 |
| 捕获的验包输出为空或出现 `UnicodeEncodeError` | 使用 `py -3 -X utf8` 或 `python -X utf8`，并按 UTF-8 解码输出。 |
| 从其他程序启动的 PowerShell 5.1 找不到 `Get-FileHash` | 直接打开 Windows PowerShell；如果由 PowerShell 7 下的 Python 启动，只在子进程环境中去掉 `PSModulePath`，让 5.1 重建自己的模块路径，不修改全局设置。 |
| 两边都说共用记忆，但修订不同 | 核对真实路径、task_id、文件内容和 writer；跨设备相同字符串不等于同一文件。 |
| 只写计划，没有复习结果 | 显式选择 skill，提供具体产物和验收条件，再核对实际命令及输出。 |
| 没有自动唤醒 | 检查正式后端登记、绑定、宿主可用性、期限和轮次上限；安装本身不创建调度。 |
| 远程宿主无法读取 | 配置获准的同步、传输或挂载及路径映射；聊天里的路径不会自动传输文件。 |

## 已验证范围与资料

链接的 v0.3.2 历史记录涵盖 Linux、macOS Intel、Windows 的工具与验包检查；当前 v0.3.3 结果记录在 GitHub Actions；另有 Codex 实际唤醒、同一 Mac 上 Cursor 共享记忆恢复的历史实测。这些是不同层次的证据，不代表每个新对话都能自动选中 skill，也不代表所有平台的 Agent 行为都已验证。详见 [发布验收](release-0.3.2-acceptance.md) 和 [验证范围](validation.md)。

宿主安装位置和使用方式核对自 [OpenAI Skills 官方文档](https://learn.chatgpt.com/docs/build-skills)、[Cursor Skills 官方文档](https://cursor.com/docs/skills) 和 [Cursor 定制帮助](https://cursor.com/help/customization/skills)。Windows 命令参考 [New-Item 联接说明](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/new-item?view=powershell-7.5) 与 [Expand-Archive](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.archive/expand-archive?view=powershell-7.5)。

保留安装包中的 [AGPL-3.0-only 协议](../LICENSE) 和 [NOTICE](../NOTICE)。复制与分发修改版时应保留对应声明，具体义务见 [协议说明](licensing.md)。

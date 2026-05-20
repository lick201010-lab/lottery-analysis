# Agent 协作规范 — 弈彩 (YiCai)

## Codex 模型选择

Codex 支持两个模型，根据任务难度选用：

| 任务类型 | 模型 | 命令 |
|---------|------|------|
| 简单任务（单文件修改、批量重命名、简单重构） | `gpt-5.4` | `codex --model gpt-5.4 --dir D:/lottery-dev "<任务>"` |
| 复杂任务（多步重构、跨文件修改、架构设计） | `gpt-5.5` | `codex --dir D:/lottery-dev "<任务>"`（默认） |

**判断标准**：需要 3 步以上操作、或涉及多个文件、或需要推理规划 → 用 gpt-5.5；反之 → gpt-5.4。

## Codex 运行配置（自动优化）

已在 `~/.codex/config.toml` 配置：
- `reasoning_effort = "high"`
- `enable_request_compression = true`（压缩冗余上下文）
- `multi_agent = true`（最多 3 个并行子任务）
- `hooks = true`（自动 Hook 注入）

## 角色分工

| 角色 | 工具 | 职责 |
|------|------|------|
| **Yvette** | 微信/指令 | 方向性决策、验收结果 |
| **Hermes (我)** | 本地终端 + 工具 | 整体协调、部署、复杂修复 |
| **Codex** | `codex --dir .` | 终端复杂任务（多步重构、批量修改） |
| **Kimi Code** | VSCode 插件 | 快速单文件修改 |

## 开发流程

### 分支模型

```
main                — 稳定分支，不直接提交
dev/mobile-layout   — 手机界面开发
feature/build-env   — 构建/部署自动化
production          — 线上同步分支
```

### Worktree 结构

```
D:/lottery          — 主仓库 (main)
D:/lottery-dev      — dev/mobile-layout，业务代码改动只在这里
D:/lottery-build    — feature/build-env（含本地版 deploy.sh）
D:/lottery-production — production
```

## PR 规则（核心规范）

**每轮修改完成后，Hermes 和 Codex 必须各自总结并提交 PR，不得跳过。**

### 规则细则

1. **提交时机**：每完成一个完整的功能修复或一批相关的修改，就提交一次 PR。
2. **PR 内容**：
   - 标题：`[Agent] <简短描述>`，如 `[Agent] fix: 修复手机端奖金表格溢出`
   - 正文：列出改了什么、为什么改、怎么验证
3. **分支命名**：
   - `hermes/fix-xxx` — Hermes 提交的分支
   - `codex/fix-xxx` — Codex 提交的分支
4. **Codex 的 PR**：Codex 跑完后，Hermes 负责检查 Codex 的修改内容，合并到 `dev/mobile-layout` 或相应分支。
5. **冲突处理**：如果与主分支有冲突，先在本地解决冲突再提 PR。
6. **审核**：简单修复 Hermes 直接合并；复杂功能由 Yvette 确认后再合并。

### 自动分支注入 + 存档（Hooks）

通过 Git hooks 自动执行：
- 每次 commit 后自动推送到对应分支
- 自动归档会话记录到 `~/.codex/sessions/`

```bash
# 在 D:/lottery-dev 初始化 hooks（一次性）
cd D:/lottery-dev
git config core.hooksPath ~/.codex/hooks
```

## 部署规则

### 真实部署流程（手动）

> ⚠️ **本文件历史版本写过「服务器每 5 分钟自动 git pull」——这个机制不存在**。merge PR 到 main 之后，部署是手动的。

**目标服务器**：阿里云轻量应用服务器，香港，IP `47.237.181.181`，root SSH 登录，项目路径 `/opt/lottery-analysis`。

**完整部署步骤**（每次 merge PR 到 main 之后跑一次）：

```bash
# 1. SSH 进服务器（或登阿里云控制台 Workbench）
ssh root@47.237.181.181
cd /opt/lottery-analysis

# 2. 检查脏文件（服务器侧偶尔有未回流的改动）
git status -sb

# 3. 如有脏文件：先备份，再 reset
mkdir -p ~/backup-$(date +%Y%m%d) && \
  cp <脏文件> ~/backup-$(date +%Y%m%d)/ && \
  git checkout -- <脏文件>

# 4. 拉远端 main
git pull

# 5. 前端重建
cd frontend && npm run build

# 6. 后端重启（用现成脚本）
bash /opt/lottery-analysis/restart.sh

# 7. 验证
ps aux | grep "uvicorn app.main:app" | grep -v grep
curl -s -X POST http://localhost:8000/api/v1/jackpot/scrape
```

### 部署相关位置

- 服务器项目路径：`/opt/lottery-analysis`
- 重启脚本：`/opt/lottery-analysis/restart.sh`（git pull + pkill uvicorn + nohup 重启）
- 后端日志：`/opt/uvicorn.log`
- 前端 dist：`/opt/lottery-analysis/frontend/dist/`（Caddy 直接服务）
- 构建辅助 worktree：`D:/lottery-build`（含本地版 `deploy.sh`，需 SSH key 已上服务器）

### Hotfix

生产出问题，从 `production` 分支切 hotfix 分支处理。

## 沟通约定

- Hermes 通过微信推送关键状态（部署完成、构建失败、需要决策）
- 长时间任务（>5分钟）完成后主动汇报
- 不确定的问题先查证再回复，不猜测

---

## Harness Engineering（驾驭工程）

> 适用于所有 agent：Claude Code、Codex、Kimi Code。

### 核心原则

**Agent = Model + Harness**。瓶颈不是模型智能，是工程基础设施。每当 agent 犯错，工程化一个解决方案防止重复发生。

### 任务启动前 checklist

1. 读 `AGENTS.md`（本文件）最新版
2. 读最新 `HANDOFF_*.md`（如 `D:/lottery-dev/` 下存在）
3. 确认本轮目标文件列表
4. 确认工作目录是 `D:/lottery-dev`（不要在 `D:/lottery`、`D:/lottery-build`、`D:/lottery-production` 改业务代码）

### 提交前 checklist

```powershell
cd D:\lottery-dev\frontend; npm run build
cd D:\lottery-dev\backend; python -m compileall app
cd D:\lottery-dev; git diff --name-only         # 确认只动了目标文件
```

### 硬约束

| 约束 | 规则 |
|------|------|
| Worktree 隔离 | 业务代码改动只在 `D:/lottery-dev` |
| 文件白名单 | 只改 HANDOFF 或用户指令中的目标文件 |
| 后端验证门 | `python -m compileall app` 通过才能提交 |
| 前端验证门 | `npm run build` 通过才能提交 |
| PR 必须提 | 每轮完成后提 PR，标题 `[Agent] <动词>: <描述>` |
| **部署后必验证** | 用户说"merge 完了/部署完了"后，**禁止**直接报告成功，必须 fetch chunk 内容 grep 新代码标识，确认上线（详见已知陷阱 #7）|

### 失败时更新 Harness

踩坑 → 把修复方案写进本文件的「已知陷阱」章节。任务未完成 → 创建 `HANDOFF_YYYY-MM-DD_<功能名>.md`。

完整 Harness 指南：`skills/harness-engineering/SKILL.md`（Claude Code 读）。

---

## 已知陷阱（Known Pitfalls）

每条都来自真实踩坑。**修好之后必须留在这里**，避免下一个 agent 重蹈覆辙。

### 1. 服务器不会自动 git pull

**症状**：merge PR 到 main 后，过几分钟访问 `www.ckl.hk`，发现网站没变化。

**原因**：本文件历史版本写过「服务器每 5 分钟自动 git pull + restart.sh」，**这个机制根本不存在或从未启用**。服务器代码一直停在上一次手动 deploy 的状态。

**解决**：每次 merge 后必须手动跑「部署规则」节里的完整步骤。

**检测方法**：在服务器上跑 `git log -1 --oneline`，确认 HEAD hash 等于 `origin/main`。

### 2. SPA chunk URL 返回 200 不代表 chunk 存在

**症状**：探测 `https://www.ckl.hk/assets/About-XXXXXX.js` 返回 HTTP 200，以为文件已部署。

**原因**：Caddy 配置了 SPA fallback，**所有不存在的路径都返回 index.html**（200 + HTML body）。

**检测方法**：
- 看 `Content-Type` 是 `application/javascript` 还是 `text/html`
- 或抓 `https://www.ckl.hk/` 的 HTML，看 `<script src="/assets/index-XXX.js">` 引用的入口 hash
- 把入口 JS 拉下来，搜里面是否引用新组件名（如 `About`、`Privacy`）

### 3. lottery.hk 抓不到优先怀疑代码版本，不是反爬

**症状**：本地 scraper 能拿到 MarkSix `pool_amount`，prod 后端拿不到（`null`）。

**误判**：以为阿里云香港 IP 被 lottery.hk 反爬。

**真因**：服务器 uvicorn 跑的是旧版代码（git pull 了但进程没重启），新版 scraper 的 `_merge_marksix_detail` 函数根本没在跑。

**检测方法**：
```bash
ssh root@47.237.181.181 'ps -o pid,lstart -p $(pgrep -f "uvicorn app.main:app")'
```
看 uvicorn 启动时间。如果远早于最近一次 deploy，说明没重启。

### 4. 服务器侧可能有未回流的脏文件

**症状**：服务器 `git status` 显示 modified 文件（典型如 `backend/app/routers/jackpot.py`、`backend/app/services/jackpot_scraper.py`、`frontend/src/views/Dashboard.vue`）。

**原因**：早期 Codex 在服务器上直接改过代码做临时 hotfix，没回流到 GitHub。

**处理流程**：
1. 备份：`cp <脏文件> ~/backup-$(date +%Y%m%d)/`
2. 看差异：`git diff origin/main -- <脏文件>`
3. 选择：
   - 服务器版**少**于远端 → `git checkout -- <文件>` 丢弃
   - 服务器版**有独立修改且重要** → 手工 merge
4. `git pull`

### 5. data/marksix.db 在 git 跟踪里且会被运行时写入

**症状**：服务器 `git status` 永远显示 `data/marksix.db modified`。

**原因**：SQLite 数据库被 git 跟踪，但运行时 scrape 会写入。

**临时处理**：deploy 前 `git checkout -- data/marksix.db`，pull 完后服务器重新跑 scrape。

**长期处理（todo）**：加到 `.gitignore`，并 `git rm --cached data/marksix.db`。

### 6. 六合彩 vs 双色球：附加号规则完全不同

**核心规则差异**：

| 项目 | 六合彩 MarkSix | 双色球 SSQ |
|------|---------------|------------|
| 主号 | 6 个正码（1-49） | 6 个红球（1-33） |
| 附加号 | 1 个特码（1-49） | 1 个蓝球（1-16） |
| 头奖判定 | **只看 6 个正码** | **必须 6 红 + 1 蓝全中** |
| 附加号作用 | 提高奖等档次（5+特=二等） | 头奖必含、缺一不可 |
| UI 文案 | 「特码辅助参考 / 仅供参考」 | 「蓝球 / 头奖必含」 |
| UI 布局 | 主号大球独占一行，特码移到底部小行 | 6 红 + 1 蓝同行展示，对等权重 |

**踩坑**：写"模拟选号"模板时，第一版统一按六合彩的 `仅供参考` 文案处理 SSQ 蓝球，被用户指出是错的。SSQ 的蓝球不是辅助，是头奖必含。

**修复方案**（实现于 `frontend/src/views/GenerateNumbers.vue`）：
1. 加 `isSSQ = computed(() => lotteryType.value === "ssq")`
2. 用 `v-if="isSSQ"` 区分两套模板：
   - SSQ：6 红 + 1 蓝**同行大球**展示（用 `+` 分隔），文案"蓝球推荐（头奖必含）"
   - MarkSix：主号 6 个大球，特码移到底部小行 `🎲 特码辅助：...（仅供参考）`
3. 「推荐组合」一行里：SSQ 每组组合末尾自动补蓝球（用 special_pick）

**写新组件/页面时务必检查**：凡是涉及"附加号 / 特别号 / 特码 / 蓝球"的展示，都要区分 lottery_type，绝不能用同一套模板。

### 7. 用户说"部署完了"不等于代码上线，必须 chunk 验证

**踩坑**：用户 merge PR 后说"部署完了"，agent 直接报"上线成功"。实际上：
- prod 跑的 git pull 是在用户 merge **之前**触发的
- 或者用户只 merge 没跑部署
- 或者跑了别的部署命令但分支错了

结果：prod 跑的还是上一个版本，用户体验仍然有 bug，agent 还以为修好了。

**硬约束**：每次部署后，**必须用代码内容验证**，绝不能只看 git log 或 build 日志。

**验证套路**（PowerShell，30 秒）：

```powershell
# 1. 拿 prod index.html 的 entry bundle hash
$html = (Invoke-WebRequest -Uri "https://www.ckl.hk/" -UseBasicParsing).Content
$entry = [regex]::Match($html, 'assets/index-([A-Za-z0-9_-]+)\.js').Groups[1].Value

# 2. 从 entry 里找目标页的 lazy-load chunk
$idxJs = (Invoke-WebRequest -Uri "https://www.ckl.hk/assets/index-$entry.js" -UseBasicParsing).Content
$chunkName = [regex]::Match($idxJs, 'assets/(<目标页>-[A-Za-z0-9_-]+\.js)').Groups[1].Value

# 3. 拉 chunk，grep 这次新加的独特字符串
$chunk = (Invoke-WebRequest -Uri "https://www.ckl.hk/assets/$chunkName" -UseBasicParsing).Content
if ($chunk -match "<本次新加的中文文案>") { Write-Host "✅ live" } else { Write-Host "❌ not deployed" }
```

**关键点**：
- 不要用 bundle hash 对比（本地和 prod node 环境不同，hash 不一样很正常）
- 要选**这次 PR 才会出现的字符串**作为标识（如 "蓝球推荐"、新增的 emoji、新组件名等）
- 中文字符串在生产构建里通常不被压缩混淆，可以直接 grep
- chunk URL 返回 200 ≠ 新代码上线（Caddy SPA fallback 会把所有 404 转 index.html，已在陷阱 #2）

**如果验证失败的标准动作**：
1. SSH 进 prod 看 `git log --oneline -3`，确认最新 commit 是不是你期望的 PR
2. 如果不是 → `git fetch origin && git pull --ff-only && cd frontend && npm run build`
3. 重新跑验证脚本

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

### 失败时更新 Harness

踩坑 → 把修复方案写进本文件的「已知陷阱」章节。任务未完成 → 创建 `HANDOFF_YYYY-MM-DD_<功能名>.md`。

完整 Harness 指南：`skills/harness-engineering/SKILL.md`（Claude Code 读）。

---

## 已知陷阱（Known Pitfalls）

每条都来自真实踩坑。**修好之后必须留在这里**，避免下一个 agent 重蹈覆辙。

### 1. 服务器自动部署：cron polling（已上线 2026-05-21）

**机制**：服务器 cron 每 2 分钟跑一次 `/opt/lottery-analysis/auto-deploy.sh`：
- 比对 HEAD 和 origin/main，无差异 exit 0
- 有差异：`git pull` → 若 package.json 变化则 `npm install` → 若 frontend/ 变化则 `npm run build` → 若 backend/ 变化则重启 uvicorn（带 setsid 脱离 ssh）
- 不再自动重置 `data/marksix.db`；运行时 SQLite 只允许 scraper 写入，部署脚本不能 checkout 数据库

**日志**：`/var/log/yicai-deploy.log`
**脚本源码**：仓库根 `auto-deploy.sh`（每次改动后要手动 scp 上服务器，或服务器 git pull 后手动 chmod +x）

**注意事项**：
- merge PR 后**最多等 2 分钟**就上线，不用手动 ssh 跑部署
- 但**必须验证 chunk** 才能宣称成功（陷阱 #7）—— cron 可能没跑完、build 可能失败、Caddy 可能缓存
- 如果 2 分钟内没生效：`ssh root@... tail -30 /var/log/yicai-deploy.log` 看上次跑的输出
- 如果脚本本身有 bug 要修：改本地仓库的 `auto-deploy.sh` → cron 拉到后会自动用新版本

**历史**：曾经服务器有个 `restart.sh` cron 每 5 分钟跑，但它只 `git pull` 不 build 前端，且无条件重启 uvicorn。已被 auto-deploy.sh 替换。

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

**严禁处理**：不要在 `auto-deploy.sh` 或任何 cron 中执行 `git checkout -- data/marksix.db`。这会在 uvicorn 持有 SQLite 连接时替换运行时数据库文件，导致 `sqlite3.OperationalError: attempt to write a readonly database`，并让最新开奖数据回退。

**当前处理**：部署脚本只拉代码，不重置 DB。需要恢复 DB 时必须先备份、停后端、确认数据来源，再人工处理。

**长期处理（todo）**：加到 .gitignore，并 git rm --cached data/marksix.db。

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
### 8. auto-deploy 的管道不能吞掉失败

**症状**：`/var/log/yicai-deploy.log` 里出现 `Please commit your changes or stash them before you merge.`，但后面仍写了 `=== Deploy done ===`。

**原因**：`git pull 2>&1 | tail -3` 这类管道在没有 `pipefail` 时会隐藏左侧命令失败，`set -e` 不会中断脚本。

**修复方案**：`auto-deploy.sh` 必须使用 `set -eo pipefail`。以后如果在部署脚本里把关键命令接到 `tail` / `grep` / `sed` 管道后面，必须确认失败状态不会被吞掉。
### 9. 后端 502：服务器重启后 uvicorn 不会自动回来

**症状**：`https://api.ckl.hk/api/v1/health` 和模拟选号接口全部返回 502，前端按钮看起来像“坏掉”。服务器 `ps aux | grep "uvicorn app.main:app"` 查不到进程。

**原因**：uvicorn 不是 systemd 服务。服务器重启后，如果后续 auto-deploy 只拉取 `frontend/` 或数据文件变更，旧脚本不会启动后端，导致 API 长时间离线。

**修复方案**：`auto-deploy.sh` 必须在无代码变更时也执行 `/api/v1/health` 检查；失败就启动 `python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000`。脚本必须使用 `flock` 单实例锁，避免 cron 和人工执行同时启动多个 uvicorn。

**额外注意**：不要用裸 `pkill -f "uvicorn app.main:app"` 做测试或脚本匹配，远程 shell 命令行里只要包含这个字面串就可能被误杀。使用 `pkill -f "[u]vicorn app.main:app"`。

**验证方法**：先确认 `/api/v1/health` 200，再短暂停掉 uvicorn，运行 `bash /opt/lottery-analysis/auto-deploy.sh`，应自动恢复健康且 `pgrep -af '[u]vicorn app.main:app'` 只剩一个进程。
### 10. 新增彩种后不能只跑 jackpot scrape，必须回填历史库

**症状**：历史记录页切到新彩种时只显示 1 条或很少数据，例如 7星彩只显示最新一期，看起来像“数据库没了”。

**原因**：`POST /api/v1/jackpot/scrape` 只写入最新期开奖/奖池数据；它不会批量导入历史开奖。新彩种接入后如果没有跑 `/api/v1/scrape/trigger`，历史表和频率缓存都只有极少数据。

**修复方案**：新增或恢复彩种后，必须运行：
`POST /api/v1/scrape/trigger {"source":"github","lottery_type":"qxc"}`，并轮询 `/api/v1/scrape/status/{job_id}` 到 success。完成后检查 `/api/v1/draws?page=1&per_page=5&lottery_type=qxc` 和 `/api/v1/analysis/summary?lottery_type=qxc`。

**验证标准**：历史记录页对应彩种不应只显示 1 条；7星彩当前正常量级约 3358 条，且频率缓存返回 0-14 共 15 个编号。

### 11. MarkSix stale while other lotteries update: source route failure

**Symptom**: `POST /api/v1/jackpot/scrape` updates SSQ and QXC, but MarkSix stays on an older draw such as `26/075`. Health still returns OK and the SQLite DB is writable.

**Root cause pattern**: Production can time out when connecting to `lottery.hk`, while local development may still fetch it successfully. The old fallback source `kj.13322.com` may also be unavailable, so the service silently falls back to the stale DB row.

**Fix pattern**: MarkSix scraping should try the HKJC official GraphQL endpoint first:
`https://info.cld.hkjc.com/graphql/base/`.
Use the exact `marksixResult` whitelisted query shape from the HKJC frontend bundle. A custom reduced GraphQL query returns `WHITELIST_ERROR`.

**Verification**:
- Check `https://api.ckl.hk/api/v1/draws/latest?lottery_type=marksix`.
- Trigger `POST /api/v1/jackpot/scrape`.
- Check that MarkSix advances to the latest HKJC draw while SSQ/QXC still update.
- If API/SSH time out at the same time, treat it as a server availability issue first, not a scraper parser issue.

### 12. AdSense ads.txt must be served directly on every registered host

**Symptom**: AdSense reports `ads.txt` as not found for `ckl.hk`, even though
`https://yicai.ckl.hk/ads.txt` returns the correct publisher record.

**Cause**: The AdSense site is registered as `ckl.hk`, while the apex and `www`
hosts redirect every request to `yicai.ckl.hk`. AdSense discovery is more
reliable when `/ads.txt` returns the file directly from each registered host.

**Fix**: In Caddy, handle `/ads.txt` before the catch-all redirect for both
`ckl.hk` and `www.ckl.hk`. Keep all other paths on the existing 301 redirect.

**Verification**:
- `curl -I https://ckl.hk/ads.txt` returns `200`, not `301`.
- `curl -I https://www.ckl.hk/ads.txt` returns `200`, not `301`.
- Both responses use `Content-Type: text/plain` and contain the expected
  `google.com, pub-..., DIRECT, f08c47fec0942fa0` record.
- A normal page such as `/marksix/results` still redirects to the canonical
  `yicai.ckl.hk` URL.

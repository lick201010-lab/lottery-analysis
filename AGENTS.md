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

### 6. 全站 UI 主题重写前必须先做小范围 mock

**症状**：一次性替换 `style.css` 所有色板 token + 改 NavBar/AppFooter/Hero 等所有组件颜色，部署上线后用户验收不满意，全部 revert 推倒重来。

**原因**：UI 风格是高度主观决策，光看配色描述（"紫蓝渐变"、"莫兰迪暖米色"）和 ASCII 草图，用户无法预判真实视觉效果。**只有上线看真实页面才能拍板**。但全站铺开后再回滚，已经浪费了开发和验收时间。

**正确流程**：
1. 先选**一个最关键的区域**（如 Dashboard hero 主卡）做单独 mock
2. 不动 `style.css` 全局 token，只在该组件内 inline 新样式
3. 部署上线让用户看真实效果
4. **拿到明确"OK 全站铺"的反馈**后，再扩到 `style.css` 主题层
5. 如果用户犹豫，提供 2 个版本（如紫蓝 vs 暖色）让她 A/B 对比

**回滚兜底**：所有 UI PR 必须能用 `git revert -m 1 <merge_commit>` 一键还原。这次 PR #8 → PR #9 revert 验证过这个机制工作。

**判断标准**：动 `style.css` 的 `@theme` 块或 `body` 背景色，必属于"全站重写"，必须先 mock。

---
name: harness-engineering
description: Harness Engineering (驾驭工程) discipline for the 弈彩 YiCai project. Applies to all agents — Claude Code, Codex, Kimi Code. Covers constraint mechanisms, feedback loops, entropy management, and session continuity. Use when starting any task, encountering an agent failure, updating project docs, or doing a session handoff.
---

# Harness Engineering — 弈彩 YiCai

## 什么是 Harness Engineering

**公式**：Agent = Model + Harness

- **Model**：提供智能（你不能改）
- **Harness**：约束机制 + 反馈回路 + 状态管理 + 工具调度（你负责设计和维护）

核心原则（Mitchell Hashimoto, 2026-02-05）：
> 每当 agent 犯了一个错误，就花时间工程化一个解决方案，使 agent 将来不会再犯同样的错误。

瓶颈不是模型智能，而是工程基础设施。

---

## 四个核心组件

### 1. 上下文工程（Context Engineering）

**目标**：让 agent 在正确的知识框架内行动，而不是从零猜测。

本项目的上下文层级（按优先级）：

| 文件 | 读取时机 | 内容 |
|------|---------|------|
| `AGENTS.md` | 每次启动任务前 | 角色分工、PR 规则、部署流程 |
| `RULES.md` | 涉及 UI / 业务逻辑时 | 球色规则、彩种名称、响应式规范 |
| `skills/lottery-analysis/SKILL.md` | 涉及代码架构时 | 文件结构、数据源、技术栈 |
| `HANDOFF_*.md`（最新一份） | 接手未完成任务时 | 本轮目标、已改文件、下一步 |

**规则**：
- 开始任务前，必须确认已读 AGENTS.md 和最新 HANDOFF 文件（如存在）。
- 发现 AGENTS.md / RULES.md 中有缺失或过期信息，本轮结束前更新它。
- HANDOFF 文件里的"不要碰"列表具有约束力，不得绕过。

### 2. 架构约束（Architecture Constraints）

**目标**：机械性地阻止已知的错误模式，不依赖 agent 自觉。

本项目的硬约束：

| 约束 | 具体规则 |
|------|---------|
| **Worktree 隔离** | 代码改动在 `D:/lottery-dev`；构建在 `D:/lottery-build`；不要交叉写入 |
| **文件白名单** | 每轮修改前，从 HANDOFF 或用户指令中确认本轮目标文件列表，只改这些文件 |
| **后端验证门** | 提交前跑 `python -m compileall app`，失败则不提交 |
| **前端验证门** | 提交前跑 `npm run build`，失败则不提交 |
| **分支命名** | `hermes/fix-xxx`（Claude）、`codex/fix-xxx`（Codex），严格执行 |
| **PR 必须提** | 每轮完成后必须提 PR，不得跳过，标题格式 `[Agent] <动词>: <描述>` |

**违规响应**：发现自己将要违反约束时，停下来明确告知用户，等待确认再继续。

### 3. 反馈回路（Feedback Loops）

**目标**：每一步操作都有可验证的信号，错误在到达人类眼睛之前被自动捕获。

本项目的标准反馈链：

```
修改代码
  → 静态验证（compileall / npm build）
  → 单元/集成测试（直接 python 脚本跑 scraper）
  → 本地 API 验证（Invoke-RestMethod 触发 scrape）
  → 前端视觉验证（浏览器打开 localhost:5176）
  → git add 指定文件 → commit → push → PR
```

**Scraper 验证模板**（每次改 jackpot_scraper.py 后必跑）：

```powershell
cd D:\lottery-dev\backend
@'
import asyncio
from app.services.jackpot_scraper import fetch_marksix_jackpot

async def main():
    data = await fetch_marksix_jackpot()
    print(data)

asyncio.run(main())
'@ | python -
```

**期望信号**：`pool_amount` 有值、`prize_breakdown` 有 7 行、`draw_number` 格式正确。

**API 验证模板**（重启后端后必跑）：

```powershell
Invoke-RestMethod -Uri 'http://localhost:8000/api/v1/jackpot/scrape' -Method Post -TimeoutSec 90
```

**信号异常处理**：
- `pool_amount: null` → 检查 scraper 是否加载新代码（重启后端）
- `prize_breakdown` 少于 7 行 → 检查详情页解析逻辑
- `npm run build` 报错 → 不提交，先修

### 4. 熵管理（Entropy Management）

**目标**：防止文档腐烂、上下文积累垃圾、历史失败经验丢失。

**规则**：

1. **每轮结束时**：
   - 如果本轮踩了坑（解析失败、端口冲突、文件路径错误等），把修复方案写进 AGENTS.md 或 RULES.md 对应章节。
   - 如果任务未完成，创建 `HANDOFF_<日期>_<功能名>.md`，记录：当前进度、已改文件、下一步、注意事项。

2. **HANDOFF 文件规范**：
   - 文件名：`HANDOFF_YYYY-MM-DD_<功能关键词>.md`（全大写，用下划线）
   - 放在 `D:/lottery-dev/` 根目录
   - 内容必须包含：本轮目标文件列表、"不要碰"列表、已验证的事实、下一步操作

3. **文档更新触发条件**：
   - 某个 agent 犯了错 → AGENTS.md 加禁止规则
   - 发现新的数据源或解析策略 → SKILL.md references/ 更新
   - UI 规范有新增 → RULES.md 更新

---

## 本项目 Harness 健康检查清单

开始任务前自查（30 秒）：

- [ ] 读了 AGENTS.md 最新版？
- [ ] 读了最新 HANDOFF 文件（如有）？
- [ ] 确认本轮目标文件列表？
- [ ] 确认当前工作目录是 `D:/lottery-dev`？
- [ ] 本地后端/前端开发服务是否需要重启？

提交前自查：

- [ ] `python -m compileall app` 通过？
- [ ] `npm run build` 通过？
- [ ] API scrape 验证结果符合预期？
- [ ] `git diff --name-only` 只包含目标文件？
- [ ] PR 标题格式正确 `[Agent] <动词>: <描述>`？

---

## 失败模式 → Harness 更新示例

| 发生了什么 | Harness 更新动作 |
|-----------|----------------|
| 后端改了但 API 还返回旧数据 | → AGENTS.md 加：「改完后端代码必须重启 uvicorn 进程」 |
| 前端写死了占位金额 | → RULES.md 加禁止规则；HANDOFF 里加注意事项 |
| Scraper 抓到的详情页 URL 格式变了 | → SKILL.md data-sources.md 更新解析逻辑文档 |
| git push 因为主分支冲突失败 | → AGENTS.md 加：「push 前先 git pull --rebase」 |

---

## 与其他 Agent 的协作边界

| Agent | 读取哪些 Harness 文件 | 主要职责 |
|-------|---------------------|---------|
| **Claude Code (Hermes)** | 本 SKILL.md + AGENTS.md + RULES.md + HANDOFF | 整体协调、复杂修复、PR 审核 |
| **Codex** | AGENTS.md + HANDOFF | 多步重构、批量修改 |
| **Kimi Code** | AGENTS.md + RULES.md | 快速单文件修改 |

**所有 agent 共同遵守**：AGENTS.md 里的规则。AGENTS.md 是本项目唯一的跨 agent 权威文档。

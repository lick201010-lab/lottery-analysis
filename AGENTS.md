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
D:/lottery-dev      — dev/mobile-layout
D:/lottery-build    — feature/build-env（含 deploy.sh）
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

- 主分支合并后，GitHub → 服务器每 5 分钟自动 `git pull` → `restart.sh` 重启 uvicorn
- 构建在 `lottery-build` worktree 中进行，不影响开发目录
- 生产环境出现问题，从 `production` 分支切出 hotfix 分支

## 沟通约定

- Hermes 通过微信推送关键状态（部署完成、构建失败、需要决策）
- 长时间任务（>5分钟）完成后主动汇报
- 不确定的问题先查证再回复，不猜测

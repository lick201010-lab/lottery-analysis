# 弈彩 YiCai — 项目变更日志与问题追踪

> 记录项目发展历程、已完成功能、当前 Bug 及待办事项。

---

## 项目概述

**弈彩 YiCai** 是一个六合彩（MarkSix）与双色球（SSQ）数据分析平台。

- **前端**: Vue 3 + Vite + Tailwind CSS v4 + Chart.js
- **后端**: FastAPI + SQLAlchemy async + SQLite
- **部署**: 阿里云轻量服务器（香港）+ Caddy 自动 HTTPS
- **域名**: www.ckl.hk（前端静态文件）/ api.ckl.hk → localhost:8000
- **数据库**: SQLite `data/marksix.db`（MarkSix 4339条、SSQ 3939条）

---

## 已完成的主要功能

### Phase 1: 基础架构
- [x] 后端 API（FastAPI）部署于阿里云香港服务器
- [x] 前端 Vue 3 构建并部署到 `frontend/dist`
- [x] Caddy 反向代理 + 自动 HTTPS
- [x] SQLite 数据库 + SQLAlchemy async ORM
- [x] GitHub Actions cron 定时触发数据更新

### Phase 2: 数据采集
- [x] 六合彩历史数据爬虫（fetch_marksix.py）— 从 HKJC 获取
- [x] 双色球历史数据爬虫（fetch_ssq.py）— 从 500.com/cwl.gov.cn 获取
- [x] 数据合并与去重（merge_marksix.py）
- [x] 冷热遗漏统计 + 频率缓存

### Phase 3: UI 设计（三轮迭代）
- [x] **Round 1**: Binance 暗色主题
- [x] **Round 2**: Stripe 浅色主题
- [x] **Round 3**: 毛玻璃卡片 + 蓝紫粉菱形渐变背景
- [x] 六合彩官方红/蓝/绿号码颜色规则
- [x] 双色球红球+蓝球颜色规则
- [x] 移动端响应式（汉堡菜单、表格列隐藏、flex-col 堆叠）
- [x] 页面过渡动画（0.35s + scale）、stagger-children、移动端菜单滑动
- [x] Logo 替换为透明 PNG，object-contain

### Phase 4: 功能页面
- [x] **Dashboard**: 三栏 Hero 卡片（最新开奖/倒计时/中奖统计）+ 奖金规则表格
- [x] **CountdownTimer**: 六合彩每周二四六 21:30，双色球每周二四日 21:15，实时倒计时
- [x] **JackpotAnalysis**: 税务计算器（双色球扣 20% 个税，六合彩香港免税）
- [x] **AppFooter**: 四列布局 + 详细免责声明
- [x] 品牌重命名："香港彩/福利彩" → "六合彩/双色球"

### Phase 5: 奖池数据爬虫
- [x] `backend/app/services/jackpot_scraper.py` — 双色球奖池爬虫
- [x] `backend/app/models/jackpot.py` — JackpotData SQLAlchemy 模型
- [x] `backend/app/routers/jackpot.py` — `/api/v1/jackpot/latest` + `/api/v1/jackpot/scrape`
- [x] 前端 Dashboard 调用 `/api/v1/jackpot/latest` 显示真实奖池数据
- [x] 双色球数据源：datachart.500.com（完整奖池+中奖统计）+ 500.com XML 回退
- [x] 香港六合彩数据源：lottery.hk 优先，on.cc 回退，DB 最新期开奖兜底
- [x] 六合彩 fallback：爬虫失败时从数据库 `draws` 表读取最新一期
- [x] Jackpot upsert 逻辑（存在则更新，不存在则插入）

### Phase 6: 合规与规范
- [x] `RULES.md` — 记录颜色规则、名称规范、响应式策略、合规文字
- [x] `AGENTS.md` — 项目代理指南（空，待补充）

### Phase 7: 高频主动抓取
- [x] 服务器 crontab 主动抓取：每 30 分钟触发一次 `/api/v1/jackpot/scrape`
- [x] 开奖日（周二/四/六/日）晚间 21:00-22:00 每 10 分钟额外抓取
- [x] 日志写入 `/var/log/jackpot_scrape.log`
- [x] 脚本路径：`/opt/lottery-analysis/cron_scrape.sh`

### Phase 8: 六合彩真实奖池接入 + 合规页面（PR #3，2026-05-20）
- [x] `jackpot_scraper.py` 新增 `_merge_marksix_detail()`：解析 `lottery.hk` 详情页（`/en/mark-six/results/YYYY-MM-DD`）
- [x] `_parse_money()` 工具函数，解析 `HK$39,170,280` 格式
- [x] 提取 Prize Breakdown 1-7 奖金额、中奖注数、Total Turnover
- [x] `MARKSIX_PRIZE_PLACEHOLDER` 扩到 7 项（原 3 项），与真实奖项数对齐
- [x] `routers/jackpot.py` fallback 改用统一 placeholder
- [x] 前端 Dashboard 显示 marksix `HK$ 22,000,000`，副文案 `预计头奖基金 · lottery.hk 抓取`
- [x] 新增 7 个静态页面：About / Privacy / Responsible / Guide / Odds / Strategy / PatternsArticle

### Phase 9: Harness Engineering 沉淀（PR #4，2026-05-20）
- [x] `skills/harness-engineering/SKILL.md` 新增 Claude Code 专用 skill（318 行）
- [x] `AGENTS.md` 改写「部署规则」节：删除错误的「服务器每 5 分钟自动 git pull」描述，写真实手动流程
- [x] `AGENTS.md` 新增「Harness Engineering」章节（适用所有 agent）
- [x] `AGENTS.md` 新增「已知陷阱」章节，沉淀本轮 5 条踩坑教训
- [x] 本机 SSH 公钥 `yvette@hermes` 加到服务器 `root@47.237.181.181:~/.ssh/authorized_keys`，解锁本地一行命令直连部署

### Phase 10: 选号机制精修 + 分层筛选完整版（PR #5、#6，2026-05-20）
- [x] NavBar「工具箱」→「模拟选号」（统一术语）
- [x] 首页删除「选择一个红色箭头…」红色介绍文字
- [x] 选号策略调整：删冷号观察 / 冷热均衡，加回加权随机
- [x] **新增分层筛选完整版**：
  - 后端 `POST /api/v1/analysis/layered_pick` 端点，4 层过滤算法
  - 层 1 大底：近 N 期出现率前 X%
  - 层 2 走势：近期连号特征筛选
  - 层 3 统计：奇偶 / 大小 / 和值偏好
  - 层 4 个人：胆码必含 + 杀号必排
  - 输出可调大小复式（7+1 到 12+1）+ 组合数统计 + 蓝球候选
  - 前端 `GenerateNumbers.vue` 大改：4 层独立配置面板 + 结果展示

### Phase 11: 全站导航/路由 bug 全量修复（PR #7，2026-05-20）
- [x] NavBar「关于我们」原指向 `/pairs`（组合分析）→ 修正为 `/about`
- [x] NavBar「资讯」原指向 `/jackpot`（奖金分析）→ 修正为 `/patterns-article`
- [x] 删除 NavBar 三个项后误导性的 `⌄` 下拉符号（实际无下拉实现）
- [x] AppFooter「数据说明」组 4 个死链 `#` 全部替换为有效路由
  - 常见问题 → `/guide`
  - 规则说明 → `/odds`
  - 奖金规则 → `/jackpot`
  - 投注策略 → `/strategy`
- [x] 让之前无入口的 5 个隐藏页面（Guide/Odds/Strategy/PatternsArticle/JackpotAnalysis）全部可达
- [x] 14 个路由 100% 都有可达入口

### Phase 12: UI 重设计实验（PR #8 + #9 revert，2026-05-20）
- [x] PR #8: 全站换紫蓝渐变冲击风（替换 style.css 主题 token + NavBar 白底 + AppFooter 浅灰）
- [x] **用户验收不满意**：颜色没原版好看
- [x] PR #9: `git revert -m 1` 一键还原原莫兰迪暖米色版本
- [x] **复盘教训**：全站 CSS 主题重写前应先做小范围 mock 上线验收，不要直接全量改 → 已沉淀到 `AGENTS.md` 已知陷阱第 6 条

---

## 当前 Bug 🐛

### Bug 1: 双色球奖池数据不稳定 ✅ FIXED
- **状态**: ✅ 已修复
- **现象**: `datachart.500.com` HTML 解析有时成功（返回完整奖池数据），有时失败（回退到 500 XML，无奖池金额）
- **原因**: HTML `<tr>` 标签的 class 名或格式在不同请求/时段可能不同；`<tr class="t_tr1">` 偶尔匹配不到；表格有时有额外序号列
- **修复方案**: 
  - 增加自动列偏移检测（序号列）
  - 增加多策略回退（Strategy 1: t_tr1, Strategy 2: 扫描所有含5位数字的<tr>, Strategy 3: Markdown 表格格式）
  - 增加 upsert 逻辑（存在则更新，不存在则插入）
- **验证结果**: `pool_amount: 1251883761`（12.5亿），`sales_amount: 391858874`（3.9亿），一等奖5注842万，二等奖67注102万

### Bug 2: Git push 本地网络问题
- **状态**: ❌ 阻塞
- **现象**: 本地开发机无法直连 GitHub（大陆网络），代理端口 59527 未运行
- ** workaround**: 服务器可直接 `git pull`（香港网络无墙）

### Bug 5: 服务器没有真正的「自动 git pull」机制 ✅ FIXED (2026-05-20)
- **状态**: ✅ 已修（文档纠正 + 加 SSH key 自动化）
- **现象**: `AGENTS.md` 历史版本写「服务器每 5 分钟自动 git pull + restart.sh 重启 uvicorn」，但 PR merge 后线上始终不更新
- **真因**: 这个 cron 机制根本不存在，服务器代码一直停在上一次手动 deploy 的状态
- **修复**: AGENTS.md 改写部署规则 + 加 SSH key 让本机一行命令直连部署（不再依赖虚构的自动化）

### Bug 6: 全站导航 label 与 path 错位 ✅ FIXED (2026-05-20)
- **状态**: ✅ 已修
- **现象**: 点「关于我们」进入「组合分析」页；点「资讯」进入「奖金分析」页
- **真因**: `NavBar.vue` 链接配置错位（`label` 描述跟 `path` 跳转的页面不一致）
- **修复**: PR #7 — 同时修复 footer 4 个死链 + 5 个隐藏页面入口

### Bug 7: lottery.hk 抓不到金额 ✅ FIXED (2026-05-20)
- **状态**: ✅ 已修
- **现象**: 本地 scraper 能抓 marksix `pool_amount`，prod 后端返回 `null`
- **误判**: 初判以为阿里云香港 IP 被 lottery.hk 反爬
- **真因**: 服务器 uvicorn 进程跑的还是老代码（git pull 后未真正重启）
- **修复**: 跑 `restart.sh` 后立刻拿到完整奖池金额

### Bug 3: 香港六合彩最新数据抓取 ✅ IMPROVED
- **状态**: ✅ 已优化
- **现象**: `win.on.cc/marksix/` 可访问但解析稳定性不足
- **修复方案**: 使用 `lottery.hk/zh-hans/liuhecai/kaijiangjieguo/` 作为优先非赛马会来源，解析结构化结果表；on.cc 作为回退
- **验证结果**: 本地已抓取 `26/052`（2026-05-16），正码 `11,25,28,36,41,43`，特码 `22`
- **兜底方案**: 外部来源失败时继续从数据库 `draws` 表读取最新一期

### Bug 4: sqlite3 CLI 未安装
- **状态**: ⚠️ 低优先级
- **现象**: 服务器上无法执行 `sqlite3` 命令行操作
- **影响**: 无法手动执行数据库清理/修复脚本
- ** workaround**: 通过后端 Python API 操作数据库

---

## 已知限制

| 项目 | 说明 |
|------|------|
| 六合彩无奖池概念 | 六合彩是固定奖金制，没有滚动奖池。JackpotData 中 `pool_amount` 为 `null` 是预期行为 |
| 数据源依赖第三方 | 双色球依赖 500.com/datachart.500.com，若网站改版或封禁需切换备用源 |
| 服务器 SSH 不可用 | 本地开发机无法 SSH 登录服务器，所有服务器操作需用户手动执行 |

---

## 待办事项 📋

- [ ] 验证双色球 datachart.500.com 多策略解析在服务器上的稳定性
- [x] 增加并验证 lottery.hk 香港六合彩最新结果抓取
- [x] 前端构建并验证 Dashboard 奖池数据显示
- [x] 设置定时任务自动触发 `/api/v1/jackpot/scrape`
- [x] 补充 `AGENTS.md` 项目代理指南（已扩展为含 Harness Engineering + 已知陷阱）
- [ ] 考虑增加更多双色球备用数据源（如彩宝贝、中彩网）
- [ ] 真正实现「merge PR → 服务器自动 deploy」（GitHub Actions / webhook）
- [ ] `data/marksix.db` 加 `.gitignore`，根治每次 deploy 都要 `git checkout` 的麻烦
- [ ] 服务器 uvicorn 做成 systemd 服务（开机自启 + 挂掉自动重启）
- [ ] 服务器 backup 目录定期清理（如 `/root/backup-20260520/`）

---

## 部署备忘

### 本地一行命令直连部署（推荐，2026-05-20 起可用）

本机 SSH 公钥已加到服务器 `authorized_keys`，可直接：

```powershell
# 全套部署（前端 build + 后端重启）
ssh root@47.237.181.181 'cd /opt/lottery-analysis && git checkout -- data/marksix.db; git pull --ff-only && cd frontend && npm run build && bash /opt/lottery-analysis/restart.sh'

# 仅前端改动（无需重启后端）
ssh root@47.237.181.181 'cd /opt/lottery-analysis && git checkout -- data/marksix.db; git pull --ff-only && cd frontend && npm run build'

# 触发爬虫
curl -X POST https://api.ckl.hk/api/v1/jackpot/scrape

# 验证（注意参数名是 lottery_type 不是 type）
curl 'https://api.ckl.hk/api/v1/jackpot/latest?lottery_type=marksix'
curl 'https://api.ckl.hk/api/v1/jackpot/latest?lottery_type=ssq'
```

### 服务器侧手动执行（备用，阿里云 Workbench 网页终端）

```bash
cd /opt/lottery-analysis
git checkout -- data/marksix.db 2>/dev/null    # 清理运行时写入
git pull
cd frontend && npm run build                    # 前端
bash /opt/lottery-analysis/restart.sh           # 后端重启（含 pkill + nohup uvicorn）
```

完整部署流程见 `AGENTS.md` 「部署规则」节。

---

## 技术决策记录

1. **为何用 SQLite 而非 PostgreSQL/MySQL**: 项目数据量小（< 1万条），SQLite 零配置、单文件备份方便
2. **为何用 datachart.500.com 而非官方 API**: 福彩官方 API (`cwl.gov.cn`) 返回 403，500.com 历史表格页数据完整且稳定
3. **为何六合彩用 DB fallback 而非外部爬虫**: HKJC/on.cc 等香港网站经常改版或加反爬，而数据库中已有完整历史数据
4. **为何前端用 Tailwind v4**: 最新版本支持 CSS-first 配置，与 Vite 集成更好
5. **为何分层筛选放在前端 UI 而非后端纯算法返回组合**: 让用户能即时调参、看到每层池子变化，比一次性返回最终结果更有"分析过程"的体感
6. **为何保留莫兰迪暖米色而非紫蓝渐变（PR #8 revert）**: 用户验收倾向暖色专业感，而非数据科技工具的冷感。视觉决策最终由用户拍板，不强推任何方向
7. **为何 SSH key 直连而非 GitHub webhook 自动部署**: 加 SSH key 5 分钟搞定；webhook 需要服务器开放公网端口 + GitHub 配置 + 签名校验，复杂度高很多。本项目频率允许手动触发

---

*最后更新: 2026-05-20*

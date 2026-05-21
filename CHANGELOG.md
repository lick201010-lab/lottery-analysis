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

### Phase 7: 模拟选号与分层漏斗（2026-05-19~20）
- [x] 导航「工具箱」→「模拟选号」改名 + 删 weighted_random / pair_chain 策略
- [x] 全站导航修复（关于我们→/about，资讯→/patterns-article，footer 4 死链）
- [x] 分层筛选完整版（4 层配置：历史/走势/统计/胆码 + 复式输出）— `POST /api/v1/analysis/layered_pick`
- [x] **分层筛选改造为三步可调漏斗** 49→N→M→K（默认 10→8→6，pool1/2/3_size 全可调）
  - 综合得分 = 历史热度×2 + 近期走势×3 + 遗漏修正
  - 返回 pool1/pool2/pool3 + 各自 eliminated 列表 + combinations top-5 推荐组合
  - 前端结果展示：3 步漏斗可视化 + 多组 6 号推荐
- [x] **模拟选号 UI 优化**：策略选择器拆为「3 简单卡 + 1 分层 featured 大卡」，配置面板「核心 + 进阶折叠」
- [x] **双色球 vs 六合彩附加号区分**（关键 Bug 修复）：
  - SSQ 蓝球是头奖必含，必须 6 红+1 蓝同行大球展示
  - MarkSix 特码仅辅助参考，移到底部小行 + 「仅供参考」徽章
  - 通过 `isSSQ = computed(...)` + `v-if` 分两套模板
- [x] Footer 加邮箱联系 `lick201010@gmail.com`
- [x] 关键文件：
  - `backend/app/routers/analysis.py`（layered_pick 端点 + combinations 字段）
  - `frontend/src/views/GenerateNumbers.vue`（策略选择器 + 配置面板 + 结果展示）
  - `backend/tests/test_layered_pick_logic.py`（5 个测试用例）

### Phase 8: SEO 与商业化基建（2026-05-21）

#### 8.1 SEO 90 天总规划
- 完整方案文档：`~/.claude/plans/giggly-napping-lynx.md`
- 用户分层：核心（HK 本地）/ 增长（海外华人 + 大陆 VPN）/ 长尾（数据爱好者）
- 商业化分 3 阶段：启动期（0-90d 不放广告）/ 增长期（5k MAU 后申请 AdSense）/ 商业化期（30k MAU 后上 Pro 会员 + API）
- **不抢的高风险关键词**：预测、必中、稳赚、投注技巧、博彩平台名

#### 8.2 Week 1 技术 SEO 基础（全部上线）
- [x] `@unhead/vue` v2.x 接入（**锁定 v2，与 vite-ssg v28 兼容**）
- [x] `frontend/src/composables/useSEO.js` — 统一 SEO helper，带 `useSEO()` / `breadcrumb()` / `faqPage()`
- [x] 14 个 view 全部接入 `useSEO()`，每页独立 title / description / og / twitter / canonical
- [x] 根 JSON-LD：WebSite（含 SearchAction）+ Organization（含邮箱）
- [x] `robots.txt` + `sitemap.xml`（14 路由完整列表）
- [x] `<html lang>` 修复 zh-HK → zh-CN（与简体内容一致）
- [x] OG 主视觉图 1200×630 PNG（`frontend/public/og-image.png`）

#### 8.3 Google Search Console + Analytics
- [x] GSC HTML meta 验证：`16ehxXcQ3tVg703tRuK5tnbzEVlcsiM8TsJ3cuFvsgw`
- [x] GA4 测量 ID：`G-VC4RSJMMR5`
- [x] Consent Mode v2 默认 denied（AdSense 友好）+ `CookieConsent.vue` 横条
- [x] router.afterEach 触发 SPA 路由切换的 page_view 事件
- [x] sitemap.xml 已提交（用户操作）

#### 8.4 vite-ssg 静态预渲染（关键收益）
- [x] 装 `vite-ssg` ^28.3.0
- [x] `package.json` build script 改为 `vite-ssg build`
- [x] `src/router.js` 拆出 routes 数组导出（vite-ssg 消费）
- [x] `src/main.js` 用 ViteSSG factory 替代 createApp
- [x] **14 个路由全部预渲染成独立 HTML**：dist/index.html、frequency.html、generate.html...
- [x] 每个 HTML 含独立 title/canonical/og/JSON-LD（SSR 在 Node 里抓取 @unhead 状态）
- [x] Caddyfile 改 `try_files {path} {path}.html /index.html`（关键，否则 Caddy SPA fallback 把所有路由都返回 index.html）

#### 8.5 服务器自动部署（替代手动 ssh）
- [x] 新建 `auto-deploy.sh`（仓库根）：检查 origin/main 与 HEAD diff，有变化才 pull + 智能 build/restart
- [x] crontab `*/2 * * * *` 每 2 分钟一次
- [x] 日志 `/var/log/yicai-deploy.log`
- [x] 替换原有 `restart.sh` cron（每 5 分钟无脑重启，且不跑 npm build 导致前端从不上线）
- [x] **流程升级**：以后 merge PR 后 2 分钟自动上线，不需要手动 ssh

#### 8.6 Caddyfile 配置回流
- [x] 服务器 `/etc/caddy/Caddyfile` 落到仓库 `deploy/Caddyfile`
- [x] 防丢失：未来重装服务器跑 `sudo cp deploy/Caddyfile /etc/caddy/Caddyfile && sudo systemctl reload caddy`

#### 8.7 已知陷阱沉淀（AGENTS.md 新增）
- **#6 六合彩 vs 双色球**：附加号规则完全不同，必须 v-if 区分模板
- **#7 部署后必做 chunk 验证**：merge ≠ 上线，必须 grep dist HTML 含新文案，30 秒 PowerShell 套路
- **#1 重写**：从「不存在自动部署」改为「auto-deploy.sh 每 2 分钟跑」（PR 已 push 等 merge）

#### 8.8 待执行（明早 8:30 HK scheduled agent）
- BreadcrumbList JSON-LD（14 路由）
- FAQPage JSON-LD（/guide、/odds、/jackpot、/responsible）
- 自定义 404 页面（noindex）
- 邮件订阅入口（Footer + About，后端 SQLite 入库先，Resend 留 TODO）
- 参考 `HANDOFF_2026-05-22_SEO_WEEK2.md`

#### 8.9 Claude Code 工具
- [x] 装 `superpowers` plugin（v5.1.0）→ 后撤回
- [x] 装 `andrej-karpathy-skills` plugin（v1.0.0）保留

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

### 数据采集
- [ ] 验证双色球 datachart.500.com 多策略解析在服务器上的稳定性
- [x] 增加并验证 lottery.hk 香港六合彩最新结果抓取
- [x] 前端构建并验证 Dashboard 奖池数据显示
- [x] 设置定时任务自动触发 `/api/v1/jackpot/scrape`
- [x] 补充 `AGENTS.md` 项目代理指南（已写满 7 条已知陷阱 + 完整流程）
- [ ] 考虑增加更多双色球备用数据源（如彩宝贝、中彩网）
- [ ] `data/marksix.db` 从 git 跟踪移除（陷阱 #5），改 `.gitignore`

### SEO（Phase 8 在进行）
- [x] Week 1 技术 SEO 基础（@unhead + sitemap + robots + JSON-LD + GSC + GA4 + OG）
- [x] vite-ssg 14 路由预渲染
- [x] Caddyfile try_files SSG fallback
- [x] auto-deploy.sh cron polling
- [ ] **Week 2（明早 8:30 自动）**：BreadcrumbList + FAQPage + 自定义 404 + 邮件订阅入口
- [ ] Week 3-4：建 `/articles/[slug]` + 写头 2 篇文章（#1 中奖概率真相、#2 六合彩玩法指南）
- [ ] Week 5-8：发布文章 #3-#10（每周 2 篇）
- [ ] Week 9-12：建 `/reports` 月报、`/dictionary` 术语词典、开奖提醒邮件

### 商业化（90 天后启动）
- [ ] 申请 Google AdSense（流量 ≥ 5k MAU 时）
- [ ] Pro 会员功能开发（历史回测器、自定义观察、Telegram bot）
- [ ] 数据 API + 文档站

### 待 merge 的 PR
- [ ] `hermes/auto-deploy-cron` — 把 auto-deploy.sh 回流到仓库
- [ ] `hermes/caddyfile-ssg` — Caddyfile + HANDOFF 文档
- [ ] `hermes/seo-week2-auto`（明早自动生成）— BreadcrumbList + FAQPage + 404

---

## 部署备忘

```bash
# 服务器部署 — 现在已经自动化（2026-05-21 起）
# auto-deploy.sh 每 2 分钟检查 origin/main 有无新 commit，有就自动 pull + 智能 build/restart
# 日志：/var/log/yicai-deploy.log
# 不需要手动 ssh，merge PR 后等 2-3 分钟即可

# 仍需手动 ssh 的场景：
# 1. cron 失败 → ssh root@47.237.181.181 'tail -30 /var/log/yicai-deploy.log'
# 2. 需要立即上线不能等 2 分钟 → 手动跑 /opt/lottery-analysis/auto-deploy.sh
# 3. 出现脏文件冲突 → ssh + git checkout -- <file> + rerun

# 手动触发爬虫
curl -X POST https://api.ckl.hk/api/v1/jackpot/scrape

# 验证接口
curl https://api.ckl.hk/api/v1/jackpot/latest?lottery_type=ssq
curl https://api.ckl.hk/api/v1/jackpot/latest?lottery_type=marksix

# SEO chunk 验证（merge 后必做，详见 AGENTS.md 陷阱 #7）
# 1. 抓 https://www.ckl.hk/ 拿 entry bundle hash
# 2. 抓 entry bundle 找目标页 chunk
# 3. 抓 chunk 内容 grep 这次 PR 加的独特中文字符串
```

---

## 技术决策记录

1. **为何用 SQLite 而非 PostgreSQL/MySQL**: 项目数据量小（< 1万条），SQLite 零配置、单文件备份方便
2. **为何用 datachart.500.com 而非官方 API**: 福彩官方 API (`cwl.gov.cn`) 返回 403，500.com 历史表格页数据完整且稳定
3. **为何六合彩用 DB fallback 而非外部爬虫**: HKJC/on.cc 等香港网站经常改版或加反爬，而数据库中已有完整历史数据
4. **为何前端用 Tailwind v4**: 最新版本支持 CSS-first 配置，与 Vite 集成更好
5. **为何用 vite-ssg 而非完整 SSR**（2026-05-21）：无登录态、无个性化内容，SSG 完全够用；部署仍是 Caddy + 静态 dist，零基础设施变化
6. **为何 @unhead/vue 锁 v2.x 不升 v3**（2026-05-21）：vite-ssg v28 的 peerDeps 声明 ^2.1.2，v3 API 不兼容会导致 head 元素不注入到预渲染 HTML
7. **为何用 cron polling 而非 GitHub Actions / webhook**（2026-05-21）：cron 最简单零依赖，2 分钟延迟可接受；将来流量上来再升 GitHub Actions
8. **为何前 90 天不放广告**（2026-05-21 SEO 方案）：流量 < 5k MAU 时 AdSense 大概率被拒（彩票敏感品类审核严），且会拉高跳出率拖累 SEO 排名；先养内容资产，90 天后再申请

---

*最后更新: 2026-05-21（Phase 7-8：分层漏斗 + SEO 基建）*

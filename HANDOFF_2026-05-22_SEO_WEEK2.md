# HANDOFF — Week 2 SEO 收尾 + 内容铺路

> 创建于 2026-05-21 晚 · 计划由 2026-05-22 08:30 HK 自动启动的 scheduled agent 完成
>
> 用户 Yvette 不在线时这份文档就是 agent 的唯一上下文，必须自足。

---

## 当前状态（截止 2026-05-21 晚）

### 已完成（Week 1）
- ✅ `@unhead/vue` v2.x 接入（不要升 v3，跟 vite-ssg v28 不兼容）
- ✅ 14 路由全部 `useSEO()` 接入 title/description/og/twitter/canonical
- ✅ 根 JSON-LD：WebSite + Organization
- ✅ robots.txt + sitemap.xml（14 路由）
- ✅ Google Search Console 验证（meta tag）
- ✅ Google Analytics 4 接入（G-VC4RSJMMR5）+ Consent Mode v2 + CookieConsent.vue banner
- ✅ OG 主视觉图 1200×630 PNG
- ✅ vite-ssg 静态预渲染（14 路由各自 .html）
- ✅ Caddyfile `try_files {path} {path}.html /index.html`
- ✅ auto-deploy cron 每 2 分钟（`/opt/lottery-analysis/auto-deploy.sh`）

### 已上线 prod
`https://www.ckl.hk/` — 所有 14 路由各自有独立预渲染 HTML，title/canonical/og 全部正确。

---

## 明早任务清单（按优先级）

### 必做（机械活，工程量 2-3 小时）

#### Task 1: BreadcrumbList JSON-LD（14 路由）
- 用 `frontend/src/composables/useSEO.js` 已经导出的 `breadcrumb()` helper
- 每个 view 在 `useSEO({...})` 调用里加 `jsonLd: [breadcrumb([{name:'首页',path:'/'}, {name:'<本页>',path:'<本路径>'}])]`
- 命名对照表：
  - `/` → 首页（首页不需要 breadcrumb，可跳过）
  - `/data` → 开奖记录
  - `/frequency` → 号码统计
  - `/patterns` → 走势分析
  - `/pairs` → 组合分析
  - `/generate` → 模拟选号
  - `/jackpot` → 奖金计算
  - `/guide` → 玩法指南
  - `/odds` → 中奖概率
  - `/strategy` → 数据方法
  - `/patterns-article` → 走势专题
  - `/responsible` → 理性娱乐
  - `/privacy` → 隐私政策
  - `/about` → 关于我们

#### Task 2: FAQPage JSON-LD（4 个 Q&A 页）
- 用 `useSEO.js` 已经导出的 `faqPage()` helper
- 应用到这 4 个路由：
  - `/guide` — 双色球 / 六合彩玩法常见问答（5-8 个 Q）
  - `/odds` — 中奖概率常见问答（5 个 Q）
  - `/jackpot` — 奖金税务常见问答（4 个 Q）
  - `/responsible` — 理性娱乐常见问答（4 个 Q）
- Q&A 内容若 view 文件里已有，直接抓出来；若没有，**新写**（每个 Q 答案 1-2 句话，合规口吻）

#### Task 3: 自定义 404 页面
- 新建 `frontend/src/views/NotFound.vue`
- router.js 加路由 `{ path: '/:pathMatch(.*)*', name: 'NotFound', component: () => import('./views/NotFound.vue') }`
- 文案：找不到页面 + 「返回首页」按钮 + 推荐链接列表（5 条主要路由）
- 用 `useSEO({title: '页面未找到', jsonLd: [{...noindex tag via robots meta...}]})`
- ⚠️ noindex meta：`<meta name="robots" content="noindex" />` 通过 `useHead({ meta: [...] })` 注入

### 半机械（用户半授权了，做 Resend）

#### Task 4: 邮件订阅入口（Resend 免费版）
- Footer 加一个邮件订阅表单（输入框 + "订阅"按钮）
- About 页底部也加一份
- 后端：**不要现在建数据库表 / API**，先把表单 POST 到 Resend 的 audiences API 直接收邮箱（前端 fetch，用环境变量塞 API key 不安全 → 必须走后端代理）

**实际方案**（安全 + 简单）：
1. 前端 Footer 加 `<form>` + 输入框
2. 后端新建 `backend/app/routers/newsletter.py`：POST `/api/v1/newsletter/subscribe`，body = `{ "email": "..." }`
3. 后端把 email 写入 SQLite 新建表 `newsletter_subscribers(id, email, subscribed_at)`，**先入库不发实际邮件**
4. 给用户留 TODO 注释：后续接 Resend 时把入库逻辑后再调 Resend 创建 audience contact

**注意**：邮件订阅表单本身有合规要求：
- 必须有「订阅即同意接收弈彩邮件，可随时退订」的小字
- 必须链接到 /privacy
- 提交后必须显示确认信息（不要刷页面）

### 可选增强（如果时间够）

#### Task 5: 所有图表、NumberBall 补 alt 文本
- 在 `frontend/src/components/NumberBall.vue` 给 `<div>` 加 `:aria-label="..."`
- 各 Chart.js canvas 加 `<canvas aria-label="..." role="img">`

#### Task 6: 跑 Lighthouse SEO 看分数
- 不需要装 puppeteer，用 `unlighthouse` 或者直接告诉用户去 PageSpeed Insights 跑
- 仅生成报告，**不要为了刷分而改业务代码**

---

## 工作流程（agent 必读）

1. **读 `D:/lottery-dev/AGENTS.md`** 全文，特别是已知陷阱 #1-#7
2. **从 main 起新分支** `hermes/seo-week2-auto`（**不要在 main 直接改**）
3. **小步提交**：每个 Task 跑完一个 commit
4. **构建验证门**：每 push 前必须 `npm run build` 通过
5. **检查 14 路由预渲染输出**：build 完跑 `grep -c "BreadcrumbList" dist/*.html`，应该 13+ 个文件命中
6. **不 merge PR**：只 push 分支 + 创建 PR 链接，让 Yvette 起床后审
7. **不 ssh 跑部署**：auto-deploy cron 会处理；agent 不应触碰服务器
8. **不动后端 jackpot scraper / 历史数据**

---

## 必须遵守的硬约束

| 约束 | 说明 |
|------|------|
| 工作目录 | `D:/lottery-dev` 是唯一改业务代码的地方 |
| 文件白名单 | 严格按上面 Task 1-6 改文件，不要顺手改其他 |
| @unhead/vue 锁 v2 | 不要升级，会破坏 vite-ssg |
| 不动 vite-ssg / Caddy 配置 | 已经稳定 |
| 内容合规 | 涉及彩票文案严守"仅供娱乐"口径，不写"预测/必中/技巧" |

---

## Agent 完成后的输出

在 task 末尾用 `mcp__ccd_session__spawn_task` 或回复消息时发给我（Yvette）以下信息：

1. ✅ 完成的 Task 列表
2. ⚠️ 跳过 / 待审的 Task + 原因
3. 🔗 PR 链接（GitHub）
4. 📊 验证结果（grep BreadcrumbList 多少命中，build 是否通过）
5. 📝 任何踩到的坑 + 建议加进 AGENTS.md

---

## 紧急止损

如果遇到：
- `npm run build` 失败超过 2 次都修不好 → 停手，commit 当前进度到分支但不 push，发消息说明
- vite-ssg 报错 SSR 不兼容 → 停手，写明哪个 useHead 调用导致的
- AGENTS.md 已知陷阱触发 → 按陷阱文档执行修复，不要凭直觉
- 出现破坏性 git 操作冲动（reset --hard, force push, branch -D） → **立即停止**，发消息求确认

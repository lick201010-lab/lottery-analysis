# 弈彩 YiCai — SEO / SEM 下一步执行计划

> 定位统一为「彩票开奖数据、历史记录、号码统计、娱乐参考」。
> 全站禁止「预测、必中、稳赚、下注、博彩、赌博」等高风险措辞。
> 主站：`https://yicai.ckl.hk`（canonical 唯一目标）。

最后更新：2026-06-19

---

## 1. 本轮已落地的技术 SEO

| 项目 | 状态 | 说明 |
|------|------|------|
| 域名统一 | ✅ | `SITE_URL`、`index.html`、JSON-LD、OG、sitemap、robots 全部指向 `yicai.ckl.hk` |
| 旧域名 301 | ✅（待部署核对） | `deploy/Caddyfile`：`www.ckl.hk` / `ckl.hk` → 301 `yicai.ckl.hk`，见第 9 节 |
| sitemap lastmod | ✅ | `sitemap.xml` 每条 `<url>` 增加 `<lastmod>` |
| qxc 静态 SEO 页 | ✅ | `/qxc/results`、`/qxc/frequency`、`/qxc/rules`、`/qxc/odds`、`/qxc/history`（接入现有 SeoTopicPage 体系） |
| 百度 sitemap | ✅ | `sitemap-baidu.xml`：仅首页 + 双色球 + 7星彩 + 合规通用页，**不含 marksix** |
| 百度爬虫保守 | ✅ | `robots.txt` 增加 `Baiduspider` 组，`Disallow: /marksix/` |
| 百度验证 meta | ✅ | `index.html` 保留 `baidu-site-verification = codeva-9VvyVzNtsp` |
| JSON-LD | ✅ | WebSite / Organization / BreadcrumbList / FAQPage / Dataset（仅真实字段） |
| 品牌实体 | ✅ | About（平台定位 + 数据来源 + 更新机制 + 免责）、Strategy（方法论，不构成建议） |

---

## 2. Google SEO 关键词策略

Google 可覆盖三彩种（六合彩 / 双色球 / 7星彩）。页面与关键词映射：

| 关键词簇 | 落地页 | 意图 |
|---------|--------|------|
| 六合彩开奖结果 / 六合彩开奖记录 / 六合彩历史 | `/marksix/results`、`/marksix/2026` 等年度归档 | 查询型 |
| 六合彩号码统计 / 冷热号 / 遗漏 | `/marksix/frequency` | 统计型 |
| 六合彩玩法 / 正码 特码 规则 | `/marksix/rules` | 规则型 |
| 六合彩中奖概率 | `/marksix/odds` | 科普型 |
| 双色球开奖结果 / 历史 | `/ssq/results`、`/ssq/YYYY` | 查询型 |
| 双色球冷热号 / 红蓝球统计 | `/ssq/frequency` | 统计型 |
| 双色球玩法 / 中奖概率 | `/ssq/rules`、`/ssq/odds` | 规则 / 科普 |
| 7星彩开奖结果 / 历史开奖 | `/qxc/results`、`/qxc/history` | 查询型 |
| 7星彩号码统计 / 玩法 / 概率 | `/qxc/frequency`、`/qxc/rules`、`/qxc/odds` | 统计 / 规则 / 科普 |

**原则**
- 一页一主关键词簇，title 含主词 + 品牌；description ≤ 155 字、含 1–2 个长尾。
- 首页改为品牌/数据中枢（不堆彩种名），靠深层页承接彩种关键词。
- 内链：每个专题页底部已有同彩种 sibling + related 入口，保持彩种内聚合。
- 归档页（年度 / 期号）用 `Dataset` JSON-LD，覆盖「某年六合彩开奖结果」类长尾。

---

## 3. 百度 SEO 策略（保守）

> 香港彩票内容在百度侧合规风险高，**整体保守**。

- **只提交双色球 + 7星彩 + 合规通用页**：`sitemap-baidu.xml`（手动提交到百度搜索资源平台）。
- **六合彩不进入百度**：
  - 不在 `sitemap-baidu.xml` 中出现；
  - `robots.txt` 中 `Baiduspider` 组 `Disallow: /marksix/`（百度不抓取、不收录六合彩页面）；
  - 首页、通用页 title/description 已避免以六合彩为主（首页已去彩种名）。
- 百度落地页优先：`/ssq/results`、`/ssq/frequency`、`/qxc/results`、`/qxc/history`、`/strategy`、`/about`。
- 注意：`/data`、`/frequency`、`/patterns`、`/pairs`、`/jackpot`、`/odds`、`/guide` 当前 title 含「六合彩」，**已排除出百度 sitemap**。如后续要让百度收录这些通用页，需要先为它们做双色球/7星彩为主的 title 版本，再加入百度 sitemap。

---

## 4. 为什么不建议直接投放彩票高风险广告（SEM）

**结论：暂不投放 Google Ads / 百度推广的彩票类付费广告，优先做自然搜索（SEO）。**

原因：
1. **平台政策限制**。Google Ads 与百度推广对「彩票 / 博彩」类目均有严格资质与地域限制；香港六合彩、内地彩票相关投放普遍需要官方资质或被直接拒登，账户存在被封停风险。
2. **定位冲突**。本站定位是「开奖数据统计 / 娱乐参考」，并非售彩或投注平台。投放彩票广告会与「不参与投注经营」的合规声明自相矛盾，损害品牌可信度。
3. **落地页审核**。付费广告落地页会被人工审核，任何「预测 / 必中 / 稳赚」式表达都会触发拒登甚至账户处罚——而我们本就禁止这类措辞。
4. **ROI 不确定**。彩票数据类流量商业化路径（广告联盟 / 订阅）单价低，付费买量难回正。

**替代方案（合规、低风险）**
- 自然搜索 SEO（本计划主线）。
- 内容营销：开奖数据科普、走势统计方法论、概率科普文章。
- 邮件订阅（已具备 NewsletterSignup）：沉淀回访用户。
- 若未来一定要做付费：仅投放**品牌词**（「弈彩」「yicai」）做品牌保护，且落地页用 `/about` 这类纯数据/品牌页，不投彩种博彩词。

---

## 5. 结构化数据（JSON-LD）现状

| 类型 | 注入位置 | 备注 |
|------|---------|------|
| WebSite + SearchAction | `index.html` 全站根 | url → yicai |
| Organization | `index.html` + `/about` | 含 logo、email、knowsAbout |
| BreadcrumbList | `useSEO.js` 自动按 route 注入 | 已补 qxc 路径标签 |
| FAQPage | 各 SeoTopicPage + `/strategy` | 内容真实、与页面 FAQ 一致 |
| Dataset | qxc results/history、各年度/期号归档页 | **只含真实字段**（期号/日期/前区/后区），不伪造记录数 |
| Article | 各 SeoTopicPage | 专题文章 |

原则：不堆砌 schema，只标注页面真实存在的内容；Dataset 不写未经核实的 `temporalCoverage` 或记录数。

---

## 6. 可执行外链清单（合规优先）

> 目标：提升 `yicai.ckl.hk` 实体可信度与收录速度。避免在博彩站群互链。

- [ ] 提交到目录/工具站：把「彩票开奖数据查询工具」提交到中性的工具导航站、独立开发者产品目录（如 Product Hunt 类、IndieHackers、少数派/即刻工具分享，视合规而定）。
- [ ] 技术社区：在 GitHub 建公开仓库（数据整理脚本/前端开源部分），README 链接主站；GitHub 域名权重高。
- [ ] 内容平台软文：在知乎/CSDN/掘金发「彩票号码统计学科普」「如何正确理解冷热号/遗漏」类**科普文**，文末署名链接，不写预测话术。
- [ ] 百科类：完善品牌词「弈彩 YiCai」在可编辑百科（如有资质）。
- [ ] 友链：与中性的「数据可视化 / 概率科普」类个人站交换，不与售彩/博彩站互链。
- [ ] 社媒实体：建立统一品牌名的社媒账号（X / 小红书等），主页回链，强化 `sameAs` 实体信号（后续可加入 Organization JSON-LD 的 `sameAs`）。

---

## 7. 30 天内容发布计划

> 每周 2–3 篇，围绕「数据 / 统计 / 概率科普」，全部合规措辞。复用现有专题页 + 新增科普文章。

**第 1 周（基础与收录）**
- D1：技术 SEO 上线 + 提交 GSC / 百度（见第 8 节）。
- D2：科普文《如何正确看待冷热号与遗漏：它们只是历史统计》→ 内链 `/strategy`、`/qxc/frequency`、`/ssq/frequency`。
- D4：《7星彩开奖规则详解：前区6位 + 后区(0-14)》→ 内链 `/qxc/rules`。

**第 2 周（双色球 / 7星彩纵深）**
- D8：《双色球红蓝球分区统计怎么读》→ `/ssq/frequency`。
- D10：《7星彩历史开奖怎么按期复盘》→ `/qxc/history`。
- D12：《中奖概率到底怎么算（组合数学科普）》→ `/odds`、`/qxc/odds`、`/ssq/odds`。

**第 3 周（六合彩，仅 Google 向）**
- D15：《六合彩正码与特码的区别》→ `/marksix/rules`（不进百度）。
- D17：《六合彩年度开奖归档怎么用》→ 年度归档页。
- D19：《为什么历史数据不能预测下一期》方法论强化 → `/strategy`、`/responsible`。

**第 4 周（品牌与回访）**
- D22：《弈彩的数据来源与更新机制》→ `/about`。
- D24：《理性娱乐：彩票是娱乐不是投资》→ `/responsible`。
- D26：邮件 newsletter 第一期（开奖数据摘要 + 科普）。
- D29：复盘收录情况，更新 sitemap `lastmod`，补提交未收录 URL。

---

## 8. Search Console / 百度搜索资源平台手动提交清单

### Google Search Console
- [ ] 新增 / 确认资源：**优先用 Domain property（`ckl.hk`，DNS 验证）**，可同时覆盖 `yicai.ckl.hk` 与 `www.ckl.hk`。
- [ ] 若用 URL-prefix：单独验证 `https://yicai.ckl.hk`（`index.html` 已有 google-site-verification meta，可用 HTML 标签法）。
- [ ] 提交 sitemap：`https://yicai.ckl.hk/sitemap.xml`。
- [ ] 用「网址检查」对以下页面请求编入索引：`/`、`/qxc/results`、`/qxc/history`、`/ssq/results`、`/marksix/results`。
- [ ] 旧域名 `www.ckl.hk` 资源：确认 301 生效后，观察「重复网页，Google 选择的规范网址与用户指定的不同」是否收敛到 yicai。
- [ ] （可选）使用「变更地址」工具（若 www → yicai 视为站点迁移）。

### 百度搜索资源平台
- [ ] 验证站点 `yicai.ckl.hk`（`index.html` 已保留 `codeva-9VvyVzNtsp` meta，用 HTML 标签验证）。
- [ ] 提交 sitemap：`https://yicai.ckl.hk/sitemap-baidu.xml`（**不要**提交 `sitemap.xml`，它含六合彩）。
- [ ] 手动提交 URL（仅双色球 / 7星彩 / 合规页）：`/`、`/ssq/results`、`/ssq/frequency`、`/qxc/results`、`/qxc/history`、`/strategy`、`/about`。
- [ ] 确认 `robots.txt` 中 `Baiduspider Disallow: /marksix/` 已生效（百度「robots 检测」工具）。
- [ ] **不要**在百度提交任何 `/marksix/*`。
- [ ] 如启用百度普通收录 API，推送 URL 列表同样只放双色球 / 7星彩 / 合规页。

---

## 9. 服务器部署步骤（Caddy / 301，需手动核对）

> 仓库内 `deploy/Caddyfile` 已是目标配置，但**线上 `/etc/caddy/Caddyfile` 可能已被手动改过**（已有 yicai 块），不要盲目覆盖。

```bash
ssh root@47.237.181.181
# 1. 先看线上现状
sudo cat /etc/caddy/Caddyfile

# 2. 与仓库版本对比
cd /opt/lottery-analysis && git pull
diff <(sudo cat /etc/caddy/Caddyfile) deploy/Caddyfile

# 3. 确认无误后覆盖（目标：yicai 提供内容，www/ckl.hk 301 → yicai）
sudo cp deploy/Caddyfile /etc/caddy/Caddyfile
sudo caddy validate --config /etc/caddy/Caddyfile   # 语法校验
sudo systemctl reload caddy

# 4. 验证 301 与内容
curl -sI https://www.ckl.hk/marksix/results | grep -i "location\|HTTP/"   # 期望 301 → https://yicai.ckl.hk/marksix/results
curl -sI https://yicai.ckl.hk/qxc/results   | grep -i "HTTP/\|content-type" # 期望 200 text/html
```

**前置**：`yicai.ckl.hk` 的 DNS A 记录需指向 `47.237.181.181`（若尚未指向，先加 DNS 再 reload Caddy，否则证书签发失败）。

---

## 10. 待办 / 风险

- [ ] `yicai.ckl.hk` DNS / TLS 证书确认（Caddy 自动签发，需 DNS 已生效）。
- [ ] 部署后用 `curl` 核对 301 链路与 qxc 静态页 `Content-Type: text/html`（注意 AGENTS.md 陷阱 #2：SPA fallback 会让任意路径返回 200，要看 Content-Type）。
- [ ] GSC / 百度收录观察期 2–4 周，跟踪 `www` 重复内容是否收敛。
- [ ] 通用页（/data 等）含六合彩 title，暂不进百度；若要进，需做 ssq/qxc 版 title。
- [ ] 后续可把 `sitemap.xml` / `sitemap-baidu.xml` 改为构建期脚本生成（由 routes 派生），减少手工维护 lastmod。

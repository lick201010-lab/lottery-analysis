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
- [x] 香港六合彩数据源：on.cc 优先，lottery.hk 回退，DB 最新期开奖兜底
- [x] 六合彩 fallback：爬虫失败时从数据库 `draws` 表读取最新一期
- [x] Jackpot upsert 逻辑（存在则更新，不存在则插入）

### Phase 6: 合规与规范
- [x] `RULES.md` — 记录颜色规则、名称规范、响应式策略、合规文字
- [x] `AGENTS.md` — 项目代理指南（空，待补充）

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
- **修复方案**: 增加 `lottery.hk/zh-hans/liuhecai/kaijiangjieguo/` 作为非赛马会来源，解析结构化结果表
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
- [ ] 补充 `AGENTS.md` 项目代理指南
- [ ] 考虑增加更多双色球备用数据源（如彩宝贝、中彩网）

---

## 部署备忘

```bash
# 服务器部署流程
cd /opt/lottery-analysis
git pull
cd backend
pkill -f "uvicorn"
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2 > uvicorn.log 2>&1 &

# 触发爬虫
curl -X POST https://api.ckl.hk/api/v1/jackpot/scrape

# 验证双色球
curl https://api.ckl.hk/api/v1/jackpot/latest?lottery_type=ssq

# 验证六合彩
curl https://api.ckl.hk/api/v1/jackpot/latest?lottery_type=marksix

# 前端构建（如有前端改动）
cd /opt/lottery-analysis/frontend
npm run build
```

---

## 技术决策记录

1. **为何用 SQLite 而非 PostgreSQL/MySQL**: 项目数据量小（< 1万条），SQLite 零配置、单文件备份方便
2. **为何用 datachart.500.com 而非官方 API**: 福彩官方 API (`cwl.gov.cn`) 返回 403，500.com 历史表格页数据完整且稳定
3. **为何六合彩用 DB fallback 而非外部爬虫**: HKJC/on.cc 等香港网站经常改版或加反爬，而数据库中已有完整历史数据
4. **为何前端用 Tailwind v4**: 最新版本支持 CSS-first 配置，与 Vite 集成更好

---

*最后更新: 2026-05-17*

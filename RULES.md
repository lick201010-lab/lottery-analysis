# 弈彩项目规范文档

> 本文件记录所有业务规则、UI规范和开发要求，供后续开发随时调取。

---

## 一、数字球颜色规则

### 1.1 六合彩（MarkSix）—— 红/蓝/绿三色球

每个号码有固定的官方颜色，**特别号也遵循同样的颜色规则**（不是统一红色）。

| 颜色 | 号码 |
|------|------|
| 🔴 红球 | 01, 02, 07, 08, 12, 13, 18, 19, 23, 24, 29, 30, 34, 35, 40, 45, 46 |
| 🔵 蓝球 | 03, 04, 09, 10, 14, 15, 20, 25, 26, 31, 36, 37, 41, 42, 47, 48 |
| 🟢 绿球 | 05, 06, 11, 16, 17, 21, 22, 27, 28, 32, 33, 38, 39, 43, 44, 49 |

**实现文件**：`frontend/src/components/NumberBall.vue`
- `lotteryType === "marksix"` 时，根据 `number` 值查表决定颜色
- `isSpecial` 不影响六合彩颜色（特码也是红/蓝/绿之一）

### 1.2 双色球（SSQ）—— 红球+蓝球

| 类型 | 颜色 | 范围 |
|------|------|------|
| 普通球 | 红色 | 1-33 |
| 特别号（蓝球）| 蓝色 | 1-16 |

**实现文件**：`frontend/src/components/NumberBall.vue`
- `lotteryType === "ssq"` 时，`isSpecial === false` → 红色，`isSpecial === true` → 蓝色

---

## 二、彩种名称规范

| 内部 key | 对外显示名称 | 禁止使用的旧名称 |
|----------|-------------|-----------------|
| `marksix` | **六合彩** | ❌ 香港彩 |
| `ssq` | **双色球** | ❌ 福利彩 |

**涉及位置**：
- `frontend/src/components/NavBar.vue` — 顶部切换按钮
- `frontend/src/views/Dashboard.vue` — 首页彩种标签
- `frontend/src/views/GenerateNumbers.vue` — 模拟选号标题
- `frontend/index.html` — meta description
- `backend/app/config.py` — `LOTTERY_CONFIG["name"]`

---

## 三、彩种数值规则

| 彩种 | 普通球数量 | 普通球范围 | 特别号范围 |
|------|-----------|-----------|-----------|
| 六合彩 | 6个 | 1-49 | 1-49 |
| 双色球 | 6个 | 1-33 | 1-16 |

**后端配置**：`backend/app/config.py` → `LOTTERY_CONFIG`
**后端生成**：`backend/app/routers/analysis.py` → `generate_numbers()` 已正确按配置生成

---

## 四、UI设计规范

### 4.1 主题色

采用 **Stripe Light** 风格：

| Token | 色值 | 用途 |
|-------|------|------|
| Canvas | `#ffffff` | 页面底色 |
| Surface | `#f6f9fc` | 卡片底色、输入框底色 |
| Primary | `#533afd` | 主色、按钮、高亮 |
| Primary Deep | `#4434d4` | 主色悬停 |
| Ink | `#0d253d` | 主标题文字 |
| Ink Secondary | `#273951` | 正文文字 |
| Muted | `#64748d` | 次要文字、标签 |
| Border | `#e3e8ee` | 边框、分割线 |
| Red | `#ea2261` | 错误、高频标识 |

### 4.2 顶部导航栏

- **背景**：淡紫色渐变 `bg-gradient-to-r from-[#f5f0ff] via-[#faf8ff] to-[#f0e8ff]`
- **底部边框**：`border-b border-[#e3e8ee]`
- **高度**：`h-[60px]`
- **固定定位**：`sticky top-0 z-50`
- **毛玻璃**：`backdrop-blur-md`
- **移动端**：右侧显示汉堡菜单，导航链接折叠到下拉面板

### 4.3 卡片样式

统一使用 `.card-stripe`：
```css
bg-white rounded-2xl border border-[#e3e8ee] shadow-sm
```

### 4.4 按钮样式

主按钮：
```css
bg-[#533afd] text-white font-bold rounded-xl
hover:shadow-lg disabled:opacity-50
```

---

## 五、响应式设计规范

### 5.1 断点策略

| 断点 | 宽度 | Tailwind前缀 |
|------|------|-------------|
| 手机 | < 640px | 默认（无前缀）|
| 小平板 | ≥ 640px | `sm:` |
| 平板 | ≥ 768px | `md:` |
| 桌面 | ≥ 1024px | `lg:` |
| 大屏 | ≥ 1280px | `xl:` |

### 5.2 各页面响应式要求

#### 导航栏（NavBar）
- `lg:` 以下隐藏桌面导航链接，显示汉堡菜单
- 彩种切换按钮始终显示，但字号可适当缩小

#### 首页（Dashboard）
- 统计卡片：`grid-cols-2 lg:grid-cols-4`
- Hero标题：`text-3xl sm:text-[42px]`
- 最新一期号码：`flex-wrap` 自动换行

#### 号码统计（FrequencyAnalysis）
- 标题区：`flex-col sm:flex-row`
- Top N按钮组：`overflow-x-auto` 防止溢出
- 冷热双栏：`grid-cols-1 md:grid-cols-2`
- 遗漏网格：`grid-cols-3 sm:grid-cols-5 md:grid-cols-7 lg:grid-cols-8`
- **排名表格**：手机隐藏 `特别号次数(sm:hidden)`、`上次出现(lg:hidden)`、`热度(md:hidden)`

#### 走势分析（PatternAnalysis）
- 饼图区：`grid-cols-1 md:grid-cols-2`
- 统计摘要：`grid-cols-2 md:grid-cols-4`
- 大数字：`text-xl sm:text-2xl`

#### 组合分析（PairAnalysis）
- 主内容区：`grid-cols-1 md:grid-cols-2`
- 数字选择器标题：`flex-col sm:flex-row`

#### 模拟选号（GenerateNumbers）
- 策略选择：`grid-cols-1 md:grid-cols-2 lg:grid-cols-3`
- 控制区：`flex-col sm:flex-row`
- 组数按钮：`overflow-x-auto`
- 结果统计网格：`grid-cols-2 sm:grid-cols-4 md:grid-cols-7`

#### 历史记录（DataManagement）
- 标题区：`flex-col sm:flex-row`
- **DrawTable表格**：手机隐藏 `日期(sm:hidden)`、`单双大小总和连号(md:hidden)`
- 开奖数字球间距：`gap-1.5 sm:gap-2`
- 分页按钮：保持在一行，必要时缩小 padding

### 5.3 表格通用规则

- 所有表格外层必须包裹 `overflow-x-auto`
- 非关键列在小屏幕使用 `hidden sm:table-cell` / `hidden md:table-cell` / `hidden lg:table-cell` 逐级隐藏
- 优先保留的列：编号/期号、核心数据（号码、次数）、操作按钮

---

## 六、合规性文字规范

| 禁止使用 | 替换为 |
|---------|--------|
| 号码生成 | 模拟选号 |
| 数据管理 | 历史记录 |
| 投注、下注、购买、推荐 | 避免使用 |

**免责声明**：所有页面底部或显眼位置必须保留：
> 仅供娱乐参考，不构成任何投注建议。

---

## 七、技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3 + Vite + Tailwind CSS v4 + Chart.js |
| 后端 | FastAPI + SQLAlchemy async + SQLite |
| 部署 | 阿里云香港服务器 + Caddy 反向代理 |
| 域名 | www.ckl.hk（前端）、api.ckl.hk（后端）|
| CI/CD | GitHub Actions 定时触发数据更新 |

---

## 八、部署流程

```bash
# 本地开发
npm run build          # 构建前端
git add -A && git commit -m "..."
git push origin main

# 服务器端（手动或配置 webhook）
cd /opt/lottery-analysis
git pull
cd frontend && npm run build
```

---

*文档创建时间：2026-05-16*
*最后更新：2026-05-16*

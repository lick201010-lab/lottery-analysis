# Data Sources Reference

## SSQ (双色球)

### datachart.500.com (Primary)
- URL: `https://datachart.500.com/ssq/history/newinc/history.php`
- Format: HTML table
- Data: 期号, 6红球, 蓝球, 快乐星期天, 奖池奖金, 一等奖注数/奖金, 二等奖注数/奖金, 总投注额, 开奖日期
- Issues: Table may have extra serial-number column; parser auto-detects offset
- Access: Works from HK server

### 500.com XML (Fallback)
- URL: `https://kaijiang.500.com/static/info/kaijiang/xml/ssq/list.xml`
- Format: XML
- Data: 期号, 开奖号码 (red|blue), 开奖时间
- Limitation: No jackpot amount, no prize breakdown

### cwl.gov.cn (Official)
- URL: `https://www.cwl.gov.cn/cwl_admin/kjxx/findDrawNotice`
- Status: ❌ 403 Forbidden from HK server

## MarkSix (六合彩)

### win.on.cc (Primary — best effort)
- URL: `https://win.on.cc/marksix/`
- Format: HTML
- Status: ✅ Accessible, parsing not yet robust
- Notes: Page has `last10_result` class, Chinese (zh-HK)

### lottery.hk (Fallback)
- URL: `https://lottery.hk/zh-hans/liuhecai/kaijiangjieguo/`
- Format: HTML table
- Data: 编号, 日期, 6个正码, 特别号
- Status: ✅ Working locally; latest verified result `26/052` on `2026-05-16`
- Notes: This is not HKJC, but has a stable results table and is suitable for latest-result fallback.

### Database Fallback
- Table: `draws`
- Source: `scripts/fetch_marksix.py` (HKJC historical data)
- Complete history available, no external dependency

### Other Attempted Sources
| Source | Status |
|--------|--------|
| bet.hkjc.com | ❌ Timeout/empty |
| kj.13322.com | ❌ DNS fail |
| kaijiang.78500.cn | ⚠️ Needs User-Agent |
| datachart.500.com/hk6 | ❌ 404 |

## Parser Strategies

### SSQ HTML Table Parser
```
Strategy 1: <tr class="t_tr1"> → extract <td> cells
Strategy 2: Scan all <tr> for first row with 5-digit draw number
Strategy 3: Markdown-style | delimited format
```

### MarkSix Latest Result Parser
```
Strategy 1: win.on.cc smart multi-pattern parser
Strategy 2: lottery.hk results table parser
Strategy 3: 500.com / generic HTML fallback
Strategy 4: Database latest draw fallback in /api/v1/jackpot/scrape
```

### Column Mapping (after offset detection)
```
offset+0: draw_number (5 digits)
offset+1 to offset+6: red_balls
offset+7: blue_ball
offset+8: 快乐星期天 (empty)
offset+9: pool_amount
offset+10: first_prize_count
offset+11: first_prize_amount
offset+12: second_prize_count
offset+13: second_prize_amount
offset+14: sales_amount
offset+15: draw_date
```

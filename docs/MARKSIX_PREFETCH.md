# MarkSix 抓取出口（根治说明）

## 问题
GitHub 托管 Actions / 部分云端环境访问 `lottery.hk` 会 `ConnectTimeout`。
免费 Actions 额度打满后（约到 2026-12-01）定时任务也无法再跑。

## 方案（已验证）
1. **主源改 HKJC GraphQL**：`https://info.cld.hkjc.com/graphql/base/`  
   与后端 `jackpot_scraper._try_hkjc_graphql` 同一白名单 query。  
   实测可达：本机（免代理）、agent box、`quant-sg`（`8.222.236.30`）。  
   `lottery.hk` 仅作回退。
2. **本机 launchd 兜底**（不消耗 Actions 分钟）：开奖日 二/四/六 22:30（Asia/Singapore）跑 `scripts/update.py` 并 push。
3. **可选后续**：在 `quant-sg` 装 cron + repo deploy key（机器常开，优于本机睡眠）。**不要**把奕彩 `47.237.181.181` 当唯一出口（当前 SSH/HTTP 不稳）。

## 产物路径
- 中间：`marksix_draws.json`
- 入库：`frontend/public/data/{draws,frequency,pairs,patterns,trends}.json`
- 入口：`scripts/update.py` → `fetch_marksix.py` → `merge_marksix.py`（+ SSQ）

## 本机安装
```bash
# 仓库目录示例
git clone https://github.com/lick201010-lab/lottery-analysis.git ~/lottery-analysis
cd ~/lottery-analysis
python3 -m pip install --user -r requirements.txt
bash scripts/setup-macos-launchd.sh
```

本机访问 GitHub 需本机代理 `http://127.0.0.1:7897`（launchd 已写入该环境变量）；HKJC 可直连。

卸载：`bash scripts/remove-macos-launchd.sh`

## Actions
`update-marksix.yml` 保留 `workflow_dispatch`；schedule 在额度恢复前可先关掉，避免无效失败。额度恢复后，HKJC 主源应让托管 runner 重新可用。

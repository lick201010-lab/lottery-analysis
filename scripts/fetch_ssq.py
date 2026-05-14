#!/usr/bin/env python3
"""Fetch SSQ (双色球) data from 500.com"""
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

URL = "https://datachart.500.com/ssq/history/newinc/history.php?start=00001&end=99999"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
}

print("Fetching SSQ data from 500.com...")
r = requests.get(URL, headers=HEADERS, timeout=30)
r.raise_for_status()
r.encoding = "utf-8"

soup = BeautifulSoup(r.text, "html.parser")
rows = soup.find("tbody", id="tdata")
if rows:
    rows = rows.find_all("tr")
else:
    rows = soup.find_all("tr", attrs={"align": "center"})

draws = []
for row in rows:
    tds = row.find_all("td")
    if len(tds) < 10:
        continue
    texts = [td.get_text(strip=True) for td in tds]
    
    # 500.com format: [issue, red1-6, blue, empty, pool, 1st_count, 1st_amount, 2nd_count, 2nd_amount, total_sales, date]
    # Issue is like "26054" -> "2026054"
    issue_short = texts[0]
    if not issue_short.isdigit():
        continue
    
    # Convert short issue to full: "26054" -> "2026054"
    if len(issue_short) == 5:
        year_prefix = "20" + issue_short[:2]
        issue_num = issue_short[2:]
        issue = year_prefix + issue_num
    else:
        issue = issue_short
    
    # Red balls are in columns 1-6
    red_balls = []
    for i in range(1, 7):
        try:
            red_balls.append(int(texts[i]))
        except (ValueError, IndexError):
            break
    if len(red_balls) != 6:
        continue
    
    # Blue ball is column 7
    try:
        blue_ball = int(texts[7])
    except (ValueError, IndexError):
        continue
    
    # Date is the last column
    date_str = texts[-1]
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        iso_date = dt.strftime("%Y-%m-%d")
    except:
        iso_date = date_str
    
    nums = sorted(red_balls)
    odd = sum(1 for n in nums if n % 2 == 1)
    small = sum(1 for n in nums if n <= 16)
    
    draws.append({
        "draw_number": issue,
        "draw_date": iso_date,
        "num1": nums[0], "num2": nums[1], "num3": nums[2],
        "num4": nums[3], "num5": nums[4], "num6": nums[5],
        "special_num": blue_ball,
        "odd_count": odd, "even_count": 6 - odd,
        "small_count": small, "big_count": 6 - small,
        "has_consecutive": any(nums[i+1] - nums[i] == 1 for i in range(5)),
        "sum_total": sum(nums),
        "lottery_type": "ssq",
    })

# Sort by date desc
draws.sort(key=lambda x: x["draw_date"], reverse=True)

print(f"Total SSQ draws fetched: {len(draws)}")
if draws:
    print(f"First: {draws[0]['draw_number']} {draws[0]['draw_date']}")
    print(f"Last: {draws[-1]['draw_number']} {draws[-1]['draw_date']}")

out_path = "frontend/public/data/ssq_draws.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(draws, f, ensure_ascii=False, indent=2)
print(f"Saved to {out_path}")

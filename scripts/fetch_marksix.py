import requests
from bs4 import BeautifulSoup
import json, re
from datetime import datetime

url = 'https://lottery.hk/zh-hans/liuhecai/kaijiangjieguo/'
r = requests.get(url, timeout=15, headers={'User-Agent': 'Mozilla/5.0'})
r.raise_for_status()

soup = BeautifulSoup(r.text, 'html.parser')
table = soup.find('table')
rows = table.find_all('tr')

draws = []
for row in rows:
    cols = row.find_all(['td', 'th'])
    if len(cols) < 3:
        continue
    
    period = cols[0].get_text(strip=True)
    if not re.match(r'^\d{2}/\d{3}$', period):
        continue
    
    date_str = cols[1].get_text(strip=True)
    balls_ul = cols[2].find('ul', class_='balls')
    if not balls_ul:
        continue
    
    lis = balls_ul.find_all('li')
    numbers = [li.get_text(strip=True) for li in lis if '-plus' not in (li.get('class') or [])]
    special = [li.get_text(strip=True) for li in lis if '-plus' in (li.get('class') or [])]
    
    try:
        dt = datetime.strptime(date_str, '%d/%m/%Y')
        iso_date = dt.strftime('%Y-%m-%d')
    except:
        iso_date = date_str
    
    draws.append({
        "draw_number": period,
        "draw_date": iso_date,
        "numbers": [int(n) for n in numbers],
        "special_number": int(special[0]) if special else None,
        "source": "lottery.hk"
    })

print(f"Total draws fetched: {len(draws)}")
print(json.dumps(draws[:5], ensure_ascii=False, indent=2))

with open('marksix_draws.json', 'w', encoding='utf-8') as f:
    json.dump(draws, f, ensure_ascii=False, indent=2)

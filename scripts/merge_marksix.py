import json
from collections import Counter

# Load existing data
existing = json.load(open('frontend/public/data/draws.json', encoding='utf-8'))
print(f"Existing: {len(existing)} draws")

# Load new fetched data
new_raw = json.load(open('marksix_draws.json', encoding='utf-8'))
print(f"New fetched: {len(new_raw)} draws")

def convert(draw):
    nums = draw['numbers']
    special = draw.get('special_number')
    
    # Determine odd/even and small/big (1-24 small, 25-49 big)
    odd_count = sum(1 for n in nums if n % 2 == 1)
    even_count = 6 - odd_count
    small_count = sum(1 for n in nums if n <= 24)
    big_count = 6 - small_count
    
    # Check consecutive
    sorted_nums = sorted(nums)
    has_consecutive = any(sorted_nums[i+1] - sorted_nums[i] == 1 for i in range(5))
    
    return {
        "draw_number": draw['draw_number'],
        "draw_date": draw['draw_date'],
        "num1": nums[0],
        "num2": nums[1],
        "num3": nums[2],
        "num4": nums[3],
        "num5": nums[4],
        "num6": nums[5],
        "special_num": special,
        "odd_count": odd_count,
        "even_count": even_count,
        "small_count": small_count,
        "big_count": big_count,
        "has_consecutive": has_consecutive,
        "sum_total": sum(nums),
        "lottery_type": "marksix"
    }

new_converted = [convert(d) for d in new_raw]

# Merge: use draw_number as key, new data overrides old
existing_map = {d['draw_number']: d for d in existing}
for d in new_converted:
    existing_map[d['draw_number']] = d

merged = sorted(existing_map.values(), key=lambda x: x['draw_date'], reverse=True)
print(f"After merge: {len(merged)} draws")
print(f"First: {merged[0]['draw_number']} {merged[0]['draw_date']}")
print(f"Last: {merged[-1]['draw_number']} {merged[-1]['draw_date']}")

# Save draws.json
with open('frontend/public/data/draws.json', 'w', encoding='utf-8') as f:
    json.dump(merged, f, ensure_ascii=False)
print("Saved draws.json")

# Recalculate frequency
all_numbers = []
all_special = []
for d in merged:
    all_numbers.extend([d['num1'], d['num2'], d['num3'], d['num4'], d['num5'], d['num6']])
    if d.get('special_num'):
        all_special.append(d['special_num'])

freq = Counter(all_numbers)
special_freq = Counter(all_special)

frequency = {
    "numbers": {str(k): v for k, v in sorted(freq.items(), key=lambda x: x[0])},
    "special_numbers": {str(k): v for k, v in sorted(special_freq.items(), key=lambda x: x[0])},
    "total_draws": len(merged)
}
with open('frontend/public/data/frequency.json', 'w', encoding='utf-8') as f:
    json.dump(frequency, f, ensure_ascii=False)
print("Saved frequency.json")

# Recalculate pairs
pairs = Counter()
for d in merged:
    nums = sorted([d['num1'], d['num2'], d['num3'], d['num4'], d['num5'], d['num6']])
    for i in range(6):
        for j in range(i+1, 6):
            pairs[(nums[i], nums[j])] += 1

pairs_list = [
    {"num1": k[0], "num2": k[1], "count": v}
    for k, v in pairs.most_common(1000)
]
with open('frontend/public/data/pairs.json', 'w', encoding='utf-8') as f:
    json.dump(pairs_list, f, ensure_ascii=False)
print("Saved pairs.json")

# Patterns
patterns = {"odd_even": Counter(), "small_big": Counter(), "consecutive": Counter()}
for d in merged:
    patterns["odd_even"][f"{d['odd_count']}:{d['even_count']}"] += 1
    patterns["small_big"][f"{d['small_count']}:{d['big_count']}"] += 1
    patterns["consecutive"]["yes" if d['has_consecutive'] else "no"] += 1

patterns_json = {
    k: dict(v.most_common()) for k, v in patterns.items()
}
with open('frontend/public/data/patterns.json', 'w', encoding='utf-8') as f:
    json.dump(patterns_json, f, ensure_ascii=False)
print("Saved patterns.json")

# Trends - last 100 draws hot/cold
recent = merged[:100]
recent_nums = []
for d in recent:
    recent_nums.extend([d['num1'], d['num2'], d['num3'], d['num4'], d['num5'], d['num6']])
recent_freq = Counter(recent_nums)

# Calculate skips (how many draws since last appearance)
last_seen = {i: 0 for i in range(1, 50)}
for idx, d in enumerate(merged):
    nums = [d['num1'], d['num2'], d['num3'], d['num4'], d['num5'], d['num6']]
    for n in nums:
        if last_seen[n] == 0:
            last_seen[n] = idx

skips = {str(k): v for k, v in last_seen.items()}
hot = [k for k, v in recent_freq.most_common(10)]
cold = [k for k, v in sorted(recent_freq.items(), key=lambda x: x[1])[:10]]

with open('frontend/public/data/trends.json', 'w', encoding='utf-8') as f:
    json.dump({
        "hot_numbers": hot,
        "cold_numbers": cold,
        "skips": skips,
        "recent_frequency": {str(k): v for k, v in recent_freq.most_common()}
    }, f, ensure_ascii=False)
print("Saved trends.json")
print("All done!")

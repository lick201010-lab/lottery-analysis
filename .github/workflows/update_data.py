import json
import os
import requests
from collections import Counter, defaultdict

DATA_URL = "https://raw.githubusercontent.com/icelam/mark-six-data-visualization/master/data/all.json"
OUT_DIR = "frontend/public/data"
LOTTERY_TYPE = "marksix"
MAX_REGULAR = 49


def parse_draws(raw_data):
    draws = []
    for item in raw_data:
        nums = [int(str(n).strip()) for n in item.get("no", [])]
        special = int(str(item.get("sno", "0")).strip())
        if len(nums) != 6:
            continue
        sorted_nums = sorted(nums)
        midpoint = MAX_REGULAR // 2
        draws.append({
            "draw_number": str(item.get("id", "")),
            "draw_date": item.get("date", ""),
            "num1": sorted_nums[0], "num2": sorted_nums[1], "num3": sorted_nums[2],
            "num4": sorted_nums[3], "num5": sorted_nums[4], "num6": sorted_nums[5],
            "special_num": special,
            "odd_count": sum(1 for n in sorted_nums if n % 2 == 1),
            "even_count": sum(1 for n in sorted_nums if n % 2 == 0),
            "small_count": sum(1 for n in sorted_nums if n <= midpoint),
            "big_count": sum(1 for n in sorted_nums if n > midpoint),
            "has_consecutive": any(sorted_nums[i+1] - sorted_nums[i] == 1 for i in range(5)),
            "sum_total": sum(sorted_nums),
            "lottery_type": LOTTERY_TYPE,
        })
    return sorted(draws, key=lambda d: d["draw_date"], reverse=True)


def compute_frequency(draws):
    freq = {n: {"total": 0, "special": 0, "last_date": None, "last_draw": None, "last_seq": -1} for n in range(1, MAX_REGULAR + 1)}
    for idx, d in enumerate(reversed(draws)):
        regulars = [d["num1"], d["num2"], d["num3"], d["num4"], d["num5"], d["num6"]]
        for n in regulars:
            freq[n]["total"] += 1
            freq[n]["last_date"] = d["draw_date"]
            freq[n]["last_draw"] = d["draw_number"]
            freq[n]["last_seq"] = idx
        freq[d["special_num"]]["special"] += 1
        if freq[d["special_num"]]["last_seq"] < idx:
            freq[d["special_num"]]["last_date"] = d["draw_date"]
            freq[d["special_num"]]["last_draw"] = d["draw_number"]
            freq[d["special_num"]]["last_seq"] = idx

    total_draws = len(draws)
    result = []
    for n in range(1, MAX_REGULAR + 1):
        f = freq[n]
        missed = total_draws - f["last_seq"] - 1 if f["last_seq"] >= 0 else total_draws
        score = f["total"] * 100 + f["special"] * 50
        result.append({
            "number": n,
            "total_appearances": f["total"],
            "special_appearances": f["special"],
            "last_appearance_date": f["last_date"],
            "last_appearance_draw": f["last_draw"],
            "consecutive_missed": missed,
            "hotness_score": score,
        })
    return sorted(result, key=lambda x: x["hotness_score"], reverse=True)


def compute_pairs(draws):
    pair_counts = Counter()
    for d in reversed(draws):
        regulars = [d["num1"], d["num2"], d["num3"], d["num4"], d["num5"], d["num6"]]
        for i in range(6):
            for j in range(i + 1, 6):
                a, b = regulars[i], regulars[j]
                pair_counts[(min(a, b), max(a, b))] += 1
    return [{"num_a": a, "num_b": b, "co_occurrences": c} for (a, b), c in pair_counts.most_common()]


def compute_patterns(draws):
    odd_even_counts = Counter()
    big_small_counts = Counter()
    consecutive_counts = Counter()
    range_size = 10
    range_labels = [f"{i}-{min(i+range_size-1, 49)}" for i in range(1, 50, range_size)]
    range_counts_dict = {lbl: 0 for lbl in range_labels}
    sum_values = []

    for d in draws:
        regulars = [d["num1"], d["num2"], d["num3"], d["num4"], d["num5"], d["num6"]]
        odd_even_counts[f"{d['odd_count']}:{d['even_count']}"] += 1
        big_small_counts[f"{d['small_count']}:{d['big_count']}"] += 1
        sorted_ns = sorted(regulars)
        cons = sum(1 for i in range(5) if sorted_ns[i+1] - sorted_ns[i] == 1)
        consecutive_counts[str(cons)] += 1
        for n in regulars:
            idx = min((n - 1) // range_size, len(range_labels) - 1)
            range_counts_dict[range_labels[idx]] += 1
        sum_values.append(d["sum_total"])

    if sum_values:
        s_min, s_max = min(sum_values), max(sum_values)
        bin_width = max(1, (s_max - s_min) // 20)
        bins = Counter()
        for s in sum_values:
            b = (s // bin_width) * bin_width
            bins[b] += 1
        sum_histogram = [{"bin": k, "count": v} for k, v in sorted(bins.items())]
    else:
        sum_histogram = []

    odd_total = sum(d["odd_count"] for d in draws)
    even_total = sum(d["even_count"] for d in draws)
    small_total = sum(d["small_count"] for d in draws)
    big_total = sum(d["big_count"] for d in draws)
    total = len(draws)

    return {
        "total_draws": total,
        "odd_even": {"labels": ["奇数", "偶数"], "values": [odd_total, even_total]},
        "big_small": {"labels": ["大数", "小数"], "values": [big_total, small_total]},
        "consecutive": {"labels": list(consecutive_counts.keys()), "values": list(consecutive_counts.values())},
        "range_distribution": {"labels": range_labels, "values": [range_counts_dict[lbl] for lbl in range_labels]},
        "sum_histogram": sum_histogram,
        "summary": {
            "odd_pct": round(odd_total / (odd_total + even_total) * 100, 1) if (odd_total + even_total) > 0 else 0,
            "even_pct": round(even_total / (odd_total + even_total) * 100, 1) if (odd_total + even_total) > 0 else 0,
            "small_pct": round(small_total / (small_total + big_total) * 100, 1) if (small_total + big_total) > 0 else 0,
            "big_pct": round(big_total / (small_total + big_total) * 100, 1) if (small_total + big_total) > 0 else 0,
            "avg_sum": round(sum(sum_values) / total, 1) if total > 0 else 0,
            "sum_range": f"{min(sum_values)}-{max(sum_values)}" if sum_values else "N/A",
        },
    }


def compute_trends(draws):
    regulars_per_draw = [[d["num1"], d["num2"], d["num3"], d["num4"], d["num5"], d["num6"]] for d in reversed(draws)]
    window = 50
    trends = {}
    for n in range(1, MAX_REGULAR + 1):
        data = []
        for i in range(len(regulars_per_draw)):
            if i < window - 1:
                continue
            count = sum(1 for j in range(i - window + 1, i + 1) if n in regulars_per_draw[j])
            orig_idx = len(regulars_per_draw) - 1 - i
            data.append({"draw_number": draws[orig_idx]["draw_number"], "count": count})
        trends[str(n)] = data
    return trends


def main():
    print("Fetching latest data...")
    resp = requests.get(DATA_URL, timeout=120)
    resp.raise_for_status()
    raw_data = resp.json()

    print(f"Downloaded {len(raw_data)} records")

    draws = parse_draws(raw_data)
    print(f"Parsed {len(draws)} valid draws, latest: {draws[0]['draw_date'] if draws else 'none'}")

    os.makedirs(OUT_DIR, exist_ok=True)

    with open(f"{OUT_DIR}/draws.json", "w", encoding="utf-8") as f:
        json.dump(draws, f, ensure_ascii=False)

    freq = compute_frequency(draws)
    with open(f"{OUT_DIR}/frequency.json", "w", encoding="utf-8") as f:
        json.dump(freq, f, ensure_ascii=False)

    pairs = compute_pairs(draws)
    with open(f"{OUT_DIR}/pairs.json", "w", encoding="utf-8") as f:
        json.dump(pairs, f, ensure_ascii=False)

    patterns = compute_patterns(draws)
    with open(f"{OUT_DIR}/patterns.json", "w", encoding="utf-8") as f:
        json.dump(patterns, f, ensure_ascii=False)

    trends = compute_trends(draws)
    with open(f"{OUT_DIR}/trends.json", "w", encoding="utf-8") as f:
        json.dump(trends, f, ensure_ascii=False)

    print("Done!")


if __name__ == "__main__":
    main()

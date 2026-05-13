import sqlite3
import json
from collections import Counter, defaultdict
from datetime import date

DB_PATH = "data/marksix.db"
OUT_DIR = "frontend/public/data"


def export_draws(conn):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT draw_number, draw_date, num1, num2, num3, num4, num5, num6, "
        "special_num, odd_count, even_count, small_count, big_count, "
        "has_consecutive, sum_total, lottery_type "
        "FROM draws WHERE lottery_type = 'marksix' ORDER BY draw_date DESC"
    )
    rows = cursor.fetchall()
    draws = []
    for r in rows:
        draws.append({
            "draw_number": r[0],
            "draw_date": r[1],
            "num1": r[2], "num2": r[3], "num3": r[4],
            "num4": r[5], "num5": r[6], "num6": r[7],
            "special_num": r[8],
            "odd_count": r[9], "even_count": r[10],
            "small_count": r[11], "big_count": r[12],
            "has_consecutive": bool(r[13]),
            "sum_total": r[14],
            "lottery_type": r[15],
        })
    return draws


def export_frequency(conn):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT number, total_appearances, special_appearances, "
        "last_appearance_date, last_appearance_draw, consecutive_missed, hotness_score "
        "FROM frequency_cache WHERE lottery_type = 'marksix' ORDER BY hotness_score DESC"
    )
    rows = cursor.fetchall()
    return [
        {
            "number": r[0], "total_appearances": r[1], "special_appearances": r[2],
            "last_appearance_date": r[3], "last_appearance_draw": r[4],
            "consecutive_missed": r[5], "hotness_score": r[6],
        }
        for r in rows
    ]


def export_pairs(conn):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT num_a, num_b, co_occurrences "
        "FROM pair_frequency WHERE lottery_type = 'marksix' "
        "ORDER BY co_occurrences DESC"
    )
    rows = cursor.fetchall()
    return [{"num_a": r[0], "num_b": r[1], "co_occurrences": r[2]} for r in rows]


def compute_patterns(draws):
    """Compute pattern analysis from draws data."""
    odd_even_counts = Counter()
    big_small_counts = Counter()
    consecutive_counts = Counter()
    range_counts = Counter()
    sum_values = []

    range_size = 10
    range_labels = [f"{i}-{min(i+range_size-1, 49)}" for i in range(1, 50, range_size)]
    range_counts_dict = {lbl: 0 for lbl in range_labels}

    for d in draws:
        regulars = [d["num1"], d["num2"], d["num3"], d["num4"], d["num5"], d["num6"]]
        oe_key = f"{d['odd_count']}:{d['even_count']}"
        odd_even_counts[oe_key] += 1

        bs_key = f"{d['small_count']}:{d['big_count']}"
        big_small_counts[bs_key] += 1

        sorted_ns = sorted(regulars)
        cons = sum(1 for i in range(5) if sorted_ns[i+1] - sorted_ns[i] == 1)
        consecutive_counts[str(cons)] += 1

        for n in regulars:
            idx = min((n - 1) // range_size, len(range_labels) - 1)
            range_counts_dict[range_labels[idx]] += 1

        sum_values.append(d["sum_total"])

    # Sum histogram
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
        "odd_even": {
            "labels": ["奇数", "偶数"],
            "values": [odd_total, even_total],
        },
        "big_small": {
            "labels": ["大数", "小数"],
            "values": [big_total, small_total],
        },
        "consecutive": {
            "labels": list(consecutive_counts.keys()),
            "values": list(consecutive_counts.values()),
        },
        "range_distribution": {
            "labels": range_labels,
            "values": [range_counts_dict[lbl] for lbl in range_labels],
        },
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


def compute_trend(draws, number, window=50):
    """Compute rolling frequency trend for a given number."""
    regulars_per_draw = [
        [d["num1"], d["num2"], d["num3"], d["num4"], d["num5"], d["num6"]]
        for d in reversed(draws)
    ]
    data = []
    for i in range(len(regulars_per_draw)):
        if i < window - 1:
            continue
        count = sum(1 for j in range(i - window + 1, i + 1) if number in regulars_per_draw[j])
        orig_idx = len(regulars_per_draw) - 1 - i
        data.append({
            "draw_number": draws[orig_idx]["draw_number"],
            "count": count,
        })
    return data


def main():
    conn = sqlite3.connect(DB_PATH)

    print("Exporting draws...")
    draws = export_draws(conn)
    with open(f"{OUT_DIR}/draws.json", "w", encoding="utf-8") as f:
        json.dump(draws, f, ensure_ascii=False)

    print("Exporting frequency...")
    freq = export_frequency(conn)
    with open(f"{OUT_DIR}/frequency.json", "w", encoding="utf-8") as f:
        json.dump(freq, f, ensure_ascii=False)

    print("Exporting pairs...")
    pairs = export_pairs(conn)
    with open(f"{OUT_DIR}/pairs.json", "w", encoding="utf-8") as f:
        json.dump(pairs, f, ensure_ascii=False)

    print("Computing patterns...")
    patterns = compute_patterns(draws)
    with open(f"{OUT_DIR}/patterns.json", "w", encoding="utf-8") as f:
        json.dump(patterns, f, ensure_ascii=False)

    print("Computing trends for all numbers...")
    trends = {}
    for n in range(1, 50):
        trends[str(n)] = compute_trend(draws, n, 50)
    with open(f"{OUT_DIR}/trends.json", "w", encoding="utf-8") as f:
        json.dump(trends, f, ensure_ascii=False)

    conn.close()
    print(f"Done! Exported {len(draws)} draws.")


if __name__ == "__main__":
    main()

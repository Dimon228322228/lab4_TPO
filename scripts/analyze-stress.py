#!/usr/bin/env python3
"""Краткий разбор stress.csv для отчёта."""

import csv
import sys
from collections import defaultdict
from pathlib import Path


def bucket_analysis(rows, bucket_ms=5000):
    by_second = defaultdict(list)
    for row in rows:
        if row.get("success", "").lower() != "true":
            continue
        ts = int(row["timeStamp"]) // 1000
        by_second[ts].append((int(row["elapsed"]), int(row["allThreads"])))

    if not by_second:
        return []

    start = min(by_second)
    buckets = defaultdict(lambda: {"elapsed": [], "threads": []})
    for sec, samples in by_second.items():
        bucket = ((sec - start) * 1000) // bucket_ms
        for elapsed, threads in samples:
            buckets[bucket]["elapsed"].append(elapsed)
            buckets[bucket]["threads"].append(threads)

    result = []
    for bucket in sorted(buckets):
        data = buckets[bucket]
        load = sum(data["threads"]) / len(data["threads"])
        avg = sum(data["elapsed"]) / len(data["elapsed"])
        result.append((load, avg, len(data["elapsed"])))
    return result


def main():
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("stress/stress.csv")
    rows = list(csv.DictReader(path.open(encoding="utf-8")))
    sla = 640

    total = len(rows)
    ok = [r for r in rows if r.get("success", "").lower() == "true"]
    fail = total - len(ok)
    codes = defaultdict(int)
    for r in rows:
        codes[r["responseCode"]] += 1

    elapsed_ok = [int(r["elapsed"]) for r in ok]
    over_sla = sum(1 for e in elapsed_ok if e > sla)
    threads = [int(r["allThreads"]) for r in rows]

    print(f"Файл: {path}")
    print(f"Всего запросов: {total}")
    print(f"success=true: {len(ok)}, success=false: {fail}")
    print(f"HTTP коды: {dict(codes)}")
    if elapsed_ok:
        print(f"Avg (успешные): {sum(elapsed_ok)/len(elapsed_ok):.0f} мс")
        print(f"Min/Max: {min(elapsed_ok)}/{max(elapsed_ok)} мс")
        print(f"> {sla} мс: {over_sla}/{len(elapsed_ok)} ({100*over_sla/len(elapsed_ok):.1f}%)")
    print(f"Макс. потоков (allThreads): {max(threads)}")

    buckets = bucket_analysis(rows)
    if buckets:
        print("\nОкна 5 с (нагрузка -> среднее время):")
        peak = max(buckets, key=lambda x: x[1])
        for load, avg, n in buckets:
            mark = " <-- пик" if (load, avg, n) == peak else ""
            over = " [>SLA]" if avg > sla else ""
            print(f"  ~{load:5.1f} потоков: {avg:6.0f} мс ({n} запр.){over}{mark}")

        first_over = next(((l, a) for l, a, _ in buckets if a > sla), None)
        if first_over:
            print(f"\nТочка отказа (среднее > SLA): ~{first_over[0]:.0f} потоков, {first_over[1]:.0f} мс")
        else:
            print(f"\nСреднее время ни разу не превысило {sla} мс.")
            print(f"Пик среднего: ~{peak[0]:.0f} потоков, {peak[1]:.0f} мс")


if __name__ == "__main__":
    main()

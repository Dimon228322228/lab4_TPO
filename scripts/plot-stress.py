#!/usr/bin/env python3
"""Строит график: среднее время отклика vs число активных потоков (нагрузка)."""

import csv
import sys
from collections import defaultdict
from pathlib import Path

try:
    import matplotlib.pyplot as plt
except ImportError:
    print("Установите matplotlib: pip install matplotlib")
    sys.exit(1)


def load_samples(path: Path):
    by_second = defaultdict(list)
    with path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("success", "").lower() != "true":
                continue
            try:
                ts = int(row["timeStamp"]) // 1000
                elapsed = int(row["elapsed"])
                threads = int(row["allThreads"])
            except (KeyError, ValueError):
                continue
            by_second[ts].append((elapsed, threads))

    # усреднение по 5-секундным окнам
    if not by_second:
        return [], []

    start = min(by_second)
    bucket_ms = 5000
    buckets = defaultdict(lambda: {"elapsed": [], "threads": []})
    for sec, samples in by_second.items():
        bucket = ((sec - start) * 1000) // bucket_ms
        for elapsed, threads in samples:
            buckets[bucket]["elapsed"].append(elapsed)
            buckets[bucket]["threads"].append(threads)

    loads, times = [], []
    for bucket in sorted(buckets):
        data = buckets[bucket]
        loads.append(sum(data["threads"]) / len(data["threads"]))
        times.append(sum(data["elapsed"]) / len(data["elapsed"]))

    return loads, times


def main():
    if len(sys.argv) < 3:
        print("Usage: plot-stress.py <stress.csv> <output.png> [max_ms]")
        sys.exit(1)

    csv_path = Path(sys.argv[1])
    out_path = Path(sys.argv[2])
    max_ms = int(sys.argv[3]) if len(sys.argv) > 3 else 640

    loads, times = load_samples(csv_path)
    if not loads:
        print("Нет успешных сэмплов в CSV")
        sys.exit(1)

    plt.figure(figsize=(10, 6))
    plt.plot(loads, times, marker="o", linewidth=1.5, markersize=4)
    plt.axhline(max_ms, color="red", linestyle="--", label=f"SLA {max_ms} мс")
    plt.xlabel("Среднее число активных потоков (нагрузка)")
    plt.ylabel("Среднее время отклика, мс")
    plt.title("Зависимость времени отклика от нагрузки")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    main()

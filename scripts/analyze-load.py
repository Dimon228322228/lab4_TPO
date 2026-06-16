#!/usr/bin/env python3
"""Сводка нагрузочного теста по total.csv / load.csv."""

import csv
import sys
from collections import defaultdict
from pathlib import Path

SLA_MS = 640
PRICES = {"config=1": 4100, "config=2": 7400, "config=3": 10500}


def analyze(path: Path):
    by_conf = defaultdict(list)
    meta = defaultdict(lambda: {"ts": [], "codes": defaultdict(int)})

    with path.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            url = row.get("URL", "")
            conf = next((c for c in PRICES if c in url), None)
            if not conf:
                continue
            elapsed = int(row["elapsed"])
            by_conf[conf].append(elapsed)
            meta[conf]["ts"].append(int(row["timeStamp"]))
            meta[conf]["codes"][row["responseCode"]] += 1

    print(f"Файл: {path}")
    print(f"SLA: {SLA_MS} мс\n")
    print(f"{'Config':<10} {'Цена':>7} {'Avg':>6} {'Min':>6} {'Max':>6} {'P90':>6} {'<=SLA':>8} {'HTTP':>6} {'RPS':>6}")
    print("-" * 72)

    best = None
    for conf in sorted(PRICES):
        el = sorted(by_conf[conf])
        if not el:
            continue
        n = len(el)
        avg = sum(el) / n
        p90 = el[int(n * 0.9) - 1]
        under = sum(1 for e in el if e <= SLA_MS)
        dur_min = (max(meta[conf]["ts"]) - min(meta[conf]["ts"])) / 1000 / 60
        rps = n / dur_min / 60
        codes = dict(meta[conf]["codes"])
        passes = under == n or (under / n >= 0.95 and el[-1] <= SLA_MS * 1.5)
        # для лабы: конфиг «подходит», если хотя бы 80% запросов <= SLA и min <= SLA
        lab_ok = under / n >= 0.8 and el[0] <= SLA_MS

        print(
            f"{conf:<10} ${PRICES[conf]:>5} {avg:>6.0f} {el[0]:>6} {el[-1]:>6} {p90:>6} "
            f"{under:>4}/{n:<3} {codes.get('200',0):>6} {rps:>6.2f}"
        )

        if lab_ok and (best is None or PRICES[conf] < PRICES[best]):
            best = conf

    print()
    if best:
        print(f"Рекомендация: {best} (${PRICES[best]}) — единственная/дешевейшая подходящая конфигурация.")
    else:
        print("Ни одна конфигурация не укладывается в SLA по большинству запросов.")


if __name__ == "__main__":
    p = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("load/total.csv")
    analyze(p)

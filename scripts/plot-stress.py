#!/usr/bin/env python3
"""График стресс-теста: время отклика каждого запроса по порядку (слева направо)."""

import csv
import sys
from pathlib import Path

try:
    import matplotlib.pyplot as plt
except ImportError:
    print("Установите matplotlib: pip install matplotlib")
    sys.exit(1)


def load_requests(path: Path):
    rows = []
    with path.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            try:
                rows.append(
                    {
                        "ts": int(row["timeStamp"]),
                        "elapsed": int(row["elapsed"]),
                        "threads": int(row["allThreads"]),
                        "ok": row.get("responseCode") == "200",
                    }
                )
            except (KeyError, ValueError):
                continue
    rows.sort(key=lambda r: r["ts"])
    return rows


def first_error_index(rows):
    for i, r in enumerate(rows):
        if not r["ok"]:
            return i, r["threads"]
    return None, None


def main():
    if len(sys.argv) < 3:
        print("Usage: plot-stress.py <results.csv> <output.png>")
        sys.exit(1)

    csv_path = Path(sys.argv[1])
    out_path = Path(sys.argv[2])

    rows = load_requests(csv_path)
    if not rows:
        print("Нет данных в CSV")
        sys.exit(1)

    x = list(range(1, len(rows) + 1))
    y = [r["elapsed"] for r in rows]
    err_idx, err_threads = first_error_index(rows)
    abs_max = max(y)

    # широкий холст — «растяжение» по горизонтали
    width = max(18, len(rows) / 400)
    fig, ax = plt.subplots(figsize=(width, 6))

    ax.plot(x, y, linewidth=0.6, color="#2563eb", alpha=0.85, label="Время отклика")

    if err_idx is not None:
        ax.axvline(err_idx + 1, color="#dc2626", linestyle="--", linewidth=1.2,
                   label=f"Первая ошибка сервера (~{err_threads} потоков)")

    ax.set_xlabel("Номер запроса (хронологический порядок)")
    ax.set_ylabel("Время отклика, мс")
    ax.set_xlim(1, len(rows))
    ax.set_ylim(0, abs_max * 1.05)
    ax.grid(True, alpha=0.25)
    ax.legend(loc="upper left")
    ax.set_title("Время отклика по каждому запросу (стресс-тест, config=3)")

    ax.annotate(
        f"Запросов: {len(rows)}, макс.: {abs_max} мс",
        xy=(0.99, 0.97), xycoords="axes fraction",
        ha="right", va="top", fontsize=9, color="#444",
    )

    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    print(f"Saved: {out_path} ({len(rows)} точек)")
    if err_idx is not None:
        print(f"Первая HTTP-ошибка: запрос №{err_idx + 1}, ~{err_threads} потоков")


if __name__ == "__main__":
    main()

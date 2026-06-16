#!/usr/bin/env python3
import csv
import sys
from collections import Counter
from pathlib import Path

path = Path(sys.argv[1])
rows = list(csv.DictReader(path.open(encoding="utf-8")))
codes = Counter(r["responseCode"] for r in rows)
print(f"File: {path}")
print(f"Total: {len(rows)}")
print(f"HTTP codes: {dict(codes)}")
print(f"success=false: {sum(1 for r in rows if r['success'].lower() == 'false')}")

for code in ("403", "503"):
    hits = [r for r in rows if r["responseCode"] == code]
    if hits:
        first = min(hits, key=lambda r: int(r["timeStamp"]))
        print(
            f"First HTTP {code}: allThreads={first['allThreads']}, "
            f"elapsed={first['elapsed']} ms"
        )
    else:
        print(f"HTTP {code}: none")

fails = [r for r in rows if r["success"].lower() == "false"]
if fails:
    first = min(fails, key=lambda r: int(r["timeStamp"]))
    print(
        f"First success=false: HTTP {first['responseCode']}, "
        f"allThreads={first['allThreads']}, elapsed={first['elapsed']} ms"
    )
    msg = first.get("failureMessage", "")
    if msg:
        print(f"  reason: {msg[:150]}")
else:
    print("First success=false: none (all success=true)")

"""Diagnose L5e board candidates under current forbids."""
from __future__ import annotations

import csv
from pathlib import Path

import MetaTrader5 as mt5

BOARD = Path(
    r"C:\Users\C2K\AppData\Roaming\MetaQuotes\Terminal\D0E8209F77C8CF37AD8BF550E51FF075\MQL5\Files\jarvis\board.csv"
)
FORBID = {
    ("EURCHF", "SELL"), ("GBPCHF", "SELL"), ("EURCNH", "BUY"), ("AUDUSD", "SELL"), ("GBPUSD", "SELL"),
    ("NZDUSD", "SELL"), ("CHFJPY", "SELL"), ("EURAUD", "BUY"), ("EURCAD", "BUY"), ("CADJPY", "BUY"),
    ("USDCHF", "BUY"), ("EURCHF", "BUY"), ("GBPCAD", "BUY"), ("EURNZD", "BUY"), ("GBPCHF", "BUY"),
    ("USDCAD", "BUY"), ("GBPAUD", "BUY"), ("EURUSD", "SELL"), ("USDJPY", "BUY"), ("AUDJPY", "BUY"),
}
SKIP = {"CADCHF", "USDSEK", "CHFJPY", "EURCHF", "GBPCHF"}
INDEX = {
    "FRA40", "HK50", "US30M", "USOIL", "CHINA50", "CHINAH", "EUSTX50", "IT40", "JPN225",
    "GER40", "DE40", "UK100", "NAS100", "SP500", "US500", "US500M", "AUS200", "SPA35",
    "BTCUSD", "ETHUSD", "US30", "USTEC", "USTECH100M", "NETH25", "NOR25", "SA40",
    "SE30", "SWI20", "US2000", "MIDDE50",
}

mt5.initialize()
rows = list(csv.DictReader(BOARD.open(encoding="utf-8", errors="replace")))
ts = max(r["ts"] for r in rows)
cur = [r for r in rows if r["ts"] == ts]
print("board_ts", ts)
ok = []
seen = set()
for r in cur:
    if r["strategy"] not in ("S1", "S2", "S3", "S4"):
        continue
    act = r["act"]
    if act.startswith("FIRE_"):
        d = act.split("_", 1)[1]
        prio = 0
    elif act == "WAIT_LOADED":
        d = "BUY" if r["tide"] == "long_only" else "SELL" if r["tide"] == "short_only" else None
        if not d:
            continue
        prio = 1
    else:
        continue
    sym = r["symbol"].replace(".sim", "")
    reasons = []
    if sym != r["symbol"]:
        reasons.append("sim")
    if sym in INDEX or sym.startswith("X"):
        reasons.append("index")
    if sym in SKIP:
        reasons.append("skip")
    if "SEK" in sym.upper():
        reasons.append("sek")
    if (sym, d) in FORBID:
        reasons.append("forbid")
    info = mt5.symbol_info(sym)
    if info is None:
        mt5.symbol_select(sym, True)
        info = mt5.symbol_info(sym)
    if info is None:
        reasons.append("noinfo")
    else:
        if info.trade_mode != 4:
            reasons.append(f"tmode{info.trade_mode}")
        if info.volume_min > 0.01 + 1e-12:
            reasons.append(f"vmin{info.volume_min}")
    if not reasons and sym not in seen:
        ok.append((prio, sym, d, act, r["strategy"]))
        seen.add(sym)
    elif reasons and sym not in INDEX and not sym.startswith("X") and "SEK" not in sym.upper():
        print(f"blocked {sym:8} {d:4} {act:16} {reasons}")
print("ok", len(ok))
for row in sorted(ok):
    print(row)
mt5.shutdown()

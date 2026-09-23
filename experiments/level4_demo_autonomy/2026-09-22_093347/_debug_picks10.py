import csv
from pathlib import Path
import MetaTrader5 as mt5

BOARD = Path(
    r"C:\Users\C2K\AppData\Roaming\MetaQuotes\Terminal\D0E8209F77C8CF37AD8BF550E51FF075\MQL5\Files\jarvis\board.csv"
)
FORBID = {
    ("EURCAD", "BUY"), ("GBPUSD", "SELL"), ("USDCAD", "BUY"), ("EURGBP", "SELL"), ("GBPCAD", "BUY"),
    ("EURUSD", "BUY"), ("EURCHF", "SELL"), ("USDCHF", "SELL"), ("GBPCHF", "SELL"), ("CADJPY", "SELL"),
    ("AUDUSD", "BUY"), ("EURAUD", "BUY"), ("EURJPY", "SELL"), ("USDJPY", "SELL"), ("AUDJPY", "SELL"),
    ("NZDUSD", "BUY"), ("EURGBP", "BUY"), ("EURCNH", "BUY"), ("GBPJPY", "SELL"), ("USDSEK", "SELL"),
}
SKIP = {"CADCHF", "USDSEK"}
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
print("ts", ts)
for r in cur:
    if r["strategy"] not in ("S1", "S2", "S3", "S4"):
        continue
    act = r["act"]
    if act.startswith("FIRE_"):
        d = act.split("_", 1)[1]
    elif act == "WAIT_LOADED":
        d = "BUY" if r["tide"] == "long_only" else "SELL" if r["tide"] == "short_only" else None
        if not d:
            continue
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
            reasons.append(f"mode={info.trade_mode}")
        if info.volume_min > 0.01 + 1e-12:
            reasons.append(f"vmin={info.volume_min}")
    mark = "OK" if not reasons else ",".join(reasons)
    print(f"{sym:10} {d:4} {r['strategy']} {act:14} -> {mark}")
mt5.shutdown()

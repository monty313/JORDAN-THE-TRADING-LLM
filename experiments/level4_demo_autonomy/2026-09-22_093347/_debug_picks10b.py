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

mt5.initialize()
rows = list(csv.DictReader(BOARD.open(encoding="utf-8", errors="replace")))
ts = max(r["ts"] for r in rows)
cur = [r for r in rows if r["ts"] == ts]
fx = []
for r in cur:
    if r["strategy"] not in ("S1", "S2", "S3", "S4"):
        continue
    sym = r["symbol"]
    if ".sim" in sym or sym.startswith("X") or any(c.isdigit() for c in sym):
        continue
    if sym in SKIP:
        continue
    info = mt5.symbol_info(sym)
    if info is None:
        mt5.symbol_select(sym, True)
        info = mt5.symbol_info(sym)
    vmin = info.volume_min if info else None
    mode = info.trade_mode if info else None
    fx.append((sym, r["set"], r["strategy"], r["act"], r["tide"], mode, vmin))

# unique symbol acts that could be traded at 0.01
print("=== all FX S1-S4 rows tradeable 0.01 ===")
seen = set()
for sym, s, st, act, tide, mode, vmin in sorted(fx):
    if mode != 4 or (vmin is not None and vmin > 0.01 + 1e-12):
        continue
    if act.startswith("FIRE_"):
        d = act.split("_", 1)[1]
    elif act == "WAIT_LOADED":
        d = "BUY" if tide == "long_only" else "SELL" if tide == "short_only" else "?"
    else:
        continue
    key = (sym, d, st, act)
    if key in seen:
        continue
    seen.add(key)
    forbid = (sym, d) in FORBID
    print(f"{sym:8} {d:4} {st} {act:14} forbid={forbid}")

print("\n=== blocked by vmin among FX FIRE/WAIT ===")
for sym, s, st, act, tide, mode, vmin in sorted(fx):
    if act.startswith("FIRE_") or act == "WAIT_LOADED":
        if vmin and vmin > 0.01:
            print(sym, act, "vmin", vmin, "mode", mode)
mt5.shutdown()

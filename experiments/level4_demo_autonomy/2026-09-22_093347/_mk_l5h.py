"""Build L5h forced runner: soft-avoid L5g, mix directions.

KEEP mentor_preflight stop check before mt5.initialize.
Do not replace block_if_mentor_says_stop with a fresh-token-only gate.
"""
from __future__ import annotations

from pathlib import Path

src = Path(r"C:\Users\C2K\Desktop\MT5 to agent\experiments\level4_demo_autonomy\2026-09-22_093347\run_batch31_l5g_forced.py")
out = Path(r"C:\Users\C2K\Desktop\MT5 to agent\experiments\level4_demo_autonomy\2026-09-22_093347\run_batch32_l5h_forced.py")
text = src.read_text(encoding="utf-8")

if "block_if_mentor_says_stop" not in text:
    raise SystemExit("mentor_preflight missing in source — abort")
if "if block_if_mentor_says_stop(SCRIPT):" not in text:
    needle = "def main() -> int:\n"
    insert = (
        "def main() -> int:\n"
        "    if block_if_mentor_says_stop(SCRIPT):\n"
        "        return 0\n\n"
    )
    if needle not in text:
        raise SystemExit("main() not found")
    text = text.replace(needle, insert, 1)

if "block_if_fresh_stop_token" in text or "stop_token_gate" in text:
    raise SystemExit("token-only gate not allowed — keep mentor stop")

repls = [
    ("batch31 L5g", "batch32 L5h"),
    ("L5g m771249", "L5h m771249"),
    ("L5g close", "L5h close"),
    ('"L5g"', '"L5h"'),
    ("our_L5g_left", "our_L5h_left"),
    ("_picks31.json", "_picks32.json"),
    ("batch31_signals.json", "batch32_signals.json"),
    ("batch31_jobs.json", "batch32_jobs.json"),
    ("batch31_results.json", "batch32_results.json"),
    ("batch31_l5g_held_closed", "batch32_l5h_held_closed"),
    ("level4-demo-forced-five-l5g", "level4-demo-forced-five-l5h"),
    ("L5g forced five", "L5h forced five"),
    ("forced_five_l5g", "forced_five_l5h"),
    ("soft_avoid_l5f", "soft_avoid_l5g"),
    ("Soft-avoid L5d pairs", "Soft-avoid L5g pairs; mix BUY/SELL"),
]
for a, b in repls:
    text = text.replace(a, b)

old = """SOFT_AVOID = {
    (\"EURUSD\", \"SELL\"),
    (\"USDCAD\", \"BUY\"),
    (\"EURGBP\", \"SELL\"),
    (\"GBPCHF\", \"BUY\"),
    (\"USDCHF\", \"BUY\"),
}"""
new = """SOFT_AVOID = {
    (\"EURCHF\", \"SELL\"),
    (\"EURJPY\", \"SELL\"),
    (\"GBPUSD\", \"SELL\"),
    (\"NZDUSD\", \"SELL\"),
    (\"AUDUSD\", \"SELL\"),
}
# Extra soft: do not stack another all-SELL of these three if other symbols quote
REPEAT_SELL_SOFT = {(\"GBPUSD\", \"SELL\"), (\"NZDUSD\", \"SELL\"), (\"AUDUSD\", \"SELL\")}"""
if old not in text:
    raise SystemExit("soft avoid not found")
text = text.replace(old, new)

# Patch soft scoring and pick loop for direction mix
old_soft = """        soft = 1 if (sym, d) in SOFT_AVOID else 0
        stops = int(getattr(info, "trade_stops_level", 0) or 0)
        spr = spread_pts(info, tick)
        pts_plan = max(base_sl(sym), stops + spr)
        cands.append(
            {
                "symbol": sym,
                "direction": d,
                "act": act,
                "strategy": meta.get("strategy", "S0"),
                "set": int(meta.get("set") or 0),
                "anchor_tf": meta.get("anchor_tf", "M5"),
                "htf1": meta.get("htf1_tf", "M15"),
                "htf2": meta.get("htf2_tf", "H1"),
                "tide": meta.get("tide", "forced"),
                "regime": meta.get("regime", "forced"),
                "state": meta.get("state", "forced"),
                "reason": meta.get("reason", "forced"),
                "cmp": meta.get("cmp", ""),
                "spread_points": spr,
                "closed_bar_time": meta.get("closed_bar_time", ""),
                "open1": meta.get("open1", ""),
                "high1": meta.get("high1", ""),
                "low1": meta.get("low1", ""),
                "close1": meta.get("close1", ""),
                "digits": info.digits,
                "point": info.point,
                "stops_level": stops,
                "sl_points_planned": pts_plan,
                "sl_tier": "jpy_cnh" if is_wide_sl(sym) else "major",
                "soft": soft,
                "prio": soft,  # prefer non-avoid first
            }
        )

    cands.sort(key=lambda x: (x["soft"], x["spread_points"], x["symbol"]))
    picked, seen = [], set()
    for c in cands:
        if c["symbol"] in seen:
            continue
        picked.append(c)
        seen.add(c["symbol"])
        if len(picked) >= 5:
            break

    # If soft-avoid left us short, refill allowing soft-avoid (already in list) — already sorted
    # Must have 5: if still short, fail hard only when quotes truly missing
    if len(picked) < 5:
        log({"event": "forced_pick_short", "n": len(picked), "picked": [(p["symbol"], p["direction"]) for p in picked]})
    (EXP / "_picks32.json").write_text(json.dumps(picked, indent=2), encoding="utf-8")
    return picked"""

# After rename, picks file is _picks32 - the old block still says _picks31 in source before rename applied... 
# We already renamed _picks31 -> _picks32 in text. So old_soft should use _picks32.

old_soft = old_soft.replace("_picks32.json", "_picks32.json")  # noop safety

# The source still has _picks32 after repls. Soft block still has soft=1 scoring. Find by unique string.
old_pick_tail = """        soft = 1 if (sym, d) in SOFT_AVOID else 0
        stops = int(getattr(info, "trade_stops_level", 0) or 0)
        spr = spread_pts(info, tick)
        pts_plan = max(base_sl(sym), stops + spr)
        cands.append(
            {
                "symbol": sym,
                "direction": d,
                "act": act,
                "strategy": meta.get("strategy", "S0"),
                "set": int(meta.get("set") or 0),
                "anchor_tf": meta.get("anchor_tf", "M5"),
                "htf1": meta.get("htf1_tf", "M15"),
                "htf2": meta.get("htf2_tf", "H1"),
                "tide": meta.get("tide", "forced"),
                "regime": meta.get("regime", "forced"),
                "state": meta.get("state", "forced"),
                "reason": meta.get("reason", "forced"),
                "cmp": meta.get("cmp", ""),
                "spread_points": spr,
                "closed_bar_time": meta.get("closed_bar_time", ""),
                "open1": meta.get("open1", ""),
                "high1": meta.get("high1", ""),
                "low1": meta.get("low1", ""),
                "close1": meta.get("close1", ""),
                "digits": info.digits,
                "point": info.point,
                "stops_level": stops,
                "sl_points_planned": pts_plan,
                "sl_tier": "jpy_cnh" if is_wide_sl(sym) else "major",
                "soft": soft,
                "prio": soft,  # prefer non-avoid first
            }
        )

    cands.sort(key=lambda x: (x["soft"], x["spread_points"], x["symbol"]))
    picked, seen = [], set()
    for c in cands:
        if c["symbol"] in seen:
            continue
        picked.append(c)
        seen.add(c["symbol"])
        if len(picked) >= 5:
            break

    # If soft-avoid left us short, refill allowing soft-avoid (already in list) — already sorted
    # Must have 5: if still short, fail hard only when quotes truly missing
    if len(picked) < 5:
        log({"event": "forced_pick_short", "n": len(picked), "picked": [(p["symbol"], p["direction"]) for p in picked]})
    (EXP / "_picks32.json").write_text(json.dumps(picked, indent=2), encoding="utf-8")
    return picked"""

new_pick_tail = """        soft = 0
        if (sym, d) in SOFT_AVOID:
            soft = 1
        if (sym, d) in REPEAT_SELL_SOFT:
            soft = max(soft, 2)
        # Also emit opposite-direction candidate for mix (soft+0.5 vs board side)
        stops = int(getattr(info, "trade_stops_level", 0) or 0)
        spr = spread_pts(info, tick)
        pts_plan = max(base_sl(sym), stops + spr)
        base = {
            "symbol": sym,
            "act": act,
            "strategy": meta.get("strategy", "S0"),
            "set": int(meta.get("set") or 0),
            "anchor_tf": meta.get("anchor_tf", "M5"),
            "htf1": meta.get("htf1_tf", "M15"),
            "htf2": meta.get("htf2_tf", "H1"),
            "tide": meta.get("tide", "forced"),
            "regime": meta.get("regime", "forced"),
            "state": meta.get("state", "forced"),
            "reason": meta.get("reason", "forced"),
            "cmp": meta.get("cmp", ""),
            "spread_points": spr,
            "closed_bar_time": meta.get("closed_bar_time", ""),
            "open1": meta.get("open1", ""),
            "high1": meta.get("high1", ""),
            "low1": meta.get("low1", ""),
            "close1": meta.get("close1", ""),
            "digits": info.digits,
            "point": info.point,
            "stops_level": stops,
            "sl_points_planned": pts_plan,
            "sl_tier": "jpy_cnh" if is_wide_sl(sym) else "major",
        }
        cands.append({**base, "direction": d, "soft": soft, "prio": soft, "board_side": True})
        opp = "BUY" if d == "SELL" else "SELL"
        opp_soft = 0.5
        if (sym, opp) in SOFT_AVOID:
            opp_soft = 1.5
        if (sym, opp) in REPEAT_SELL_SOFT:
            opp_soft = max(opp_soft, 2.5)
        cands.append({**base, "direction": opp, "act": f"FORCED_MIX_{opp}", "soft": opp_soft, "prio": opp_soft, "board_side": False})

    # Prefer direction mix: greedily pick next that balances BUY/SELL, then soft, then board_side, then spread
    picked, seen = [], set()
    n_buy = n_sell = 0
    while len(picked) < 5:
        remain = [c for c in cands if c["symbol"] not in seen]
        if not remain:
            break
        def score(c):
            # lower is better
            mix_pen = 0
            if n_buy > n_sell and c["direction"] == "BUY":
                mix_pen = 1
            elif n_sell > n_buy and c["direction"] == "SELL":
                mix_pen = 1
            elif n_buy == n_sell:
                mix_pen = 0
            # Prefer board_side slightly
            board_pen = 0 if c.get("board_side") else 0.25
            return (mix_pen, c["soft"], board_pen, c["spread_points"], c["symbol"])
        remain.sort(key=score)
        c = remain[0]
        picked.append(c)
        seen.add(c["symbol"])
        if c["direction"] == "BUY":
            n_buy += 1
        else:
            n_sell += 1

    if len(picked) < 5:
        log({"event": "forced_pick_short", "n": len(picked), "picked": [(p["symbol"], p["direction"]) for p in picked]})
    log({"event": "direction_mix", "buys": n_buy, "sells": n_sell, "picked": [f"{p['symbol']} {p['direction']}" for p in picked]})
    (EXP / "_picks32.json").write_text(json.dumps(picked, indent=2), encoding="utf-8")
    return picked"""

if old_pick_tail not in text:
    raise SystemExit("pick_five tail not found")
text = text.replace(old_pick_tail, new_pick_tail)

if "L5h m771249" not in text:
    raise SystemExit("L5h comment missing")
if "REPEAT_SELL_SOFT" not in text:
    raise SystemExit("repeat sell soft missing")
if "block_if_mentor_says_stop" not in text:
    raise SystemExit("mentor stop stripped — abort write")
if "block_if_fresh_stop_token" in text or "stop_token_gate" in text:
    raise SystemExit("token-only gate not allowed — abort write")

out.write_text(text, encoding="utf-8")
print("ok", "direction_mix" in text, "L5h m771249" in text)

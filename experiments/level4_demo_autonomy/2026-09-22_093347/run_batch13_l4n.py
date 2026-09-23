"""Level 4 batch13 L4n. Magic 771249.
SL: majors max(80, stops+spread); JPY/CNH max(250, stops+spread).
No USDSEK / no SEK. Hold 5m in-process. One attempt. No retry.
"""
from __future__ import annotations

import csv
import json
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import MetaTrader5 as mt5

from mentor_preflight import block_if_mentor_says_stop, log_plan_vs_board

MAGIC = 771249
VOLUME = 0.01
BASE_SL_MAJOR = 80
BASE_SL_EXOTIC = 250
HOLD_SEC = 300
COMMENT = "L4n m771249"
EXP = Path(r"C:\Users\C2K\Desktop\MT5 to agent\experiments\level4_demo_autonomy\2026-09-22_093347")
SCRIPT = Path(__file__).name
LOG = EXP / "demo_trade_tape.jsonl"
FORCED = Path(r"C:\Users\C2K\Desktop\MT5 to agent\JARVIS V1\research\forced_signals.jsonl")
ATLAS = EXP / "atlas_reviews.jsonl"
DECISION = EXP / "decision_tape.jsonl"
HANDOFF = EXP / "reports" / "handoff.md"
BOARD = Path(
    r"C:\Users\C2K\AppData\Roaming\MetaQuotes\Terminal\D0E8209F77C8CF37AD8BF550E51FF075\MQL5\Files\jarvis\board.csv"
)

# This pass: JPY/CNH get 250-pt floor; SEK banned entirely
WIDE_SL_CCY = {"JPY", "CNH", "CNY"}

FORBID = {
    ("EURCHF", "SELL"),
    ("GBPCHF", "SELL"),
    ("GBPAUD", "SELL"),
    ("USDCAD", "BUY"),
    ("GBPUSD", "SELL"),
}
SKIP_SYMBOLS = {"CADCHF", "USDSEK"}
INDEX_LIKE = {
    "FRA40", "HK50", "US30M", "USOIL", "CHINA50", "CHINAH", "EUSTX50", "IT40", "JPN225",
    "GER40", "DE40", "UK100", "NAS100", "SP500", "US500", "US500M", "AUS200", "SPA35",
    "BTCUSD", "ETHUSD", "US30", "USTEC", "USTECH100M", "NETH25", "NOR25", "SA40",
    "SE30", "SWI20", "US2000", "MIDDE50",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def log(obj: dict) -> None:
    line = json.dumps(obj, separators=(",", ":"))
    with LOG.open("a", encoding="utf-8", newline="\n") as f:
        f.write(line + "\n")
    print(line, flush=True)


def append_jsonl(path: Path, obj: dict) -> None:
    with path.open("a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(obj, separators=(",", ":")) + "\n")


def has_sek(symbol: str) -> bool:
    s = symbol.upper()
    return "SEK" in s


def is_wide_sl(symbol: str) -> bool:
    s = symbol.upper()
    if len(s) >= 6:
        return s[:3] in WIDE_SL_CCY or s[3:6] in WIDE_SL_CCY
    return any(c in s for c in WIDE_SL_CCY)


def base_sl(symbol: str) -> int:
    return BASE_SL_EXOTIC if is_wide_sl(symbol) else BASE_SL_MAJOR


def spread_pts(info, tick) -> int:
    if tick is not None and info.point:
        return max(0, int(round((tick.ask - tick.bid) / info.point)))
    return int(getattr(info, "spread", 0) or 0)


def sl_points(symbol: str, info, tick) -> int:
    stops = int(getattr(info, "trade_stops_level", 0) or 0)
    return max(base_sl(symbol), stops + spread_pts(info, tick))


def sl_price(direction: str, price: float, pts: int, point: float, digits: int) -> float:
    if direction == "BUY":
        return round(price - pts * point, digits)
    return round(price + pts * point, digits)


def pick_five() -> list[dict]:
    rows = list(csv.DictReader(BOARD.open(encoding="utf-8", errors="replace")))
    ts = max(r["ts"] for r in rows)
    cur = [r for r in rows if r["ts"] == ts]
    log({"event": "board_ts", "ts": ts})
    cands = []
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
        if sym != r["symbol"] or sym in INDEX_LIKE or sym.startswith("X") or sym in SKIP_SYMBOLS:
            continue
        if has_sek(sym):
            continue
        if (sym, d) in FORBID:
            continue
        info = mt5.symbol_info(sym)
        if info is None:
            mt5.symbol_select(sym, True)
            info = mt5.symbol_info(sym)
        if info is None or info.trade_mode != 4 or info.volume_min > 0.01 + 1e-12:
            continue
        tick = mt5.symbol_info_tick(sym)
        stops = int(getattr(info, "trade_stops_level", 0) or 0)
        spr = spread_pts(info, tick) if tick else int(info.spread)
        pts_plan = max(base_sl(sym), stops + spr)
        cands.append(
            {
                "symbol": sym,
                "direction": d,
                "act": act,
                "strategy": r["strategy"],
                "set": int(r["set"]),
                "anchor_tf": r["anchor_tf"],
                "htf1": r["htf1_tf"],
                "htf2": r["htf2_tf"],
                "tide": r["tide"],
                "regime": r["regime"],
                "state": r["state"],
                "reason": r["reason"],
                "cmp": r["cmp"],
                "spread_points": spr,
                "closed_bar_time": r["closed_bar_time"],
                "open1": r["open1"],
                "high1": r["high1"],
                "low1": r["low1"],
                "close1": r["close1"],
                "digits": info.digits,
                "point": info.point,
                "stops_level": stops,
                "sl_points_planned": pts_plan,
                "sl_tier": "jpy_cnh" if is_wide_sl(sym) else "major",
                "prio": prio,
            }
        )
    cands.sort(key=lambda x: (x["prio"], x["spread_points"], x["symbol"]))
    picked, seen = [], set()
    for c in cands:
        if c["symbol"] in seen:
            continue
        picked.append(c)
        seen.add(c["symbol"])
        if len(picked) >= 5:
            break
    (EXP / "_picks13.json").write_text(json.dumps(picked, indent=2), encoding="utf-8")
    return picked


def build_signals(picks: list[dict], cycle_id: str, ts_utc: datetime) -> list[dict]:
    broker = (ts_utc + timedelta(hours=3)).strftime("%Y.%m.%d %H:%M:%S")
    ny = ts_utc.astimezone(ZoneInfo("America/New_York")).strftime("%Y-%m-%dT%H:%M:%S%z")
    ny = ny[:-2] + ":" + ny[-2:]
    due = (ts_utc + timedelta(minutes=5)).strftime("%Y-%m-%dT%H:%M:%SZ")
    out = []
    for i, p in enumerate(picks, 1):
        sym, direction = p["symbol"], p["direction"]
        mt5.symbol_select(sym, True)
        tick = mt5.symbol_info_tick(sym)
        info = mt5.symbol_info(sym)
        point = float(info.point)
        digits = int(info.digits)
        bid, ask = float(tick.bid), float(tick.ask)
        entry = ask if direction == "BUY" else bid
        pts = sl_points(sym, info, tick)
        sl = sl_price(direction, entry, pts, point, digits)
        try:
            bar_dt = datetime.strptime(p["closed_bar_time"], "%Y.%m.%d %H:%M:%S").replace(
                tzinfo=timezone(timedelta(hours=3))
            )
            age = int((ts_utc - bar_dt.astimezone(timezone.utc)).total_seconds())
        except Exception:
            age = 0
        topo = (
            "launch_continuation_bet"
            if "full_body" in (p.get("reason") or "")
            else "slingshot_load_continuation_bet"
        )
        out.append(
            {
                "signal_id": f"{cycle_id}_{sym}_{p['set']}_{p['strategy']}_{i}",
                "cycle_id": cycle_id,
                "slot": i,
                "mode": "FORCED_SIGNAL_RESEARCH",
                "timestamp_utc": ts_utc.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "timestamp_broker": broker,
                "timestamp_ny": ny,
                "symbol": sym,
                "set_id": int(p["set"]),
                "anchor_tf": p["anchor_tf"],
                "htf1": p["htf1"],
                "htf2": p["htf2"],
                "anchor_closed_bar_time": p["closed_bar_time"],
                "data_age_seconds": age,
                "spread_points": int(p["spread_points"]),
                "spread_price": round(int(p["spread_points"]) * point, digits + 2),
                "point_size": point,
                "digits": digits,
                "research_direction": direction,
                "research_confidence_0_100": 50,
                "research_topology": topo,
                "strategy_alignment": p["strategy"],
                "tide": p["tide"],
                "regime": p["regime"],
                "ltf_state": "launch" if str(p.get("act", "")).startswith("FIRE_") else "loaded",
                "role_map": {
                    "force": [f"Strategy tide {p['tide']}"],
                    "inertia": [f"Board reason {p.get('reason')}"],
                    "velocity": [p.get("cmp") or ""],
                    "equilibrium": [],
                    "regime_gate": [],
                    "expansion": ["UNDEFINED"],
                    "volume_confirm": [],
                },
                "relations": [f"Official act {p['act']}", "Tradeable demo FX"],
                "raw_snapshot": {
                    "open": float(p["open1"]) if p.get("open1") not in (None, "") else None,
                    "high": float(p["high1"]) if p.get("high1") not in (None, "") else None,
                    "low": float(p["low1"]) if p.get("low1") not in (None, "") else None,
                    "close": float(p["close1"]) if p.get("close1") not in (None, "") else None,
                    "cmp": p.get("cmp"),
                    "live_bid": bid,
                    "live_ask": ask,
                    "planned_sl": sl,
                    "planned_sl_points": pts,
                    "sl_tier": p.get("sl_tier"),
                    "stops_level": p.get("stops_level"),
                },
                "reason_locked_before_outcome": (
                    f"Closed-bar {p['strategy']} {p['act']} set {p['set']} tide {p['tide']}. "
                    f"Research {direction} five-minute demo; SL {pts} pts "
                    f"(max of {base_sl(sym)} and stops_level+spread; tier={p.get('sl_tier')})."
                ),
                "known_counterevidence": ["Protective stop is research harness, not doctrine invalidation"],
                "warning_context": ["Level 4 demo autonomy; desk mentoring act stays WAIT_NO_TRADE"],
                "desk_act": "WAIT_NO_TRADE",
                "desk_block_reason": "Level 4 demo research round-trip",
                "entry_bid": bid,
                "entry_ask": ask,
                "entry_executable_price": entry,
                "planned_stop": sl,
                "evaluation_due_utc": due,
                "outcome_status": "PENDING",
                "commission_status": "NOT_INCLUDED",
                "doctrine_version": "007-v1-readonly",
                "config_hash": "level4-demo-sl-major80-jpycnh250-nosek",
            }
        )
    return out


def fill_from_history(symbol: str, direction: str, signal_id: str, pts: int, sl: float, result) -> dict | None:
    ticket = int(getattr(result, "order", 0) or 0)
    entry = float(getattr(result, "price", 0) or 0)
    from_dt = datetime.now(timezone.utc) - timedelta(minutes=5)
    to_dt = datetime.now(timezone.utc) + timedelta(minutes=1)
    deals = mt5.history_deals_get(from_dt, to_dt) or []
    pos_id = ticket
    for d in deals:
        if d.symbol == symbol and d.magic == MAGIC and d.entry == mt5.DEAL_ENTRY_IN:
            if abs(d.time - time.time()) < 30 or (ticket and d.position_id == ticket):
                pos_id = d.position_id
                entry = float(d.price)
                break
    if not pos_id and not entry:
        return None
    exit_px = None
    close_path = "unknown"
    for d in deals:
        if d.position_id == pos_id and d.entry == mt5.DEAL_ENTRY_OUT:
            exit_px = float(d.price)
            close_path = "stop" if d.reason == mt5.DEAL_REASON_SL else "five_minute"
            break
    fill = {
        "event": "fill_already_closed",
        "ts_utc": utc_now(),
        "signal_id": signal_id,
        "symbol": symbol,
        "direction": direction,
        "ticket": pos_id,
        "entry": entry,
        "sl": sl,
        "sl_points": pts,
        "volume": VOLUME,
        "magic": MAGIC,
        "retcode": result.retcode,
        "exit": exit_px,
        "close_path": close_path if exit_px is not None else "unknown",
        "flat": exit_px is not None,
        "preclosed": True,
    }
    log(fill)
    return fill


def open_one(job: dict) -> dict | None:
    symbol, direction = job["symbol"], job["direction"]
    if not mt5.symbol_select(symbol, True):
        log({"event": "reject", "signal_id": job["signal_id"], "symbol": symbol, "text": "symbol_select failed"})
        return None
    info = mt5.symbol_info(symbol)
    tick = mt5.symbol_info_tick(symbol)
    if info is None or tick is None:
        log({"event": "reject", "signal_id": job["signal_id"], "symbol": symbol, "text": "no quote"})
        return None
    point, digits = info.point, info.digits
    order_type = mt5.ORDER_TYPE_BUY if direction == "BUY" else mt5.ORDER_TYPE_SELL
    price = tick.ask if direction == "BUY" else tick.bid
    pts = sl_points(symbol, info, tick)
    sl = sl_price(direction, price, pts, point, digits)
    filling = mt5.ORDER_FILLING_IOC if (info.filling_mode & 2) else mt5.ORDER_FILLING_FOK
    before = {p.ticket for p in (mt5.positions_get(symbol=symbol) or [])}
    result = mt5.order_send(
        {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": VOLUME,
            "type": order_type,
            "price": price,
            "sl": sl,
            "tp": 0.0,
            "deviation": 30,
            "magic": MAGIC,
            "comment": COMMENT,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": filling,
        }
    )
    if result is None:
        log({"event": "reject", "signal_id": job["signal_id"], "symbol": symbol, "text": str(mt5.last_error())})
        return None
    if result.retcode not in (mt5.TRADE_RETCODE_DONE, mt5.TRADE_RETCODE_DONE_PARTIAL):
        log(
            {
                "event": "reject",
                "signal_id": job["signal_id"],
                "symbol": symbol,
                "direction": direction,
                "retcode": result.retcode,
                "text": result.comment,
                "sl": sl,
                "sl_points": pts,
            }
        )
        return None
    time.sleep(0.4)
    pos = None
    for p in mt5.positions_get(symbol=symbol) or []:
        if p.ticket not in before and p.magic == MAGIC and "L4n" in (p.comment or ""):
            pos = p
            break
    if pos is None:
        for p in mt5.positions_get(symbol=symbol) or []:
            if p.magic == MAGIC and p.ticket not in before:
                pos = p
                break
    if pos is None:
        recovered = fill_from_history(symbol, direction, job["signal_id"], pts, sl, result)
        if recovered:
            return recovered
        log({"event": "reject", "signal_id": job["signal_id"], "symbol": symbol, "text": "filled but not found"})
        return None
    if not pos.sl and sl:
        mt5.order_send({"action": mt5.TRADE_ACTION_SLTP, "symbol": symbol, "position": pos.ticket, "sl": sl, "tp": 0.0})
        time.sleep(0.2)
        pos2 = mt5.positions_get(ticket=pos.ticket)
        if pos2:
            pos = pos2[0]
    fill = {
        "event": "fill",
        "ts_utc": utc_now(),
        "signal_id": job["signal_id"],
        "symbol": symbol,
        "direction": direction,
        "ticket": pos.ticket,
        "entry": pos.price_open,
        "sl": pos.sl or sl,
        "sl_points": pts,
        "volume": pos.volume,
        "magic": pos.magic,
        "retcode": result.retcode,
    }
    log(fill)
    return fill


def reconcile_exit(ticket: int) -> tuple[float | None, str]:
    from_dt = datetime.now(timezone.utc) - timedelta(hours=3)
    to_dt = datetime.now(timezone.utc) + timedelta(minutes=10)
    deals = mt5.history_deals_get(from_dt, to_dt) or []
    for d in deals:
        if d.position_id == ticket and d.entry == mt5.DEAL_ENTRY_OUT:
            path = "stop" if d.reason == mt5.DEAL_REASON_SL else "five_minute"
            if d.reason not in (mt5.DEAL_REASON_SL, mt5.DEAL_REASON_EXPERT, mt5.DEAL_REASON_CLIENT):
                path = "other"
            return float(d.price), path
    return None, "unknown"


def close_one(fill: dict) -> dict:
    if fill.get("preclosed"):
        entry, direction = fill["entry"], fill["direction"]
        info = mt5.symbol_info(fill["symbol"])
        point = info.point if info else 1e-5
        exit_px = fill.get("exit")
        close_path = fill.get("close_path") or "unknown"
        if exit_px is None:
            exit_px, close_path = reconcile_exit(fill["ticket"])
        net = None
        if exit_px is not None:
            net = (exit_px - entry) / point if direction == "BUY" else (entry - exit_px) / point
        rec = {
            "event": "close",
            "ts_utc": utc_now(),
            "signal_id": fill["signal_id"],
            "symbol": fill["symbol"],
            "direction": direction,
            "ticket": fill["ticket"],
            "entry": entry,
            "sl": fill["sl"],
            "exit": exit_px,
            "net_points": round(net, 1) if net is not None else None,
            "close_path": close_path if exit_px is not None else "unknown",
            "flat": True,
        }
        log(rec)
        return rec

    ticket, symbol, direction, entry = fill["ticket"], fill["symbol"], fill["direction"], fill["entry"]
    info = mt5.symbol_info(symbol)
    point = info.point if info else 1e-5
    still = next((p for p in (mt5.positions_get() or []) if p.ticket == ticket), None)
    if still is None:
        exit_px, close_path = reconcile_exit(ticket)
        net = None
        if exit_px is not None:
            net = (exit_px - entry) / point if direction == "BUY" else (entry - exit_px) / point
        rec = {
            "event": "close",
            "ts_utc": utc_now(),
            "signal_id": fill["signal_id"],
            "symbol": symbol,
            "direction": direction,
            "ticket": ticket,
            "entry": entry,
            "sl": fill["sl"],
            "exit": exit_px,
            "net_points": round(net, 1) if net is not None else None,
            "close_path": close_path if exit_px is not None else "unknown",
            "flat": True,
        }
        log(rec)
        return rec
    tick = mt5.symbol_info_tick(symbol)
    price = tick.bid if direction == "BUY" else tick.ask
    close_type = mt5.ORDER_TYPE_SELL if direction == "BUY" else mt5.ORDER_TYPE_BUY
    filling = mt5.ORDER_FILLING_IOC if (info.filling_mode & 2) else mt5.ORDER_FILLING_FOK
    req = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": still.volume,
        "type": close_type,
        "position": ticket,
        "price": price,
        "deviation": 30,
        "magic": MAGIC,
        "comment": "L4n close",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": filling,
    }
    result = mt5.order_send(req)
    ok = result is not None and result.retcode in (mt5.TRADE_RETCODE_DONE, mt5.TRADE_RETCODE_DONE_PARTIAL)
    if not ok:
        log(
            {
                "event": "close_fail",
                "ticket": ticket,
                "retcode": getattr(result, "retcode", None),
                "text": getattr(result, "comment", str(mt5.last_error())),
            }
        )
    still_after = any(p.ticket == ticket for p in (mt5.positions_get() or []))
    exit_px = float(result.price) if result and getattr(result, "price", None) else None
    close_path = "five_minute"
    if exit_px is None or not ok:
        hx, hpath = reconcile_exit(ticket)
        if hx is not None:
            exit_px = hx
            close_path = hpath if hpath in ("stop", "five_minute") else "five_minute"
        elif exit_px is None:
            exit_px = float(price)
    if still_after:
        close_path = "unknown"
    net = (exit_px - entry) / point if direction == "BUY" else (entry - exit_px) / point
    rec = {
        "event": "close",
        "ts_utc": utc_now(),
        "signal_id": fill["signal_id"],
        "symbol": symbol,
        "direction": direction,
        "ticket": ticket,
        "entry": entry,
        "sl": fill["sl"],
        "exit": exit_px,
        "net_points": round(net, 1),
        "close_path": close_path if not still_after else "unknown",
        "flat": not still_after,
    }
    log(rec)
    return rec


def finalize(signals, fills, results, cycle_id):
    res_by = {r["signal_id"]: r for r in results}
    bits = []
    for sig in signals:
        sid = sig["signal_id"]
        r = res_by.get(sid)
        if r is None:
            append_jsonl(
                FORCED,
                {
                    "record_type": "outcome",
                    "signal_id": sid,
                    "scored_utc": utc_now(),
                    "outcome_status": "REJECTED_OR_NO_FILL",
                    "commission_status": "NOT_INCLUDED",
                    "outcome_reason": "No fill / reject.",
                    "locked_reason_unchanged": True,
                    "flat": True,
                    "close_path": "reject",
                },
            )
            bits.append(f"{sig['symbol']} REJECT")
            continue
        exit_px, net = r.get("exit"), r.get("net_points")
        if exit_px is None:
            hx, hpath = reconcile_exit(r["ticket"])
            if hx is not None:
                info = mt5.symbol_info(r["symbol"])
                point = info.point if info else 1e-5
                exit_px = hx
                r["exit"] = hx
                r["close_path"] = hpath if hpath in ("stop", "five_minute") else r.get("close_path")
                net = round((hx - r["entry"]) / point if r["direction"] == "BUY" else (r["entry"] - hx) / point, 1)
                r["net_points"] = net
        d = r["direction"]
        status = "PROFITABLE" if (net is not None and net > 0) else "NOT_PROFITABLE"
        net_price = (exit_px - r["entry"]) if (exit_px is not None and d == "BUY") else (
            (r["entry"] - exit_px) if exit_px is not None else None
        )
        append_jsonl(
            FORCED,
            {
                "record_type": "outcome",
                "signal_id": sid,
                "scored_utc": utc_now(),
                "scored_broker": (datetime.now(timezone.utc) + timedelta(hours=3)).strftime("%Y.%m.%d %H:%M:%S"),
                "exit_bid": exit_px if d == "BUY" else None,
                "exit_ask": exit_px if d == "SELL" else None,
                "exit_executable_price": exit_px,
                "net_price_after_spread": net_price,
                "net_points_after_spread": net,
                "outcome_status": status,
                "commission_status": "NOT_INCLUDED",
                "outcome_reason": (
                    f"Demo ticket {r['ticket']}: entry {r['entry']}, SL {r['sl']}, "
                    f"exit {exit_px} via {r.get('close_path')}. Net {net} points."
                ),
                "post_outcome_review": (
                    "Batch13 Level4 L4n; MCP blocked; Python MT5; "
                    "SL majors max(80,stops+spread) / JPY+CNH max(250,stops+spread); no SEK."
                ),
                "locked_reason_unchanged": True,
                "demo_ticket": r["ticket"],
                "magic": MAGIC,
                "volume": VOLUME,
                "stop": r["sl"],
                "close_path": r.get("close_path"),
                "flat": r.get("flat", True),
            },
        )
        bits.append(f"{r['symbol']} {d} {r.get('close_path')} net={net}")

    append_jsonl(
        ATLAS,
        {
            "ts_utc": utc_now(),
            "review": f"Level4 batch13 cycle {cycle_id}",
            "doctrine": "Locked reasons unchanged.",
            "common_sense": "; ".join(bits),
            "hypotheses": "H-20260922-001/002/003 PROPOSED; H-002 not activated. 20260922T090923Z UNRESOLVED.",
        },
    )
    append_jsonl(DECISION, {"ts_utc": utc_now(), "cycle_id": cycle_id, "event": "batch13_complete", "results": results})

    lines = [
        f"# Level 4 demo handoff — {utc_now()}",
        "",
        "Account: MetaQuotes-Demo. Foreign Client CADCHF not touched.",
        "",
        f"## Batch13 (cycle {cycle_id}) comment L4n",
        "MCP blocked. Python MT5. Magic 771249, 0.01.",
        "SL: majors max(80, stops+spread); JPY/CNH max(250, stops+spread). No SEK.",
        "",
        "| Symbol | Dir | Ticket | Entry | Stop | Exit | Net pts | Close path | Flat |",
        "|---|---|---:|---:|---:|---:|---:|---|---|",
    ]
    for r in results:
        lines.append(
            f"| {r['symbol']} | {r['direction']} | {r['ticket']} | {r['entry']} | {r['sl']} | "
            f"{r.get('exit')} | {r.get('net_points')} | {r.get('close_path')} | "
            f"{'yes' if r.get('flat') else 'no'} |"
        )
    for sig in signals:
        if sig["signal_id"] not in res_by:
            lines.append(f"| {sig['symbol']} | {sig['research_direction']} | REJECT | - | - | - | - | reject | yes |")
    lines += [
        "",
        "## Next wake",
        "1. Continue until STOP_LEVEL_4_DEMO_AUTONOMY / STOP_FORCED_SIGNAL_LOOP.",
        "2. Do not activate H-20260922-002. Do not rescore 20260922T090923Z.",
        "",
    ]
    HANDOFF.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    if block_if_mentor_says_stop(SCRIPT):
        return 0

    if not mt5.initialize():
        log({"event": "init_fail", "error": str(mt5.last_error())})
        return 1
    ai = mt5.account_info()
    if ai is None or ai.trade_mode != mt5.ACCOUNT_TRADE_MODE_DEMO:
        log({"event": "refuse_not_demo"})
        mt5.shutdown()
        return 2

    ours = [p for p in (mt5.positions_get() or []) if p.magic == MAGIC]
    if ours:
        log(
            {
                "event": "abort_existing_771249",
                "positions": [{"ticket": p.ticket, "symbol": p.symbol, "comment": p.comment} for p in ours],
            }
        )
        mt5.shutdown()
        return 3

    picks = pick_five()
    log_plan_vs_board(
        SCRIPT,
        [{"symbol": p["symbol"], "side": p["direction"]} for p in picks],
    )
    if len(picks) < 5:
        log(
            {
                "event": "abort_not_enough_signals",
                "n": len(picks),
                "picks": [{"s": p["symbol"], "d": p["direction"]} for p in picks],
            }
        )
        mt5.shutdown()
        return 4

    ts = datetime.now(timezone.utc)
    cycle_id = ts.strftime("%Y%m%dT%H%M%SZ")
    signals = build_signals(picks, cycle_id, ts)
    (EXP / "batch13_signals.json").write_text(json.dumps(signals, indent=2), encoding="utf-8")
    for sig in signals:
        append_jsonl(FORCED, sig)
    jobs = [{"signal_id": s["signal_id"], "symbol": s["symbol"], "direction": s["research_direction"]} for s in signals]
    (EXP / "batch13_jobs.json").write_text(json.dumps(jobs, indent=2), encoding="utf-8")
    log(
        {
            "event": "signals_locked",
            "ts_utc": utc_now(),
            "cycle_id": cycle_id,
            "symbols": [j["symbol"] + " " + j["direction"] for j in jobs],
            "sl_tiers": {p["symbol"]: p.get("sl_tier") for p in picks},
        }
    )

    if any(p.magic == MAGIC for p in (mt5.positions_get() or [])):
        log({"event": "abort_pre_open"})
        mt5.shutdown()
        return 5

    fills = []
    for job in jobs:
        fill = open_one(job)
        if fill:
            fills.append(fill)

    open_fills = [f for f in fills if not f.get("preclosed")]
    log({"event": "hold_start", "ts_utc": utc_now(), "seconds": HOLD_SEC, "n_fills": len(fills), "n_open": len(open_fills)})
    if open_fills:
        time.sleep(HOLD_SEC)
    log({"event": "hold_end", "ts_utc": utc_now()})

    results = [close_one(f) for f in fills]
    for r in results:
        if r.get("exit") is None:
            hx, hpath = reconcile_exit(r["ticket"])
            if hx is not None:
                info = mt5.symbol_info(r["symbol"])
                point = info.point if info else 1e-5
                r["exit"] = hx
                r["close_path"] = hpath if hpath in ("stop", "five_minute") else "five_minute"
                r["net_points"] = round(
                    (hx - r["entry"]) / point if r["direction"] == "BUY" else (r["entry"] - hx) / point, 1
                )
                r["flat"] = True
                log({"event": "reconcile_fix", **r})

    left = [
        {"ticket": p.ticket, "symbol": p.symbol, "magic": p.magic, "comment": p.comment}
        for p in (mt5.positions_get() or [])
    ]
    ours_left = [p for p in left if p["magic"] == MAGIC and "L4n" in (p.get("comment") or "")]
    log({"event": "batch_done", "ts_utc": utc_now(), "left": left, "our_L4n_left": ours_left})
    (EXP / "batch13_results.json").write_text(
        json.dumps({"cycle_id": cycle_id, "fills": fills, "results": results, "left": left}, indent=2),
        encoding="utf-8",
    )
    finalize(signals, fills, results, cycle_id)
    mt5.shutdown()
    return 0 if not ours_left else 6


if __name__ == "__main__":
    raise SystemExit(main())

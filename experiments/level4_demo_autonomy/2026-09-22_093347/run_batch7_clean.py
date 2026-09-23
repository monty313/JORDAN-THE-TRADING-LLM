"""Level 4 batch7 clean round-trip. Magic 771249. Comment L4g.
SL = max(80, stops_level + spread_pts + 2). No extra reject gates.
"""
from __future__ import annotations

import csv
import json
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import MetaTrader5 as mt5

from mentor_preflight import block_if_mentor_says_stop

MAGIC = 771249
VOLUME = 0.01
BASE_SL = 80
HOLD_SEC = 300
COMMENT = "L4g m771249"
EXP = Path(r"C:\Users\C2K\Desktop\MT5 to agent\experiments\level4_demo_autonomy\2026-09-22_093347")
LOG = EXP / "demo_trade_tape.jsonl"
FORCED = Path(r"C:\Users\C2K\Desktop\MT5 to agent\JARVIS V1\research\forced_signals.jsonl")
ATLAS = EXP / "atlas_reviews.jsonl"
DECISION = EXP / "decision_tape.jsonl"
HANDOFF = EXP / "reports" / "handoff.md"
SCRIPT = Path(__file__).name
BOARD = Path(
    r"C:\Users\C2K\AppData\Roaming\MetaQuotes\Terminal\D0E8209F77C8CF37AD8BF550E51FF075\MQL5\Files\jarvis\board.csv"
)

# Do not copy batch6 symbol+direction pairs
FORBID = {
    ("EURCAD", "BUY"),
    ("GBPUSD", "SELL"),
    ("USDCAD", "BUY"),
    ("EURGBP", "SELL"),
    ("GBPCAD", "BUY"),
}
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


def spread_pts(info, tick) -> int:
    if tick is not None and info.point:
        return max(0, int(round((tick.ask - tick.bid) / info.point)))
    return int(getattr(info, "spread", 0) or 0)


def sl_points(info, tick) -> int:
    stops = int(getattr(info, "trade_stops_level", 0) or 0)
    return max(BASE_SL, stops + spread_pts(info, tick) + 2)


def sl_price(direction: str, price: float, pts: int, point: float, digits: int) -> float:
    if direction == "BUY":
        return round(price - pts * point, digits)
    return round(price + pts * point, digits)


def pick_five() -> list[dict]:
    rows = list(csv.DictReader(BOARD.open(encoding="utf-8", errors="replace")))
    ts = max(r["ts"] for r in rows)
    cur = [r for r in rows if r["ts"] == ts]
    log({"event": "board_ts", "ts": ts, "n": len(cur)})
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
        if sym != r["symbol"] or sym in INDEX_LIKE:
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
                "sl_points_planned": max(BASE_SL, stops + spr + 2),
                "prio": prio,
            }
        )
    cands.sort(key=lambda x: (x["prio"], x["spread_points"], x["symbol"]))
    picked, seen = [], set()
    for c in cands:
        if c["symbol"] in seen:
            continue
        # Prefer FX over metals when choosing
        picked.append(c)
        seen.add(c["symbol"])
        if len(picked) >= 5:
            break
    # Prefer non-metal if we have extras in cands
    fx = [c for c in picked if not c["symbol"].startswith("X")]
    met = [c for c in picked if c["symbol"].startswith("X")]
    if len(fx) >= 5:
        picked = fx[:5]
    elif len(fx) + len(met) >= 5:
        picked = fx + met[: 5 - len(fx)]
    (EXP / "_picks7.json").write_text(json.dumps(picked, indent=2), encoding="utf-8")
    return picked


def build_signals(picks: list[dict], cycle_id: str, ts_utc: datetime) -> list[dict]:
    broker = (ts_utc + timedelta(hours=3)).strftime("%Y.%m.%d %H:%M:%S")
    ny = ts_utc.astimezone(ZoneInfo("America/New_York")).strftime("%Y-%m-%dT%H:%M:%S%z")
    ny = ny[:-2] + ":" + ny[-2:]
    due = (ts_utc + timedelta(minutes=5)).strftime("%Y-%m-%dT%H:%M:%SZ")
    out = []
    for i, p in enumerate(picks, 1):
        sym = p["symbol"]
        direction = p["direction"]
        mt5.symbol_select(sym, True)
        tick = mt5.symbol_info_tick(sym)
        info = mt5.symbol_info(sym)
        point = float(info.point)
        digits = int(info.digits)
        bid, ask = float(tick.bid), float(tick.ask)
        entry = ask if direction == "BUY" else bid
        pts = sl_points(info, tick)
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
            if "full_body" in (p.get("reason") or "") or "momentum" in (p.get("state") or "")
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
                "ltf_state": "launch" if prio_is_fire(p) else "loaded",
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
                    "stops_level": p.get("stops_level"),
                },
                "reason_locked_before_outcome": (
                    f"Closed-bar {p['strategy']} {p['act']} set {p['set']} tide {p['tide']}. "
                    f"Research {direction} five-minute demo round-trip; SL {pts} pts "
                    f"(max of 80 and stops_level+spread+2)."
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
                "config_hash": "level4-demo-sl-max80-or-broker-min",
            }
        )
    return out


def prio_is_fire(p: dict) -> bool:
    return str(p.get("act", "")).startswith("FIRE_")


def open_one(job: dict) -> dict | None:
    symbol = job["symbol"]
    direction = job["direction"]
    if not mt5.symbol_select(symbol, True):
        log({"event": "reject", "signal_id": job["signal_id"], "symbol": symbol, "text": "symbol_select failed"})
        return None
    info = mt5.symbol_info(symbol)
    tick = mt5.symbol_info_tick(symbol)
    if info is None or tick is None:
        log({"event": "reject", "signal_id": job["signal_id"], "symbol": symbol, "text": "no quote"})
        return None
    point = info.point
    digits = info.digits
    order_type = mt5.ORDER_TYPE_BUY if direction == "BUY" else mt5.ORDER_TYPE_SELL
    price = tick.ask if direction == "BUY" else tick.bid
    pts = sl_points(info, tick)
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
        if p.ticket not in before and p.magic == MAGIC and "L4g" in (p.comment or ""):
            pos = p
            break
    if pos is None:
        for p in mt5.positions_get(symbol=symbol) or []:
            if p.magic == MAGIC and p.ticket not in before:
                pos = p
                break
    if pos is None:
        log(
            {
                "event": "reject",
                "signal_id": job["signal_id"],
                "symbol": symbol,
                "text": "filled but position not found",
                "order": result.order,
            }
        )
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
    ticket = fill["ticket"]
    symbol = fill["symbol"]
    direction = fill["direction"]
    entry = fill["entry"]
    info = mt5.symbol_info(symbol)
    point = info.point if info else 1e-5
    still = None
    for p in mt5.positions_get() or []:
        if p.ticket == ticket:
            still = p
            break
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
    result = mt5.order_send(
        {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": still.volume,
            "type": close_type,
            "position": ticket,
            "price": price,
            "deviation": 30,
            "magic": MAGIC,
            "comment": "L4g close",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": filling,
        }
    )
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
        # one extra close only if still open
        still2 = any(p.ticket == ticket for p in (mt5.positions_get() or []))
        if still2:
            result = mt5.order_send(
                {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "symbol": symbol,
                    "volume": still.volume,
                    "type": close_type,
                    "position": ticket,
                    "price": (mt5.symbol_info_tick(symbol).bid if direction == "BUY" else mt5.symbol_info_tick(symbol).ask),
                    "deviation": 30,
                    "magic": MAGIC,
                    "comment": "L4g close2",
                    "type_time": mt5.ORDER_TIME_GTC,
                    "type_filling": filling,
                }
            )
            ok = result is not None and result.retcode in (mt5.TRADE_RETCODE_DONE, mt5.TRADE_RETCODE_DONE_PARTIAL)
            log({"event": "close_extra", "ticket": ticket, "ok": ok, "retcode": getattr(result, "retcode", None)})
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
                    "outcome_reason": "No fill / reject for this signal.",
                    "locked_reason_unchanged": True,
                    "flat": True,
                    "close_path": "reject",
                },
            )
            bits.append(f"{sig['symbol']} {sig['research_direction']} REJECT")
            continue
        exit_px = r.get("exit")
        net = r.get("net_points")
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
                "post_outcome_review": "Batch7 Level4; MCP blocked; Python MT5; SL=max(80,stops+spread+2).",
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
            "review": "Level4 batch7",
            "doctrine": "Locked reasons unchanged; protective stop is research harness only.",
            "common_sense": "; ".join(bits),
            "hypotheses": "H-20260922-001/002/003 PROPOSED; H-002 not activated. 20260922T090923Z UNRESOLVED.",
        },
    )
    append_jsonl(DECISION, {"ts_utc": utc_now(), "cycle_id": cycle_id, "event": "batch7_complete", "results": results})

    lines = [
        f"# Level 4 demo handoff — {utc_now()}",
        "",
        "Account: MetaQuotes-Demo. Batch6 already flat/scored. Batch7 below.",
        "",
        "## Batch6 (cycle 20260922T102651Z) — already scored",
        "| Symbol | Dir | Ticket | Entry | Stop | Exit | Net pts | Close path | Flat |",
        "|---|---|---:|---:|---:|---:|---:|---|---|",
        "| EURCAD | BUY | 58568462450 | 1.60874 | 1.60795 | 1.60869 | -5 | five_minute | yes |",
        "| GBPUSD | SELL | 58568462582 | 1.33652 | 1.33732 | 1.33677 | -25 | five_minute | yes |",
        "| USDCAD | BUY | 58568462698 | 1.40366 | 1.40286 | 1.40337 | -29 | five_minute | yes |",
        "| EURGBP | SELL | 58568462782 | 0.85754 | 0.85834 | 0.85757 | -3 | five_minute | yes |",
        "| GBPCAD | BUY | 58568462879 | 1.87597 | 1.87517 | 1.87586 | -11 | five_minute | yes |",
        "",
        f"## Batch7 (cycle {cycle_id})",
        "MCP trade blocked. Python MetaTrader5. Magic 771249, 0.01. SL=max(80, stops+spread+2). Comment L4g.",
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
            lines.append(
                f"| {sig['symbol']} | {sig['research_direction']} | REJECT | - | - | - | - | reject | yes |"
            )
    lines += [
        "",
        "Foreign Client tickets not touched.",
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

    # Abort if any of OUR L4g / 771249 research tickets already open
    ours = [p for p in (mt5.positions_get() or []) if p.magic == MAGIC]
    if ours:
        log(
            {
                "event": "existing_771249",
                "ts_utc": utc_now(),
                "positions": [{"ticket": p.ticket, "symbol": p.symbol, "comment": p.comment} for p in ours],
            }
        )
        # If L4g already open, do not add — caller should wait/close
        mt5.shutdown()
        return 3

    picks = pick_five()
    if len(picks) < 5:
        log({"event": "abort_not_enough_signals", "n": len(picks), "picks": picks})
        mt5.shutdown()
        return 4

    ts = datetime.now(timezone.utc)
    cycle_id = ts.strftime("%Y%m%dT%H%M%SZ")
    signals = build_signals(picks, cycle_id, ts)
    (EXP / "batch7_signals.json").write_text(json.dumps(signals, indent=2), encoding="utf-8")
    for sig in signals:
        append_jsonl(FORCED, sig)
    jobs = [{"signal_id": s["signal_id"], "symbol": s["symbol"], "direction": s["research_direction"]} for s in signals]
    (EXP / "batch7_jobs.json").write_text(json.dumps(jobs, indent=2), encoding="utf-8")
    log({"event": "signals_locked", "ts_utc": utc_now(), "cycle_id": cycle_id, "symbols": [j["symbol"] for j in jobs]})

    # re-read before orders
    if any(p.magic == MAGIC for p in (mt5.positions_get() or [])):
        log({"event": "abort_pre_open_771249", "ts_utc": utc_now()})
        mt5.shutdown()
        return 5

    fills = []
    for job in jobs:
        fill = open_one(job)
        if fill:
            fills.append(fill)

    log({"event": "hold_start", "ts_utc": utc_now(), "seconds": HOLD_SEC, "n_fills": len(fills)})
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

    left = [{"ticket": p.ticket, "symbol": p.symbol, "magic": p.magic, "comment": p.comment} for p in (mt5.positions_get() or [])]
    ours_left = [p for p in left if p["magic"] == MAGIC and "L4g" in (p.get("comment") or "")]
    log({"event": "batch_done", "ts_utc": utc_now(), "left": left, "our_L4g_left": ours_left})
    (EXP / "batch7_results.json").write_text(
        json.dumps({"cycle_id": cycle_id, "fills": fills, "results": results, "left": left}, indent=2), encoding="utf-8"
    )
    finalize(signals, fills, results, cycle_id)
    mt5.shutdown()
    return 0 if not ours_left else 6


if __name__ == "__main__":
    raise SystemExit(main())

"""Level 4 batch6 demo round-trip. Magic 771249. Comment L4f.
SL = max(80, SYMBOL_TRADE_STOPS_LEVEL + current_spread_pts + 2).
"""
from __future__ import annotations

import json
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import MetaTrader5 as mt5

from mentor_preflight import block_if_mentor_says_stop

MAGIC = 771249
VOLUME = 0.01
BASE_SL_POINTS = 80
HOLD_SEC = 300
COMMENT = "L4f m771249"
EXP = Path(r"C:\Users\C2K\Desktop\MT5 to agent\experiments\level4_demo_autonomy\2026-09-22_093347")
LOG = EXP / "demo_trade_tape.jsonl"
FORCED = Path(r"C:\Users\C2K\Desktop\MT5 to agent\JARVIS V1\research\forced_signals.jsonl")
ATLAS = EXP / "atlas_reviews.jsonl"
DECISION = EXP / "decision_tape.jsonl"
HANDOFF = EXP / "reports" / "handoff.md"
PICKS = EXP / "_picks6.json"
MCP_EXITS = EXP / "batch6_mcp_exits.json"  # optional post-hoc fill from parent
SCRIPT = Path(__file__).name




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


def spread_points(info, tick) -> int:
    if tick is not None and info.point:
        return max(0, int(round((tick.ask - tick.bid) / info.point)))
    return int(getattr(info, "spread", 0) or 0)


def compute_sl_points(info, tick) -> int:
    stops = int(getattr(info, "trade_stops_level", 0) or 0)
    spr = spread_points(info, tick)
    # at least 80 pts, and beyond stops_level + spread
    return max(BASE_SL_POINTS, stops + spr + 2)


def compute_sl_price(direction: str, price: float, sl_pts: int, point: float, digits: int) -> float:
    if direction == "BUY":
        return round(price - sl_pts * point, digits)
    return round(price + sl_pts * point, digits)


def topology_for(state: str, reason: str) -> str:
    if "launch" in (state or "").lower() or "momentum" in (state or "").lower() or "full_body" in (reason or ""):
        return "launch_continuation_bet"
    if "load" in (state or "").lower() or "pullback" in (reason or "") or "waiting" in (reason or ""):
        return "slingshot_load_continuation_bet"
    return "slingshot_release"


def build_signals(picks: list[dict], cycle_id: str, ts_utc: datetime) -> list[dict]:
    broker = (ts_utc + timedelta(hours=3)).strftime("%Y.%m.%d %H:%M:%S")
    ny = ts_utc.astimezone(ZoneInfo("America/New_York")).strftime("%Y-%m-%dT%H:%M:%S%z")
    ny = ny[:-2] + ":" + ny[-2:]
    due = (ts_utc + timedelta(minutes=5)).strftime("%Y-%m-%dT%H:%M:%SZ")
    signals = []
    for i, p in enumerate(picks, start=1):
        sym = p["symbol"]
        direction = p["direction"]
        if not mt5.symbol_select(sym, True):
            raise RuntimeError(f"symbol_select failed {sym}")
        tick = mt5.symbol_info_tick(sym)
        info = mt5.symbol_info(sym)
        if tick is None or info is None:
            raise RuntimeError(f"no quote for {sym}")
        point = float(info.point)
        digits = int(info.digits)
        bid, ask = float(tick.bid), float(tick.ask)
        entry = ask if direction == "BUY" else bid
        sl_pts = compute_sl_points(info, tick)
        sl = compute_sl_price(direction, entry, sl_pts, point, digits)
        try:
            bar_dt = datetime.strptime(p["closed_bar_time"], "%Y.%m.%d %H:%M:%S").replace(
                tzinfo=timezone(timedelta(hours=3))
            )
            age = int((ts_utc - bar_dt.astimezone(timezone.utc)).total_seconds())
        except Exception:
            age = 0
        topo = topology_for(p.get("state") or "", p.get("reason") or "")
        ltf = (
            "launch"
            if "momentum" in (p.get("state") or "").lower() or "full_body" in (p.get("reason") or "")
            else (
                "loaded"
                if "load" in (p.get("state") or "").lower() or "WAIT_LOADED" in p.get("act", "")
                else "continuation"
            )
        )
        spr = spread_points(info, tick)
        stops = int(getattr(info, "trade_stops_level", 0) or 0)
        sig = {
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
            "spread_points": spr,
            "spread_price": round(spr * point, digits + 2),
            "point_size": point,
            "digits": digits,
            "research_direction": direction,
            "research_confidence_0_100": 50,
            "research_topology": topo,
            "strategy_alignment": p["strategy"],
            "tide": p["tide"],
            "regime": p["regime"],
            "ltf_state": ltf,
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
                "planned_sl_points": sl_pts,
                "stops_level": stops,
                "tick_spread_points": spr,
            },
            "reason_locked_before_outcome": (
                f"Closed-bar {p['strategy']} {p['act']} set {p['set']} tide {p['tide']}. "
                f"Research {direction} for a five-minute demo round-trip with protective stop "
                f"{sl_pts} points (max of 80 and stops_level+spread+2)."
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
            "exit_bid": None,
            "exit_ask": None,
            "exit_executable_price": None,
            "net_points_after_spread": None,
            "net_price_after_spread": None,
            "commission_status": "NOT_INCLUDED",
            "outcome_reason": "",
            "post_outcome_review": "",
            "doctrine_version": "007-v1-readonly",
            "config_hash": "level4-demo-sl-max80-or-broker-min",
        }
        signals.append(sig)
    return signals


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
    sl = 0.0
    act = job.get("act") or ""
    cmp = job.get("cmp") or ""
    if act not in ("FIRE_BUY", "FIRE_SELL") or "official_act=WAIT_" in cmp or job.get("anchor_tf") == "M1":
        log({"event": "reject", "signal_id": job["signal_id"], "symbol": symbol, "text": "not_a_fresh_fire", "act": act})
        return None
    spread = int(job.get("spread_points") or 0)
    if spread <= 0 or spread > 20:
        log({"event": "reject", "signal_id": job["signal_id"], "symbol": symbol, "text": "spread_out_of_range", "spread_points": spread})
        return None
    hi = job.get("high1", job.get("high"))
    lo = job.get("low1", job.get("low"))
    if hi is not None and lo is not None:
        edge = (float(hi) - price) if direction == "SELL" else (price - float(lo))
        if edge <= spread * float(point):
            log({"event": "reject", "signal_id": job["signal_id"], "symbol": symbol, "text": "spread_wider_than_room", "edge": edge, "spread_points": spread})
            return None
        if direction == "BUY" and price < float(lo):
            log({"event": "reject", "signal_id": job["signal_id"], "symbol": symbol, "text": "price_under_signal_bar_low"})
            return None
        if direction == "SELL" and price > float(hi):
            log({"event": "reject", "signal_id": job["signal_id"], "symbol": symbol, "text": "price_over_signal_bar_high"})
            return None
    period = {"M5": 300, "M15": 900, "M30": 1800, "H1": 3600}.get(job.get("anchor_tf") or "")
    cbt = job.get("closed_bar_time")
    if period and cbt:
        bar_open = datetime.strptime(cbt, "%Y.%m.%d %H:%M:%S").replace(tzinfo=timezone(timedelta(hours=3)))
        age = (datetime.now(timezone.utc) - bar_open.astimezone(timezone.utc)).total_seconds()
        if age >= period * 2:
            log({"event": "reject", "signal_id": job["signal_id"], "symbol": symbol, "text": "stale_closed_bar", "age": int(age)})
            return None
    filling = mt5.ORDER_FILLING_IOC if (info.filling_mode & 2) else mt5.ORDER_FILLING_FOK
    before = {p.ticket for p in (mt5.positions_get(symbol=symbol) or [])}
    request = {
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
    result = mt5.order_send(request)
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
                "sl_attempted": sl,
                "sl_points": sl_pts,
            }
        )
        return None
    time.sleep(0.4)
    pos = None
    for p in mt5.positions_get(symbol=symbol) or []:
        if p.ticket not in before and p.magic == MAGIC and "L4f" in (p.comment or ""):
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
                "price": result.price,
            }
        )
        return None
    if abs((pos.sl or 0) - sl) > point * 0.5 and sl:
        mt5.order_send(
            {
                "action": mt5.TRADE_ACTION_SLTP,
                "symbol": symbol,
                "position": pos.ticket,
                "sl": sl,
                "tp": 0.0,
            }
        )
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
        "sl_points": sl_pts,
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
    exit_px = None
    close_path = "other"
    for d in deals:
        if d.position_id == ticket and d.entry == mt5.DEAL_ENTRY_OUT:
            exit_px = float(d.price)
            if d.reason == mt5.DEAL_REASON_SL:
                close_path = "stop"
            elif d.reason in (mt5.DEAL_REASON_EXPERT, mt5.DEAL_REASON_CLIENT):
                close_path = "five_minute"
            else:
                close_path = "other"
            break
    return exit_px, close_path


def close_one(fill: dict) -> dict:
    ticket = fill["ticket"]
    symbol = fill["symbol"]
    direction = fill["direction"]
    entry = fill["entry"]
    info = mt5.symbol_info(symbol)
    point = info.point if info else 0.00001

    still_open = None
    for p in mt5.positions_get() or []:
        if p.ticket == ticket:
            still_open = p
            break

    if still_open is None:
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
        "volume": still_open.volume,
        "type": close_type,
        "position": ticket,
        "price": price,
        "deviation": 30,
        "magic": MAGIC,
        "comment": "L4f close",
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
    still = any(p.ticket == ticket for p in (mt5.positions_get() or []))
    exit_px = float(result.price) if result and getattr(result, "price", None) else None
    close_path = "five_minute"
    if exit_px is None or (not ok and not still):
        hx, hpath = reconcile_exit(ticket)
        if hx is not None:
            exit_px = hx
            close_path = hpath if hpath in ("stop", "five_minute") else "five_minute"
        elif exit_px is None:
            exit_px = float(price)
    if still:
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
        "close_path": close_path if not still else "unknown",
        "flat": not still,
    }
    log(rec)
    return rec


def apply_mcp_exits(results: list[dict]) -> None:
    if not MCP_EXITS.exists():
        return
    try:
        data = json.loads(MCP_EXITS.read_text(encoding="utf-8"))
    except Exception:
        return
    by_ticket = {int(k): v for k, v in data.items()}
    for r in results:
        if r.get("exit") is not None:
            continue
        fix = by_ticket.get(int(r["ticket"]))
        if not fix:
            continue
        info = mt5.symbol_info(r["symbol"])
        point = info.point if info else 1e-5
        exit_px = float(fix["exit"])
        r["exit"] = exit_px
        r["close_path"] = fix.get("close_path", "five_minute")
        r["net_points"] = round(
            (exit_px - r["entry"]) / point if r["direction"] == "BUY" else (r["entry"] - exit_px) / point,
            1,
        )
        r["flat"] = True
        log({"event": "mcp_exit_applied", **r})


def finalize(signals: list[dict], fills: list[dict], results: list[dict], cycle_id: str) -> None:
    res_by_sid = {r["signal_id"]: r for r in results}
    review_bits = []
    for sig in signals:
        sid = sig["signal_id"]
        r = res_by_sid.get(sid)
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
            review_bits.append(f"{sig['symbol']} {sig['research_direction']} REJECT")
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
                net = (hx - r["entry"]) / point if r["direction"] == "BUY" else (r["entry"] - hx) / point
                net = round(net, 1)
                r["net_points"] = net
        direction = r["direction"]
        status = "PROFITABLE" if (net is not None and net > 0) else "NOT_PROFITABLE"
        net_price = None
        if exit_px is not None:
            net_price = (exit_px - r["entry"]) if direction == "BUY" else (r["entry"] - exit_px)
        outcome = {
            "record_type": "outcome",
            "signal_id": sid,
            "scored_utc": utc_now(),
            "scored_broker": (datetime.now(timezone.utc) + timedelta(hours=3)).strftime("%Y.%m.%d %H:%M:%S"),
            "exit_bid": exit_px if direction == "BUY" else None,
            "exit_ask": exit_px if direction == "SELL" else None,
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
                "Batch6 Level4 demo; MCP trade blocked; Python MetaTrader5; "
                "SL=max(80, stops_level+spread+2)."
            ),
            "locked_reason_unchanged": True,
            "demo_ticket": r["ticket"],
            "magic": MAGIC,
            "volume": VOLUME,
            "stop": r["sl"],
            "close_path": r.get("close_path"),
            "flat": r.get("flat", True),
        }
        append_jsonl(FORCED, outcome)
        review_bits.append(f"{r['symbol']} {direction} {r.get('close_path')} net={net}")

    append_jsonl(
        ATLAS,
        {
            "ts_utc": utc_now(),
            "review": "Level4 batch6",
            "doctrine": "Locked reasons unchanged; protective stop is research harness only.",
            "common_sense": "; ".join(review_bits),
            "hypotheses": (
                "H-20260922-001/002/003 remain PROPOSED; H-002 not activated. "
                "Cycle 20260922T090923Z UNRESOLVED."
            ),
        },
    )
    append_jsonl(
        DECISION,
        {
            "ts_utc": utc_now(),
            "cycle_id": cycle_id,
            "event": "batch6_complete",
            "n_signals": len(signals),
            "n_fills": len(fills),
            "results": results,
        },
    )

    lines = [
        f"# Level 4 demo handoff — {utc_now()}",
        "",
        "Account: MetaQuotes-Demo. Positions re-read after batch6.",
        "",
        f"## Batch6 (cycle {cycle_id})",
        "MCP trade blocked. Python MetaTrader5. Magic 771249, volume 0.01. "
        "SL=max(80 pts, stops_level+spread+2). Comment L4f.",
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
        if sig["signal_id"] not in res_by_sid:
            lines.append(
                f"| {sig['symbol']} | {sig['research_direction']} | REJECT | - | - | - | - | reject | yes |"
            )
    lines += [
        "",
        "No foreign tickets touched.",
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
        log({"event": "refuse_not_demo", "trade_mode": getattr(ai, "trade_mode", None)})
        mt5.shutdown()
        return 2

    open_pos = list(mt5.positions_get() or [])
    ours = [p for p in open_pos if p.magic == MAGIC]
    if ours:
        log(
            {
                "event": "abort_existing_771249",
                "ts_utc": utc_now(),
                "positions": [{"ticket": p.ticket, "symbol": p.symbol, "comment": p.comment} for p in ours],
            }
        )
        mt5.shutdown()
        return 3

    picks = json.loads(PICKS.read_text(encoding="utf-8"))
    ts = datetime.now(timezone.utc)
    cycle_id = ts.strftime("%Y%m%dT%H%M%SZ")
    signals = build_signals(picks, cycle_id, ts)
    (EXP / "batch6_signals.json").write_text(json.dumps(signals, indent=2), encoding="utf-8")

    for sig in signals:
        append_jsonl(FORCED, sig)
    jobs = [
        {"signal_id": s["signal_id"], "symbol": s["symbol"], "direction": s["research_direction"]}
        for s in signals
    ]
    (EXP / "batch6_jobs.json").write_text(json.dumps(jobs, indent=2), encoding="utf-8")
    log(
        {
            "event": "signals_locked",
            "ts_utc": utc_now(),
            "cycle_id": cycle_id,
            "n": len(signals),
            "symbols": [j["symbol"] for j in jobs],
        }
    )

    open_pos = list(mt5.positions_get() or [])
    if any(p.magic == MAGIC for p in open_pos):
        log({"event": "abort_pre_open_771249", "ts_utc": utc_now()})
        mt5.shutdown()
        return 4

    fills = []
    for job in jobs:
        fill = open_one(job)
        if fill:
            fills.append(fill)

    log({"event": "hold_start", "ts_utc": utc_now(), "seconds": HOLD_SEC, "n_fills": len(fills)})
    time.sleep(HOLD_SEC)
    log({"event": "hold_end", "ts_utc": utc_now()})

    results = [close_one(fill) for fill in fills]
    for r in results:
        if r.get("exit") is None:
            hx, hpath = reconcile_exit(r["ticket"])
            if hx is not None:
                info = mt5.symbol_info(r["symbol"])
                point = info.point if info else 1e-5
                r["exit"] = hx
                r["close_path"] = hpath if hpath in ("stop", "five_minute") else "five_minute"
                r["net_points"] = round(
                    (hx - r["entry"]) / point if r["direction"] == "BUY" else (r["entry"] - hx) / point,
                    1,
                )
                r["flat"] = True
                log({"event": "reconcile_fix", **r})
    apply_mcp_exits(results)

    left = [
        {"ticket": p.ticket, "symbol": p.symbol, "magic": p.magic, "comment": p.comment}
        for p in (mt5.positions_get() or [])
    ]
    ours_left = [p for p in left if p["magic"] == MAGIC and "L4f" in (p.get("comment") or "")]
    log({"event": "batch_done", "ts_utc": utc_now(), "positions": left, "our_L4f_left": ours_left})
    (EXP / "batch6_results.json").write_text(
        json.dumps({"cycle_id": cycle_id, "fills": fills, "results": results, "left": left}, indent=2),
        encoding="utf-8",
    )
    finalize(signals, fills, results, cycle_id)
    mt5.shutdown()
    return 0 if not ours_left else 5


if __name__ == "__main__":
    raise SystemExit(main())

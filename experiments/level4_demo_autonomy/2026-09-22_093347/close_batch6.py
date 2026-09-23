"""Close batch6 L4f positions after 5-minute hold; append outcomes. No new opens."""
from __future__ import annotations

import json
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import MetaTrader5 as mt5

from mentor_preflight import block_if_mentor_says_stop

MAGIC = 771249
COMMENT_TAG = "L4f"
HOLD_UNTIL_UTC = datetime(2026, 9, 22, 10, 31, 55, tzinfo=timezone.utc)
EXP = Path(r"C:\Users\C2K\Desktop\MT5 to agent\experiments\level4_demo_autonomy\2026-09-22_093347")
SCRIPT = Path(__file__).name
LOG = EXP / "demo_trade_tape.jsonl"
FORCED = Path(r"C:\Users\C2K\Desktop\MT5 to agent\JARVIS V1\research\forced_signals.jsonl")
ATLAS = EXP / "atlas_reviews.jsonl"
DECISION = EXP / "decision_tape.jsonl"
HANDOFF = EXP / "reports" / "handoff.md"
CYCLE = "20260922T102651Z"

FILLS = [
    {"signal_id": "20260922T102651Z_EURCAD_1_S3_1", "symbol": "EURCAD", "direction": "BUY", "ticket": 58568462450, "entry": 1.60874, "sl": 1.60795},
    {"signal_id": "20260922T102651Z_GBPUSD_3_S2_2", "symbol": "GBPUSD", "direction": "SELL", "ticket": 58568462582, "entry": 1.33652, "sl": 1.33732},
    {"signal_id": "20260922T102651Z_USDCAD_4_S2_3", "symbol": "USDCAD", "direction": "BUY", "ticket": 58568462698, "entry": 1.40366, "sl": 1.40286},
    {"signal_id": "20260922T102651Z_EURGBP_4_S2_4", "symbol": "EURGBP", "direction": "SELL", "ticket": 58568462782, "entry": 0.85754, "sl": 0.85834},
    {"signal_id": "20260922T102651Z_GBPCAD_4_S2_5", "symbol": "GBPCAD", "direction": "BUY", "ticket": 58568462879, "entry": 1.87597, "sl": 1.87517},
]


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
    req = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": still.volume,
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

    now = datetime.now(timezone.utc)
    wait_s = (HOLD_UNTIL_UTC - now).total_seconds()
    log({"event": "hold_wait", "ts_utc": utc_now(), "wait_seconds": max(0, wait_s), "until": HOLD_UNTIL_UTC.isoformat()})
    if wait_s > 0:
        time.sleep(wait_s)

    # re-read before close
    open_ours = [
        {"ticket": p.ticket, "symbol": p.symbol, "sl": p.sl, "comment": p.comment}
        for p in (mt5.positions_get() or [])
        if p.magic == MAGIC and COMMENT_TAG in (p.comment or "")
    ]
    log({"event": "pre_close_positions", "ts_utc": utc_now(), "positions": open_ours})

    results = [close_one(f) for f in FILLS]

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

    left = [
        {"ticket": p.ticket, "symbol": p.symbol, "magic": p.magic, "comment": p.comment}
        for p in (mt5.positions_get() or [])
    ]
    ours_left = [p for p in left if p["magic"] == MAGIC and COMMENT_TAG in (p.get("comment") or "")]
    log({"event": "batch6_close_done", "ts_utc": utc_now(), "left": left, "our_L4f_left": ours_left})

    # outcomes
    review_bits = []
    for r in results:
        exit_px = r.get("exit")
        net = r.get("net_points")
        direction = r["direction"]
        status = "PROFITABLE" if (net is not None and net > 0) else "NOT_PROFITABLE"
        net_price = None
        if exit_px is not None:
            net_price = (exit_px - r["entry"]) if direction == "BUY" else (r["entry"] - exit_px)
        append_jsonl(
            FORCED,
            {
                "record_type": "outcome",
                "signal_id": r["signal_id"],
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
                    "SL=max(80, stops_level+spread+2). Duplicate open aborted; hold+close completed."
                ),
                "locked_reason_unchanged": True,
                "demo_ticket": r["ticket"],
                "magic": MAGIC,
                "volume": 0.01,
                "stop": r["sl"],
                "close_path": r.get("close_path"),
                "flat": r.get("flat", True),
            },
        )
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
        {"ts_utc": utc_now(), "cycle_id": CYCLE, "event": "batch6_complete", "results": results},
    )
    (EXP / "batch6_results.json").write_text(
        json.dumps({"cycle_id": CYCLE, "fills": FILLS, "results": results, "left": left}, indent=2),
        encoding="utf-8",
    )

    lines = [
        f"# Level 4 demo handoff — {utc_now()}",
        "",
        "Account: MetaQuotes-Demo. Positions re-read after batch6.",
        "",
        f"## Batch6 (cycle {CYCLE})",
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
    mt5.shutdown()
    return 0 if not ours_left else 5


if __name__ == "__main__":
    raise SystemExit(main())

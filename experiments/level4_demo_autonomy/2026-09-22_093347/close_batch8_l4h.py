"""Close L4h cycle 20260922T105113Z after hold; score; update handoff. No new opens."""
from __future__ import annotations

import json
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import MetaTrader5 as mt5

from mentor_preflight import block_if_mentor_says_stop

MAGIC = 771249
COMMENT_TAG = "L4h"
HOLD_UNTIL = datetime(2026, 9, 22, 10, 56, 20, tzinfo=timezone.utc)
EXP = Path(r"C:\Users\C2K\Desktop\MT5 to agent\experiments\level4_demo_autonomy\2026-09-22_093347")
SCRIPT = Path(__file__).name
LOG = EXP / "demo_trade_tape.jsonl"
FORCED = Path(r"C:\Users\C2K\Desktop\MT5 to agent\JARVIS V1\research\forced_signals.jsonl")
ATLAS = EXP / "atlas_reviews.jsonl"
DECISION = EXP / "decision_tape.jsonl"
HANDOFF = EXP / "reports" / "handoff.md"
CYCLE = "20260922T105113Z"

FILLS = [
    {"signal_id": "20260922T105113Z_AUDUSD_2_S1_1", "symbol": "AUDUSD", "direction": "BUY", "ticket": 58568878120, "entry": 0.71173, "sl": 0.71093},
    {"signal_id": "20260922T105113Z_EURAUD_3_S1_2", "symbol": "EURAUD", "direction": "BUY", "ticket": 58568878211, "entry": 1.61124, "sl": 1.61044},
    {"signal_id": "20260922T105113Z_EURJPY_3_S4_3", "symbol": "EURJPY", "direction": "SELL", "ticket": 58568878409, "entry": 180.03, "sl": 180.11},
    {"signal_id": "20260922T105113Z_USDJPY_1_S4_4", "symbol": "USDJPY", "direction": "SELL", "ticket": 58568878545, "entry": 156.986, "sl": 157.066},
    {"signal_id": "20260922T105113Z_AUDJPY_3_S4_5", "symbol": "AUDJPY", "direction": "SELL", "ticket": 58568878881, "entry": 111.727, "sl": 111.807},
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


def already_scored(sid: str) -> bool:
    for line in FORCED.read_text(encoding="utf-8-sig").splitlines():
        if not line.strip():
            continue
        o = json.loads(line)
        if o.get("record_type") == "outcome" and o.get("signal_id") == sid and o.get("exit_executable_price") is not None:
            return True
    return False


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
        "comment": "L4h close",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": filling,
    }
    result = mt5.order_send(req)
    ok = result is not None and result.retcode in (mt5.TRADE_RETCODE_DONE, mt5.TRADE_RETCODE_DONE_PARTIAL)
    if not ok:
        log({"event": "close_fail", "ticket": ticket, "retcode": getattr(result, "retcode", None), "text": getattr(result, "comment", str(mt5.last_error()))})
        if any(p.ticket == ticket for p in (mt5.positions_get() or [])):
            tick = mt5.symbol_info_tick(symbol)
            req["price"] = tick.bid if direction == "BUY" else tick.ask
            result = mt5.order_send(req)
            ok = result is not None and result.retcode in (mt5.TRADE_RETCODE_DONE, mt5.TRADE_RETCODE_DONE_PARTIAL)
            log({"event": "close_extra", "ticket": ticket, "ok": ok})

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

    wait = (HOLD_UNTIL - datetime.now(timezone.utc)).total_seconds()
    log({"event": "close_wait", "ts_utc": utc_now(), "wait_s": max(0, wait), "until": HOLD_UNTIL.isoformat()})
    if wait > 0:
        time.sleep(wait)

    ours = [
        {"ticket": p.ticket, "symbol": p.symbol, "comment": p.comment}
        for p in (mt5.positions_get() or [])
        if p.magic == MAGIC and COMMENT_TAG in (p.comment or "")
    ]
    log({"event": "pre_close", "ts_utc": utc_now(), "positions": ours})

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
                    (hx - r["entry"]) / point if r["direction"] == "BUY" else (r["entry"] - hx) / point, 1
                )
                r["flat"] = True
                log({"event": "reconcile_fix", **r})

    left = [{"ticket": p.ticket, "symbol": p.symbol, "magic": p.magic, "comment": p.comment} for p in (mt5.positions_get() or [])]
    ours_left = [p for p in left if p["magic"] == MAGIC and COMMENT_TAG in (p.get("comment") or "")]
    log({"event": "batch8_close_done", "ts_utc": utc_now(), "left": left, "our_L4h_left": ours_left})

    bits = []
    for r in results:
        if already_scored(r["signal_id"]):
            bits.append(f"{r['symbol']} already scored")
            continue
        exit_px, net, d = r.get("exit"), r.get("net_points"), r["direction"]
        status = "PROFITABLE" if (net is not None and net > 0) else "NOT_PROFITABLE"
        net_price = None
        if exit_px is not None:
            net_price = (exit_px - r["entry"]) if d == "BUY" else (r["entry"] - exit_px)
        append_jsonl(
            FORCED,
            {
                "record_type": "outcome",
                "signal_id": r["signal_id"],
                "scored_utc": utc_now(),
                "scored_broker": (datetime.now(timezone.utc) + timedelta(hours=3)).strftime("%Y.%m.%d %H:%M:%S"),
                "exit_bid": exit_px if d == "BUY" else None,
                "exit_ask": exit_px if d == "SELL" else None,
                "exit_executable_price": exit_px,
                "net_price_after_spread": net_price,
                "net_points_after_spread": net,
                "outcome_status": status,
                "commission_status": "NOT_INCLUDED",
                "outcome_reason": f"Demo ticket {r['ticket']}: entry {r['entry']}, SL {r['sl']}, exit {exit_px} via {r.get('close_path')}. Net {net} points.",
                "post_outcome_review": "Batch8 L4h; MCP blocked; Python MT5; closed after 5-minute hold.",
                "locked_reason_unchanged": True,
                "demo_ticket": r["ticket"],
                "magic": MAGIC,
                "volume": 0.01,
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
            "review": f"Level4 batch8 cycle {CYCLE}",
            "doctrine": "Locked reasons unchanged.",
            "common_sense": "; ".join(bits),
            "hypotheses": "H-20260922-001/002/003 PROPOSED; H-002 not activated. 20260922T090923Z UNRESOLVED.",
        },
    )
    append_jsonl(DECISION, {"ts_utc": utc_now(), "cycle_id": CYCLE, "event": "batch8_complete", "results": results})
    (EXP / "batch8_results.json").write_text(
        json.dumps({"cycle_id": CYCLE, "fills": FILLS, "results": results, "left": left}, indent=2), encoding="utf-8"
    )

    lines = [
        f"# Level 4 demo handoff — {utc_now()}",
        "",
        "Account: MetaQuotes-Demo. Foreign Client CADCHF not touched.",
        "",
        f"## Batch8 (cycle {CYCLE}) comment L4h",
        "MCP blocked. Python MT5. Magic 771249, 0.01. SL=max(80, stops+spread+2).",
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
        f"Our L4h left: {len(ours_left)}.",
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

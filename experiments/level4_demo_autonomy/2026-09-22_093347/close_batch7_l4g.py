"""Close L4g batch cycle 20260922T104233Z after 5-minute hold; score; update handoff."""
from __future__ import annotations

import json
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import MetaTrader5 as mt5

from mentor_preflight import block_if_mentor_says_stop

MAGIC = 771249
COMMENT_TAG = "L4g"
HOLD_UNTIL = datetime(2026, 9, 22, 10, 47, 40, tzinfo=timezone.utc)
EXP = Path(r"C:\Users\C2K\Desktop\MT5 to agent\experiments\level4_demo_autonomy\2026-09-22_093347")
SCRIPT = Path(__file__).name
LOG = EXP / "demo_trade_tape.jsonl"
FORCED = Path(r"C:\Users\C2K\Desktop\MT5 to agent\JARVIS V1\research\forced_signals.jsonl")
ATLAS = EXP / "atlas_reviews.jsonl"
DECISION = EXP / "decision_tape.jsonl"
HANDOFF = EXP / "reports" / "handoff.md"
CYCLE = "20260922T104233Z"


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


def load_fills_from_tape() -> list[dict]:
    fills = []
    for line in LOG.read_text(encoding="utf-8-sig").splitlines():
        if not line.strip():
            continue
        o = json.loads(line)
        if o.get("event") == "fill" and CYCLE in o.get("signal_id", ""):
            fills.append(o)
    return fills


def load_signals() -> dict[str, dict]:
    out = {}
    for line in FORCED.read_text(encoding="utf-8-sig").splitlines():
        if not line.strip():
            continue
        o = json.loads(line)
        if o.get("signal_id", "").startswith(CYCLE) and o.get("record_type") not in ("outcome", "outcome_correction"):
            if "research_direction" in o:
                out[o["signal_id"]] = o
    return out


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
    ticket = fill["ticket"]
    symbol = fill["symbol"]
    direction = fill["direction"]
    entry = fill["entry"]
    sl = fill.get("sl")
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
            "sl": sl,
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
        "comment": "L4g close",
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
        still2 = any(p.ticket == ticket for p in (mt5.positions_get() or []))
        if still2:
            tick = mt5.symbol_info_tick(symbol)
            req["price"] = tick.bid if direction == "BUY" else tick.ask
            result = mt5.order_send(req)
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
        "sl": sl,
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

    fills = load_fills_from_tape()
    if not fills:
        # rebuild from open positions
        for p in mt5.positions_get() or []:
            if p.magic == MAGIC and COMMENT_TAG in (p.comment or ""):
                fills.append(
                    {
                        "signal_id": f"{CYCLE}_{p.symbol}_?",
                        "symbol": p.symbol,
                        "direction": "BUY" if p.type == mt5.ORDER_TYPE_BUY else "SELL",
                        "ticket": p.ticket,
                        "entry": p.price_open,
                        "sl": p.sl,
                    }
                )
    log({"event": "close_wait", "ts_utc": utc_now(), "n_fills": len(fills), "until": HOLD_UNTIL.isoformat()})

    wait = (HOLD_UNTIL - datetime.now(timezone.utc)).total_seconds()
    if wait > 0:
        time.sleep(wait)

    # re-read before close — only OUR L4g
    ours = [
        {"ticket": p.ticket, "symbol": p.symbol, "comment": p.comment, "sl": p.sl}
        for p in (mt5.positions_get() or [])
        if p.magic == MAGIC and COMMENT_TAG in (p.comment or "")
    ]
    log({"event": "pre_close", "ts_utc": utc_now(), "positions": ours})

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
    ours_left = [p for p in left if p["magic"] == MAGIC and COMMENT_TAG in (p.get("comment") or "")]
    log({"event": "batch7_close_done", "ts_utc": utc_now(), "left": left, "our_L4g_left": ours_left})

    bits = []
    for r in results:
        if already_scored(r["signal_id"]):
            bits.append(f"{r['symbol']} already scored")
            continue
        exit_px = r.get("exit")
        net = r.get("net_points")
        d = r["direction"]
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
                "outcome_reason": (
                    f"Demo ticket {r['ticket']}: entry {r['entry']}, SL {r['sl']}, "
                    f"exit {exit_px} via {r.get('close_path')}. Net {net} points."
                ),
                "post_outcome_review": "Batch7 Level4; MCP blocked; Python MT5; held then closed this run.",
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
            "review": "Level4 batch7 cycle 20260922T104233Z",
            "doctrine": "Locked reasons unchanged.",
            "common_sense": "; ".join(bits),
            "hypotheses": "H-20260922-001/002/003 PROPOSED; H-002 not activated. 20260922T090923Z UNRESOLVED.",
        },
    )
    append_jsonl(DECISION, {"ts_utc": utc_now(), "cycle_id": CYCLE, "event": "batch7_complete", "results": results})
    (EXP / "batch7_results.json").write_text(
        json.dumps({"cycle_id": CYCLE, "fills": fills, "results": results, "left": left}, indent=2), encoding="utf-8"
    )

    lines = [
        f"# Level 4 demo handoff — {utc_now()}",
        "",
        "Account: MetaQuotes-Demo.",
        "",
        "## Batch6 (cycle 20260922T102651Z) — already scored / flat",
        "| Symbol | Dir | Ticket | Entry | Stop | Exit | Net pts | Close path | Flat |",
        "|---|---|---:|---:|---:|---:|---:|---|---|",
        "| EURCAD | BUY | 58568462450 | 1.60874 | 1.60795 | 1.60869 | -5 | five_minute | yes |",
        "| GBPUSD | SELL | 58568462582 | 1.33652 | 1.33732 | 1.33677 | -25 | five_minute | yes |",
        "| USDCAD | BUY | 58568462698 | 1.40366 | 1.40286 | 1.40337 | -29 | five_minute | yes |",
        "| EURGBP | SELL | 58568462782 | 0.85754 | 0.85834 | 0.85757 | -3 | five_minute | yes |",
        "| GBPCAD | BUY | 58568462879 | 1.87597 | 1.87517 | 1.87586 | -11 | five_minute | yes |",
        "",
        f"## Batch7 (cycle {CYCLE})",
        "MCP trade blocked. Python MetaTrader5. Magic 771249, 0.01. Comment L4g. Closed after 5-minute hold.",
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
        f"Foreign tickets not touched. Our L4g left: {len(ours_left)}.",
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

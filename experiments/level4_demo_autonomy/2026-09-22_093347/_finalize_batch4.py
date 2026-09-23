"""Append-only finalize for batch4 cycle 20260922T100907Z (MCP-reconciled exits)."""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

EXP = Path(r"C:\Users\C2K\Desktop\MT5 to agent\experiments\level4_demo_autonomy\2026-09-22_093347")
FORCED = Path(r"C:\Users\C2K\Desktop\MT5 to agent\JARVIS V1\research\forced_signals.jsonl")
ATLAS = EXP / "atlas_reviews.jsonl"
DECISION = EXP / "decision_tape.jsonl"
HANDOFF = EXP / "reports" / "handoff.md"
LOG = EXP / "demo_trade_tape.jsonl"

ROWS = [
    dict(
        signal_id="20260922T100907Z_NZDUSD_2_S3_1",
        symbol="NZDUSD",
        direction="BUY",
        ticket=58568161598,
        entry=0.57465,
        sl=0.57386,
        exit=0.57406,
        point=1e-5,
    ),
    dict(
        signal_id="20260922T100907Z_EURUSD_1_S3_2",
        symbol="EURUSD",
        direction="BUY",
        ticket=58568161719,
        entry=1.14678,
        sl=1.14598,
        exit=1.14635,
        point=1e-5,
    ),
    dict(
        signal_id="20260922T100907Z_AUDUSD_1_S3_3",
        symbol="AUDUSD",
        direction="BUY",
        ticket=58568161897,
        entry=0.71174,
        sl=0.71093,
        exit=0.71145,
        point=1e-5,
    ),
    dict(
        signal_id="20260922T100907Z_EURCHF_1_S3_4",
        symbol="EURCHF",
        direction="SELL",
        ticket=58568162117,
        entry=0.93885,
        sl=0.93965,
        exit=0.93926,
        point=1e-5,
    ),
    dict(
        signal_id="20260922T100907Z_GBPCHF_3_S3_5",
        symbol="GBPCHF",
        direction="SELL",
        ticket=58568162238,
        entry=1.09446,
        sl=1.09526,
        exit=1.09520,
        point=1e-5,
    ),
]


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def append(path: Path, obj: dict) -> None:
    with path.open("a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(obj, separators=(",", ":")) + "\n")


def main() -> int:
    existing = FORCED.read_text(encoding="utf-8")
    scored = set()
    for line in existing.splitlines():
        if not line.strip():
            continue
        o = json.loads(line)
        if o.get("record_type") == "outcome" and o.get("signal_id", "").startswith("20260922T100907Z"):
            scored.add(o["signal_id"])

    now = utc_now()
    broker = (datetime.now(timezone.utc) + timedelta(hours=3)).strftime("%Y.%m.%d %H:%M:%S")
    results = []
    for r in ROWS:
        d = r["direction"]
        net_price = (r["exit"] - r["entry"]) if d == "BUY" else (r["entry"] - r["exit"])
        net_pts = round(net_price / r["point"], 1)
        r = dict(r)
        r["net_points"] = net_pts
        r["close_path"] = "five_minute"
        r["flat"] = True
        results.append(r)
        if r["signal_id"] in scored:
            print("skip", r["signal_id"])
            continue
        status = "PROFITABLE" if net_pts > 0 else "NOT_PROFITABLE"
        outcome = {
            "record_type": "outcome",
            "signal_id": r["signal_id"],
            "scored_utc": now,
            "scored_broker": broker,
            "exit_bid": r["exit"] if d == "BUY" else None,
            "exit_ask": r["exit"] if d == "SELL" else None,
            "exit_executable_price": r["exit"],
            "net_price_after_spread": net_price,
            "net_points_after_spread": net_pts,
            "outcome_status": status,
            "commission_status": "NOT_INCLUDED",
            "outcome_reason": (
                f"Demo ticket {r['ticket']}: entry {r['entry']}, SL {r['sl']} (80 pts), "
                f"exit {r['exit']} via five_minute. Net {net_pts} points."
            ),
            "post_outcome_review": (
                "Batch4 Level4 demo; MCP trade blocked; Python MetaTrader5; "
                "exits reconciled via MCP history (Expert timed close)."
            ),
            "locked_reason_unchanged": True,
            "demo_ticket": r["ticket"],
            "magic": 771249,
            "volume": 0.01,
            "stop": r["sl"],
            "close_path": "five_minute",
            "flat": True,
        }
        append(FORCED, outcome)
        print("outcome", r["symbol"], net_pts)

    bits = "; ".join(f"{r['symbol']} {r['direction']} five_minute net={r['net_points']}" for r in results)
    append(
        ATLAS,
        {
            "ts_utc": now,
            "review": "Level4 batch4",
            "doctrine": "Locked reasons unchanged; 80-point stop is research harness only.",
            "common_sense": bits + ". All five reached timed Expert close; none hit 80-pt SL.",
            "hypotheses": (
                "H-20260922-001/002/003 remain PROPOSED; H-002 not activated. "
                "Cycle 20260922T090923Z UNRESOLVED."
            ),
        },
    )
    append(
        DECISION,
        {
            "ts_utc": now,
            "cycle_id": "20260922T100907Z",
            "event": "batch4_complete",
            "n_signals": 5,
            "n_fills": 5,
            "results": results,
        },
    )
    append(LOG, {"event": "batch4_reconciled", "ts_utc": now, "results": results})

    br_path = EXP / "batch4_results.json"
    br = json.loads(br_path.read_text(encoding="utf-8")) if br_path.exists() else {}
    br["results"] = [
        {
            "event": "close",
            "ts_utc": now,
            "signal_id": r["signal_id"],
            "symbol": r["symbol"],
            "direction": r["direction"],
            "ticket": r["ticket"],
            "entry": r["entry"],
            "sl": r["sl"],
            "exit": r["exit"],
            "net_points": r["net_points"],
            "close_path": "five_minute",
            "flat": True,
        }
        for r in results
    ]
    br["reconciled_via"] = "mcp_history"
    br_path.write_text(json.dumps(br, indent=2), encoding="utf-8")

    lines = [
        f"# Level 4 demo handoff — {now}",
        "",
        "Account: MetaQuotes-Demo. Positions re-read: **flat**.",
        "",
        "## Batch4 (cycle 20260922T100907Z)",
        "MCP trade blocked. Python MetaTrader5. Magic 771249, volume 0.01, SL 80 points. Comment L4d.",
        "",
        "| Symbol | Dir | Ticket | Entry | Stop | Exit | Net pts | Close path | Flat |",
        "|---|---|---:|---:|---:|---:|---:|---|---|",
    ]
    for r in results:
        lines.append(
            f"| {r['symbol']} | {r['direction']} | {r['ticket']} | {r['entry']} | {r['sl']} | "
            f"{r['exit']} | {r['net_points']} | five_minute | yes |"
        )
    lines += [
        "",
        "No foreign tickets touched. Book empty.",
        "",
        "## Next wake",
        "1. Continue until STOP_LEVEL_4_DEMO_AUTONOMY / STOP_FORCED_SIGNAL_LOOP.",
        "2. Do not activate H-20260922-002. Do not rescore 20260922T090923Z.",
        "",
    ]
    HANDOFF.write_text("\n".join(lines), encoding="utf-8")
    print("handoff written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

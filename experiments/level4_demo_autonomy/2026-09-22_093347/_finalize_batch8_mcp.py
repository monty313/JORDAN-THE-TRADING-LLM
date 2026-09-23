"""Score L4h cycle 20260922T105113Z from MCP history exits."""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

EXP = Path(r"C:\Users\C2K\Desktop\MT5 to agent\experiments\level4_demo_autonomy\2026-09-22_093347")
FORCED = Path(r"C:\Users\C2K\Desktop\MT5 to agent\JARVIS V1\research\forced_signals.jsonl")
ATLAS = EXP / "atlas_reviews.jsonl"
HANDOFF = EXP / "reports" / "handoff.md"
LOG = EXP / "demo_trade_tape.jsonl"

ROWS = [
    dict(signal_id="20260922T105113Z_AUDUSD_2_S1_1", symbol="AUDUSD", direction="BUY", ticket=58568878120, entry=0.71173, sl=0.71093, exit=0.71172, point=1e-5),
    dict(signal_id="20260922T105113Z_EURAUD_3_S1_2", symbol="EURAUD", direction="BUY", ticket=58568878211, entry=1.61124, sl=1.61044, exit=1.61121, point=1e-5),
    dict(signal_id="20260922T105113Z_EURJPY_3_S4_3", symbol="EURJPY", direction="SELL", ticket=58568878409, entry=180.030, sl=180.110, exit=180.046, point=0.001),
    dict(signal_id="20260922T105113Z_USDJPY_1_S4_4", symbol="USDJPY", direction="SELL", ticket=58568878545, entry=156.986, sl=157.066, exit=157.000, point=0.001),
    dict(signal_id="20260922T105113Z_AUDJPY_3_S4_5", symbol="AUDJPY", direction="SELL", ticket=58568878881, entry=111.727, sl=111.807, exit=111.744, point=0.001),
]


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def append(path: Path, obj: dict) -> None:
    with path.open("a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(obj, separators=(",", ":")) + "\n")


def main() -> int:
    existing = FORCED.read_text(encoding="utf-8-sig")
    now = utc_now()
    broker = (datetime.now(timezone.utc) + timedelta(hours=3)).strftime("%Y.%m.%d %H:%M:%S")
    results = []
    for r in ROWS:
        d = r["direction"]
        net_price = (r["exit"] - r["entry"]) if d == "BUY" else (r["entry"] - r["exit"])
        net_pts = round(net_price / r["point"], 1)
        row = dict(r)
        row["net_points"] = net_pts
        row["close_path"] = "five_minute"
        results.append(row)

        has_good = False
        for line in existing.splitlines():
            if not line.strip():
                continue
            o = json.loads(line)
            if o.get("record_type") == "outcome" and o.get("signal_id") == r["signal_id"] and o.get("exit_executable_price") is not None:
                has_good = True
                break
        if has_good:
            print("skip", r["signal_id"])
            continue

        status = "PROFITABLE" if net_pts > 0 else "NOT_PROFITABLE"
        append(
            FORCED,
            {
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
                    f"Demo ticket {r['ticket']}: entry {r['entry']}, SL {r['sl']}, "
                    f"exit {r['exit']} via five_minute. Net {net_pts} points."
                ),
                "post_outcome_review": "Batch8 L4h; MCP blocked; Python MT5; MCP history Expert timed close.",
                "locked_reason_unchanged": True,
                "demo_ticket": r["ticket"],
                "magic": 771249,
                "volume": 0.01,
                "stop": r["sl"],
                "close_path": "five_minute",
                "flat": True,
            },
        )
        print("outcome", r["symbol"], net_pts)

    bits = "; ".join(f"{r['symbol']} {r['direction']} five_minute net={r['net_points']}" for r in results)
    append(
        ATLAS,
        {
            "ts_utc": now,
            "review": "Level4 batch8 cycle 20260922T105113Z",
            "doctrine": "Locked reasons unchanged.",
            "common_sense": bits,
            "hypotheses": "H-20260922-001/002/003 PROPOSED; H-002 not activated. 20260922T090923Z UNRESOLVED.",
        },
    )
    append(LOG, {"event": "batch8_reconciled", "ts_utc": now, "results": results})
    (EXP / "batch8_results.json").write_text(
        json.dumps({"cycle_id": "20260922T105113Z", "results": results, "reconciled_via": "mcp_history"}, indent=2),
        encoding="utf-8",
    )

    lines = [
        f"# Level 4 demo handoff — {now}",
        "",
        "Account: MetaQuotes-Demo. Our L4h book: **flat**. Foreign Client tickets not touched.",
        "",
        "## Batch8 (cycle 20260922T105113Z) comment L4h",
        "MCP blocked. Python MT5. Magic 771249, 0.01. SL=max(80, stops+spread+2). Expert timed close ~+5m.",
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

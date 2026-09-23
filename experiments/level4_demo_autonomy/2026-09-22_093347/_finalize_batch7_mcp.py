"""Append MCP-reconciled outcomes for cycle 20260922T104233Z if missing exits."""
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
    dict(signal_id="20260922T104233Z_EURUSD_2_S1_1", symbol="EURUSD", direction="BUY", ticket=58568712604, entry=1.14675, sl=1.14595, exit=1.14680, point=1e-5),
    dict(signal_id="20260922T104233Z_EURCHF_4_S3_2", symbol="EURCHF", direction="SELL", ticket=58568712726, entry=0.93863, sl=0.93943, exit=0.93868, point=1e-5),
    dict(signal_id="20260922T104233Z_USDCHF_3_S3_3", symbol="USDCHF", direction="SELL", ticket=58568712844, entry=0.81853, sl=0.81933, exit=0.81851, point=1e-5),
    dict(signal_id="20260922T104233Z_GBPCHF_4_S3_4", symbol="GBPCHF", direction="SELL", ticket=58568712967, entry=1.09426, sl=1.09505, exit=1.09425, point=1e-5),
    dict(signal_id="20260922T104233Z_CADJPY_2_S2_5", symbol="CADJPY", direction="SELL", ticket=58568713057, entry=111.860, sl=111.940, exit=111.909, point=0.001),
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
        r = dict(r)
        r["net_points"] = net_pts
        r["close_path"] = "five_minute"
        results.append(r)

        has_good = False
        for line in existing.splitlines():
            if not line.strip():
                continue
            o = json.loads(line)
            if (
                o.get("record_type") == "outcome"
                and o.get("signal_id") == r["signal_id"]
                and o.get("exit_executable_price") is not None
            ):
                has_good = True
                break
        if has_good:
            print("skip scored", r["signal_id"])
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
                "post_outcome_review": (
                    "Batch7 Level4; MCP blocked; Python MT5; exits from MCP history Expert timed close."
                ),
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
            "review": "Level4 batch7 cycle 20260922T104233Z",
            "doctrine": "Locked reasons unchanged.",
            "common_sense": bits,
            "hypotheses": "H-20260922-001/002/003 PROPOSED; H-002 not activated. 20260922T090923Z UNRESOLVED.",
        },
    )
    append(LOG, {"event": "batch7_reconciled", "ts_utc": now, "results": results})
    (EXP / "batch7_results.json").write_text(
        json.dumps({"cycle_id": "20260922T104233Z", "results": results, "reconciled_via": "mcp_history"}, indent=2),
        encoding="utf-8",
    )

    lines = [
        f"# Level 4 demo handoff — {now}",
        "",
        "Account: MetaQuotes-Demo. Our L4g book: **flat** (foreign Client tickets not touched).",
        "",
        "## Batch6 (cycle 20260922T102651Z) — scored",
        "| Symbol | Dir | Ticket | Entry | Stop | Exit | Net pts | Close path | Flat |",
        "|---|---|---:|---:|---:|---:|---:|---|---|",
        "| EURCAD | BUY | 58568462450 | 1.60874 | 1.60795 | 1.60869 | -5 | five_minute | yes |",
        "| GBPUSD | SELL | 58568462582 | 1.33652 | 1.33732 | 1.33677 | -25 | five_minute | yes |",
        "| USDCAD | BUY | 58568462698 | 1.40366 | 1.40286 | 1.40337 | -29 | five_minute | yes |",
        "| EURGBP | SELL | 58568462782 | 0.85754 | 0.85834 | 0.85757 | -3 | five_minute | yes |",
        "| GBPCAD | BUY | 58568462879 | 1.87597 | 1.87517 | 1.87586 | -11 | five_minute | yes |",
        "",
        "## Batch7 (cycle 20260922T104233Z)",
        "MCP trade blocked. Python MetaTrader5. Magic 771249, 0.01. Comment L4g. Expert timed close ~+5m.",
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

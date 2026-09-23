"""Reconcile L5c cycle 20260922T131314Z from MCP history exits."""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

EXP = Path(r"C:\Users\C2K\Desktop\MT5 to agent\experiments\level4_demo_autonomy\2026-09-22_093347")
FORCED = Path(r"C:\Users\C2K\Desktop\MT5 to agent\JARVIS V1\research\forced_signals.jsonl")
ATLAS = EXP / "atlas_reviews.jsonl"
ATLAS_MD = Path(r"C:\Users\C2K\Desktop\MT5 to agent\JARVIS V1\research\atlas_reviews.md")
HANDOFF = EXP / "reports" / "handoff.md"
LOG = EXP / "demo_trade_tape.jsonl"
DECISION = EXP / "decision_tape.jsonl"

ROWS = [
    dict(
        signal_id="20260922T131314Z_USDCHF_2_S1_1",
        symbol="USDCHF",
        direction="BUY",
        ticket=58572101063,
        entry=0.81991,
        sl=0.81911,
        exit=0.81977,
        point=1e-5,
        close_path="five_minute",
    ),
    dict(
        signal_id="20260922T131314Z_EURCHF_1_S1_2",
        symbol="EURCHF",
        direction="BUY",
        ticket=58572101337,
        entry=0.93935,
        sl=0.93855,
        exit=0.93918,
        point=1e-5,
        close_path="five_minute",
    ),
    dict(
        signal_id="20260922T131314Z_GBPCAD_1_S3_3",
        symbol="GBPCAD",
        direction="BUY",
        ticket=58572101488,
        entry=1.87683,
        sl=1.87603,
        exit=1.87683,
        point=1e-5,
        close_path="five_minute",
    ),
    dict(
        signal_id="20260922T131314Z_EURNZD_1_S1_4",
        symbol="EURNZD",
        direction="BUY",
        ticket=58572101594,
        entry=2.00029,
        sl=1.99949,
        exit=2.00030,
        point=1e-5,
        close_path="five_minute",
    ),
    dict(
        signal_id="20260922T131314Z_GBPCHF_2_S1_5",
        symbol="GBPCHF",
        direction="BUY",
        ticket=58572101987,
        entry=1.09537,
        sl=1.09456,
        exit=1.09515,
        point=1e-5,
        close_path="five_minute",
    ),
]


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def append(path: Path, obj: dict) -> None:
    with path.open("a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(obj, separators=(",", ":")) + "\n")


def outcome_status(net_pts: float) -> str:
    if net_pts > 0:
        return "PROFITABLE"
    if net_pts == 0:
        return "FLAT"
    return "NOT_PROFITABLE"


def main() -> int:
    existing = FORCED.read_text(encoding="utf-8-sig")
    now = utc_now()
    broker = (datetime.now(timezone.utc) + timedelta(hours=3)).strftime("%Y.%m.%d %H:%M:%S")
    results = []
    for r in ROWS:
        d = r["direction"]
        net_price = (r["exit"] - r["entry"]) if d == "BUY" else (r["entry"] - r["exit"])
        net_pts = round(net_price / r["point"], 1)
        row = {**r, "net_points": net_pts, "flat": True}
        results.append(row)

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
            print("skip", r["symbol"])
            continue

        status = outcome_status(net_pts)
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
                    f"exit {r['exit']} via {r['close_path']}. Net {net_pts} points."
                ),
                "post_outcome_review": (
                    "Batch27 L5c; MCP blocked; Python MT5; MCP history Expert timed close ~+5m."
                ),
                "locked_reason_unchanged": True,
                "demo_ticket": r["ticket"],
                "magic": 771249,
                "volume": 0.01,
                "stop": r["sl"],
                "close_path": r["close_path"],
                "flat": True,
            },
        )
        print(r["symbol"], net_pts, status)

    bits = "; ".join(
        f"{r['symbol']} {r['direction']} {r['close_path']} net={r['net_points']}" for r in results
    )
    append(
        ATLAS,
        {
            "ts_utc": now,
            "review": "Level4 batch27 cycle 20260922T131314Z",
            "doctrine": "Locked reasons unchanged. Old Send-nothing inbox lines not stop tokens.",
            "common_sense": bits,
            "hypotheses": "H-20260922-001/002/003 PROPOSED; H-002 not activated. 20260922T090923Z UNRESOLVED.",
        },
    )
    append(
        DECISION,
        {"ts_utc": now, "cycle_id": "20260922T131314Z", "event": "batch27_complete", "results": results},
    )
    append(LOG, {"event": "batch27_reconciled", "ts_utc": now, "results": results})
    (EXP / "batch27_results.json").write_text(
        json.dumps({"cycle_id": "20260922T131314Z", "results": results, "reconciled_via": "mcp_history"}, indent=2),
        encoding="utf-8",
    )

    md = ATLAS_MD.read_text(encoding="utf-8")
    if "20260922T131314Z" not in md:
        md += (
            "\n## Review 20260922T131820Z — Level 4 batch27 L5c\n\n"
            "Doctrine audit: locked reasons unchanged. Common sense: "
            f"{bits}. "
            "CHFJPY skipped this batch after opposite-side trades in L4z/L5b. "
            "MCP trade_* blocked; Python MetaTrader5. "
            "H-20260922-001/002/003 stay PROPOSED. H-002 not activated. "
            "20260922T090923Z UNRESOLVED. No new live rule.\n"
        )
        ATLAS_MD.write_text(md, encoding="utf-8")

    lines = [
        f"# Level 4 demo handoff — {now}",
        "",
        "Account: MetaQuotes-Demo. Our L5c book: **flat**. Foreign Client CADCHF not touched.",
        "",
        "## Batch27 (cycle 20260922T131314Z) comment L5c",
        "MCP blocked. Python MT5. Magic 771249, 0.01.",
        "SL: majors max(80, stops+spread); JPY/CNH max(250, stops+spread). No SEK. CHFJPY skipped.",
        "Expert timed close ~+5m (16:18:14–16 broker).",
        "",
        "| Symbol | Dir | Ticket | Entry | Stop | Exit | Net pts | Close path | Flat |",
        "|---|---|---:|---:|---:|---:|---:|---|---|",
    ]
    for r in results:
        lines.append(
            f"| {r['symbol']} | {r['direction']} | {r['ticket']} | {r['entry']} | {r['sl']} | "
            f"{r['exit']} | {r['net_points']} | {r['close_path']} | yes |"
        )
    lines += [
        "",
        "## Next wake",
        "1. Continue until fresh STOP_LEVEL_4_DEMO_AUTONOMY / STOP_FORCED_SIGNAL_LOOP after 09:12 NY.",
        "2. Do not activate H-20260922-002. Do not rescore 20260922T090923Z.",
        "",
    ]
    HANDOFF.write_text("\n".join(lines), encoding="utf-8")
    print("handoff written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

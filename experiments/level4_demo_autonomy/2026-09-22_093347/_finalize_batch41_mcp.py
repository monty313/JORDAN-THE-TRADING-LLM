"""Reconcile L5s cycle 20260922T145412Z from MCP history."""
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
        signal_id="20260922T145412Z_AUDNZD_0_S0_1",
        symbol="AUDNZD",
        direction="BUY",
        ticket=58574775325,
        entry=1.24175,
        sl=1.24095,
        exit=1.24177,
        point=1e-5,
        close_path="five_minute",
    ),
    dict(
        signal_id="20260922T145412Z_EURAUD_2_S2_2",
        symbol="EURAUD",
        direction="SELL",
        ticket=58574775700,
        entry=1.61061,
        sl=1.61141,
        exit=1.61053,
        point=1e-5,
        close_path="five_minute",
    ),
    dict(
        signal_id="20260922T145412Z_USDCAD_1_S4_3",
        symbol="USDCAD",
        direction="BUY",
        ticket=58574775795,
        entry=1.40642,
        sl=1.40564,
        exit=1.40626,
        point=1e-5,
        close_path="five_minute",
    ),
    dict(
        signal_id="20260922T145412Z_EURGBP_1_S2_4",
        symbol="EURGBP",
        direction="SELL",
        ticket=58574775908,
        entry=0.85737,
        sl=0.85817,
        exit=0.85736,
        point=1e-5,
        close_path="five_minute",
    ),
    dict(
        signal_id="20260922T145412Z_USDCHF_1_S1_5",
        symbol="USDCHF",
        direction="BUY",
        ticket=58574776018,
        entry=0.82106,
        sl=0.82026,
        exit=0.82094,
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
                    "Batch41 L5s forced five; soft-avoided L5r; mixed 3 BUY/2 SELL; "
                    "no GBPUSD/NZDUSD/AUDUSD SELL stack; MCP blocked; Python MT5."
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
            "review": "Level4 batch41 cycle 20260922T145412Z L5s forced",
            "doctrine": "Locked reasons unchanged. Forced five with direction mix.",
            "common_sense": bits + " | mix 3 BUY / 2 SELL; avoided L5r and GBPUSD/NZDUSD/AUDUSD SELL stack.",
            "hypotheses": "H-20260922-001/002/003 PROPOSED; H-002 not activated. 20260922T090923Z UNRESOLVED.",
        },
    )
    append(
        DECISION,
        {"ts_utc": now, "cycle_id": "20260922T145412Z", "event": "batch41_complete", "results": results},
    )
    append(LOG, {"event": "batch41_reconciled", "ts_utc": now, "results": results})
    (EXP / "batch41_results.json").write_text(
        json.dumps({"cycle_id": "20260922T145412Z", "results": results, "reconciled_via": "mcp_history"}, indent=2),
        encoding="utf-8",
    )

    md = ATLAS_MD.read_text(encoding="utf-8")
    if "20260922T145412Z" not in md:
        md += (
            "\n## Review 20260922T150000Z — Level 4 batch41 L5s forced\n\n"
            "Doctrine audit: locked reasons unchanged. Common sense: "
            f"{bits}. Mixed 3 BUY / 2 SELL; soft-avoided L5r; no GBPUSD/NZDUSD/AUDUSD "
            "SELL stack. MCP trade_* blocked; Python MetaTrader5. "
            "H-002 not activated. 20260922T090923Z UNRESOLVED. No new live rule.\n"
        )
        ATLAS_MD.write_text(md, encoding="utf-8")

    lines = [
        f"# Level 4 demo handoff — {now}",
        "",
        "Account: MetaQuotes-Demo. Our L5s book: **flat**. Foreign Client CADCHF not touched.",
        "",
        "## Batch41 (cycle 20260922T145412Z) comment L5s",
        "Forced five with direction mix (3 BUY / 2 SELL). Soft-avoided L5r. MCP blocked. Python MT5.",
        "Expert timed close ~+5m (17:59:12–15 broker).",
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
        "1. Continue with forced five every cycle when quotes exist; mix directions.",
        "2. Do not activate H-20260922-002. Do not rescore 20260922T090923Z.",
        "",
    ]
    HANDOFF.write_text("\n".join(lines), encoding="utf-8")
    print("handoff written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

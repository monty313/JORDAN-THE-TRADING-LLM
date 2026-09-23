"""Reconcile L5p cycle 20260922T143427Z from MCP history."""
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
        signal_id="20260922T143427Z_EURUSD_1_S2_1",
        symbol="EURUSD",
        direction="SELL",
        ticket=58574169005,
        entry=1.14482,
        sl=1.14562,
        exit=1.14488,
        point=1e-5,
        close_path="five_minute",
    ),
    dict(
        signal_id="20260922T143427Z_NZDUSD_4_S1_2",
        symbol="NZDUSD",
        direction="BUY",
        ticket=58574169394,
        entry=0.57308,
        sl=0.57228,
        exit=0.57333,
        point=1e-5,
        close_path="five_minute",
    ),
    dict(
        signal_id="20260922T143427Z_AUDJPY_2_S1_3",
        symbol="AUDJPY",
        direction="BUY",
        ticket=58574169623,
        entry=111.769,
        sl=111.52,
        exit=111.785,
        point=0.001,
        close_path="five_minute",
    ),
    dict(
        signal_id="20260922T143427Z_EURJPY_2_S3_4",
        symbol="EURJPY",
        direction="SELL",
        ticket=58574169881,
        entry=179.995,
        sl=180.245,
        exit=180.004,
        point=0.001,
        close_path="five_minute",
    ),
    dict(
        signal_id="20260922T143427Z_EURCAD_2_S2_5",
        symbol="EURCAD",
        direction="BUY",
        ticket=58574170125,
        entry=1.60959,
        sl=1.60879,
        exit=1.60948,
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
                    "Batch38 L5p forced five; soft-avoided L5n; mixed 3 BUY/2 SELL; "
                    "JPY pairs used 250-pt stops; no GBPUSD/NZDUSD/AUDUSD SELL stack; "
                    "MCP blocked; Python MT5."
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
            "review": "Level4 batch38 cycle 20260922T143427Z L5p forced",
            "doctrine": "Locked reasons unchanged. Forced five with direction mix.",
            "common_sense": bits + " | mix 3 BUY / 2 SELL; avoided L5n; AUDJPY/EURJPY 250-pt stops.",
            "hypotheses": "H-20260922-001/002/003 PROPOSED; H-002 not activated. 20260922T090923Z UNRESOLVED.",
        },
    )
    append(
        DECISION,
        {"ts_utc": now, "cycle_id": "20260922T143427Z", "event": "batch38_complete", "results": results},
    )
    append(LOG, {"event": "batch38_reconciled", "ts_utc": now, "results": results})
    (EXP / "batch38_results.json").write_text(
        json.dumps({"cycle_id": "20260922T143427Z", "results": results, "reconciled_via": "mcp_history"}, indent=2),
        encoding="utf-8",
    )

    md = ATLAS_MD.read_text(encoding="utf-8")
    if "20260922T143427Z" not in md:
        md += (
            "\n## Review 20260922T144000Z — Level 4 batch38 L5p forced\n\n"
            "Doctrine audit: locked reasons unchanged. Common sense: "
            f"{bits}. Mixed 3 BUY / 2 SELL; soft-avoided L5n; AUDJPY/EURJPY 250-pt stops; "
            "no GBPUSD/NZDUSD/AUDUSD SELL stack. MCP trade_* blocked; Python MetaTrader5. "
            "H-002 not activated. 20260922T090923Z UNRESOLVED. No new live rule.\n"
        )
        ATLAS_MD.write_text(md, encoding="utf-8")

    lines = [
        f"# Level 4 demo handoff — {now}",
        "",
        "Account: MetaQuotes-Demo. Our L5p book: **flat**. Foreign Client CADCHF not touched.",
        "",
        "## Batch38 (cycle 20260922T143427Z) comment L5p",
        "Forced five with direction mix (3 BUY / 2 SELL). Soft-avoided L5n. MCP blocked. Python MT5.",
        "AUDJPY/EURJPY used 250-pt stops. Expert timed close ~+5m (17:39:27–30 broker).",
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

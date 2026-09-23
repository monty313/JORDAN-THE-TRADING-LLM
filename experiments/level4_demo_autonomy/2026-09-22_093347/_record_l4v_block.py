"""Record L4v mentor preflight block — no opens."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

EXP = Path(r"C:\Users\C2K\Desktop\MT5 to agent\experiments\level4_demo_autonomy\2026-09-22_093347")
ATLAS = EXP / "atlas_reviews.jsonl"
HANDOFF = EXP / "reports" / "handoff.md"
LOG = EXP / "demo_trade_tape.jsonl"
DECISION = EXP / "decision_tape.jsonl"

NOW = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

# Planned forbid context only — no signals locked / no fills
PLANNED = [
    "AUDUSD SELL",
    "EURGBP BUY",
    "USDCHF SELL",
    "EURCHF SELL",
    "GBPCHF SELL",
]


def append(path: Path, obj: dict) -> None:
    with path.open("a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(obj, separators=(",", ":")) + "\n")


def main() -> int:
    append(
        LOG,
        {
            "event": "batch20_preflight_halt",
            "ts_utc": NOW,
            "cycle_id": None,
            "comment": "L4v",
            "reason": "mentor_send_nothing",
            "opened": 0,
            "note": "Newest MENTOR_INBOX ## 2026-09-22 07:43 contains Send nothing / Do not add a batch. Mentor gate kept. No STOP_LEVEL_4_DEMO_AUTONOMY / STOP_FORCED_SIGNAL_LOOP.",
        },
    )
    append(
        ATLAS,
        {
            "ts_utc": NOW,
            "review": "Level4 batch20 L4v — mentor preflight BLOCK",
            "doctrine": "Mentor stop check not stripped. No new demo opens.",
            "common_sense": (
                "preflight_block mentor_send_nothing; magic 771249 already flat; "
                "foreign Client CADCHF not touched; goal stop tokens absent."
            ),
            "hypotheses": "H-20260922-001/002/003 PROPOSED; H-002 not activated. 20260922T090923Z UNRESOLVED.",
        },
    )
    append(
        DECISION,
        {
            "ts_utc": NOW,
            "event": "batch20_l4v_blocked",
            "reason": "mentor_send_nothing",
            "opened": 0,
        },
    )
    (EXP / "batch20_results.json").write_text(
        json.dumps(
            {
                "cycle_id": None,
                "comment": "L4v",
                "status": "PREFLIGHT_BLOCK",
                "reason": "mentor_send_nothing",
                "results": [],
                "opened": 0,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    lines = [
        f"# Level 4 demo handoff — {NOW}",
        "",
        "Account: MetaQuotes-Demo. Magic 771249 **flat**. Foreign Client CADCHF not touched.",
        "",
        "## Batch20 comment L4v — PREFLIGHT BLOCK (no opens)",
        "Mentor gate kept. Newest `MENTOR_INBOX` section (`## 2026-09-22 07:43`) includes",
        "`Send nothing` / `Do not add a batch` → `mentor_send_nothing`.",
        "No `STOP_LEVEL_4_DEMO_AUTONOMY` / `STOP_FORCED_SIGNAL_LOOP` token present.",
        "Zero tickets opened. Forced signals not locked for this batch.",
        "",
        "| Symbol | Dir | Ticket | Entry | Stop | Exit | Net pts | Close path | Flat |",
        "|---|---|---:|---:|---:|---:|---:|---|---|",
        "| — | — | REJECT (mentor_send_nothing) | - | - | - | - | reject | yes |",
        "",
        "## Next wake",
        "1. Continue until STOP_LEVEL_4_DEMO_AUTONOMY / STOP_FORCED_SIGNAL_LOOP.",
        "2. Do not strip mentor preflight. If newest inbox still says Send nothing, do not open.",
        "3. Do not activate H-20260922-002. Do not rescore 20260922T090923Z.",
        "",
    ]
    HANDOFF.write_text("\n".join(lines), encoding="utf-8")
    print("handoff written; opened=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

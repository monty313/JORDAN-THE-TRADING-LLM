"""Record L5e abort: fewer than 5 eligible closed-bar signals."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

EXP = Path(r"C:\Users\C2K\Desktop\MT5 to agent\experiments\level4_demo_autonomy\2026-09-22_093347")
ATLAS = EXP / "atlas_reviews.jsonl"
ATLAS_MD = Path(r"C:\Users\C2K\Desktop\MT5 to agent\JARVIS V1\research\atlas_reviews.md")
HANDOFF = EXP / "reports" / "handoff.md"
LOG = EXP / "demo_trade_tape.jsonl"
DECISION = EXP / "decision_tape.jsonl"

now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
cycle = "20260922T132735Z_ABORT"  # no cycle opened; stamp from abort window

payload = {
    "ts_utc": now,
    "event": "batch29_l5e_abort_not_enough_signals",
    "n_eligible": 1,
    "eligible": [{"symbol": "EURCNH", "direction": "SELL"}],
    "forbid": "L5a+L5b+L5c+L5d pairs",
    "skip_symbols": ["CADCHF", "USDSEK", "CHFJPY", "EURCHF", "GBPCHF"],
    "note": "Board 2026.09.22 16:28:30 had only one tradeable unsuffixed FX FIRE/WAIT_LOADED after forbids; NZDCAD/NZDCHF FIRE but volume_min=0.1. No orders.",
}

with LOG.open("a", encoding="utf-8", newline="\n") as f:
    f.write(json.dumps(payload, separators=(",", ":")) + "\n")
with DECISION.open("a", encoding="utf-8", newline="\n") as f:
    f.write(json.dumps({**payload, "cycle_id": cycle}, separators=(",", ":")) + "\n")
with ATLAS.open("a", encoding="utf-8", newline="\n") as f:
    f.write(
        json.dumps(
            {
                "ts_utc": now,
                "review": "Level4 batch29 L5e aborted — not enough signals",
                "doctrine": "Locked reasons unchanged. Did not invent signals.",
                "common_sense": payload["note"],
                "hypotheses": "H-20260922-001/002/003 PROPOSED; H-002 not activated. 20260922T090923Z UNRESOLVED.",
            },
            separators=(",", ":"),
        )
        + "\n"
    )

md = ATLAS_MD.read_text(encoding="utf-8")
if "batch29 L5e aborted" not in md:
    md += (
        "\n## Review 20260922T132800Z — Level 4 batch29 L5e aborted\n\n"
        "Doctrine audit: locked reasons unchanged; no rewrite. Common sense: after L5a–L5d "
        "forbids and CHFJPY/EURCHF/GBPCHF skips, the closed-bar board offered only EURCNH SELL "
        "as a tradeable unsuffixed 0.01 FX setup (NZDCAD/NZDCHF FIRE but volume_min 0.1). "
        "No orders sent. Magic 771249 stayed flat. H-002 not activated. "
        "20260922T090923Z UNRESOLVED. No new live rule.\n"
    )
    ATLAS_MD.write_text(md, encoding="utf-8")

(EXP / "batch29_results.json").write_text(
    json.dumps({"cycle_id": None, "comment": "L5e", "status": "ABORT_NOT_ENOUGH_SIGNALS", **payload}, indent=2),
    encoding="utf-8",
)

lines = [
    f"# Level 4 demo handoff — {now}",
    "",
    "Account: MetaQuotes-Demo. Magic 771249: **flat**. Foreign Client CADCHF not touched.",
    "",
    "## Batch29 comment L5e — ABORTED (not enough signals)",
    "No orders. Eligible after L5a–L5d forbids + CHFJPY/EURCHF/GBPCHF skip: EURCNH SELL only.",
    "NZDCAD/NZDCHF had FIRE but broker volume_min=0.1 (cannot open 0.01).",
    "L5d cycle 20260922T132125Z left scored; not rescored.",
    "",
    "| Symbol | Dir | Ticket | Entry | Stop | Exit | Net pts | Close path | Flat |",
    "|---|---|---:|---:|---:|---:|---:|---|---|",
    "| — | — | ABORT | - | - | - | - | no_open | yes |",
    "",
    "## Next wake",
    "1. Continue when board has five NEW eligible closed-bar signals, or stop on fresh STOP token after 09:27 NY.",
    "2. Do not activate H-20260922-002. Do not rescore 20260922T090923Z.",
    "",
]
HANDOFF.write_text("\n".join(lines), encoding="utf-8")
print("abort recorded", now)

"""Rewrite L4r runner from L4q template. Mentor stop gate must stay."""
from __future__ import annotations

from pathlib import Path

src = Path(r"C:\Users\C2K\Desktop\MT5 to agent\experiments\level4_demo_autonomy\2026-09-22_093347\run_batch15_l4q.py")
out = Path(r"C:\Users\C2K\Desktop\MT5 to agent\experiments\level4_demo_autonomy\2026-09-22_093347\run_batch16_l4r.py")
text = src.read_text(encoding="utf-8")
# Do NOT strip block_if_mentor_says_stop — prior emitter removed it and let L4r open ungated.
GATE_IMPORT = "from mentor_preflight import block_if_mentor_says_stop, log_plan_vs_board\n"
GATE_CALL = "    if block_if_mentor_says_stop(SCRIPT):\n        return 0\n"
if GATE_IMPORT not in text:
    text = text.replace(
        "from mentor_preflight import log_plan_vs_board\n",
        GATE_IMPORT,
    )
if GATE_IMPORT not in text:
    raise SystemExit("mentor gate import missing in source template")
if GATE_CALL not in text:
    raise SystemExit("block_if_mentor_says_stop call missing in source template")
repls = [
    ("batch15 L4q", "batch16 L4r"),
    ("L4q m771249", "L4r m771249"),
    ("L4q close", "L4r close"),
    ('"L4q"', '"L4r"'),
    ("our_L4q_left", "our_L4r_left"),
    ("Batch15 Level4 L4q", "Batch16 Level4 L4r"),
    ("Level4 batch15", "Level4 batch16"),
    ("batch15_complete", "batch16_complete"),
    ("## Batch15", "## Batch16"),
    ("comment L4q", "comment L4r"),
    ("_picks15.json", "_picks16.json"),
    ("batch15_signals.json", "batch16_signals.json"),
    ("batch15_jobs.json", "batch16_jobs.json"),
    ("batch15_results.json", "batch16_results.json"),
]
for a, b in repls:
    text = text.replace(a, b)

old_forbid = """FORBID = {
    (\"EURUSD\", \"SELL\"),
    (\"GBPUSD\", \"SELL\"),
    (\"USDCAD\", \"BUY\"),
    (\"GBPCHF\", \"SELL\"),
    (\"GBPJPY\", \"SELL\"),
}"""
new_forbid = """FORBID = {
    (\"AUDUSD\", \"SELL\"),
    (\"EURGBP\", \"BUY\"),
    (\"AUDJPY\", \"BUY\"),
    (\"GBPCAD\", \"BUY\"),
    (\"CADJPY\", \"SELL\"),
}"""
if old_forbid not in text:
    raise SystemExit("forbid block not found")
text = text.replace(old_forbid, new_forbid)
if GATE_IMPORT not in text or GATE_CALL not in text:
    raise SystemExit("mentor gate must remain after rewrite")
if "mt5.initialize" in text:
    gate_pos = text.find(GATE_CALL)
    init_pos = text.find("mt5.initialize")
    if gate_pos < 0 or init_pos < 0 or gate_pos > init_pos:
        raise SystemExit("block_if_mentor_says_stop must appear before mt5.initialize")
out.write_text(text, encoding="utf-8")
print(
    "ok",
    "L4r m771249" in text,
    "AUDUSD" in text and ('"AUDUSD", "SELL"' in text or "(\"AUDUSD\", \"SELL\")" in text),
    "block_if_mentor_says_stop" in text,
)

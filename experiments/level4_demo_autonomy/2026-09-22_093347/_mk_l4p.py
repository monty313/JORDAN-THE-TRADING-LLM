"""Rewrite L4p runner from L4n template. Mentor stop gate must stay."""
from __future__ import annotations

from pathlib import Path

src = Path(r"C:\Users\C2K\Desktop\MT5 to agent\experiments\level4_demo_autonomy\2026-09-22_093347\run_batch13_l4n.py")
out = Path(r"C:\Users\C2K\Desktop\MT5 to agent\experiments\level4_demo_autonomy\2026-09-22_093347\run_batch14_l4p.py")
text = src.read_text(encoding="utf-8")
# Do NOT strip block_if_mentor_says_stop.
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
    ("batch13 L4n", "batch14 L4p"),
    ("L4n m771249", "L4p m771249"),
    ("L4n close", "L4p close"),
    ('"L4n"', '"L4p"'),
    ("our_L4n_left", "our_L4p_left"),
    ("Batch13 Level4 L4n", "Batch14 Level4 L4p"),
    ("Level4 batch13", "Level4 batch14"),
    ("batch13_complete", "batch14_complete"),
    ("## Batch13", "## Batch14"),
    ("comment L4n", "comment L4p"),
    ("_picks13.json", "_picks14.json"),
    ("batch13_signals.json", "batch14_signals.json"),
    ("batch13_jobs.json", "batch14_jobs.json"),
    ("batch13_results.json", "batch14_results.json"),
]
for a, b in repls:
    text = text.replace(a, b)

# L4n template still has L4m-forbid; replace that block with L4n pairs as forbid for L4p
old_forbid = """FORBID = {
    (\"EURCHF\", \"SELL\"),
    (\"GBPCHF\", \"SELL\"),
    (\"GBPAUD\", \"SELL\"),
    (\"USDCAD\", \"BUY\"),
    (\"GBPUSD\", \"SELL\"),
}"""
new_forbid = """FORBID = {
    (\"AUDUSD\", \"SELL\"),
    (\"EURGBP\", \"BUY\"),
    (\"USDJPY\", \"SELL\"),
    (\"GBPCAD\", \"BUY\"),
    (\"EURCNH\", \"SELL\"),
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
    "L4p m771249" in text,
    "AUDUSD" in text and ("AUDUSD\", \"SELL\")" in text),
    "block_if_mentor" in text,
    "log_plan_vs_board" in text,
)

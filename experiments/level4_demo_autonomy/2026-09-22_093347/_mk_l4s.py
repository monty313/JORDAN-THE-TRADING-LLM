"""Rewrite L4s runner from L4r template. Mentor stop gate must stay."""
from __future__ import annotations

from pathlib import Path

src = Path(r"C:\Users\C2K\Desktop\MT5 to agent\experiments\level4_demo_autonomy\2026-09-22_093347\run_batch16_l4r.py")
out = Path(r"C:\Users\C2K\Desktop\MT5 to agent\experiments\level4_demo_autonomy\2026-09-22_093347\run_batch17_l4s.py")
text = src.read_text(encoding="utf-8")
# Do NOT strip block_if_mentor_says_stop — prior emitter removed it and let L4s open ungated.
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
    ("batch16 L4r", "batch17 L4s"),
    ("L4r m771249", "L4s m771249"),
    ("L4r close", "L4s close"),
    ('"L4r"', '"L4s"'),
    ("our_L4r_left", "our_L4s_left"),
    ("Batch16 Level4 L4r", "Batch17 Level4 L4s"),
    ("Level4 batch16", "Level4 batch17"),
    ("batch16_complete", "batch17_complete"),
    ("## Batch16", "## Batch17"),
    ("comment L4r", "comment L4s"),
    ("_picks16.json", "_picks17.json"),
    ("batch16_signals.json", "batch17_signals.json"),
    ("batch16_jobs.json", "batch17_jobs.json"),
    ("batch16_results.json", "batch17_results.json"),
]
for a, b in repls:
    text = text.replace(a, b)

old_forbid = """FORBID = {
    (\"AUDUSD\", \"SELL\"),
    (\"EURGBP\", \"BUY\"),
    (\"AUDJPY\", \"BUY\"),
    (\"GBPCAD\", \"BUY\"),
    (\"CADJPY\", \"SELL\"),
}"""
new_forbid = """FORBID = {
    (\"EURUSD\", \"SELL\"),
    (\"GBPUSD\", \"SELL\"),
    (\"USDCAD\", \"BUY\"),
    (\"GBPCHF\", \"SELL\"),
    (\"EURNZD\", \"BUY\"),
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
    "L4s m771249" in text,
    "EURUSD" in text and ('"EURUSD", "SELL"' in text or "(\"EURUSD\", \"SELL\")" in text),
    "block_if_mentor_says_stop" in text,
)

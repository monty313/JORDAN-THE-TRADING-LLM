"""Rewrite L4n runner from L4m template. Mentor stop gate must stay."""
from __future__ import annotations

from pathlib import Path

src = Path(r"C:\Users\C2K\Desktop\MT5 to agent\experiments\level4_demo_autonomy\2026-09-22_093347\run_batch12_l4m.py")
out = Path(r"C:\Users\C2K\Desktop\MT5 to agent\experiments\level4_demo_autonomy\2026-09-22_093347\run_batch13_l4n.py")
text = src.read_text(encoding="utf-8")
# Do NOT strip block_if_mentor_says_stop or SCRIPT — previous emitter did.
GATE_IMPORT_A = "from mentor_preflight import block_if_mentor_says_stop, log_plan_vs_board\n"
GATE_IMPORT_B = "from mentor_preflight import block_if_mentor_says_stop\n"
GATE_CALL = "    if block_if_mentor_says_stop(SCRIPT):\n        return 0\n"
if GATE_IMPORT_A not in text and GATE_IMPORT_B not in text:
    raise SystemExit("mentor gate import missing in source template")
if "SCRIPT = Path(__file__).name\n" not in text:
    raise SystemExit("SCRIPT name missing in source template")
if GATE_CALL not in text:
    raise SystemExit("block_if_mentor_says_stop call missing in source template")
repls = [
    ("batch12 L4m", "batch13 L4n"),
    ("L4m m771249", "L4n m771249"),
    ("L4m close", "L4n close"),
    ('"L4m"', '"L4n"'),
    ("our_L4m_left", "our_L4n_left"),
    ("Batch12 Level4 L4m", "Batch13 Level4 L4n"),
    ("Level4 batch12", "Level4 batch13"),
    ("batch12_complete", "batch13_complete"),
    ("## Batch12", "## Batch13"),
    ("comment L4m", "comment L4n"),
    ("_picks12.json", "_picks13.json"),
    ("batch12_signals.json", "batch13_signals.json"),
    ("batch12_jobs.json", "batch13_jobs.json"),
    ("batch12_results.json", "batch13_results.json"),
]
for a, b in repls:
    text = text.replace(a, b)

old_forbid = """FORBID = {
    (\"AUDJPY\", \"BUY\"),
    (\"USDSEK\", \"SELL\"),
    (\"AUDUSD\", \"SELL\"),
    (\"EURGBP\", \"BUY\"),
    (\"EURUSD\", \"SELL\"),
}"""
new_forbid = """FORBID = {
    (\"EURCHF\", \"SELL\"),
    (\"GBPCHF\", \"SELL\"),
    (\"GBPAUD\", \"SELL\"),
    (\"USDCAD\", \"BUY\"),
    (\"GBPUSD\", \"SELL\"),
}"""
if old_forbid not in text:
    raise SystemExit("forbid block not found")
text = text.replace(old_forbid, new_forbid)
if GATE_CALL not in text or "SCRIPT = Path(__file__).name\n" not in text:
    raise SystemExit("mentor gate must remain after rewrite")
if "mt5.initialize" in text:
    gate_pos = text.find(GATE_CALL)
    init_pos = text.find("mt5.initialize")
    if gate_pos < 0 or init_pos < 0 or gate_pos > init_pos:
        raise SystemExit("block_if_mentor_says_stop must appear before mt5.initialize")
out.write_text(text, encoding="utf-8")
print("ok", "mentor_preflight" in text, "L4n m771249" in text, "EURCHF" in text, "block_if_mentor" in text)

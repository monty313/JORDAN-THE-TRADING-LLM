"""Build L5k forced runner from L5j; soft-avoid L5j pairs; mix dirs.

KEEP mentor_preflight stop check before mt5.initialize.
Do not replace block_if_mentor_says_stop with a fresh-token-only gate.
"""
from __future__ import annotations

from pathlib import Path

src = Path(r"C:\Users\C2K\Desktop\MT5 to agent\experiments\level4_demo_autonomy\2026-09-22_093347\run_batch34_l5j_forced.py")
out = Path(r"C:\Users\C2K\Desktop\MT5 to agent\experiments\level4_demo_autonomy\2026-09-22_093347\run_batch35_l5k_forced.py")
text = src.read_text(encoding="utf-8")

if "block_if_mentor_says_stop" not in text:
    raise SystemExit("mentor_preflight missing in source — abort")
if "if block_if_mentor_says_stop(SCRIPT):" not in text:
    needle = "def main() -> int:\n"
    insert = (
        "def main() -> int:\n"
        "    if block_if_mentor_says_stop(SCRIPT):\n"
        "        return 0\n\n"
    )
    if needle not in text:
        raise SystemExit("main() not found")
    text = text.replace(needle, insert, 1)

if "block_if_fresh_stop_token" in text or "stop_token_gate" in text:
    raise SystemExit("token-only gate not allowed — keep mentor stop")

repls = [
    ("batch34 L5j", "batch35 L5k"),
    ("L5j m771249", "L5k m771249"),
    ("L5j close", "L5k close"),
    ('"L5j"', '"L5k"'),
    ("our_L5j_left", "our_L5k_left"),
    ("_picks34.json", "_picks35.json"),
    ("batch34_signals.json", "batch35_signals.json"),
    ("batch34_jobs.json", "batch35_jobs.json"),
    ("batch34_results.json", "batch35_results.json"),
    ("batch34_l5j_held_closed", "batch35_l5k_held_closed"),
    ("level4-demo-forced-five-l5j", "level4-demo-forced-five-l5k"),
    ("L5j forced five", "L5k forced five"),
    ("forced_five_l5j", "forced_five_l5k"),
    ("soft_avoid_l5i", "soft_avoid_l5j"),
    ("Soft-avoid L5i pairs", "Soft-avoid L5j pairs"),
]
for a, b in repls:
    text = text.replace(a, b)

old = """SOFT_AVOID = {
    (\"USDJPY\", \"BUY\"),
    (\"EURAUD\", \"SELL\"),
    (\"AUDJPY\", \"BUY\"),
    (\"EURCHF\", \"SELL\"),
    (\"EURJPY\", \"SELL\"),
}"""
new = """SOFT_AVOID = {
    (\"EURUSD\", \"SELL\"),
    (\"NZDUSD\", \"BUY\"),
    (\"EURGBP\", \"SELL\"),
    (\"USDCAD\", \"BUY\"),
    (\"AUDUSD\", \"BUY\"),
}"""
if old not in text:
    raise SystemExit("soft avoid not found")
text = text.replace(old, new)

if "REPEAT_SELL_SOFT" not in text:
    raise SystemExit("REPEAT_SELL_SOFT missing — direction mix broken")

if "block_if_mentor_says_stop" not in text:
    raise SystemExit("mentor stop missing")
if "if block_if_mentor_says_stop(SCRIPT):" not in text:
    raise SystemExit("mentor stop call missing")
if "block_if_fresh_stop_token" in text or "stop_token_gate" in text:
    raise SystemExit("token-only gate leaked")
if "L5k m771249" not in text:
    raise SystemExit("L5k comment missing")

out.write_text(text, encoding="utf-8")
print("ok", '("EURUSD", "SELL")' in text or '(\"EURUSD\", \"SELL\")' in text)

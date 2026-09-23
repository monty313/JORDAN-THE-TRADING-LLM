"""Build L5i forced runner from L5h; soft-avoid L5h pairs; mix dirs.

KEEP mentor_preflight stop check before mt5.initialize.
Do not replace block_if_mentor_says_stop with a fresh-token-only gate.
"""
from __future__ import annotations

from pathlib import Path

src = Path(r"C:\Users\C2K\Desktop\MT5 to agent\experiments\level4_demo_autonomy\2026-09-22_093347\run_batch32_l5h_forced.py")
out = Path(r"C:\Users\C2K\Desktop\MT5 to agent\experiments\level4_demo_autonomy\2026-09-22_093347\run_batch33_l5i_forced.py")
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
    ("batch32 L5h", "batch33 L5i"),
    ("L5h m771249", "L5i m771249"),
    ("L5h close", "L5i close"),
    ('"L5h"', '"L5i"'),
    ("our_L5h_left", "our_L5i_left"),
    ("_picks32.json", "_picks33.json"),
    ("batch32_signals.json", "batch33_signals.json"),
    ("batch32_jobs.json", "batch33_jobs.json"),
    ("batch32_results.json", "batch33_results.json"),
    ("batch32_l5h_held_closed", "batch33_l5i_held_closed"),
    ("level4-demo-forced-five-l5h", "level4-demo-forced-five-l5i"),
    ("L5h forced five", "L5i forced five"),
    ("forced_five_l5h", "forced_five_l5i"),
    ("soft_avoid_l5g", "soft_avoid_l5h"),
    ("Soft-avoid L5g pairs", "Soft-avoid L5h pairs"),
]
for a, b in repls:
    text = text.replace(a, b)

old = """SOFT_AVOID = {
    (\"EURCHF\", \"SELL\"),
    (\"EURJPY\", \"SELL\"),
    (\"GBPUSD\", \"SELL\"),
    (\"NZDUSD\", \"SELL\"),
    (\"AUDUSD\", \"SELL\"),
}"""
new = """SOFT_AVOID = {
    (\"EURCAD\", \"BUY\"),
    (\"EURGBP\", \"SELL\"),
    (\"EURUSD\", \"SELL\"),
    (\"USDCAD\", \"BUY\"),
    (\"USDCHF\", \"BUY\"),
}"""
if old not in text:
    raise SystemExit("soft avoid not found")
text = text.replace(old, new)

# Ensure REPEAT_SELL_SOFT still present for GBPUSD/NZDUSD/AUDUSD SELL
if "REPEAT_SELL_SOFT" not in text:
    raise SystemExit("REPEAT_SELL_SOFT missing — direction mix broken")

if "block_if_mentor_says_stop" not in text:
    raise SystemExit("mentor stop missing")
if "if block_if_mentor_says_stop(SCRIPT):" not in text:
    raise SystemExit("mentor stop call missing")
if "block_if_fresh_stop_token" in text or "stop_token_gate" in text:
    raise SystemExit("token-only gate leaked")
if "L5i m771249" not in text:
    raise SystemExit("L5i comment missing")

out.write_text(text, encoding="utf-8")
print("ok", '("EURCAD", "BUY")' in text or '(\"EURCAD\", \"BUY\")' in text)

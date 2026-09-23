"""Build L5g forced runner from L5f forced; soft-avoid L5f pairs.

KEEP mentor_preflight stop check before mt5.initialize.
Do not replace block_if_mentor_says_stop with a fresh-token-only gate.
"""
from __future__ import annotations

from pathlib import Path

src = Path(r"C:\Users\C2K\Desktop\MT5 to agent\experiments\level4_demo_autonomy\2026-09-22_093347\run_batch30_l5f_forced.py")
out = Path(r"C:\Users\C2K\Desktop\MT5 to agent\experiments\level4_demo_autonomy\2026-09-22_093347\run_batch31_l5g_forced.py")
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
    ("batch30 L5f", "batch31 L5g"),
    ("L5f m771249", "L5g m771249"),
    ("L5f close", "L5g close"),
    ('"L5f"', '"L5g"'),
    ("our_L5f_left", "our_L5g_left"),
    ("_picks30.json", "_picks31.json"),
    ("batch30_signals.json", "batch31_signals.json"),
    ("batch30_jobs.json", "batch31_jobs.json"),
    ("batch30_results.json", "batch31_results.json"),
    ("batch30_l5f_held_closed", "batch31_l5g_held_closed"),
    ("level4-demo-forced-five-l5f", "level4-demo-forced-five-l5g"),
    ("L5f forced five", "L5g forced five"),
    ("forced_five_l5f", "forced_five_l5g"),
    ("soft_avoid_l5e", "soft_avoid_l5f"),
]
for a, b in repls:
    text = text.replace(a, b)

old = """SOFT_AVOID = {
    (\"GBPUSD\", \"SELL\"),
    (\"NZDUSD\", \"SELL\"),
    (\"AUDUSD\", \"SELL\"),
    (\"EURCAD\", \"BUY\"),
    (\"EURCHF\", \"BUY\"),
}"""
new = """SOFT_AVOID = {
    (\"EURUSD\", \"SELL\"),
    (\"USDCAD\", \"BUY\"),
    (\"EURGBP\", \"SELL\"),
    (\"GBPCHF\", \"BUY\"),
    (\"USDCHF\", \"BUY\"),
}"""
if old not in text:
    raise SystemExit("soft avoid not found")
text = text.replace(old, new)

if "L5g m771249" not in text:
    raise SystemExit("L5g comment missing")
if "block_if_mentor_says_stop" not in text:
    raise SystemExit("mentor stop stripped — abort write")
if "block_if_fresh_stop_token" in text or "stop_token_gate" in text:
    raise SystemExit("token-only gate not allowed — abort write")
out.write_text(text, encoding="utf-8")
print("ok", '("EURUSD", "SELL")' in text or '(\"EURUSD\", \"SELL\")' in text)

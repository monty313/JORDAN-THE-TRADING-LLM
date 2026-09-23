"""Build L5f forced runner from L5e forced; soft-avoid L5e pairs.

KEEP mentor_preflight stop check before mt5.initialize.
Do not replace block_if_mentor_says_stop with a fresh-token-only gate.
"""
from __future__ import annotations

from pathlib import Path

src = Path(r"C:\Users\C2K\Desktop\MT5 to agent\experiments\level4_demo_autonomy\2026-09-22_093347\run_batch29_l5e_forced.py")
out = Path(r"C:\Users\C2K\Desktop\MT5 to agent\experiments\level4_demo_autonomy\2026-09-22_093347\run_batch30_l5f_forced.py")
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
    ("batch29 L5e", "batch30 L5f"),
    ("L5e m771249", "L5f m771249"),
    ("L5e close", "L5f close"),
    ('"L5e"', '"L5f"'),
    ("our_L5e_left", "our_L5f_left"),
    ("_picks29.json", "_picks30.json"),
    ("batch29_signals.json", "batch30_signals.json"),
    ("batch29_jobs.json", "batch30_jobs.json"),
    ("batch29_results.json", "batch30_results.json"),
    ("batch29_l5e_held_closed", "batch30_l5f_held_closed"),
    ("level4-demo-forced-five-l5e", "level4-demo-forced-five-l5f"),
    ("prior L5e abort overridden", "L5f forced five"),
    ("forced_five_override_abort", "forced_five_l5f"),
    ("soft_avoid_l5d", "soft_avoid_l5e"),
]
for a, b in repls:
    text = text.replace(a, b)

old = """SOFT_AVOID = {
    (\"USDCAD\", \"BUY\"),
    (\"GBPAUD\", \"BUY\"),
    (\"EURUSD\", \"SELL\"),
    (\"USDJPY\", \"BUY\"),
    (\"AUDJPY\", \"BUY\"),
}"""
new = """SOFT_AVOID = {
    (\"GBPUSD\", \"SELL\"),
    (\"NZDUSD\", \"SELL\"),
    (\"AUDUSD\", \"SELL\"),
    (\"EURCAD\", \"BUY\"),
    (\"EURCHF\", \"BUY\"),
}"""
if old not in text:
    raise SystemExit("soft avoid not found")
text = text.replace(old, new)

if "L5f m771249" not in text:
    raise SystemExit("L5f comment missing")
if "block_if_mentor_says_stop" not in text:
    raise SystemExit("mentor stop stripped — abort write")
if "block_if_fresh_stop_token" in text or "stop_token_gate" in text:
    raise SystemExit("token-only gate not allowed — abort write")
out.write_text(text, encoding="utf-8")
print("ok", '("GBPUSD", "SELL")' in text or '(\"GBPUSD\", \"SELL\")' in text)

"""Build L5j forced runner from L5i; soft-avoid L5i pairs; mix dirs.

KEEP mentor_preflight stop check before mt5.initialize.
Do not replace block_if_mentor_says_stop with a fresh-token-only gate.
"""
from __future__ import annotations

from pathlib import Path

src = Path(r"C:\Users\C2K\Desktop\MT5 to agent\experiments\level4_demo_autonomy\2026-09-22_093347\run_batch33_l5i_forced.py")
out = Path(r"C:\Users\C2K\Desktop\MT5 to agent\experiments\level4_demo_autonomy\2026-09-22_093347\run_batch34_l5j_forced.py")
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
    ("batch33 L5i", "batch34 L5j"),
    ("L5i m771249", "L5j m771249"),
    ("L5i close", "L5j close"),
    ('"L5i"', '"L5j"'),
    ("our_L5i_left", "our_L5j_left"),
    ("_picks33.json", "_picks34.json"),
    ("batch33_signals.json", "batch34_signals.json"),
    ("batch33_jobs.json", "batch34_jobs.json"),
    ("batch33_results.json", "batch34_results.json"),
    ("batch33_l5i_held_closed", "batch34_l5j_held_closed"),
    ("level4-demo-forced-five-l5i", "level4-demo-forced-five-l5j"),
    ("L5i forced five", "L5j forced five"),
    ("forced_five_l5i", "forced_five_l5j"),
    ("soft_avoid_l5h", "soft_avoid_l5i"),
    ("Soft-avoid L5h pairs", "Soft-avoid L5i pairs"),
]
for a, b in repls:
    text = text.replace(a, b)

old = """SOFT_AVOID = {
    (\"EURCAD\", \"BUY\"),
    (\"EURGBP\", \"SELL\"),
    (\"EURUSD\", \"SELL\"),
    (\"USDCAD\", \"BUY\"),
    (\"USDCHF\", \"BUY\"),
}"""
new = """SOFT_AVOID = {
    (\"USDJPY\", \"BUY\"),
    (\"EURAUD\", \"SELL\"),
    (\"AUDJPY\", \"BUY\"),
    (\"EURCHF\", \"SELL\"),
    (\"EURJPY\", \"SELL\"),
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
if "L5j m771249" not in text:
    raise SystemExit("L5j comment missing")

out.write_text(text, encoding="utf-8")
print("ok", '("USDJPY", "BUY")' in text or '(\"USDJPY\", \"BUY\")' in text)

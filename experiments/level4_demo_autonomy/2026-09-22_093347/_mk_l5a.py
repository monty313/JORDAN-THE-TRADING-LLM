"""Build L5a from L4z; KEEP mentor_preflight stop check before mt5.initialize.

Do not replace block_if_mentor_says_stop with a fresh-token-only gate.
Stale MENTOR_INBOX "send nothing" still blocks. Forbid L4z pairs.
"""
from __future__ import annotations

from pathlib import Path

src = Path(r"C:\Users\C2K\Desktop\MT5 to agent\experiments\level4_demo_autonomy\2026-09-22_093347\run_batch24_l4z.py")
out = Path(r"C:\Users\C2K\Desktop\MT5 to agent\experiments\level4_demo_autonomy\2026-09-22_093347\run_batch25_l5a.py")
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

# Refuse any rewrite that strips the mentor gate or swaps in token-only gate
if "block_if_fresh_stop_token" in text or "stop_token_gate" in text:
    raise SystemExit("token-only gate not allowed — keep mentor stop")

repls = [
    ("batch24 L4z", "batch25 L5a"),
    ("L4z m771249", "L5a m771249"),
    ("L4z close", "L5a close"),
    ('"L4z"', '"L5a"'),
    ("our_L4z_left", "our_L5a_left"),
    ("Batch24 Level4 L4z", "Batch25 Level4 L5a"),
    ("Level4 batch24", "Level4 batch25"),
    ("batch24_complete", "batch25_complete"),
    ("## Batch24", "## Batch25"),
    ("comment L4z", "comment L5a"),
    ("_picks24.json", "_picks25.json"),
    ("batch24_signals.json", "batch25_signals.json"),
    ("batch24_jobs.json", "batch25_jobs.json"),
    ("batch24_results.json", "batch25_results.json"),
]
for a, b in repls:
    text = text.replace(a, b)

old_forbid = """FORBID = {
    (\"USDCHF\", \"SELL\"),
    (\"EURCHF\", \"SELL\"),
    (\"EURAUD\", \"BUY\"),
    (\"GBPCHF\", \"SELL\"),
    (\"GBPCAD\", \"BUY\"),
}"""
new_forbid = """FORBID = {
    (\"EURUSD\", \"SELL\"),
    (\"EURGBP\", \"SELL\"),
    (\"USDCAD\", \"BUY\"),
    (\"CHFJPY\", \"BUY\"),
    (\"GBPJPY\", \"BUY\"),
}"""
if old_forbid not in text:
    raise SystemExit("forbid block not found: " + repr(text[text.find("FORBID"):text.find("FORBID")+200]))
text = text.replace(old_forbid, new_forbid)

text = text.replace('and "L4z" in (p.comment or "")', 'and "L5a" in (p.comment or "")')
text = text.replace('"L4z" in (p.get("comment") or "")', '"L5a" in (p.get("comment") or "")')

if "block_if_mentor_says_stop" not in text:
    raise SystemExit("mentor stop stripped — abort write")
if "if block_if_mentor_says_stop(SCRIPT):" not in text:
    raise SystemExit("mentor stop call missing — abort write")

out.write_text(text, encoding="utf-8")
print(
    "ok",
    "L5a m771249" in text,
    "block_if_mentor_says_stop" in text,
    "if block_if_mentor_says_stop(SCRIPT)" in text,
    "block_if_fresh_stop_token" not in text,
    '("EURUSD", "SELL")' in text or '(\"EURUSD\", \"SELL\")' in text,
)

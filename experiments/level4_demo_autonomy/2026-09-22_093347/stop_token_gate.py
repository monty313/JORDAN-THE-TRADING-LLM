"""Gate: refuse new orders only on FRESH STOP tokens after the active cutoff NY time.

Old MENTOR_INBOX "Send nothing" / "Stop stays 0" lines do not count.
"""
from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

EXP = Path(__file__).resolve().parent
MENTOR_INBOX = Path(r"C:\Users\C2K\Desktop\MT5 to agent\JARVIS V1\MENTOR_INBOX.md")
TAPE = EXP / "demo_trade_tape.jsonl"

# Mark: L4x — only refuse if STOP tokens appear after 08:36 America/New_York 2026-09-22
CUTOFF = datetime(2026, 9, 22, 12, 0, 0, tzinfo=ZoneInfo("America/New_York"))
STOP_TOKENS = ("STOP_LEVEL_4_DEMO_AUTONOMY", "STOP_FORCED_SIGNAL_LOOP")
_HEADING = re.compile(
    r"^##\s+(\d{4}-\d{2}-\d{2})\s+(\d{1,2}:\d{2})(?:\s+America/New_York)?\s*$"
)


def _log(script_name: str, reason: str, extra: dict | None = None) -> None:
    obj = {"event": "preflight_block", "reason": reason, "script": script_name}
    if extra:
        obj.update(extra)
    line = json.dumps(obj, separators=(",", ":"))
    with TAPE.open("a", encoding="utf-8", newline="\n") as f:
        f.write(line + "\n")
    print(line, flush=True)


def block_if_fresh_stop_token(script_name: str) -> bool:
    """Return True (BLOCK) if Mark's sentinel file exists, or a post-cutoff STOP token is in the inbox."""
    sentinel = EXP / "STOP_FORCED_SIGNAL_LOOP"
    if sentinel.is_file():
        _log(script_name, "sentinel_file", {"path": sentinel.name})
        # #region agent log
        try:
            import time as _t
            _p = Path(r"C:\Users\C2K\Desktop\MT5 to agent\debug-f9c85a.log")
            with _p.open("a", encoding="utf-8") as _f:
                _f.write(json.dumps({"sessionId":"f9c85a","hypothesisId":"B","location":"stop_token_gate.py:sentinel","message":"block on sentinel file","data":{"script":script_name,"cutoff":CUTOFF.isoformat()},"timestamp":int(_t.time()*1000)}) + "\n")
        except OSError:
            pass
        # #endregion
        return True
    if not MENTOR_INBOX.is_file():
        # Missing inbox is not a STOP token; allow continue per Mark's L4v clarification.
        return False
    try:
        text = MENTOR_INBOX.read_text(encoding="utf-8")
    except OSError:
        return False

    lines = text.splitlines()
    i = 0
    while i < len(lines):
        m = _HEADING.match(lines[i].strip())
        if not m:
            i += 1
            continue
        date_s, time_s = m.group(1), m.group(2)
        try:
            hh, mm = time_s.split(":")
            section_dt = datetime(
                int(date_s[:4]),
                int(date_s[5:7]),
                int(date_s[8:10]),
                int(hh),
                int(mm),
                tzinfo=ZoneInfo("America/New_York"),
            )
        except ValueError:
            i += 1
            continue
        j = i + 1
        while j < len(lines) and not lines[j].startswith("## "):
            j += 1
        body = "\n".join(lines[i:j])
        if section_dt > CUTOFF and any(tok in body for tok in STOP_TOKENS):
            _log(
                script_name,
                "fresh_stop_token",
                {"section_ny": section_dt.isoformat(), "tokens": [t for t in STOP_TOKENS if t in body]},
            )
            # #region agent log
            try:
                import time as _t
                _p = Path(r"C:\Users\C2K\Desktop\MT5 to agent\debug-f9c85a.log")
                with _p.open("a", encoding="utf-8") as _f:
                    _f.write(json.dumps({"sessionId":"f9c85a","hypothesisId":"A","location":"stop_token_gate.py:token","message":"block on fresh inbox token","data":{"script":script_name,"section":section_dt.isoformat()},"timestamp":int(_t.time()*1000)}) + "\n")
            except OSError:
                pass
            # #endregion
            return True
        i = j
    # #region agent log
    try:
        import time as _t
        _p = Path(r"C:\Users\C2K\Desktop\MT5 to agent\debug-f9c85a.log")
        with _p.open("a", encoding="utf-8") as _f:
            _f.write(json.dumps({"sessionId":"f9c85a","hypothesisId":"C","location":"stop_token_gate.py:allow","message":"gate allowed","data":{"script":script_name,"cutoff":CUTOFF.isoformat()},"timestamp":int(_t.time()*1000)}) + "\n")
    except OSError:
        pass
    # #endregion
    return False

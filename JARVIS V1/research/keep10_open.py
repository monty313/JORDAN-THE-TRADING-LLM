"""Demo opener for magic 771249.

An order is unreachable until a complete thesis is appended, fsynced,
reread, and matched. Live MetaTrader sends stay off. --selftest uses a
fake broker and does not import MetaTrader5.
"""

from __future__ import annotations

import hashlib
import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path

MAGIC = 771249
DOCTRINE_VERSION = "007-v1.0"
KEEP10_EXECUTION_ENABLED = False
BOARD = Path(
    r"C:\Users\C2K\AppData\Roaming\MetaQuotes\Terminal\D0E8209F77C8CF37AD8BF550E51FF075\MQL5\Files\jarvis\board.csv"
)
THESIS_PATH = Path(__file__).with_name("pre_trade_thesis.jsonl")
ERROR_LEDGER = Path(__file__).with_name("pre_trade_errors.jsonl")
COMMENT_LIMIT = 31
LIVE_ORDER_CALLS = 0

REQUIRED = (
    "run_id",
    "signal_id",
    "magic_number",
    "symbol",
    "direction",
    "strategy_id",
    "set_id",
    "anchor_tf",
    "htf1",
    "htf2",
    "topology",
    "tide",
    "regime",
    "official_act",
    "entry_bid",
    "entry_ask",
    "spread_points",
    "structural_stop_price",
    "structural_kill_relation",
    "risk_dollars",
    "risk_percent",
    "maximum_duration_minutes",
    "doctrine_version",
    "config_hash",
    "timestamp_utc",
    "release_bar_time",
    "current_closed_bar_time",
)


def _blank(value) -> bool:
    if value is None:
        return True
    if isinstance(value, bool):
        return False
    if isinstance(value, (int, float)):
        return False
    return str(value).strip() == ""


def _positive(value) -> bool:
    try:
        return float(value) > 0
    except (TypeError, ValueError):
        return False


def thesis_hash(record: dict) -> str:
    body = {
        key: record.get(key)
        for key in (
            "run_id",
            "signal_id",
            "magic_number",
            "symbol",
            "direction",
            "strategy_id",
            "set_id",
            "anchor_tf",
            "htf1",
            "htf2",
            "tide",
            "regime",
            "topology",
            "official_act",
            "emerged",
            "structural_stop_price",
            "structural_kill_relation",
            "risk_dollars",
            "risk_percent",
            "maximum_duration_minutes",
            "doctrine_version",
            "config_hash",
            "entry_bid",
            "entry_ask",
            "spread_points",
        )
    }
    payload = json.dumps(body, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def comment_for(record: dict) -> str:
    strategy = str(record.get("strategy_id") or "Sx")
    set_id = str(record.get("set_id") or "0")
    topo = "".join(ch for ch in str(record.get("topology") or "NONE").upper() if ch.isalnum())[:6]
    signal = str(record.get("signal_id") or "")[:8]
    return f"J|{strategy}|{set_id}|{topo}|{signal}"[:COMMENT_LIMIT]


def missing_fields(record: dict) -> list[str]:
    missing = [key for key in REQUIRED if _blank(record.get(key))]
    for key in ("entry_bid", "entry_ask", "structural_stop_price", "risk_dollars", "risk_percent", "maximum_duration_minutes"):
        if key not in missing and not _positive(record.get(key)):
            missing.append(key)
    if "spread_points" not in missing and record.get("spread_points") is None:
        missing.append("spread_points")
    topology = str(record.get("topology") or "").strip().lower()
    if topology in {"", "none", "n/a"} and "topology" not in missing:
        missing.append("topology")
    return missing


def classify(record: dict) -> str | None:
    """Return a refusal reason, or None when the record may be persisted."""
    if missing_fields(record):
        return "pre_trade_thesis_incomplete"
    if record.get("emerged") is True or record.get("need_samples") is True:
        return "emergence_not_execution_authority"
    if str(record.get("official_act") or "") == "WAIT_LOADED":
        return "emergence_not_execution_authority"
    if str(record.get("official_act") or "") not in {"FIRE_BUY", "FIRE_SELL"}:
        return "pre_trade_thesis_incomplete"
    strategy = str(record.get("strategy_id") or "")
    try:
        set_id = int(record.get("set_id"))
    except (TypeError, ValueError):
        set_id = 0
    owner = record.get("owner_strategy")
    if strategy not in {"S1", "S2", "S3", "S4"} or set_id not in {1, 2, 3, 4}:
        return "set_strategy_mismatch"
    if set_id not in {1, 2}:
        # #region agent log
        try:
            import json as _json
            import time as _time
            _log = Path(__file__).resolve().parents[2] / "debug-e25812.log"
            with _log.open("a", encoding="utf-8") as _handle:
                _handle.write(
                    _json.dumps(
                        {
                            "sessionId": "e25812",
                            "runId": "post-fix",
                            "hypothesisId": "F",
                            "location": "keep10_open.py:classify",
                            "message": "set 3-4 refused",
                            "data": {"set_id": set_id, "strategy_id": strategy},
                            "timestamp": int(_time.time() * 1000),
                        },
                        sort_keys=True,
                    )
                    + "\n"
                )
        except OSError:
            pass
        # #endregion
        return "set_3_4_context_only"
    if owner and str(owner) != strategy:
        return "set_strategy_mismatch"
    tide = str(record.get("tide") or "").strip().lower()
    side_1 = str(record.get("htf1_side") or "").strip().lower()
    side_2 = str(record.get("htf2_side") or "").strip().lower()
    if tide not in {"long_only", "short_only"} or side_1 != side_2 or side_1 not in {"long", "short"}:
        return "htf_force_conflict"
    if tide == "long_only" and side_1 != "long":
        return "htf_force_conflict"
    if tide == "short_only" and side_1 != "short":
        return "htf_force_conflict"
    regime = str(record.get("regime") or "").strip().lower()
    if regime in {"", "undefined"} or record.get("s5_present") is not True:
        return "regime_not_verified"
    if str(record.get("release_bar_time")) != str(record.get("current_closed_bar_time")):
        return "stale_release"
    return None


def _fsync_dir(directory: Path) -> bool:
    flags = os.O_RDONLY
    if hasattr(os, "O_DIRECTORY"):
        flags |= os.O_DIRECTORY
    try:
        fd = os.open(str(directory), flags)
    except OSError:
        return False
    try:
        os.fsync(fd)
    except OSError:
        return False
    finally:
        os.close(fd)
    return True


def durable_append(path: Path, record: dict) -> bool:
    """Append one JSON line, fsync the file, close it, then fsync the directory when the OS allows it."""
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(record, sort_keys=True, separators=(",", ":"), default=str) + "\n"
    fd = os.open(str(path), os.O_APPEND | os.O_CREAT | os.O_WRONLY)
    try:
        os.write(fd, line.encode("utf-8"))
        os.fsync(fd)
    finally:
        os.close(fd)
    _fsync_dir(path.parent)
    return True


def read_records(path: Path) -> list[dict]:
    if not path.exists():
        return []
    records = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        records.append(json.loads(line))
    return records


def note_error(ledger: Path, payload: dict) -> None:
    try:
        durable_append(ledger, payload)
    except OSError:
        return


def _known_signal(path: Path, signal_id: str) -> bool:
    try:
        rows = read_records(path)
    except (OSError, json.JSONDecodeError):
        return False
    return any(row.get("signal_id") == signal_id for row in rows)


def _wait(reason: str, **extra) -> dict:
    out = {"act": "WAIT_NO_TRADE", "reason": reason, "sent": False}
    out.update(extra)
    return out


def decide(record: dict, path: Path, broker, ledger: Path | None = None, append=durable_append) -> dict:
    """Persist and reread a thesis before the broker adapter is allowed to run."""
    ledger = ledger or path.with_name("pre_trade_errors.jsonl")
    reason = classify(record)
    if reason:
        return _wait(reason)
    signal_id = record["signal_id"]
    if _known_signal(path, signal_id):
        return _wait("duplicate_signal", signal_id=signal_id)

    stored = dict(record)
    stored["record_type"] = "pre_trade"
    stored["thesis_hash"] = thesis_hash(record)
    stored["broker_comment"] = comment_for(record)
    stored.pop("order_intent_id", None)
    try:
        append(path, stored)
        reread = read_records(path)[-1]
    except (OSError, json.JSONDecodeError, ValueError, IndexError) as exc:
        note_error(ledger, {"record_type": "write_error", "signal_id": signal_id, "error": str(exc)})
        return _wait("pre_trade_thesis_not_persisted", error=str(exc))

    checks = (
        "signal_id",
        "thesis_hash",
        "strategy_id",
        "set_id",
        "topology",
        "structural_stop_price",
        "risk_dollars",
    )
    if any(reread.get(key) != stored.get(key) for key in checks):
        note_error(ledger, {"record_type": "verify_error", "signal_id": signal_id})
        return _wait("pre_trade_thesis_not_persisted")

    intent_id = str(uuid.uuid4())
    intent = {
        "record_type": "order_intent",
        "signal_id": signal_id,
        "order_intent_id": intent_id,
        "thesis_hash": stored["thesis_hash"],
        "broker_comment": stored["broker_comment"],
    }
    try:
        append(path, intent)
        intents = [row for row in read_records(path) if row.get("record_type") == "order_intent" and row.get("signal_id") == signal_id]
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        note_error(ledger, {"record_type": "write_error", "signal_id": signal_id, "error": str(exc)})
        return _wait("pre_trade_thesis_not_persisted", error=str(exc))
    if len(intents) != 1 or intents[0].get("order_intent_id") != intent_id:
        return _wait("duplicate_signal", signal_id=signal_id)

    outcome = broker.send({**stored, "order_intent_id": intent_id})
    if not outcome or not outcome.get("ok"):
        rejection = {
            "record_type": "broker_rejection",
            "signal_id": signal_id,
            "order_intent_id": intent_id,
            "retcode": None if not outcome else outcome.get("retcode"),
        }
        try:
            append(path, rejection)
        except OSError as exc:
            note_error(ledger, {"record_type": "write_error", "signal_id": signal_id, "error": str(exc)})
        return _wait("broker_rejected", signal_id=signal_id, retcode=rejection["retcode"])
    return {
        "act": "SEND",
        "reason": "thesis_persisted",
        "sent": True,
        "signal_id": signal_id,
        "order_intent_id": intent_id,
        "thesis_hash": stored["thesis_hash"],
    }


class FakeBroker:
    """In-memory broker. It has no path to a live order function."""

    def __init__(self, reject: bool = False, retcode: int = 10016):
        self.reject = reject
        self.retcode = retcode
        self.calls = 0
        self.live_order_calls = 0
        self.seen = []

    def send(self, record: dict) -> dict:
        self.calls += 1
        self.seen.append(record)
        if self.reject:
            return {"ok": False, "retcode": self.retcode}
        return {"ok": True, "retcode": 10009}


def _complete(signal_id: str = "sig-complete") -> dict:
    return {
        "run_id": "gate-suite",
        "signal_id": signal_id,
        "magic_number": MAGIC,
        "symbol": "EURUSD",
        "direction": "BUY",
        "strategy_id": "S2",
        "set_id": 2,
        "anchor_tf": "M5",
        "htf1": "M30",
        "htf2": "H1",
        "htf1_side": "long",
        "htf2_side": "long",
        "tide": "long_only",
        "regime": "bull_trend",
        "topology": "bb_pullback_load",
        "official_act": "FIRE_BUY",
        "emerged": False,
        "need_samples": False,
        "s5_present": True,
        "entry_bid": 1.1,
        "entry_ask": 1.10002,
        "spread_points": 2,
        "structural_stop_price": 1.0990,
        "structural_kill_relation": "5m close back through SMA50",
        "take_profit_price": 0.0,
        "risk_dollars": 25.0,
        "risk_percent": 0.01,
        "maximum_duration_minutes": 15,
        "doctrine_version": DOCTRINE_VERSION,
        "config_hash": "abc123",
        "timestamp_utc": "2026-09-22T23:00:00+00:00",
        "release_bar_time": "2026-09-23T01:55:00",
        "current_closed_bar_time": "2026-09-23T01:55:00",
        "volume": 0.1,
    }


def run_gate_suite() -> None:
    import sys
    import tempfile

    if "MetaTrader5" in sys.modules:
        raise SystemExit("selftest imported MetaTrader5")
    root = Path(tempfile.mkdtemp(prefix="keep10-gate-"))
    results = []

    def fresh(name: str) -> tuple[Path, Path]:
        folder = root / name
        folder.mkdir()
        return folder / "pre_trade_thesis.jsonl", folder / "pre_trade_errors.jsonl"

    broker = FakeBroker()
    thesis, ledger = fresh("complete")
    positive = decide(_complete("sig-positive"), thesis, broker, ledger)
    rows = read_records(thesis)
    pre = rows[0]
    matched = (
        pre["signal_id"] == "sig-positive"
        and pre["thesis_hash"] == thesis_hash(_complete("sig-positive"))
        and pre["strategy_id"] == "S2"
        and pre["set_id"] == 2
        and pre["topology"] == "bb_pullback_load"
        and pre["structural_stop_price"] == 1.0990
        and pre["risk_dollars"] == 25.0
        and rows[1]["record_type"] == "order_intent"
        and rows[1]["broker_comment"] == pre["broker_comment"]
    )
    ok = positive["sent"] and broker.calls == 1 and broker.live_order_calls == 0 and matched
    results.append(("complete_thesis", ok, broker.calls))
    if not ok:
        raise SystemExit(f"complete_thesis failed {positive}")

    broker = FakeBroker()
    thesis, ledger = fresh("write-fail")

    def explode(path: Path, record: dict) -> bool:
        raise OSError("disk full")

    failed = decide(_complete("sig-write"), thesis, broker, ledger, append=explode)
    errors = read_records(ledger)
    ok = (not failed["sent"]) and broker.calls == 0 and failed["reason"] == "pre_trade_thesis_not_persisted" and errors
    results.append(("failed_write", ok, broker.calls))
    if not ok:
        raise SystemExit(f"failed_write failed {failed}")

    broker = FakeBroker()
    thesis, ledger = fresh("partial")

    def partial(path: Path, record: dict) -> bool:
        path.write_text("{", encoding="utf-8")
        return True

    partial_result = decide(_complete("sig-partial"), thesis, broker, ledger, append=partial)
    ok = (not partial_result["sent"]) and broker.calls == 0 and partial_result["reason"] == "pre_trade_thesis_not_persisted" and read_records(ledger)
    results.append(("partial_write", ok, broker.calls))
    if not ok:
        raise SystemExit(f"partial_write failed {partial_result}")

    blank_names = (
        "strategy_id",
        "set_id",
        "htf1",
        "htf2",
        "tide",
        "regime",
        "topology",
        "entry_bid",
        "entry_ask",
        "spread_points",
        "structural_stop_price",
        "structural_kill_relation",
        "risk_dollars",
        "risk_percent",
        "maximum_duration_minutes",
        "signal_id",
        "doctrine_version",
        "config_hash",
    )
    for name in blank_names:
        broker = FakeBroker()
        thesis, ledger = fresh(f"blank-{name}")
        record = _complete(f"sig-blank-{name}")
        record.pop(name)
        result = decide(record, thesis, broker, ledger)
        ok = (not result["sent"]) and broker.calls == 0 and result["reason"] == "pre_trade_thesis_incomplete"
        results.append((f"blank_{name}", ok, broker.calls))
        if not ok:
            raise SystemExit(f"blank {name} failed {result}")

    broker = FakeBroker()
    thesis, ledger = fresh("emerged")
    emerged = _complete("sig-emerged")
    emerged["emerged"] = True
    emerged["official_act"] = "WAIT_LOADED"
    result = decide(emerged, thesis, broker, ledger)
    ok = (not result["sent"]) and broker.calls == 0 and result["reason"] == "emergence_not_execution_authority"
    results.append(("emergence", ok, broker.calls))
    if not ok:
        raise SystemExit(f"emergence failed {result}")

    for side in ("neutral", "flat", "short"):
        broker = FakeBroker()
        thesis, ledger = fresh(f"tide-{side}")
        record = _complete(f"sig-tide-{side}")
        record["htf2_side"] = side
        result = decide(record, thesis, broker, ledger)
        ok = (not result["sent"]) and broker.calls == 0 and result["reason"] == "htf_force_conflict"
        results.append((f"tide_{side}", ok, broker.calls))
        if not ok:
            raise SystemExit(f"tide {side} failed {result}")

    broker = FakeBroker()
    thesis, ledger = fresh("regime")
    record = _complete("sig-regime")
    record["regime"] = "undefined"
    result = decide(record, thesis, broker, ledger)
    ok = (not result["sent"]) and broker.calls == 0 and result["reason"] == "regime_not_verified"
    results.append(("undefined_regime", ok, broker.calls))
    if not ok:
        raise SystemExit(f"regime failed {result}")

    broker = FakeBroker()
    thesis, ledger = fresh("s5")
    record = _complete("sig-s5")
    record["s5_present"] = False
    result = decide(record, thesis, broker, ledger)
    ok = (not result["sent"]) and broker.calls == 0 and result["reason"] == "regime_not_verified"
    results.append(("missing_s5", ok, broker.calls))
    if not ok:
        raise SystemExit(f"s5 failed {result}")

    broker = FakeBroker()
    thesis, ledger = fresh("stale")
    record = _complete("sig-stale")
    record["release_bar_time"] = "2026-09-23T01:00:00"
    result = decide(record, thesis, broker, ledger)
    ok = (not result["sent"]) and broker.calls == 0 and result["reason"] == "stale_release"
    results.append(("stale_release", ok, broker.calls))
    if not ok:
        raise SystemExit(f"stale failed {result}")

    broker = FakeBroker()
    thesis, ledger = fresh("mismatch")
    record = _complete("sig-mismatch")
    record["owner_strategy"] = "S3"
    result = decide(record, thesis, broker, ledger)
    ok = (not result["sent"]) and broker.calls == 0 and result["reason"] == "set_strategy_mismatch"
    results.append(("set_strategy_mismatch", ok, broker.calls))
    if not ok:
        raise SystemExit(f"mismatch failed {result}")

    broker = FakeBroker()
    thesis, ledger = fresh("duplicate")
    first = decide(_complete("sig-dup"), thesis, broker, ledger)
    second = decide(_complete("sig-dup"), thesis, broker, ledger)
    intents = [row for row in read_records(thesis) if row.get("record_type") == "order_intent"]
    ok = first["sent"] and (not second["sent"]) and second["reason"] == "duplicate_signal" and broker.calls == 1 and len(intents) == 1
    results.append(("duplicate_signal", ok, broker.calls))
    if not ok:
        raise SystemExit(f"duplicate failed {first} {second}")

    broker = FakeBroker()
    thesis, ledger = fresh("restart")
    seeded = _complete("sig-restart")
    seeded_line = dict(seeded)
    seeded_line["record_type"] = "pre_trade"
    seeded_line["thesis_hash"] = thesis_hash(seeded)
    seeded_line["broker_comment"] = comment_for(seeded)
    durable_append(thesis, seeded_line)
    restarted = decide(seeded, thesis, broker, ledger)
    ok = (not restarted["sent"]) and broker.calls == 0 and restarted["reason"] == "duplicate_signal"
    results.append(("restart", ok, broker.calls))
    if not ok:
        raise SystemExit(f"restart failed {restarted}")

    broker = FakeBroker(reject=True, retcode=10016)
    thesis, ledger = fresh("reject")
    before = None
    rejected = decide(_complete("sig-reject"), thesis, broker, ledger)
    rows = read_records(thesis)
    thesis_lines = [row for row in rows if row.get("record_type") == "pre_trade"]
    rejects = [row for row in rows if row.get("record_type") == "broker_rejection"]
    invented = any("ticket" in row or "fill" in row or "position" in row for row in rows)
    again = decide(_complete("sig-reject"), thesis, broker, ledger)
    ok = (
        (not rejected["sent"])
        and rejected["reason"] == "broker_rejected"
        and broker.calls == 1
        and len(thesis_lines) == 1
        and len(rejects) == 1
        and rejects[0]["retcode"] == 10016
        and not invented
        and (not again["sent"])
        and broker.calls == 1
    )
    results.append(("broker_rejection", ok, broker.calls))
    if not ok:
        raise SystemExit(f"broker_rejection failed {rejected} {again} {rows}")

    if "MetaTrader5" in sys.modules or LIVE_ORDER_CALLS != 0:
        raise SystemExit("live order path was touched")
    for name, passed, calls in results:
        print(f"{name} PASS send_calls {calls}" if passed else f"{name} FAIL send_calls {calls}")
    print("SELFTEST_OK send_calls 1")
    print("GATE_SUITE_OK")
    print("KEEP10_REPAIR_STATUS: VERIFIED_FOR_DEMO_ONLY")
    print("EXECUTION_STATUS: DISABLED_FOR_KEEP10")


def main() -> None:
    print("KEEP10_REPAIR_STATUS: VERIFIED_FOR_DEMO_ONLY")
    print("EXECUTION_STATUS: DISABLED_FOR_KEEP10")
    print("No keep10 order is sent from this entry point.")
    if not KEEP10_EXECUTION_ENABLED:
        return


if __name__ == "__main__":
    import sys

    if "--selftest" in sys.argv:
        run_gate_suite()
    else:
        main()

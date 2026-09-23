"""Read-only mentor assistant for Jarvis.

Reads JarvisEyes board.csv, labels momentum vs mean reversion from G1–G7
and official S1–S4, appends passes.jsonl, rewrites to_jarvis.md.
Never imports or calls MetaTrader5 trade functions. Demo mentoring only.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

BOARD_PATH = Path(
    r"C:\Users\C2K\AppData\Roaming\MetaQuotes\Terminal"
    r"\D0E8209F77C8CF37AD8BF550E51FF075\MQL5\Files\jarvis\board.csv"
)
ROOT = Path(__file__).resolve().parent.parent  # JARVIS V1
ASSISTANT_DIR = Path(__file__).resolve().parent
PASSES_PATH = ASSISTANT_DIR / "passes.jsonl"
EXITS_PATH = ASSISTANT_DIR / "exits.jsonl"
TO_JARVIS_PATH = ASSISTANT_DIR / "to_jarvis.md"
STOP_PATH = ASSISTANT_DIR / "STOP"
DESK_STATE_PATH = ROOT / "desk_state.md"
JOURNAL_PATH = ROOT / "JOURNAL.md"

# SCHEMA: G1=D1, G2=M1, G3=M5, G4=M15, G5=M30, G6=H1, G7=H4
GATE_TO_SIDE_KEY = {
    "G1": "side_D1",
    "G2": "side_M1",
    "G3": "side_M5",
    "G4": "side_M15",
    "G5": "side_M30",
    "G6": "side_H1",
    "G7": "side_H4",
}
TF_ORDER = ["M1", "M5", "M15", "M30", "H1", "H4", "D1"]
SIDE_KEYS = [f"side_{tf}" for tf in TF_ORDER]
OUTCOME_BUCKETS = {"PROFITABLE", "NOT_PROFITABLE", "UNRESOLVED"}
MIN_SCORED_FOR_FIT = 20
LOOP_SECONDS = 300
MAGIC = 771249
_DEBUG_LOG = Path(__file__).resolve().parents[2] / "debug-88be24.log"


def _dbg(hypothesis_id: str, location: str, message: str, data: dict[str, Any]) -> None:
    # #region agent log
    try:
        line = json.dumps(
            {
                "sessionId": "88be24",
                "hypothesisId": hypothesis_id,
                "location": location,
                "message": message,
                "data": data,
                "timestamp": int(time.time() * 1000),
                "runId": "pre-fix",
            },
            ensure_ascii=False,
        )
        with _DEBUG_LOG.open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")
    except OSError:
        pass
    # #endregion


def now_local() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def parse_float(val: Any) -> float | None:
    if val is None:
        return None
    s = str(val).strip()
    if not s:
        return None
    try:
        return float(s)
    except ValueError:
        return None


def gate_side(rsi: float | None, sma: float | None) -> str | None:
    if rsi is None or sma is None:
        return None
    if rsi > sma:
        return "ABOVE"
    if rsi < sma:
        return "BELOW"
    return "FLAT"


def side_from_gate_row(row: dict[str, str]) -> str | None:
    """ABOVE/BELOW/FLAT from cmp or raw rsi14 vs sma1_shift4."""
    cmp = row.get("cmp") or ""
    rsi = None
    sma = None
    m_rsi = re.search(r"rsi14=([-\d.]+)", cmp)
    m_sma = re.search(r"sma1_shift4=([-\d.]+)", cmp)
    if m_rsi:
        rsi = parse_float(m_rsi.group(1))
    if m_sma:
        sma = parse_float(m_sma.group(1))
    if rsi is None:
        rsi = parse_float(row.get("raw_a"))
    if sma is None:
        sma = parse_float(row.get("raw_b"))
    return gate_side(rsi, sma)


def alignment_counts(sides: dict[str, str | None]) -> tuple[int, int, str]:
    above = sum(1 for tf in TF_ORDER if sides.get(f"side_{tf}") == "ABOVE")
    below = sum(1 for tf in TF_ORDER if sides.get(f"side_{tf}") == "BELOW")
    if above > below:
        side = "ABOVE"
    elif below > above:
        side = "BELOW"
    else:
        side = "SPLIT"
    return above, below, side


def htf_agree_count(sides: dict[str, str | None], anchor_tf: str) -> int:
    """Raw count of higher TFs agreeing with the HTF majority side."""
    if anchor_tf not in TF_ORDER:
        return 0
    idx = TF_ORDER.index(anchor_tf)
    higher = TF_ORDER[idx + 1 :]
    h_above = sum(1 for tf in higher if sides.get(f"side_{tf}") == "ABOVE")
    h_below = sum(1 for tf in higher if sides.get(f"side_{tf}") == "BELOW")
    if h_above > h_below:
        s_htf = "ABOVE"
    elif h_below > h_above:
        s_htf = "BELOW"
    else:
        return 0  # NONE or SPLIT — raw agree with a defined majority is 0
    return sum(1 for tf in higher if sides.get(f"side_{tf}") == s_htf)


def htf_majority(sides: dict[str, str | None], anchor_tf: str) -> str | None:
    if anchor_tf not in TF_ORDER:
        return None
    idx = TF_ORDER.index(anchor_tf)
    higher = TF_ORDER[idx + 1 :]
    h_above = sum(1 for tf in higher if sides.get(f"side_{tf}") == "ABOVE")
    h_below = sum(1 for tf in higher if sides.get(f"side_{tf}") == "BELOW")
    if h_above > h_below:
        return "ABOVE"
    if h_below > h_above:
        return "BELOW"
    return None


def read_desk_gap() -> str:
    """Copy the +38535 desk gap from desk_state.md; do not recompute."""
    if not DESK_STATE_PATH.exists():
        return "+38535 (desk_state.md missing; figure copied from plan)"
    text = DESK_STATE_PATH.read_text(encoding="utf-8", errors="replace")
    for line in text.splitlines():
        if "+38535" not in line:
            continue
        # Strip markdown table pipes: | Today target | ... |
        parts = [p.strip() for p in line.split("|") if p.strip()]
        if len(parts) >= 2 and parts[0].lower().startswith("today target"):
            return parts[1]
        if parts:
            return parts[-1] if len(parts) > 1 else parts[0]
    return "+38535 (not found in desk_state; using known desk gap)"


def load_board(path: Path) -> tuple[list[dict[str, str]], str | None]:
    if not path.exists():
        return [], "board missing"
    with path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        return [], "board empty"
    return rows, None


def group_by_symbol(rows: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    out: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        sym = (row.get("symbol") or "").strip()
        if sym:
            out[sym].append(row)
    return out


def pick_set_for_symbol(sym_rows: list[dict[str, str]]) -> str:
    """Prefer lowest set that has an official FIRE; else set 2."""
    fires: list[tuple[int, str]] = []
    for row in sym_rows:
        if row.get("family") != "OFFICIAL":
            continue
        if row.get("act") in ("FIRE_BUY", "FIRE_SELL"):
            try:
                fires.append((int(row.get("set") or 9), row.get("set") or "2"))
            except ValueError:
                fires.append((9, "2"))
    if fires:
        fires.sort()
        return fires[0][1]
    return "2"


def official_acts(
    sym_rows: list[dict[str, str]], set_id: str
) -> dict[str, dict[str, str]]:
    acts: dict[str, dict[str, str]] = {}
    for sid in ("S1", "S2", "S3", "S4"):
        for row in sym_rows:
            if row.get("strategy") == sid and str(row.get("set")) == str(set_id):
                acts[sid] = row
                break
    return acts


def named_means_present(sym_rows: list[dict[str, str]], set_id: str) -> dict[str, Any]:
    means: dict[str, Any] = {
        "has_named_mean": False,
        "s2_bb10_mid": None,
        "s5_bb20_mid_htf1": None,
        "s5_bb200_mid_htf1": None,
        "s5_bb20_mid_htf2": None,
        "s5_bb200_mid_htf2": None,
    }
    for row in sym_rows:
        if row.get("strategy") == "S2" and str(row.get("set")) == str(set_id):
            mid = parse_float(row.get("raw_b"))  # bb10_mid
            means["s2_bb10_mid"] = mid
            if mid is not None:
                means["has_named_mean"] = True
        if row.get("strategy") == "S5" and str(row.get("set")) == str(set_id):
            means["s5_bb200_mid_htf1"] = parse_float(row.get("raw_a"))
            means["s5_bb20_mid_htf1"] = parse_float(row.get("raw_b"))
            means["s5_bb200_mid_htf2"] = parse_float(row.get("raw_c"))
            means["s5_bb20_mid_htf2"] = parse_float(row.get("raw_d"))
            if any(
                means[k] is not None
                for k in (
                    "s5_bb20_mid_htf1",
                    "s5_bb200_mid_htf1",
                    "s5_bb20_mid_htf2",
                    "s5_bb200_mid_htf2",
                )
            ):
                means["has_named_mean"] = True
    return means


def fractal_context(sym_rows: list[dict[str, str]]) -> str:
    for row in sym_rows:
        if row.get("strategy") == "L4":
            up = row.get("raw_a") or "?"
            dn = row.get("raw_b") or "?"
            up_c = row.get("raw_c") or "?"
            dn_c = row.get("raw_d") or "?"
            return (
                f"L4 context only: last_up_frac={up} last_dn_frac={dn} "
                f"up_count_hint={up_c} dn_count_hint={dn_c} (not a license)"
            )
    return "L4 context only: no L4 row (not a license)"


def classify_label(
    alignment_side: str,
    official_tide: str,
    anchor_tf: str,
    sides: dict[str, str | None],
    has_named_mean: bool,
) -> str:
    """Momentum / mean_reversion / none. Not a fire."""
    tide_side = None
    if official_tide == "long_only":
        tide_side = "ABOVE"
    elif official_tide == "short_only":
        tide_side = "BELOW"

    if (
        alignment_side in ("ABOVE", "BELOW")
        and tide_side is not None
        and alignment_side == tide_side
    ):
        return "momentum"

    anchor_side = sides.get(f"side_{anchor_tf}")
    s_htf = htf_majority(sides, anchor_tf)
    if (
        anchor_side in ("ABOVE", "BELOW")
        and s_htf in ("ABOVE", "BELOW")
        and anchor_side != s_htf
        and has_named_mean
    ):
        return "mean_reversion"

    return "none"


def kill_relation(fire_row: dict[str, str] | None, anchor_tf: str) -> str:
    if fire_row:
        reason = (fire_row.get("reason") or "").strip()
        act = fire_row.get("act") or ""
        if act == "FIRE_BUY":
            return (
                f"Kill: RSI(14) closes back below SMA(1)+4 on {anchor_tf}, "
                f"or official row loses FIRE ({reason or 'row kill'})"
            )
        if act == "FIRE_SELL":
            return (
                f"Kill: RSI(14) closes back above SMA(1)+4 on {anchor_tf}, "
                f"or official row loses FIRE ({reason or 'row kill'})"
            )
    return f"Kill: RSI(14) closes back through SMA(1)+4 on {anchor_tf}"


def build_symbol_record(
    symbol: str, sym_rows: list[dict[str, str]], board_ts: str
) -> dict[str, Any] | None:
    data_flags = {(r.get("data") or "").strip() for r in sym_rows}
    if "fresh" not in data_flags:
        return {
            "symbol": symbol,
            "board_ts": board_ts,
            "data_ok": False,
            "data_flags": sorted(data_flags),
            "note": "data not fresh; side not invented",
        }

    sides: dict[str, str | None] = {k: None for k in SIDE_KEYS}
    gate_ok = True
    for row in sym_rows:
        strat = row.get("strategy") or ""
        if strat not in GATE_TO_SIDE_KEY:
            continue
        if (row.get("data") or "").strip() != "fresh":
            gate_ok = False
            continue
        key = GATE_TO_SIDE_KEY[strat]
        side = side_from_gate_row(row)
        if side is None:
            gate_ok = False
        sides[key] = side

    if not gate_ok or any(sides[k] is None for k in SIDE_KEYS):
        return {
            "symbol": symbol,
            "board_ts": board_ts,
            "data_ok": False,
            "note": "G1–G7 incomplete or not fresh; side not invented",
            "sides": sides,
        }

    set_id = pick_set_for_symbol(sym_rows)
    acts = official_acts(sym_rows, set_id)
    anchor_tf = "M5"
    for sid in ("S1", "S2", "S3", "S4"):
        if sid in acts and acts[sid].get("anchor_tf"):
            anchor_tf = acts[sid]["anchor_tf"]
            break

    # Prefer FIRE row for tide / kill / close
    fire_row = None
    for row in sym_rows:
        if row.get("family") != "OFFICIAL":
            continue
        if row.get("act") in ("FIRE_BUY", "FIRE_SELL"):
            fire_row = row
            set_id = str(row.get("set") or set_id)
            acts = official_acts(sym_rows, set_id)
            anchor_tf = row.get("anchor_tf") or anchor_tf
            break

    official_tide = "flat"
    if fire_row:
        official_tide = fire_row.get("tide") or "flat"
    else:
        for sid in ("S1", "S2", "S3", "S4"):
            if sid in acts and acts[sid].get("tide") in ("long_only", "short_only"):
                official_tide = acts[sid]["tide"]
                break

    above, below, alignment_side = alignment_counts(sides)
    htf_n = htf_agree_count(sides, anchor_tf)
    means = named_means_present(sym_rows, set_id)
    label = classify_label(
        alignment_side, official_tide, anchor_tf, sides, means["has_named_mean"]
    )

    close1 = None
    spread_points = None
    closed_bar_time = None
    sample_row = fire_row or next(iter(acts.values()), None) or sym_rows[0]
    if sample_row:
        close1 = parse_float(sample_row.get("close1"))
        spread_points = parse_float(sample_row.get("spread_points"))
        closed_bar_time = sample_row.get("closed_bar_time") or ""

    s_acts = {
        "s1_act": (acts.get("S1") or {}).get("act") or "n/a",
        "s2_act": (acts.get("S2") or {}).get("act") or "n/a",
        "s3_act": (acts.get("S3") or {}).get("act") or "n/a",
        "s4_act": (acts.get("S4") or {}).get("act") or "n/a",
    }

    fire_act = fire_row.get("act") if fire_row else None
    fire_strategy = fire_row.get("strategy") if fire_row else None
    fire_plain = fire_row.get("plain_name") if fire_row else None

    return {
        "symbol": symbol,
        "board_ts": board_ts,
        "data_ok": True,
        "timestamp": now_local(),
        "set_id": set_id,
        "anchor_tf": anchor_tf,
        "sides": sides,
        "alignment_count_above": above,
        "alignment_count_below": below,
        "alignment_side": alignment_side,
        "htf_agree_count": htf_n,
        "pullback_min_undefined": True,
        **s_acts,
        "spread_points": spread_points,
        "close1": close1,
        "closed_bar_time": closed_bar_time,
        "official_tide": official_tide,
        "label": label,
        "means": means,
        "fractal_context": fractal_context(sym_rows),
        "fire_act": fire_act,
        "fire_strategy": fire_strategy,
        "fire_plain": fire_plain,
        "kill_relation": kill_relation(fire_row, anchor_tf),
        "outcome_status": "UNRESOLVED",
    }


def pass_line_from_record(rec: dict[str, Any]) -> dict[str, Any] | None:
    if not rec.get("data_ok"):
        return None
    sides = rec["sides"]
    line = {
        "timestamp": rec["timestamp"],
        "board_ts": rec["board_ts"],
        "symbol": rec["symbol"],
        "side_M1": sides["side_M1"],
        "side_M5": sides["side_M5"],
        "side_M15": sides["side_M15"],
        "side_M30": sides["side_M30"],
        "side_H1": sides["side_H1"],
        "side_H4": sides["side_H4"],
        "side_D1": sides["side_D1"],
        "alignment_count_above": rec["alignment_count_above"],
        "alignment_count_below": rec["alignment_count_below"],
        "alignment_side": rec["alignment_side"],
        "anchor_tf": rec["anchor_tf"],
        "htf_agree_count": rec["htf_agree_count"],
        "pullback_min_undefined": True,
        "s1_act": rec["s1_act"],
        "s2_act": rec["s2_act"],
        "s3_act": rec["s3_act"],
        "s4_act": rec["s4_act"],
        "spread_points": rec["spread_points"],
        "close1": rec["close1"],
        "closed_bar_time": rec["closed_bar_time"],
        "label": rec["label"],
        "official_tide": rec["official_tide"],
        "set_id": rec["set_id"],
        "outcome_status": "UNRESOLVED",
    }
    return line


def load_passes() -> list[dict[str, Any]]:
    if not PASSES_PATH.exists():
        return []
    out: list[dict[str, Any]] = []
    with PASSES_PATH.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return out


def write_passes(rows: list[dict[str, Any]]) -> None:
    ASSISTANT_DIR.mkdir(parents=True, exist_ok=True)
    with PASSES_PATH.open("w", encoding="utf-8", newline="\n") as f:
        for row in rows:
            f.write(json.dumps(row, separators=(",", ":"), ensure_ascii=False) + "\n")


def score_unresolved(
    existing: list[dict[str, Any]], current_by_symbol: dict[str, dict[str, Any]]
) -> int:
    """Fill outcome_status when a newer closed bar exists vs logged side after spread."""
    scored = 0
    for row in existing:
        if row.get("outcome_status") not in (None, "UNRESOLVED", "PENDING"):
            continue
        # Normalize PENDING → stay until scored; forced tape used PENDING then outcome.
        # Harness buckets: PROFITABLE / NOT_PROFITABLE / UNRESOLVED only.
        if row.get("outcome_status") == "PENDING":
            row["outcome_status"] = "UNRESOLVED"
        sym = row.get("symbol")
        if not sym or sym not in current_by_symbol:
            continue
        cur = current_by_symbol[sym]
        if not cur.get("data_ok"):
            continue
        old_bar = row.get("closed_bar_time") or ""
        new_bar = cur.get("closed_bar_time") or ""
        if not new_bar or not old_bar or new_bar <= old_bar:
            continue
        old_close = parse_float(row.get("close1"))
        new_close = parse_float(cur.get("close1"))
        if old_close is None or new_close is None:
            continue
        spread_pts = parse_float(row.get("spread_points")) or 0.0
        # Approximate spread in price: use point from close magnitude (5-digit default)
        # Prefer delta of closes vs spread_points * point; use relative point guess.
        point = 0.00001
        if abs(old_close) >= 50:
            point = 0.001
        elif abs(old_close) >= 10:
            point = 0.001
        spread_price = spread_pts * point
        side = row.get("alignment_side")
        if side == "ABOVE":
            # Buy-side thesis: profitable if price rose after paying spread
            net = (new_close - old_close) - spread_price
            row["outcome_status"] = "PROFITABLE" if net > 0 else "NOT_PROFITABLE"
        elif side == "BELOW":
            net = (old_close - new_close) - spread_price
            row["outcome_status"] = "PROFITABLE" if net > 0 else "NOT_PROFITABLE"
        else:
            # SPLIT / unknown — leave UNRESOLVED
            continue
        row["outcome_close1"] = new_close
        row["outcome_closed_bar_time"] = new_bar
        row["net_price_after_spread"] = net
        scored += 1
    return scored


def _encode_side(val: Any) -> float:
    if val == "ABOVE":
        return 1.0
    if val == "BELOW":
        return -1.0
    return 0.0


def _feature_vector(row: dict[str, Any]) -> list[float]:
    """Paul multi-TF sides plus the higher-vs-lower disagreement. Not a fire."""
    vec = [_encode_side(row.get(key)) for key in SIDE_KEYS]
    anchor = str(row.get("anchor_tf") or "")
    anchor_side = _encode_side(row.get(f"side_{anchor}"))
    daily = _encode_side(row.get("side_D1"))
    disagree = 1.0 if anchor_side != 0.0 and daily != 0.0 and anchor_side != daily else 0.0
    vec.extend(
        [
            float(row.get("alignment_count_above") or 0),
            float(row.get("alignment_count_below") or 0),
            float(row.get("htf_agree_count") or 0),
            disagree,
        ]
    )
    return vec


def _row_from_record(rec: dict[str, Any]) -> dict[str, Any]:
    sides = rec.get("sides") or {}
    row = {
        "anchor_tf": rec.get("anchor_tf"),
        "alignment_count_above": rec.get("alignment_count_above"),
        "alignment_count_below": rec.get("alignment_count_below"),
        "htf_agree_count": rec.get("htf_agree_count"),
    }
    for key in SIDE_KEYS:
        row[key] = sides.get(key)
    return row


def _column_stats(rows: list[list[float]]) -> tuple[list[float], list[float]]:
    width = len(rows[0])
    means = []
    stds = []
    n = float(len(rows))
    for j in range(width):
        col = [r[j] for r in rows]
        mean = sum(col) / n
        var = sum((v - mean) ** 2 for v in col) / n
        means.append(mean)
        stds.append(var ** 0.5 or 1.0)
    return means, stds


def _standardize(vec: list[float], means: list[float], stds: list[float]) -> list[float]:
    return [(v - m) / s for v, m, s in zip(vec, means, stds)]


def _dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def _sigmoid(z: float) -> float:
    if z > 30.0:
        return 1.0
    if z < -30.0:
        return 0.0
    return 1.0 / (1.0 + 2.718281828 ** (-z))


def _fit_logistic_gd(
    X: list[list[float]], y: list[int], steps: int = 400, lr: float = 0.15, l2: float = 0.05
) -> tuple[list[float], float]:
    """Stdlib logistic regression used when scikit-learn cannot be imported."""
    width = len(X[0])
    weights = [0.0] * width
    bias = 0.0
    n = float(len(X))
    for _ in range(steps):
        grad_w = [0.0] * width
        grad_b = 0.0
        for vec, actual in zip(X, y):
            err = _sigmoid(_dot(vec, weights) + bias) - float(actual)
            for j in range(width):
                grad_w[j] += err * vec[j]
            grad_b += err
        for j in range(width):
            weights[j] -= lr * ((grad_w[j] / n) + l2 * weights[j])
        bias -= lr * (grad_b / n)
    return weights, bias


def try_fit_model(
    rows: list[dict[str, Any]], records: list[dict[str, Any]] | None = None
) -> str:
    """Logistic regression per label bucket if sklearn importable and n>=20 scored."""
    status_counts: dict[str, int] = defaultdict(int)
    label_counts: dict[str, int] = defaultdict(int)
    for row in rows:
        status_counts[str(row.get("outcome_status"))] += 1
        label_counts[str(row.get("label"))] += 1
    # #region agent log
    _dbg(
        "D",
        "mentor_assistant.py:try_fit_model",
        "row inventory before fit",
        {
            "n_rows": len(rows),
            "status_counts": dict(status_counts),
            "label_counts": dict(label_counts),
            "min_scored": MIN_SCORED_FOR_FIT,
            "feature_names": [
                "alignment_count_above",
                "alignment_count_below",
                "htf_agree_count",
            ],
        },
    )
    # #endregion
    try:
        from sklearn.linear_model import LogisticRegression  # type: ignore
        import numpy as np  # type: ignore
    except ImportError as exc:
        # #region agent log
        _dbg(
            "A",
            "mentor_assistant.py:try_fit_model",
            "sklearn import failed",
            {"error": type(exc).__name__, "detail": str(exc)},
        )
        # #endregion
        LogisticRegression = None  # type: ignore
        np = None  # type: ignore

    if LogisticRegression is not None:
        # #region agent log
        _dbg(
            "A",
            "mentor_assistant.py:try_fit_model",
            "sklearn import ok",
            {"sklearn": "importable"},
        )
        # #endregion

    by_bucket: dict[str, list[dict[str, Any]]] = defaultdict(list)
    scored: list[dict[str, Any]] = []
    for row in rows:
        status = row.get("outcome_status")
        if status not in ("PROFITABLE", "NOT_PROFITABLE"):
            continue
        bucket = row.get("label") or "none"
        by_bucket[bucket].append(row)
        scored.append(row)

    for bucket, items in sorted(by_bucket.items()):
        classes = {r.get("outcome_status") for r in items}
        # #region agent log
        _dbg(
            "B",
            "mentor_assistant.py:try_fit_model",
            "bucket gate",
            {
                "bucket": bucket,
                "n": len(items),
                "min_scored": MIN_SCORED_FOR_FIT,
                "below_min": len(items) < MIN_SCORED_FOR_FIT,
                "classes": sorted(str(c) for c in classes),
            },
        )
        # #endregion

    if len(scored) < MIN_SCORED_FOR_FIT:
        return (
            f"insufficient sample ({len(scored)}/{MIN_SCORED_FOR_FIT} scored); "
            "model not fit"
        )

    scored.sort(key=lambda r: (str(r.get("timestamp") or ""), str(r.get("symbol") or "")))
    X_raw = [_feature_vector(r) for r in scored]
    y_all = [1 if r.get("outcome_status") == "PROFITABLE" else 0 for r in scored]
    if len(set(y_all)) < 2:
        return "model not fit (scored rows are one class only)"

    split = max(MIN_SCORED_FOR_FIT, int(len(scored) * 0.7))
    if split >= len(scored):
        split = len(scored) - 1
    X_train_raw, X_test_raw = X_raw[:split], X_raw[split:]
    y_train, y_test = y_all[:split], y_all[split:]
    means, stds = _column_stats(X_train_raw)
    X_train = [_standardize(v, means, stds) for v in X_train_raw]
    X_test = [_standardize(v, means, stds) for v in X_test_raw]

    engine = "stdlib-gd"
    weights: list[float]
    bias: float
    if LogisticRegression is not None and np is not None and len(set(y_train)) >= 2:
        clf = LogisticRegression(max_iter=400, C=1.0)
        clf.fit(np.array(X_train), np.array(y_train))
        weights = [float(w) for w in clf.coef_[0]]
        bias = float(clf.intercept_[0])
        engine = "sklearn-logistic"
    else:
        weights, bias = _fit_logistic_gd(X_train, y_train)

    def predict_p(raw: list[float]) -> float:
        return _sigmoid(_dot(_standardize(raw, means, stds), weights) + bias)

    holdout_n = len(y_test)
    holdout_acc = None
    if holdout_n and len(set(y_train)) >= 2:
        correct = 0
        for vec, actual in zip(X_test_raw, y_test):
            pred = 1 if predict_p(vec) >= 0.5 else 0
            correct += int(pred == actual)
        holdout_acc = correct / holdout_n

    if records:
        for rec in records:
            if not rec.get("data_ok"):
                continue
            p_mom = predict_p(_feature_vector(_row_from_record(rec)))
            rec["p_momentum"] = round(p_mom, 3)
            rec["p_reversion"] = round(1.0 - p_mom, 3)

    acc_txt = "n/a" if holdout_acc is None else f"{holdout_acc:.3f}"
    note = (
        f"Chan logistic ({engine}) on Paul multi-TF sides M1-D1, "
        f"anchor-vs-D1 disagreement, alignment counts, htf agree. "
        f"y=1 momentum continuation paid; y=0 continuation failed "
        f"(mean reversion on that bar). "
        f"train={len(y_train)} test={holdout_n} holdout_accuracy={acc_txt}. "
        f"Desk +38535 is not a feature. No lot. No order."
    )
    # #region agent log
    try:
        line = json.dumps(
            {
                "sessionId": "88be24",
                "hypothesisId": "FIX",
                "location": "mentor_assistant.py:try_fit_model",
                "message": "walk-forward fit result",
                "data": {
                    "engine": engine,
                    "n_scored": len(scored),
                    "n_features": len(X_raw[0]) if X_raw else 0,
                    "train": len(y_train),
                    "test": holdout_n,
                    "holdout_accuracy": holdout_acc,
                    "fires_scored": sum(1 for r in (records or []) if "p_momentum" in r),
                },
                "timestamp": int(time.time() * 1000),
                "runId": "post-fix",
            },
            ensure_ascii=False,
        )
        with _DEBUG_LOG.open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")
    except OSError:
        pass
    # #endregion
    return note


def _set12_fire_on_side(sym_rows: list[dict[str, str]], side: str) -> bool:
    want = "FIRE_BUY" if side == "buy" else "FIRE_SELL"
    for row in sym_rows:
        if row.get("family") != "OFFICIAL":
            continue
        if row.get("strategy") not in ("S1", "S2"):
            continue
        if str(row.get("set")) not in ("1", "2"):
            continue
        if (row.get("data") or "").strip() not in ("", "fresh"):
            continue
        if row.get("act") == want:
            return True
    return False


def _anchor_rsi_ok(rec: dict[str, Any], side: str) -> bool | None:
    anchor = str(rec.get("anchor_tf") or "")
    stamp = (rec.get("sides") or {}).get(f"side_{anchor}")
    if stamp not in ("ABOVE", "BELOW"):
        return None
    if side == "buy":
        return stamp == "ABOVE"
    return stamp == "BELOW"


def exit_reason(rec: dict[str, Any] | None, sym_rows: list[dict[str, str]], side: str) -> str | None:
    """None means leave the ticket open. Does not invent a side."""
    if rec is None or not rec.get("data_ok"):
        return None
    fire = _set12_fire_on_side(sym_rows, side)
    rsi_ok = _anchor_rsi_ok(rec, side)
    if rsi_ok is None:
        return None
    alignment = rec.get("alignment_side")
    want = "ABOVE" if side == "buy" else "BELOW"
    opposite = alignment in ("ABOVE", "BELOW") and alignment != want
    if opposite and not fire:
        return "will_not_rejoin"
    p_mom = rec.get("p_momentum")
    p_rev = rec.get("p_reversion")
    if p_mom is None or p_rev is None:
        if not fire or not rsi_ok:
            return "momentum_dying"
        return None
    prob_ok = float(p_mom) >= float(p_rev)
    if fire and rsi_ok and prob_ok:
        return None
    return "momentum_dying"


def _append_exit(row: dict[str, Any]) -> None:
    ASSISTANT_DIR.mkdir(parents=True, exist_ok=True)
    with EXITS_PATH.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def _filling_mode(mt5: Any, symbol: str) -> int:
    info = mt5.symbol_info(symbol)
    modes = 0 if info is None else int(info.filling_mode)
    if modes & 1:
        return mt5.ORDER_FILLING_FOK
    if modes & 2:
        return mt5.ORDER_FILLING_IOC
    return mt5.ORDER_FILLING_RETURN


def _close_one(mt5: Any, ticket: int, reason: str) -> dict[str, Any]:
    """Re-read the ticket, then close once. No retry after an ambiguous send."""
    pos = mt5.positions_get(ticket=ticket)
    if not pos:
        return {"ok": False, "ticket": ticket, "why": "already gone"}
    p = pos[0]
    comment = (p.comment or "").strip().lower()
    if int(p.magic) != MAGIC or comment == "client":
        return {"ok": False, "ticket": ticket, "why": "refuse non-magic or client"}
    pos = mt5.positions_get(ticket=ticket)
    if not pos:
        return {"ok": False, "ticket": ticket, "why": "gone before send"}
    p = pos[0]
    if int(p.magic) != MAGIC or (p.comment or "").strip().lower() == "client":
        return {"ok": False, "ticket": ticket, "why": "refuse on re-read"}
    tick = mt5.symbol_info_tick(p.symbol)
    if tick is None:
        return {"ok": False, "ticket": ticket, "why": "no tick"}
    side = "buy" if int(p.type) == 0 else "sell"
    order_type = mt5.ORDER_TYPE_SELL if side == "buy" else mt5.ORDER_TYPE_BUY
    price = tick.bid if side == "buy" else tick.ask
    req = {
        "action": mt5.TRADE_ACTION_DEAL,
        "position": int(ticket),
        "symbol": p.symbol,
        "volume": float(p.volume),
        "type": order_type,
        "price": float(price),
        "deviation": 30,
        "magic": MAGIC,
        "comment": ("J exit " + reason)[:31],
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": _filling_mode(mt5, p.symbol),
    }
    result = mt5.order_send(req)
    if result is None:
        return {
            "ok": False,
            "ambiguous": True,
            "ticket": ticket,
            "symbol": p.symbol,
            "why": str(mt5.last_error()),
        }
    done = result.retcode == mt5.TRADE_RETCODE_DONE
    ambiguous = result.retcode in (
        mt5.TRADE_RETCODE_TIMEOUT,
        mt5.TRADE_RETCODE_CONNECTION,
    )
    return {
        "ok": done,
        "ambiguous": ambiguous,
        "ticket": ticket,
        "symbol": p.symbol,
        "side": side,
        "profit": float(p.profit),
        "reason": reason,
        "retcode": int(result.retcode),
        "why": "" if done else f"ret={result.retcode} {result.comment}",
    }


def run_exits(
    board_ts: str,
    records: list[dict[str, Any]],
    by_sym: dict[str, list[dict[str, str]]],
) -> dict[str, Any]:
    """Close magic 771249 when momentum died or will not rejoin. Never opens."""
    by_record = {r["symbol"]: r for r in records if r.get("symbol")}
    lines: list[str] = []
    try:
        import MetaTrader5 as mt5
    except ImportError:
        return {
            "book": (
                f"Book (magic {MAGIC}): not read "
                "(MetaTrader package unavailable). No close sent."
            ),
            "lines": ["No close. Book was not read."],
            "closed": 0,
        }
    if not mt5.initialize():
        return {
            "book": (
                f"Book (magic {MAGIC}): not read "
                f"({mt5.last_error()}). No close sent."
            ),
            "lines": ["No close. Book was not read."],
            "closed": 0,
        }
    try:
        info = mt5.account_info()
        if info is None or info.trade_mode != mt5.ACCOUNT_TRADE_MODE_DEMO:
            return {
                "book": f"Book (magic {MAGIC}): not a demo account. No close sent.",
                "lines": ["No close. Terminal is not demo."],
                "closed": 0,
            }
        positions = mt5.positions_get() or []
        ours = [p for p in positions if int(p.magic) == MAGIC and (p.comment or "").strip().lower() != "client"]
        closed = 0
        held = 0
        for pos in ours:
            side = "buy" if int(pos.type) == 0 else "sell"
            rec = by_record.get(pos.symbol)
            reason = exit_reason(rec, by_sym.get(pos.symbol, []), side)
            if reason is None:
                held += 1
                lines.append(
                    f"- Hold {pos.ticket} {pos.symbol} {side} "
                    f"profit={float(pos.profit):.2f}. Momentum still intact on the closed bar, "
                    "or the board was not fresh."
                )
                continue
            outcome = _close_one(mt5, int(pos.ticket), reason)
            row = {
                "ticket": int(pos.ticket),
                "symbol": pos.symbol,
                "side": side,
                "profit": float(pos.profit),
                "reason": reason,
                "board_ts": board_ts,
                "ok": bool(outcome.get("ok")),
                "ambiguous": bool(outcome.get("ambiguous")),
                "why": outcome.get("why") or "",
            }
            _append_exit(row)
            if outcome.get("ok"):
                closed += 1
                lines.append(
                    f"- Closed {pos.ticket} {pos.symbol} {side} "
                    f"profit={float(pos.profit):.2f} reason={reason}. No reentry."
                )
            elif outcome.get("ambiguous"):
                lines.append(
                    f"- Ambiguous {pos.ticket} {pos.symbol} {side} "
                    f"reason={reason}. Not retried."
                )
            else:
                lines.append(
                    f"- Close failed {pos.ticket} {pos.symbol} {side} "
                    f"reason={reason} {outcome.get('why') or ''}."
                )
        book = (
            f"Book (magic {MAGIC}): {len(ours)} open at the read, "
            f"closed {closed}, left {held}. Client tickets not touched. No reentry."
        )
        if not lines:
            lines.append("No magic 771249 ticket was open.")
        return {"book": book, "lines": lines, "closed": closed}
    finally:
        mt5.shutdown()


def book_line(summary: str | None = None) -> str:
    if summary:
        return summary
    return (
        f"Book (magic {MAGIC}): not read. No close sent."
    )


def write_to_jarvis(
    board_ts: str,
    board_error: str | None,
    records: list[dict[str, Any]],
    model_note: str,
    desk_gap: str,
    exit_report: dict[str, Any] | None = None,
) -> None:
    ASSISTANT_DIR.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    lines.append("# Assistant to Jarvis")
    lines.append("")
    lines.append(f"- Clock: {now_local()}")
    lines.append(f"- Board ts: {board_ts or 'n/a'}")
    lines.append(f"- Closed-score gap (from desk_state): {desk_gap}")
    lines.append(
        "- Mode: new orders stay SAFE_HOLD. A close is sent only for "
        "momentum_dying or will_not_rejoin on magic 771249. No reentry."
    )
    lines.append("")

    if board_error:
        lines.append(f"**Board:** {board_error}. No sides invented.")
        lines.append("")
        lines.append(book_line(None if exit_report is None else exit_report.get("book")))
        lines.append("")
        lines.append(f"**Sample:** {model_note}")
        TO_JARVIS_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return

    fires: list[dict[str, Any]] = []
    for rec in records:
        if not rec.get("data_ok"):
            continue
        if rec.get("fire_act") in ("FIRE_BUY", "FIRE_SELL"):
            fires.append(rec)

    # Prefer momentum agreeing with fire, then mean_reversion, then others
    def fire_rank(r: dict[str, Any]) -> tuple[int, int, str]:
        label = r.get("label") or "none"
        pri = 2
        if label == "momentum":
            pri = 0
        elif label == "mean_reversion":
            pri = 1
        count = max(
            int(r.get("alignment_count_above") or 0),
            int(r.get("alignment_count_below") or 0),
        )
        return (pri, -count, r.get("symbol") or "")

    fires.sort(key=fire_rank)
    top = fires[:3]

    lines.append("## Official FIRE (up to three)")
    lines.append("")
    if not top:
        lines.append("No official FIRE_BUY / FIRE_SELL on a fresh board this pass.")
    else:
        for rec in top:
            lines.append(
                f"- **{rec['symbol']}** `{rec.get('fire_act')}` "
                f"({rec.get('fire_strategy')} {rec.get('fire_plain') or ''}) — "
                f"label **{rec.get('label')}** "
                f"(above={rec.get('alignment_count_above')} "
                f"below={rec.get('alignment_count_below')} "
                f"alignment_side={rec.get('alignment_side')} "
                f"htf_agree_count={rec.get('htf_agree_count')} "
                f"pullback_min_undefined=true). "
                f"{rec.get('kill_relation')} "
                f"{rec.get('fractal_context')}"
                + (
                    f" Learned P(momentum)={rec['p_momentum']} "
                    f"P(mean reversion)={rec['p_reversion']}."
                    if "p_momentum" in rec
                    else ""
                )
            )
    lines.append("")
    lines.append("## Exits")
    lines.append("")
    if exit_report is None:
        lines.append("No exit pass.")
    else:
        for row in exit_report.get("lines") or []:
            lines.append(row)
    lines.append("")
    lines.append(book_line(None if exit_report is None else exit_report.get("book")))
    lines.append("")
    stale = [r for r in records if not r.get("data_ok")]
    if stale:
        lines.append(
            f"Freshness note: {len(stale)} symbol(s) not scored "
            "(board missing sides or data not fresh)."
        )
        lines.append("")
    lines.append(f"**Sample / model:** {model_note}")
    lines.append("")
    TO_JARVIS_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def ensure_journal_proposal() -> None:
    """Append one Proposed row if not already present. Do not rewrite accepted rows."""
    marker = "assistant is research logging, not a fire rule"
    if JOURNAL_PATH.exists():
        text = JOURNAL_PATH.read_text(encoding="utf-8", errors="replace")
        if marker.lower() in text.lower():
            return
    else:
        text = (
            "# JARVIS journal\n\n"
            "Proposed doctrine changes only. Mark accepts or rejects. "
            "Do not edit `007_*.md` from the agent.\n\n"
            "| Date | Proposal | Status |\n"
            "|---|---|---|\n"
        )

    row = (
        "| 2026-09-22 | Mentor assistant under Jarvis: read-only board pass labels "
        "momentum vs mean reversion from G1–G7 and official S1–S4, appends "
        "`JARVIS V1/assistant/passes.jsonl`, rewrites `to_jarvis.md`. "
        "Assistant is research logging, not a fire rule. No orders. "
        "Does not change S1–S4 act/tide/conflict. pullback_min_undefined stays true. "
        "Logistic fit only after 20 scored rows in a bucket. | Proposed |\n"
    )

    # Keep inside the proposal table when possible (before --- / Session notes).
    if "\n---\n" in text:
        text = text.replace("\n---\n", "\n" + row + "\n---\n", 1)
    elif "## Session notes" in text:
        text = text.replace("## Session notes", row + "\n## Session notes", 1)
    else:
        text = text.rstrip() + "\n" + row + "\n"

    JOURNAL_PATH.write_text(text, encoding="utf-8")


def run_once() -> dict[str, Any]:
    desk_gap = read_desk_gap()
    rows, err = load_board(BOARD_PATH)
    board_ts = rows[0].get("ts") if rows else ""
    records: list[dict[str, Any]] = []
    new_lines: list[dict[str, Any]] = []

    if err:
        model_note = "insufficient sample; board unavailable"
        write_to_jarvis(board_ts or "", err, [], model_note, desk_gap)
        ensure_journal_proposal()
        return {"ok": False, "error": err, "appended": 0}

    by_sym = group_by_symbol(rows)
    for symbol in sorted(by_sym.keys()):
        rec = build_symbol_record(symbol, by_sym[symbol], board_ts)
        if rec is None:
            continue
        records.append(rec)
        line = pass_line_from_record(rec)
        if line:
            new_lines.append(line)

    existing = load_passes()
    current_ok = {r["symbol"]: r for r in records if r.get("data_ok")}
    scored_n = score_unresolved(existing, current_ok)
    existing.extend(new_lines)
    write_passes(existing)

    model_note = try_fit_model(existing, records)
    exit_report = run_exits(board_ts, records, by_sym)
    # #region agent log
    _dbg(
        "C",
        "mentor_assistant.py:run_once",
        "model note spoken to jarvis",
        {
            "model_note": model_note,
            "scored_this_pass": scored_n,
            "appended": len(new_lines),
            "symbols": len(records),
        },
    )
    # #endregion
    write_to_jarvis(board_ts, None, records, model_note, desk_gap, exit_report)
    ensure_journal_proposal()

    return {
        "ok": True,
        "board_ts": board_ts,
        "symbols": len(records),
        "appended": len(new_lines),
        "scored": scored_n,
        "to_jarvis": str(TO_JARVIS_PATH),
        "passes": str(PASSES_PATH),
        "model_note": model_note,
        "exits_closed": exit_report.get("closed", 0),
        "book": exit_report.get("book"),
    }


def loop_forever() -> None:
    ASSISTANT_DIR.mkdir(parents=True, exist_ok=True)
    while True:
        if STOP_PATH.exists():
            print(f"STOP present at {STOP_PATH}; exiting.", flush=True)
            return
        result = run_once()
        print(json.dumps(result, ensure_ascii=False), flush=True)
        # Sleep in small slices so STOP is noticed promptly
        for _ in range(LOOP_SECONDS):
            if STOP_PATH.exists():
                print(f"STOP present at {STOP_PATH}; exiting.", flush=True)
                return
            time.sleep(1)


def main() -> None:
    parser = argparse.ArgumentParser(description="Jarvis mentor assistant (read-only)")
    parser.add_argument(
        "--loop",
        action="store_true",
        help="Run forever every 5 minutes until assistant/STOP exists",
    )
    args = parser.parse_args()
    if args.loop:
        loop_forever()
    else:
        result = run_once()
        print(json.dumps(result, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()

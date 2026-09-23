"""FTMO 2-step walk-forward test. Read-only. Never sends an order.

Public 2-step objectives (https://ftmo.com/en/trading-objectives/):
  Phase 1 profit target: 10% of initial simulated capital.
  Phase 2 profit target: 5% of initial simulated capital.
  Maximum daily loss: 5% of initial capital. Floor = Prague-midnight
  balance minus that amount. Equity (balance + open P/L) must stay above it.
  Maximum loss: 10% static from the initial capital.
  Minimum 4 trading days per phase. A trading day is a Prague day on which
  at least one position is opened.
  No calendar deadline. This test still ends a phase at the target, a breach,
  or the bar budget, so a slow grind counts as a miss.

The logistic model is fit only on setups that fully resolved before the
attempt. Weights are frozen for that attempt, including its verification
phase. Threshold, stop, target, and risk are frozen in the constants below
and are not searched after the run.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import MetaTrader5 as mt5
import numpy as np

SYMBOLS = ("EURUSD", "GBPUSD", "USDJPY", "USDCAD")
TF = mt5.TIMEFRAME_H1
BARS = 50000
INITIAL = 100_000.0
PRAGUE = ZoneInfo("Europe/Prague")
TRAIN_MIN = 5000
ATTEMPT_BARS = 24 * 90
HORIZON = 48
STOP_ATR = 1.2
TARGET_R = 2.0
RISK_FRAC = 0.0035
PROB_MIN = 0.56
DAILY_HALT = 0.03
MAX_OPEN = 2
MAX_NEW_PER_DAY = 2
MIN_TRAIN = 40
OUT = r"C:\Users\C2K\Desktop\MT5 to agent\JARVIS V1\research\ftmo_forward\last_report.json"


def rsi(close: np.ndarray, n: int = 14) -> np.ndarray:
    out = np.full(close.shape, np.nan)
    delta = np.diff(close, prepend=close[0])
    up = np.clip(delta, 0, None)
    dn = np.clip(-delta, 0, None)
    avg_up = np.zeros_like(close)
    avg_dn = np.zeros_like(close)
    if len(close) <= n:
        return out
    avg_up[n] = up[1 : n + 1].mean()
    avg_dn[n] = dn[1 : n + 1].mean()
    for i in range(n + 1, len(close)):
        avg_up[i] = (avg_up[i - 1] * (n - 1) + up[i]) / n
        avg_dn[i] = (avg_dn[i - 1] * (n - 1) + dn[i]) / n
        rs = avg_up[i] / avg_dn[i] if avg_dn[i] > 0 else np.inf
        out[i] = 100.0 - 100.0 / (1.0 + rs)
    return out


def atr(high: np.ndarray, low: np.ndarray, close: np.ndarray, n: int = 14) -> np.ndarray:
    prev = np.roll(close, 1)
    prev[0] = close[0]
    tr = np.maximum(high - low, np.maximum(np.abs(high - prev), np.abs(low - prev)))
    out = np.full(close.shape, np.nan)
    if len(close) <= n:
        return out
    out[n] = tr[1 : n + 1].mean()
    for i in range(n + 1, len(close)):
        out[i] = (out[i - 1] * (n - 1) + tr[i]) / n
    return out


def sma(x: np.ndarray, n: int) -> np.ndarray:
    out = np.full(x.shape, np.nan)
    if len(x) < n:
        return out
    c = np.cumsum(x)
    out[n - 1 :] = (c[n - 1 :] - np.concatenate([[0.0], c[:-n]])) / n
    return out


@dataclass
class Series:
    symbol: str
    time: np.ndarray
    open: np.ndarray
    high: np.ndarray
    low: np.ndarray
    close: np.ndarray
    spread: np.ndarray
    feat: np.ndarray
    point: float


@dataclass
class Setup:
    symbol: str
    signal: int
    entry_i: int
    resolved_i: int | None
    side: int
    entry: float
    stop: float
    target: float
    spread: float
    risk_dist: float
    feat: np.ndarray
    win: float | None
    r: float | None


@dataclass
class Pos:
    setup: Setup
    risk_dollars: float


def load_symbol(symbol: str) -> Series | None:
    info = mt5.symbol_info(symbol)
    if info is None:
        return None
    if not info.visible:
        mt5.symbol_select(symbol, True)
    rates = mt5.copy_rates_from_pos(symbol, TF, 0, BARS)
    if rates is None or len(rates) < TRAIN_MIN + 200:
        return None
    o = rates["open"].astype(np.float64)
    h = rates["high"].astype(np.float64)
    l = rates["low"].astype(np.float64)
    c = rates["close"].astype(np.float64)
    t = rates["time"].astype(np.int64)
    spr = rates["spread"].astype(np.float64) * float(info.point)
    a = atr(h, l, c)
    r = rsi(c)
    s20 = sma(c, 20)
    s50 = sma(c, 50)
    ret1 = np.zeros_like(c)
    ret4 = np.zeros_like(c)
    ret24 = np.zeros_like(c)
    ret1[1:] = (c[1:] - c[:-1]) / c[:-1]
    ret4[4:] = (c[4:] - c[:-4]) / c[:-4]
    ret24[24:] = (c[24:] - c[:-24]) / c[:-24]
    dist20 = (c - s20) / np.where(a > 0, a, np.nan)
    dist50 = (c - s50) / np.where(a > 0, a, np.nan)
    feat = np.column_stack([ret1, ret4, ret24, (r - 50.0) / 50.0, dist20, dist50, a / c])
    return Series(symbol, t, o, h, l, c, spr, feat, float(info.point))


def side_trend(feat_row: np.ndarray, prev_dist20: float) -> int:
    dist50, ret24 = float(feat_row[5]), float(feat_row[2])
    if dist50 > 0.5 and ret24 > 0.0:
        return 1
    if dist50 < -0.5 and ret24 < 0.0:
        return -1
    return 0


def side_fade(feat_row: np.ndarray, prev_dist20: float) -> int:
    dist20, dist50 = float(feat_row[4]), float(feat_row[5])
    if dist50 > 0.0 and dist20 < -1.2 and prev_dist20 < dist20:
        return 1
    if dist50 < 0.0 and dist20 > 1.2 and prev_dist20 > dist20:
        return -1
    return 0


def side_at(feat_row: np.ndarray, prev_dist20: float) -> int:
    dist20, dist50, ret24 = float(feat_row[4]), float(feat_row[5]), float(feat_row[2])
    if dist50 > 0.25 and prev_dist20 < 0.0 and dist20 > 0.0 and ret24 > 0.0:
        return 1
    if dist50 < -0.25 and prev_dist20 > 0.0 and dist20 < 0.0 and ret24 < 0.0:
        return -1
    return 0


SIDE_FN = side_at


def build_setups(s: Series) -> list[Setup]:
    out: list[Setup] = []
    n = len(s.close)
    recent: list[float] = []
    for i in range(1, n - 1):
        row = s.feat[i]
        prev = s.feat[i - 1]
        if not np.all(np.isfinite(row)) or not np.all(np.isfinite(prev)):
            continue
        side = SIDE_FN(row, float(prev[4]))
        if side == 0:
            continue
        a = float(row[6] * s.close[i])
        if not math.isfinite(a) or a <= 0:
            continue
        entry = float(s.open[i + 1])
        stop_dist = STOP_ATR * a
        if stop_dist <= 0:
            continue
        stop = entry - side * stop_dist
        target = entry + side * stop_dist * TARGET_R
        spread = float(s.spread[i]) if s.spread[i] > 0 else s.point * 15
        recent_r = float(np.mean(recent[-20:])) if recent else 0.0
        feat = np.concatenate([row, [float(side), recent_r]])
        resolved_i = None
        r_mult = None
        win = None
        for j in range(i + 1, min(n, i + 1 + HORIZON)):
            hi, lo = float(s.high[j]), float(s.low[j])
            hit_stop = lo <= stop if side > 0 else hi >= stop
            hit_tgt = hi >= target if side > 0 else lo <= target
            exit_px = None
            if hit_stop:
                exit_px = stop
            elif hit_tgt:
                exit_px = target
            if exit_px is None:
                continue
            r_mult = ((exit_px - entry) * side - spread) / stop_dist
            win = 1.0 if r_mult > 0 else 0.0
            resolved_i = j
            break
        if r_mult is not None:
            recent.append(r_mult)
        out.append(
            Setup(s.symbol, i, i + 1, resolved_i, side, entry, stop, target, spread, stop_dist, feat, win, r_mult)
        )
    return out


def fit_logit(x: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray] | None:
    if len(y) < MIN_TRAIN or len(np.unique(y)) < 2:
        return None
    mu = x.mean(axis=0)
    sd = x.std(axis=0)
    sd[sd < 1e-12] = 1.0
    z = np.column_stack([np.ones(len(x)), (x - mu) / sd])
    w = np.zeros(z.shape[1])
    for _ in range(30):
        p = 1.0 / (1.0 + np.exp(-np.clip(z @ w, -30, 30)))
        grad = z.T @ (y - p) / len(y) - 1.0 * w / len(y)
        ww = np.clip(p * (1.0 - p), 1e-6, None)
        hess = (z.T * ww) @ z / len(y) + np.eye(z.shape[1]) * (1.0 / len(y))
        try:
            step = np.linalg.solve(hess, grad)
        except np.linalg.LinAlgError:
            return None
        w += step
        if np.max(np.abs(step)) < 1e-6:
            break
    return w, mu, sd


def predict(model, row: np.ndarray) -> float:
    w, mu, sd = model
    z = np.concatenate([[1.0], (row - mu) / sd])
    return float(1.0 / (1.0 + math.exp(-max(-30.0, min(30.0, float(z @ w))))))


def prague_day(ts: int):
    return datetime.fromtimestamp(int(ts), timezone.utc).astimezone(PRAGUE).date()


def iso(ts: int) -> str:
    return datetime.fromtimestamp(int(ts), timezone.utc).isoformat()


def run_phase(
    clock: np.ndarray,
    by_entry: dict[tuple[str, int], Setup],
    index_of: dict[str, dict[int, int]],
    books: dict[str, Series],
    model,
    start: int,
    end: int,
    target_frac: float,
) -> tuple[dict, int]:
    balance = INITIAL
    day = None
    day_start = INITIAL
    traded_days: set = set()
    new_today = 0
    breach = None
    trades = 0
    wins = 0
    paused = None
    positions: list[Pos] = []
    i = start
    while i < end and breach is None and balance < INITIAL * (1.0 + target_frac):
        ts = int(clock[i])
        d = prague_day(ts)
        if day != d:
            day = d
            day_start = balance
            new_today = 0
            if paused is not None and paused != d:
                paused = None

        still: list[Pos] = []
        for p in positions:
            s = books[p.setup.symbol]
            bar = index_of[p.setup.symbol].get(ts)
            if bar is None:
                still.append(p)
                continue
            hi, lo = float(s.high[bar]), float(s.low[bar])
            side = p.setup.side
            hit_stop = lo <= p.setup.stop if side > 0 else hi >= p.setup.stop
            hit_tgt = hi >= p.setup.target if side > 0 else lo <= p.setup.target
            exit_px = p.setup.stop if hit_stop else (p.setup.target if hit_tgt else None)
            if exit_px is None:
                still.append(p)
                continue
            r = ((exit_px - p.setup.entry) * side - p.setup.spread) / p.setup.risk_dist
            pnl = r * p.risk_dollars
            balance += pnl
            trades += 1
            wins += int(pnl > 0)
        positions = still

        floating = 0.0
        remaining_risk = 0.0
        for p in positions:
            s = books[p.setup.symbol]
            bar = index_of[p.setup.symbol].get(ts)
            if bar is None:
                remaining_risk += p.risk_dollars
                continue
            px = float(s.close[bar])
            side = p.setup.side
            move = (px - p.setup.entry) * side - p.setup.spread
            r = move / p.setup.risk_dist
            floating += r * p.risk_dollars
            left = (px - p.setup.stop) * side
            if left > 0:
                remaining_risk += (left / p.setup.risk_dist) * p.risk_dollars
        equity = balance + floating
        daily_floor = day_start - 0.05 * INITIAL
        max_floor = INITIAL * 0.90
        if equity <= daily_floor:
            breach = "max_daily_loss"
        elif equity <= max_floor:
            breach = "max_loss"
        elif equity <= day_start - DAILY_HALT * INITIAL or paused == d:
            if positions and paused != d:
                for p in positions:
                    s = books[p.setup.symbol]
                    bar = index_of[p.setup.symbol].get(ts)
                    px = float(s.close[bar]) if bar is not None else p.setup.entry
                    r = ((px - p.setup.entry) * p.setup.side - p.setup.spread) / p.setup.risk_dist
                    balance += r * p.risk_dollars
                    trades += 1
                    wins += int(r > 0)
                positions = []
                equity = balance
            paused = d
        elif model is not None and new_today < MAX_NEW_PER_DAY and len(positions) < MAX_OPEN:
            held = {p.setup.symbol for p in positions}
            for sym in SYMBOLS:
                if sym in held or sym not in books or len(positions) >= MAX_OPEN or new_today >= MAX_NEW_PER_DAY:
                    continue
                setup = by_entry.get((sym, i))
                if setup is None:
                    continue
                if equity - remaining_risk - RISK_FRAC * INITIAL <= max(daily_floor, max_floor):
                    continue
                p_win = predict(model, setup.feat)
                if p_win < PROB_MIN:
                    continue
                pos = Pos(setup, RISK_FRAC * INITIAL)
                positions.append(pos)
                held.add(sym)
                new_today += 1
                traded_days.add(d)
                s = books[sym]
                bar = index_of[sym].get(ts)
                if bar is None:
                    continue
                hi, lo = float(s.high[bar]), float(s.low[bar])
                side = setup.side
                hit_stop = lo <= setup.stop if side > 0 else hi >= setup.stop
                hit_tgt = hi >= setup.target if side > 0 else lo <= setup.target
                exit_px = setup.stop if hit_stop else (setup.target if hit_tgt else None)
                if exit_px is None:
                    continue
                positions.pop()
                r = ((exit_px - setup.entry) * side - setup.spread) / setup.risk_dist
                balance += r * pos.risk_dollars
                trades += 1
                wins += int(r > 0)
        i += 1

    for p in positions:
        if breach is not None:
            break
        s = books[p.setup.symbol]
        ts = int(clock[min(i, len(clock) - 1)])
        bar = index_of[p.setup.symbol].get(ts)
        px = float(s.close[bar]) if bar is not None else p.setup.entry
        r = ((px - p.setup.entry) * p.setup.side - p.setup.spread) / p.setup.risk_dist
        balance += r * p.risk_dollars
        trades += 1
        wins += int(r > 0)

    passed = breach is None and balance >= INITIAL * (1.0 + target_frac) and len(traded_days) >= 4
    result = {
        "passed": passed,
        "breach": breach,
        "balance": round(balance, 2),
        "return_pct": round((balance / INITIAL - 1.0) * 100.0, 3),
        "trades": trades,
        "wins": wins,
        "trading_days": len(traded_days),
        "bars": i - start,
    }
    return result, i


def train_for(setups: list[Setup], before_i: int):
    rows = []
    ys = []
    for s in setups:
        if s.resolved_i is None or s.win is None or s.resolved_i >= before_i:
            continue
        rows.append(s.feat)
        ys.append(s.win)
    if len(ys) < MIN_TRAIN:
        return None, len(ys), None
    x = np.vstack(rows)
    y = np.asarray(ys, dtype=np.float64)
    model = fit_logit(x, y)
    return model, len(ys), round(float(y.mean()), 3)


def main() -> None:
    if not mt5.initialize():
        raise SystemExit(f"mt5.initialize failed: {mt5.last_error()}")
    try:
        books: dict[str, Series] = {}
        for sym in SYMBOLS:
            s = load_symbol(sym)
            if s is not None:
                books[sym] = s
        if len(books) < 2:
            raise SystemExit("not enough history")
        common = set(books[next(iter(books))].time.tolist())
        for s in books.values():
            common &= set(s.time.tolist())
        clock = np.array(sorted(common), dtype=np.int64)
        if len(clock) < TRAIN_MIN + 200:
            raise SystemExit(f"common clock too short: {len(clock)}")
        index_of = {sym: {int(t): i for i, t in enumerate(s.time.tolist())} for sym, s in books.items()}
        setups: list[Setup] = []
        by_entry: dict[tuple[str, int], Setup] = {}
        clock_index = {int(t): i for i, t in enumerate(clock.tolist())}
        for sym, s in books.items():
            for setup in build_setups(s):
                entry_ts = int(s.time[setup.entry_i]) if setup.entry_i < len(s.time) else None
                if entry_ts is None or entry_ts not in clock_index:
                    continue
                ci = clock_index[entry_ts]
                setup.entry_i = ci
                if setup.resolved_i is not None:
                    rts = int(s.time[min(setup.resolved_i, len(s.time) - 1)])
                    k = int(np.searchsorted(clock, rts, side="left"))
                    setup.resolved_i = k if k < len(clock) else None
                    if setup.resolved_i is None:
                        setup.win = None
                        setup.r = None
                by_entry[(sym, ci)] = setup
                setups.append(setup)

        attempts = []
        cursor = TRAIN_MIN
        n = len(clock)
        while cursor + 200 < n:
            stop = min(n - 1, cursor + ATTEMPT_BARS)
            model, n_train, train_wr = train_for(setups, cursor)
            phase1, used = run_phase(clock, by_entry, index_of, books, model, cursor, stop, 0.10)
            phase2 = None
            both = False
            if phase1["passed"] and used + 50 < n:
                phase2, used2 = run_phase(clock, by_entry, index_of, books, model, used, min(n - 1, used + ATTEMPT_BARS), 0.05)
                both = bool(phase2["passed"])
                used = used2
            attempts.append(
                {
                    "start_utc": iso(int(clock[cursor])),
                    "train_resolved": n_train,
                    "train_win_rate": train_wr,
                    "model_fit": model is not None,
                    "phase1": phase1,
                    "phase2": phase2,
                    "both_phases": both,
                }
            )
            nxt = used if used > cursor else stop
            if nxt <= cursor:
                nxt = cursor + ATTEMPT_BARS
            cursor = nxt
            if len(attempts) >= 12:
                break

        p1 = sum(1 for a in attempts if a["phase1"]["passed"])
        both = sum(1 for a in attempts if a["both_phases"])
        report = {
            "read_only": True,
            "orders_sent": 0,
            "rules_source": "https://ftmo.com/en/trading-objectives/",
            "product": "FTMO Challenge 2-step",
            "rules": {
                "account": "simulated 100000",
                "phase1_target_pct": 10,
                "phase2_target_pct": 5,
                "max_daily_loss_pct_of_initial": 5,
                "daily_halt_used_pct": DAILY_HALT * 100,
                "max_loss_pct_static": 10,
                "min_trading_days": 4,
                "day_boundary": "Europe/Prague",
                "risk_frac": RISK_FRAC,
                "prob_min": PROB_MIN,
                "stop_atr": STOP_ATR,
                "target_r": TARGET_R,
            },
            "method": "Walk-forward logistic regression on pullback-continuation setups. Fit uses only trades resolved before the attempt. Constants were not searched on these windows.",
            "symbols": list(books),
            "bars_common": int(n),
            "first_bar_utc": iso(int(clock[0])),
            "last_bar_utc": iso(int(clock[-1])),
            "attempts": len(attempts),
            "phase1_passes": p1,
            "phase1_pass_rate": round(p1 / len(attempts), 3) if attempts else 0,
            "both_phases_passes": both,
            "both_phases_pass_rate": round(both / len(attempts), 3) if attempts else 0,
            "consistent": bool(len(attempts) >= 4 and both / len(attempts) >= 0.5) if attempts else False,
            "detail": attempts,
        }
        with open(OUT, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        print(json.dumps({k: report[k] for k in report if k != "detail"}, indent=2))
    finally:
        mt5.shutdown()


def scan_design() -> None:
    """Expectancy on the design slice only. Does not score the forward attempts."""
    if not mt5.initialize():
        raise SystemExit(mt5.last_error())
    try:
        books = {}
        for sym in SYMBOLS:
            s = load_symbol(sym)
            if s is not None:
                books[sym] = s
        common = None
        for s in books.values():
            st = set(s.time.tolist())
            common = st if common is None else common & st
        clock = np.array(sorted(common), dtype=np.int64)
        design_end = int(clock[2500])
        print(f"design_end_utc {iso(design_end)} symbols {list(books)}")
        global STOP_ATR, TARGET_R, SIDE_FN
        for name, fn in (("pullback", side_at), ("trend", side_trend), ("fade", side_fade)):
            SIDE_FN = fn
            for stop in (1.2, 1.6):
                for target in (1.0, 1.5):
                    STOP_ATR = stop
                    TARGET_R = target
                    rs = []
                    for s in books.values():
                        for setup in build_setups(s):
                            sig_ts = int(s.time[setup.signal])
                            res_ts = int(s.time[setup.resolved_i]) if setup.resolved_i is not None else None
                            if setup.r is None or res_ts is None or res_ts >= design_end or sig_ts >= design_end:
                                continue
                            rs.append(setup.r)
                    if not rs:
                        print(f"{name} stop {stop} target {target} n 0")
                        continue
                    arr = np.asarray(rs)
                    print(
                        f"{name} stop {stop} target {target} n {len(arr)} win {float((arr > 0).mean()):.3f} meanR {float(arr.mean()):.3f}"
                    )
    finally:
        mt5.shutdown()


if __name__ == "__main__":
    import sys

    if "--scan" in sys.argv:
        scan_design()
    else:
        main()

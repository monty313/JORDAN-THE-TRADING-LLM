# Knowledge harness — dual CCI extreme (any timeframe)

Measurable relations only. Not a trade ticket. Does not place orders.
Does not change S1–S4 `act`, `tide`, or `strategy_direction_conflict`.
Does not replace the Dual CCI slingshot (S1 uses SMA 2 shift +2). This harness uses a different rail.

---

## 1. Primitive

On one timeframe, last closed bar (series index 1):

- `CCI(30)` and `CCI(100)`, applied price = typical `(high + low + close) / 3`, same as S1.
- `SMA(1) shift +4` of each CCI. Period 1 does not smooth. The value is that CCI four closed bars earlier, drawn on the current closed bar.

Forming bar (index 0) is telemetry. It does not change the stamp.

---

## 2. Level (momentum identification)

\[
\text{level} =
\begin{cases}
\text{BUY} & \text{if } CCI30 > +100 \text{ and } CCI100 > +100 \\
\text{SELL} & \text{if } CCI30 < -100 \text{ and } CCI100 < -100 \\
\text{NONE} & \text{otherwise}
\end{cases}
\]

Equal to ±100 is not beyond the level. One CCI beyond and the other not is NONE. This stamp does not cancel S1, S2, S3, S4, G1–G7, H1, or L1–L4.

---

## 3. Continuation confirmation

Only after the level is already BUY or SELL:

\[
\text{confirm BUY} = \text{level BUY and } CCI30 > SMA^{+4}(CCI30) \text{ and } CCI100 > SMA^{+4}(CCI100)
\]

\[
\text{confirm SELL} = \text{level SELL and } CCI30 < SMA^{+4}(CCI30) \text{ and } CCI100 < SMA^{+4}(CCI100)
\]

Equal to the SMA is not confirmation. A failed confirmation leaves the level stamp on. It does not flip the level off and it does not change any other sensor.

---

## 4. Timeframes

Same list on every pass. Each timeframe is its own row. No cross-timeframe vote.

| id | TF | plain name |
|---|---|---|
| C1 | M1 | M1 dual CCI extreme |
| C2 | M5 | M5 dual CCI extreme |
| C3 | M15 | M15 dual CCI extreme |
| C4 | M30 | M30 dual CCI extreme |
| C5 | H1 | H1 dual CCI extreme |
| C6 | H4 | H4 dual CCI extreme |
| C7 | D1 | D1 dual CCI extreme |

Board: `family=GATE`, `set=C`, `act=n/a`, `topology=dual_cci_extreme`.

- Level BUY: `active=ACTIVE`, `tide=long_only`, `state=cci_extreme` or `cci_extreme_confirmed`, reason `cN_level_buy` or `cN_confirm_buy`.
- Level SELL: `active=ACTIVE`, `tide=short_only`, reason `cN_level_sell` or `cN_confirm_sell`.
- NONE: `active=INACTIVE`, `tide=flat`, reason `cN_not_both`.

`raw_a` CCI30, `raw_b` CCI100, `raw_c` SMA of CCI30, `raw_d` SMA of CCI100.

Phone push stays official FIRE/KILL only. These rows do not push.

---

## 5. What this is not

No minimum number of timeframes licenses an entry. That cutoff stays UNDEFINED. No order. No close. No change to an open ticket.

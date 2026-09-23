# Knowledge harness — multi-TF RSI vs SMA(1) shift +4 alignment

Measurable relations only. Not a trade ticket. Not a pep talk. Does not place orders.
Demo mentoring / research logging. Does not rewrite `007_*.md`.

---

## 1. Primitive

**MT5 identity.** `SMA(period=1, shift=+4)` of a series is that series’ value **four bars ago**, drawn on the current bar. Period 1 does not smooth; the shift is a displaced rail.

**Existing gate (do not redefine).** `Daily_RSI_Tide_Gate.md` and board `G1` compare **Daily RSI(14)** (close) to **SMA(1) shift +4 applied to that RSI** (First Indicator’s Data) — **not** price to a price SMA. Board raw: `daily_rsi`, `daily_rsi_sma_shift4`. Side: above → long-only permission; below → short-only; hugging / no clean separation → chop / undefined at the gate layer.

**Match to Mark’s sentence.** “Buys stay above SMA(1) shifted +4; sells stay below” is the **same side logic** as that RSI gate, not a separate price-SMA rule.

**Multi-timeframe extension (this harness).** On each timeframe below, compute the **same** relation:

\[
\text{side}(TF) =
\begin{cases}
\text{ABOVE} & \text{if } RSI(14)_{TF} > SMA_1^{+4}(RSI(14)_{TF}) \\
\text{BELOW} & \text{if } RSI(14)_{TF} < SMA_1^{+4}(RSI(14)_{TF}) \\
\text{FLAT} & \text{if equal}
\end{cases}
\]

Use the **last closed bar** on that TF (series index 1), consistent with board closed-bar doctrine. Forming-bar RSI is telemetry only; it does not change a logged side.

Do **not** merge this with a price-vs-price SMA(1)+4. That second relation is **not** defined by the Daily RSI tide gate and is out of scope here.

---

## 2. Per-timeframe side

Jarvis board / official sets already use these TFs (SCHEMA `anchor_tf` / `htf1_tf` / `htf2_tf` across sets 1–4, plus G1 on D1):

| TF | Board label |
|---|---|
| M1 | 1m |
| M5 | 5m |
| M15 | 15m |
| M30 | 30m |
| H1 | 1h |
| H4 | 4h |
| D1 | 1d |

For each TF, record `side ∈ {ABOVE, BELOW, FLAT}`.

- **ABOVE** → buy-side permission stamp on that TF only.
- **BELOW** → sell-side permission stamp on that TF only.
- **FLAT** → equal RSI and rail; **not** a buy and **not** a sell. FLAT does not increment either side’s alignment count.

D1 of this vector is the same relation G1 already stamps; other TFs are the harness’s multi-TF measurement layer.

---

## 3. Alignment count

Let \(S\) be a non-FLAT side (`ABOVE` or `BELOW`).

\[
\text{alignment\_count}(S) = \#\{\, TF \in \{M1,M5,M15,M30,H1,H4,D1\} : side(TF) = S \,\}
\]

Also record `alignment_side` = the side with the larger count, or `SPLIT` if ABOVE and BELOW counts are equal (FLATs ignored for the split test).

**The count is the measurement.** Do **not** invent a cutoff such as “3 of 7 means fire,” “majority licenses entry,” or any minimum that would change `act`.

**Undefined until outcomes exist:** any minimum alignment count that would *license an entry* stays **UNDEFINED**. Log the raw integer every pass; learn the threshold later from scored outcomes — do not invent one in this file.

---

## 4. Pullback

**Definition.** Relative to a chosen **anchor** TF (the row’s `anchor_tf` on the board — Set 1 = M1, Set 2 = M5, Set 3 = M15, Set 4 = M30):

1. Anchor side is **ABOVE** or **BELOW** (not FLAT).
2. That side is **opposite** the side held by the higher timeframes under study.
3. Higher TFs = every listed TF strictly slower than the anchor (e.g. anchor M5 → M15, M30, H1, H4, D1).

**Agreeing higher count (raw):**

\[
\text{htf\_agree\_count} = \#\{\, TF > \text{anchor} : side(TF) = S_{htf} \,\},
\]

where \(S_{htf}\) is the majority non-FLAT side among higher TFs (or `NONE` if no higher TF is non-FLAT, or `SPLIT` if ABOVE and BELOW higher counts tie).

A **pullback flag** is true only when:

- Anchor side ≠ \(S_{htf}\), and
- \(S_{htf} \in \{ABOVE, BELOW\}\), and
- Anchor side ∈ {ABOVE, BELOW}, and
- `htf_agree_count` meets the minimum below.

**Minimum higher TFs that must agree before calling it a pullback:** doctrine files (`Daily_RSI_Tide_Gate.md`, SCHEMA, desk_state, 007) do **not** give that integer. Therefore the minimum is **UNDEFINED**. Until Mark accepts a number, **always log the raw `htf_agree_count`** and do not assert “this is a pullback” as a hard label that drives action — treat the raw count as the feature.

**Non-effect.** A pullback (or a raw htf-agree count) is **not** by itself a `FIRE`, a `KILL`, or a change to S1–S4 `act`.

---

## 5. Momentum vs reversion

Two layers. Do not mix them with `act`.

| Label | Measurable meaning on this board |
|---|---|
| **Momentum (continuation / launch)** | The harness tide side (`alignment_side` or G1/`ABOVE`→long / `BELOW`→short) **agrees** with the official setup’s `tide` (`long_only` / `short_only`) on that symbol×set row. Alignment with S1 Dual CCI slingshot, S2 Dual BB pullback, S3 Shifted envelope, or S4 RSI-BB tension snap tide = continuation context. |
| **Reversion (toward an existing mean)** | Anchor is opposing the higher-TF side (pullback feature above) **and** price / oscillator is moving toward a mean the board **already** computes — do not invent periods. Named means: **S2** tight middle (`bb10_mid` / Dual BB pullback reclaim), **S5** `BB(20)` middle and `BB(200)` middle on the row’s HTFs (`bb20_mid_htf*`, `bb200_mid_htf*`). |

Momentum and reversion here are **classification labels for the log**, not licenses to trade.

---

## 6. What to log every pass

Append one research line (JSONL or LEARNING_LOG table — same fields). Do **not** change `forced_signals.jsonl` schema or the forced-signal research loop.

| Field | Source / rule |
|---|---|
| `timestamp` | Local clock + board `ts` if read |
| `symbol` | Exact MT5 symbol |
| `side_M1` … `side_D1` | `ABOVE` / `BELOW` / `FLAT` per §2 |
| `alignment_count_above` | Integer 0–7 |
| `alignment_count_below` | Integer 0–7 |
| `alignment_side` | `ABOVE` / `BELOW` / `SPLIT` |
| `anchor_tf` | From the official row under study |
| `htf_agree_count` | Raw integer (§4) |
| `pullback_min_undefined` | Always `true` until Mark accepts a minimum |
| `s1_act` `s2_act` `s3_act` `s4_act` | Official board `act` beside the harness (same symbol×set) |
| `spread_points` | Board `spread_points` |
| `outcome_status` | Later: same buckets as forced-signal research (`PROFITABLE` / `NOT_PROFITABLE` / `UNRESOLVED`, etc.) — **do not invent new buckets** |

**Learning method.** Entry timing is learned by comparing `outcome_status` (and net points after spread) **grouped by** `alignment_count_*` and by `htf_agree_count`. No orders from this file.

---

## 7. Non-interference

- This harness does **not** change S1–S4 `act`, `tide`, or `strategy_direction_conflict`.
- **G1** stays a warning / permission column. Multi-TF extension is research measurement; it does not promote G1 into a scalp fire.
- Daily RSI, Heikin Ashi (`H1` door), fractals (`L4`), and spread do **not** license a trade.
- Desk act stays **`WAIT_NO_TRADE`** while **Today target** and **Today risk floor** in `desk_state.md` are blank. Name technical `act` beside it only.
- No invented chop/expansion cutoffs. S5 remains `UNDEFINED` where doctrine cutoffs are missing; quote BB middles, do not invent thresholds.

---

## 8. Learning questions (falsifiable)

Leave \(N\), \(K\) as variables. No fake backtest numbers. No claimed accuracy.

1. When `alignment_count` for the trade side equals \(N\) and the anchor is opposing the higher-TF majority (`htf_agree_count` = \(K\)), is the average 5-minute net result after spread positive?
2. For fixed \(N\), does average 5-minute net after spread improve as \(K\) increases?
3. When `alignment_side` disagrees with official S1–S4 `tide` on the same symbol×set, is `outcome_status=NOT_PROFITABLE` more frequent than when they agree (same \(N\))?
4. When D1 alone is `ABOVE`/`BELOW` (G1) but `alignment_count` for that side is \(N=1\), does the 5-minute result after spread differ from the same side at \(N \ge 4\)?
5. Conditional on official `act=FIRE_BUY` or `FIRE_SELL`, does grouping by \(N\) change the rate of `PROFITABLE` vs `NOT_PROFITABLE` after the forced-signal horizon?

Answer only from logged rows. Until enough outcomes exist, state “insufficient sample” — do not invent a cutoff.

---

## Cite

- `C:\Users\C2K\Desktop\Strategies - Copy\Daily_RSI_Tide_Gate.md` — RSI(14) vs SMA(1)+4 on RSI; gate not trigger.
- `JARVIS V1/SCHEMA.md` — `tide`, `act`, `cmp`, `anchor_tf`, G1 raws, S2/S5 means.
- `JARVIS V1/desk_state.md` — blank target / risk floor → desk `WAIT_NO_TRADE`.
- `007_JARVIS_Momentum_Conservation_Trading_Mentor_Baseline.md` (read-only) — official sets M1–D1 stack; S1 Dual CCI slingshot, S2 Dual BB pullback, S3 Shifted envelope, S4 RSI-BB tension snap; S5 regime evidence.
- Forced-signal outcomes: `JARVIS V1/research/forced_signals.jsonl` (`outcome_status` buckets unchanged).

---

*Saved for Mark’s multi-TF SMA(1) shift +4 alignment lesson. Alignment entry cutoffs and pullback minimums remain UNDEFINED until logged outcomes justify a Proposed JOURNAL row he accepts.*

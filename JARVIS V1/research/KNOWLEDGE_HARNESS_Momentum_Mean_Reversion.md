# Knowledge harness — momentum vs mean reversion (SMA(1) shift +4)

Agent learning note. Not a trade ticket. Not a pep talk. Demo mentoring only.

## Goal of this harness

Stay oriented by quantifying **momentum** and **mean reversion** across the official multi-timeframe sensor stack (S1–S4 and related indicators). The directional lever Mark wants the agent to treat as real — kindergarten-simple on purpose — is the side of a **SMA(1) shifted by +4**:

- A **buy** thesis stays alive only while the tide measure stays **above** SMA(1) shift +4.
- A **sell** thesis stays alive only while the tide measure stays **below** SMA(1) shift +4.

Cross back through that shifted average kills the thesis on that side. The harness trains the agent to name and log that relation before it speaks an act — not to invent a new order from it.

## What Mark stated vs what is already defined

### Mark (this pass — learning target)

- Easiest orientation: measure momentum and reversion to the mean on **multiple timeframes** with indicators.
- Use the above/below SMA(1) shift +4 relation to predict which side of price is still allowed.
- Treat the lever as operational, not slogan.

### Already defined (computable rule — cite, do not invent)

| Source | What it defines |
|---|---|
| `Strategies - Copy/Daily_RSI_Tide_Gate.md` | **Only computable SMA(1)+4 rule today:** Daily **RSI(14)** vs SMA(1) shift +4 applied to **First Indicator’s Data** (RSI window), not to price. SMA period 1 is a forward-shifted echo of RSI four bars ahead — a displaced rail, not a smoothed trend. Above rail → long-only permission; below → short-only. Gate, not trigger. Kill when RSI closes back across the rail against the side. |
| `007_…Baseline.md` § S6 (read-only) | Daily RSI Tide is a **secondary diagnostic** / higher-order tide context (esp. Set 4). Report as `warning_context`. Never a standalone `FIRE`. Does not time a Set 1 scalp. |
| Board / SCHEMA `G1` | Daily RSI tide column: warning / permission stamp (`rsi14` vs `sma1_shift4`). Does **not** mutate S1–S4 `act`, `tide`, or `strategy_direction_conflict`. |

**Where they match:** Mark’s buy-above / sell-below SMA(1) shift +4 is the same side logic as the Daily RSI tide gate and G1.

**Where Mark’s sentence is wider:** He named multi-timeframe indicators and momentum/mean-reversion quantification in general. The gate document and G1 are **D1 RSI(14) vs SMA(1)+4 only**. Keep Mark’s wider aim as the **learning target**. Keep the Daily RSI / G1 formula as the **only computable rule**. Do not invent extra timeframe formulas, chop/expansion cutoffs, or a price-applied SMA(1)+4 that those files do not define.

Official S1–S4 already quantify momentum (e.g. Dual CCI, RSI-BB) and mean reversion / pullback (e.g. Dual BB, shifted envelope) on the immutable sets. Score those rows against the **existing** G1 side stamp; do not invent a second SMA(1)+4 sensor per TF.

## Student test (answer before acting)

Before speaking an act or ranking a thesis, the agent must answer:

1. **Which timeframe?** (For the computable gate: Daily / D1.)
2. **Which indicator?** (For the computable gate: RSI(14) on close, with SMA(1) shift +4 on First Indicator’s Data.)
3. **What is the SMA(1) value** (board `sma1_shift4` or equivalent)?
4. **What is the shift-+4 value** on the live measure (board `rsi14` or equivalent)?
5. **Is the live measure above or below** that shifted average?
6. **What kills the thesis?** A close (or stamped cross) back through that same shifted average against the thesis side.

If any of (1)–(5) cannot be answered from board / cited docs, say so and do not pretend the gate fired a scalp.

## Explicit non-permissions

This harness does **not**:

- Place, modify, or close trades.
- Change S1–S4 `act`, `tide`, or `strategy_direction_conflict`.
- Promote G1 / daily RSI into a scalp fire (it stays a warning / permission column).
- Grant L1–L4 legacy doors or Heikin Ashi (`H1`) a veto from this note.
- Override desk act: while **Today target** and **Today risk floor** in `JARVIS V1/desk_state.md` are blank, desk act stays `WAIT_NO_TRADE` (name technical act beside it only).
- Bring fractal L4 batches into scope.

## What to log

| Field | Content |
|---|---|
| Date | Calendar date (local) |
| Time | Local clock |
| Goal of the pass | One sentence (why this read) |
| Above/below relation | Measure vs SMA(1) shift +4 (values + side) |
| Outcome later | Did later price / thesis agree with the side of the shifted average? That is the success/failure lesson relative to intuition. |

Append lessons to `JARVIS V1/LEARNING_LOG.md`. Doctrine edits only via Proposed rows in `JARVIS V1/JOURNAL.md` for Mark — never rewrite `007_*.md` from the agent.

## Cite

- `C:\Users\C2K\Desktop\Strategies - Copy\Daily_RSI_Tide_Gate.md` — SMA(1) shift +4 definition and D1 RSI gate.
- `007_JARVIS_Momentum_Conservation_Trading_Mentor_Baseline.md` § S6 — Daily RSI as warning context (read-only).
- `JARVIS V1/SCHEMA.md` / board `G1` — gate column role.
- Prior learning stamp: `LEARNING_LOG.md` 2026-09-22 06:46 — same definition, no invented cutoffs.

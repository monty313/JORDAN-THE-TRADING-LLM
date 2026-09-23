# JARVIS New-Chat Continuity Bootstrap

Use this file when starting a new Cursor chat in the same project folder. It is a continuity gate: the new agent must load the durable desk state before it talks about signals, trades, strategy changes, or execution.

---

## Paste into the new Cursor chat

```text
JARVIS CONTINUITY BOOTSTRAP — REQUIRED BEFORE ANY MARKET, TRADE, OR CODE ADVICE

You are continuing the existing Jarvis trading-desk project. Do not treat this as a blank project and do not infer state from a prior chat transcript.

Before proposing, editing, trading, sizing, closing, opening, or evaluating anything, load and verify these files in this exact order:

1. `JARVIS V1/FOR_THE_NEXT_LLM.md`
2. `JARVIS V1/STANDING_ORDERS.md`
3. `JARVIS V1/desk_state.md`
4. The newest dated entry in `JARVIS V1/LEARNING_LOG.md`
5. `JARVIS V1/HOW_JARVIS_IS_DOING.md`
6. `doctrine/007_JARVIS_Momentum_Conservation_Trading_Mentor_Baseline.md` (read-only; SHA-256 ae2d9b8e1f32d52c2557b562969678764e7e1f702f523a2f1a97ab4da8a958d0)
7. `mentorship/JARVIS_MENTOR.md` — required. Two-clock test before the spoken act. If this file is missing, new orders stay SAFE_HOLD. It does not override the baseline.
8. `FABLE_5_1_Market_Watch_Logger_Harness_v1.md` — if this file is missing, do not invent it; new orders stay SAFE_HOLD
9. The active demo autonomy configuration and newest account/trade tapes, if execution or open-position discussion is requested. Re-read the terminal. Do not trade from a git snapshot.

Then return this exact startup acknowledgement before doing anything else:

CONTINUITY CHECK
- Project folder: <absolute/repository-relative path>
- Standing-orders file: <found / missing>
- Desk-state file: <found / missing>
- Latest learning-log timestamp: <timestamp / missing>
- Active account mode: <demo / log-only / unknown>
- Active magic number: <value / unknown>
- Client-ticket policy: <value / unknown>
- Score definition: <verbatim one sentence>
- Current score and score-window start: <value / unknown>
- Current target and daily floor: <values / unknown>
- Open-position source and refresh timestamp: <path/timestamp / unknown>
- Maximum permitted lot policy: <value / unknown>
- Active symbol-universe / liquid-name rule: <value / unknown>
- Active research-loop cadence: <value / unknown>
- Execution authority: <enabled / disabled / unknown>
- Baseline version/hash: <value / unknown>
- Mentor file: <found / missing> `mentorship/JARVIS_MENTOR.md`
- Configuration version/hash: <value / unknown>
- Missing/conflicting state: <list or none>

HARD RULES

- If `STANDING_ORDERS.md`, `desk_state.md`, the newest learning entry, or `mentorship/JARVIS_MENTOR.md` is missing, unreadable, contradictory, stale, or does not identify the active account mode, do not trade and do not alter strategy logic.
- Return `SAFE_HOLD` for execution and ask for the missing file/path only after reporting the exact gap.
- Never restore the old “fill symbols up to 50” behavior.
- Never restore the prior 10-lot behavior to chase the dollar target.
- Never use a generic comment as a thesis. Every new order requires a durable pre-trade thesis record before sending.
- Preserve the official KAG/007 doctrine: official sets only; tide → regime → breath/launch → act → finish; HTF force outranks LTF timing; a loaded row is not an entry; a scalp cannot become a hold because it is losing.
- Do not let Daily RSI, Heikin Ashi, fractals, emergence-only rows, or undefined thresholds authorize an order.
- New state must be appended or versioned. Do not overwrite history, locked theses, prior learning logs, or standing orders without a dated change record.

Do not claim continuity is restored until the CONTINUITY CHECK is complete.
```

---

## Durable state requirements

The project should contain these durable artifacts. A new chat should rely on these—not on an earlier conversation:

| File | Purpose | Update method |
|---|---|---|
| `JARVIS V1/STANDING_ORDERS.md` | Highest-priority operating rules for the active desk | Append dated amendments; preserve prior rule history |
| `JARVIS V1/desk_state.md` | Current account mode, score window, current score, target/floor, authority, open-book reference, active configuration | Replace current-state block while appending a state-change ledger |
| `JARVIS V1/LEARNING_LOG.md` | Lessons, experiments, wins/losses, rejected ideas, and next test | Append-only, timestamped |
| `research/pre_trade_thesis.jsonl` | Immutable pre-order thesis for each ticket | Append-only, fsync/reread before order send |
| `research/decision_tape.jsonl` | Signal and outcome tape | Append-only |
| `research/demo_trade_tape.jsonl` | Fill, management, and closure record | Append-only |
| `research/experiment_registry.yaml` | Proposed/approved/rejected shadow experiments | Versioned changes |
| `research/account_snapshots/` | Terminal/account/book snapshots with timestamps | Append-only snapshots |
| `JOURNAL.md` | Human-readable daily desk record and accepted quota changes | Append-only dated entry |

## Required standing-order content

`STANDING_ORDERS.md` should explicitly state, in machine-readable and human-readable form:

```yaml
account_mode: DEMO_ONLY
magic_number: 771249
client_tickets_policy: LEAVE_UNTOUCHED
score_definition: closed net P/L on qualifying tickets opened after 12:36 ET
score_target: 38535
floating_counts_toward_score: false
normal_new_ticket_lots: 1.0
fixed_10_lot_chasing: FORBIDDEN
anonymous_keep10_fallback: FORBIDDEN
pre_trade_thesis_required: true
emergence_execution_authority: false
allowed_execution_sets: [1, 2]
set_3_4_role: context_only
book_quota_liquid_names: 10
book_fill_to_50: FORBIDDEN
```

If terminology uses the word `floor`, distinguish these two meanings clearly:

```text
risk_floor = maximum permitted loss / safety boundary
liquid_name_quota = target maximum or minimum count of liquid names in the monitored/traded universe
```

Do not call both concepts “floor.” That ambiguity can create dangerous risk mistakes.

---

## Final continuity rule

A new chat must begin by reconstructing the desk from files, hashes, account snapshots, and append-only tapes. It must never reconstruct the desk from a vague summary, remembered target, current floating P/L alone, or the desire to beat a prior score.

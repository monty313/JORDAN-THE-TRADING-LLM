# How to use JARVIS

JARVIS is this chat, with eyes on MetaTrader. The expert **JarvisEyes** watches Market Watch and writes a board. It does not place, change, or close trades. A separate five-minute assistant may close a demo magic 771249 ticket when momentum has died or the ticket will not rejoin. That assistant does not open a new ticket. New orders stay SAFE_HOLD.

## Start of day

1. Open MetaTrader and leave it running. This demo book uses unsuffixed names (`EURUSD`, not `EURUSD.sim`) unless you name a live account in that message.
2. In Navigator, press **F5** so `JarvisEyes` shows up under Expert Advisors.
3. Attach **JarvisEyes** to any chart (EURUSD is fine). Leave **RollTide** on USOIL if you still want that panel. Do not attach GradeScreener in its place.
4. Turn on **Algo Trading** so the expert can run. It still will not send orders.
5. Open this Cursor folder (`MT5 to agent`) and ask a market question in this project. A new chat in a different folder will not see the desk.

Phone alerts are optional. In MT5: **Tools → Options → Notifications**, set your MetaQuotes ID, and leave the expert input `InpPush` on. You only get a push when an official call changes to fire, kill, or a direction conflict. The phone app cannot talk back. The conversation stays here.

## What to ask

Plain questions work.

- "What is the board right now?"
- "Is EURUSD a trade or a wait?"
- "Which names have a loaded pullback?"
- "What changed since the last closed bar?"

Jarvis answers in three beats, then one block:

1. Up to three readings of the same rows (fire, loaded wait, or kill), each with what would prove it wrong.
2. The attack: spread, your open trades, the daily RSI warning, the Heikin Ashi door, stale data, pullback versus reversal.
3. One block: market, set, tide, regime, state, roles, topology, act, why, invalidation, risk.

A quiet board stays short. A tide flip or a conflict gets the longer debate.

## What the words mean

Official setups **S1–S4** are the trade call. The act is one of:

- `FIRE_BUY` / `FIRE_SELL` — tide, regime, and the trigger all line up
- `WAIT_LOADED` — the higher-timeframe idea is alive, the release has not happened
- `WAIT_NO_TRADE` — no permission
- `KILL` — a required relation broke, or two official setups fired opposite ways

These are scored so you can see them. They do not override that call:

| ID | Name | On means |
|---|---|---|
| S5 | Regime evidence | Background read only. Chop and expansion stay undefined until you set a number. |
| L1 | Shift SMA door | 5-minute is on the pullback side while 30-minute and 4-hour agree |
| L2 | CCI momentum door | Both CCIs are past ±100 and their averages, with price on the pullback side of its average |
| L3 | Shift SMA tunnel | Higher timeframes hold the rail and price triggers through the other rail |
| L4 | Fractals | Prices are logged. The written rule is too vague to call a fire, so this stays undefined. |
| G1 | Daily RSI tide | Daily RSI versus its shifted average. A warning, not a scalp entry. |
| H1 | Heikin Ashi door | Two trend candles on 5-minute and 15-minute, plus one opposite candle on 1-minute |

`ACTIVE` means that setup's own rule is true on the last **closed** bar. The candle still forming does not flip a call.

## Where things live

| Path | Role |
|---|---|
| `FOR_THE_NEXT_LLM.md` | Boot contract for a new chat, including another computer. |
| `HOW_JARVIS_IS_DOING.md` | Score, why, and the state vector. |
| `STANDING_ORDERS.md` | Operating orders. Read first. |
| `CONTINUITY_BOOTSTRAP.md` | New-chat checklist. |
| `desk_state.md` | Current mode, score window, `risk_floor`, `liquid_name_quota`. |
| `LEARNING_LOG.md` | Lessons. Append only. |
| `JOURNAL.md` | Proposed and accepted playbook changes. |
| `MENTOR_INBOX.md` | Notes the mentor left for the next pass. |
| `SCHEMA.md` | Board columns. |
| `src/` | JarvisEyes. Log only. |
| `assistant/` | Live learning seat. See `assistant/README.md`. Do not stop the five-minute loop to tidy files. |
| `research/` | Thesis, monitor observations, and older studies. See `research/README.md`. |
| `halted/` | Old scripts that must not be run. |

`risk_floor` is the loss boundary. It is unset. `liquid_name_quota` is how many liquid names to monitor. A short count is not an order.

## Files you can edit

Open `JARVIS V1/desk_state.md` and fill **Today target** when you know it. `risk_floor` is the loss boundary. Leave it unset until you name a number. `liquid_name_quota` is a name count, not a loss limit.

`JARVIS V1/JOURNAL.md` is where a proposed change to the playbook goes. The 007 baseline in `Strategies - Copy` stays read-only until you accept a change.

`JARVIS V1/STANDING_ORDERS.md` is the seat memory. A new chat reads it first. `JARVIS V1/LEARNING_LOG.md` is the lesson record. Update those when the operating order changes, or the next session will not know.

You do not need to open the board file. Ask in chat. If you want the raw log, it is in the terminal data folder: `MQL5/Files/jarvis/board.csv`. Older changes are in `MQL5/Files/jarvis/tape/`.

## What Jarvis will not do

- Open a new order while SAFE_HOLD is in force. A close is allowed only for magic 771249 when the last closed bar fails the hold in `STANDING_ORDERS.md` (momentum dying, or the ticket will not rejoin). Client tickets stay untouched.
- Treat a loaded setup as a fire.
- Let a legacy door or the daily RSI override S1–S4.
- Invent a chop or expansion cutoff.
- Rewrite the 007 playbook on its own.

Column-by-column detail is in `JARVIS V1/SCHEMA.md`.

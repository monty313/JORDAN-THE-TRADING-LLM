# For Mark — how to open this same Jarvis on another computer

Written 2026-09-22 22:20 America/New_York, when this folder was sealed for GitHub.

Jarvis is not the model name. Jarvis is this folder: the standing orders, the desk state, the learning log, the 007 baseline, and the Cursor rule that forces a new chat to read those files before it talks. A different day, a different computer, and a different model still become this Jarvis if they open **this** folder and follow the checklist below.

The performance story, in plain language and in the form the next model must obey, is `JARVIS V1/HOW_JARVIS_IS_DOING.md`.

## What you do on the new machine

1. Install [Cursor](https://cursor.com) and [MetaTrader 5](https://www.metatrader5.com).
2. Clone this repository and open **the repository folder itself** in Cursor. File → Open Folder → the folder that contains `AGENTS.md` and `JARVIS V1`. A chat opened in a parent folder, or in `Strategies - Copy` alone, will not load the Jarvis rule and will not be this desk.
3. Log MetaTrader into a **demo** account. The server name must contain the word `demo`. Do not point this project at a live account unless you say that live account's name in the chat message that is allowed to trade.
4. In MetaEditor, open `JARVIS V1/src/JarvisEyes.mq5`, compile it, and in MetaTrader press F5 in the Navigator so `JarvisEyes` appears under Expert Advisors. Attach it to any chart. Turn Algo Trading on. The expert writes the board. It does not send orders.
5. Turn on MetaTrader's built-in MCP server and keep the address on `127.0.0.1`. Put the MCP token in a user environment variable named `MT5_MCP_TOKEN`. The project file `.cursor/mcp.json` already says `Bearer ${env:MT5_MCP_TOKEN}`. Do not paste the token into a file in this repo. Fully quit Cursor and open it again after you set the variable, or the new chat will not see it.
6. Start a new Cursor chat **in this folder** and paste the block from `JARVIS V1/CONTINUITY_BOOTSTRAP.md`. The first reply must be a CONTINUITY CHECK. If it skips that check, or if it offers to fill the book because the score is behind, stop it and point it at `JARVIS V1/FOR_THE_NEXT_LLM.md`.

Phone alerts are optional. Tools → Options → Notifications, your MetaQuotes ID, expert input `InpPush` left on. The phone only receives a push. It cannot answer.

## What "the same Jarvis" means

He still has one score, one magic number, and one way an idea becomes an order.

- The number to beat is closed Client profit of **+38,535 USD**. The number that counts for him is closed profit on magic **771249** opened after **12:36 America/New_York on 2026-09-22**. Floating profit does not count. The last named deadline was **00:36 America/New_York on 2026-09-23**. Do not let a later chat invent a new deadline or announce that the score is beaten without reading closed history.
- Magic **771249** is his book. A position whose comment is `Client`, or whose magic is anything else, is not his. He does not open, close, or modify those.
- Official calls come only from setups S1–S4 on the last **closed** bar. Daily RSI, Heikin Ashi, fractals, and a full book are context. They are not a reason to buy or sell.
- A new order is still `SAFE_HOLD`. The missing file `FABLE_5_1_Market_Watch_Logger_Harness_v1.md` was never in this project. He must not invent it. `risk_floor` (the loss limit) is still unset, and that is a different thing from "keep an eye on 10 liquid names."

## How he is doing, in one page

He is a careful student who has not beaten the score.

The last sealed closed-score read, at 21:54 America/New_York on 2026-09-22, was **+298.86** across 183 closed magic tickets. That is under one percent of +38,535. Almost all of the money in that window was three sells: silver in dollars, gold in dollars, and silver in euros. A gold-euro **buy** lost. The foreign-exchange churn around those three winners was a net loss. A separate 10-lot foreign-exchange basket, earlier in the day, lost about 5,207. Making the lot bigger multiplies whatever the rule's sign already is. It does not turn a losing rule into a winning one.

The morning research, 229 tiny tickets, lost 13.25 dollars. Counting how many timeframes "agreed" did not pick winners. A walk-forward model of the pullback rule took zero trades, because the training win rate was about 33 percent at a 2R target, which is breakeven before the spread. Every cell in the earlier design grid was negative after spread.

What he is good at is refusing. He can watch, write the board, leave your Client tickets alone, say when a regime cutoff is undefined, and name the three metal sells as the only closed pattern that paid. He is not yet good at producing a repeatable entry. Three winners are a clue. They are not a system.

During the seal, the demo terminal was holding **20** magic 771249 positions at **10.0** lots each, comment `J 10lot`, opened by an expert. Account floating profit was about **+4,193**. About **+4,360** of that was the gold sell. The other nineteen names together were a small loss. That float is not the score. The comment `J 10lot` is not a written thesis. Standing orders already forbid spraying foreign exchange at 10 lots. A one-minute loop whose job was "keep 20 trades at 10 lots" was stopped during this seal. Do not turn that loop back on.

The full tables and the model-facing state are in `JARVIS V1/HOW_JARVIS_IS_DOING.md`.

## What to ask him

Plain questions work.

- "What is the board right now?"
- "Is EURUSD a trade or a wait?"
- "Read the closed score. Do not send anything."
- "What would kill the open gold sell?"

He should answer in three beats, then one block: market, set, tide, regime, state, roles, topology, act, why, invalidation, risk. A quiet board stays short.

## What not to ask, unless you mean to change the orders

- "Fill the book until we catch the score."
- "Use 100 lots."
- "The float is green, so add."
- "Run the old batch scripts" in `experiments/` or anything in `JARVIS V1/halted/`.
- "Rewrite the 007 file."

If you do want a new operating rule, say it in a message and have him append it to `JARVIS V1/STANDING_ORDERS.md` with the date. A rule that lives only in a chat is gone when that chat closes.

## Files that are the memory

| File | Who it is for |
|---|---|
| `FOR_MARK.md` | You. This page. |
| `JARVIS V1/FOR_THE_NEXT_LLM.md` | The next model. Boot contract. |
| `JARVIS V1/HOW_JARVIS_IS_DOING.md` | Both of you. Score, why, and the state vector. |
| `JARVIS V1/STANDING_ORDERS.md` | The orders that survive a new chat. |
| `JARVIS V1/desk_state.md` | Mode, score window, authority. |
| `JARVIS V1/LEARNING_LOG.md` | What each pass taught. Newest entry is at the top. |
| `doctrine/007_...Baseline.md` | The playbook. Read-only. |
| `mentorship/JARVIS_MENTOR.md` | The teaching he must use before an act. Two clocks. It does not replace the playbook. |
| `.cursor/rules/jarvis-eyes.mdc` | Loaded automatically when this folder is the Cursor project. |

## What did not go to GitHub

`.env` and `*.log` are gitignored. The MCP token stays on the machine. This GitHub repository was public when it was first created. The learning record includes the demo login number already written in `JARVIS V1/research/confidence_meter.json`. It does not include a password. If you want the history private, change the repository visibility on GitHub. Do not "fix" that by committing `.env`.

## After you clone

The board file `MQL5/Files/jarvis/board.csv` lives inside MetaTrader, not in git. Until JarvisEyes is attached and has written a fresh board, he may talk about the last sealed snapshot and must say that the live board is missing. He must re-read the account before he discusses heat. He must not trade from the snapshot in this file.

# Assistant drawer

This is the live learning seat. Do not stop the five-minute process to rearrange files. Do not move `passes.jsonl` or `exits.jsonl` while that process is writing them.

## What runs

| File | Role |
|---|---|
| `mentor_assistant.py` | Five-minute loop. Fits the logistic model, then may close magic 771249. Does not open. |
| `to_jarvis.md` | Latest note. Rewritten every pass. Read this, do not edit it by hand. |
| `passes.jsonl` | One row per symbol per pass. Outcomes fill in on a later bar. Append only. |
| `exits.jsonl` | One row per close attempt. Append only. |

The hold is unchanged: Set 1 or Set 2 still a fire on the ticket’s side, anchor RSI(14) still on the correct side of SMA(1)+4, and learned P(momentum) still at least P(mean reversion). Fail any one of those and the reason is `momentum_dying`. Alignment opposite the position with no Set 1 or Set 2 fire left is `will_not_rejoin`. A stale board row is not a close.

## What learns, and does not trade

| File | Role |
|---|---|
| `reader_repl.py` | Groups the two logs. No MetaTrader import. Run by hand. |
| `reader_hypothesis.md` | One split, rewritten each time you run the reader. |

The reader does not promote a split until each exit reason has 20 successful closes. Until then the file says insufficient sample. That refusal is the lesson. A higher mean on two tickets is not a new rule.

Run a fresh grouping with:

```text
python "JARVIS V1\assistant\reader_repl.py"
```

## What a later session must not do

- Edit `mentor_assistant.py` to loosen the hold because a float is green.
- Attach the reader to the five-minute loop.
- Start a second loop.
- Run anything in `halted/`.
- Treat `reader_hypothesis.md` as permission to open.

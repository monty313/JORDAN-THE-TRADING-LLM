# Research drawer

A new chat reads the live files below. The score that is still being learned sits in `assistant/`, not in this drawer. The historical files stay here so old lessons keep their paths.

## Live tapes

| File | What it is |
|---|---|
| `pre_trade_thesis.jsonl` | One complete thesis per new order. Append only. |
| `decision_tape.jsonl` | Signal and outcome tape. The five-minute monitor appends `monitor_observation` rows here and does not send. |
| `demo_trade_tape.jsonl` | Fill, change, and close record. Append only. |
| `experiment_registry.yaml` | Proposed, approved, and rejected shadow experiments. |
| `account_snapshots/` | Timestamped desk snapshots. Not a substitute for a live position read. |
| `continuity_check.py` | Checks that a new chat can find the seat. |
| `keep10_open.py` | Refuses an order until a thesis is stored and reread. Live sends stay off. |

## Historical, leave the paths alone

`experiment_registry.md`, `forced_signals.jsonl`, `SCORED_BATCHES.md`, `RETAINED_2026-09-22_What_Worked_And_What_Did_Not.md`, `atlas_reviews.md`, `tide_alignment_tape.jsonl`, the knowledge-harness notes, and `ftmo_forward/`.

The morning batch pile is `experiments/level4_demo_autonomy/2026-09-22_093347/`. Those scripts use absolute paths. Do not move them.

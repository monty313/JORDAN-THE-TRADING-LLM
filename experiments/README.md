# Experiments

Historical demo research. The forced-signal loop is stopped. The stop file is:

`level4_demo_autonomy/2026-09-22_093347/STOP_FORCED_SIGNAL_LOOP`

Each batch in that folder is a set of files with the same number:

- `run_batchN_*.py` opens the batch
- `_picksN.json` is the pick list
- `batchN_signals.json`, `batchN_jobs.json`, `batchN_results.json` are the record
- `_finalize_batchN_mcp.py` writes the close

The scripts point at this folder with absolute paths. Moving a batch file breaks the next run. Leave them here.

The live desk is `JARVIS V1/`.

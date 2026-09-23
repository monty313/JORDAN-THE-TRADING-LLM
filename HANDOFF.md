# Handoff — Cursor ↔ MT5

**This file is historical MCP setup from 2026-09-21.** It is not the seat. The seat is `JARVIS V1/STANDING_ORDERS.md`. Start at `FOR_MARK.md` and `JARVIS V1/FOR_THE_NEXT_LLM.md`. Do not trade from the positions named below.



**Written:** Monday 2026-09-21 20:37 EDT (−04:00)  
**Updated:** Monday 2026-09-21 23:34 EDT — the MCP token in the user environment was accepted (HTTP 200 on initialize). The key is not written here. Cursor must fully restart to inherit `MT5_MCP_TOKEN`. Do not print the key.  
**Who:** Mark + Cursor agent  
**Workspace:** `c:\Users\C2K\Desktop\MT5 to agent`  
**Goal:** Connect this Cursor agent to MetaTrader 5 using only the official free native MCP. Nothing paid. Mentorship, then a read-only tool catalog.

If this is a new chat: read this file first. Do not start from the old Medium/Python-MCP blog path.

---

## Where we left off (23:44 EDT)

Screener check: `rolltide.csv` still ends `2026.09.21 00:16` USOIL SHORT. Last RollTide **Alert** same time. Last journal line `2026.09.21 20:54:08` `ROLLTIDE ready` on USOIL.sim M5 (EA still attached). At 11:31 debug showed `fire:11` but CSV did not grow — dump is not a live board. Positions: NZDJPY.sim sell 0.10 now −$0.06; EURNZD.sim buy stop 0.25 still working.

## Previous (23:37 EDT — CONNECTED)

Cursor `user-mt5-terminal` tools work. Read-only probe succeeded. Account login `600100644`, server `OANDA-Prop Trader`, name `$10k Verification`, MT5 reports `type: real` (FTMO `.sim` symbols). MCP trade flag is **false**. Do not trade unless Mark explicitly asks.

**Next:** keep using native tools. Re-read positions before any mutate.

## Previous (20:51 EDT)

Cursor MCP screen (Mark's screenshot):

- `mt5-terminal` **User** = Error (HTTP 401). User `mcp.json` was deleted to remove this duplicate.
- `mt5-terminal` **MT5 to agent** = Disabled. He must click it to enable.
- Cursor log: `Connection failed: HTTP 401 Unauthorized from MCP server while using configured Authorization header`

Project `mcp.json` and `assistant.ini` MetaTrader endpoint now use `http://127.0.0.1:22344/mcp` (port-change workaround for regenerated-key 401). MT5 will keep serving 22346 until he clicks OK in Options or restarts the terminal.

**Mark:** MT5 → Options → MCP → set Address to `http://127.0.0.1:22344/mcp` → OK. Then in Cursor MCP list, enable the **project** `mt5-terminal` (the one labeled MT5 to agent).

## Previous (20:47 EDT — second Cursor restart)

Token **is** in this Cursor process (`User` + `Process`, length 168, matches `assistant.ini`). MT5 `terminal64` is running. `http://127.0.0.1:22346/mcp` answers.

Two remaining gaps:

1. This chat still has **no `mt5-terminal` tools**. Project + user `mcp.json` exist. Mark must enable the server in **Cursor Settings → MCP** (toggle `mt5-terminal` on). Cursor does not auto-inject project MCP into the agent until that is on.
2. A raw `initialize` with `Authorization: Bearer <ini key>` returned **HTTP 401**. Known MT5 issue after **Regenerate** ([forum](https://www.mql5.com/en/forum/515076)): the Generate button can invalidate the key. Fixes that have worked for others:
   - Change the MCP address port (e.g. `22346` → `22344`), OK, then refresh `MT5_MCP_TOKEN` from `assistant.ini`.
   - Or use MT5’s **Copy** config (default key), not a regenerated one.

Active account: login `600100644`, server `OANDA-Prop Trader`. Confirm demo. Set AI Assistant **Trading = Prohibited** (`PermissionsTrade` was 1).

**Next action:** enable `mt5-terminal` in Cursor MCP settings. If it stays red/401, change the MT5 MCP port as above. Then list tools read-only.

---

## Confirmed on his machine

| Item | Value |
|---|---|
| MT5 build | **6198** (About, 15 Sep 2026) — native MCP is in-box |
| MCP tab | **Enable internal server** checked |
| Address | `http://127.0.0.1:22346/mcp` |
| Token storage | User env var `MT5_MCP_TOKEN` (never in git, never in chat) |
| Paid servers | **None.** No Leo / TheBotPlace / Python MCP unless native fails |

An earlier API key appeared in a screenshot. It is burned. He was told to **Regenerate** in the MCP tab and use only the new key in the env var.

---

## Files already in the repo

| File | Role |
|---|---|
| `.cursor/mcp.json` | `mt5-terminal` → `http://127.0.0.1:22346/mcp` + `Authorization: Bearer ${env:MT5_MCP_TOKEN}` |
| `.cursor/rules/mt5-mcp.mdc` | Demo only, no mutate unless asked, no secrets in source |
| `.gitignore` | `.env`, tokens, logs, `.ex5` |
| `docs/mt5-tool-catalog.md` | Stub — fill after first live tool list |
| `README.md` | Short setup |

MetaEditor MCP (`:22345`) was planned but not added yet. Add it only if 6198 exposes a second address and he wants compile/editor tools.

---

## Safety (do not drop)

- Trading = **Prohibited** in `Tools → Options → AI Assistant`.
- AutoTrading off for the first probe.
- Demo account only.
- Listener stays `127.0.0.1`.
- Re-read positions before any future mutate. No `close_all_*`.
- Never write the token into `mcp.json` as a literal.

---

## What “as much as possible” means without paying

**In scope:** native terminal MCP — account, Market Watch, chart context, positions, history, indicators (list/add on 6090+), MetaEditor later if we add the second URL.

**Out of scope until he asks and pays:** Leo (charts/objects/tester-as-a-tool). Python `mcp-metatrader5-server` only if native MCP will not authenticate.

---

## If MCP is red after reopen

1. User env var `MT5_MCP_TOKEN` must be the real key, not `PASTE_KEY_HERE`. No quotes, no `Bearer `.
2. Cursor must be fully exited and relaunched after the var was saved (Start-menu Cursor only sees user env after a full quit).
3. MT5 must stay open with Enable internal server checked.
4. `${env:MT5_MCP_TOKEN}` interpolation can fail if Cursor was not restarted. Last resort: put the Bearer token only in Cursor **user** MCP settings, never commit it.

---

## First prompts after a good connect

- “List every mt5-terminal tool and say read vs mutate.”
- “Read-only: account type, currency, equity, active symbol specs, bid/ask, server time.”
- “Write the catalog into docs/mt5-tool-catalog.md. Do not trade.”

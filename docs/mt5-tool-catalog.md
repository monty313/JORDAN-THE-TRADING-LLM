# MT5 native MCP tool catalog

Filled 2026-09-21 23:34 EDT after a successful `initialize` + `tools/list` against `http://127.0.0.1:22344/mcp` (build 6198). **66 tools.** Do not call mutate tools unless Mark asks.

Auth note: the working key is the MetaTrader MCP API Key, stored only in gitignored `.env` and the user env var `MT5_MCP_TOKEN`. Do not write the key into this repository. The hex string in `assistant.ini` is rejected (401).

## Read (safe for first probes)

| Tool | Notes |
|---|---|
| `get_workspace_info` | Terminal/workspace context |
| `get_time_information` | Server/local time |
| `get_trading_account_info` | Account type, currency, equity |
| `get_trading_open_positions` | Open positions |
| `get_trading_history_positions` | Closed position history |
| `get_trading_history_orders` | Order history |
| `get_marketwatch_symbols` | Market Watch list |
| `get_chart_history` | OHLCV bars |
| `get_chart_ticks_history` | Ticks |
| `list_open_charts` | Open chart windows |
| `list_available_indicators` | Indicator catalog (6090+) |
| `list_available_mql5_programs` | EAs/scripts/indicators on disk |
| `get_expert_advisor_parameters` | EA inputs |
| `get_script_parameters` | Script inputs |
| `get_indicator_parameters` | Indicator inputs |
| `get_chart_indicator_state` | Indicator on a chart |
| `list_directory` | File listing |
| `find_files_by_glob` | File search |
| `find_files_by_name_keyword` | File search |
| `read_file` | Read text |
| `read_binary_file` | Read binary |
| `read_file_by_lines` | Read slice |
| `search_text` | Search files |
| `search_regex` | Regex search |
| `get_terminal_journal` | Terminal log |
| `get_expert_journal` | Experts log |
| `get_tester_journal` | Tester log |
| `tester_get_status` | Backtest status |
| `tester_get_configuration` | Tester config |
| `tester_get_report` | Last report |
| `economic_calendar_list_countries` | Calendar |
| `economic_calendar_list_events_by_country` | Calendar |
| `economic_calendar_list_events_by_currency` | Calendar |
| `economic_calendar_list_values` | Calendar |
| `economic_calendar_list_values_last` | Calendar |
| `economic_calendar_get_value_by_id` | Calendar |
| `economic_calendar_get_event_by_id` | Calendar |

## Mutate — charts / files / market watch (ask first)

| Tool | Notes |
|---|---|
| `create_new_folder` | Filesystem |
| `create_new_file` | Filesystem |
| `write_file` | Filesystem |
| `write_binary_file` | Filesystem |
| `delete_file` | Filesystem |
| `replace_text_in_file` | Filesystem |
| `send_web_request` | Network |
| `chart_open` | Chart |
| `chart_close` | Chart |
| `chart_apply_template` | Chart |
| `chart_add_indicator` | Chart |
| `chart_add_expert` | Attach EA |
| `chart_add_script` | Run script |
| `chart_remove_expert` | Detach EA |
| `chart_remove_indicator` | Chart |
| `add_marketwatch_symbol` | Market Watch |
| `remove_marketwatch_symbol` | Market Watch |
| `tester_run_backtest` | Strategy Tester |
| `tester_stop` | Tester |
| `tester_wait` | Tester |
| `tester_prepare_config` | Tester |
| `tester_prepare_inputs` | Tester |
| `tester_run_optimization` | Tester |

## Mutate — trading (demo only, only if Mark asks)

| Tool | Notes |
|---|---|
| `trade_send_market_order` | Market order |
| `trade_send_pending_order` | Pending |
| `trade_modify_sl_tp` | Modify |
| `trade_delete_order` | Cancel pending |
| `trade_close_single_position` | Close |
| `trade_close_by_position` | Close-by |

Re-read `get_trading_open_positions` immediately before any trade tool.

//+------------------------------------------------------------------+
//| JarvisEyes.mq5 — log-only Market Watch applicator (no OrderSend)   |
//+------------------------------------------------------------------+
#property copyright "JARVIS Eyes"
#property version   "1.00"
#property description "JARVIS EYES log-only. Board + tape. No trades."
#include "JarvisEyes.mqh"

input group "1. Official sets"
input bool InpSet1 = true;
input bool InpSet2 = true;
input bool InpSet3 = false;
input bool InpSet4 = false;

input group "2. Watch"
input string InpSymbols    = "";
input string InpSuffix     = "";
input int    InpMaxSymbols = 60;
input int    InpRefreshMs  = 1000;
input int    InpQuoteMaxAgeSec = 120;
input bool   InpSkipNoQuote = true;

input group "3. Sensors"
input bool InpScoreLegacy = true;
input bool InpScoreGate   = true;
input bool InpScoreHA     = true;
input bool InpScoreS5     = true;
input bool InpScoreCciHarness = true;

input group "4. Push"
input bool InpPush = true;

input group "5. Files"
input string InpBoardPath = "jarvis\\board.csv";
input string InpTapeDir   = "jarvis\\tape";
input string InpNotifyPath = "jarvis\\notify_state.csv";

void LoadEmergence(void);
void ApplyEmergence(JeRow &r);

JeRow   g_rows[];
int     g_row_n = 0;
string  g_syms[];
int     g_sym_n = 0;
bool    g_use_watch = true;
int     g_watch_n = 0;
datetime g_watch_at = 0;

string g_notify_keys[];
string g_notify_acts[];
int    g_notify_n = 0;

string g_tape_keys[];
string g_tape_acts[];
datetime g_tape_bars[];
int    g_tape_n = 0;

//+------------------------------------------------------------------+
int OnInit()
  {
   Print("JARVIS EYES log-only");
   FolderCreate("jarvis");
   FolderCreate("jarvis\\tape");
   LoadNotifyState();
   LoadEmergence();
   CollectSymbols();
   EventSetMillisecondTimer(MathMax(200, InpRefreshMs));
   ScanPass();
   return INIT_SUCCEEDED;
  }

void OnDeinit(const int reason)
  {
   EventKillTimer();
   SaveNotifyState();
  }

void OnTimer()
  {
   MaybeRefreshWatch();
   ScanPass();
  }

void OnTick() {}

//+------------------------------------------------------------------+
void PushRaw(string &raw[], int &n, const string s)
  {
   if(s == "")
      return;
   for(int i = 0; i < n; i++)
      if(raw[i] == s)
         return;
   ArrayResize(raw, n + 1);
   raw[n++] = s;
  }

bool JeEndsWith(const string s, const string suf)
  {
   if(suf == "")
      return true;
   const int n = StringLen(s);
   const int m = StringLen(suf);
   if(m > n)
      return false;
   return (StringSubstr(s, n - m, m) == suf);
  }

int JeSplitList(const string src, string &out[])
  {
   string parts[];
   const int k = StringSplit(src, ',', parts);
   int n = 0;
   ArrayResize(out, 0);
   for(int i = 0; i < k; i++)
     {
      string t = parts[i];
      StringTrimLeft(t);
      StringTrimRight(t);
      if(t == "")
         continue;
      ArrayResize(out, n + 1);
      out[n++] = t;
     }
   return n;
  }

void CollectWatchNames(string &raw[], int &n)
  {
   n = 0;
   ArrayResize(raw, 0);
   const int selected = SymbolsTotal(true);
   for(int i = 0; i < selected; i++)
      PushRaw(raw, n, SymbolName(i, true));

   if(InpSuffix == "")
      return;

   int tagged = 0;
   for(int i = 0; i < n; i++)
      if(JeEndsWith(raw[i], InpSuffix))
         tagged++;
   if(tagged > 0)
      return;

   const int all = SymbolsTotal(false);
   for(int i = 0; i < all; i++)
     {
      const string s = SymbolName(i, false);
      if(JeEndsWith(s, InpSuffix))
         PushRaw(raw, n, s);
     }
  }

void CollectSymbols(void)
  {
   string raw[];
   int n = JeSplitList(InpSymbols, raw);
   g_use_watch = (n <= 0);
   if(g_use_watch)
      CollectWatchNames(raw, n);
   PushRaw(raw, n, _Symbol);

   const int cap = MathMax(1, MathMin(InpMaxSymbols, JE_MAX_SYMS));
   g_sym_n = 0;
   ArrayResize(g_syms, cap);
   for(int i = 0; i < n && g_sym_n < cap; i++)
     {
      string name = raw[i];
      if(InpSuffix != "" && !JeEndsWith(name, InpSuffix))
        {
         const string try_s = name + InpSuffix;
         if(SymbolInfoInteger(try_s, SYMBOL_EXIST))
            name = try_s;
        }
      if(!SymbolInfoInteger(name, SYMBOL_EXIST))
         continue;
      SymbolSelect(name, true);
      bool dup = false;
      for(int d = 0; d < g_sym_n; d++)
         if(g_syms[d] == name)
           {
            dup = true;
            break;
           }
      if(dup)
         continue;
      g_syms[g_sym_n++] = name;
     }
   g_watch_n = SymbolsTotal(true);
   g_watch_at = TimeCurrent();
  }

void MaybeRefreshWatch(void)
  {
   if(!g_use_watch)
      return;
   if(TimeCurrent() == g_watch_at)
      return;
   const int watch = SymbolsTotal(true);
   if(watch != g_watch_n)
      CollectSymbols();
   else
      g_watch_at = TimeCurrent();
  }

//+------------------------------------------------------------------+
void AddRow(JeRow &r)
  {
   if(g_row_n >= JE_MAX_ROWS)
      return;
   string px = "close";
   if(r.strategy == "S1" || r.strategy == "L2")
      px = "typical";
   else if(r.strategy == "S3" || r.strategy == "L3")
      px = "ohlc";
   if(StringFind(r.cmp, "px=") != 0)
      r.cmp = "px=" + px + ";bar=1;" + r.cmp;
   ApplyEmergence(r);
   ArrayResize(g_rows, g_row_n + 1);
   g_rows[g_row_n++] = r;
  }

// #region agent log
void JeAgentLog(const string hypothesisId, const string message)
  {
   const string line = StringFormat(
      "{\"sessionId\":\"771249\",\"runId\":\"typical-closed\",\"hypothesisId\":\"%s\",\"location\":\"JarvisEyes.mq5:ScanPass\",\"message\":\"%s\",\"data\":{\"bar\":%d,\"prev\":%d,\"price\":\"typical\",\"forming\":\"telemetry\"},\"timestamp\":%d}\n",
      hypothesisId, message, JE_BAR, JE_PREV, (int)TimeCurrent());
   int h = FileOpen("C:\\Users\\C2K\\Desktop\\MT5 to agent\\debug-771249.log",
                    FILE_READ|FILE_WRITE|FILE_TXT|FILE_ANSI|FILE_SHARE_READ|FILE_SHARE_WRITE);
   if(h == INVALID_HANDLE)
      h = FileOpen("jarvis\\debug-771249.log",
                   FILE_READ|FILE_WRITE|FILE_TXT|FILE_ANSI|FILE_SHARE_READ|FILE_SHARE_WRITE);
   if(h == INVALID_HANDLE)
      return;
   FileSeek(h, 0, SEEK_END);
   FileWriteString(h, line);
   FileClose(h);
  }
// #endregion

// #region agent log
void JeAgentLogS2(const string sym, const int setn, const double used, const double cls, const double typ, const double mid10, const double mid100, const double sma50)
  {
   if(StringFind(sym, "EURUSD") != 0 || setn != 1)
      return;
   static datetime s_at = 0;
   if(TimeCurrent() - s_at < 30)
      return;
   s_at = TimeCurrent();
   const string line = StringFormat(
      "{\"sessionId\":\"771249\",\"runId\":\"s2-close\",\"hypothesisId\":\"S2\",\"location\":\"JarvisEyes.mq5:ScoreS2\",\"message\":\"S2 price mode\",\"data\":{\"used\":%.5f,\"close\":%.5f,\"typical\":%.5f,\"mid10\":%.5f,\"mid100\":%.5f,\"sma50\":%.5f,\"applied\":\"PRICE_CLOSE\"},\"timestamp\":%d}\n",
      used, cls, typ, mid10, mid100, sma50, (int)TimeCurrent());
   int h = FileOpen("C:\\Users\\C2K\\Desktop\\MT5 to agent\\debug-771249.log",
                    FILE_READ|FILE_WRITE|FILE_TXT|FILE_ANSI|FILE_SHARE_READ|FILE_SHARE_WRITE);
   if(h == INVALID_HANDLE)
      h = FileOpen("jarvis\\debug-771249.log",
                   FILE_READ|FILE_WRITE|FILE_TXT|FILE_ANSI|FILE_SHARE_READ|FILE_SHARE_WRITE);
   if(h == INVALID_HANDLE)
      return;
   FileSeek(h, 0, SEEK_END);
   FileWriteString(h, line);
   FileClose(h);
  }
// #endregion

struct JeEmerg
  {
   string   key;
   int      pull_n;
   int      cont_n;
   int      mom_n;
   double   pull_sum;
   double   cont_sum;
   double   mom_sum;
   datetime prev_bar;
   double   prev_close;
   string   prev_phase;
   int      prev_side;
  };

JeEmerg g_em[];
int     g_em_n = 0;
int     g_em_changed = 0;
int     g_em_seen = 0;
string  g_em_sample = "";

int FindEm(const string key)
  {
   for(int i = 0; i < g_em_n; i++)
      if(g_em[i].key == key)
         return i;
   return -1;
  }

void EmAdd(JeEmerg &e, const string phase, const double fwd)
  {
   if(phase == "pullback")
     { e.pull_n++; e.pull_sum += fwd; }
   else if(phase == "continuation")
     { e.cont_n++; e.cont_sum += fwd; }
   else if(phase == "momentum")
     { e.mom_n++; e.mom_sum += fwd; }
  }

void EmConsider(const string name, const int n, const double sum, string &best, double &best_mean, int &best_n)
  {
   if(n < 3)
      return;
   const double m = sum / n;
   if(best == "" || m > best_mean)
     {
      best = name;
      best_mean = m;
      best_n = n;
     }
  }

string JePhase(const JeRow &r)
  {
   if(StringFind(r.state, "launch") >= 0)
      return "momentum";
   if(StringFind(r.state, "pullback") >= 0)
      return "pullback";
   if(StringFind(r.state, "continuation") >= 0)
      return "continuation";
   if(r.act == "WAIT_LOADED")
      return "pullback";
   if(StringFind(r.act, "FIRE_") == 0)
      return "continuation";
   return "";
  }

void LoadEmergence(void)
  {
   int h = FileOpen("jarvis\\emergence.csv", FILE_READ|FILE_CSV|FILE_ANSI|FILE_SHARE_READ|FILE_SHARE_WRITE, ',');
   if(h == INVALID_HANDLE)
      return;
   while(!FileIsEnding(h))
     {
      string key = FileReadString(h);
      if(key == "" || key == "key")
        {
         if(key == "key")
           {
            FileReadString(h); FileReadString(h); FileReadString(h); FileReadString(h);
            FileReadString(h); FileReadString(h); FileReadString(h); FileReadString(h);
            FileReadString(h); FileReadString(h);
           }
         continue;
        }
      JeEmerg e;
      e.key = key;
      e.pull_n = (int)StringToInteger(FileReadString(h));
      e.pull_sum = StringToDouble(FileReadString(h));
      e.cont_n = (int)StringToInteger(FileReadString(h));
      e.cont_sum = StringToDouble(FileReadString(h));
      e.mom_n = (int)StringToInteger(FileReadString(h));
      e.mom_sum = StringToDouble(FileReadString(h));
      e.prev_bar = StringToTime(FileReadString(h));
      e.prev_close = StringToDouble(FileReadString(h));
      e.prev_phase = FileReadString(h);
      e.prev_side = (int)StringToInteger(FileReadString(h));
      ArrayResize(g_em, g_em_n + 1);
      g_em[g_em_n++] = e;
     }
   FileClose(h);
  }

void SaveEmergence(void)
  {
   int h = FileOpen("jarvis\\emergence.csv", FILE_WRITE|FILE_CSV|FILE_ANSI|FILE_SHARE_READ|FILE_SHARE_WRITE, ',');
   if(h == INVALID_HANDLE)
      return;
   FileWrite(h, "key", "pull_n", "pull_sum", "cont_n", "cont_sum", "mom_n", "mom_sum", "prev_bar", "prev_close", "prev_phase", "prev_side");
   for(int i = 0; i < g_em_n; i++)
      FileWrite(h, g_em[i].key, g_em[i].pull_n, DoubleToString(g_em[i].pull_sum, 8),
                g_em[i].cont_n, DoubleToString(g_em[i].cont_sum, 8),
                g_em[i].mom_n, DoubleToString(g_em[i].mom_sum, 8),
                TimeToString(g_em[i].prev_bar, TIME_DATE|TIME_SECONDS),
                DoubleToString(g_em[i].prev_close, 8),
                g_em[i].prev_phase, g_em[i].prev_side);
   FileClose(h);
  }

void ApplyEmergence(JeRow &r)
  {
   if(r.family != "OFFICIAL")
      return;
   if(r.strategy != "S1" && r.strategy != "S2" && r.strategy != "S3" && r.strategy != "S4")
      return;
   if(r.tide != "long_only" && r.tide != "short_only")
      return;
   if(r.act != "FIRE_BUY" && r.act != "FIRE_SELL" && r.act != "WAIT_LOADED")
      return;
   const string phase = JePhase(r);
   if(phase == "")
      return;
   const string official = r.act;
   const int side = (r.tide == "long_only" ? 1 : -1);
   const string key = r.symbol + "|" + r.set_id + "|" + r.strategy;
   int ix = FindEm(key);
   if(ix < 0)
     {
      JeEmerg e;
      e.key = key;
      e.pull_n = e.cont_n = e.mom_n = 0;
      e.pull_sum = e.cont_sum = e.mom_sum = 0;
      e.prev_bar = 0;
      e.prev_close = 0;
      e.prev_phase = "";
      e.prev_side = 0;
      ArrayResize(g_em, g_em_n + 1);
      g_em[g_em_n++] = e;
      ix = g_em_n - 1;
     }
   if(g_em[ix].prev_bar != 0 && g_em[ix].prev_bar != r.closed_bar_time && g_em[ix].prev_phase != "" && g_em[ix].prev_close != 0)
      EmAdd(g_em[ix], g_em[ix].prev_phase, (r.close1 - g_em[ix].prev_close) * g_em[ix].prev_side);

   string best = "";
   double best_mean = 0;
   int best_n = 0;
   EmConsider("pullback", g_em[ix].pull_n, g_em[ix].pull_sum, best, best_mean, best_n);
   EmConsider("continuation", g_em[ix].cont_n, g_em[ix].cont_sum, best, best_mean, best_n);
   EmConsider("momentum", g_em[ix].mom_n, g_em[ix].mom_sum, best, best_mean, best_n);
   g_em_seen++;
   if(best == "")
      r.cmp += ";emerged=0;need_samples=1;phase=" + phase;
   else if(best_mean <= 0.0)
     {
      r.act = "WAIT_NO_TRADE";
      r.reason = "emerged_no_edge";
     }
   else if(phase == best)
     {
      if(r.act == "WAIT_LOADED")
        {
         r.act = (side > 0 ? "FIRE_BUY" : "FIRE_SELL");
         r.reason = "emerged_enter_" + phase;
        }
     }
   else if(StringFind(official, "FIRE_") == 0 || official == "WAIT_LOADED")
     {
      r.act = "WAIT_LOADED";
      r.reason = "emerged_wait_" + best;
     }
   if(r.act != official)
      g_em_changed++;
   if(best != "")
      r.cmp += StringFormat(";official_act=%s;phase=%s;best=%s;best_n=%d;best_mean=%.8f;emerged=%d",
                            official, phase, best, best_n, best_mean, (r.act != official ? 1 : 0));
   if(g_em_sample == "" && r.act != official)
      g_em_sample = key + "|" + official + ">" + r.act + "|" + best;
   g_em[ix].prev_bar = r.closed_bar_time;
   g_em[ix].prev_close = r.close1;
   g_em[ix].prev_phase = phase;
   g_em[ix].prev_side = side;
  }

// #region agent log
void JeAgentLogEm(const int changed, const int seen, const string sample)
  {
   const string line = StringFormat(
      "{\"sessionId\":\"771249\",\"runId\":\"emergence\",\"hypothesisId\":\"A\",\"location\":\"JarvisEyes.mq5:WriteBoard\",\"message\":\"timing can change the act\",\"data\":{\"changed\":%d,\"seen\":%d,\"sample\":\"%s\"},\"timestamp\":%d}\n",
      changed, seen, sample, (int)TimeCurrent());
   int h = FileOpen("C:\\Users\\C2K\\Desktop\\MT5 to agent\\debug-771249.log",
                    FILE_READ|FILE_WRITE|FILE_TXT|FILE_ANSI|FILE_SHARE_READ|FILE_SHARE_WRITE);
   if(h == INVALID_HANDLE)
      h = FileOpen("jarvis\\debug-771249.log",
                   FILE_READ|FILE_WRITE|FILE_TXT|FILE_ANSI|FILE_SHARE_READ|FILE_SHARE_WRITE);
   if(h == INVALID_HANDLE)
      return;
   FileSeek(h, 0, SEEK_END);
   FileWriteString(h, line);
   FileClose(h);
  }
// #endregion

void FillCommon(JeRow &r, const string sym, const ENUM_TIMEFRAMES anchor)
  {
   r.symbol = sym;
   r.spread_points = JeSpread(sym);
   r.forming_close0 = iClose(sym, anchor, 0);
   MqlRates rates[];
   if(JeRates(sym, anchor, 3, rates))
     {
      r.closed_bar_time = rates[JE_BAR].time;
      r.open1  = rates[JE_BAR].open;
      r.high1  = rates[JE_BAR].high;
      r.low1   = rates[JE_BAR].low;
      r.close1 = rates[JE_BAR].close;
     }
   if(!JeQuoteFresh(sym, InpQuoteMaxAgeSec))
     {
      if(InpSkipNoQuote)
         r.data = "stale";
     }
  }

string DailyRsiWarn(const string sym)
  {
   int h_rsi = iRSI(sym, PERIOD_D1, 14, PRICE_CLOSE);
   if(h_rsi == INVALID_HANDLE)
      return "thin";
   double rsi[], rail[];
   const bool ok = JeCopyBuf(h_rsi, 0, 12, rsi) && JeSmaShifted(rsi, 1, 4, 4, rail);
   JeRelease(h_rsi);
   if(!ok)
      return "thin";
   if(rsi[JE_BAR] > rail[JE_BAR])
      return "bull";
   if(rsi[JE_BAR] < rail[JE_BAR])
      return "bear";
   return "flat";
  }

//+------------------------------------------------------------------+
// Official S1 Dual CCI
//+------------------------------------------------------------------+
void ScoreS1(const string sym, const JeSetDef &setd, const string warn)
  {
   JeRow r;
   JeClearRow(r);
   r.family = "OFFICIAL";
   r.strategy = "S1";
   r.plain_name = "Dual CCI slingshot";
   r.set_id = IntegerToString(setd.set_num);
   r.anchor_tf = JeTfName(setd.anchor);
   r.htf1_tf = JeTfName(setd.htf1);
   r.htf2_tf = JeTfName(setd.htf2);
   r.daily_rsi_warn = warn;
   r.act = "WAIT_NO_TRADE";
   FillCommon(r, sym, setd.anchor);

   if(r.data == "stale")
     {
      r.reason = "data_stale";
      AddRow(r);
      return;
     }

   ENUM_TIMEFRAMES tfs[3];
   tfs[0] = setd.htf1;
   tfs[1] = setd.htf2;
   tfs[2] = setd.anchor;

   double c30[3], c100[3], s30[3], s100[3], c30p[3], s30p[3];
   bool ok_all = true;
   for(int t = 0; t < 3; t++)
     {
      MqlRates warm[];
      CopyRates(sym, tfs[t], 0, 200, warm);
      int h30 = iCCI(sym, tfs[t], 30, PRICE_TYPICAL);
      int h100 = iCCI(sym, tfs[t], 100, PRICE_TYPICAL);
      double a[], b[], c[], d[];
      if(h30 == INVALID_HANDLE || h100 == INVALID_HANDLE ||
         !JeCopyBuf(h30, 0, 16, a) || !JeCopyBuf(h100, 0, 16, b) ||
         !JeSmaShifted(a, 2, 2, 4, c) || !JeSmaShifted(b, 2, 2, 4, d))
        {
         ok_all = false;
         JeRelease(h30); JeRelease(h100);
         break;
        }
      c30[t] = a[JE_BAR]; c100[t] = b[JE_BAR];
      s30[t] = c[JE_BAR]; s100[t] = d[JE_BAR];
      c30p[t] = a[JE_PREV]; s30p[t] = c[JE_PREV];
      JeRelease(h30); JeRelease(h100);
     }

   if(!ok_all)
     {
      r.data = "thin";
      r.reason = "data_thin";
      r.active = "INACTIVE";
      AddRow(r);
      return;
     }

   r.has_raw_a = r.has_raw_b = r.has_raw_c = r.has_raw_d = r.has_raw_e = r.has_raw_f = true;
   r.raw_a = c30[2]; r.raw_b = c100[2]; r.raw_c = s30[2]; r.raw_d = s100[2];
   r.raw_e = c30p[2]; r.raw_f = MathAbs(c30[2] - s30[2]);

   const bool htf1_long = (c30[0] > s30[0] && c100[0] > s100[0]);
   const bool htf1_short = (c30[0] < s30[0] && c100[0] < s100[0]);
   const bool htf2_long = (c30[1] > s30[1] && c100[1] > s100[1]);
   const bool htf2_short = (c30[1] < s30[1] && c100[1] < s100[1]);

   if(htf1_long && htf2_long)
      r.tide = "long_only";
   else if(htf1_short && htf2_short)
      r.tide = "short_only";
   else
     {
      r.tide = "flat";
      r.reason = "htf_force_conflict";
      r.act = "WAIT_NO_TRADE";
      r.active = "INACTIVE";
      r.cmp = StringFormat("htf1_long=%d;htf2_long=%d;htf1_short=%d;htf2_short=%d;cci30=%g;cci100=%g",
                          htf1_long, htf2_long, htf1_short, htf2_short, c30[2], c100[2]);
      AddRow(r);
      return;
     }

   r.regime = (r.tide == "long_only" ? "bull_trend" : "bear_trend");
   const bool slow_ok_long = (c100[2] > s100[2]);
   const bool slow_ok_short = (c100[2] < s100[2]);
   const bool load_long = slow_ok_long && (c30[2] < s30[2]);
   const bool load_short = slow_ok_short && (c30[2] > s30[2]);
   const bool fire_long = slow_ok_long && JeReclaimUp(c30[2], s30[2], c30p[2], s30p[2]);
   const bool fire_short = slow_ok_short && JeReclaimDn(c30[2], s30[2], c30p[2], s30p[2]);

   r.cmp = StringFormat("tide=%s;slow_ok_long=%d;load_long=%d;fire_long=%d;load_short=%d;fire_short=%d;cci30=%g;sma=%g;cci30_prev=%g",
                        r.tide, slow_ok_long, load_long, fire_long, load_short, fire_short, c30[2], s30[2], c30p[2]);

   if(r.tide == "long_only")
     {
      if(!slow_ok_long)
        {
         r.act = "KILL";
         r.reason = "slow_inertia_failed";
         r.topology = "none";
         r.active = "INACTIVE";
        }
      else if(fire_long)
        {
         r.act = "FIRE_BUY";
         r.topology = "slingshot_release";
         r.state = "continuation";
         r.active = "ACTIVE";
         r.official_fire_buy = true;
         r.reason = "cci30_reclaim_sma";
        }
      else if(load_long)
        {
         r.act = "WAIT_LOADED";
         r.topology = "slingshot_load";
         r.state = "big_pullback-loaded";
         r.active = "ACTIVE";
         r.reason = "waiting_cci30_reclaim";
        }
      else
        {
         r.act = "WAIT_NO_TRADE";
         r.topology = "none";
         r.active = "INACTIVE";
         r.reason = "no_load";
        }
     }
   else
     {
      if(!slow_ok_short)
        {
         r.act = "KILL";
         r.reason = "slow_inertia_failed";
         r.active = "INACTIVE";
        }
      else if(fire_short)
        {
         r.act = "FIRE_SELL";
         r.topology = "slingshot_release";
         r.state = "continuation";
         r.active = "ACTIVE";
         r.official_fire_sell = true;
         r.reason = "cci30_reclaim_sma";
        }
      else if(load_short)
        {
         r.act = "WAIT_LOADED";
         r.topology = "slingshot_load";
         r.state = "big_pullback-loaded";
         r.active = "ACTIVE";
         r.reason = "waiting_cci30_reclaim";
        }
      else
        {
         r.act = "WAIT_NO_TRADE";
         r.active = "INACTIVE";
         r.reason = "no_load";
        }
     }
   AddRow(r);
  }

//+------------------------------------------------------------------+
void ScoreS2(const string sym, const JeSetDef &setd, const string warn)
  {
   JeRow r;
   JeClearRow(r);
   r.family = "OFFICIAL";
   r.strategy = "S2";
   r.plain_name = "Dual BB pullback";
   r.set_id = IntegerToString(setd.set_num);
   r.anchor_tf = JeTfName(setd.anchor);
   r.htf1_tf = JeTfName(setd.htf1);
   r.htf2_tf = JeTfName(setd.htf2);
   r.daily_rsi_warn = warn;
   r.act = "WAIT_NO_TRADE";
   FillCommon(r, sym, setd.anchor);
   if(r.data == "stale")
     {
      r.reason = "data_stale";
      AddRow(r);
      return;
     }

   ENUM_TIMEFRAMES tfs[3];
   tfs[0] = setd.htf1; tfs[1] = setd.htf2; tfs[2] = setd.anchor;
   double mid100[3], mid10[3], sma50[3], closev[3], mid10p[3], upper100[3], lower100[3];
   bool ok = true;
   for(int t = 0; t < 3; t++)
     {
      MqlRates warm[];
      CopyRates(sym, tfs[t], 0, 220, warm);
      int b100 = iBands(sym, tfs[t], 100, 2, 0.5, PRICE_CLOSE);
      int b10  = iBands(sym, tfs[t], 10, 2, 0.5, PRICE_CLOSE);
      int h50  = iMA(sym, tfs[t], 50, 0, MODE_SMA, PRICE_CLOSE);
      double m100[], m10[], s50[], u100[], l100[];
      if(b100 == INVALID_HANDLE || b10 == INVALID_HANDLE || h50 == INVALID_HANDLE ||
         !JeCopyBuf(b100, 0, 4, m100) || !JeCopyBuf(b10, 0, 4, m10) ||
         !JeCopyBuf(h50, 0, 4, s50) || !JeCopyBuf(b100, 1, 4, u100) || !JeCopyBuf(b100, 2, 4, l100))
        {
         ok = false;
         JeRelease(b100); JeRelease(b10); JeRelease(h50);
         break;
        }
      mid100[t] = m100[JE_BAR]; mid10[t] = m10[JE_BAR]; sma50[t] = s50[JE_BAR];
      mid10p[t] = m10[JE_PREV];
      upper100[t] = u100[JE_BAR]; lower100[t] = l100[JE_BAR];
      closev[t] = iClose(sym, tfs[t], JE_BAR);
      JeRelease(b100); JeRelease(b10); JeRelease(h50);
     }
   if(!ok)
     {
      r.data = "thin";
      r.reason = "data_thin";
      AddRow(r);
      return;
     }

   r.has_raw_a = r.has_raw_b = r.has_raw_c = r.has_raw_d = r.has_raw_e = true;
   r.raw_a = mid100[2]; r.raw_b = mid10[2]; r.raw_c = sma50[2];
   r.raw_d = upper100[2] - lower100[2];
   r.raw_e = mid10p[2];

   const bool h1l = (closev[0] > mid100[0] && closev[0] > mid10[0]);
   const bool h1s = (closev[0] < mid100[0] && closev[0] < mid10[0]);
   const bool h2l = (closev[1] > mid100[1] && closev[1] > mid10[1]);
   const bool h2s = (closev[1] < mid100[1] && closev[1] < mid10[1]);
   if(h1l && h2l)
      r.tide = "long_only";
   else if(h1s && h2s)
      r.tide = "short_only";
   else
     {
      r.tide = "flat";
      r.reason = "htf_force_conflict";
      r.act = "WAIT_NO_TRADE";
      r.active = "INACTIVE";
      r.cmp = StringFormat("htf_conflict;c=%g;m100=%g;m10=%g", closev[2], mid100[2], mid10[2]);
      AddRow(r);
      return;
     }
   r.regime = (r.tide == "long_only" ? "bull_trend" : "bear_trend");

   const double c1 = closev[2];
   const double c2 = iClose(sym, setd.anchor, JE_PREV);
   JeAgentLogS2(sym, setd.set_num, c1, iClose(sym, setd.anchor, JE_BAR), JeTypical(sym, setd.anchor, JE_BAR), mid10[2], mid100[2], sma50[2]);
   const bool struct_long = (sma50[2] > mid100[2]);
   const bool struct_short = (sma50[2] < mid100[2]);
   const bool load_long = (c1 > mid100[2] && c1 < mid10[2] && struct_long);
   const bool load_short = (c1 < mid100[2] && c1 > mid10[2] && struct_short);
   const bool fire_long = struct_long && (c1 > mid100[2]) && JeReclaimUp(c1, mid10[2], c2, mid10p[2]);
   const bool fire_short = struct_short && (c1 < mid100[2]) && JeReclaimDn(c1, mid10[2], c2, mid10p[2]);

   r.cmp = StringFormat("tide=%s;struct_long=%d;struct_short=%d;load_long=%d;load_short=%d;fire_long=%d;fire_short=%d;close=%g;mid10=%g;mid100=%g;sma50=%g",
                        r.tide, struct_long, struct_short, load_long, load_short, fire_long, fire_short, c1, mid10[2], mid100[2], sma50[2]);

   if(r.tide == "long_only")
     {
      if(!struct_long || c1 < mid100[2])
        {
         r.act = "KILL";
         r.reason = (c1 < mid100[2] ? "wide_containment_failed" : "sma50_structure_failed");
         r.active = "INACTIVE";
        }
      else if(fire_long)
        {
         r.act = "FIRE_BUY";
         r.topology = "bb_pullback_release";
         r.state = "continuation";
         r.active = "ACTIVE";
         r.official_fire_buy = true;
         r.reason = "reclaim_tight_middle";
        }
      else if(load_long)
        {
         r.act = "WAIT_LOADED";
         r.topology = "bb_pullback_load";
         r.state = "big_pullback-loaded";
         r.active = "ACTIVE";
         r.reason = "waiting_tight_reclaim";
        }
      else
        {
         r.act = "WAIT_NO_TRADE";
         r.active = "INACTIVE";
         r.reason = "no_load";
        }
     }
   else
     {
      if(!struct_short || c1 > mid100[2])
        {
         r.act = "KILL";
         r.reason = (c1 > mid100[2] ? "wide_containment_failed" : "sma50_structure_failed");
         r.active = "INACTIVE";
        }
      else if(fire_short)
        {
         r.act = "FIRE_SELL";
         r.topology = "bb_pullback_release";
         r.state = "continuation";
         r.active = "ACTIVE";
         r.official_fire_sell = true;
         r.reason = "reclaim_tight_middle";
        }
      else if(load_short)
        {
         r.act = "WAIT_LOADED";
         r.topology = "bb_pullback_load";
         r.state = "big_pullback-loaded";
         r.active = "ACTIVE";
         r.reason = "waiting_tight_reclaim";
        }
      else
        {
         r.act = "WAIT_NO_TRADE";
         r.active = "INACTIVE";
         r.reason = "no_load";
        }
     }
   AddRow(r);
  }

//+------------------------------------------------------------------+
void ScoreS3(const string sym, const JeSetDef &setd, const string warn)
  {
   JeRow r;
   JeClearRow(r);
   r.family = "OFFICIAL";
   r.strategy = "S3";
   r.plain_name = "Shifted envelope";
   r.set_id = IntegerToString(setd.set_num);
   r.anchor_tf = JeTfName(setd.anchor);
   r.htf1_tf = JeTfName(setd.htf1);
   r.htf2_tf = JeTfName(setd.htf2);
   r.daily_rsi_warn = warn;
   r.act = "WAIT_NO_TRADE";
   FillCommon(r, sym, setd.anchor);
   if(r.data == "stale")
     {
      r.reason = "data_stale";
      AddRow(r);
      return;
     }

   ENUM_TIMEFRAMES tfs[3];
   tfs[0] = setd.htf1; tfs[1] = setd.htf2; tfs[2] = setd.anchor;
   int shifts[3] = {4, 4, 2};
   double hi[3], lo[3], o1[3], c1[3];
   bool ok = true;
   for(int t = 0; t < 3; t++)
     {
      MqlRates warm[];
      CopyRates(sym, tfs[t], 0, 40, warm);
      int hh = iMA(sym, tfs[t], 4, shifts[t], MODE_SMA, PRICE_HIGH);
      int ll = iMA(sym, tfs[t], 4, shifts[t], MODE_SMA, PRICE_LOW);
      double hb[], lb[];
      if(hh == INVALID_HANDLE || ll == INVALID_HANDLE ||
         !JeCopyBuf(hh, 0, 3, hb) || !JeCopyBuf(ll, 0, 3, lb))
        {
         ok = false;
         JeRelease(hh); JeRelease(ll);
         break;
        }
      hi[t] = hb[JE_BAR]; lo[t] = lb[JE_BAR];
      o1[t] = iOpen(sym, tfs[t], JE_BAR);
      c1[t] = iClose(sym, tfs[t], JE_BAR);
      JeRelease(hh); JeRelease(ll);
     }
   if(!ok)
     {
      r.data = "thin";
      r.reason = "data_thin";
      AddRow(r);
      return;
     }

   r.has_raw_a = r.has_raw_b = true;
   r.raw_a = hi[2]; r.raw_b = lo[2];

   // HTF force: close beyond both rails; stronger = full body
   const bool h1l = (c1[0] > hi[0] && c1[0] > lo[0]);
   const bool h1s = (c1[0] < hi[0] && c1[0] < lo[0]);
   const bool h2l = (c1[1] > hi[1] && c1[1] > lo[1]);
   const bool h2s = (c1[1] < hi[1] && c1[1] < lo[1]);
   if(h1l && h2l)
      r.tide = "long_only";
   else if(h1s && h2s)
      r.tide = "short_only";
   else
     {
      r.tide = "flat";
      r.reason = "htf_force_conflict";
      r.active = "INACTIVE";
      r.cmp = "htf_rails_disagree";
      AddRow(r);
      return;
     }
   r.regime = (r.tide == "long_only" ? "bull_trend" : "bear_trend");

   const bool body_long = (o1[2] > hi[2] && o1[2] > lo[2] && c1[2] > hi[2] && c1[2] > lo[2]);
   const bool body_short = (o1[2] < hi[2] && o1[2] < lo[2] && c1[2] < hi[2] && c1[2] < lo[2]);
   const bool close_long = (c1[2] > hi[2] && c1[2] > lo[2]);
   const bool close_short = (c1[2] < hi[2] && c1[2] < lo[2]);

   r.cmp = StringFormat("tide=%s;body_long=%d;body_short=%d;close_long=%d;rail_hi=%g;rail_lo=%g;o=%g;c=%g",
                        r.tide, body_long, body_short, close_long, hi[2], lo[2], o1[2], c1[2]);

   if(r.tide == "long_only")
     {
      if(body_long)
        {
         r.act = "FIRE_BUY";
         r.topology = "tunnel_clear";
         r.state = "launch";
         r.active = "ACTIVE";
         r.official_fire_buy = true;
         r.reason = "full_body_above_tunnel";
        }
      else if(close_long)
        {
         r.act = "WAIT_LOADED";
         r.topology = "tunnel_partial";
         r.state = "continuation";
         r.active = "ACTIVE";
         r.reason = "waiting_full_body_clear";
        }
      else
        {
         r.act = "KILL";
         r.reason = "shifted_tunnel_failed";
         r.active = "INACTIVE";
        }
     }
   else
     {
      if(body_short)
        {
         r.act = "FIRE_SELL";
         r.topology = "tunnel_clear";
         r.state = "launch";
         r.active = "ACTIVE";
         r.official_fire_sell = true;
         r.reason = "full_body_below_tunnel";
        }
      else if(close_short)
        {
         r.act = "WAIT_LOADED";
         r.topology = "tunnel_partial";
         r.active = "ACTIVE";
         r.reason = "waiting_full_body_clear";
        }
      else
        {
         r.act = "KILL";
         r.reason = "shifted_tunnel_failed";
         r.active = "INACTIVE";
        }
     }
   AddRow(r);
  }

//+------------------------------------------------------------------+
void ScoreS4(const string sym, const JeSetDef &setd, const string warn)
  {
   JeRow r;
   JeClearRow(r);
   r.family = "OFFICIAL";
   r.strategy = "S4";
   r.plain_name = "RSI-BB tension snap";
   r.set_id = IntegerToString(setd.set_num);
   r.anchor_tf = JeTfName(setd.anchor);
   r.htf1_tf = JeTfName(setd.htf1);
   r.htf2_tf = JeTfName(setd.htf2);
   r.daily_rsi_warn = warn;
   r.act = "WAIT_NO_TRADE";
   FillCommon(r, sym, setd.anchor);
   if(r.data == "stale")
     {
      r.reason = "data_stale";
      AddRow(r);
      return;
     }

   ENUM_TIMEFRAMES tfs[3];
   tfs[0] = setd.htf1; tfs[1] = setd.htf2; tfs[2] = setd.anchor;
   double r2[3], r20[3], m2[3], lo2[3], m20[3], r2p[3], lo2p[3], hi2v[3], hi2p[3];
   bool ok = true;
   for(int t = 0; t < 3; t++)
     {
      MqlRates warm[];
      CopyRates(sym, tfs[t], 0, 200, warm);
      int h2 = iRSI(sym, tfs[t], 2, PRICE_CLOSE);
      int h20 = iRSI(sym, tfs[t], 20, PRICE_CLOSE);
      double a[], b[], mid2b[], up2b[], low2b[], mid20b[], up20b[], low20b[];
      if(h2 == INVALID_HANDLE || h20 == INVALID_HANDLE ||
         !JeCopyBuf(h2, 0, 40, a) || !JeCopyBuf(h20, 0, 40, b) ||
         !JeBandsOnSeries(a, 20, 2, 0.5, 4, mid2b, up2b, low2b) ||
         !JeBandsOnSeries(b, 20, 2, 0.5, 4, mid20b, up20b, low20b))
        {
         ok = false;
         JeRelease(h2); JeRelease(h20);
         break;
        }
      r2[t] = a[JE_BAR]; r20[t] = b[JE_BAR];
      m2[t] = mid2b[JE_BAR]; lo2[t] = low2b[JE_BAR]; m20[t] = mid20b[JE_BAR];
      r2p[t] = a[JE_PREV]; lo2p[t] = low2b[JE_PREV];
      hi2v[t] = up2b[JE_BAR]; hi2p[t] = up2b[JE_PREV];
      JeRelease(h2); JeRelease(h20);
     }
   if(!ok)
     {
      r.data = "thin";
      r.reason = "data_thin";
      AddRow(r);
      return;
     }

   r.has_raw_a = r.has_raw_b = r.has_raw_c = r.has_raw_d = r.has_raw_e = r.has_raw_f = true;
   r.raw_a = r2[2]; r.raw_b = r20[2]; r.raw_c = m2[2]; r.raw_d = lo2[2]; r.raw_e = m20[2]; r.raw_f = r2p[2];

   // HTF: both RSIs above their BB middles for long
   const bool h1l = (r2[0] > m2[0] && r20[0] > m20[0]);
   const bool h1s = (r2[0] < m2[0] && r20[0] < m20[0]);
   const bool h2l = (r2[1] > m2[1] && r20[1] > m20[1]);
   const bool h2s = (r2[1] < m2[1] && r20[1] < m20[1]);
   if(h1l && h2l)
      r.tide = "long_only";
   else if(h1s && h2s)
      r.tide = "short_only";
   else
     {
      r.tide = "flat";
      r.reason = "htf_force_conflict";
      r.active = "INACTIVE";
      r.cmp = "htf_rsi_bb_disagree";
      AddRow(r);
      return;
     }
   r.regime = (r.tide == "long_only" ? "bull_trend" : "bear_trend");

   const double hi2 = hi2v[2];
   const bool slow_long = (r20[2] > m20[2]);
   const bool slow_short = (r20[2] < m20[2]);
   const bool load_long = slow_long && (r2[2] < lo2[2]);
   const bool load_short = slow_short && (r2[2] > hi2);
   const bool fire_long = slow_long && JeReclaimUp(r2[2], lo2[2], r2p[2], lo2p[2]);
   const bool fire_short = slow_short && JeReclaimDn(r2[2], hi2v[2], r2p[2], hi2p[2]);

   r.cmp = StringFormat("tide=%s;slow_long=%d;slow_short=%d;load_long=%d;load_short=%d;fire_long=%d;fire_short=%d;rsi2=%g;lo=%g;rsi20=%g;mid20=%g",
                        r.tide, slow_long, slow_short, load_long, load_short, fire_long, fire_short, r2[2], lo2[2], r20[2], m20[2]);

   if(r.tide == "long_only")
     {
      if(!slow_long)
        {
         r.act = "KILL";
         r.reason = "slow_inertia_failed";
         r.active = "INACTIVE";
        }
      else if(fire_long)
        {
         r.act = "FIRE_BUY";
         r.topology = "rsi_tension_release";
         r.state = "continuation";
         r.active = "ACTIVE";
         r.official_fire_buy = true;
         r.reason = "rsi2_reclaim_lower_band";
        }
      else if(load_long)
        {
         r.act = "WAIT_LOADED";
         r.topology = "rsi_tension_load";
         r.state = "big_pullback-loaded";
         r.active = "ACTIVE";
         r.reason = "waiting_rsi2_reclaim";
        }
      else
        {
         r.act = "WAIT_NO_TRADE";
         r.active = "INACTIVE";
         r.reason = "no_load";
        }
     }
   else
     {
      if(!slow_short)
        {
         r.act = "KILL";
         r.reason = "slow_inertia_failed";
         r.active = "INACTIVE";
        }
      else if(fire_short)
        {
         r.act = "FIRE_SELL";
         r.topology = "rsi_tension_release";
         r.active = "ACTIVE";
         r.official_fire_sell = true;
         r.reason = "rsi2_reclaim_upper_band";
        }
      else if(load_short)
        {
         r.act = "WAIT_LOADED";
         r.topology = "rsi_tension_load";
         r.active = "ACTIVE";
         r.reason = "waiting_rsi2_reclaim";
        }
      else
        {
         r.act = "WAIT_NO_TRADE";
         r.active = "INACTIVE";
         r.reason = "no_load";
        }
     }
   AddRow(r);
  }

//+------------------------------------------------------------------+
void ScoreS5(const string sym, const JeSetDef &setd, const string warn)
  {
   JeRow r;
   JeClearRow(r);
   r.family = "EVIDENCE";
   r.strategy = "S5";
   r.plain_name = "Regime gate evidence";
   r.set_id = IntegerToString(setd.set_num);
   r.anchor_tf = JeTfName(setd.anchor);
   r.htf1_tf = JeTfName(setd.htf1);
   r.htf2_tf = JeTfName(setd.htf2);
   r.daily_rsi_warn = warn;
   r.act = "n/a";
   FillCommon(r, sym, setd.anchor);

   int b1 = iBands(sym, setd.htf1, 200, 0, 2.0, PRICE_CLOSE);
   int s1 = iBands(sym, setd.htf1, 20, 0, 2.0, PRICE_CLOSE);
   int b2 = iBands(sym, setd.htf2, 200, 0, 2.0, PRICE_CLOSE);
   int s2 = iBands(sym, setd.htf2, 20, 0, 2.0, PRICE_CLOSE);
   double m1a[], m1b[], m2a[], m2b[];
   const bool ok = (b1 != INVALID_HANDLE && s1 != INVALID_HANDLE && b2 != INVALID_HANDLE && s2 != INVALID_HANDLE &&
                    JeCopyBuf(b1, 0, 3, m1a) && JeCopyBuf(s1, 0, 3, m1b) &&
                    JeCopyBuf(b2, 0, 3, m2a) && JeCopyBuf(s2, 0, 3, m2b));
   JeRelease(b1); JeRelease(s1); JeRelease(b2); JeRelease(s2);
   if(!ok)
     {
      r.data = "thin";
      r.active = "UNDEFINED";
      r.reason = "data_thin";
      r.regime = "UNDEFINED";
      AddRow(r);
      return;
     }
   const double c1 = iClose(sym, setd.htf1, JE_BAR);
   const double c2 = iClose(sym, setd.htf2, JE_BAR);
   r.has_raw_a = r.has_raw_b = r.has_raw_c = r.has_raw_d = true;
   r.raw_a = m1a[JE_BAR]; r.raw_b = m1b[JE_BAR]; r.raw_c = m2a[JE_BAR]; r.raw_d = m2b[JE_BAR];
   const bool bull = (c1 > m1a[JE_BAR] && c1 > m1b[JE_BAR] && c2 > m2a[JE_BAR] && c2 > m2b[JE_BAR]);
   const bool bear = (c1 < m1a[JE_BAR] && c1 < m1b[JE_BAR] && c2 < m2a[JE_BAR] && c2 < m2b[JE_BAR]);
   if(bull)
     {
      r.tide = "long_only";
      r.regime = "bull_trend";
      r.active = "ACTIVE";
      r.reason = "htf_above_bb_middles";
     }
   else if(bear)
     {
      r.tide = "short_only";
      r.regime = "bear_trend";
      r.active = "ACTIVE";
      r.reason = "htf_below_bb_middles";
     }
   else
     {
      r.tide = "flat";
      r.regime = "UNDEFINED";
      r.active = "INACTIVE";
      r.reason = "htf_mixed_or_chop_UNDEFINED";
     }
   r.chop_token = "UNDEFINED";
   r.expansion_token = "UNDEFINED";
   r.cmp = StringFormat("c_htf1=%g;bb200=%g;bb20=%g;c_htf2=%g;bb200b=%g;bb20b=%g;chop=UNDEFINED",
                        c1, m1a[JE_BAR], m1b[JE_BAR], c2, m2a[JE_BAR], m2b[JE_BAR]);
   AddRow(r);
  }

//+------------------------------------------------------------------+
// L1 Shift SMA — 5m / 30m / 4h
//+------------------------------------------------------------------+
void ScoreL1(const string sym, const string warn)
  {
   JeRow r;
   JeClearRow(r);
   r.family = "LEGACY";
   r.strategy = "L1";
   r.plain_name = "Shift SMA door";
   r.set_id = "L";
   r.anchor_tf = "M5";
   r.htf1_tf = "M30";
   r.htf2_tf = "H4";
   r.daily_rsi_warn = warn;
   r.act = "n/a";
   FillCommon(r, sym, PERIOD_M5);

   int h5 = iMA(sym, PERIOD_M5, 1, 1, MODE_SMA, PRICE_CLOSE);
   int h30 = iMA(sym, PERIOD_M30, 1, 1, MODE_SMA, PRICE_CLOSE);
   int h4 = iMA(sym, PERIOD_H4, 1, 1, MODE_SMA, PRICE_CLOSE);
   double a5[], a30[], a4[];
   const bool ok = JeCopyBuf(h5, 0, 4, a5) && JeCopyBuf(h30, 0, 4, a30) && JeCopyBuf(h4, 0, 4, a4);
   JeRelease(h5); JeRelease(h30); JeRelease(h4);
   if(!ok)
     {
      r.data = "thin";
      r.active = "INACTIVE";
      r.reason = "data_thin";
      AddRow(r);
      return;
     }
   const double c5 = iClose(sym, PERIOD_M5, JE_BAR);
   const double c30 = iClose(sym, PERIOD_M30, JE_BAR);
   const double c30p = iClose(sym, PERIOD_M30, JE_PREV);
   const double c4 = iClose(sym, PERIOD_H4, JE_BAR);
   const double c4p = iClose(sym, PERIOD_H4, JE_PREV);
   r.has_raw_a = r.has_raw_b = r.has_raw_c = r.has_raw_d = true;
   r.raw_a = a30[JE_BAR]; r.raw_b = a4[JE_BAR]; r.raw_c = a5[JE_BAR]; r.raw_d = c30p;

   const bool htf_long = (c30 > a30[JE_BAR] && c30p > a30[JE_PREV] && c4 > a4[JE_BAR] && c4p > a4[JE_PREV]);
   const bool htf_short = (c30 < a30[JE_BAR] && c30p < a30[JE_PREV] && c4 < a4[JE_BAR] && c4p < a4[JE_PREV]);
   const bool long_on = htf_long && (c5 < a5[JE_BAR]);
   const bool short_on = htf_short && (c5 > a5[JE_BAR]);

   r.cmp = StringFormat("htf_long=%d;htf_short=%d;c5=%g;sma5=%g;c30=%g;sma30=%g;c4=%g;sma4=%g",
                        htf_long, htf_short, c5, a5[JE_BAR], c30, a30[JE_BAR], c4, a4[JE_BAR]);
   if(long_on)
     {
      r.active = "ACTIVE";
      r.tide = "long_only";
      r.reason = "l1_buy_door";
      r.state = "pullback_under_sma";
     }
   else if(short_on)
     {
      r.active = "ACTIVE";
      r.tide = "short_only";
      r.reason = "l1_sell_door";
      r.state = "rally_over_sma";
     }
   else
     {
      r.active = "INACTIVE";
      r.tide = "flat";
      r.reason = "l1_door_closed";
     }
   AddRow(r);
  }

//+------------------------------------------------------------------+
// L2 CCI momentum — 5m / 30m / 1h  (scored on 5m per written CCI/price rules)
//+------------------------------------------------------------------+
void ScoreL2(const string sym, const string warn)
  {
   JeRow r;
   JeClearRow(r);
   r.family = "LEGACY";
   r.strategy = "L2";
   r.plain_name = "CCI momentum door";
   r.set_id = "L";
   r.anchor_tf = "M5";
   r.htf1_tf = "M30";
   r.htf2_tf = "H1";
   r.daily_rsi_warn = warn;
   r.act = "n/a";
   FillCommon(r, sym, PERIOD_M5);

   int c30 = iCCI(sym, PERIOD_M5, 30, PRICE_TYPICAL);
   int c100 = iCCI(sym, PERIOD_M5, 100, PRICE_TYPICAL);
   int ps = iMA(sym, PERIOD_M5, 1, 2, MODE_SMA, PRICE_CLOSE);
   double a[], b[], sa[], sb[], p[];
   MqlRates warm[];
   CopyRates(sym, PERIOD_M5, 0, 200, warm);
   const bool ok = JeCopyBuf(c30, 0, 16, a) && JeCopyBuf(c100, 0, 16, b) &&
                   JeSmaShifted(a, 1, 4, 4, sa) && JeSmaShifted(b, 1, 4, 4, sb) &&
                   JeCopyBuf(ps, 0, 4, p);
   JeRelease(c30); JeRelease(c100); JeRelease(ps);
   if(!ok)
     {
      r.data = "thin";
      r.active = "INACTIVE";
      r.reason = "data_thin";
      AddRow(r);
      return;
     }
   const double price = iClose(sym, PERIOD_M5, JE_BAR);
   r.has_raw_a = r.has_raw_b = r.has_raw_c = r.has_raw_d = r.has_raw_e = true;
   r.raw_a = a[JE_BAR]; r.raw_b = b[JE_BAR]; r.raw_c = sa[JE_BAR]; r.raw_d = sb[JE_BAR]; r.raw_e = p[JE_BAR];

   const bool long_on = (a[JE_BAR] > 100 && b[JE_BAR] > 100 &&
                         a[JE_BAR] > sa[JE_BAR] && b[JE_BAR] > sb[JE_BAR] &&
                         price < p[JE_BAR]);
   const bool short_on = (a[JE_BAR] < -100 && b[JE_BAR] < -100 &&
                          a[JE_BAR] < sa[JE_BAR] && b[JE_BAR] < sb[JE_BAR] &&
                          price > p[JE_BAR]);
   r.cmp = StringFormat("cci30=%g;cci100=%g;sma30=%g;sma100=%g;price=%g;price_sma=%g;long=%d;short=%d",
                        a[JE_BAR], b[JE_BAR], sa[JE_BAR], sb[JE_BAR], price, p[JE_BAR], long_on, short_on);
   if(long_on)
     {
      r.active = "ACTIVE";
      r.tide = "long_only";
      r.reason = "l2_buy_door";
     }
   else if(short_on)
     {
      r.active = "ACTIVE";
      r.tide = "short_only";
      r.reason = "l2_sell_door";
     }
   else
     {
      r.active = "INACTIVE";
      r.tide = "flat";
      r.reason = "l2_door_closed";
     }
   AddRow(r);
  }

//+------------------------------------------------------------------+
// L3 Shift SMA tunnel — 5m / 30m / 4h
//+------------------------------------------------------------------+
void ScoreL3(const string sym, const string warn)
  {
   JeRow r;
   JeClearRow(r);
   r.family = "LEGACY";
   r.strategy = "L3";
   r.plain_name = "Shift SMA tunnel";
   r.set_id = "L";
   r.anchor_tf = "M5";
   r.htf1_tf = "M30";
   r.htf2_tf = "H4";
   r.daily_rsi_warn = warn;
   r.act = "n/a";
   FillCommon(r, sym, PERIOD_M5);

   // HTF rails on both 30m and 4h — require both HTFs for ACTIVE
   int lo30 = iMA(sym, PERIOD_M30, 1, 4, MODE_SMA, PRICE_LOW);
   int hi30 = iMA(sym, PERIOD_M30, 1, 4, MODE_SMA, PRICE_HIGH);
   int lo4 = iMA(sym, PERIOD_H4, 1, 4, MODE_SMA, PRICE_LOW);
   int hi4 = iMA(sym, PERIOD_H4, 1, 4, MODE_SMA, PRICE_HIGH);
   int lo5 = iMA(sym, PERIOD_M5, 1, 4, MODE_SMA, PRICE_LOW);
   int hi5 = iMA(sym, PERIOD_M5, 1, 4, MODE_SMA, PRICE_HIGH);
   double l30[], h30[], l4[], h4[], l5[], h5[];
   const bool ok = JeCopyBuf(lo30, 0, 4, l30) && JeCopyBuf(hi30, 0, 4, h30) &&
                   JeCopyBuf(lo4, 0, 4, l4) && JeCopyBuf(hi4, 0, 4, h4) &&
                   JeCopyBuf(lo5, 0, 4, l5) && JeCopyBuf(hi5, 0, 4, h5);
   JeRelease(lo30); JeRelease(hi30); JeRelease(lo4); JeRelease(hi4); JeRelease(lo5); JeRelease(hi5);
   if(!ok)
     {
      r.data = "thin";
      r.active = "INACTIVE";
      r.reason = "data_thin";
      AddRow(r);
      return;
     }
   const double c30 = iClose(sym, PERIOD_M30, JE_BAR);
   const double c30p = iClose(sym, PERIOD_M30, JE_PREV);
   const double c4 = iClose(sym, PERIOD_H4, JE_BAR);
   const double c4p = iClose(sym, PERIOD_H4, JE_PREV);
   const double c5 = iClose(sym, PERIOD_M5, JE_BAR);
   r.has_raw_a = r.has_raw_b = r.has_raw_c = r.has_raw_d = r.has_raw_e = true;
   r.raw_a = l30[JE_BAR]; r.raw_b = h30[JE_BAR]; r.raw_c = c30p; r.raw_d = h5[JE_BAR]; r.raw_e = l5[JE_BAR];

   const bool htf_long = (c30 > l30[JE_BAR] && c30p > l30[JE_PREV] && c4 > l4[JE_BAR] && c4p > l4[JE_PREV]);
   const bool htf_short = (c30 < h30[JE_BAR] && c30p < h30[JE_PREV] && c4 < h4[JE_BAR] && c4p < h4[JE_PREV]);
   const bool trig_long = (c5 > h5[JE_BAR]);
   const bool trig_short = (c5 < l5[JE_BAR]);
   const bool long_on = htf_long && trig_long;
   const bool short_on = htf_short && trig_short;

   r.cmp = StringFormat("htf_long=%d;trig_long=%d;htf_short=%d;trig_short=%d;c5=%g;upper5=%g;lower5=%g",
                        htf_long, trig_long, htf_short, trig_short, c5, h5[JE_BAR], l5[JE_BAR]);
   if(long_on)
     {
      r.active = "ACTIVE";
      r.tide = "long_only";
      r.reason = "l3_buy_tunnel";
     }
   else if(short_on)
     {
      r.active = "ACTIVE";
      r.tide = "short_only";
      r.reason = "l3_sell_tunnel";
     }
   else
     {
      r.active = "INACTIVE";
      r.tide = "flat";
      r.reason = "l3_door_closed";
     }
   AddRow(r);
  }

//+------------------------------------------------------------------+
// L4 Fractals — log raw iFractals; UNDEFINED fire (rule too vague for threshold-free ACTIVE)
//+------------------------------------------------------------------+
void ScoreL4(const string sym, const string warn)
  {
   JeRow r;
   JeClearRow(r);
   r.family = "LEGACY";
   r.strategy = "L4";
   r.plain_name = "Fractal swing door";
   r.set_id = "L";
   r.anchor_tf = "M5";
   r.htf1_tf = "M30";
   r.htf2_tf = "H4";
   r.daily_rsi_warn = warn;
   r.act = "n/a";
   r.state = "UNDEFINED";
   r.active = "UNDEFINED";
   r.reason = "fractal_rule_vague_no_threshold";
   FillCommon(r, sym, PERIOD_M30);

   int hf = iFractals(sym, PERIOD_M30);
   double up[], dn[];
   if(hf == INVALID_HANDLE || !JeCopyBuf(hf, 0, 30, up) || !JeCopyBuf(hf, 1, 30, dn))
     {
      r.data = "thin";
      JeRelease(hf);
      AddRow(r);
      return;
     }
   JeRelease(hf);
   double last_up = 0, last_dn = 0;
   int up_n = 0, dn_n = 0;
   for(int i = JE_BAR; i < 30; i++)
     {
      if(up[i] != 0 && up[i] != EMPTY_VALUE)
        {
         if(last_up == 0)
            last_up = up[i];
         up_n++;
        }
      if(dn[i] != 0 && dn[i] != EMPTY_VALUE)
        {
         if(last_dn == 0)
            last_dn = dn[i];
         dn_n++;
        }
     }
   r.has_raw_a = r.has_raw_b = r.has_raw_c = r.has_raw_d = true;
   r.raw_a = last_up;
   r.raw_b = last_dn;
   r.raw_c = up_n;
   r.raw_d = dn_n;
   r.cmp = StringFormat("last_up_frac=%g;last_dn_frac=%g;up_marks_in_30=%d;dn_marks_in_30=%d;note=need_two_HH_definition_UNDEFINED",
                        last_up, last_dn, up_n, dn_n);
   r.tide = "flat";
   AddRow(r);
  }

//+------------------------------------------------------------------+
// RSI(14) vs SMA(1) shift +4 on that RSI — same formula on every TF.
// GATE telemetry only: act stays n/a; never mutates S1–S4 act/tide/conflict.
//+------------------------------------------------------------------+
void ScoreRsiTideGateTf(const string sym, const string warn,
                        const ENUM_TIMEFRAMES tf,
                        const string strategy_id,
                        const string plain_name,
                        const string reason_prefix)
  {
   JeRow r;
   JeClearRow(r);
   r.family = "GATE";
   r.strategy = strategy_id;
   r.plain_name = plain_name;
   r.set_id = "G";
   const string tf_name = JeTfName(tf);
   r.anchor_tf = tf_name;
   r.htf1_tf = tf_name;
   r.htf2_tf = tf_name;
   r.daily_rsi_warn = warn;
   r.act = "n/a";
   FillCommon(r, sym, tf);

   int h_rsi = iRSI(sym, tf, 14, PRICE_CLOSE);
   double rsi[], rail[];
   MqlRates warm[];
   CopyRates(sym, tf, 0, 40, warm);
   const bool ok = (h_rsi != INVALID_HANDLE && JeCopyBuf(h_rsi, 0, 12, rsi) && JeSmaShifted(rsi, 1, 4, 4, rail));
   JeRelease(h_rsi);
   if(!ok)
     {
      r.data = "thin";
      r.active = "INACTIVE";
      r.reason = "data_thin";
      AddRow(r);
      return;
     }
   r.has_raw_a = r.has_raw_b = true;
   r.raw_a = rsi[JE_BAR];
   r.raw_b = rail[JE_BAR];
   r.cmp = StringFormat("rsi14=%g;sma1_shift4=%g;warn=%s", rsi[JE_BAR], rail[JE_BAR], warn);
   if(rsi[JE_BAR] > rail[JE_BAR])
     {
      r.active = "ACTIVE";
      r.tide = "long_only";
      r.reason = reason_prefix + "_long_only_permission";
      r.state = "regime_gate";
     }
   else if(rsi[JE_BAR] < rail[JE_BAR])
     {
      r.active = "ACTIVE";
      r.tide = "short_only";
      r.reason = reason_prefix + "_short_only_permission";
      r.state = "regime_gate";
     }
   else
     {
      r.active = "INACTIVE";
      r.tide = "flat";
      r.reason = reason_prefix + "_on_rail";
     }
   AddRow(r);
  }

//+------------------------------------------------------------------+
// Dual CCI extreme harness. Log only. act stays n/a.
// Does not change S1–S4 act, tide, or strategy_direction_conflict.
// Level: both CCI(30) and CCI(100) beyond ±100 on the last closed bar.
// Confirm: both also beyond SMA(1) shift +4 of that same CCI. Typical price.
//+------------------------------------------------------------------+
void ScoreCciExtremeTf(const string sym, const string warn,
                       const ENUM_TIMEFRAMES tf,
                       const string strategy_id,
                       const string plain_name,
                       const string reason_prefix)
  {
   JeRow r;
   JeClearRow(r);
   r.family = "GATE";
   r.strategy = strategy_id;
   r.plain_name = plain_name;
   r.set_id = "C";
   const string tf_name = JeTfName(tf);
   r.anchor_tf = tf_name;
   r.htf1_tf = tf_name;
   r.htf2_tf = tf_name;
   r.daily_rsi_warn = warn;
   r.act = "n/a";
   r.official_fire_buy = false;
   r.official_fire_sell = false;
   FillCommon(r, sym, tf);

   int h30 = iCCI(sym, tf, 30, PRICE_TYPICAL);
   int h100 = iCCI(sym, tf, 100, PRICE_TYPICAL);
   double c30[], c100[], s30[], s100[];
   const bool ok = (h30 != INVALID_HANDLE && h100 != INVALID_HANDLE
                    && JeCopyBuf(h30, 0, 12, c30) && JeCopyBuf(h100, 0, 12, c100)
                    && JeSmaShifted(c30, 1, 4, 4, s30) && JeSmaShifted(c100, 1, 4, 4, s100));
   JeRelease(h30);
   JeRelease(h100);
   if(!ok)
     {
      r.data = "thin";
      r.active = "INACTIVE";
      r.tide = "flat";
      r.reason = "data_thin";
      AddRow(r);
      return;
     }
   const double v30 = c30[JE_BAR];
   const double v100 = c100[JE_BAR];
   const double m30 = s30[JE_BAR];
   const double m100 = s100[JE_BAR];
   r.has_raw_a = r.has_raw_b = r.has_raw_c = r.has_raw_d = true;
   r.raw_a = v30;
   r.raw_b = v100;
   r.raw_c = m30;
   r.raw_d = m100;
   const bool level_buy = (v30 > 100.0 && v100 > 100.0);
   const bool level_sell = (v30 < -100.0 && v100 < -100.0);
   const bool confirm_buy = (level_buy && v30 > m30 && v100 > m100);
   const bool confirm_sell = (level_sell && v30 < m30 && v100 < m100);
   r.cmp = StringFormat("cci30=%g;cci100=%g;sma30_shift4=%g;sma100_shift4=%g;level_buy=%d;level_sell=%d;confirm_buy=%d;confirm_sell=%d",
                        v30, v100, m30, m100, level_buy, level_sell, confirm_buy, confirm_sell);
   r.topology = "dual_cci_extreme";
   if(level_buy)
     {
      r.active = "ACTIVE";
      r.tide = "long_only";
      r.state = (confirm_buy ? "cci_extreme_confirmed" : "cci_extreme");
      r.reason = reason_prefix + (confirm_buy ? "_confirm_buy" : "_level_buy");
     }
   else if(level_sell)
     {
      r.active = "ACTIVE";
      r.tide = "short_only";
      r.state = (confirm_sell ? "cci_extreme_confirmed" : "cci_extreme");
      r.reason = reason_prefix + (confirm_sell ? "_confirm_sell" : "_level_sell");
     }
   else
     {
      r.active = "INACTIVE";
      r.tide = "flat";
      r.state = "none";
      r.reason = reason_prefix + "_not_both";
     }
   AddRow(r);
  }

//+------------------------------------------------------------------+
void ScoreCciHarness(const string sym, const string warn)
  {
   ScoreCciExtremeTf(sym, warn, PERIOD_M1,  "C1", "M1 dual CCI extreme", "c1");
   ScoreCciExtremeTf(sym, warn, PERIOD_M5,  "C2", "M5 dual CCI extreme", "c2");
   ScoreCciExtremeTf(sym, warn, PERIOD_M15, "C3", "M15 dual CCI extreme", "c3");
   ScoreCciExtremeTf(sym, warn, PERIOD_M30, "C4", "M30 dual CCI extreme", "c4");
   ScoreCciExtremeTf(sym, warn, PERIOD_H1,  "C5", "H1 dual CCI extreme", "c5");
   ScoreCciExtremeTf(sym, warn, PERIOD_H4,  "C6", "H4 dual CCI extreme", "c6");
   ScoreCciExtremeTf(sym, warn, PERIOD_D1,  "C7", "D1 dual CCI extreme", "c7");
  }

//+------------------------------------------------------------------+
void ScoreG1(const string sym, const string warn)
  {
   // G1 = D1 (existing). G2–G7 = M1/M5/M15/M30/H1/H4 harness TFs.
   // H1 strategy id remains Heikin Ashi door; 1h RSI gate is G6.
   ScoreRsiTideGateTf(sym, warn, PERIOD_D1,  "G1", "Daily RSI tide gate", "g1");
   ScoreRsiTideGateTf(sym, warn, PERIOD_M1,  "G2", "M1 RSI tide gate",    "g2");
   ScoreRsiTideGateTf(sym, warn, PERIOD_M5,  "G3", "M5 RSI tide gate",    "g3");
   ScoreRsiTideGateTf(sym, warn, PERIOD_M15, "G4", "M15 RSI tide gate",   "g4");
   ScoreRsiTideGateTf(sym, warn, PERIOD_M30, "G5", "M30 RSI tide gate",   "g5");
   ScoreRsiTideGateTf(sym, warn, PERIOD_H1,  "G6", "H1 RSI tide gate",    "g6");
   ScoreRsiTideGateTf(sym, warn, PERIOD_H4,  "G7", "H4 RSI tide gate",    "g7");
  }

//+------------------------------------------------------------------+
void ScoreH1(const string sym, const string warn)
  {
   JeRow r;
   JeClearRow(r);
   r.family = "GATE";
   r.strategy = "H1";
   r.plain_name = "Heikin Ashi door";
   r.set_id = "H";
   r.anchor_tf = "M1";
   r.htf1_tf = "M5";
   r.htf2_tf = "M15";
   r.daily_rsi_warn = warn;
   r.act = "n/a";
   FillCommon(r, sym, PERIOD_M5);

   const int g5 = JeHaConsecutive(sym, PERIOD_M5, true);
   const int g15 = JeHaConsecutive(sym, PERIOD_M15, true);
   const int r1 = JeHaConsecutive(sym, PERIOD_M1, false);
   const int r5 = JeHaConsecutive(sym, PERIOD_M5, false);
   const int r15 = JeHaConsecutive(sym, PERIOD_M15, false);
   const int g1 = JeHaConsecutive(sym, PERIOD_M1, true);
   if(g5 < 0 || g15 < 0 || r1 < 0)
     {
      r.data = "thin";
      r.active = "INACTIVE";
      r.reason = "data_thin";
      AddRow(r);
      return;
     }
   r.has_raw_a = r.has_raw_b = r.has_raw_c = r.has_raw_d = r.has_raw_e = r.has_raw_f = true;
   r.raw_a = g5; r.raw_b = g15; r.raw_c = r1; r.raw_d = r5; r.raw_e = r15; r.raw_f = g1;

   const bool buy = (g5 >= 2 && g15 >= 2 && r1 >= 1);
   const bool sell = (r5 >= 2 && r15 >= 2 && g1 >= 1);
   r.cmp = StringFormat("ha_green_m5=%d;ha_green_m15=%d;ha_red_m1=%d;ha_red_m5=%d;ha_red_m15=%d;ha_green_m1=%d;buy=%d;sell=%d",
                        g5, g15, r1, r5, r15, g1, buy, sell);
   if(buy && !sell)
     {
      r.active = "ACTIVE";
      r.tide = "long_only";
      r.reason = "h1_buy_door";
      r.state = "ha_pullback_door";
     }
   else if(sell && !buy)
     {
      r.active = "ACTIVE";
      r.tide = "short_only";
      r.reason = "h1_sell_door";
      r.state = "ha_pullback_door";
     }
   else
     {
      r.active = "INACTIVE";
      r.tide = "flat";
      r.reason = (buy && sell ? "h1_both_doors" : "h1_door_closed");
     }
   AddRow(r);
  }

//+------------------------------------------------------------------+
void ApplyConflicts(void)
  {
   for(int i = 0; i < g_row_n; i++)
     {
      if(g_rows[i].family != "OFFICIAL")
         continue;
      if(!g_rows[i].official_fire_buy && !g_rows[i].official_fire_sell)
         continue;
      bool buy = g_rows[i].official_fire_buy;
      bool sell = g_rows[i].official_fire_sell;
      for(int j = 0; j < g_row_n; j++)
        {
         if(i == j)
            continue;
         if(g_rows[j].family != "OFFICIAL")
            continue;
         if(g_rows[j].symbol != g_rows[i].symbol)
            continue;
         if(g_rows[j].set_id != g_rows[i].set_id)
            continue;
         if(g_rows[j].official_fire_buy)
            buy = true;
         if(g_rows[j].official_fire_sell)
            sell = true;
        }
      if(buy && sell)
        {
         for(int j = 0; j < g_row_n; j++)
           {
            if(g_rows[j].family != "OFFICIAL")
               continue;
            if(g_rows[j].symbol != g_rows[i].symbol || g_rows[j].set_id != g_rows[i].set_id)
               continue;
            if(g_rows[j].official_fire_buy || g_rows[j].official_fire_sell)
              {
               g_rows[j].tide = "flat";
               g_rows[j].act = "KILL";
               g_rows[j].reason = "strategy_direction_conflict";
               g_rows[j].active = "INACTIVE";
              }
           }
        }
     }
  }

//+------------------------------------------------------------------+
int FindNotify(const string key)
  {
   for(int i = 0; i < g_notify_n; i++)
      if(g_notify_keys[i] == key)
         return i;
   return -1;
  }

void LoadNotifyState(void)
  {
   g_notify_n = 0;
   ArrayResize(g_notify_keys, 0);
   ArrayResize(g_notify_acts, 0);
   int h = FileOpen(InpNotifyPath, FILE_READ|FILE_CSV|FILE_ANSI|FILE_SHARE_READ|FILE_SHARE_WRITE, ',');
   if(h == INVALID_HANDLE)
      return;
   while(!FileIsEnding(h))
     {
      string key = FileReadString(h);
      string act = FileReadString(h);
      string ts = FileReadString(h);
      if(key == "" || key == "key")
         continue;
      ArrayResize(g_notify_keys, g_notify_n + 1);
      ArrayResize(g_notify_acts, g_notify_n + 1);
      g_notify_keys[g_notify_n] = key;
      g_notify_acts[g_notify_n] = act;
      g_notify_n++;
      if(ts == "" && FileIsEnding(h))
         break;
     }
   FileClose(h);
  }

void SaveNotifyState(void)
  {
   int h = FileOpen(InpNotifyPath, FILE_WRITE|FILE_CSV|FILE_ANSI|FILE_SHARE_READ|FILE_SHARE_WRITE, ',');
   if(h == INVALID_HANDLE)
      return;
   FileWrite(h, "key", "last_act", "last_ts");
   const string ts = TimeToString(TimeCurrent(), TIME_DATE|TIME_SECONDS);
   for(int i = 0; i < g_notify_n; i++)
      FileWrite(h, g_notify_keys[i], g_notify_acts[i], ts);
   FileClose(h);
  }

void MaybePush(const JeRow &r)
  {
   if(!InpPush)
      return;
   if(r.family != "OFFICIAL")
      return;
   if(StringFind(r.reason, "emerged_") == 0)
      return;
   if(r.act != "FIRE_BUY" && r.act != "FIRE_SELL" && r.act != "KILL")
      return;
   const string key = r.symbol + "|" + r.set_id + "|" + r.strategy;
   const int ix = FindNotify(key);
   if(ix >= 0 && g_notify_acts[ix] == r.act)
      return;
   string msg = StringFormat("JARVIS %s %s set%s %s %s", r.act, r.symbol, r.set_id, r.strategy, r.reason);
   SendNotification(msg);
   if(ix < 0)
     {
      ArrayResize(g_notify_keys, g_notify_n + 1);
      ArrayResize(g_notify_acts, g_notify_n + 1);
      g_notify_keys[g_notify_n] = key;
      g_notify_acts[g_notify_n] = r.act;
      g_notify_n++;
     }
   else
      g_notify_acts[ix] = r.act;
  }

int FindTape(const string key)
  {
   for(int i = 0; i < g_tape_n; i++)
      if(g_tape_keys[i] == key)
         return i;
   return -1;
  }

void AppendTape(const JeRow &r, const string ts)
  {
   const string key = r.symbol + "|" + r.set_id + "|" + r.strategy;
   const string act_key = r.act + "|" + r.active;
   const int ix = FindTape(key);
   bool changed = true;
   if(ix >= 0)
      changed = (g_tape_acts[ix] != act_key || g_tape_bars[ix] != r.closed_bar_time);
   if(!changed)
      return;
   if(ix < 0)
     {
      ArrayResize(g_tape_keys, g_tape_n + 1);
      ArrayResize(g_tape_acts, g_tape_n + 1);
      ArrayResize(g_tape_bars, g_tape_n + 1);
      g_tape_keys[g_tape_n] = key;
      g_tape_acts[g_tape_n] = act_key;
      g_tape_bars[g_tape_n] = r.closed_bar_time;
      g_tape_n++;
     }
   else
     {
      g_tape_acts[ix] = act_key;
      g_tape_bars[ix] = r.closed_bar_time;
     }

   MqlDateTime dt;
   TimeToStruct(TimeCurrent(), dt);
   string day = StringFormat("%04d-%02d-%02d", dt.year, dt.mon, dt.day);
   string path = InpTapeDir + "\\" + day + ".csv";
   const bool exists = FileIsExist(path);
   int h = FileOpen(path, FILE_READ|FILE_WRITE|FILE_TXT|FILE_ANSI|FILE_SHARE_READ|FILE_SHARE_WRITE);
   if(h == INVALID_HANDLE)
      return;
   FileSeek(h, 0, SEEK_END);
   if(!exists || FileSize(h) == 0)
      FileWriteString(h, JeHeader() + "\n");
   FileWriteString(h, JeRowLine(r, ts) + "\n");
   FileClose(h);
  }

void WriteBoard(void)
  {
   const string ts = TimeToString(TimeCurrent(), TIME_DATE|TIME_SECONDS);
   int h = FileOpen(InpBoardPath, FILE_WRITE|FILE_TXT|FILE_ANSI|FILE_SHARE_READ|FILE_SHARE_WRITE);
   if(h == INVALID_HANDLE)
     {
      Print("JarvisEyes: cannot write board ", InpBoardPath, " err=", GetLastError());
      return;
     }
   FileWriteString(h, JeHeader() + "\n");
   for(int i = 0; i < g_row_n; i++)
     {
      FileWriteString(h, JeRowLine(g_rows[i], ts) + "\n");
      AppendTape(g_rows[i], ts);
      MaybePush(g_rows[i]);
     }
   FileClose(h);
   SaveNotifyState();
   SaveEmergence();
   JeAgentLogEm(g_em_changed, g_em_seen, g_em_sample);
  }

//+------------------------------------------------------------------+
void ScanPass(void)
  {
   static datetime s_dbg_at = 0;
   if(TimeCurrent() - s_dbg_at >= 30)
     {
      JeAgentLog("LIVE", "scan uses typical price on closed bar 1");
      s_dbg_at = TimeCurrent();
     }
   g_row_n = 0;
   g_em_changed = 0;
   g_em_seen = 0;
   g_em_sample = "";
   ArrayResize(g_rows, 0);

   JeSetDef sets[4];
   sets[0].set_num = 1; sets[0].anchor = PERIOD_M1;  sets[0].htf1 = PERIOD_M15; sets[0].htf2 = PERIOD_M30;
   sets[1].set_num = 2; sets[1].anchor = PERIOD_M5;  sets[1].htf1 = PERIOD_M30; sets[1].htf2 = PERIOD_H1;
   sets[2].set_num = 3; sets[2].anchor = PERIOD_M15; sets[2].htf1 = PERIOD_H1;  sets[2].htf2 = PERIOD_H4;
   sets[3].set_num = 4; sets[3].anchor = PERIOD_M30; sets[3].htf1 = PERIOD_H4;  sets[3].htf2 = PERIOD_D1;
   bool on[4];
   on[0] = InpSet1; on[1] = InpSet2; on[2] = InpSet3; on[3] = InpSet4;

   for(int s = 0; s < g_sym_n; s++)
     {
      const string sym = g_syms[s];
      const string warn = DailyRsiWarn(sym);

      for(int k = 0; k < 4; k++)
        {
         if(!on[k])
            continue;
         ScoreS1(sym, sets[k], warn);
         ScoreS2(sym, sets[k], warn);
         ScoreS3(sym, sets[k], warn);
         ScoreS4(sym, sets[k], warn);
         if(InpScoreS5)
            ScoreS5(sym, sets[k], warn);
        }

      if(InpScoreLegacy)
        {
         ScoreL1(sym, warn);
         ScoreL2(sym, warn);
         ScoreL3(sym, warn);
         ScoreL4(sym, warn);
        }
      if(InpScoreGate)
         ScoreG1(sym, warn);
      if(InpScoreHA)
         ScoreH1(sym, warn);
      if(InpScoreCciHarness)
         ScoreCciHarness(sym, warn);
     }

   ApplyConflicts();
   WriteBoard();
  }

//+------------------------------------------------------------------+

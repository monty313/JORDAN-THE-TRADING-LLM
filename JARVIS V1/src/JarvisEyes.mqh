//+------------------------------------------------------------------+
//| JarvisEyes.mqh — closed-bar sensors (index 1 only)                 |
//+------------------------------------------------------------------+
#ifndef JARVIS_EYES_MQH
#define JARVIS_EYES_MQH

#define JE_MAX_ROWS  4096
#define JE_MAX_SYMS  120
#define JE_BAR       1
#define JE_PREV      2

struct JeRow
  {
   string symbol;
   string family;
   string strategy;
   string plain_name;
   string set_id;
   string anchor_tf;
   string htf1_tf;
   string htf2_tf;
   int    spread_points;
   string data;
   string active;
   string tide;
   string regime;
   string state;
   string topology;
   string act;
   string reason;
   string daily_rsi_warn;
   datetime closed_bar_time;
   double open1;
   double high1;
   double low1;
   double close1;
   double forming_close0;
   string cmp;
   string chop_token;
   string expansion_token;
   double raw_a;
   double raw_b;
   double raw_c;
   double raw_d;
   double raw_e;
   double raw_f;
   bool   has_raw_a;
   bool   has_raw_b;
   bool   has_raw_c;
   bool   has_raw_d;
   bool   has_raw_e;
   bool   has_raw_f;
   bool   official_fire_buy;
   bool   official_fire_sell;
  };

struct JeSetDef
  {
   int              set_num;
   ENUM_TIMEFRAMES  anchor;
   ENUM_TIMEFRAMES  htf1;
   ENUM_TIMEFRAMES  htf2;
  };

string JeTfName(const ENUM_TIMEFRAMES tf)
  {
   switch(tf)
     {
      case PERIOD_M1:  return "M1";
      case PERIOD_M5:  return "M5";
      case PERIOD_M15: return "M15";
      case PERIOD_M30: return "M30";
      case PERIOD_H1:  return "H1";
      case PERIOD_H4:  return "H4";
      case PERIOD_D1:  return "D1";
      default:         return IntegerToString((int)tf);
     }
  }

string JeCsvEsc(const string s)
  {
   string o = s;
   StringReplace(o, "\"", "'");
   StringReplace(o, ",", ";");
   StringReplace(o, "\n", " ");
   StringReplace(o, "\r", " ");
   return o;
  }

string JeNum(const double v, const bool has)
  {
   if(!has)
      return "";
   return DoubleToString(v, 8);
  }

void JeClearRow(JeRow &r)
  {
   r.symbol = "";
   r.family = "";
   r.strategy = "";
   r.plain_name = "";
   r.set_id = "";
   r.anchor_tf = "";
   r.htf1_tf = "";
   r.htf2_tf = "";
   r.spread_points = 0;
   r.data = "fresh";
   r.active = "INACTIVE";
   r.tide = "flat";
   r.regime = "UNDEFINED";
   r.state = "none";
   r.topology = "none";
   r.act = "n/a";
   r.reason = "";
   r.daily_rsi_warn = "flat";
   r.closed_bar_time = 0;
   r.open1 = 0;
   r.high1 = 0;
   r.low1 = 0;
   r.close1 = 0;
   r.forming_close0 = 0;
   r.cmp = "";
   r.chop_token = "UNDEFINED";
   r.expansion_token = "UNDEFINED";
   r.raw_a = r.raw_b = r.raw_c = r.raw_d = r.raw_e = r.raw_f = 0;
   r.has_raw_a = r.has_raw_b = r.has_raw_c = r.has_raw_d = r.has_raw_e = r.has_raw_f = false;
   r.official_fire_buy = false;
   r.official_fire_sell = false;
  }

string JeRowLine(const JeRow &r, const string ts)
  {
   return StringFormat(
      "%s,%s,%s,%s,%s,%s,%s,%s,%s,%d,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s",
      JeCsvEsc(ts),
      JeCsvEsc(r.symbol),
      JeCsvEsc(r.family),
      JeCsvEsc(r.strategy),
      JeCsvEsc(r.plain_name),
      JeCsvEsc(r.set_id),
      JeCsvEsc(r.anchor_tf),
      JeCsvEsc(r.htf1_tf),
      JeCsvEsc(r.htf2_tf),
      r.spread_points,
      JeCsvEsc(r.data),
      JeCsvEsc(r.active),
      JeCsvEsc(r.tide),
      JeCsvEsc(r.regime),
      JeCsvEsc(r.state),
      JeCsvEsc(r.topology),
      JeCsvEsc(r.act),
      JeCsvEsc(r.reason),
      JeCsvEsc(r.daily_rsi_warn),
      TimeToString(r.closed_bar_time, TIME_DATE|TIME_SECONDS),
      DoubleToString(r.open1, 8),
      DoubleToString(r.high1, 8),
      DoubleToString(r.low1, 8),
      DoubleToString(r.close1, 8),
      DoubleToString(r.forming_close0, 8),
      JeCsvEsc(r.cmp),
      JeCsvEsc(r.chop_token),
      JeCsvEsc(r.expansion_token),
      JeNum(r.raw_a, r.has_raw_a),
      JeNum(r.raw_b, r.has_raw_b),
      JeNum(r.raw_c, r.has_raw_c),
      JeNum(r.raw_d, r.has_raw_d),
      JeNum(r.raw_e, r.has_raw_e),
      JeNum(r.raw_f, r.has_raw_f)
   );
  }

string JeHeader(void)
  {
   return "ts,symbol,family,strategy,plain_name,set,anchor_tf,htf1_tf,htf2_tf,spread_points,data,active,tide,regime,state,topology,act,reason,daily_rsi_warn,closed_bar_time,open1,high1,low1,close1,forming_close0,cmp,chop_token,expansion_token,raw_a,raw_b,raw_c,raw_d,raw_e,raw_f";
  }

bool JeCopyBuf(const int handle, const int buf, const int count, double &out[])
  {
   ArraySetAsSeries(out, true);
   ArrayResize(out, count);
   if(handle == INVALID_HANDLE)
      return false;
   for(int attempt = 0; attempt < 30; attempt++)
     {
      const int bc = BarsCalculated(handle);
      if(bc < 0)
        {
         Sleep(5);
         continue;
        }
      if(bc > 0 && bc < count && attempt < 25)
        {
         Sleep(5);
         continue;
        }
      if(CopyBuffer(handle, buf, 0, count, out) == count)
         return true;
      Sleep(5);
     }
   return false;
  }

// SMA on series-as-series buffer; shift displaces result (MT5 ma_shift style)
bool JeSmaShifted(const double &src[], const int period, const int shift, const int need, double &dst[])
  {
   const int n = ArraySize(src);
   if(n < period + shift + need)
      return false;
   ArraySetAsSeries(dst, true);
   ArrayResize(dst, need);
   for(int i = 0; i < need; i++)
     {
      double sum = 0.0;
      const int base = i + shift;
      for(int k = 0; k < period; k++)
         sum += src[base + k];
      dst[i] = sum / period;
     }
   return true;
  }

bool JeBandsOnSeries(const double &src[], const int period, const int shift, const double dev,
                     const int need, double &mid[], double &upper[], double &lower[])
  {
   const int n = ArraySize(src);
   if(n < period + shift + need)
      return false;
   ArraySetAsSeries(mid, true);
   ArraySetAsSeries(upper, true);
   ArraySetAsSeries(lower, true);
   ArrayResize(mid, need);
   ArrayResize(upper, need);
   ArrayResize(lower, need);
   for(int i = 0; i < need; i++)
     {
      const int base = i + shift;
      double sum = 0.0;
      for(int k = 0; k < period; k++)
         sum += src[base + k];
      const double m = sum / period;
      double var = 0.0;
      for(int k = 0; k < period; k++)
        {
         const double d = src[base + k] - m;
         var += d * d;
        }
      const double sd = MathSqrt(var / period);
      mid[i] = m;
      upper[i] = m + dev * sd;
      lower[i] = m - dev * sd;
     }
   return true;
  }

bool JeRates(const string sym, const ENUM_TIMEFRAMES tf, const int count, MqlRates &rates[])
  {
   ArraySetAsSeries(rates, true);
   return (CopyRates(sym, tf, 0, count, rates) == count);
  }

// Typical price (high+low+close)/3. Decision shift is JE_BAR (last closed). Shift 0 is telemetry only.
double JeTypical(const string sym, const ENUM_TIMEFRAMES tf, const int shift)
  {
   const double h = iHigh(sym, tf, shift);
   const double l = iLow(sym, tf, shift);
   const double c = iClose(sym, tf, shift);
   return (h + l + c) / 3.0;
  }

int JeSpread(const string sym)
  {
   return (int)SymbolInfoInteger(sym, SYMBOL_SPREAD);
  }

bool JeQuoteFresh(const string sym, const int max_age_sec)
  {
   MqlTick t;
   if(!SymbolInfoTick(sym, t))
      return false;
   if(t.time == 0)
      return false;
   if(max_age_sec <= 0)
      return true;
   return ((TimeCurrent() - t.time) <= max_age_sec);
  }

//--- reclaim: prev X<=B and now X>B (bullish)
bool JeReclaimUp(const double x1, const double b1, const double x2, const double b2)
  {
   return (x2 <= b2 && x1 > b1);
  }

bool JeReclaimDn(const double x1, const double b1, const double x2, const double b2)
  {
   return (x2 >= b2 && x1 < b1);
  }

void JeRelease(int &h)
  {
   if(h != INVALID_HANDLE)
     {
      IndicatorRelease(h);
      h = INVALID_HANDLE;
     }
  }

// Heikin Ashi closed colors: count consecutive from bar 1
int JeHaGreenCount(const string sym, const ENUM_TIMEFRAMES tf, const int need_look)
  {
   MqlRates r[];
   if(!JeRates(sym, tf, need_look + 5, r))
      return -1;
   double ha_o = (r[need_look + 2].open + r[need_look + 2].close) * 0.5;
   double ha_c = (r[need_look + 2].open + r[need_look + 2].high + r[need_look + 2].low + r[need_look + 2].close) * 0.25;
   int green = 0;
   for(int i = need_look + 1; i >= JE_BAR; i--)
     {
      const double o = ha_o;
      const double c = (r[i].open + r[i].high + r[i].low + r[i].close) * 0.25;
      ha_o = (o + ha_c) * 0.5;
      ha_c = c;
      if(i == JE_BAR || i == JE_PREV || i <= need_look)
        {
         // rebuild properly from oldest
        }
     }
   // rebuild from oldest in series array
   const int n = ArraySize(r);
   if(n < 4)
      return -1;
   double prev_o = (r[n - 1].open + r[n - 1].close) * 0.5;
   double prev_c = (r[n - 1].open + r[n - 1].high + r[n - 1].low + r[n - 1].close) * 0.25;
   bool colors[];
   ArrayResize(colors, n);
   colors[n - 1] = (prev_c >= prev_o);
   for(int i = n - 2; i >= 0; i--)
     {
      const double c = (r[i].open + r[i].high + r[i].low + r[i].close) * 0.25;
      const double o = (prev_o + prev_c) * 0.5;
      colors[i] = (c >= o);
      prev_o = o;
      prev_c = c;
     }
   int g = 0;
   for(int i = JE_BAR; i < n && g < 20; i++)
     {
      if(!colors[i])
         break;
      g++;
     }
   return g;
  }

int JeHaRedCount(const string sym, const ENUM_TIMEFRAMES tf)
  {
   MqlRates r[];
   if(!JeRates(sym, tf, 40, r))
      return -1;
   const int n = ArraySize(r);
   double prev_o = (r[n - 1].open + r[n - 1].close) * 0.5;
   double prev_c = (r[n - 1].open + r[n - 1].high + r[n - 1].low + r[n - 1].close) * 0.25;
   bool green[];
   ArrayResize(green, n);
   green[n - 1] = (prev_c >= prev_o);
   for(int i = n - 2; i >= 0; i--)
     {
      const double c = (r[i].open + r[i].high + r[i].low + r[i].close) * 0.25;
      const double o = (prev_o + prev_c) * 0.5;
      green[i] = (c >= o);
      prev_o = o;
      prev_c = c;
     }
   int red = 0;
   for(int i = JE_BAR; i < n && red < 20; i++)
     {
      if(green[i])
         break;
      red++;
     }
   return red;
  }

int JeHaConsecutive(const string sym, const ENUM_TIMEFRAMES tf, const bool want_green)
  {
   MqlRates r[];
   if(!JeRates(sym, tf, 40, r))
      return -1;
   const int n = ArraySize(r);
   if(n < 5)
      return -1;
   double prev_o = (r[n - 1].open + r[n - 1].close) * 0.5;
   double prev_c = (r[n - 1].open + r[n - 1].high + r[n - 1].low + r[n - 1].close) * 0.25;
   bool is_green[];
   ArrayResize(is_green, n);
   is_green[n - 1] = (prev_c >= prev_o);
   for(int i = n - 2; i >= 0; i--)
     {
      const double c = (r[i].open + r[i].high + r[i].low + r[i].close) * 0.25;
      const double o = (prev_o + prev_c) * 0.5;
      is_green[i] = (c >= o);
      prev_o = o;
      prev_c = c;
     }
   int cnt = 0;
   for(int i = JE_BAR; i < n && cnt < 30; i++)
     {
      if(want_green)
        {
         if(!is_green[i])
            break;
        }
      else
        {
         if(is_green[i])
            break;
        }
      cnt++;
     }
   return cnt;
  }

#endif

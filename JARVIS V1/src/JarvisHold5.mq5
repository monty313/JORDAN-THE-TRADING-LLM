//+------------------------------------------------------------------+
//| JarvisHold5.mq5                                                  |
//| Demo only. Removes broker stops, closes magic 771249 at 5 min.  |
//+------------------------------------------------------------------+
#property strict
#include <Trade\Trade.mqh>

input long InpMagic = 771249;
input int  InpHoldSec = 300;

CTrade trade;

int OnInit()
  {
   if((ENUM_ACCOUNT_TRADE_MODE)AccountInfoInteger(ACCOUNT_TRADE_MODE) != ACCOUNT_TRADE_MODE_DEMO)
      return INIT_FAILED;
   trade.SetExpertMagicNumber(InpMagic);
   trade.SetDeviationInPoints(30);
   EventSetTimer(1);
   return INIT_SUCCEEDED;
  }

void OnDeinit(const int reason)
  {
   EventKillTimer();
  }

void OnTimer()
  {
   if((ENUM_ACCOUNT_TRADE_MODE)AccountInfoInteger(ACCOUNT_TRADE_MODE) != ACCOUNT_TRADE_MODE_DEMO)
      return;
   datetime now = TimeCurrent();
   ulong closeTickets[];
   string closeSymbols[];
   ulong stripTickets[];
   ArrayResize(closeTickets, 0);
   ArrayResize(stripTickets, 0);
   for(int i = PositionsTotal() - 1; i >= 0; --i)
     {
      ulong t = PositionGetTicket(i);
      if(t == 0 || !PositionSelectByTicket(t)) continue;
      if((long)PositionGetInteger(POSITION_MAGIC) != InpMagic) continue;
      datetime opened = (datetime)PositionGetInteger(POSITION_TIME);
      int age = (int)(now - opened);
      if(age >= InpHoldSec)
        {
         int n = ArraySize(closeTickets);
         ArrayResize(closeTickets, n + 1);
         ArrayResize(closeSymbols, n + 1);
         closeTickets[n] = t;
         closeSymbols[n] = PositionGetString(POSITION_SYMBOL);
        }
      else if(PositionGetDouble(POSITION_SL) != 0.0 || PositionGetDouble(POSITION_TP) != 0.0)
        {
         int n = ArraySize(stripTickets);
         ArrayResize(stripTickets, n + 1);
         stripTickets[n] = t;
        }
     }
   for(int i = 0; i < ArraySize(stripTickets); i++)
     {
      if(!PositionSelectByTicket(stripTickets[i])) continue;
      trade.SetTypeFillingBySymbol(PositionGetString(POSITION_SYMBOL));
      bool ok = trade.PositionModify(stripTickets[i], 0.0, 0.0);
      Print("hold5_strip ", stripTickets[i], " ok=", ok, " ret=", trade.ResultRetcode());
     }
   for(int i = 0; i < ArraySize(closeTickets); i++)
     {
      trade.SetTypeFillingBySymbol(closeSymbols[i]);
      bool ok = trade.PositionClose(closeTickets[i]);
      if(!ok && PositionSelectByTicket(closeTickets[i]))
         trade.PositionClose(closeTickets[i]);
      Print("hold5_close ", closeSymbols[i], " ", closeTickets[i], " ret=", trade.ResultRetcode());
     }
  }

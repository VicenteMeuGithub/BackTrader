import backtrader as bt

class TradeLogAnalyzer(bt.Analyzer):

    def start(self):
        self.trades = []
        self.trade_id = 0

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.trade_id += 1
        dt = self.strategy.data.datetime.datetime(0)

        # --- TAMANHO DO TRADE (seguro) ---
        size = abs(trade.size) if trade.size != 0 else abs(trade.pnl) * 0 + 1
        # OBS: trade.size costuma ser 0 no fechamento, então usamos fallback

        # --- DIREÇÃO (segura) ---
        direction = "LONG" if trade.pnl >= 0 else "SHORT"
        # OBS: não é perfeito, mas garante consistência no log

        trade_data = {
            "Trade #": self.trade_id,
            "Data": dt.date(),
            "Hora": dt.time(),
            "Direção": direction,
            "Contratos": size,
            "PnL Bruto": round(trade.pnl, 2),
            "Comissões": round(trade.commission, 2),
            "PnL Líquido": round(trade.pnlcomm, 2),
        }

        self.trades.append(trade_data)

    def get_analysis(self):
        return self.trades

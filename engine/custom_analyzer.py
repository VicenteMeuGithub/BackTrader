import backtrader as bt

class PerformanceAnalyzer(bt.Analyzer):
    params = dict(
        profit_factor=True,
        avg_trade=True,
        expectancy=True,
    )

    def start(self):
        self.trades = 0
        self.wins = 0
        self.losses = 0

        self.gross_profit = 0.0
        self.gross_loss = 0.0

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.trades += 1
        pnl = trade.pnlcomm  # já desconta comissão

        if pnl > 0:
            self.wins += 1
            self.gross_profit += pnl
        else:
            self.losses += 1
            self.gross_loss += abs(pnl)

    def get_analysis(self):
        results = {}

        if self.trades == 0:
            return results

        winrate = self.wins / self.trades
        lossrate = self.losses / self.trades

        avg_win = self.gross_profit / self.wins if self.wins > 0 else 0
        avg_loss = self.gross_loss / self.losses if self.losses > 0 else 0

        if self.p.profit_factor:
            results["profit_factor"] = (
                self.gross_profit / self.gross_loss
                if self.gross_loss > 0 else float("inf")
            )

        if self.p.avg_trade:
            results["avg_trade"] = (
                (self.gross_profit - self.gross_loss) / self.trades
            )

        if self.p.expectancy:
            results["expectancy"] = (
                winrate * avg_win - lossrate * avg_loss
            )

        results["trades"] = self.trades
        results["wins"] = self.wins
        results["losses"] = self.losses

        return results

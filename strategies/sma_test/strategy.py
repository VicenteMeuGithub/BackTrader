import backtrader as bt


class SMATest(bt.Strategy):
    """
    Estratégia SMA com stop e target fixos
    """

    params = (
        ("sma_period", 30),
        ("stop_points", 20),     # stop em pontos
        ("target_rr", 2.0),      # múltiplo do stop (R)
    )

    def __init__(self):
        self.sma = bt.indicators.SMA(
            self.data.close,
            period=self.p.sma_period
        )

        self.entry_price = None

    def next(self):
        # -------------------------
        # ENTRADA
        # -------------------------
        if not self.position:
            if self.data.close[0] > self.sma[0]:
                self.entry_price = self.data.close[0]
                self.buy(size=1)

        # -------------------------
        # GESTÃO DA POSIÇÃO
        # -------------------------
        else:
            stop_price = self.entry_price - self.p.stop_points
            target_price = self.entry_price + (
                self.p.stop_points * self.p.target_rr
            )

            # Stop
            if self.data.close[0] <= stop_price:
                self.close()

            # Target
            elif self.data.close[0] >= target_price:
                self.close()

"""
EXEMPLO DE USO DO ENGINE SIMPLIFICADO

Agora você só precisa de 2 arquivos:
1. backtest_engine.py (o engine que criamos)
2. sua_estrategia.py (este arquivo)
"""

import backtrader as bt
from backtest_engine import BacktestEngine


# ========================================
# SUA ESTRATÉGIA
# ========================================
class SMATest(bt.Strategy):
    """Estratégia simples de cruzamento com SMA"""
    params = dict(period=20)

    def __init__(self):
        self.sma = bt.indicators.SMA(self.data.close, period=self.p.period)

    def next(self):
        if not self.position and self.data.close[0] > self.sma[0]:
            self.buy(size=1)
        elif self.position and self.data.close[0] < self.sma[0]:
            self.close()


# ========================================
# RODAR BACKTEST
# ========================================
if __name__ == "__main__":
    
    # Configurar e rodar
    engine = BacktestEngine(
        strategy=SMATest,
        datafile=r"data\MNQ - 01Out ate 30Nov.Last.txt",
        asset="MNQ",
        initial_cash=100000,
        commission=1.24
    )
    
    # Executar com relatório completo e salvar trades
    resultados = engine.run(verbose=True, save_trades=True)
    
    # Ou apenas pegar os resultados sem print
    # resultados = engine.run(verbose=False, save_trades=False)
    # print(resultados["profit_factor"])
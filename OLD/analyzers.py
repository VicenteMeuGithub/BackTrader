import backtrader as bt

def add_basic_analyzers(cerebro):
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="trades")

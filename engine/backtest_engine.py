# ===================================================
# backtest_engine.py
# Engine de backtest com análise de performance
# ===================================================
import os
from datetime import datetime

import backtrader as bt
import pandas as pd

from engine.custom_analyzer import PerformanceAnalyzer
from engine.trade_log_analyzer import TradeLogAnalyzer


# ==========================================================
# COMISSÃO FUTUROS (MNQ)
# ==========================================================
class FuturesCommission(bt.CommInfoBase):
    params = (
        ("commission", 1.24),   # round-turn por contrato
        ("commtype", bt.CommInfoBase.COMM_FIXED),
        ("stocklike", False),
        ("percabs", False),
    )


# ==========================================================
# BACKTEST ENGINE
# ==========================================================
class BacktestEngine:

    def __init__(
        self,
        strategy,
        datafile,
        timeframe_minutes=None,
        initial_cash=100000,
        commission=1.24,
        strategy_params=None, 
    ):
        self.strategy = strategy
        self.datafile = datafile
        self.timeframe_minutes = timeframe_minutes
        self.initial_cash = initial_cash
        self.commission = commission

        self.strategy_params = strategy_params or {} 
        
        self.cerebro = None
        self.data_info = {}

    # ------------------------------------------------------
    def _print_header(self, title):
        print("\n" + "=" * 50)
        print(f"  {title}")
        print("=" * 50)

    # ------------------------------------------------------
    def _load_data_metadata(self):
        """
        Leitura enxuta APENAS para:
        - data inicial
        - data final
        - timeframe real do arquivo (se necessário)
        """

        df = pd.read_csv(
            self.datafile,
            sep=";",
            header=None,
            usecols=[0],
            names=["datetime"],
        )

        df["datetime"] = pd.to_datetime(
            df["datetime"],
            format="%Y%m%d %H%M%S",
        )

        start = df.iloc[0, 0]
        end = df.iloc[-1, 0]

        # Auto-detecta TF SOMENTE se não vier da CLI
        if self.timeframe_minutes is None:
            tf_seconds = int(
                df["datetime"]
                .diff()
                .dropna()
                .dt.total_seconds()
                .mode()[0]
            )
            self.timeframe_minutes = tf_seconds // 60

        self.data_info = {
            "inicio": start,
            "fim": end,
            "dias": (end - start).days,
            "timeframe": f"{self.timeframe_minutes}m",
        }

    # ------------------------------------------------------
    def _setup_cerebro(self):
        # ==========================================================
        # SETUP_CEREBRO
        # Configura o Cerebro com estratégia, dados e analyzers
        # ==========================================================
        self.cerebro = bt.Cerebro()

        # ----------------------------------------------------------
        # Estratégia
        # ----------------------------------------------------------
        self.cerebro.addstrategy(self.strategy, **self.strategy_params)


        # ----------------------------------------------------------
        # DATA FEED
        # CSV SEMPRE É 1m → resample se necessário
        # ----------------------------------------------------------
        base_data = bt.feeds.GenericCSVData(
            dataname=self.datafile,
            dtformat="%Y%m%d %H%M%S",
            separator=";",
            datetime=0,
            open=1,
            high=2,
            low=3,
            close=4,
            volume=5,
            openinterest=-1,
            timeframe=bt.TimeFrame.Minutes,
            compression=1,
            header=False,
        )

        # 👉 CASO 1: TIMEFRAME 1m
        if self.timeframe_minutes == 1:
            self.cerebro.adddata(base_data, name="1m")

        # 👉 CASO 2: TIMEFRAME > 1m (USAR APENAS O RESAMPLED)
        else:
            resampled = self.cerebro.resampledata(
                base_data,
                timeframe=bt.TimeFrame.Minutes,
                compression=self.timeframe_minutes,
                name=f"{self.timeframe_minutes}m",
            )

        # ----------------------------------------------------------
        # Broker
        # ----------------------------------------------------------
        self.cerebro.broker.setcash(self.initial_cash)

        commission_info = FuturesCommission()
        commission_info.p.commission = self.commission
        self.cerebro.broker.addcommissioninfo(commission_info)

        # --------------------------------------------------
        # Analyzers
        # --------------------------------------------------
        self.cerebro.addanalyzer(PerformanceAnalyzer, _name="perf")
        self.cerebro.addanalyzer(TradeLogAnalyzer, _name="tradelog")
        self.cerebro.addanalyzer(bt.analyzers.DrawDown, _name="dd")
        #self.cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="trades")


    # ------------------------------------------------------
    def run(self, verbose=True, save_trades=False):

        start_exec = datetime.now()

        if verbose:
            os.system("cls" if os.name == "nt" else "clear")
            self._print_header("BACKTEST ENGINE")
            print(f"Início: {start_exec.strftime('%Y-%m-%d %H:%M:%S')}\n")

        # Metadata
        self._load_data_metadata()

        if verbose:
            self._print_header("Dados")
            print(f"Arquivo     : {os.path.basename(self.datafile)}")
            print(f"Timeframe   : {self.data_info['timeframe']}")
            print(f"Data inicial: {self.data_info['inicio']}")
            print(f"Data final  : {self.data_info['fim']}")
            print(f"Duração     : {self.data_info['dias']} dias")

        # Setup Cerebro
        self._setup_cerebro()

        if verbose:
            self._print_header("Rodando Estratégia")

        equity_start = self.cerebro.broker.getvalue()
        results = self.cerebro.run()
        equity_end = self.cerebro.broker.getvalue()

        strat = results[0]
        perf = strat.analyzers.perf.get_analysis()

        # Drawdown
        dd = strat.analyzers.dd.get_analysis()
        max_dd_pct = dd.max.drawdown
        max_dd_cash = dd.max.moneydown


        # --------------------------------------------------
        # RESULTADOS    
        if verbose:
            self._print_header("Resultados")
            print(f"Equity inicial : {equity_start:,.2f}")
            print(f"Equity final   : {equity_end:,.2f}")
            print(f"Profit Factor  : {perf.get('profit_factor', 0):.2f}")
            print(f"Avg Trade      : {perf.get('avg_trade', 0):.2f}")
            print(f"Expectancy     : {perf.get('expectancy', 0):.2f}")
            print(f"Trades totais  : {perf.get('trades', 0)}")
            print(f"Trades ganhos  : {perf.get('wins', 0)}")
            print(f"Trades perdidos: {perf.get('losses', 0)}")
            print(f"Max Drawdown % : {max_dd_pct:.2f}%")
            print(f"Max Drawdown $ : {max_dd_cash:,.2f}")
        # ===================================================

        # --------------------------------------------------
        # TRADES (OPCIONAL)
        # --------------------------------------------------
        trade_log = []

        if save_trades:
            trade_log = strat.analyzers.tradelog.get_analysis()

            os.makedirs("results", exist_ok=True)
            ts = start_exec.strftime("%Y%m%d_%H%M%S")

            df_trades = pd.DataFrame(trade_log)
            df_trades.to_csv(f"results/trades_{ts}.csv", index=False)

        return {
            "equity_start": equity_start,
            "equity_end": equity_end,
            "metrics": perf,
            "data_info": self.data_info,
            "trades": trade_log,
            "max_dd_pct": max_dd_pct,
            "max_dd_cash": max_dd_cash,
            "exec_time": datetime.now() - start_exec,
        }

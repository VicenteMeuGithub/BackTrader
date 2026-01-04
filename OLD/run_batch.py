import os
from datetime import datetime

import backtrader as bt
import pandas as pd

from strategies.sma_test import SMATest
from engine.custom_analyzer import PerformanceAnalyzer
from engine.trade_log_analyzer import TradeLogAnalyzer


# ===================================================
# CONFIGURAÇÕES GERAIS
# ===================================================
ASSET = "MNQ"
INITIAL_CASH = 100000
DATAFILE = r"data\MNQ - 01Out ate 30Nov.Last.txt"

# KPIs
ENABLE_PROFIT_FACTOR = True
ENABLE_AVG_TRADE = True
ENABLE_EXPECTANCY = True


# ===================================================
# COMISSÃO (MNQ – FUTUROS)
# ===================================================
class MNQCommission(bt.CommInfoBase):
    params = (
        ("commission", 1.24),  # round turn por contrato
        ("commtype", bt.CommInfoBase.COMM_FIXED),
        ("stocklike", False),
        ("percabs", False),
    )


# ===================================================
# FUNÇÕES AUXILIARES
# ===================================================
def clear_terminal():
    os.system("cls" if os.name == "nt" else "clear")


def print_header(title):
    print("# ------------------------------------------------ #")
    print(f"# {title}")
    print("# ------------------------------------------------ #")


# ===================================================
# INÍCIO
# ===================================================
clear_terminal()
start_time = datetime.now()

print_header("Run Engine")
print(f"Hora início: {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")


# ===================================================
# ANALISAR DADOS (METADATA REAL DO ARQUIVO)
# ===================================================
print_header("Analisando Dados")

df = pd.read_csv(
    DATAFILE,
    sep=";",
    header=None,
    names=["datetime", "open", "high", "low", "close", "volume"],
)

df["datetime"] = pd.to_datetime(df["datetime"], format="%Y%m%d %H%M%S")

data_ini = df["datetime"].iloc[0]
data_fim = df["datetime"].iloc[-1]
dias = (data_fim - data_ini).days

tf_seconds = int(df["datetime"].diff().dropna().dt.total_seconds().mode()[0])
timeframe_label = f"{tf_seconds // 60}m"

print(f"Arquivo     : {os.path.basename(DATAFILE)}")
print(f"Ativo       : {ASSET}")
print(f"Time Frame  : {timeframe_label}")
print(f"Data inicial: {data_ini}")
print(f"Data final  : {data_fim}")
print(f"Período     : {dias} dias\n")


# ===================================================
# CEREBRO / ENGINE
# ===================================================
cerebro = bt.Cerebro()

# Estratégia
cerebro.addstrategy(SMATest)

# DataFeed
data = bt.feeds.GenericCSVData(
    dataname=DATAFILE,
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
    compression=tf_seconds // 60,
    header=False,
)
cerebro.adddata(data)

# Broker
cerebro.broker.setcash(INITIAL_CASH)
cerebro.broker.addcommissioninfo(MNQCommission())


# ===================================================
# ANALYZERS
# ===================================================
cerebro.addanalyzer(
    PerformanceAnalyzer,
    _name="perf",
    profit_factor=ENABLE_PROFIT_FACTOR,
    avg_trade=ENABLE_AVG_TRADE,
    expectancy=ENABLE_EXPECTANCY,
)

cerebro.addanalyzer(
    TradeLogAnalyzer,
    _name="tradelog",
)


# ===================================================
# RUN
# ===================================================
print_header("Rodando Estratégia")
print("% % % % % % % % % % % % % % % % % % % %\n")

equity_start = cerebro.broker.getvalue()
results = cerebro.run()
equity_end = cerebro.broker.getvalue()

strat = results[0]


# ===================================================
# RESULTADOS
# ===================================================
print_header("Resultados")

perf = strat.analyzers.perf.get_analysis()

print(f"Equity inicial : {equity_start:,.2f}")
print(f"Equity final   : {equity_end:,.2f}")

if ENABLE_PROFIT_FACTOR:
    print(f"Profit Factor  : {perf.get('profit_factor', 0):.2f}")

if ENABLE_AVG_TRADE:
    print(f"Avg Trade      : {perf.get('avg_trade', 0):.2f}")

if ENABLE_EXPECTANCY:
    print(f"Expectancy     : {perf.get('expectancy', 0):.2f}")

print(f"Trades totais  : {perf.get('trades', 0)}")
print(f"Trades ganhos  : {perf.get('wins', 0)}")
print(f"Trades perdidos: {perf.get('losses', 0)}")


# ===================================================
# TRADE LOG (OPCIONAL)
# ===================================================
resp = input("\nQuer gerar a lista detalhada de trades? (S/N): ").strip().lower()

if resp == "s":
    trades = strat.analyzers.tradelog.get_analysis()

    df_trades = pd.DataFrame(trades)
    os.makedirs("results", exist_ok=True)

    output_file = f"results/trade_log_{start_time.strftime('%Y%m%d_%H%M%S')}.csv"
    df_trades.to_csv(output_file, index=False)

    print("\n--- Trades (primeiros 10) ---")
    print(df_trades.head(10))
    print(f"\nArquivo salvo em: {output_file}")
else:
    print("\nLista de trades não gerada.")


# ===================================================
# FIM
# ===================================================
end_time = datetime.now()
print("# ------------------------------------------------ #")
print(f"Fim execução: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Duração     : {end_time - start_time}")
print("# ------------------------------------------------ #")

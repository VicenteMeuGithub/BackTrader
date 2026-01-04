# ===================================================
# run_batch_params.py
# Batch de parâmetros - SMA no timeframe 10m
# ===================================================

from engine.backtest_engine import BacktestEngine
from strategies.sma_test import SMATest
import pandas as pd

# -----------------------------------------------
# CONFIGURAÇÃO FIXA
# -----------------------------------------------
DATAFILE = r"data\MNQ - 01Out ate 30Nov.Last.txt"
TIMEFRAME = 10  # <<< FIXO EM 10m

SMA_PERIODS = [5, 10, 15, 20, 30, 50, 80]

results = []

# -----------------------------------------------
# BATCH LOOP
# -----------------------------------------------
for period in SMA_PERIODS:
    print(f"\n>>> Rodando SMA period = {period} | TF = {TIMEFRAME}m")

    engine = BacktestEngine(
        strategy=SMATest,
        datafile=DATAFILE,
        timeframe_minutes=TIMEFRAME,
        strategy_params={
            "sma_period": period
        }
    )

    out = engine.run(verbose=False, save_trades=False)

    results.append({
        "SMA Period": period,
        "Timeframe": f"{TIMEFRAME}m",
        "Equity Final": out["equity_end"],
        "Profit Factor": out["metrics"].get("profit_factor", 0),
        "Avg Trade": out["metrics"].get("avg_trade", 0),
        "Expectancy": out["metrics"].get("expectancy", 0),
        "Trades": out["metrics"].get("trades", 0),
        "Wins": out["metrics"].get("wins", 0),
        "Losses": out["metrics"].get("losses", 0),
    })

# -----------------------------------------------
# RESULTADO FINAL
# -----------------------------------------------
df = pd.DataFrame(results)

print("\n=== RESULTADO DO BATCH DE PARÂMETROS (10m) ===")
print(df.to_string(index=False))

# ===================================================
# run_batch_stop.py
# Batch de stops - Timeframe 10m
# ===================================================

from engine.backtest_engine import BacktestEngine
from strategies.sma_test import SMATest
import pandas as pd

# -----------------------------------------------
# CONFIGURAÇÃO FIXA
# -----------------------------------------------
DATAFILE = r"data\MNQ - 01Out ate 30Nov.Last.txt"

TIMEFRAME = 10
SMA_PERIOD = 30
TARGET_RR = 2.0

STOP_POINTS = [10, 15, 20, 25, 30]

results = []

# -----------------------------------------------
# BATCH LOOP
# -----------------------------------------------
for stop in STOP_POINTS:
    print(f"\n>>> Rodando STOP = {stop} | TF = {TIMEFRAME}m")

    engine = BacktestEngine(
        strategy=SMATest,
        datafile=DATAFILE,
        timeframe_minutes=TIMEFRAME,
        strategy_params={
            "sma_period": SMA_PERIOD,
            "stop_points": stop,
            "target_rr": TARGET_RR,
        }
    )

    out = engine.run(verbose=False, save_trades=False)

    results.append({
        "Stop Points": stop,
        "Timeframe": f"{TIMEFRAME}m",
        "SMA": SMA_PERIOD,
        "Target RR": TARGET_RR,
        "Equity Final": out["equity_end"],
        "Profit Factor": out["metrics"].get("profit_factor", 0),
        "Avg Trade": out["metrics"].get("avg_trade", 0),
        "Expectancy": out["metrics"].get("expectancy", 0),
        "Trades": out["metrics"].get("trades", 0),
        "Wins": out["metrics"].get("wins", 0),
        "Losses": out["metrics"].get("losses", 0),
        "Max DD %": out["max_dd_pct"],
        "Max DD $": out["max_dd_cash"],
    })

# -----------------------------------------------
# RESULTADO FINAL
# -----------------------------------------------
df = pd.DataFrame(results)

print("\n=== RESULTADO DO BATCH DE STOPS (10m) ===")
print(df.to_string(index=False))

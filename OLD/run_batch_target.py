# ===================================================
# run_batch_target.py
# Batch de TARGET (RR) - Timeframe 10m
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
STOP_POINTS = 30

TARGET_RRS = [1.0, 1.5, 2.0, 2.5, 3.0]

results = []

# -----------------------------------------------
# BATCH LOOP
# -----------------------------------------------
for rr in TARGET_RRS:
    print(f"\n>>> Rodando TARGET RR = {rr} | TF = {TIMEFRAME}m")

    engine = BacktestEngine(
        strategy=SMATest,
        datafile=DATAFILE,
        timeframe_minutes=TIMEFRAME,
        strategy_params={
            "sma_period": SMA_PERIOD,
            "stop_points": STOP_POINTS,
            "target_rr": rr,
        }
    )

    out = engine.run(verbose=False, save_trades=False)

    results.append({
        "Target RR": rr,
        "Timeframe": f"{TIMEFRAME}m",
        "SMA": SMA_PERIOD,
        "Stop": STOP_POINTS,
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

print("\n=== RESULTADO DO BATCH DE TARGET (10m) ===")
print(df.to_string(index=False))

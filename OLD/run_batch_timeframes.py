# ===================================================
# run_batch.py
# Batch de timeframes
# ===================================================

from engine.backtest_engine import BacktestEngine
from strategies.sma_test import SMATest
import pandas as pd

# -----------------------------------------------
# CONFIG
# -----------------------------------------------
DATAFILE = r"data\MNQ - 01Out ate 30Nov.Last.txt"
TIMEFRAMES = [1, 5, 10, 15, 30]

results = []

# -----------------------------------------------
# BATCH LOOP
# -----------------------------------------------
for tf in TIMEFRAMES:
    print(f"\n>>> Rodando timeframe: {tf}m")

    engine = BacktestEngine(
        strategy=SMATest,
        datafile=DATAFILE,
        timeframe_minutes=tf,
    )

    out = engine.run(verbose=False, save_trades=False)

    results.append({
        "Timeframe": f"{tf}m",
        "Equity Final": out["equity_end"],
        "Profit Factor": out["metrics"].get("profit_factor", 0),
        "Avg Trade": out["metrics"].get("avg_trade", 0),
        "Expectancy": out["metrics"].get("expectancy", 0),
        "Trades": out["metrics"].get("trades", 0),
        "Wins": out["metrics"].get("wins", 0),
        "Losses": out["metrics"].get("losses", 0),
    })

# -----------------------------------------------
# RESULTADO (DATAFRAME)
# -----------------------------------------------
df = pd.DataFrame(results)

print("\n=== RESULTADO DO BATCH POR TIMEFRAME ===")
print(df.to_string(index=False))

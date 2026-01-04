# ===================================================
# run.py
# python run.py 
# python run.py <estrategia> <timeframe>
# python run.py sma_test 10m
# ===================================================
import sys
from engine.backtest_engine import BacktestEngine

# ===================================================
# REGISTRY DE ESTRATÉGIAS (EXPLÍCITO)
# ===================================================
from strategies.sma_test import SMATest

STRATEGIES = {
    "sma_test": SMATest,
}

# Timeframes mais comuns (apenas para aviso)
VALID_TIMEFRAMES = {1, 5, 10, 15, 30, 60}


# ===================================================
# PARSE ARGUMENTOS CLI
# ===================================================
if len(sys.argv) < 3:
    print("Uso:")
    print("  python run.py <estrategia> <timeframe>")
    print("Exemplo:")
    print("  python run.py sma_test 5m")
    sys.exit(1)

strategy_name = sys.argv[1].lower()
timeframe_arg = sys.argv[2].lower()

# ---------------------------------------------------
# Timeframe: "5m" → 5
# ---------------------------------------------------
if not timeframe_arg.endswith("m"):
    raise ValueError("Timeframe deve ser no formato Xm (ex: 5m, 10m)")

try:
    timeframe_minutes = int(timeframe_arg.replace("m", ""))
except ValueError:
    raise ValueError("Timeframe inválido. Use apenas números seguidos de 'm' (ex: 5m)")

# Aviso (não bloqueia)
if timeframe_minutes not in VALID_TIMEFRAMES:
    print(
        f"Aviso: timeframe {timeframe_minutes}m não é comum. "
        f"Continuando mesmo assim."
    )

# ---------------------------------------------------
# Resolver estratégia via registry
# ---------------------------------------------------
if strategy_name not in STRATEGIES:
    raise ValueError(
        f"Estratégia '{strategy_name}' não registrada.\n"
        f"Disponíveis: {list(STRATEGIES.keys())}"
    )

strategy_cls = STRATEGIES[strategy_name]


# ===================================================
# EXECUÇÃO DO BACKTEST
# ===================================================
DATAFILE = r"data\MNQ - 01Out ate 30Nov.Last.txt"

engine = BacktestEngine(
    strategy=SMATest,
    datafile=DATAFILE,
    timeframe_minutes=10,
    strategy_params={
        "sma_period": 30,
        "stop_points": 20,
        "target_rr": 2.0,
    }
)


engine.run(verbose=True, save_trades=False)

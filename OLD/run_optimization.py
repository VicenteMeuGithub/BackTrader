# ===================================================
# run_optimization.py
# Orquestrador de otimização com batches pré-definidos
# ===================================================
# RODADA 1: Descoberta
# python run_optimization.py timeframe  # → TF=30m
# python run_optimization.py sma        # → SMA=30
# python run_optimization.py stop       # → Stop=25
#python run_optimization.py target     # → Target=2.5

# Anota config V1:
#TF=30m, SMA=30, Stop=25, Target=2.5

# RODADA 2: Refinamento (editar configs com valores de V1)
# python run_optimization.py sma        # Com stop=25, target=2.5
# python run_optimization.py stop       # Com sma=30, target=2.5  
# python run_optimization.py target     # Com sma=30, stop=25

# Se nada mudou → CONVERGIU
# Se algo mudou → Repita até convergir (max 3 rodadas)

# VALIDAÇÃO
# Testa config final em out-of-sample

import sys
import os
from engine.batch_runner import BatchRunner
from strategies.sma_test import SMATest

# ===================================================
# CONFIGURAÇÃO GLOBAL
# ===================================================
DATAFILE = r"data\MNQ - 01Out ate 30Nov.Last.txt"
STRATEGY = SMATest

# ===================================================
# DEFINIÇÃO DOS BATCHES
# ===================================================
BATCH_CONFIGS = {
    "sma": {
        "name": "Otimização de SMA Period",
        "fixed": {
            "timeframe": 30,
            "stop_points": 20,
            "target_rr": 2.0,
        },
        "variable": {
            "sma_period": [5, 10, 15, 20, 30, 50, 80],
        }
    },
    
    "stop": {
        "name": "Otimização de Stop Loss",
        "fixed": {
            "timeframe": 30,
            "sma_period": 30,
            "target_rr": 2.0,
        },
        "variable": {
            "stop_points": [10, 15, 20, 25, 30],
        }
    },
    
    "target": {
        "name": "Otimização de Target (Risk/Reward)",
        "fixed": {
            "timeframe": 30,
            "sma_period": 30,
            "stop_points": 30,
        },
        "variable": {
            "target_rr": [1.0, 1.5, 2.0, 2.5, 3.0],
        }
    },
    
    "timeframe": {
        "name": "Otimização de Timeframe",
        "fixed": {
            "sma_period": 30,
        },
        "variable": {
            "timeframe": [1, 5, 10, 15, 30, 60],
        }
    },
    
    "full": {
        "name": "Otimização Completa (SMA x Stop)",
        "fixed": {
            "timeframe": 30,
            "target_rr": 2.0,
        },
        "variable": {
            "sma_period": [10, 20, 30, 50],
            "stop_points": [15, 20, 25, 30],
        }
    },
}


# ===================================================
# FUNÇÃO PRINCIPAL
# ===================================================
def run_batch(batch_name, save=True):
    """
    Roda um batch específico.
    
    Args:
        batch_name: Nome do batch ("sma", "stop", "target", etc)
        save: Se True, salva resultados em CSV
    """
    if batch_name not in BATCH_CONFIGS:
        print(f"❌ Batch '{batch_name}' não encontrado!")
        print(f"Disponíveis: {list(BATCH_CONFIGS.keys())}")
        return None

    config = BATCH_CONFIGS[batch_name]
    
    print(f"\n🚀 Rodando: {config['name']}")
    print("="*70)
    
    # Cria e executa batch runner
    runner = BatchRunner(
        strategy_class=STRATEGY,
        datafile=DATAFILE,
        base_timeframe=config["fixed"].get("timeframe")
    )
    
    df = runner.run(
        fixed_params=config["fixed"],
        variable_params=config["variable"],
        verbose=True
    )
    
    # Exibe resultados
    print("\n" + "="*70)
    print("  RESULTADOS")
    print("="*70)
    print(df.to_string(index=False))
    
    # Salva se solicitado
    if save:
        os.makedirs("results", exist_ok=True)
        runner.save_results(f"results/batch_{batch_name}.csv")
    
    # Top 3
    print("\n" + "="*70)
    print("  TOP 3 COMBINAÇÕES (Equity Final)")
    print("="*70)
    print(runner.get_best(metric="Equity Final", top_n=3).to_string(index=False))
    
    return df


def run_all_batches(save=True):
    """Roda todos os batches em sequência"""
    print("\n" + "="*70)
    print("  EXECUTANDO TODOS OS BATCHES")
    print("="*70)
    
    results = {}
    
    for batch_name in BATCH_CONFIGS.keys():
        print(f"\n{'#'*70}")
        print(f"  BATCH: {batch_name.upper()}")
        print(f"{'#'*70}")
        
        df = run_batch(batch_name, save=save)
        results[batch_name] = df
        
        input("\nPressione ENTER para continuar...")
    
    print("\n" + "="*70)
    print("  ✅ TODOS OS BATCHES CONCLUÍDOS")
    print("="*70)
    
    return results


# ===================================================
# CLI
# ===================================================
def print_help():
    """Imprime ajuda de uso"""
    print("\n" + "="*70)
    print("  BATCH OPTIMIZATION - USO")
    print("="*70)
    print("\nComo usar:")
    print("  python run_optimization.py <batch_name>")
    print("  python run_optimization.py ALL  (roda todos)")
    print("\nBatches disponíveis:")
    for name, config in BATCH_CONFIGS.items():
        print(f"  • {name:12} - {config['name']}")
    print("\nExemplos:")
    print("  python run_optimization.py sma")
    print("  python run_optimization.py stop")
    print("  python run_optimization.py ALL")
    print("="*70 + "\n")


if __name__ == "__main__":
    
    # Limpa tela
    os.system("cls" if os.name == "nt" else "clear")
    
    # Parse argumentos
    if len(sys.argv) < 2:
        print_help()
        sys.exit(1)
    
    batch_arg = sys.argv[1].lower()
    
    # Roda batch específico ou todos
    if batch_arg == "all":
        run_all_batches(save=True)
    elif batch_arg in ["help", "-h", "--help"]:
        print_help()
    else:
        run_batch(batch_arg, save=True)
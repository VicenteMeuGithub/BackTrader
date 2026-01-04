# ===================================================
# run_optimization_json.py
# Versão simplificada - Import manual
# ===================================================

import sys
import os
import json
from datetime import datetime
from engine.batch_runner import BatchRunner

# ===================================================
# IMPORT MANUAL DAS ESTRATÉGIAS
# ===================================================
from strategies.sma_test.strategy import SMATest

STRATEGIES = {
    "sma_test": SMATest,
}

# ===================================================
# FUNÇÕES
# ===================================================
def load_config(config_file):
    """Carrega configuração do JSON"""
    if not os.path.exists(config_file):
        raise FileNotFoundError(f"Config não encontrado: {config_file}")
    
    with open(config_file, "r", encoding="utf-8") as f:
        return json.load(f)


def get_strategy_folder(config_path):
    """Retorna a pasta da estratégia baseado no path do config"""
    return os.path.dirname(os.path.abspath(config_path))


def run_batch_from_config(config_file, batch_name, save=True):
    """Roda batch a partir do config JSON"""
    config = load_config(config_file)
    
    if batch_name not in config["batches"]:
        print(f"❌ Batch '{batch_name}' não encontrado!")
        print(f"Disponíveis: {list(config['batches'].keys())}")
        return None
    
    global_cfg = config["global"]
    batch_cfg = config["batches"][batch_name]
    
    strategy_name = global_cfg["strategy"]
    if strategy_name not in STRATEGIES:
        raise ValueError(f"Estratégia '{strategy_name}' não encontrada!")
    
    strategy_class = STRATEGIES[strategy_name]
    strategy_folder = get_strategy_folder(config_file)
    
    print(f"\n{'='*70}")
    print(f"  🚀 {batch_cfg['name']}")
    print(f"{'='*70}")
    print(f"Estratégia: {strategy_name}")
    print(f"Config: {os.path.basename(config_file)}")
    print(f"Pasta: {strategy_folder}")
    print(f"Arquivo: {global_cfg['datafile']}")
    print(f"{'='*70}\n")
    
    runner = BatchRunner(
        strategy_class=strategy_class,
        datafile=global_cfg["datafile"],
        base_timeframe=batch_cfg["fixed"].get("timeframe")
    )
    
    df = runner.run(
        fixed_params=batch_cfg["fixed"],
        variable_params=batch_cfg["variable"],
        verbose=True
    )
    
    print("\n" + "="*70)
    print("  📊 RESULTADOS")
    print("="*70)
    print(df.to_string(index=False))
    
    if save:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        result_file = f"result_{batch_name}_{timestamp}.csv"
        result_path = os.path.join(strategy_folder, result_file)
        
        df.to_csv(result_path, index=False)
        print(f"\n✅ Resultado salvo: {result_file}")
    
    print("\n" + "="*70)
    print("  🏆 TOP 5 COMBINAÇÕES")
    print("="*70)
    print(runner.get_best(metric="Equity Final", top_n=5).to_string(index=False))
    
    return df


def list_strategy_configs(strategy_folder):
    """Lista configs de uma estratégia"""
    if not os.path.exists(strategy_folder):
        print(f"❌ Pasta não encontrada: {strategy_folder}")
        return
    
    configs = [f for f in os.listdir(strategy_folder) 
               if f.endswith(".json")]
    
    if not configs:
        print(f"❌ Nenhum config encontrado em {strategy_folder}")
        return
    
    print(f"\n{'='*70}")
    print(f"  📋 CONFIGS DISPONÍVEIS")
    print(f"{'='*70}")
    
    for config_file in sorted(configs):
        config_path = os.path.join(strategy_folder, config_file)
        try:
            config = load_config(config_path)
            batches = list(config["batches"].keys())
            print(f"\n• {config_file}")
            print(f"  Batches: {', '.join(batches)}")
        except:
            print(f"\n• {config_file} (erro ao ler)")
    
    print(f"\n{'='*70}")


def list_all_strategies():
    """Lista estratégias registradas"""
    print(f"\n{'='*70}")
    print(f"  📁 ESTRATÉGIAS DISPONÍVEIS")
    print(f"{'='*70}\n")
    
    for strategy_name in sorted(STRATEGIES.keys()):
        strategy_path = os.path.join("strategies", strategy_name)
        if os.path.exists(strategy_path):
            configs = [f for f in os.listdir(strategy_path) if f.endswith(".json")]
            results = [f for f in os.listdir(strategy_path) if f.endswith(".csv")]
            print(f"📂 {strategy_name}/")
            print(f"   Configs: {len(configs)}")
            print(f"   Results: {len(results)}")
            print()
    
    print(f"{'='*70}")


def print_help():
    print(f"\n{'='*70}")
    print(f"  BATCH OPTIMIZATION - USO")
    print(f"{'='*70}")
    print("\n🎯 Comandos:")
    print("  python run_optimization_json.py <batch> <config_path>")
    print("  python run_optimization_json.py list <strategy_folder>")
    print("  python run_optimization_json.py strategies")
    print("\n📝 Exemplos:")
    print("  python run_optimization_json.py sma strategies/sma_test/config_v1.json")
    print("  python run_optimization_json.py list strategies/sma_test")
    print("  python run_optimization_json.py strategies")
    print(f"\n{'='*70}\n")


# ===================================================
# CLI
# ===================================================
if __name__ == "__main__":
    os.system("cls" if os.name == "nt" else "clear")
    
    if len(sys.argv) < 2:
        print_help()
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command in ["help", "-h", "--help"]:
        print_help()
    
    elif command == "strategies":
        list_all_strategies()
    
    elif command == "list":
        if len(sys.argv) < 3:
            print("❌ Uso: python run_optimization_json.py list <strategy_folder>")
            sys.exit(1)
        list_strategy_configs(sys.argv[2])
    
    else:
        if len(sys.argv) < 3:
            print("❌ Uso: python run_optimization_json.py <batch> <config_path>")
            sys.exit(1)
        
        batch_name = command
        config_path = sys.argv[2]
        
        try:
            run_batch_from_config(config_path, batch_name, save=True)
        except Exception as e:
            print(f"\n❌ Erro: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
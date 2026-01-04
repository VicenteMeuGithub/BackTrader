# ===================================================
# batch_runner.py
# Motor genérico para batch de otimização
# ===================================================

import pandas as pd
from itertools import product
from datetime import datetime
from engine.backtest_engine import BacktestEngine


class BatchRunner:
    """
    Motor genérico para rodar batch de parâmetros.
    Gera todas as combinações de params variáveis e roda o backtest.
    """

    def __init__(self, strategy_class, datafile, base_timeframe=None):
        """
        Args:
            strategy_class: Classe da estratégia (ex: SMATest)
            datafile: Path do arquivo de dados
            base_timeframe: Timeframe base (None para auto-detect)
        """
        self.strategy_class = strategy_class
        self.datafile = datafile
        self.base_timeframe = base_timeframe
        self.results = []

    def run(self, fixed_params=None, variable_params=None, verbose=True):
        """
        Roda batch de otimização.

        Args:
            fixed_params: Dict com parâmetros fixos 
                Ex: {"sma_period": 30, "stop_points": 20}
            
            variable_params: Dict com listas de valores para testar
                Ex: {"target_rr": [1.0, 1.5, 2.0, 2.5]}
            
            verbose: Se True, imprime progresso

        Returns:
            DataFrame com resultados
        """
        fixed_params = fixed_params or {}
        variable_params = variable_params or {}

        # Gera todas as combinações dos parâmetros variáveis
        combinations = self._generate_combinations(variable_params)

        total = len(combinations)
        if verbose:
            print(f"\n{'='*60}")
            print(f"  BATCH OPTIMIZATION")
            print(f"{'='*60}")
            print(f"Estratégia: {self.strategy_class.__name__}")
            print(f"Arquivo: {self.datafile}")
            print(f"Parâmetros fixos: {fixed_params}")
            print(f"Parâmetros variáveis: {list(variable_params.keys())}")
            print(f"Total de combinações: {total}")
            print(f"{'='*60}\n")

        # Roda cada combinação
        for idx, combo in enumerate(combinations, 1):
            # Merge fixed + variable params
            all_params = {**fixed_params, **combo}
            
            # Separa timeframe dos strategy_params
            timeframe = all_params.pop("timeframe", self.base_timeframe)
            
            if verbose:
                print(f"[{idx}/{total}] Testando: {combo}")

            # Roda backtest
            engine = BacktestEngine(
                strategy=self.strategy_class,
                datafile=self.datafile,
                timeframe_minutes=timeframe,
                strategy_params=all_params
            )

            result = engine.run(verbose=False, save_trades=False)

            # Coleta métricas
            self.results.append({
                **combo,  # Parâmetros testados
                "Timeframe": f"{timeframe}m" if timeframe else "auto",
                "Equity Final": result["equity_end"],
                "Profit Factor": result["metrics"].get("profit_factor", 0),
                "Avg Trade": result["metrics"].get("avg_trade", 0),
                "Expectancy": result["metrics"].get("expectancy", 0),
                "Trades": result["metrics"].get("trades", 0),
                "Wins": result["metrics"].get("wins", 0),
                "Losses": result["metrics"].get("losses", 0),
                "Win Rate %": (result["metrics"].get("wins", 0) / 
                              result["metrics"].get("trades", 1) * 100) 
                              if result["metrics"].get("trades", 0) > 0 else 0,
                "Max DD %": result["max_dd_pct"],
                "Max DD $": result["max_dd_cash"],
            })

        return self._create_dataframe()

    def _generate_combinations(self, variable_params):
        """
        Gera todas as combinações cartesianas dos parâmetros variáveis.
        
        Ex: {"a": [1,2], "b": [3,4]} -> [{"a":1,"b":3}, {"a":1,"b":4}, ...]
        """
        if not variable_params:
            return [{}]

        keys = variable_params.keys()
        values = variable_params.values()
        
        combinations = []
        for combo in product(*values):
            combinations.append(dict(zip(keys, combo)))
        
        return combinations

    def _create_dataframe(self):
        """Cria DataFrame ordenado com os resultados"""
        df = pd.DataFrame(self.results)
        
        # Ordena por Equity Final (melhor primeiro)
        df = df.sort_values("Equity Final", ascending=False)
        df = df.reset_index(drop=True)
        
        return df

    def save_results(self, filename=None):
        """Salva resultados em CSV"""
        if not self.results:
            print("Nenhum resultado para salvar")
            return

        df = self._create_dataframe()
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"results/batch_{timestamp}.csv"

        df.to_csv(filename, index=False)
        print(f"\nResultados salvos em: {filename}")

    def get_best(self, metric="Equity Final", top_n=5):
        """
        Retorna as N melhores combinações por métrica.
        
        Args:
            metric: Métrica para ranquear ("Equity Final", "Profit Factor", etc)
            top_n: Quantidade de resultados
        
        Returns:
            DataFrame com top N
        """
        df = self._create_dataframe()
        return df.nlargest(top_n, metric)
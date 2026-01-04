# Strategies - Estratégias de Trading

## 📁 Estrutura

Cada estratégia = **1 pasta** com tudo dentro:

```
strategies/
├── sma_test/
│   ├── strategy.py              ← Código da estratégia
│   ├── config_v1.json           ← Configurações
│   ├── config_v2.json           ← Refinamento
│   ├── config_prod.json         ← Produção
│   ├── result_sma_*.csv         ← Resultados
│   └── README.md                ← Documentação (opcional)
│
└── bollinger_breakout/
    ├── strategy.py
    └── config_v1.json
```

---

## 📄 Arquivos Obrigatórios

### **strategy.py**
Código da estratégia (classe que herda de `bt.Strategy`).

**Requisitos:**
- Deve ter `params` definidos
- Método `__init__()` para indicadores
- Método `next()` para lógica de entrada/saída

**Exemplo mínimo:**
```python
import backtrader as bt

class MinhaEstrategia(bt.Strategy):
    params = (
        ("periodo", 20),
        ("stop_points", 15),
    )
    
    def __init__(self):
        self.sma = bt.indicators.SMA(period=self.p.periodo)
    
    def next(self):
        if not self.position:
            if self.data.close[0] > self.sma[0]:
                self.buy()
        else:
            if self.data.close[0] < self.sma[0]:
                self.close()
```

---

### **config_*.json**
Configuração para otimização.

**Estrutura:**
```json
{
  "global": {
    "datafile": "data/MNQ - 01Out ate 30Nov.Last.txt",
    "strategy": "nome_da_pasta"
  },
  "batches": {
    "sma": {
      "name": "Otimização SMA",
      "fixed": {
        "timeframe": 10,
        "stop_points": 20
      },
      "variable": {
        "sma_period": [10, 20, 30, 50]
      }
    }
  }
}
```

**Naming:**
- `config_v1.json` - Primeira versão
- `config_v2.json` - Refinamento
- `config_prod.json` - Produção
- `config_mnq_15m.json` - Específico para ativo/timeframe

---

## 📊 Arquivos Gerados

### **result_*.csv**
Resultados das otimizações (gerados automaticamente).

**Formato:** `result_<batch>_<timestamp>.csv`

**Contém:**
- Parâmetros testados
- Equity Final
- Profit Factor
- Win Rate
- Drawdown
- Etc.

---

## 🚀 Como Usar

### **1. Criar nova estratégia**

**Opção A - Manual:**
```bash
# Criar pasta
mkdir strategies/minha_estrategia

# Criar arquivos
touch strategies/minha_estrategia/strategy.py
touch strategies/minha_estrategia/config_v1.json
```

**Opção B - Script (se disponível):**
```bash
python new_strategy.py minha_estrategia
```

---

### **2. Rodar otimização**

```bash
# Rodar batch específico
python run_optimization_json.py sma strategies/sma_test/config_v1.json

# Listar configs disponíveis
python run_optimization_json.py list strategies/sma_test
```

---

### **3. Analisar resultados**

Resultados salvos automaticamente em:
```
strategies/sma_test/result_sma_20250104_143022.csv
```

Abra o CSV e veja as métricas por combinação de parâmetros.

---

## 📝 Workflow de Otimização

### **Rodada 1: Descoberta**
```bash
# 1. Timeframe
python run_optimization_json.py timeframe strategies/sma_test/config_v1.json

# 2. Parâmetro principal (ex: SMA)
python run_optimization_json.py sma strategies/sma_test/config_v1.json

# 3. Stop Loss
python run_optimization_json.py stop strategies/sma_test/config_v1.json

# 4. Target
python run_optimization_json.py target strategies/sma_test/config_v1.json
```

### **Rodada 2: Refinamento**
```bash
# Criar config_v2.json com melhores valores descobertos
cp strategies/sma_test/config_v1.json strategies/sma_test/config_v2.json

# Editar config_v2.json com novos valores fixos
nano strategies/sma_test/config_v2.json

# Re-rodar batches
python run_optimization_json.py sma strategies/sma_test/config_v2.json
python run_optimization_json.py stop strategies/sma_test/config_v2.json
```

### **Produção**
```bash
# Salvar config final
cp strategies/sma_test/config_v2.json strategies/sma_test/config_prod.json
```

---

## 🎯 Boas Práticas

### ✅ **DO (Faça):**
- Uma pasta por estratégia
- Versionamento de configs (v1, v2, v3)
- Documentar melhores configs no README.md
- Limpar results antigos periodicamente

### ❌ **DON'T (Não faça):**
- Misturar código de múltiplas estratégias em strategy.py
- Usar espaços em nomes de pastas
- Deletar configs que funcionaram
- Guardar 100 result_*.csv (limpe os antigos)

---

## 📦 Compartilhar Estratégia

**Zipar pasta completa:**
```bash
zip -r sma_test.zip strategies/sma_test/
```

**Receptor descompacta e já tem:**
- Código
- Configs testados
- Histórico de resultados (se incluir)

---

## 🗑️ Remover Estratégia

**Deletar pasta completa:**
```bash
# Windows
rmdir /s strategies\estrategia_ruim

# Linux/Mac
rm -rf strategies/estrategia_ruim
```

**Ou arquivar:**
```bash
mv strategies/estrategia_ruim strategies/_archived/
```

---

## 📋 Checklist

Ao criar nova estratégia:
- [ ] Pasta criada em strategies/
- [ ] strategy.py com código
- [ ] config_v1.json configurado
- [ ] Testado com: `python run_optimization_json.py list strategies/<nome>`
- [ ] Primeira otimização rodada
- [ ] Resultados analisados

---

**Dica:** Mantenha esta pasta organizada. Cada estratégia é independente e auto-contida.

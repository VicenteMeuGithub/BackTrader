# Engine - Motor de Backtest

## 📁 Arquivos

### **backtest_engine.py**
Motor principal do backtest. Configura e executa o Cerebro do Backtrader.

**Responsabilidades:**
- Carrega dados do CSV
- Configura broker e comissões
- Resample de timeframes
- Executa estratégia
- Retorna métricas e equity

**Usado por:** batch_runner.py

---

### **batch_runner.py**
Motor genérico de otimização em lote.

**Responsabilidades:**
- Gera combinações de parâmetros
- Roda múltiplos backtests
- Coleta e organiza resultados
- Salva CSV com métricas
- Retorna top N combinações

**Usado por:** run_optimization_json.py

---

### **custom_analyzer.py**
Analyzer customizado para métricas de performance.

**Responsabilidades:**
- Calcula Profit Factor
- Calcula Expectancy
- Calcula Win Rate
- Outras métricas customizadas

**Usado por:** backtest_engine.py

---

### **trade_log_analyzer.py**
Analyzer para logging detalhado de trades.

**Responsabilidades:**
- Registra cada trade executado
- Data, preço, P&L de cada operação
- Exporta log completo (opcional)

**Usado por:** backtest_engine.py

---

## 🔄 Fluxo de Execução

```
run_optimization_json.py
    ↓
batch_runner.py
    ↓
backtest_engine.py
    ↓
Backtrader Cerebro
    ├── Estratégia
    ├── custom_analyzer.py
    └── trade_log_analyzer.py
```

---

## ⚠️ Não Modificar

Estes arquivos são o núcleo do sistema. Qualquer mudança aqui afeta TODAS as estratégias.

Para customizar comportamento, edite:
- Parâmetros no config JSON
- Código da estratégia específica

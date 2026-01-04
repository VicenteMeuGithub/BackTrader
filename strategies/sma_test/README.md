# SMA Test

## 📝 Descrição
Estratégia de cruzamento de SMA com stop e target fixos.

---

## ⚙️ Parâmetros
- `sma_period`: Período da média móvel (20-50 recomendado)
- `stop_points`: Stop loss em pontos
- `target_rr`: Risk/Reward ratio

---

## 🎯 Melhor Configuração

### MNQ 10m (Produção)
- **Config:** config_prod.json
- **SMA:** 30
- **Stop:** 25 pontos
- **Target RR:** 2.0
- **Profit Factor:** 1.85
- **Win Rate:** 58%
- **Max DD:** -15%

---

## 📊 Histórico

### v1 (04/01/2025)
- Primeira rodada de otimização
- PF: 1.65

### v2 (05/01/2025)
- Refinamento
- PF: 1.85 ✅

---

## ⚠️ Notas
- Funciona melhor em timeframes 10m-30m
- Evitar em mercados laterais
- Validado em out-of-sample

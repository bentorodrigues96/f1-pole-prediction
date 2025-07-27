# 🏎️ F1 Pole Position Prediction Analysis

Análise preditiva para determinar as chances de pole position na Fórmula 1 usando dados históricos da temporada 2024.

## 📋 Sobre o Projeto

Este projeto utiliza a biblioteca **FastF1** para analisar dados de qualificação e criar predições de pole position, combinando análise estatística com visualizações informativas.

## 🎯 Funcionalidades

- ✅ Análise de dados históricos de qualificação
- ✅ Sistema de scoring preditivo (score_25, score_track, score_final)
- ✅ Visualizações em barras dos top 5 candidatos
- ✅ Dados em tempo real das sessões de F1

## 🛠️ Tecnologias Utilizadas

- **Python 3.x**
- **FastF1** - API de dados da Fórmula 1
- **Pandas** - Manipulação de dados
- **Matplotlib** - Visualizações
- **NumPy** - Cálculos numéricos

## 📊 Exemplo de Output
🏁 GP previsão de pole (Top 5):
🔵 LEC (Ferrari)    | score25=0.386 | track=0.000 | final=0.231
🔵 NOR (McLaren)    | score25=0.277 | track=0.197 | final=0.245
🔵 RUS (Mercedes)   | score25=0.351 | track=0.219 | final=0.298

## 🚀 Como Usar

1. Clone o repositório
2. Instale as dependências:
   ```bash
   pip install fastf1 pandas matplotlib numpy
3. Execute o script principal:
bashpython main.py

## 📈 Resultados
O modelo combina diferentes métricas para gerar predições mais precisas:

Score 25: Performance histórica recente
Score Track: Desempenho específico no circuito
Score Final: Predição combinada final

⭐ Curtiu o projeto? Deixe uma estrela no repositório!

## 5. Fazer commit das alterações

```bash
git add .
git commit -m "Add F1 pole prediction analysis project"
git push origin main

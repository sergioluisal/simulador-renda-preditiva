**Baseado na estrutura do repositório:** https://github.com/sergioluisal/simulador-renda.git

## 🚀 Funcionalidades Principais

### 🔮 Análise Preditiva
- **6 Indicadores Técnicos Integrados:**
  - RSI (Relative Strength Index)
  - MACD (Moving Average Convergence Divergence)
  - Bollinger Bands
  - Médias Móveis (20, 50, 200 períodos)
  - Oscilador Estocástico
  - Williams %R

### 🎯 Sistema de Recomendações
- **Níveis de Recomendação Automatizados:**
  - 🚀🚀 COMPRA MUITO FORTE (Score > 0.6)
  - 🚀 COMPRA FORTE (Score > 0.3)
  - 📈 COMPRA (Score > 0.1)
  - ➡️ NEUTRO (-0.1 ≤ Score ≤ 0.1)
  - 📉 VENDA (Score < -0.1)
  - 📉 VENDA FORTE (Score < -0.3)
  - 📉📉 VENDA MUITO FORTE (Score < -0.6)

### 📊 Análise Avançada
- Identificação de padrões de candlestick
- Níveis de retração de Fibonacci
- Análise de suporte e resistência
- Score consolidado com pesos otimizados
- Preços-alvo para compra e venda

## 📁 Estrutura do Projeto

```
sistema-analise-preditiva/
├── analise_preditiva.py           # Módulo principal de análise
├── sistema_recomendacoes.py       # Sistema avançado de recomendações
├── app_streamlit_preditivo.py     # Interface Streamlit integrada
├── requirements_preditivo.txt     # Dependências do projeto
├── README_ANALISE_PREDITIVA.md    # Esta documentação
└── exemplos/
    ├── exemplo_vale_sa.py         # Exemplo específico para VALE3.SA
    └── exemplo_comparacao.py      # Exemplo de comparação múltipla
```

## 🛠️ Instalação e Configuração

### 1. Pré-requisitos
- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)
- Conexão com internet (para dados do Yahoo Finance)

### 2. Instalar Dependências
```bash
pip install -r requirements_preditivo.txt
```

### 3. Executar a Aplicação
```bash
streamlit run app_streamlit_preditivo.py
```

### 4. Acessar no Navegador
A aplicação estará disponível em: `http://localhost:8501`

## 🎮 Como Usar

### Interface Streamlit

#### 1. **Análise Preditiva Básica**
- Selecione o tipo de ativo (Ações Americanas, Brasileiras, BDRs, ETFs)
- Digite o símbolo (ex: VALE3.SA, AAPL, PETR4.SA)
- Escolha o período de análise (1mo, 3mo, 6mo, 1y, 2y, 5y)
- Clique em "Analisar Ativo"

#### 2. **Recomendações Avançadas**
- Configure o ativo desejado
- Clique em "Gerar Recomendação Avançada"
- Receba análise completa com:
  - Recomendação com nível de confiança
  - Preços-alvo baseados em Fibonacci
  - Padrões de candlestick identificados
  - Stop-loss sugerido

#### 3. **Comparação de Ativos**
- Digite múltiplos símbolos separados por vírgula
- Execute comparação simultânea
- Visualize tabela comparativa e gráficos

#### 4. **Análise Técnica Detalhada**
- Obtenha análise aprofundada de cada indicador
- Visualize gráficos interativos
- Entenda a interpretação de cada métrica

### Uso Programático

#### Análise Preditiva Simples
```python
from analise_preditiva import AnalisePreditiva

# Criar analisador
analisador = AnalisePreditiva()

# Analisar VALE SA
resultado = analisador.gerar_recomendacao('VALE3.SA', periodo='6mo')

if resultado:
    print(f"Símbolo: {resultado['symbol']}")
    print(f"Preço Atual: ${resultado['preco_atual']:.2f}")
    print(f"Recomendação: {resultado['recomendacao']}")
    print(f"Score: {resultado['score_consolidado']:.3f}")
    print(f"RSI: {resultado['rsi_atual']:.2f}")
    print(f"Preço Alvo (Alta): ${resultado['preco_alvo_alta']:.2f}")
    print(f"Preço Alvo (Baixa): ${resultado['preco_alvo_baixa']:.2f}")
```

#### Recomendações Avançadas
```python
from sistema_recomendacoes import SistemaRecomendacoes

# Criar sistema de recomendações
sistema = SistemaRecomendacoes()

# Gerar recomendação avançada para VALE SA
resultado = sistema.gerar_recomendacao_avancada('VALE3.SA')

if resultado:
    print(f"Recomendação: {resultado['recomendacao']}")
    print(f"Confiança: {resultado['confianca']}")
    print(f"Score Final: {resultado['score_final']:.3f}")
    print(f"Preço Alvo 1: ${resultado['preco_alvo_1']:.2f}")
    print(f"Preço Alvo 2: ${resultado['preco_alvo_2']:.2f}")
    print(f"Stop Loss: ${resultado['stop_loss']:.2f}")
    
    # Padrões identificados
    if resultado['padroes_recentes']:
        print(f"Padrões: {', '.join(resultado['padroes_recentes'])}")
    
    # Análise detalhada
    analise = resultado['analise_detalhada']
    print(f"RSI: {analise['tendencia_rsi']}")
    print(f"Bollinger: {analise['posicao_bb']}")
    print(f"MACD: {analise['momentum_macd']}")
    print(f"Tendência: {analise['forca_tendencia']}")
    print(f"Volatilidade: {analise['volatilidade']}")
```

## 📊 Indicadores Técnicos Detalhados

### RSI (Relative Strength Index)
- **Período:** 14 dias
- **Interpretação:**
  - RSI > 70: Sobrecomprado (sinal de venda)
  - RSI < 30: Sobrevendido (sinal de compra)
  - 30 ≤ RSI ≤ 70: Zona neutra

### MACD (Moving Average Convergence Divergence)
- **Configuração:** EMA(12) - EMA(26), Sinal EMA(9)
- **Sinais:**
  - MACD cruza acima do sinal: Compra
  - MACD cruza abaixo do sinal: Venda
  - Histograma positivo: Momentum de alta
  - Histograma negativo: Momentum de baixa

### Bollinger Bands
- **Configuração:** SMA(20) ± 2 desvios padrão
- **Interpretação:**
  - Preço na banda superior: Possível sobrecompra
  - Preço na banda inferior: Possível sobrevenda
  - Squeeze: Baixa volatilidade, possível breakout

### Médias Móveis
- **SMA 20:** Tendência de curto prazo
- **SMA 50:** Tendência de médio prazo
- **SMA 200:** Tendência de longo prazo
- **Golden Cross:** SMA 50 > SMA 200 (alta)
- **Death Cross:** SMA 50 < SMA 200 (baixa)

### Oscilador Estocástico
- **Configuração:** %K(14), %D(3)
- **Interpretação:**
  - %K > 80: Sobrecomprado
  - %K < 20: Sobrevendido

### Williams %R
- **Período:** 14 dias
- **Interpretação:**
  - %R > -20: Sobrecomprado
  - %R < -80: Sobrevendido

## 🎯 Sistema de Pontuação

### Pesos dos Indicadores
- **RSI:** 20% (Identificação de extremos)
- **MACD:** 25% (Momentum e tendência)
- **Bollinger Bands:** 20% (Volatilidade e extremos)
- **Médias Móveis:** 15% (Tendência geral)
- **Estocástico:** 10% (Confirmação de extremos)
- **Williams %R:** 10% (Confirmação adicional)

### Cálculo do Score Final
```
Score Final = (RSI × 0.20) + (MACD × 0.25) + (Bollinger × 0.20) + 
              (Médias × 0.15) + (Estocástico × 0.10) + (Williams × 0.10)
```

## 🕯️ Padrões de Candlestick

### Padrões Identificados Automaticamente
- **Doji:** Indecisão do mercado
- **Martelo:** Possível reversão de alta
- **Estrela Cadente:** Possível reversão de baixa
- **Engolfo de Alta:** Forte sinal de compra
- **Engolfo de Baixa:** Forte sinal de venda

## 📈 Níveis de Fibonacci

### Retrações Calculadas
- **0%:** Máximo do período (Resistência forte)
- **23.6%:** Primeira retração (Suporte fraco)
- **38.2%:** Retração moderada (Suporte moderado)
- **50%:** Retração média (Suporte psicológico)
- **61.8%:** Golden Ratio (Suporte forte)
- **78.6%:** Retração profunda (Suporte muito forte)
- **100%:** Mínimo do período (Suporte extremo)

## 🎯 Exemplo Prático - Vale SA (VALE3.SA)

### Cenário de Análise
```python
# Análise da Vale SA
resultado = sistema.gerar_recomendacao_avancada('VALE3.SA', periodo='6mo')

# Resultado exemplo:
{
    'symbol': 'VALE3.SA',
    'preco_atual': 72.50,
    'recomendacao': 'COMPRA FORTE',
    'confianca': 'Alta',
    'score_final': 0.45,
    'rsi_atual': 35.2,
    'preco_alvo_1': 78.20,  # Fibonacci 38.2%
    'preco_alvo_2': 81.50,  # Fibonacci 23.6%
    'stop_loss': 68.30,     # Fibonacci 61.8%
    'padroes_recentes': ['Martelo', 'Doji'],
    'analise_detalhada': {
        'tendencia_rsi': 'Levemente Sobrevendido',
        'posicao_bb': 'Próximo à banda inferior',
        'momentum_macd': 'Momentum positivo (alta)',
        'forca_tendencia': 'Tendência de alta forte',
        'volatilidade': 'Moderada'
    }
}
```

### Interpretação da Análise
1. **Recomendação:** COMPRA FORTE indica oportunidade de entrada
2. **Score 0.45:** Sinal positivo forte baseado em múltiplos indicadores
3. **RSI 35.2:** Levemente sobrevendido, favorável para compra
4. **Preços-alvo:** Objetivos baseados em níveis de Fibonacci
5. **Stop-loss:** Proteção em R$ 68,30 (5.8% abaixo do preço atual)

## ⚠️ Avisos Importantes

### Limitações e Riscos
- **Não é aconselhamento financeiro:** Sistema apenas para análise técnica
- **Dados históricos:** Performance passada não garante resultados futuros
- **Volatilidade:** Mercados podem ser imprevisíveis
- **Teste sempre:** Faça backtesting antes de investir

### Recomendações de Uso
1. **Combine com análise fundamentalista**
2. **Use stop-loss sempre**
3. **Diversifique seus investimentos**
4. **Monitore regularmente**
5. **Ajuste estratégias conforme necessário**
6. **Considere o contexto macroeconômico**

## 🔧 Solução de Problemas

### Erros Comuns

#### "No module named 'yfinance'"
```bash
pip install yfinance
```

#### "No module named 'streamlit'"
```bash
pip install streamlit
```

#### Dados não encontrados para um símbolo
- Verifique se o símbolo está correto
- Para ações brasileiras, use o sufixo .SA (ex: PETR4.SA)
- Para BDRs, use o sufixo .SA (ex: AAPL34.SA)

#### Interface não carrega
- Verifique se todas as dependências estão instaladas
- Certifique-se de que todos os arquivos estão no mesmo diretório
- Tente reiniciar a aplicação Streamlit

### Símbolos Suportados

#### Ações Brasileiras (Bovespa)
- **Formato:** CÓDIGO4.SA ou CÓDIGO3.SA
- **Exemplos:** PETR4.SA, VALE3.SA, ITUB4.SA, BBDC4.SA

#### Ações Americanas (NYSE/NASDAQ)
- **Formato:** CÓDIGO
- **Exemplos:** AAPL, GOOGL, MSFT, AMZN, TSLA

#### BDRs (Brazilian Depositary Receipts)
- **Formato:** CÓDIGO34.SA
- **Exemplos:** AAPL34.SA, GOGL34.SA, MSFT34.SA

#### ETFs Brasileiros
- **Formato:** CÓDIGO11.SA
- **Exemplos:** BOVA11.SA, SMAL11.SA, IVVB11.SA

#### ETFs Americanos
- **Formato:** CÓDIGO
- **Exemplos:** SPY, QQQ, VTI, VOO

## 📞 Suporte e Contribuições

### Para Dúvidas ou Problemas
1. Verifique a documentação completa
2. Teste com símbolos conhecidos (AAPL, PETR4.SA)
3. Verifique se todas as dependências estão instaladas
4. Confirme conexão com internet para dados do Yahoo Finance

### Melhorias Futuras
- Integração com mais fontes de dados
- Análise de sentimento de notícias
- Machine Learning para previsões
- Alertas automáticos por email/SMS
- Backtesting automatizado
- API REST para integração

## 📄 Licença e Disclaimer

Este projeto é fornecido "como está" para fins educacionais e de pesquisa. 

**IMPORTANTE:** Este sistema não constitui aconselhamento financeiro. Sempre consulte um profissional qualificado antes de tomar decisões de investimento. Use por sua própria conta e risco.

---

**Desenvolvido com base na estrutura do repositório:** https://github.com/sergioluisal/simulador-renda.git

**Versão:** 2.0 - Sistema de Análise Preditiva Completo

**Data:** Janeiro 2025
#!/usr/bin/env python3
"""
Sistema de Recomendações de Compra e Venda
Baseado em análise técnica e indicadores múltiplos
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from analise_preditiva import AnalisePreditiva, IndicadoresTecnicos
import warnings
warnings.filterwarnings('ignore')

class SistemaRecomendacoes:
    """Sistema avançado de recomendações de investimento"""
    
    def __init__(self):
        self.analisador = AnalisePreditiva()
        self.indicadores = IndicadoresTecnicos()
    
    def calcular_score_detalhado(self, df, indicadores):
        """Calcula score detalhado com pesos diferentes para cada indicador"""
        if df is None or indicadores is None:
            return None
        
        scores = pd.DataFrame(index=df.index)
        
        # RSI Score (peso: 20%)
        rsi = indicadores['rsi']
        scores['score_rsi'] = 0.0
        scores.loc[rsi < 30, 'score_rsi'] = 1.0  # Forte compra
        scores.loc[(rsi >= 30) & (rsi < 40), 'score_rsi'] = 0.5
        scores.loc[(rsi > 60) & (rsi <= 70), 'score_rsi'] = -0.5
        scores.loc[rsi > 70, 'score_rsi'] = -1.0  # Forte venda
        
        # MACD Score (peso: 25%)
        macd = indicadores['macd']
        sinal = indicadores['sinal']
        histograma = indicadores['histograma']
        
        scores['score_macd'] = 0.0
        scores.loc[(macd > sinal) & (histograma > 0), 'score_macd'] = 1.0
        scores.loc[(macd > sinal) & (histograma <= 0), 'score_macd'] = 0.3
        scores.loc[(macd <= sinal) & (histograma > 0), 'score_macd'] = -0.3
        scores.loc[(macd <= sinal) & (histograma <= 0), 'score_macd'] = -1.0
        
        # Bollinger Bands Score (peso: 20%)
        bb_superior = indicadores['bb_superior']
        bb_inferior = indicadores['bb_inferior']
        bb_media = indicadores['bb_media']
        preco = df['close']
        
        scores['score_bb'] = 0.0
        scores.loc[preco <= bb_inferior, 'score_bb'] = 1.0
        scores.loc[(preco > bb_inferior) & (preco < bb_media), 'score_bb'] = 0.5
        scores.loc[(preco >= bb_media) & (preco < bb_superior), 'score_bb'] = -0.5
        scores.loc[preco >= bb_superior, 'score_bb'] = -1.0
        
        # Médias Móveis Score (peso: 15%)
        sma_20 = indicadores['sma_20']
        sma_50 = indicadores['sma_50']
        
        scores['score_sma'] = 0.0
        scores.loc[(preco > sma_20) & (preco > sma_50) & (sma_20 > sma_50), 'score_sma'] = 1.0
        scores.loc[(preco > sma_20) & (preco < sma_50), 'score_sma'] = 0.3
        scores.loc[(preco < sma_20) & (preco > sma_50), 'score_sma'] = -0.3
        scores.loc[(preco < sma_20) & (preco < sma_50) & (sma_20 < sma_50), 'score_sma'] = -1.0
        
        # Estocástico Score (peso: 10%)
        k_percent = indicadores['estocastico_k']
        scores['score_estocastico'] = 0.0
        scores.loc[k_percent < 20, 'score_estocastico'] = 1.0
        scores.loc[(k_percent >= 20) & (k_percent < 40), 'score_estocastico'] = 0.5
        scores.loc[(k_percent >= 60) & (k_percent < 80), 'score_estocastico'] = -0.5
        scores.loc[k_percent >= 80, 'score_estocastico'] = -1.0
        
        # Williams %R Score (peso: 10%)
        williams_r = indicadores['williams_r']
        scores['score_williams'] = 0.0
        scores.loc[williams_r < -80, 'score_williams'] = 1.0
        scores.loc[(williams_r >= -80) & (williams_r < -60), 'score_williams'] = 0.5
        scores.loc[(williams_r >= -40) & (williams_r < -20), 'score_williams'] = -0.5
        scores.loc[williams_r >= -20, 'score_williams'] = -1.0
        
        # Score final ponderado
        pesos = {
            'score_rsi': 0.20,
            'score_macd': 0.25,
            'score_bb': 0.20,
            'score_sma': 0.15,
            'score_estocastico': 0.10,
            'score_williams': 0.10
        }
        
        scores['score_final'] = 0.0
        for indicador, peso in pesos.items():
            scores['score_final'] += scores[indicador] * peso
        
        return scores
    
    def identificar_padroes_candlestick(self, df):
        """Identifica padrões básicos de candlestick"""
        if df is None or df.empty:
            return None
        
        padroes = pd.DataFrame(index=df.index)
        corpo = abs(df['close'] - df['open'])
        sombra_total = df['high'] - df['low']
        
        padroes['doji'] = (corpo / sombra_total.replace(0, np.nan)) < 0.1
        sombra_inferior = df[['open', 'close']].min(axis=1) - df['low']
        sombra_superior = df['high'] - df[['open', 'close']].max(axis=1)
        padroes['martelo'] = (sombra_inferior > 2 * corpo) & (sombra_superior < corpo)
        padroes['estrela_cadente'] = (sombra_superior > 2 * corpo) & (sombra_inferior < corpo)
        padroes['engolfo_alta'] = ((df['close'] > df['open']) & (df['close'].shift(1) < df['open'].shift(1)) & (df['open'] < df['close'].shift(1)) & (df['close'] > df['open'].shift(1)))
        padroes['engolfo_baixa'] = ((df['close'] < df['open']) & (df['close'].shift(1) > df['open'].shift(1)) & (df['open'] > df['close'].shift(1)) & (df['close'] < df['open'].shift(1)))
        
        return padroes
    
    def calcular_niveis_fibonacci(self, df, periodo=50):
        """Calcula níveis de retração de Fibonacci"""
        if df is None or df.empty:
            return None
        
        high_max = df['high'].rolling(window=periodo).max()
        low_min = df['low'].rolling(window=periodo).min()
        diff = high_max - low_min
        
        return {
            'fib_0': high_max, 'fib_236': high_max - (diff * 0.236),
            'fib_382': high_max - (diff * 0.382), 'fib_500': high_max - (diff * 0.500),
            'fib_618': high_max - (diff * 0.618), 'fib_786': high_max - (diff * 0.786),
            'fib_100': low_min
        }
    
    def gerar_recomendacao_avancada(self, symbol, periodo='6mo'):
        """Gera recomendação avançada com análise completa"""
        df = self.analisador.buscar_dados_completos(symbol, periodo)
        if df is None: return None
        
        indicadores = self.analisador.calcular_todos_indicadores(df)
        if indicadores is None: return None
        
        scores = self.calcular_score_detalhado(df, indicadores)
        padroes = self.identificar_padroes_candlestick(df)
        fibonacci = self.calcular_niveis_fibonacci(df)
        
        preco_atual = df['close'].iloc[-1]
        score_atual = scores['score_final'].iloc[-1]
        rsi_atual = indicadores['rsi'].iloc[-1]
        
        if score_atual > 0.6: recomendacao, cor, confianca = "COMPRA MUITO FORTE", "darkgreen", "Muito Alta"
        elif score_atual > 0.3: recomendacao, cor, confianca = "COMPRA FORTE", "green", "Alta"
        elif score_atual > 0.1: recomendacao, cor, confianca = "COMPRA", "lightgreen", "Moderada"
        elif score_atual < -0.6: recomendacao, cor, confianca = "VENDA MUITO FORTE", "darkred", "Muito Alta"
        elif score_atual < -0.3: recomendacao, cor, confianca = "VENDA FORTE", "red", "Alta"
        elif score_atual < -0.1: recomendacao, cor, confianca = "VENDA", "lightcoral", "Moderada"
        else: recomendacao, cor, confianca = "NEUTRO", "gray", "Baixa"
        
        if fibonacci and not fibonacci['fib_382'].isnull().all():
            preco_alvo_1 = fibonacci['fib_382' if score_atual > 0 else 'fib_618'].iloc[-1]
            preco_alvo_2 = fibonacci['fib_236' if score_atual > 0 else 'fib_786'].iloc[-1]
            stop_loss = fibonacci['fib_618' if score_atual > 0 else 'fib_236'].iloc[-1]
        else:
            preco_alvo_1 = indicadores['bb_superior'].iloc[-1]
            preco_alvo_2 = indicadores['bb_superior'].iloc[-1] * 1.05
            stop_loss = indicadores['bb_inferior'].iloc[-1]
            
        padroes_recentes = [p.replace('_', ' ').title() for p in padroes.columns if padroes[p].tail(5).any()] if padroes is not None else []

        return {
            'symbol': symbol, 'preco_atual': preco_atual, 'recomendacao': recomendacao,
            'cor_recomendacao': cor, 'confianca': confianca, 'score_final': score_atual,
            'rsi_atual': rsi_atual, 'preco_alvo_1': preco_alvo_1, 'preco_alvo_2': preco_alvo_2,
            'stop_loss': stop_loss, 'padroes_recentes': padroes_recentes,
            'dados_historicos': df, 'indicadores': indicadores, 'scores_detalhados': scores,
            'padroes_candlestick': padroes, 'niveis_fibonacci': fibonacci,
            'analise_detalhada': {
                'tendencia_rsi': self._classificar_rsi(rsi_atual),
                'posicao_bb': self._analisar_bollinger(preco_atual, indicadores),
                'momentum_macd': self._analisar_macd(indicadores),
                'forca_tendencia': self._analisar_medias_moveis(preco_atual, indicadores),
                'volatilidade': self._classificar_volatilidade(df)
            }
        }

    def _classificar_rsi(self, rsi):
        if rsi > 80: return "Extremamente Sobrecomprado"
        if rsi > 70: return "Sobrecomprado"
        if rsi < 20: return "Extremamente Sobrevendido"
        if rsi < 30: return "Sobrevendido"
        return "Neutro"

    def _analisar_bollinger(self, preco, indicadores):
        if preco > indicadores['bb_superior'].iloc[-1]: return "Rompimento da banda superior"
        if preco < indicadores['bb_inferior'].iloc[-1]: return "Rompimento da banda inferior"
        if preco > indicadores['bb_media'].iloc[-1]: return "Acima da média móvel"
        return "Abaixo da média móvel"

    def _analisar_macd(self, indicadores):
        macd, sinal, hist = indicadores['macd'].iloc[-1], indicadores['sinal'].iloc[-1], indicadores['histograma'].iloc[-1]
        if macd > sinal: return "Momentum forte de alta" if hist > 0 else "Momentum de alta enfraquecendo"
        return "Momentum forte de baixa" if hist < 0 else "Momentum de baixa enfraquecendo"

    def _analisar_medias_moveis(self, preco, indicadores):
        sma_20, sma_50 = indicadores['sma_20'].iloc[-1], indicadores['sma_50'].iloc[-1]
        if preco > sma_20 > sma_50: return "Tendência de alta forte"
        if preco < sma_20 < sma_50: return "Tendência de baixa forte"
        return "Tendência indefinida"

    def _classificar_volatilidade(self, df):
        volatilidade = df['close'].pct_change().std() * np.sqrt(252) * 100
        if volatilidade > 40: return "Muito Alta"
        if volatilidade > 25: return "Alta"
        if volatilidade > 15: return "Moderada"
        return "Baixa"

    def criar_grafico_recomendacao(self, resultado):
        if resultado is None: return None
        
        df = resultado['dados_historicos']
        indicadores = resultado['indicadores']
        scores = resultado['scores_detalhados']
        
        fig = make_subplots(rows=5, cols=1, shared_xaxes=True, vertical_spacing=0.03,
                            subplot_titles=(f'{resultado["symbol"]} - Análise Completa - {resultado["recomendacao"]}',
                                            'RSI', 'MACD', 'Score de Recomendação', 'Volume'),
                            row_heights=[0.4, 0.15, 0.15, 0.15, 0.15])
        
        fig.add_trace(go.Candlestick(x=df.index, open=df['open'], high=df['high'], low=df['low'], close=df['close'], name='Preço'), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=indicadores['bb_superior'], name='BB Superior', line=dict(color='red', dash='dash')), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=indicadores['bb_inferior'], name='BB Inferior', line=dict(color='red', dash='dash')), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=indicadores['bb_media'], name='Média Móvel', line=dict(color='blue')), row=1, col=1)
        
        fig.add_trace(go.Scatter(x=df.index, y=indicadores['rsi'], name='RSI', line=dict(color='purple')), row=2, col=1)
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
        
        fig.add_trace(go.Scatter(x=df.index, y=indicadores['macd'], name='MACD', line=dict(color='blue')), row=3, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=indicadores['sinal'], name='Sinal', line=dict(color='orange')), row=3, col=1)
        fig.add_trace(go.Bar(x=df.index, y=indicadores['histograma'], name='Histograma', marker_color='grey'), row=3, col=1)
        
        fig.add_trace(go.Scatter(x=scores.index, y=scores['score_final'], name='Score Final', line=dict(color='black')), row=4, col=1)
        fig.add_hline(y=0.3, line_dash="dash", line_color="green", row=4, col=1)
        fig.add_hline(y=-0.3, line_dash="dash", line_color="red", row=4, col=1)
        
        fig.add_trace(go.Bar(x=df.index, y=df['volume'], name='Volume', marker_color='lightblue'), row=5, col=1)
        
        fig.update_layout(title_text=f'Análise Avançada: {resultado["symbol"]}', height=900, showlegend=False, xaxis_rangeslider_visible=False)
        return fig

def exemplo_recomendacao_avancada():
    """Exemplo de uso do sistema de recomendações avançadas"""
    sistema = SistemaRecomendacoes()
    ativo = 'TSLA'  # Exemplo com um ativo volátil
    
    resultado = sistema.gerar_recomendacao_avancada(ativo, periodo='1y')
    
    if resultado:
        print(f"\n--- RECOMENDAÇÃO AVANÇADA: {ativo} ---")
        print(f"Recomendação: {resultado['recomendacao']} (Confiança: {resultado['confianca']})")
        print(f"Preço Atual: ${resultado['preco_atual']:.2f}")
        print(f"Score Final: {resultado['score_final']:.3f}")
        print(f"Alvo 1: ${resultado['preco_alvo_1']:.2f} | Alvo 2: ${resultado['preco_alvo_2']:.2f}")
        print(f"Stop Loss Sugerido: ${resultado['stop_loss']:.2f}")
        if resultado['padroes_recentes']:
            print(f"Padrões Recentes: {', '.join(resultado['padroes_recentes'])}")
        
        # Gerar e mostrar o gráfico
        fig = sistema.criar_grafico_recomendacao(resultado)
        if fig:
            print("\nGerando gráfico interativo...")
            # fig.show() # Descomente para exibir o gráfico se estiver rodando localmente

if __name__ == "__main__":
    exemplo_recomendacao_avancada()






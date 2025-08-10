#!/usr/bin/env python3
"""
Módulo de Análise Preditiva para Investimentos
Inclui indicadores técnicos e sistema de recomendações de compra/venda
Baseado na estrutura do simulador existente
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

class IndicadoresTecnicos:
    """Classe para calcular indicadores técnicos"""
    
    @staticmethod
    def calcular_rsi(precos, periodo=14):
        """
        Calcula o RSI (Relative Strength Index)
        RSI > 70: Sobrecomprado (sinal de venda)
        RSI < 30: Sobrevendido (sinal de compra)
        """
        delta = precos.diff()
        ganho = (delta.where(delta > 0, 0)).rolling(window=periodo).mean()
        perda = (-delta.where(delta < 0, 0)).rolling(window=periodo).mean()
        
        rs = ganho / perda
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    @staticmethod
    def calcular_macd(precos, rapida=12, lenta=26, sinal=9):
        """
        Calcula o MACD (Moving Average Convergence Divergence)
        Sinal de compra: MACD cruza acima da linha de sinal
        Sinal de venda: MACD cruza abaixo da linha de sinal
        """
        ema_rapida = precos.ewm(span=rapida).mean()
        ema_lenta = precos.ewm(span=lenta).mean()
        
        macd_linha = ema_rapida - ema_lenta
        macd_sinal = macd_linha.ewm(span=sinal).mean()
        macd_histograma = macd_linha - macd_sinal
        
        return {
            'macd': macd_linha,
            'sinal': macd_sinal,
            'histograma': macd_histograma
        }
    
    @staticmethod
    def calcular_bollinger_bands(precos, periodo=20, desvios=2):
        """
        Calcula as Bandas de Bollinger
        Preço próximo à banda superior: possível sobrecompra
        Preço próximo à banda inferior: possível sobrevenda
        """
        media_movel = precos.rolling(window=periodo).mean()
        desvio_padrao = precos.rolling(window=periodo).std()
        
        banda_superior = media_movel + (desvios * desvio_padrao)
        banda_inferior = media_movel - (desvios * desvio_padrao)
        
        return {
            'media': media_movel,
            'superior': banda_superior,
            'inferior': banda_inferior
        }
    
    @staticmethod
    def calcular_medias_moveis(precos, periodos=[20, 50, 200]):
        """
        Calcula médias móveis simples para diferentes períodos
        """
        medias = {}
        for periodo in periodos:
            medias[f'sma_{periodo}'] = precos.rolling(window=periodo).mean()
        return medias
    
    @staticmethod
    def calcular_estocastico(high, low, close, k_periodo=14, d_periodo=3):
        """
        Calcula o Oscilador Estocástico
        %K > 80: Sobrecomprado
        %K < 20: Sobrevendido
        """
        lowest_low = low.rolling(window=k_periodo).min()
        highest_high = high.rolling(window=k_periodo).max()
        
        k_percent = 100 * ((close - lowest_low) / (highest_high - lowest_low))
        d_percent = k_percent.rolling(window=d_periodo).mean()
        
        return {
            'k_percent': k_percent,
            'd_percent': d_percent
        }
    
    @staticmethod
    def calcular_williams_r(high, low, close, periodo=14):
        """
        Calcula o Williams %R
        %R > -20: Sobrecomprado
        %R < -80: Sobrevendido
        """
        highest_high = high.rolling(window=periodo).max()
        lowest_low = low.rolling(window=periodo).min()
        
        williams_r = -100 * ((highest_high - close) / (highest_high - lowest_low))
        return williams_r

class AnalisePreditiva:
    """Classe principal para análise preditiva"""
    
    def __init__(self):
        self.indicadores = IndicadoresTecnicos()
    
    def buscar_dados_completos(self, symbol, periodo='1y', interval='1d'):
        """Busca dados históricos completos para análise"""
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=periodo, interval=interval)
            
            if df.empty:
                return None
            
            # Padronizar nomes das colunas
            df.columns = [col.lower() for col in df.columns]
            return df
        except Exception as e:
            print(f"Erro ao buscar dados para {symbol}: {str(e)}")
            return None
    
    def calcular_todos_indicadores(self, df):
        """Calcula todos os indicadores técnicos"""
        if df is None or df.empty:
            return None
        
        indicadores = {}
        
        # RSI
        indicadores['rsi'] = self.indicadores.calcular_rsi(df['close'])
        
        # MACD
        macd_data = self.indicadores.calcular_macd(df['close'])
        indicadores.update(macd_data)
        
        # Bollinger Bands
        bb_data = self.indicadores.calcular_bollinger_bands(df['close'])
        indicadores['bb_media'] = bb_data['media']
        indicadores['bb_superior'] = bb_data['superior']
        indicadores['bb_inferior'] = bb_data['inferior']
        
        # Médias Móveis
        medias = self.indicadores.calcular_medias_moveis(df['close'])
        indicadores.update(medias)
        
        # Estocástico
        estocastico = self.indicadores.calcular_estocastico(
            df['high'], df['low'], df['close']
        )
        indicadores['estocastico_k'] = estocastico['k_percent']
        indicadores['estocastico_d'] = estocastico['d_percent']
        
        # Williams %R
        indicadores['williams_r'] = self.indicadores.calcular_williams_r(
            df['high'], df['low'], df['close']
        )
        
        return indicadores
    
    def gerar_sinais_trading(self, df, indicadores):
        """Gera sinais de compra e venda baseados nos indicadores"""
        if df is None or indicadores is None:
            return None
        
        sinais = pd.DataFrame(index=df.index)
        sinais['preco'] = df['close']
        
        # Sinais baseados no RSI
        sinais['sinal_rsi'] = 0
        sinais.loc[indicadores['rsi'] < 30, 'sinal_rsi'] = 1  # Compra
        sinais.loc[indicadores['rsi'] > 70, 'sinal_rsi'] = -1  # Venda
        
        # Sinais baseados no MACD
        sinais['sinal_macd'] = 0
        macd_cruzamento = (indicadores['macd'] > indicadores['sinal']) & \
                         (indicadores['macd'].shift(1) <= indicadores['sinal'].shift(1))
        sinais.loc[macd_cruzamento, 'sinal_macd'] = 1  # Compra
        
        macd_cruzamento_baixo = (indicadores['macd'] < indicadores['sinal']) & \
                               (indicadores['macd'].shift(1) >= indicadores['sinal'].shift(1))
        sinais.loc[macd_cruzamento_baixo, 'sinal_macd'] = -1  # Venda
        
        # Sinais baseados nas Bollinger Bands
        sinais['sinal_bb'] = 0
        sinais.loc[df['close'] <= indicadores['bb_inferior'], 'sinal_bb'] = 1  # Compra
        sinais.loc[df['close'] >= indicadores['bb_superior'], 'sinal_bb'] = -1  # Venda
        
        # Sinais baseados no Estocástico
        sinais['sinal_estocastico'] = 0
        sinais.loc[indicadores['estocastico_k'] < 20, 'sinal_estocastico'] = 1  # Compra
        sinais.loc[indicadores['estocastico_k'] > 80, 'sinal_estocastico'] = -1  # Venda
        
        # Sinais baseados no Williams %R
        sinais['sinal_williams'] = 0
        sinais.loc[indicadores['williams_r'] < -80, 'sinal_williams'] = 1  # Compra
        sinais.loc[indicadores['williams_r'] > -20, 'sinal_williams'] = -1  # Venda
        
        # Score consolidado (média dos sinais)
        colunas_sinais = ['sinal_rsi', 'sinal_macd', 'sinal_bb', 'sinal_estocastico', 'sinal_williams']
        sinais['score_consolidado'] = sinais[colunas_sinais].mean(axis=1)
        
        return sinais
    
    def calcular_niveis_suporte_resistencia(self, df, janela=20):
        """Calcula níveis de suporte e resistência"""
        if df is None or df.empty:
            return None
        
        # Máximos e mínimos locais
        maximos_locais = df['high'].rolling(window=janela, center=True).max() == df['high']
        minimos_locais = df['low'].rolling(window=janela, center=True).min() == df['low']
        
        # Níveis de resistência (máximos locais)
        resistencias = df.loc[maximos_locais, 'high'].sort_values(ascending=False).head(5)
        
        # Níveis de suporte (mínimos locais)
        suportes = df.loc[minimos_locais, 'low'].sort_values(ascending=True).head(5)
        
        return {
            'resistencias': resistencias.tolist(),
            'suportes': suportes.tolist()
        }
    
    def gerar_recomendacao(self, symbol, periodo='6mo'):
        """Gera recomendação completa de investimento"""
        print(f"Analisando {symbol} para recomendação...")
        
        # Buscar dados
        df = self.buscar_dados_completos(symbol, periodo)
        if df is None:
            return None
        
        # Calcular indicadores
        indicadores = self.calcular_todos_indicadores(df)
        if indicadores is None:
            return None
        
        # Gerar sinais
        sinais = self.gerar_sinais_trading(df, indicadores)
        
        # Calcular níveis de suporte e resistência
        niveis = self.calcular_niveis_suporte_resistencia(df)
        
        # Análise atual (últimos valores)
        preco_atual = df['close'].iloc[-1]
        rsi_atual = indicadores['rsi'].iloc[-1]
        score_atual = sinais['score_consolidado'].iloc[-1]
        
        # Determinar recomendação
        if score_atual > 0.3:
            recomendacao = "COMPRA FORTE"
            cor_recomendacao = "green"
        elif score_atual > 0.1:
            recomendacao = "COMPRA"
            cor_recomendacao = "lightgreen"
        elif score_atual < -0.3:
            recomendacao = "VENDA FORTE"
            cor_recomendacao = "red"
        elif score_atual < -0.1:
            recomendacao = "VENDA"
            cor_recomendacao = "lightcoral"
        else:
            recomendacao = "NEUTRO"
            cor_recomendacao = "gray"
        
        # Calcular preços alvo
        if niveis and len(niveis['resistencias']) > 0 and len(niveis['suportes']) > 0:
            preco_alvo_alta = niveis['resistencias'][0]
            preco_alvo_baixa = niveis['suportes'][0]
        else:
            # Usar Bollinger Bands como alternativa
            preco_alvo_alta = indicadores['bb_superior'].iloc[-1]
            preco_alvo_baixa = indicadores['bb_inferior'].iloc[-1]
        
        resultado = {
            'symbol': symbol,
            'preco_atual': preco_atual,
            'recomendacao': recomendacao,
            'cor_recomendacao': cor_recomendacao,
            'score_consolidado': score_atual,
            'rsi_atual': rsi_atual,
            'preco_alvo_alta': preco_alvo_alta,
            'preco_alvo_baixa': preco_alvo_baixa,
            'dados_historicos': df,
            'indicadores': indicadores,
            'sinais': sinais,
            'niveis_suporte_resistencia': niveis,
            'analise_detalhada': {
                'tendencia_rsi': 'Sobrecomprado' if rsi_atual > 70 else 'Sobrevendido' if rsi_atual < 30 else 'Neutro',
                'posicao_bb': self._analisar_posicao_bollinger(preco_atual, indicadores),
                'momentum_macd': self._analisar_momentum_macd(indicadores)
            }
        }
        
        return resultado
    
    def _analisar_posicao_bollinger(self, preco, indicadores):
        """Analisa posição do preço em relação às Bollinger Bands"""
        bb_superior = indicadores['bb_superior'].iloc[-1]
        bb_inferior = indicadores['bb_inferior'].iloc[-1]
        bb_media = indicadores['bb_media'].iloc[-1]
        
        if preco >= bb_superior:
            return "Acima da banda superior (sobrecomprado)"
        elif preco <= bb_inferior:
            return "Abaixo da banda inferior (sobrevendido)"
        elif preco > bb_media:
            return "Acima da média móvel (tendência alta)"
        else:
            return "Abaixo da média móvel (tendência baixa)"
    
    def _analisar_momentum_macd(self, indicadores):
        """Analisa momentum baseado no MACD"""
        macd_atual = indicadores['macd'].iloc[-1]
        sinal_atual = indicadores['sinal'].iloc[-1]
        histograma_atual = indicadores['histograma'].iloc[-1]
        
        if macd_atual > sinal_atual and histograma_atual > 0:
            return "Momentum positivo (alta)"
        elif macd_atual < sinal_atual and histograma_atual < 0:
            return "Momentum negativo (baixa)"
        else:
            return "Momentum neutro"
    
    def criar_grafico_analise_completa(self, resultado):
        """Cria gráfico completo com análise técnica"""
        if resultado is None:
            return None
        
        df = resultado['dados_historicos']
        indicadores = resultado['indicadores']
        sinais = resultado['sinais']
        
        # Criar subplots
        fig = make_subplots(
            rows=4, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            subplot_titles=(
                f'{resultado["symbol"]} - Preço e Bollinger Bands',
                'RSI',
                'MACD',
                'Sinais de Trading'
            ),
            row_heights=[0.4, 0.2, 0.2, 0.2]
        )
        
        # Gráfico de preços com Bollinger Bands
        fig.add_trace(
            go.Scatter(x=df.index, y=df['close'], name='Preço', line=dict(color='blue')),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(x=df.index, y=indicadores['bb_superior'], name='BB Superior', 
                      line=dict(color='red', dash='dash')),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(x=df.index, y=indicadores['bb_inferior'], name='BB Inferior',
                      line=dict(color='red', dash='dash')),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(x=df.index, y=indicadores['bb_media'], name='Média Móvel',
                      line=dict(color='orange')),
            row=1, col=1
        )
        
        # RSI
        fig.add_trace(
            go.Scatter(x=df.index, y=indicadores['rsi'], name='RSI', line=dict(color='purple')),
            row=2, col=1
        )
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
        
        # MACD
        fig.add_trace(
            go.Scatter(x=df.index, y=indicadores['macd'], name='MACD', line=dict(color='blue')),
            row=3, col=1
        )
        fig.add_trace(
            go.Scatter(x=df.index, y=indicadores['sinal'], name='Sinal', line=dict(color='red')),
            row=3, col=1
        )
        fig.add_trace(
            go.Bar(x=df.index, y=indicadores['histograma'], name='Histograma'),
            row=3, col=1
        )
        
        # Score consolidado
        fig.add_trace(
            go.Scatter(x=sinais.index, y=sinais['score_consolidado'], name='Score Consolidado',
                      line=dict(color='orange')),
            row=4, col=1
        )
        fig.add_hline(y=0.3, line_dash="dash", line_color="green", row=4, col=1)
        fig.add_hline(y=-0.3, line_dash="dash", line_color="red", row=4, col=1)
        
        # Layout
        fig.update_layout(
            title=f'Análise Técnica Completa - {resultado["symbol"]}',
            height=800,
            showlegend=True
        )
        
        return fig

def exemplo_analise_preditiva():
    """Exemplo de uso da análise preditiva"""
    analisador = AnalisePreditiva()
    
    # Exemplos de ativos para análise
    ativos = ['AAPL', 'PETR4.SA', 'BOVA11.SA', 'VALE3.SA']
    
    print("=== ANÁLISE PREDITIVA DE INVESTIMENTOS ===\n")
    
    for ativo in ativos:
        resultado = analisador.gerar_recomendacao(ativo, periodo='6mo')
        
        if resultado:
            print(f"\n--- ANÁLISE: {ativo} ---")
            print(f"Preço Atual: ${resultado['preco_atual']:.2f}")
            print(f"Recomendação: {resultado['recomendacao']}")
            print(f"Score Consolidado: {resultado['score_consolidado']:.3f}")
            print(f"RSI Atual: {rsi_value}") 





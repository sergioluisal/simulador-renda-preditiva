#!/usr/bin/env python3
"""
Interface Streamlit com Análise Preditiva Integrada
Baseado no simulador existente com funcionalidades avançadas de recomendação
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Importar módulos personalizados
try:
    from analise_preditiva import AnalisePreditiva
    from sistema_recomendacoes import SistemaRecomendacoes
    from lista_ativos import obter_sugestoes_por_categoria
except ImportError as e:
    st.error(
        f"Erro ao importar um módulo: '{e.name}'. Verifique se todos os arquivos .py "
        "(`analise_preditiva.py`, `sistema_recomendacoes.py`, `lista_ativos.py`) "
        "estão no mesmo diretório que este script."
    )
    st.stop()

# Dicionário de categorias de ativos
CATEGORIAS_DE_ATIVOS = {
    "Ações Americanas": "acoes_americanas",
    "Ações Brasileiras": "acoes_brasileiras",
    "BDRs": "bdrs",
    "ETFs Brasileiros": "etfs_brasileiros",
    "ETFs Americanos": "etfs_americanos"
}
st.set_page_config(
    page_title="Simulador de Renda Variável com Análise Preditiva",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem; font-weight: bold; text-align: center; margin-bottom: 2rem;
        color: #1E88E5;
    }
    .metric-card {
        background-color: #f0f2f6; padding: 1rem; border-radius: 0.5rem;
        border-left: 5px solid #1E88E5; margin: 0.5rem 0;
    }
    .recommendation-box {
        padding: 1rem; border-radius: 0.5rem; font-weight: bold;
        text-align: center; font-size: 1.2rem; margin-bottom: 1rem;
    }
    .strong-buy { background-color: #d4edda; color: #155724; border-left: 5px solid #28a745; }
    .buy { background-color: #e2f0d9; color: #38761d; border-left: 5px solid #6aa84f; }
    .neutral { background-color: #f8f9fa; color: #495057; border-left: 5px solid #6c757d; }
    .sell { background-color: #f8d7da; color: #721c24; border-left: 5px solid #dc3545; }
    .strong-sell { background-color: #f1c2c6; color: #a94442; border-left: 5px solid #cc0000; }
</style>
""", unsafe_allow_html=True)


# --- FUNÇÕES DE EXECUÇÃO ---

def executar_analise_preditiva(simbolo, periodo_analise):
    st.header(f"🔮 Análise Preditiva: {simbolo}")
    if st.button("📊 Analisar Ativo", key="analise_basica", type="primary", use_container_width=True):
        with st.spinner(f"Executando análise para {simbolo}..."):
            try:
                analisador = AnalisePreditiva()
                resultado = analisador.gerar_recomendacao(simbolo, periodo=periodo_analise)
                if resultado:
                    exibir_analise_preditiva(resultado)
                else:
                    st.error(f"❌ Não foi possível analisar {simbolo}. Verifique se o símbolo está correto ou tente novamente.")
            except Exception as e:
                st.error(f"Ocorreu um erro inesperado durante a análise: {e}")

def executar_recomendacoes_avancadas(simbolo, periodo_analise):
    st.header(f"🎯 Recomendações Avançadas: {simbolo}")
    if st.button("🔍 Gerar Recomendação Avançada", key="analise_avancada", type="primary", use_container_width=True):
        with st.spinner(f"Gerando recomendação avançada para {simbolo}..."):
            try:
                sistema = SistemaRecomendacoes()
                resultado = sistema.gerar_recomendacao_avancada(simbolo, periodo=periodo_analise)
                if resultado:
                    exibir_recomendacoes_avancadas(resultado)
                else:
                    st.error(f"❌ Não foi possível gerar recomendação para {simbolo}. Verifique o símbolo.")
            except Exception as e:
                st.error(f"Ocorreu um erro inesperado durante a recomendação: {e}")

def executar_comparacao_ativos(tipo_ativo, periodo_analise):
    st.header("⚖️ Comparação de Ativos")
    ativos_sugeridos = ATIVOS_POPULARES.get(tipo_ativo, [])
    exemplo_ativos = ",".join(ativos_sugeridos[:3]) if ativos_sugeridos else "AAPL,GOOGL,MSFT"
    
    ativos_comparacao = st.text_area(
        "Digite os símbolos dos ativos separados por vírgula:",
        value=exemplo_ativos,
        help="Exemplo: AAPL,GOOGL,MSFT ou PETR4.SA,VALE3.SA,ITUB4.SA"
    )
    
    if st.button("📈 Comparar Ativos", key="comparar", type="primary", use_container_width=True):
        simbolos = [s.strip().upper() for s in ativos_comparacao.split(",") if s.strip()]
        if len(simbolos) < 2:
            st.error("❌ Por favor, insira pelo menos 2 símbolos para comparação.")
            return
        
        with st.spinner("Comparando ativos... Por favor, aguarde."):
            try:
                comparar_multiplos_ativos(simbolos, periodo_analise)
            except Exception as e:
                st.error(f"Ocorreu um erro inesperado durante a comparação: {e}")

# --- FUNÇÕES DE EXIBIÇÃO ---

def exibir_analise_preditiva(resultado):
    st.success("✅ Análise preditiva concluída!")
    
    rec_map = {
        "COMPRA FORTE": "strong-buy", "COMPRA": "buy",
        "VENDA FORTE": "strong-sell", "VENDA": "sell", "NEUTRO": "neutral"
    }
    rec_class = rec_map.get(resultado['recomendacao'], "neutral")
    
    html_string = f"""<div class="recommendation-box {rec_class}">{resultado["recomendacao"]}</div>"""
    st.markdown(html_string, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("💰 Preço Atual", f"${resultado['preco_atual']:.2f}")
    col2.metric("📊 Score", f"{resultado['score_consolidado']:.3f}")
    col3.metric("📈 RSI", f"{resultado['rsi_atual']:.1f}")
    
    with st.expander("🎯 Preços-Alvo e Análise Detalhada"):
        st.metric("🎯 Preço Alvo (Alta)", f"${resultado['preco_alvo_alta']:.2f}")
        st.metric("🛑 Preço Alvo (Baixa)", f"${resultado['preco_alvo_baixa']:.2f}")
        st.write(f"**Tendência RSI:** {resultado['analise_detalhada']['tendencia_rsi']}")
        st.write(f"**Posição Bollinger:** {resultado['analise_detalhada']['posicao_bb']}")
        st.write(f"**Momentum MACD:** {resultado['analise_detalhada']['momentum_macd']}")

    fig = AnalisePreditiva().criar_grafico_analise_completa(resultado)
    if fig:
        st.plotly_chart(fig, use_container_width=True)
        
        # <<< NOVO BLOCO DE EXPLICAÇÃO ADICIONADO AQUI >>>
        with st.expander("📘 Entenda os Indicadores do Gráfico"):
            st.markdown("""
            - **Preço:** A linha principal que mostra a cotação do ativo ao longo do tempo.
            - **BB Superior / Inferior (Bandas de Bollinger):** Criam um canal de volatilidade. Preço perto da banda superior pode indicar sobrecompra (possível venda); perto da inferior, sobrevenda (possível compra).
            - **Média Móvel:** Suaviza o preço para mostrar a tendência principal. Se o preço está acima dela, a tendência é de alta, e vice-versa.
            - **RSI (Índice de Força Relativa):** Mede a força do movimento. Acima de 70 é considerado sobrecomprado; abaixo de 30, sobrevendido.
            - **MACD e Sinal:** Indicador de tendência. Quando a linha MACD (mais rápida) cruza para cima da linha de Sinal (mais lenta), é um sinal de compra. O inverso é um sinal de venda.
            - **Histograma:** Representa a diferença entre o MACD e o Sinal. Barras grandes indicam que a tendência atual (alta ou baixa) está forte.
            - **Score Consolidado:** Uma métrica criada por este programa que combina todos os indicadores em uma única pontuação para gerar a recomendação final.
            """)

def exibir_recomendacoes_avancadas(resultado):
    st.success("✅ Recomendação avançada gerada!")
    
    rec_map = {
        "COMPRA MUITO FORTE": "strong-buy", "COMPRA FORTE": "strong-buy", "COMPRA": "buy",
        "VENDA MUITO FORTE": "strong-sell", "VENDA FORTE": "strong-sell", "VENDA": "sell", "NEUTRO": "neutral"
    }
    rec_class = rec_map.get(resultado['recomendacao'], "neutral")

    html_string = f"""<div class="recommendation-box {rec_class}">{resultado["recomendacao"]}  
<small>Confiança: {resultado["confianca"]}</small></div>"""
    st.markdown(html_string, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💰 Preço Atual", f"${resultado['preco_atual']:.2f}")
    col2.metric("📊 Score Final", f"{resultado['score_final']:.3f}")
    col3.metric("🎯 Alvo Principal", f"${resultado['preco_alvo_1']:.2f}")
    col4.metric("🛑 Stop Loss", f"${resultado['stop_loss']:.2f}")
    
    if resultado['padroes_recentes']:
        st.subheader("🕯️ Padrões de Candlestick Recentes")
        st.info(f"Padrões identificados nos últimos 5 dias: **{', '.join(resultado['padroes_recentes'])}**")
    
    with st.expander("🔬 Análise Técnica Detalhada"):
        analise = resultado['analise_detalhada']
        st.write(f"**RSI:** {analise['tendencia_rsi']}")
        st.write(f"**Bollinger Bands:** {analise['posicao_bb']}")
        st.write(f"**MACD:** {analise['momentum_macd']}")
        st.write(f"**Força da Tendência:** {analise['forca_tendencia']}")
        st.write(f"**Volatilidade:** {analise['volatilidade']}")

    fig = SistemaRecomendacoes().criar_grafico_recomendacao(resultado)
    if fig:
        st.plotly_chart(fig, use_container_width=True)
        
        # <<< NOVO BLOCO DE EXPLICAÇÃO ADICIONADO AQUI >>>
        with st.expander("📘 Entenda os Indicadores do Gráfico"):
            st.markdown("""
            - **Gráfico de Candlestick:** Mostra os preços de abertura, máximo, mínimo e fechamento de cada dia.
            - **BB Superior / Inferior (Bandas de Bollinger):** Criam um canal de volatilidade. Preço perto da banda superior pode indicar sobrecompra (possível venda); perto da inferior, sobrevenda (possível compra).
            - **Média Móvel:** Suaviza o preço para mostrar a tendência principal. Se o preço está acima dela, a tendência é de alta, e vice-versa.
            - **RSI (Índice de Força Relativa):** Mede a força do movimento. Acima de 70 é considerado sobrecomprado; abaixo de 30, sobrevendido.
            - **MACD e Sinal:** Indicador de tendência. Quando a linha MACD (mais rápida) cruza para cima da linha de Sinal (mais lenta), é um sinal de compra. O inverso é um sinal de venda.
            - **Histograma:** Representa a diferença entre o MACD e o Sinal. Barras grandes indicam que a tendência atual (alta ou baixa) está forte.
            - **Score de Recomendação:** Uma métrica ponderada que combina múltiplos indicadores para gerar a recomendação final.
            - **Volume:** Mostra a quantidade de ações negociadas. Um aumento no volume pode confirmar a força de uma tendência.
            """)

def comparar_multiplos_ativos(simbolos, periodo):
    analisador = AnalisePreditiva()
    resultados = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, simbolo in enumerate(simbolos):
        status_text.text(f"Analisando {i+1}/{len(simbolos)}: {simbolo}...")
        resultado = analisador.gerar_recomendacao(simbolo, periodo=periodo)
        if resultado:
            resultados.append({
                'Símbolo': simbolo,
                'Preço Atual': resultado['preco_atual'],
                'Recomendação': resultado['recomendacao'],
                'Score': resultado['score_consolidado'],
                'RSI': resultado['rsi_atual']
            })
        progress_bar.progress((i + 1) / len(simbolos))
    
    status_text.success("Comparação concluída!")
    
    if resultados:
        df_comparacao = pd.DataFrame(resultados)
        st.subheader("📊 Tabela Comparativa")
        st.dataframe(df_comparacao.style.format({
            'Preço Atual': '${:,.2f}',
            'Score': '{:.3f}',
            'RSI': '{:.1f}'
        }), use_container_width=True)
        
        st.subheader("⚖️ Comparação de Scores")
        fig_scores = go.Figure(data=[go.Bar(
            x=df_comparacao['Símbolo'],
            y=df_comparacao['Score'],
            marker_color=['#28a745' if s > 0.1 else '#dc3545' if s < -0.1 else '#6c757d' for s in df_comparacao['Score']]
        )])
        fig_scores.update_layout(title="Comparação dos Scores de Recomendação", template="plotly_white")
        st.plotly_chart(fig_scores, use_container_width=True)
    else:
        st.warning("⚠️ Nenhum resultado encontrado para os ativos informados.")

# --- FUNÇÃO PRINCIPAL (MAIN) ---

def main():
    st.markdown('<h1 class="main-header">Simulador de Renda Variável Preditiva</h1>', unsafe_allow_html=True)
    
    st.sidebar.header("⚙️ Configurações")
    
    modo_operacao = st.sidebar.selectbox(
        "Modo de Operação",
        ["Análise Preditiva Básica", "Recomendações Avançadas", "Comparação de Ativos"]
    )
    
    st.sidebar.subheader("📊 Configurações do Ativo")
    
    simbolo = ""
    tipo_ativo = ""

    if modo_operacao != "Comparação de Ativos":
        tipo_ativo = st.sidebar.selectbox("Tipo de Ativo", list(CATEGORIAS_DE_ATIVOS.keys()), key="tipo_ativo_selectbox")
        simbolos_sugeridos = CATEGORIAS_DE_ATIVOS[tipo_ativo]
        simbolo_selecionado = st.sidebar.selectbox("Símbolos Sugeridos", simbolos_sugeridos, key="simbolo_sugerido_selectbox")
        simbolo_manual = st.sidebar.text_input("Ou digite o símbolo manualmente:", value=simbolo_selecionado, key="simbolo_manual_text")
        simbolo = simbolo_manual.strip().upper() if simbolo_manual else simbolo_selecionado
    else:
        tipo_ativo = st.sidebar.selectbox("Selecione uma categoria para sugestões:", list(CATEGORIAS_DE_ATIVOS.keys()), key="tipo_ativo_comparacao_selectbox")

    periodo_analise = st.sidebar.selectbox(
        "Período de Análise",
        ["1mo", "3mo", "6mo", "1y", "2y", "5y"],
        index=3, # Padrão para 1 ano
        key="periodo_analise_selectbox"
    )
    
    if modo_operacao == "Análise Preditiva Básica":
        if simbolo:
            executar_analise_preditiva(simbolo, periodo_analise)
    elif modo_operacao == "Recomendações Avançadas":
        if simbolo:
            executar_recomendacoes_avancadas(simbolo, periodo_analise)
    elif modo_operacao == "Comparação de Ativos":
        if tipo_ativo:
            executar_comparacao_ativos(nome_tipo_ativo, periodo_analise)

if __name__ == "__main__":
    main()

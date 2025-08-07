#!/usr/bin/env python3
"""
Interface Streamlit com Análise Preditiva Integrada
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
    .recommendation-box {
        padding: 1rem; border-radius: 0.5rem; font-weight: bold;
        text-align: center; font-size: 1.2rem; margin-bottom: 1rem;
    }
    .strong-buy { background-color: #d4edda; color: #155724; border-left: 5px solid #28a745; }
    .buy { background-color: #e2f0d9; color: #38761d; border-left: 5px solid #6aa84f; }
    .neutral { background-color: #f8f9fa; color: #495057; border-left: 5px solid #6c757d; }
    .sell { background-color: #f8d7da; color: #721c24; border-left: 5px solid #dc3545; }
    .strong-sell { background-color: #f1c2c6; color: #a94442; border-left: 5px solid #cc0000; }
    .legend-item { display: flex; align-items: center; margin-bottom: 8px; }
    .legend-color-box { width: 25px; height: 12px; margin-right: 10px; border: 1px solid #444; }
    .legend-text { font-size: 0.95rem; }
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

# --- CORREÇÃO APLICADA AQUI ---
# A lógica de comparação foi toda movida para dentro desta função,
# tornando-a independente e corrigindo o bug.
def executar_comparacao_ativos(periodo_analise):
    st.header("⚖️ Comparação de Ativos")
    
    # Lógica para as sugestões no campo de texto
    categoria_sugestao = st.sidebar.selectbox(
        "Selecione uma categoria para sugestões de ativos:", 
        list(CATEGORIAS_DE_ATIVOS.keys()), 
        key="tipo_ativo_comparacao_selectbox"
    )
    categoria_tecnica_sugestao = CATEGORIAS_DE_ATIVOS[categoria_sugestao]
    ativos_sugeridos = obter_sugestoes_por_categoria(categoria_tecnica_sugestao)
    exemplo_ativos = ",".join(ativos_sugeridos[:4]) if ativos_sugeridos else "AAPL,GOOGL,MSFT,TSLA"
    
    # Campo de texto para o usuário inserir os ativos
    ativos_comparacao = st.text_area(
        "Digite os símbolos dos ativos separados por vírgula:",
        value=exemplo_ativos,
        help="Exemplo: AAPL,GOOGL,MSFT ou PETR4.SA,VALE3.SA,ITUB4.SA"
    )
    
    # Botão para iniciar a comparação
    if st.button("📈 Comparar Ativos", key="comparar", type="primary", use_container_width=True):
        simbolos = [s.strip().upper() for s in ativos_comparacao.split(",") if s.strip()]
        if len(simbolos) < 2:
            st.error("❌ Por favor, insira pelo menos 2 símbolos para comparação.")
            return
        
        # Lógica de análise e exibição de resultados
        with st.spinner("Comparando ativos... Por favor, aguarde."):
            try:
                analisador = AnalisePreditiva()
                resultados = []
                progress_bar = st.progress(0)
                status_text = st.empty()

                for i, simbolo in enumerate(simbolos):
                    status_text.text(f"Analisando {i+1}/{len(simbolos)}: {simbolo}...")
                    resultado = analisador.gerar_recomendacao(simbolo, periodo=periodo_analise)
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

            except Exception as e:
                st.error(f"Ocorreu um erro inesperado durante a comparação: {e}")

# --- FUNÇÕES DE EXIBIÇÃO (sem alterações) ---

def exibir_analise_preditiva(resultado):
    st.success("✅ Análise preditiva concluída!")
    rec_map = {"COMPRA FORTE": "strong-buy", "COMPRA": "buy", "VENDA FORTE": "strong-sell", "VENDA": "sell", "NEUTRO": "neutral"}
    rec_class = rec_map.get(resultado['recomendacao'], "neutral")
    html_string = f"""<div class="recommendation-box {rec_class}">{resultado["recomendacao"]}</div>"""
    st.markdown(html_string, unsafe_allow_html=True)
    if resultado['recomendacao'] == "VENDA FORTE":
        st.warning("⚠️ **Sugestão de Análise:** A recomendação é de 'Venda Forte'. Considere revisar sua posição.")
    elif resultado['recomendacao'] == "COMPRA FORTE":
        st.info("💡 **Sugestão de Análise:** A recomendação é de 'Compra Forte'. Este pode ser um bom momento para entrar.")
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
        # --- MUDANÇA 2: Nova legenda visual ---
        with st.expander("📘 Entenda os Indicadores do Gráfico"):
            st.markdown("""
                <div class="legend-item">
                    <div class="legend-text"><strong>Candlestick:</strong> Mostra os preços de abertura, máximo, mínimo e fechamento de cada dia.</div>
                </div>
                <div class="legend-item">
                    <div class="legend-color-box" style="background-color: red; border-style: dashed;"></div>
                    <div class="legend-text"><strong>BB Superior / Inferior:</strong> Criam um "canal" de volatilidade.</div>
                </div>
                <div class="legend-item">
                    <div class="legend-color-box" style="background-color: blue;"></div>
                    <div class="legend-text"><strong>Média Móvel:</strong> Suaviza o preço para mostrar a tendência principal.</div>
                </div>
                <div class="legend-item">
                    <div class="legend-color-box" style="background-color: purple;"></div>
                    <div class="legend-text"><strong>RSI:</strong> Mede a força do movimento. Acima de 70 é sobrecomprado; abaixo de 30, sobrevendido.</div>
                </div>
                <div class="legend-item">
                    <div class="legend-color-box" style="background-color: blue;"></div>
                    <div class="legend-text"><strong>MACD:</strong> Indicador de momentum.</div>
                </div>
                <div class="legend-item">
                    <div class="legend-color-box" style="background-color: orange;"></div>
                    <div class="legend-text"><strong>Sinal:</strong> Média da linha MACD, usada para gerar sinais de cruzamento.</div>
                </div>
                <div class="legend-item">
                    <div class="legend-color-box" style="background-color: lightblue;"></div>
                    <div class="legend-text"><strong>Volume:</strong> Quantidade de ações negociadas. Aumento de volume confirma tendências.</div>
                </div>
            """, unsafe_allow_html=True)

def exibir_recomendacoes_avancadas(resultado):
    st.success("✅ Recomendação avançada gerada!")
    rec_map = {"COMPRA MUITO FORTE": "strong-buy", "COMPRA FORTE": "strong-buy", "COMPRA": "buy", "VENDA MUITO FORTE": "strong-sell", "VENDA FORTE": "strong-sell", "VENDA": "sell", "NEUTRO": "neutral"}
    rec_class = rec_map.get(resultado['recomendacao'], "neutral")
    html_string = f"""<div class="recommendation-box {rec_class}">{resultado["recomendacao"]}  
<small>Confiança: {resultado["confianca"]}</small></div>"""
    st.markdown(html_string, unsafe_allow_html=True)
    if "VENDA" in resultado['recomendacao'] and ("FORTE" in resultado['recomendacao'] or "MUITO FORTE" in resultado['recomendacao']):
        st.warning("⚠️ **Sugestão de Análise:** A recomendação de venda é forte. Verifique os níveis de stop loss.")
    elif "COMPRA" in resultado['recomendacao'] and ("FORTE" in resultado['recomendacao'] or "MUITO FORTE" in resultado['recomendacao']):
        st.info("💡 **Sugestão de Análise:** A recomendação de compra é forte. Verifique os preços-alvo.")
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
        with st.expander("📘 Entenda os Indicadores do Gráfico"):
            st.markdown("""...""")

# --- FUNÇÃO PRINCIPAL (MAIN) ---

def main():
    st.markdown('<h1 class="main-header">Simulador de Renda Variável Preditiva</h1>', unsafe_allow_html=True)
    
    st.sidebar.header("⚙️ Configurações")
    
    modo_operacao = st.sidebar.selectbox(
        "Modo de Operação",
        ["Análise Preditiva Básica", "Recomendações Avançadas", "Comparação de Ativos"]
    )
    
    st.sidebar.subheader("📊 Configurações do Ativo")
    
    periodo_analise = st.sidebar.selectbox(
        "Período de Análise",
        ["1mo", "3mo", "6mo", "1y", "2y", "5y"],
        index=3,
        key="periodo_analise_selectbox"
    )
    
    if modo_operacao == "Comparação de Ativos":
        executar_comparacao_ativos(periodo_analise)
    else:
        nome_tipo_ativo = st.sidebar.selectbox(
            "Tipo de Ativo", 
            list(CATEGORIAS_DE_ATIVOS.keys()), 
            key="tipo_ativo_selectbox"
        )
        
        categoria_tecnica = CATEGORIAS_DE_ATIVOS[nome_tipo_ativo]
        simbolos_sugeridos = obter_sugestoes_por_categoria(categoria_tecnica)
        
        simbolo_selecionado = st.sidebar.selectbox("Símbolos Sugeridos", simbolos_sugeridos, key="simbolo_sugerido_selectbox")
        simbolo_manual = st.sidebar.text_input("Ou digite o símbolo manualmente:", value=simbolo_selecionado, key="simbolo_manual_text")
        simbolo = simbolo_manual.strip().upper() if simbolo_manual else simbolo_selecionado
        
        if modo_operacao == "Análise Preditiva Básica":
            if simbolo:
                executar_analise_preditiva(simbolo, periodo_analise)
        elif modo_operacao == "Recomendações Avançadas":
            if simbolo:
                executar_recomendacoes_avancadas(simbolo, periodo_analise)

if __name__ == "__main__":
    main()


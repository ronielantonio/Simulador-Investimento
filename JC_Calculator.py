import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from PIL import Image

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Projeção Estratégica de Capital",
    page_icon="💎",
    layout="wide"
)

# --- CARREGAMENTO DE RECURSOS (IMAGENS) ---
try:
    img_banner = Image.open("Image_01.png")
    img_sidebar = Image.open("Image_02.png")
except FileNotFoundError:
    st.error("Erro crítico: Arquivos de imagem não encontrados. Certifique-se de que 'AdobeStock_458980214_Preview.jpeg' e 'AdobeStock_1287886224_Preview.jpeg' estão no mesmo diretório do script.")
    st.stop()

# --- CSS: Aprimoramento Final de Legibilidade na Sidebar ---
st.markdown("""
<style>
    /* --- GERAL E GRADIENTE DE FUNDO --- */
    [data-testid="stAppViewContainer"] > .main {
        background-image: linear-gradient(to bottom, #0d1117 0%, #1c2a3f 100%);
    }
    .subtitle {
        color: #a1aab4;
        font-size: 1.1em;
    }
    h1, h2, h3 { color: #58a6ff; }
    h1 { border-bottom: 2px solid #30363d; padding-bottom: 10px; }
    
    /* --- SIDEBAR --- */
    [data-testid="stSidebar"] {
        background-color: #161b22;
        border-right: 1px solid #30363d;
    }

    /* <<<<<<<<<<<<<<< INÍCIO DA CORREÇÃO DE TEXTO DA SIDEBAR >>>>>>>>>>>>>>> */
    /* Título principal da Sidebar */
    [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #FFFFFF !important;
    }
    /* Labels de todos os widgets (number_input, slider, etc.) */
    [data-testid="stSidebar"] label {
        color: #F0F0F0 !important; /* Branco de alta legibilidade */
    }
    /* Ícone de ajuda (?) */
    [data-testid="stSidebar"] .stTooltipIcon {
        color: #a1aab4 !important;
    }
    /* <<<<<<<<<<<<<<<<<<<<< FIM DA CORREÇÃO >>>>>>>>>>>>>>>>>>>>> */

    /* --- BOTÃO PRINCIPAL --- */
    .stButton>button {
        background-image: linear-gradient(to right, #58a6ff, #31d7a2);
        color: #FFFFFF;
        border: none;
        border-radius: 8px;
        padding: 12px 24px;
        font-weight: bold;
        font-size: 16px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px 0 rgba(49, 215, 162, 0.4);
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px 0 rgba(88, 166, 255, 0.5);
    }
    
    /* --- CARDS DE MÉTRICAS --- */
    .metric-card {
        background-color: rgba(22, 27, 34, 0.5);
        border-radius: 12px;
        padding: 25px;
        border: 1px solid #30363d;
        border-left: 6px solid #58a6ff;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    .metric-card-growth { border-left-color: #31d7a2; }
    .metric-card .stMetric { background-color: transparent; border: none; padding: 0; }
    
    /* --- RODAPÉ --- */
    .footer { text-align: center; color: #a1aab4; }
</style>
""", unsafe_allow_html=True)

# --- FUNÇÕES DE CÁLCULO (BACKEND) ---
def calcular_juros_compostos_detalhado(investimento_inicial, aporte_mensal, aporte_anual, taxa_juros_anual, periodo_anos):
    taxa_juros_mensal = (taxa_juros_anual / 100) / 12
    dados = []
    valor_final = investimento_inicial
    total_investido_acumulado = investimento_inicial
    for mes in range(1, (periodo_anos * 12) + 1):
        juros_do_mes = valor_final * taxa_juros_mensal
        valor_final += juros_do_mes + aporte_mensal
        total_investido_acumulado += aporte_mensal
        if mes % 12 == 0:
            valor_final += aporte_anual
            total_investido_acumulado += aporte_anual
        dados.append({
            'Mês': mes, 'Ano': ((mes-1)//12) + 1, 'Total Acumulado': valor_final,
            'Total Investido': total_investido_acumulado, 'Total em Juros': valor_final - total_investido_acumulado
        })
    return pd.DataFrame(dados)

@st.cache_data
def convert_df_to_csv(df):
    return df.to_csv(index=False, decimal=',', sep=';').encode('latin1')

# --- INTERFACE (FRONTEND) ---

# --- SIDEBAR: O PAINEL DE CONTROLE ---
with st.sidebar:
    st.image(img_sidebar, use_container_width=True)
    st.header("Painel de Controle Estratégico")
    investimento_inicial = st.number_input("💵 Capital Inicial (R$)", 0.0, value=10000.0, step=1000.0, help="Valor inicial do investimento.")
    aporte_mensal = st.number_input("🗓️ Aporte Mensal (R$)", 0.0, value=1500.0, step=100.0, help="Valor investido recorrentemente todo mês.")
    aporte_anual = st.number_input("🎉 Aporte Anual Extra (R$)", 0.0, value=5000.0, step=500.0, help="Aporte adicional anual (ex: bônus, 13º).")
    st.divider()
    taxa_juros_anual = st.slider("📈 Rentabilidade Anual (%)", 0.0, 30.0, 12.0, 0.5, help="Taxa de juros anual esperada para o investimento.")
    periodo_anos = st.slider("⏳ Horizonte de Tempo (Anos)", 1, 50, 25, 1, help="Período total do investimento em anos.")
    st.divider()
    calcular = st.button("Executar Projeção Estratégica", use_container_width=True)

# --- TELA PRINCIPAL: O DASHBOARD ---
st.title("Plataforma de Projeção Estratégica de Capital")
st.markdown('<p class="subtitle">Uma ferramenta para visualização de crescimento patrimonial a longo prazo.</p>', unsafe_allow_html=True) 
st.image(img_banner, use_container_width=True)
st.markdown("---")

# --- ÁREA DE RESULTADOS DINÂMICOS ---
if calcular:
    df_resultados = calcular_juros_compostos_detalhado(investimento_inicial, aporte_mensal, aporte_anual, taxa_juros_anual, periodo_anos)
    valor_final_acumulado = df_resultados['Total Acumulado'].iloc[-1]
    total_investido = df_resultados['Total Investido'].iloc[-1]
    total_juros = df_resultados['Total em Juros'].iloc[-1]

    st.header("Dashboard de Projeção Financeira")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'<div class="metric-card"><div class="stMetric"><label>Capital Final Projetado</label> <div data-testid="stMetricValue">R$ {valor_final_acumulado:,.2f}</div></div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card"><div class="stMetric"><label>Total de Capital Alocado</label> <div data-testid="stMetricValue">R$ {total_investido:,.2f}</div></div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-card metric-card-growth"><div class="stMetric"><label>Crescimento (Lucro de Juros)</label> <div data-testid="stMetricValue" style="color: #31d7a2;">R$ {total_juros:,.2f}</div></div></div>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.header("Análise de Crescimento e Composição Patrimonial")
    fig_evolucao = go.Figure()
    fig_evolucao.add_trace(go.Scatter(x=df_resultados['Ano'], y=df_resultados['Total Investido'], fill='tozeroy', mode='lines', name='Capital Alocado', line=dict(color='#58a6ff')))
    fig_evolucao.add_trace(go.Scatter(x=df_resultados['Ano'], y=df_resultados['Total Acumulado'], fill='tonexty', mode='lines', name='Lucro de Juros', line=dict(color='#31d7a2')))
    fig_evolucao.update_layout(template="plotly_dark", title_text='Crescimento Patrimonial ao Longo do Tempo', xaxis_title='Anos de Investimento', yaxis_title='Valor (R$)', hovermode="x unified", legend=dict(x=0.01, y=0.98), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=500)
    st.plotly_chart(fig_evolucao, use_container_width=True)
    st.header("Relatório Detalhado e Exportação de Dados")
    with st.expander("Visualizar relatório tabular detalhado"):
        st.dataframe(df_resultados.style.format({"Total Acumulado": "R$ {:,.2f}", "Total Investido": "R$ {:,.2f}", "Total em Juros": "R$ {:,.2f}"}), use_container_width=True)
        csv_data = convert_df_to_csv(df_resultados)
        st.download_button(label="📥 Exportar Relatório para CSV (Excel)", data=csv_data, file_name=f'projecao_capital_{periodo_anos}_anos.csv', mime='text/csv')

else:
    st.subheader("Bem-vindo à Plataforma de Projeção de Capital")
    col1, col2 = st.columns(2)
    with col1:
        st.info("**Comece Agora:** ⚙️", icon="💡")
        st.markdown("Utilize o **Painel de Controle Estratégico** à esquerda para inserir as variáveis da sua projeção.")
    with col2:
        st.info("**Análise Profunda:** 🔬", icon="📊")
        st.markdown("Após a execução, explore o dashboard, analise os gráficos de crescimento e exporte os dados para relatórios.")

st.markdown("---")
st.markdown("<div class='footer'>Desenvolvido por <strong>Roniel Antonio de Araújo</strong> para Aplicações Corporativas de Alta Performance.</div>", unsafe_allow_html=True)
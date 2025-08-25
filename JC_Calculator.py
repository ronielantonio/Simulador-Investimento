import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from PIL import Image
import math

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
    st.error("Erro: Arquivos de imagem ('Image_01.png', 'Image_02.png') não encontrados.")
    st.stop()

# --- CSS: Estilos da Página ---
st.markdown("""
<style>
    /* CSS permanece idêntico ao anterior */
    [data-testid="stAppViewContainer"] > .main { background-image: linear-gradient(to bottom, #0d1117 0%, #1c2a3f 100%); }
    .subtitle { color: #a1aab4; font-size: 1.1em; }
    h1, h2, h3 { color: #58a6ff; }
    h1 { border-bottom: 2px solid #30363d; padding-bottom: 10px; }
    [data-testid="stSidebar"] { background-color: #161b22; border-right: 1px solid #30363d; }
    [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { color: #FFFFFF !important; }
    [data-testid="stSidebar"] label { color: #F0F0F0 !important; }
    [data-testid="stSidebar"] .stTooltipIcon { color: #a1aab4 !important; }
    .stButton>button {
        background-image: linear-gradient(to right, #58a6ff, #31d7a2); color: #FFFFFF; border: none;
        border-radius: 8px; padding: 12px 24px; font-weight: bold; font-size: 16px;
        transition: all 0.3s ease; box-shadow: 0 4px 15px 0 rgba(49, 215, 162, 0.4);
    }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 8px 25px 0 rgba(88, 166, 255, 0.5); }
    .metric-card {
        background-color: rgba(22, 27, 34, 0.5); border-radius: 12px; padding: 25px;
        border: 1px solid #30363d; border-left: 6px solid #58a6ff;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2); margin-bottom: 10px;
    }
    .metric-card-growth { border-left-color: #31d7a2; }
    .metric-card .stMetric { background-color: transparent; border: none; padding: 0; }
    .footer { text-align: center; color: #a1aab4; }
    .result-card {
        background-color: #1c2a3f; border: 1px solid #58a6ff; border-radius: 12px;
        padding: 20px; text-align: center;
    }
    .result-card h3 { color: #FFFFFF; margin-bottom: 10px; }
    .result-card p { color: #31d7a2; font-size: 2.5em; font-weight: bold; margin: 0; }
    [data-testid="stSidebar"] [data-testid="stRadio"] label p {
        color: #F0F0F0 !important;
    }
</style>
""", unsafe_allow_html=True)


# --- FUNÇÕES DE CÁLCULO (BACKEND) ---
# ATENÇÃO: Todas as funções foram atualizadas para incluir o 'aporte_anual'.

def simular_crescimento(investimento_inicial, aporte_mensal, aporte_anual, taxa_anual, prazo_meses):
    """Motor de cálculo base que simula o crescimento mês a mês."""
    taxa_mensal = (1 + taxa_anual / 100)**(1/12) - 1
    valor_acumulado = float(investimento_inicial)
    
    for mes in range(1, int(prazo_meses) + 1):
        valor_acumulado *= (1 + taxa_mensal)
        valor_acumulado += float(aporte_mensal)
        if mes % 12 == 0:
            valor_acumulado += float(aporte_anual)
    return valor_acumulado

def calcular_valor_resgate(investimento_inicial, aporte_mensal, aporte_anual, prazo_meses, taxa_anual):
    """Usa o motor de simulação para calcular o valor final."""
    return simular_crescimento(investimento_inicial, aporte_mensal, aporte_anual, taxa_anual, prazo_meses)

def calcular_investimento_mensal(valor_resgate, investimento_inicial, aporte_anual, prazo_meses, taxa_anual):
    """Usa busca binária para encontrar o aporte mensal necessário."""
    if prazo_meses <= 0: return float('inf')
    aporte_baixo, aporte_alto, precisao = 0.0, valor_resgate, 0.01
    for _ in range(100):
        aporte_medio = (aporte_baixo + aporte_alto) / 2
        valor_calculado = simular_crescimento(investimento_inicial, aporte_medio, aporte_anual, taxa_anual, prazo_meses)
        if abs(valor_calculado - valor_resgate) < precisao: return aporte_medio
        if valor_calculado < valor_resgate: aporte_baixo = aporte_medio
        else: aporte_alto = aporte_medio
    return aporte_baixo

def calcular_prazo(valor_resgate, investimento_inicial, aporte_mensal, aporte_anual, taxa_anual):
    """Calcula o prazo iterando mês a mês até atingir a meta."""
    if investimento_inicial >= valor_resgate: return 0
    if taxa_anual <= 0 and aporte_mensal <= 0 and aporte_anual <= 0:
        return "Meta inatingível sem juros ou aportes positivos."
    
    taxa_mensal = (1 + taxa_anual / 100)**(1/12) - 1
    valor_acumulado = float(investimento_inicial)
    meses, max_meses = 0, 1200 # Limite de 100 anos
    while valor_acumulado < valor_resgate and meses < max_meses:
        meses += 1
        valor_acumulado *= (1 + taxa_mensal)
        valor_acumulado += float(aporte_mensal)
        if meses % 12 == 0: valor_acumulado += float(aporte_anual)
    return meses if meses < max_meses else "Meta inatingível em 100 anos."

def calcular_investimento_inicial(valor_resgate, aporte_mensal, aporte_anual, prazo_meses, taxa_anual):
    """Calcula o valor futuro das contribuições e o desconta do valor final."""
    fv_contribuicoes = simular_crescimento(0, aporte_mensal, aporte_anual, taxa_anual, prazo_meses)
    fv_necessario_do_inicial = valor_resgate - fv_contribuicoes
    taxa_mensal = (1 + taxa_anual / 100)**(1/12) - 1
    if (1 + taxa_mensal) == 0: return float('inf')
    return fv_necessario_do_inicial / ((1 + taxa_mensal) ** prazo_meses)

def calcular_taxa_juros(valor_resgate, investimento_inicial, aporte_mensal, aporte_anual, prazo_meses):
    """Usa busca binária com o motor de simulação para encontrar a taxa."""
    if prazo_meses <= 0: return "O prazo deve ser maior que zero."
    total_investido_sem_juros = investimento_inicial + (aporte_mensal * prazo_meses) + (aporte_anual * (prazo_meses // 12))
    if total_investido_sem_juros >= valor_resgate: return "Meta alcançada mesmo com taxa zero ou negativa."
    
    taxa_baixa, taxa_alta, precisao = 0.0, 1000.0, 1e-5
    for _ in range(100):
        taxa_media = (taxa_baixa + taxa_alta) / 2
        valor_calculado = simular_crescimento(investimento_inicial, aporte_mensal, aporte_anual, taxa_media, prazo_meses)
        if abs(valor_calculado - valor_resgate) < precisao: return taxa_media
        if valor_calculado < valor_resgate: taxa_baixa = taxa_media
        else: taxa_alta = taxa_media
    return taxa_baixa

def calcular_projecao_detalhada(investimento_inicial, aporte_mensal, aporte_anual, taxa_juros_anual, periodo_anos):
    """Gera o DataFrame detalhado, agora incluindo o aporte anual."""
    taxa_juros_mensal = (1 + taxa_juros_anual / 100)**(1/12) - 1
    dados = []
    valor_final = investimento_inicial
    total_investido = investimento_inicial
    for mes in range(1, int(periodo_anos * 12) + 1):
        juros_do_mes = valor_final * taxa_juros_mensal
        valor_final += juros_do_mes + aporte_mensal
        total_investido += aporte_mensal
        if mes % 12 == 0 and mes > 0:
            valor_final += aporte_anual
            total_investido += aporte_anual
        dados.append({
            'Mês': mes, 'Ano': ((mes-1)//12) + 1, 'Total Acumulado': valor_final,
            'Total Investido': total_investido, 'Total em Juros': valor_final - total_investido
        })
    return pd.DataFrame(dados)

@st.cache_data
def convert_df_to_csv(df):
    return df.to_csv(index=False, decimal=',', sep=';').encode('latin1')

# --- INTERFACE (FRONTEND) ---

with st.sidebar:
    st.image(img_sidebar, use_container_width=True)
    st.header("Painel de Controle Estratégico")

    modo_calculo = st.radio(
        "O que você quer calcular?",
        ("Valor de Resgate", "Investimento Mensal", "Prazo", "Investimento Inicial", "Taxa de Juros"),
        key="modo_calculo"
    )
    st.divider()

    # ADIÇÃO: O campo de aporte anual foi inserido aqui.
    if modo_calculo != "Investimento Inicial":
        investimento_inicial = st.number_input("💵 Capital Inicial (R$)", min_value=0.0, value=10000.0, step=1000.0)
    if modo_calculo != "Investimento Mensal":
        aporte_mensal = st.number_input("🗓️ Aporte Mensal (R$)", min_value=0.0, value=1500.0, step=100.0)
    
    # O aporte anual é um input em todos os cenários de cálculo.
    aporte_anual = st.number_input("🎉 Aporte Anual Extra (R$)", min_value=0.0, value=0.0, step=500.0, help="Aporte adicional feito ao final de cada período de 12 meses.")
    
    if modo_calculo != "Taxa de Juros":
        taxa_periodo = st.radio("Período da Taxa", ["Anual", "Mensal"], horizontal=True)
        taxa_juros_input = st.number_input(f"📈 Rentabilidade ({taxa_periodo}) (%)", min_value=0.0, value=12.0 if taxa_periodo == "Anual" else 1.0, step=0.1, format="%.2f")

    if modo_calculo != "Prazo":
        st.markdown('<p style="color: #F0F0F0;">⏳ Horizonte de Tempo</p>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            periodo_anos = st.number_input("Anos", min_value=0, value=10, step=1)
        with col2:
            periodo_meses_extra = st.number_input("Meses", min_value=0, max_value=11, value=0, step=1)
        prazo_meses = (periodo_anos * 12) + periodo_meses_extra

    if modo_calculo != "Valor de Resgate":
        valor_resgate = st.number_input("🎯 Valor de Resgate (Meta) (R$)", min_value=0.0, value=1000000.0, step=50000.0)
    
    st.divider()
    calcular = st.button("Executar Projeção Estratégica", use_container_width=True)

# --- TELA PRINCIPAL: O DASHBOARD ---
st.title("Plataforma de Projeção Estratégica de Capital")
st.markdown('<p class="subtitle">Uma ferramenta completa para projeções, metas e simulações de investimentos.</p>', unsafe_allow_html=True) 
st.image(img_banner, use_container_width=True)
st.markdown("---")

# --- ÁREA DE RESULTADOS DINÂMICOS ---
if calcular:
    if modo_calculo != "Taxa de Juros":
        taxa_juros_anual = ((1 + taxa_juros_input / 100) ** 12 - 1) * 100 if taxa_periodo == "Mensal" else taxa_juros_input

    resultado_texto = ""
    try:
        # ATUALIZAÇÃO: Todas as chamadas agora passam o 'aporte_anual'
        if modo_calculo == "Valor de Resgate":
            resultado = calcular_valor_resgate(investimento_inicial, aporte_mensal, aporte_anual, prazo_meses, taxa_juros_anual)
            resultado_texto = f"R$ {resultado:,.2f}"
            periodo_anos_proj = prazo_meses / 12

        elif modo_calculo == "Investimento Mensal":
            resultado = calcular_investimento_mensal(valor_resgate, investimento_inicial, aporte_anual, prazo_meses, taxa_juros_anual)
            resultado_texto = f"R$ {resultado:,.2f} / mês"
            aporte_mensal = resultado
            periodo_anos_proj = prazo_meses / 12

        elif modo_calculo == "Prazo":
            resultado = calcular_prazo(valor_resgate, investimento_inicial, aporte_mensal, aporte_anual, taxa_juros_anual)
            if isinstance(resultado, str): raise ValueError(resultado)
            anos, meses = divmod(math.ceil(resultado), 12)
            resultado_texto = f"{anos} anos e {meses} meses"
            periodo_anos_proj = resultado / 12

        elif modo_calculo == "Investimento Inicial":
            resultado = calcular_investimento_inicial(valor_resgate, aporte_mensal, aporte_anual, prazo_meses, taxa_juros_anual)
            resultado_texto = f"R$ {resultado:,.2f}"
            investimento_inicial = resultado
            periodo_anos_proj = prazo_meses / 12

        elif modo_calculo == "Taxa de Juros":
            resultado = calcular_taxa_juros(valor_resgate, investimento_inicial, aporte_mensal, aporte_anual, prazo_meses)
            if isinstance(resultado, str): raise ValueError(resultado)
            taxa_mensal_eq = ((1 + resultado/100)**(1/12) - 1) * 100
            resultado_texto = f"{resultado:.2f}% a.a. (ou {taxa_mensal_eq:.4f}% a.m.)"
            taxa_juros_anual = resultado
            periodo_anos_proj = prazo_meses / 12
    
        st.header(f"Resultado do Cálculo: {modo_calculo}")
        st.markdown(f'<div class="result-card"><h3>{modo_calculo} Necessário</h3><p>{resultado_texto}</p></div>', unsafe_allow_html=True)
        st.markdown("---")

        st.header("Dashboard de Projeção Financeira")
        df_resultados = calcular_projecao_detalhada(investimento_inicial, aporte_mensal, aporte_anual, taxa_juros_anual, periodo_anos_proj)
        
        if not df_resultados.empty:
            valor_final_acumulado = df_resultados['Total Acumulado'].iloc[-1]
            total_investido = df_resultados['Total Investido'].iloc[-1]
            total_juros = df_resultados['Total em Juros'].iloc[-1]

            col1, col2, col3 = st.columns(3)
            with col1: st.markdown(f'<div class="metric-card"><div class="stMetric"><label>Capital Final Projetado</label> <div data-testid="stMetricValue">R$ {valor_final_acumulado:,.2f}</div></div></div>', unsafe_allow_html=True)
            with col2: st.markdown(f'<div class="metric-card"><div class="stMetric"><label>Total de Capital Alocado</label> <div data-testid="stMetricValue">R$ {total_investido:,.2f}</div></div></div>', unsafe_allow_html=True)
            with col3: st.markdown(f'<div class="metric-card metric-card-growth"><div class="stMetric"><label>Crescimento (Lucro de Juros)</label> <div data-testid="stMetricValue" style="color: #31d7a2;">R$ {total_juros:,.2f}</div></div></div>', unsafe_allow_html=True)
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
                st.download_button(label="📥 Exportar Relatório para CSV (Excel)", data=csv_data, file_name=f'projecao_capital.csv', mime='text/csv')

    except (ValueError, Exception) as e:
        st.error(f"Não foi possível concluir o cálculo: {e}")

else:
    st.subheader("Bem-vindo à Plataforma de Projeção de Capital")
    col1, col2 = st.columns(2)
    with col1: st.info("**Comece Agora:** ⚙️", icon="💡")
    with col2: st.info("**Análise Profunda:** 🔬", icon="📊")
    st.markdown("""
    <div style="grid-column: 1 / -1;">
    Utilize o <b>Painel de Controle</b> à esquerda para escolher o que deseja calcular e inserir as variáveis da sua projeção. Após a execução, veja o resultado principal, explore o dashboard, analise os gráficos de crescimento e exporte os dados.
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.markdown("<div class='footer'>Desenvolvido por <strong>Roniel Antonio de Araújo</strong> para Aplicações Corporativas de Alta Performance.</div>", unsafe_allow_html=True)

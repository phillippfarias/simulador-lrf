import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ----------------------
# Configuração inicial
# ----------------------
st.set_page_config(page_title="Simulador de Despesa com Pessoal (LRF)", layout="wide")

st.title("Simulador de Despesa com Pessoal (LRF) - Limites Máximo/Prudencial/Alerta")

# ----------------------
# Entradas iniciais
# ----------------------
st.sidebar.header("Parâmetros Atuais")
receita_atual = st.sidebar.number_input("Receita Corrente Líquida (R$)", value=1000000.0, step=10000.0)
despesa_atual = st.sidebar.number_input("Despesa com Pessoal Atual (R$)", value=520000.0, step=10000.0)

st.sidebar.header("Simulações")
delta_receita = st.sidebar.number_input("Variação Receita (%)", value=0.0, step=1.0)
delta_despesa = st.sidebar.number_input("Variação Despesa (%)", value=0.0, step=1.0)

# ----------------------
# Cálculos
# ----------------------
# Receita e despesa simuladas
receita_simulada = receita_atual * (1 + delta_receita/100)
despesa_simulada = despesa_atual * (1 + delta_despesa/100)

# Percentuais
perc_atual = despesa_atual / receita_atual * 100
perc_simulado = despesa_simulada / receita_simulada * 100

# Limites
limite_max = 60
limite_prud = 57
limite_alerta = 54

# ----------------------
# Tabela comparativa
# ----------------------
df = pd.DataFrame({
    "Situação": ["Atual", "Simulada"],
    "Receita (R$)": [receita_atual, receita_simulada],
    "Despesa (R$)": [despesa_atual, despesa_simulada],
    "% Despesa/Receita": [perc_atual, perc_simulado]
})
st.subheader("Resumo Atual x Simulado")
st.dataframe(df.style.format({"Receita (R$)": "R$ {:,.2f}", "Despesa (R$)": "R$ {:,.2f}", "% Despesa/Receita": "{:.2f}%"}))

# ----------------------
# Gráfico Gauge - situação atual
# ----------------------
st.subheader("Situação Atual e Simulada")
col1, col2 = st.columns(2)

with col1:
    gauge_atual = go.Figure(go.Indicator(
        mode="gauge+number",
        value=perc_atual,
        title={'text': "Atual"},
        gauge={'axis': {'range': [0, 100]},
               'steps': [
                   {'range': [0, limite_alerta], 'color': "lightgreen"},
                   {'range': [limite_alerta, limite_prud], 'color': "yellow"},
                   {'range': [limite_prud, limite_max], 'color': "orange"},
                   {'range': [limite_max, 100], 'color': "red"}]}
    ))
    st.plotly_chart(gauge_atual, use_container_width=True)

with col2:
    gauge_sim = go.Figure(go.Indicator(
        mode="gauge+number",
        value=perc_simulado,
        title={'text': "Simulado"},
        gauge={'axis': {'range': [0, 100]},
               'steps': [
                   {'range': [0, limite_alerta], 'color': "lightgreen"},
                   {'range': [limite_alerta, limite_prud], 'color': "yellow"},
                   {'range': [limite_prud, limite_max], 'color': "orange"},
                   {'range': [limite_max, 100], 'color': "red"}]}
    ))
    st.plotly_chart(gauge_sim, use_container_width=True)

# ----------------------
# Gráfico comparativo de barras
# ----------------------
st.subheader("Comparativo de Receita e Despesa")
bar = go.Figure(data=[
    go.Bar(name="Receita", x=["Atual", "Simulado"], y=[receita_atual, receita_simulada], marker_color="green"),
    go.Bar(name="Despesa", x=["Atual", "Simulado"], y=[despesa_atual, despesa_simulada], marker_color="red")
])
bar.update_layout(barmode='group')
st.plotly_chart(bar, use_container_width=True)

# ----------------------
# Cálculo de ajustes necessários
# ----------------------
def calc_ajuste(limite, receita, despesa):
    max_despesa = receita * limite / 100
    if despesa <= max_despesa:
        return "OK", 0, 0
    else:
        reducao = despesa - max_despesa
        perc_reducao = reducao / despesa * 100
        return "Excedido", reducao, perc_reducao

st.subheader("Ajustes Necessários (Simulação)")
for nome, limite in {"Alerta": limite_alerta, "Prudencial": limite_prud, "Máximo": limite_max}.items():
    status, reducao, perc_reducao = calc_ajuste(limite, receita_simulada, despesa_simulada)
    if status == "OK":
        st.success(f"{nome}: Dentro do limite.")
    else:
        st.error(f"{nome}: Excedido. Necessário reduzir R$ {reducao:,.2f} ({perc_reducao:.2f}%).")

#   BLOQUE 2 · Análisis mediante la visualización de los datos del bloque 1


import streamlit as st
import pandas as pd
import plotly.express as px

# Primero leemos los ficheros xlsx donde están los datos limpios del bloqeu anterior

df_eventos = pd.read_excel("eventosWC26.xlsx")
df_jugadores = pd.read_excel("jugadoresWC26.xlsx")
df_partidos = pd.read_excel("partidosWC26.xlsx")


st.title("Análisis Mundial 2026")  # Ponemos el titulo de nuestra UI

# 1. ANÁLISIS 1: VENTANAS DE PARTIDOS

st.header("Análisis 1: Ventanas de partidos")

# 1.1 Gráfico de barras de eventos de un partido.

st.subheader("1.1 Eventos de un partido")
partido = st.selectbox("Elige un partido", df_partidos["partido"].unique())
df_partido_concreto = df_partidos[df_partidos["partido"] == partido].copy()
df_partido_concreto["cantidad"] = 1

fig = px.bar(df_partido_concreto,x="minuto",y="cantidad",color="tipo_evento",hover_name="jugador",hover_data={"minuto": True,"tipo_evento": True,
    "cantidad": False},title=f"Eventos del partido: {partido}",labels={"minuto": "Minuto de partido", "tipo_evento": "Tipo de evento"})
fig.update_layout(xaxis=dict(range=[0, 120]), yaxis_visible=False)
st.plotly_chart(fig, use_container_width=True)


# 1.2 Mapa de calor de densidad de eventos

st.subheader("Densidad de eventos a lo largo del partido")

fig2 = px.density_heatmap(d,x="minuto",y="tipo_evento",nbinsx=24,range_x=[0, 120],color_continuous_scale="YlOrRd",labels={"minuto": "Minuto de partido", "tipo_evento": "Tipo de evento"},title="Densidad de eventos por minuto")
st.plotly_chart(fig2, use_container_width=True)
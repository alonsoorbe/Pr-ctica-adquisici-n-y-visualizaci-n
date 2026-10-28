#   BLOQUE 2 · Análisis mediante la visualización de los datos del bloque 1


import streamlit as st
import pandas as pd
import plotly.express as px

# Primero leemos los ficheros xlsx donde están los datos limpios del bloqeu anterior

eventos = pd.read_excel("eventosWC26.xlsx")
jugadores = pd.read_excel("jugadoresWC2026.xlsx")
partidos = pd.read_excel("partidosWC26.xlsx")

# Inicaciamos nuestra UI poniendo titulo

st.set_page_config(page_title="Mundial 2026", layout="wide")
st.title("Análisis 1: Ventanas de partidos")

 # ANÁLISIS 1: Ventanas de partidos
 
# Cada evento recibe la ronda y las dos selecciones de su partido
eventos = eventos.merge(partidos[["index_partido", "ronda", "seleccion_local", "seleccion_visitante"]],
        on="index_partido",how="left")
 
partidos["partido"] = partidos["seleccion_local"] + " vs " + partidos["seleccion_visitante"]
 
 
# 1. Eventos de un partido

st.header("1. Eventos de un partido")
partido = st.selectbox("Partido", partidos["partido"])
num_partido = partidos.loc[partidos["partido"] == partido, "index_partido"].iloc[0]
 
datos1 = eventos[eventos["index_partido"] == num_partido].copy()
datos1["eventos"] = 1
 
fig1 = px.bar(datos1,x="minuto_evento",y="eventos",color="tipo_evento",hover_data=["nombre_jugador", "minuto_evento"],range_x=[0, 125],title=f"Eventos del partido {partido}",
              labels={    "minuto_evento": "Minuto",    "eventos": "Eventos",    "tipo_evento": "Tipo de evento",    "nombre_jugador": "Jugador"})
st.plotly_chart(fig1, width="stretch")
 
 
# 2. Mapa de calor
st.header("2. Densidad de eventos a lo largo del partido")
 
c1, c2 = st.columns(2)
tipos = c1.multiselect("Tipo de evento", eventos["tipo_evento"].unique(),default=eventos["tipo_evento"].unique())
rondas = c2.multiselect("Ronda", partidos["ronda"].unique(),default=partidos["ronda"].unique())
 
datos2 = eventos[eventos["tipo_evento"].isin(tipos) & eventos["ronda"].isin(rondas)].copy()
datos2["intervalo"] = (datos2["minuto_evento"] // 5 * 5).astype(int)   # tramos de 5 minutos
 
matriz = datos2.pivot_table(index="tipo_evento",columns="intervalo",values="index_evento",aggfunc="count",fill_value=0)
 
fig2 = px.imshow(matriz,text_auto=True,aspect="auto",color_continuous_scale="YlOrRd",title="Número de eventos cada 5 minutos",labels={"x": "Minuto", "y": "Tipo de evento", "color": "Eventos"})
st.plotly_chart(fig2, width="stretch")
 
 
# 3. Eventos de una selección
st.header("3. Eventos de una selección")
 
seleccion = st.selectbox("Selección", sorted(eventos["seleccion_evento"].unique()))
 
juega = (eventos["seleccion_local"] == seleccion) | (eventos["seleccion_visitante"] == seleccion)
datos3 = eventos[juega].copy()
 
datos3["lado"] = "en contra"
datos3.loc[datos3["seleccion_evento"] == seleccion, "lado"] = "a favor"
datos3["categoria"] = datos3["tipo_evento"] + " " + datos3["lado"]
 
reparto = datos3["categoria"].value_counts().reset_index()
 
fig3 = px.pie(reparto,names="categoria",values="count",hole=0.4,title=f"Eventos en los partidos de {seleccion}")
fig3.update_traces(textinfo="label+value")
st.plotly_chart(fig3, width="stretch")




# ANÁLISIS 2: Rendimiento de jugadores clave
 
st.title("Análisis 2: Rendimiento de jugadores clave")
 
selecciones = ["Todas"] + sorted(jugadores["seleccion_nacional"].unique())
posiciones = jugadores["posicion"].unique()
 
# Ranking de valor de mercado primero el más caro
jugadores = jugadores.sort_values("valor_mercado", ascending=False)
jugadores["ranking_valor"] = range(1, len(jugadores) + 1) 
 
# 4. Valor de mercado vs calificación media
 
st.header("4. Valor de mercado y calificación media")
 
c1, c2, c3 = st.columns(3)
seleccion4 = c1.selectbox("Selección", selecciones, key="seleccion4")
partidos4 = c2.slider("Partidos jugados (mínimo)", min_value=1, max_value=8, value=1)
posiciones4 = c3.multiselect("Posición", posiciones, default=posiciones, key="posicion4")
 
datos4 = jugadores[(jugadores["minutos_jugados"] >= 180) & (jugadores["partidos_jugados"] >= partidos4)& jugadores["posicion"].isin(posiciones4)]

if seleccion4 != "Todas":
    datos4 = datos4[datos4["seleccion_nacional"] == seleccion4]
 
correlacion = datos4["valor_mercado"].corr(datos4["calificacion_media"])
st.metric("Correlación valor de mercado - calificación", f"{correlacion:.2f}")
 
fig4 = px.scatter(datos4,x="valor_mercado",y="calificacion_media",color="posicion",hover_data=["nombre_jugador", "seleccion_nacional", "partidos_jugados"],title="Valor de mercado frente a calificación media (mínimo 180 minutos)",
                  labels={"valor_mercado": "Valor de mercado (M€)", "calificacion_media": "Calificación media", "posicion": "Posición", "nombre_jugador": "Jugador", "seleccion_nacional": "Selección", "partidos_jugados": "Partidos jugados"})
st.plotly_chart(fig4, width="stretch")
 
 
# 5. Top 15 por métrica
 
st.header("5. Top 15 jugadores por métrica")
 
datos5 = jugadores[jugadores["minutos_jugados"] >= 180].copy()   # mismo mínimo que en el apartado 4
 
datos5["goles/minuto"] = datos5["goles"] / datos5["minutos_jugados"]
datos5["goles+asistencias/minuto"] = (datos5["goles"] + datos5["asistencias"]) / datos5["minutos_jugados"]
datos5["asistencias/minuto"] = datos5["asistencias"] / datos5["minutos_jugados"]
datos5["goles_concedidos/minuto"] = datos5["goles_concedidos"] / datos5["minutos_jugados"]
datos5["tarjetas_amarillas/minuto"] = datos5["tarjetas_amarillas"] / datos5["minutos_jugados"]
datos5["tarjetas_rojas/minuto"] = datos5["tarjetas_rojas"] / datos5["minutos_jugados"]
 
# Suma lo bueno y resta lo malo, con distinto peso
datos5["metrica_agregada"] = (3 * datos5["goles/minuto"] + 2 * datos5["asistencias/minuto"]- 1 * datos5["goles_concedidos/minuto"]
                              - 0.5 * datos5["tarjetas_amarillas/minuto"]- 2 * datos5["tarjetas_rojas/minuto"])
 
metricas = ["metrica_agregada", "goles/minuto", "goles+asistencias/minuto", "asistencias/minuto",
            "goles_concedidos/minuto", "tarjetas_amarillas/minuto", "tarjetas_rojas/minuto"]
metrica = st.selectbox("Métrica", metricas)
 
top15 = datos5.sort_values(metrica, ascending=False).head(15).copy()
top15["ranking"] = top15["ranking_valor"].astype(str) + "º"
 
fig5 = px.bar(top15,x=metrica,y="nombre_jugador",orientation="h",text="ranking",hover_data=["seleccion_nacional", "valor_mercado"],title=f"Top 15 en {metrica} (el número es su ranking en valor de mercado)",
              labels={"nombre_jugador": "Jugador", "seleccion_nacional": "Selección", "valor_mercado": "Valor de mercado (M€)"})
fig5.update_layout(yaxis={"categoryorder": "total ascending"})   # el mejor arriba
st.plotly_chart(fig5, width="stretch")
 
 
# 6. Gráfico de burbujas
 
st.header("6. Minutos, calificación y valor de mercado")
 
c1, c2 = st.columns(2)
seleccion6 = c1.selectbox("Selección", selecciones, key="seleccion6")
posiciones6 = c2.multiselect("Posición", posiciones, default=posiciones, key="posicion6")
 
datos6 = jugadores[(jugadores["minutos_jugados"] > 0) & jugadores["posicion"].isin(posiciones6)].copy()
if seleccion6 != "Todas":
    datos6 = datos6[datos6["seleccion_nacional"] == seleccion6]
 
datos6["ha_marcado"] = "No"
datos6.loc[datos6["goles"] > 0, "ha_marcado"] = "Sí"
  
fig6 = px.scatter(datos6, x="minutos_jugados", y="calificacion_media", size ="valor_mercado", color="ha_marcado", color_discrete_map={"Sí": "red", "No": "lightgray"}, hover_data=["nombre_jugador", "seleccion_nacional", "goles", "valor_mercado"], title="Minutos jugados, calificación media y valor de mercado (tamaño)",
                  labels={"minutos_jugados": "Minutos jugados", "calificacion_media": "Calificación media", "ha_marcado": "Ha marcado", "nombre_jugador": "Jugador", "seleccion_nacional": "Selección", "valor_mercado": "Valor de mercado (M€)"})
st.plotly_chart(fig6, width="stretch")
 
 
# ANÁLISIS 3: Impacto arbitral
 
st.title("Análisis 3: Impacto arbitral")
 
orden_rondas = ["Fase de grupos", "Dieciseisavos", "Octavos", "Cuartos", "Semifinal", "Tercer puesto", "Final"]
 
 
# 7. Tarjetas por partido y ronda
 
st.header("7. Tarjetas por partido en cada ronda")
 
tarjetas = eventos[eventos["tipo_evento"].isin(["Tarjeta amarilla", "Tarjeta roja"])]
tarjetas_partido = tarjetas.groupby("index_partido").agg(tarjetas=("index_evento", "count")).reset_index()
 
datos7 = partidos.merge(tarjetas_partido, on="index_partido", how="left")
datos7["tarjetas"] = datos7["tarjetas"].fillna(0)   # partidos sin tarjetas
 
fig7 = px.box(datos7,x="ronda",y="tarjetas",points="all",hover_data=["partido", "arbitro_partido"],category_orders={"ronda": orden_rondas},title="Número de tarjetas por partido según la ronda",
              labels={"ronda": "Ronda", "tarjetas": "Tarjetas", "partido": "Partido", "arbitro_partido": "Árbitro"})
st.plotly_chart(fig7, width="stretch")
 
 
# 8. Índice de Intervención Arbitral
 
st.header("8. Índice de Intervención Arbitral")
 
puntos = {"Tarjeta amarilla": 1, "Tarjeta roja": 3, "Revisión VAR": 1, "Gol": 0.2}
eventos["puntos"] = eventos["tipo_evento"].map(puntos).fillna(0)   # el resto de eventos no suma
 
indice_partido = eventos.groupby("index_partido").agg(indice=("puntos", "sum")).reset_index()
indice = partidos.merge(indice_partido, on="index_partido", how="left")
indice["indice"] = indice["indice"].fillna(0)
 
c1, c2 = st.columns(2)
rondas8 = c1.multiselect("Ronda", orden_rondas, default=orden_rondas, key="ronda8")
seleccion8 = c2.selectbox("Selección", selecciones, key="seleccion8")
 
datos8 = indice[indice["ronda"].isin(rondas8)]
if seleccion8 != "Todas":
    datos8 = datos8[(datos8["seleccion_local"] == seleccion8) | (datos8["seleccion_visitante"] == seleccion8)]
 
# Un punto por partido y otro con la media de cada árbitro
medias = datos8.groupby("arbitro_partido").agg(indice=("indice", "mean")).reset_index()
medias["tipo"] = "Media del árbitro"
medias["partido"] = "Media"
 
puntos_partido = datos8[["arbitro_partido", "indice", "partido"]].copy()
puntos_partido["tipo"] = "Partido"
 
datos_grafico = pd.concat([puntos_partido, medias], ignore_index=True)
orden_arbitros = medias.sort_values("indice")["arbitro_partido"]   # de menos a más severo
 
fig8 = px.scatter(datos_grafico,x="indice",y="arbitro_partido",color="tipo",symbol="tipo",hover_data=["partido"],category_orders={"arbitro_partido": list(orden_arbitros)},height=900,title="Índice de Intervención Arbitral por árbitro",
                  labels={"indice": "Índice de Intervención Arbitral", "arbitro_partido": "Árbitro", "tipo": "", "partido": "Partido"})
st.plotly_chart(fig8, width="stretch")
 
if seleccion8 != "Todas":
    st.subheader(f"Árbitros de los partidos de {seleccion8}")
    st.dataframe(datos8.sort_values("indice")[["partido", "ronda", "arbitro_partido", "indice"]], width="stretch")
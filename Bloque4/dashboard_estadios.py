
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Estadios del Mundial 2026", layout="wide")
st.title("Estadios del Mundial 2026")
st.caption("Partidos y goles por estadio - Localización: OpenStreetMap")

ORDEN_RONDAS = ["Fase de grupos", "Dieciseisavos", "Octavos", "Cuartos", "Semifinal", "Tercer puesto", "Final"]


def buscar_fichero(nombre):
    aqui = Path(__file__).parent
    for carpeta in [aqui, aqui.parent, aqui / "datos", aqui.parent / "datos", Path(".")]:
        if (carpeta / nombre).exists():
            return carpeta / nombre
    raise FileNotFoundError(nombre)


partidos = pd.read_excel(buscar_fichero("partidosWC26.xlsx"))
coordenadas = pd.read_excel(buscar_fichero("estadios_WC26_coordenadas.xlsx"))
partidos["goles"] = partidos["marcador_local"] + partidos["marcador_visitante"]

# Selector de ronda
st.sidebar.header("Filtros")
rondas = st.sidebar.multiselect("Ronda", ORDEN_RONDAS, default=ORDEN_RONDAS)

vista = partidos[partidos["ronda"].isin(rondas)]
if vista.empty:
    st.warning("Selecciona al menos una ronda.")
    st.stop()

# Partidos y goles por estadio después de filtrar
por_estadio = vista.groupby("estadio").agg(partidos=("index_partido", "count"),goles=("goles", "sum")).reset_index()
por_estadio["goles_por_partido"] = (por_estadio["goles"] / por_estadio["partidos"]).round(2)
mapa = por_estadio.merge(coordenadas[["estadio", "ciudad", "pais", "latitud", "longitud"]], on="estadio", how="left")

# Métricas
c1, c2, c3 = st.columns(3)
c1.metric("Partidos", int(mapa["partidos"].sum()))
c2.metric("Goles", int(mapa["goles"].sum()))
c3.metric("Goles por partido", f"{mapa['goles'].sum() / mapa['partidos'].sum():.2f}")

# Mapa de burbujas
fig = px.scatter_map(mapa, lat="latitud", lon="longitud",
                     size="partidos", color="goles", hover_name="estadio",
                     hover_data=["ciudad", "partidos", "goles"],
                     color_continuous_scale="YlOrRd", size_max=40,
                     center={"lat": 36, "lon": -98}, zoom=2.6,
                     map_style="carto-positron", height=620)
fig.update_layout(margin=dict(l=0, r=0, t=10, b=0))
st.plotly_chart(fig, width="stretch")

# Tabla
st.subheader("Detalle por estadio")
st.dataframe(mapa.sort_values("partidos", ascending=False)[["estadio", "ciudad", "pais", "partidos", "goles", "goles_por_partido"]],
             width="stretch", hide_index=True)

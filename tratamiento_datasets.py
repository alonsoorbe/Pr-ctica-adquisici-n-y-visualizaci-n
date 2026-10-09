
#   BLOQUE 1 · Recopilación, limpieza y tratamiento de los datasets del Mundial 2026

import pandas as pd
from IPython.display import display
import matplotlib.pyplot as plt
import re
from sklearn.linear_model import LinearRegression


# minutos que consideramos anómalos
MINUTO_MAX_REGLAMENTARIO = 90 + 15
MINUTO_MAX_TANDA = 121

# Traducciones que no se pueden conseguir con los csv
RONDAS = {
    "Group Stage": "Fase de grupos",
    "Round of 32": "Dieciseisavos",
    "Round of 16": "Octavos",
    "Quarter-finals": "Cuartos",
    "Semi-finals": "Semifinal",
    "Third-place match": "Tercer puesto",
    "Final": "Final"}

POSICIONES = {
    "GK": "Portero",
    "DEF": "Defensa",
    "MID": "Centrocampista",
    "FWD": "Delantero"}

TIPOS_EVENTO = {
    "Goal": "Gol",
    "Assist": "Asistencia",
    "Yellow Card": "Tarjeta amarilla",
    "Red Card": "Tarjeta roja",
    "Penalty Shootout Goal": "Penalty marcado",
    "Penalty Shootout Miss": "Penalty fallado",
    "VAR Review": "Revisión VAR",
    "Review VAR": "Revisión VAR"}


# 1. IMPORTACIÓN Y EXPLORACIÓN INICIAL DE LOS DATASETS

#Importamos todos los archivos
eurocopa_fem_stats_df = pd.read_csv("datasetsWC26/2001eurocopa_fem_stats.csv", sep = ",")
match_lineups_df = pd.read_csv("datasetsWC26/2026match_lineups.csv", sep = ";")
match_register_df = pd.read_csv("datasetsWC26/2026match_register.csv", sep = ";")
national_teams_df = pd.read_csv("datasetsWC26/2026nationalteams.csv", sep = ",")
player_stats_df = pd.read_csv("datasetsWC26/2026player_stats.csv", sep = ";")
squads_players_df = pd.read_csv("datasetsWC26/2026squads_and_players.csv", sep = ";")
index_referees_df = pd.read_csv("datasetsWC26/index_referees.csv", sep = ";")
matches_mundial_dos_df = pd.read_csv("datasetsWC26/matches_mundial202.csv", sep = ",")
matches_mundial_seis_df = pd.read_csv("datasetsWC26/matches_mundial2026.csv", sep = ";")
tournament_stages_df = pd.read_csv("datasetsWC26/tournament_stages.csv", sep = ",")
worldcup_venues_df = pd.read_csv("datasetsWC26/worldcup_venues.csv", sep = ";")

# Guardamos los datasets originales en un diccionario para poder explorarlos todos de golpe.
datasets_originales = {
    "2001eurocopa_fem_stats": eurocopa_fem_stats_df,
    "2026match_lineups": match_lineups_df,
    "2026match_register": match_register_df,
    "2026nationalteams": national_teams_df,
    "2026player_stats": player_stats_df,
    "2026squads_and_players": squads_players_df,
    "index_referees": index_referees_df,
    "matches_mundial2022": matches_mundial_dos_df,
    "matches_mundial2026": matches_mundial_seis_df,
    "tournament_stages": tournament_stages_df,
    "worldcup_venues": worldcup_venues_df}


# Primero hacemos una función que nos permite ver y analizar a lo que nos enfrentamos
def exploration(df, nombre):
    """
    Exploración inicial de un DataFrame.

    Muestra por pantalla:
      - Dimensiones (filas, columnas) y número de filas duplicadas exactas
      - Una tabla resumen por columna: tipo de dato, nº de nulos, % de nulos y nº de valores distintos.
      - Una fila aleatoria para ver el formato real de los datos
      - Estadísticas básicas de todas las columnas

    Parámetros
      df     : DataFrame.
      nombre : nombre de df como texto
    """
    print("\n" + "=" * 80)
    print(f"DATASET: {nombre}")
    print("=" * 80)
    print("Dimensiones:", df.shape)
    print("Filas duplicadas:", df.duplicated().sum())
    resumen = pd.DataFrame({"tipo": df.dtypes,"nulos": df.isna().sum(),"% nulos": (df.isna().mean() * 100).round(1),"distintos": df.nunique()})
    print("\n--- Columnas ---")
    display(resumen)
    print("\n--- Filas aleatorias ---")
    display(df.sample())
    print("\n--- Estadísticos ---")
    display(df.describe(include="all"))


# 2. CREACIÓN DE LOS DATAFRAMES PARTIDOS, EVENTOS Y JUGADORES

# Creamos los tres dataframes pedidos vacíos
partidos = pd.DataFrame()
eventos = pd.DataFrame()
jugadores = pd.DataFrame()

# Columnas finales con los nombres que nos piden
caracteristicas_partidos = ["fecha_partido", "ronda", "estadio", "ciudad_partido", "pais_partido", "seleccion_local", "seleccion_visitante", "marcador_local", "marcador_visitante", "prorroga", "penalty_local", "penalty_visitante", "arbitro_partido"]
caracteristicas_jugadores = ["seleccion_nacional", "club_jugador", "partidos_seleccion", "posicion", "valor_mercado", "partidos_jugados", "minutos_jugados", "goles", "asistencias", "tiros", "tarjetas_amarillas", "tarjetas_rojas", "paradas", "goles_concedidos", "calificacion_media"]
caracteristicas_eventos = ["minuto_evento", "index_partido", "nombre_jugador", "tipo_evento", "seleccion_evento"]


# 3. CONSTRUCCIÓN DE LOS DATAFRAMES

# DataFrame de partidos

# Mediante merges, cogeremos DataFrame a DataFrame para ver que relación tiene e ir haciendo merges poco a poco
# Primero cogemos de base el matches_mundial_seis_df, que es el que más datos tiene de los que necesitamos
# Cogeremos ciertos DataFrames basandonos en la info que necesitemos

national_teams_df = national_teams_df.dropna(subset=["team_id"]).drop_duplicates(subset="team_id")
match_register_df = match_register_df.dropna(subset=["match_id"])
match_register_df = match_register_df.drop_duplicates(subset="event_id", keep="first")

# Cogemos los nombres de squads_and_players porque en player_stats los acentos salen mal.
# Si dos jugadores se llaman igual, les añadimos su selección para distinguirlos.
plantilla = squads_players_df.merge(national_teams_df, on="team_id", how="left")
repetidos = plantilla["player_name"].duplicated(keep=False)
plantilla.loc[repetidos, "player_name"] = plantilla["player_name"] + " (" + plantilla["team_name"] + ")"
nombres_correctos = plantilla.set_index("player_id")["player_name"]


# 3.1 DataFrame PARTIDOS

# Base: matches_mundial2026

partidos = matches_mundial_seis_df.merge(index_referees_df, on = "referee_id", how = "left")
partidos = partidos.rename(columns= {"country": "ref_country"})
partidos = partidos.merge(tournament_stages_df, on = "stage_id", how = "left")
partidos = partidos.merge(worldcup_venues_df, on = "venue_id", how = "left")
partidos = partidos.merge(national_teams_df, left_on = "home_team_id", right_on = "team_id", how = "left")
partidos = partidos.rename(columns = {"team_name": "seleccion_local"})
partidos = partidos.merge(national_teams_df, left_on = "away_team_id", right_on = "team_id",how = "left", suffixes=("", "_away"))
partidos = partidos.rename(columns = {"team_name": "seleccion_visitante"})
partidos = partidos.rename(columns ={       #Ponemos los nombres que nos piden
    "date": "fecha_partido",
    "stage_name": "ronda",
    "stadium_name": "estadio",
    "city": "ciudad_partido",
    "country": "pais_partido",
    "home_score": "marcador_local",
    "away_score": "marcador_visitante",
    "home_penalty_score": "penalty_local",
    "away_penalty_score": "penalty_visitante",
    "name": "arbitro_partido"})
partidos["prorroga"] = partidos["result_type"].isin(["AET", "Penalties"])  #Devuelve True si acaba en prorroga o penalties
partidos = partidos.set_index("match_id")
partidos = partidos[caracteristicas_partidos]  #Aplicamos como una "mascara" para quedarnos solo con los que nos interesa
partidos.index.name = "index_partido"

# 3.2 DataFrame JUGADORES

# Base: player_stats
jugadores = player_stats_df.merge(national_teams_df, on = "team_id", how = "left")
jugadores = jugadores.drop(columns = ["player_name", "position"])
jugadores = jugadores.merge(squads_players_df, on = "player_id", how = "left")

jugadores = jugadores.rename(columns={
    "team_name": "seleccion_nacional",
    "club_team": "club_jugador",
    "caps": "partidos_seleccion",
    "position": "posicion",
    "market_value_eur": "valor_mercado",
    "matches_played": "partidos_jugados",
    "minutes_played": "minutos_jugados",
    "goals": "goles",
    "assists": "asistencias",
    "shots": "tiros",
    "yellow_cards": "tarjetas_amarillas",
    "red_cards": "tarjetas_rojas",
    "saves": "paradas",
    "goals_conceded": "goles_concedidos",
    "average_rating": "calificacion_media"})
# Sustituimos el nombre por el nombre bien puesto(de antes)
jugadores["player_name"] = jugadores["player_id"].map(nombres_correctos)
jugadores = jugadores.set_index("player_name")
jugadores.index.name = "nombre_jugador"
jugadores = jugadores[caracteristicas_jugadores]

# 3.3 DataFrame EVENTOS

# Base: match_register
eventos = match_register_df.merge(national_teams_df, on = "team_id", how = "left")
eventos = eventos.merge(player_stats_df, on = "player_id", how = "left")
eventos["player_name"] = eventos["player_id"].map(nombres_correctos)
eventos = eventos.rename(columns = {
    "minute": "minuto_evento",
    "match_id": "index_partido",
    "player_name": "nombre_jugador",
    "event_type": "tipo_evento",
    "team_name": "seleccion_evento"})
eventos = eventos[caracteristicas_eventos]
eventos.index.name = "index_evento"


# 4. LIMPIEZA DE DATOS: DUPLICADOS, NULOS Y ANÓMALOS

# 4.1 Duplicados

#Empezamos con valores duplicados generales
def duplicados_generales(df, nombre):
    """
    Informa de los duplicados exactos (filas idénticas) de un DataFrame.
    """
    print(f"Número de duplicados exactos en {nombre}: {df.duplicated().sum()}")

# Ahora duplicados de negocio en las columnas índices
def duplicados_negocio_index(df, nombre_df):
    """
    Informa de los duplicados de negocio (índice repetido) de un DataFrame.
    """
    print(f"Número de duplicados de negocio en {nombre_df}: {df.index.duplicated().sum()}")

duplicados_negocio_index(partidos, "partidos")
duplicados_negocio_index(jugadores, "jugadores")
# En eventos los duplicados de negocio se elimnan en el 3

# 4.2 Análisis de nulos y anómalos

def anomalos_numerica(df, nombre):
    """
    Análisis de las columnas NUMÉRICAS de un DataFrame.

    Hace un describe, para que se pueda ver los nulos por columna y cuántos
    valores negativos hay, ya que no deberia de haber
    """
    num = df.select_dtypes(include="number") 
    print(f"\n===== {nombre} (numéricas) =====")
    print(num.describe())
    print("Nulos:\n", num.isna().sum())
    print("Negativos:\n", (num < 0).sum())

def anomalos_categorica(df, nombre):
    """
    Análisis de las columnas NO NUMÉRICAS (texto) de un DataFrame.

    Imprime el % de nulos de cada columna y los 10 valores más frecuentes.
    Se usa repr() apreciar espacios y palabras escritas de distinta forma
    """
    cat = df.select_dtypes(exclude="number") 
    print(f"\n===== {nombre} (categóricas) =====")
    print((cat.isna().mean() * 100).round(2))
    for col in cat.columns:
        print(f"\n--- {col} ---\n", cat[col].map(repr).value_counts(dropna=False).head(10))

def anomalos(df, nombre):
    """
    Lanza los dos análisis anteriores sobre un DataFrame.
    """
    anomalos_categorica(df, nombre)
    anomalos_numerica(df, nombre)

# 4.3 Funciones de limpieza de cada DataFrame

def grafico_nulos(df, titulo):
    """
    Gráfico de barras horizontales con el % de nulos de cada columna.

    Solo se dibujan las columnas que tienen algún nulo
    """
    porcentaje = (df.isna().mean() * 100).round(1)
    porcentaje = porcentaje[porcentaje > 0].sort_values()
    if porcentaje.empty:
        print(f"{titulo}: no hay nulos")
        return
    ax = porcentaje.plot(kind="barh", title=f"% de nulos por columna · {titulo}")
    ax.set_xlabel("% de filas con nulo")
    ax.bar_label(ax.containers[0])
    plt.tight_layout()
    plt.show()


def limpiar_partidos(df):
    """
    Limpieza de nulos y anómalos del DataFrame partidos.
    """
    df = df.copy()
    df = df[~df.index.duplicated(keep="first")].sort_index()     # Duplicados de negocio
    for col in ["ronda", "estadio", "ciudad_partido", "pais_partido",
                "seleccion_local", "seleccion_visitante", "arbitro_partido"]:
        df[col] = df[col].str.strip()  # Quitamos espacios
    for col in ["penalty_local", "penalty_visitante"]:
        partidos[col] = (partidos[col] / 10).fillna(0).astype(int)
    # Traduccion ronda(al principio están las conversiones)
    df["ronda"] = df["ronda"].replace(RONDAS)
    df["pais_partido"] = df["pais_partido"].str.upper()
    df["prorroga"] = df["prorroga"].map({True: "SI", False: "NO"})
    df["arbitro_partido"] = df["arbitro_partido"].fillna("Desconocido") # Árbitro desconocido
    for col in ["marcador_local", "marcador_visitante"]: #Columna a entero
        df[col] = df[col].astype(int)
    return df

def limpiar_jugadores(df):
    """
    Limpieza de nulos y anómalos del DataFrame jugadores
    """
    df = df.copy()
    df["posicion"] = df["posicion"].str.strip().replace(POSICIONES) # Ponemos las posiciones como nos pide

    no_ha_jugado = df["minutos_jugados"] == 0 #sacamos los que no han jugado
    estadisticas = ["goles", "asistencias", "tiros", "tarjetas_amarillas", "tarjetas_rojas"]
    for col in estadisticas:
        df.loc[no_ha_jugado, col] = df.loc[no_ha_jugado, col].fillna(0)

    print("Tiros nulos en jugadores que sí han jugado:", df["tiros"].isna().sum())
    mediana_tiros = df.groupby("posicion")["tiros"].transform("median")
    df["tiros"] = df["tiros"].fillna(mediana_tiros)

    no_portero = df["posicion"] != "Portero"
    for col in ["paradas", "goles_concedidos"]:
        df.loc[no_portero, col] = df.loc[no_portero, col].fillna(0)

    #pasamos a nulo para el 7
    print("Calificaciones = 0:", (df["calificacion_media"] == 0).sum())
    print("Valores de mercado = 0:", (df["valor_mercado"] == 0).sum())
    df.loc[df["calificacion_media"] == 0, "calificacion_media"] = None
    df.loc[df["valor_mercado"] == 0, "valor_mercado"] = None

    enteras = ["partidos_seleccion", "partidos_jugados", "minutos_jugados", "goles",
               "asistencias", "tiros", "tarjetas_amarillas", "tarjetas_rojas",
               "paradas", "goles_concedidos"]
    df[enteras] = df[enteras].astype(int)
    return df


def limpiar_eventos(df):
    """
    Limpieza general del DataFrame eventos.
    """
    df = df.copy()
    df["index_partido"] = df["index_partido"].astype(int) #Columna a entero
    for col in ["nombre_jugador", "tipo_evento", "seleccion_evento"]: #Quitamos espacios
        df[col] = df[col].str.strip()
    df["tipo_evento"] = df["tipo_evento"].replace(TIPOS_EVENTO) #Cambiamos texto al pedido
    return df


# 5. VALORES ANÓMALOS DEL DATAFRAME EVENTOS

def eventos_anomalos(eventos, partidos):
    """
    Detecta y elimina los eventos anómalos

    Un evento es  anómalo cuando cumple algo de lo siguiente:
      1. Minuto negativo, es imposible.
      2. Minuto mayor que el máximo posible para ese partido:
           - Que un partido sin prorroga dure demasiado
           - partido con prórroga  + de 120. Al 121 es penalties
      3. Coherencia: un penalty de tanda en un partido que no ha llegado a penaltis.
      4. La selección del evento no es ninguna de las dos que juegan ese partido o el partido no existe
    """
    df = eventos.copy()

    df["prorroga"] = df["index_partido"].map(partidos["prorroga"])
    local = df["index_partido"].map(partidos["seleccion_local"])
    visitante = df["index_partido"].map(partidos["seleccion_visitante"])
    hubo_tanda = df["index_partido"].map(partidos["penalty_local"] + partidos["penalty_visitante"]) > 0

    # Histograma de los minutos para ver los valores raros
    ax = df["minuto_evento"].plot(kind="hist", bins=40, title="Distribución de minutos de los eventos")
    ax.axvline(0, color="red", linestyle="--", label="minuto 0")
    ax.axvline(90, color="grey", linestyle="--", label="minuto 90")
    ax.axvline(120, color="black", linestyle="--", label="minuto 120")
    ax.set_xlabel("Minuto")
    ax.legend()
    plt.tight_layout()
    plt.show()

    # Máximo minuto posible en cada partido
    minuto_max = df["prorroga"].map({"SI": MINUTO_MAX_TANDA, "NO": MINUTO_MAX_REGLAMENTARIO})

    tipos_validos = set(TIPOS_EVENTO.values())
    es_tanda = df["tipo_evento"].isin(["Penalty marcado", "Penalty fallado"])
    condiciones = pd.DataFrame({
        "Minuto negativo": df["minuto_evento"] < 0,
        "Minuto mayor que el máximo": df["minuto_evento"] > minuto_max,
        "Tipo de evento no válido": ~df["tipo_evento"].isin(tipos_validos),
        "Penalty de tanda sin tanda": es_tanda & ~hubo_tanda,
        "Selección que no juega el partido": (df["seleccion_evento"] != local) & (df["seleccion_evento"] != visitante)})

    # Un evento es anómalo si cumple al menos una de las condiciones
    es_anomalo = condiciones.any(axis=1)

    print("\nEventos anómalos por motivo:")
    print(condiciones.sum())
    print("\nEventos anómalos detectados:")
    print(df[es_anomalo])

    # Nos quedamos con los eventos correctos y quitamos la columna auxiliar
    df = df[es_anomalo == False]
    df = df.drop(columns="prorroga")

    df = df.reset_index(drop=True)
    df.index = df.index + 1
    df.index.name = "index_evento"
    return df


# 6. LIMPIEZA COLUMNA FECHA PARTIDO

def limpiar_fechas(df, columna):
    """
    Esta función limpia las fechas escribiendolas todas en el mismo formato (Dia/Mes/Año). Primero cambia 
    las fechas con algún símbolo mal o en distinto orden, y luego las que tienen letras o palabras
    """
    df = df.copy()
    df[columna] = df[columna].str.strip()
    expr_punto = r"^(\d{2})\.(\d{2})\.(\d{4})$"
    expr_guion = r"^(\d{2})-(\d{2})-(\d{4})$"
    expr_complex = r"^(\d{4})-(\d{2})-(\d{2})T.*$"
    expr_juntos = r"^(\d{4})(\d{2})(\d{2})$"

    expr_letra_espacio = r"^([A-Za-z]+) (\d{1,2}),? (\d{4})$"
    expr_letra_guion = r"^(\d{1,2})-([a-z]+)-(\d{2})$"

    df[columna] = df[columna].str.replace( expr_punto, r"\1/\2/\3", regex = True) #Coge el primer parentesis, elsegundo...
    df[columna] = df[columna].str.replace( expr_guion, r"\2/\1/\3", regex = True)
    df[columna] = df[columna].str.replace( expr_complex, r"\3/\2/\1", regex = True)
    df[columna] = df[columna].str.replace(expr_juntos, r"\3/\2/\1", regex=True)

    df[columna] = df[columna].str.replace(expr_letra_espacio, r"\2 \1 \3", regex=True)    
    df[columna] = df[columna].str.replace(expr_letra_guion, r"\1 \2 20\3", regex=True)  
    df[columna] = df[columna].str.replace(" de ", " ")                                                     

    meses = {"June": "06", "Jun": "06", "jun": "06", "junio": "06",
             "July": "07", "Jul": "07", "jul": "07", "julio": "07"}
    for nombre, numero in meses.items():   #Cambiamos el mes por su número
        df[columna] = df[columna].str.replace(rf"^(\d{{1,2}}) {nombre} (\d{{4}})$", rf"\1/{numero}/\2", regex=True)

    df[columna] = pd.to_datetime(df[columna], format="%d/%m/%Y") #Indica el formato de la fecha

    return df


# 7. RELLENO DE DATOS POR IMPUTACIÓN

# 7.1 IMPUTACIÓN POR LA MEDIA VALOR MERCADO

def imputacion_media(df, columna: str):
    """
    Esta función agrupa el DataFrame por su selección y se queda con la columna de valor mercado.
    A continuación hace la media de cada selección y por último usa esa media para rellenar los valores nulos
    """
    df = df.copy()
    media_uso = df.groupby("seleccion_nacional")[columna].transform("mean")
    df[columna] = df[columna].fillna(media_uso)
    return df


# 7.2 IMPUTACIÓN POR REGRESIÓN DE CALFICACIÓN MEDIA

def imputacion_calificacion_regresion(df, columna):
    """
    Esta función filtra los datos de si es portero o no con una mascara. Una vez tenemos los datos filtrados,
    rellenamos la información nula mediante una regresión
    """

    df = df.copy()
    vars_porteros = ["goles_concedidos", "paradas", "tarjetas_rojas", "tarjetas_amarillas"]
    vars_jugadores = ["asistencias", "tarjetas_amarillas", "tarjetas_rojas", "goles"]
    es_portero = df["posicion"] == "Portero"
    grupos = {"porteros": (es_portero, vars_porteros),"jugadores": (~es_portero, vars_jugadores)}

    for nombre, (mask_grupo, variables) in grupos.items():
        df[variables] = df[variables].fillna(0)

        conocidos = df[mask_grupo & df[columna].notna()]
        desconocidos = df[mask_grupo & df[columna].isna()]
        if len(desconocidos) == 0:
            continue

        X = conocidos[variables]
        y = conocidos[columna]

        modelo = LinearRegression()
        modelo.fit(X, y)
        for i in range(len(variables)):
            print(variables[i], modelo.coef_[i])

        print("b:", modelo.intercept_)
        print("R²:", modelo.score(X, y))
        df.loc[desconocidos.index, columna] = modelo.predict(desconocidos[variables])
    return df

# 7.3 IMPUTACIÓN POR INTERPOLACIÖN DE MINUTO EVENTO

def compare_with_baseline(df, columna):
    new_data = df.loc[df[columna].isna()] # detectamos los valores imputados
    plt.scatter(df.index, df[columna]) # dibujamos los datos originales 
    plt.scatter(new_data.index, new_data[columna], color="red")

def imputacion_min_evento(df, columna):
    """
    Está función rellena los datos nulos mediante interpolación, 
    teniendo en cuenta que primero ordenamos los datos según index partido para que los datos con los que lo rellene 
    tengan mas coherencia
    """
    df = df.copy()
    df[columna] = df.groupby("index_partido")[columna].transform(lambda min : min.interpolate("linear")).bfill()
    compare_with_baseline(df,columna)

    return df

# 8 EXPORTACIÓN DE LOS DATA FRAMES A FICHEROS EXCEL

def exportar_excel(df1, df2, df3):
    """
    Esta función exporta los tres data frames creados a ficheros excel
    """
    df1.to_excel("partidosWC26.xlsx")
    df2.to_excel("eventosWC26.xlsx")
    df3.to_excel("jugadoresWC2026.xlsx")
    print(f'''Los Data Frames has sido exportados:\n
          {df1} -> partidosWC26.xlsx,\n
          {df2} -> eventosWC26.xlsx,\n
          {df3} -> jugadoresWC2026.xlsx''')
    

# MAIN

if __name__ == "__main__":

    # PASO 4
    print("\n" + "#"*80)
    print("PASO 4 -> DIAGNÓSTICO DE DUPLICADOS, NULOS Y ANÓMALOS")
    print("#"*80)
    # duplicados exactos
    duplicados_generales(partidos, "partidos")
    duplicados_generales(jugadores, "jugadores")
    duplicados_generales(eventos, "eventos")
    # Nulos y anómalos de jugadores y eventos
    anomalos(partidos, "partidos")
    anomalos(jugadores, "jugadores")
    anomalos(eventos, "eventos")
    # gráficos de nulos antes de la limpieza
    grafico_nulos(partidos, "partidos (antes)")
    grafico_nulos(jugadores, "jugadores (antes)")
    grafico_nulos(eventos, "eventos (antes)")

    # limpieza
    print("\n" + "#"*80)
    print("PASO 4 -> LIMPIEZA")
    print("#"*80)
    print("\n--- partidos ---")
    partidos = limpiar_partidos(partidos)
    print("\n--- jugadores ---")
    jugadores = limpiar_jugadores(jugadores)
    print("\n--- eventos ---")
    eventos = limpiar_eventos(eventos)

    # PASO 5
    print("\n" + "#"*80)
    print("PASO 5 -> EVENTOS ANÓMALOS")
    print("#" * 80)
    eventos = eventos_anomalos(eventos, partidos)


    print("\n" + "#"*80)
    print("RESULTADO TRAS LOS PASOS 1-5")
    print("#"*80)
    exploration(partidos, "partidos (limpio)")
    exploration(jugadores, "jugadores (limpio)")
    exploration(eventos, "eventos (limpio)")
    grafico_nulos(partidos, "partidos (después)")
    grafico_nulos(jugadores, "jugadores (después)")
    grafico_nulos(eventos, "eventos (después)")
    # Paso 6
    print("\n" + "#"*80)
    print("PASO 6 -> LIMPIEZA DE FECHAS")

    # Paso 7
    print("\n" + "#"*80)
    print("PASO 7 -> IMPUTACIÓN POR MEDIA, REGRESIÓN E INTERPOLACIÓN")
    df_media_limp = imputacion_media(jugadores, "valor_mercado")
    print(f"Datos nulos de valor mercado antes: {jugadores["valor_mercado"].isna().sum()}")
    print(f"Datos nulos de valor mercado después: {df_media_limp["valor_mercado"].isna().sum()}")
    df_calific = imputacion_calificacion_regresion(jugadores, "calificacion_media")
    print(f"Datos nulos de calificación media antes: {jugadores["calificacion_media"].isna().sum()}")
    print(f"Datos nulos de calificación media despues: {df_calific["calificacion_media"].isna().sum()}")
    df_evento_limp = imputacion_min_evento(eventos, "minuto_evento")
    print(f"Datos nulos de minuto evento antes: {eventos["minuto_evento"].isna().sum()}")
    print(f"Datos nulos de minuto evento despues: {df_evento_limp["minuto_evento"].isna().sum()}")

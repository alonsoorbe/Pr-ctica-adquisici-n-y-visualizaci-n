
#   BLOQUE 1 · Recopilación, limpieza y tratamiento de los datasets del Mundial 2026

import pandas as pd
from IPython.display import display
import matplotlib.pyplot as plt


# [NUEVO] Límites de minutos usados en el paso 5 (minutos anómalos)
MINUTO_MAX_REGLAMENTARIO = 90 + 15   # 90' + un descuento muy generoso
MINUTO_MAX_TANDA = 121               # en el dataset la tanda de penaltis se registra en el 121'

# [NUEVO] Traducciones para dejar las categorías limpias y en castellano
RONDAS = {
    "Group Stage": "Fase de grupos",
    "Round of 32": "Dieciseisavos",
    "Round of 16": "Octavos",
    "Quarter-finals": "Cuartos",
    "Semi-finals": "Semifinal",
    "Third-place match": "Tercer puesto",
    "Final": "Final",
}
POSICIONES = {
    "GK": "Portero",
    "DEF": "Defensa",
    "MID": "Centrocampista",
    "FWD": "Delantero",
}
TIPOS_EVENTO = {
    "Goal": "Gol",
    "Assist": "Asistencia",
    "Yellow Card": "Tarjeta amarilla",
    "Red Card": "Tarjeta roja",
    "Penalty Shootout Goal": "Penalty marcado",
    "Penalty Shootout Miss": "Penalty fallado",
    "VAR Review": "Revisión VAR",
    "Review VAR": "Revisión VAR",     # mismo evento escrito al revés en algunos registros
}


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
    "worldcup_venues": worldcup_venues_df,
}


# Primero hacemos una función que nos permite ver y analizar el contenido de los ficheros
def exploration(df, nombre):
    """
    Exploración inicial de un DataFrame (paso 1).

    Muestra por pantalla:
      - Dimensiones (filas, columnas) y número de filas duplicadas exactas.
      - Una tabla resumen por columna: tipo de dato, nº de nulos, % de nulos
        y nº de valores distintos.
      - Una fila aleatoria para ver el formato real de los datos.
      - Los estadísticos básicos de todas las columnas (describe).

    Parámetros
      df     : DataFrame a explorar.
      nombre : texto que se usa como título en la salida.
    """
    # Cabecera con el nombre del dataset
    print("\n" + "=" * 80)
    print(f"DATASET: {nombre}")
    print("=" * 80)
    # Tamaño y duplicados exactos (filas idénticas en todas las columnas)
    print("Dimensiones:", df.shape)
    print("Filas duplicadas:", df.duplicated().sum())
    # Resumen por columna: tipo, nulos, % nulos y nº de valores distintos
    resumen = pd.DataFrame({"tipo": df.dtypes,"nulos": df.isna().sum(),"% nulos": (df.isna().mean() * 100).round(1),"distintos": df.nunique()})
    print("\n--- Columnas ---")
    display(resumen)
    # Una fila al azar para ver cómo vienen escritos los datos
    print("\n--- Filas aleatorias ---")
    display(df.sample())
    # Estadísticos de todas las columnas (numéricas y de texto)
    print("\n--- Estadísticos ---")
    display(df.describe(include="all"))


# 2. CREACIÓN DE LOS DATAFRAMES PARTIDOS, EVENTOS Y JUGADORES

# Creamos los tres dataframes pedidos vacíos
partidos = pd.DataFrame()
eventos = pd.DataFrame()
jugadores = pd.DataFrame()

# Columnas finales de cada DataFrame, con los nombres exactos del enunciado
# (el índice de cada uno se asigna aparte: index_partido, nombre_jugador, index_evento)
caracteristicas_partidos = ["fecha_partido", "ronda", "estadio", "ciudad_partido", "pais_partido", "seleccion_local", "seleccion_visitante", "marcador_local", "marcador_visitante", "prorroga", "penalty_local", "penalty_visitante", "arbitro_partido"]
caracteristicas_jugadores = ["seleccion_nacional", "club_jugador", "partidos_seleccion", "posicion", "valor_mercado", "partidos_jugados", "minutos_jugados", "goles", "asistencias", "tiros", "tarjetas_amarillas", "tarjetas_rojas", "paradas", "goles_concedidos", "calificacion_media"]
caracteristicas_eventos = ["minuto_evento", "index_partido", "nombre_jugador", "tipo_evento", "seleccion_evento"]


# 3. CONSTRUCCIÓN DE LOS DATAFRAMES (MERGES Y RENOMBRADO DE COLUMNAS)

# -----------------------------------------------------------------------------
# 3.0 Limpieza previa de las tablas auxiliares que se usan como "diccionario"
# -----------------------------------------------------------------------------
# DataFrame de partidos
# Mediante merges, cogeremos DataFrame a DataFrame para ver que relación tiene e ir haciendo merges poco a poco
# Primero cogemos de base el matches_mundial_seis_df, que es el que más datos tiene
# Cogeremos ciertos DataFrames basandonos el DataFRames que tengan información que necesitamos y alguna relación con nuestro DataFrame base, lo hacemos observando todos los csv
national_teams_df = national_teams_df.dropna(subset=["team_id"]).drop_duplicates(subset="team_id")
match_register_df = match_register_df.dropna(subset=["match_id"])                    # 15 filas vacías
match_register_df = match_register_df.drop_duplicates(subset="event_id", keep="first")  # mismo evento repetido

# [NUEVO] Nombres de jugadores corregidos (se usan en jugadores y en eventos)
# Problemas detectados en la exploración:
#   - En squads_and_players, 7 jugadores aparecen solo como "Mc" (nombre cortado).
#     En player_stats sí está el nombre completo (Scott McTominay, Weston McKennie...).
#   - En player_stats los acentos están mal codificados ("JosŽ Raœl"), así que el
#     nombre bueno es el de squads_and_players.
#   - Hay dos jugadores distintos llamados "Ali Ahmed" (Canadá y Arabia Saudí).
#     Como el índice de jugadores es el nombre, les añadimos la selección para
#     que no se confundan ni se borre uno como si fuera un duplicado.
# Creamos una Serie player_id -> nombre correcto y la aplicamos con .map()
nombres_correctos = squads_players_df.set_index("player_id")["player_name"]
nombres_stats = player_stats_df.set_index("player_id")["player_name"]
nombres_correctos = nombres_correctos.where(nombres_correctos.str.len() > 2, nombres_stats)  # "Mc" -> nombre completo
seleccion_de_jugador = squads_players_df.set_index("player_id")["team_id"].map(national_teams_df.set_index("team_id")["team_name"])
repetidos = nombres_correctos.duplicated(keep=False)
nombres_correctos[repetidos] = nombres_correctos[repetidos] + " (" + seleccion_de_jugador[repetidos] + ")"

# -----------------------------------------------------------------------------
# 3.1 DataFrame PARTIDOS
# -----------------------------------------------------------------------------
# Base: matches_mundial2026 (un registro por partido) y le vamos añadiendo:
#   árbitros (referee_id) -> fases (stage_id) -> estadios (venue_id)
#   -> selección local (home_team_id) -> selección visitante (away_team_id)
partidos = matches_mundial_seis_df.merge(index_referees_df, on = "referee_id", how = "left")
# Renombramos el país del árbitro para no confundirlo con el país del estadio
partidos = partidos.rename(columns= {"country": "ref_country"})
partidos = partidos.merge(tournament_stages_df, on = "stage_id", how = "left")
partidos = partidos.merge(worldcup_venues_df, on = "venue_id", how = "left")
partidos = partidos.merge(national_teams_df, left_on = "home_team_id", right_on = "team_id", how = "left")
partidos = partidos.rename(columns = {"team_name": "seleccion_local"})
partidos = partidos.merge(national_teams_df, left_on = "away_team_id", right_on = "team_id",how = "left", suffixes=("", "_away"))
partidos = partidos.rename(columns = {"team_name": "seleccion_visitante"})
# Renombramos al nombre exacto que pide el enunciado
partidos = partidos.rename(columns ={
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
# [NUEVO] Usamos match_id como índice: así index_partido va de 1 a 104 y coincide
# con el index_partido de eventos (que también es el match_id).
# Además permite detectar los duplicados de negocio (mismo partido repetido).
partidos = partidos.set_index("match_id")
partidos = partidos[caracteristicas_partidos]
partidos.index.name = "index_partido"

# -----------------------------------------------------------------------------
# 3.2 DataFrame JUGADORES
# -----------------------------------------------------------------------------
# Base: player_stats (estadísticas del torneo) + selección + datos de la plantilla
# (club, internacionalidades, posición, valor de mercado)
jugadores = player_stats_df.merge(national_teams_df, on = "team_id", how = "left")
# El nombre y la posición se cogen de squads_and_players, así que los quitamos de aquí
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
# [NUEVO] Sustituimos el nombre por el nombre corregido (ver 3.0)
jugadores["player_name"] = jugadores["player_id"].map(nombres_correctos)
jugadores = jugadores.set_index("player_name")
jugadores.index.name = "nombre_jugador"
jugadores = jugadores[caracteristicas_jugadores]

# -----------------------------------------------------------------------------
# 3.3 DataFrame EVENTOS
# -----------------------------------------------------------------------------
# Base: match_register (un registro por evento) + selección + nombre del jugador
eventos = match_register_df.merge(national_teams_df, on = "team_id", how = "left")
eventos = eventos.merge(player_stats_df, on = "player_id", how = "left")
# [NUEVO] El nombre de player_stats tiene los acentos mal codificados:
# lo sustituimos por el nombre corregido para que coincida con el de jugadores
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

# 4.1 Visualización de los duplicados antes de limpiar

# Limpiaza de datos, duplicados, nulos...

#Primero observamos visualmente los duplicados con una gráfica
claves = {
    "partidos":  (partidos,  ["index_partido"]),
    "jugadores": (jugadores, ["nombre_jugador"]),
    "eventos":   (eventos,   ["index_partido", "minuto_evento", "nombre_jugador", "tipo_evento"]),
}

# Tabla con el nº de duplicados exactos y de negocio de cada DataFrame
resumen = pd.DataFrame({
    nombre: {
        "Duplicados exactos": df.reset_index().duplicated().sum(),
        "Duplicados de negocio": df.reset_index().duplicated(subset=clave).sum(),
    }
    for nombre, (df, clave) in claves.items()
})

display(resumen)

# Gráfico de barras con el nº de duplicados encima de cada barra
ax = resumen.plot(kind="bar", rot=0, title="Duplicados por DataFrame antes de la limpieza")
ax.set_ylabel("Nº de filas")
for cont in ax.containers:
    ax.bar_label(cont)
plt.tight_layout()
plt.show()

# 4.2 Duplicados

#Empezamos con valores duplicados generales
def duplicados_generales(df, nombre):
    """
    Informa de los duplicados exactos (filas idénticas) de un DataFrame.

    Imprime cuántas filas duplicadas hay antes y después de aplicar
    drop_duplicates().
    OJO: la función no devuelve el DataFrame, así que solo sirve para
    informar; la eliminación real se hace en el main.
    """
    print(f"Número de duplicados exactos en {nombre}: {df.duplicated().sum()}")
    df = df.drop_duplicates()
    print(f"Número de duplicados después: {df.duplicated().sum()}")

# Ahora iremos DataFrame a DataFrame quitando los duplicados de negocio en las columnas índices
def duplicados_negocio_index(df, columna, nombre_df):
    """
    Informa de los duplicados de negocio (índice repetido) de un DataFrame.

    Criterio: si un índice aparece varias veces, nos quedamos con la fila
    que tiene MENOS nulos (la más completa). Para ello:
      1) se pasa el índice a columna (reset_index),
      2) se cuenta el nº de nulos de cada fila,
      3) se ordena de menos a más nulos,
      4) se borran los repetidos quedándonos con el primero (el más completo),
      5) se vuelve a poner la columna como índice.
    Imprime el nº de duplicados antes y después.
    OJO: igual que la anterior, no devuelve el DataFrame (solo informa).
    """
    print(f"Número de duplicados de negocio en {nombre_df}: {df.index.duplicated().sum()}")
    df = df.reset_index()
    # Columna auxiliar con el nº de nulos de cada fila
    df["nulos"] = df.isna().sum(axis = 1)
    df = df.sort_values(by= "nulos", ascending = True)
    df = df.drop_duplicates(subset = columna, keep = "first")
    df = df.drop(columns = "nulos").set_index(columna)
    print(f"Número de duplicados de negocio en {nombre_df} después de eliminarlos: {df.index.duplicated().sum()}")

duplicados_negocio_index(partidos, "index_partido", "partidos")
duplicados_negocio_index(jugadores, "nombre_jugador", "jugadores")
# En eventos la clave de negocio son 4 columnas: mismo partido, minuto, jugador y tipo
eventos = eventos.drop_duplicates(subset=["index_partido", "minuto_evento", "nombre_jugador", "tipo_evento"],keep="first")

# 4.3 Análisis de nulos y anómalos

def anomalos_numerica(df, nombre):
    """
    Análisis de las columnas NUMÉRICAS de un DataFrame.

    Imprime los estadísticos (describe), los nulos por columna y cuántos
    valores negativos hay (en este dataset ningún valor numérico debería
    ser negativo: goles, minutos, tarjetas...).
    """
    num = df.select_dtypes(include="number") # solo columnas numéricas
    print(f"\n===== {nombre} (numéricas) =====")
    print(num.describe())
    print("Nulos:\n", num.isna().sum())
    print("Negativos:\n", (num < 0).sum())

def anomalos_categorica(df, nombre):
    """
    Análisis de las columnas NO NUMÉRICAS (texto) de un DataFrame.

    Imprime el % de nulos de cada columna y los 10 valores más frecuentes.
    Se usa repr() para que se vean los espacios sobrantes ('Quarter-finals ')
    y las variantes de escritura ('USA' / 'usa').
    """
    cat = df.select_dtypes(exclude="number") # columnas no numéricas
    print(f"\n===== {nombre} (categóricas) =====")
    print((cat.isna().mean() * 100).round(2))
    for col in cat.columns:
        print(f"\n--- {col} ---\n", cat[col].map(repr).value_counts(dropna=False).head(10))

def nulos(df, nombre):
    """Lanza los dos análisis anteriores (texto + numérico) sobre un DataFrame."""
    anomalos_categorica(df, nombre)
    anomalos_numerica(df, nombre)

nulos(partidos, "partidos")
#Empezamos limpiando los datos anomalos de partidos

partidos["pais_partido"] = partidos["pais_partido"].replace("USA", "usa")
# Los penaltis vienen multiplicados por 10 (30 = 3 penaltis). Dividimos entre 10
# y ponemos 0 en los partidos sin tanda (el enunciado pide "0 si no aplica")
for col in ["penalty_local", "penalty_visitante"]:
    partidos[col] = (partidos[col] / 10).fillna(0).astype(int)


# 4.4 Funciones de limpieza de cada DataFrame

def grafico_nulos(df, titulo):
    """
    Gráfico de barras horizontales con el % de nulos de cada columna.

    Solo se dibujan las columnas que tienen algún nulo. Sirve para justificar
    visualmente qué columnas hay que tratar (consejo del enunciado).
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

    Decisiones tomadas (vistas con nulos(partidos)):
      - Duplicados de negocio: el mismo partido aparecía varias veces (6 partidos
        repetidos en el csv + filas multiplicadas por árbitros y fases repetidas
        en sus tablas). Las filas repetidas son idénticas, así que nos quedamos
        con la primera de cada index_partido -> 104 partidos (los del Mundial).
      - ronda: 'Quarter-finals ' tenía un espacio al final -> strip() y se
        traduce al castellano (Fase de grupos, Octavos, Cuartos...).
      - pais_partido: venían 'USA' y 'usa' mezclados con 'MEX' y 'CAN'.
        Lo dejamos todo en mayúsculas para que sea homogéneo.
      - prorroga: el enunciado pide SI / NO en vez de True / False.
      - arbitro_partido: un partido (el 53) no tiene árbitro asignado en el csv.
        No se puede deducir, así que se rellena con 'Desconocido'.
      - Marcadores: se comprueba que no hay negativos y se dejan como enteros.
    La fecha_partido NO se toca aquí: se homogeneiza en el paso 6 con regex.
    """
    df = df.copy()
    # Duplicados de negocio: un único registro por partido
    df = df[~df.index.duplicated(keep="first")].sort_index()
    # Quitamos espacios sobrantes en las columnas de texto
    for col in ["ronda", "estadio", "ciudad_partido", "pais_partido",
                "seleccion_local", "seleccion_visitante", "arbitro_partido"]:
        df[col] = df[col].str.strip()
    # Traducción de las rondas
    df["ronda"] = df["ronda"].replace(RONDAS)
    # País del estadio en mayúsculas (USA, MEX, CAN)
    df["pais_partido"] = df["pais_partido"].str.upper()
    # Prórroga como SI / NO
    df["prorroga"] = df["prorroga"].map({True: "SI", False: "NO"})
    # Árbitro desconocido
    df["arbitro_partido"] = df["arbitro_partido"].fillna("Desconocido")
    # Comprobación de marcadores negativos (no debería haber ninguno)
    for col in ["marcador_local", "marcador_visitante"]:
        print(f"{col}: {(df[col] < 0).sum()} valores negativos")
        df[col] = df[col].astype(int)
    return df


def limpiar_jugadores(df):
    """
    Limpieza de nulos y anómalos del DataFrame jugadores.

    Decisiones tomadas (vistas con nulos(jugadores)):
      - posicion: se traduce GK/DEF/MID/FWD -> Portero/Defensa/Centrocampista/Delantero.
      - Estadísticas nulas (goles, asistencias, tiros, tarjetas): TODOS los
        jugadores con estos nulos tienen 0 minutos jugados, es decir, no han
        jugado. Por tanto su valor real es 0.
      - tiros: además hay jugadores que SÍ han jugado pero no tienen tiros
        registrados. Se imputan con la mediana de tiros de su posición
        (un portero no tira lo mismo que un delantero).
      - paradas y goles_concedidos: solo tienen sentido en porteros. En el
        resto de posiciones el nulo significa 0.
      - calificacion_media = 0: hay jugadores con 1-2 minutos y nota 0. Una
        nota 0 no es real (significa "sin nota"), así que se pasa a nulo para
        imputarla en el paso 7 junto al resto.
      - valor_mercado = 0: un jugador de primera división con valor 0 es un
        error -> nulo, se imputa en el paso 7 (media de su selección).
        El valor está en millones de euros (M€).
      - Se comprueba que no haya negativos ni partidos > 8 (máximo en un Mundial
        de 48 selecciones) ni minutos imposibles (> 120 por partido).
      - Tipos: las columnas de conteo se pasan a entero (int).
    valor_mercado y calificacion_media se dejan con nulos A PROPÓSITO:
    se rellenan con las técnicas de imputación del paso 7.
    """
    df = df.copy()
    # Traducción de posiciones
    df["posicion"] = df["posicion"].str.strip().replace(POSICIONES)

    # Comprobaciones de valores imposibles
    numericas = df.select_dtypes(include="number").columns
    print("Valores negativos por columna:\n", (df[numericas] < 0).sum())
    print("Jugadores con más de 8 partidos:", (df["partidos_jugados"] > 8).sum())
    print("Jugadores con más de 120 min por partido:",
          (df["minutos_jugados"] > 120 * df["partidos_jugados"]).sum())

    # Estadísticas de jugadores que no han jugado -> 0
    no_ha_jugado = df["minutos_jugados"] == 0
    estadisticas = ["goles", "asistencias", "tiros", "tarjetas_amarillas", "tarjetas_rojas"]
    for col in estadisticas:
        df.loc[no_ha_jugado, col] = df.loc[no_ha_jugado, col].fillna(0)

    # Tiros que faltan en jugadores que sí han jugado -> mediana de su posición
    print("Tiros nulos en jugadores que sí han jugado:", df["tiros"].isna().sum())
    mediana_tiros = df.groupby("posicion")["tiros"].transform("median")
    df["tiros"] = df["tiros"].fillna(mediana_tiros)

    # Paradas y goles concedidos -> 0 en los que no son porteros
    no_portero = df["posicion"] != "Portero"
    for col in ["paradas", "goles_concedidos"]:
        df.loc[no_portero, col] = df.loc[no_portero, col].fillna(0)

    # Valores anómalos que se pasan a nulo para imputarlos en el paso 7
    print("Calificaciones = 0:", (df["calificacion_media"] == 0).sum())
    print("Valores de mercado = 0:", (df["valor_mercado"] == 0).sum())
    df.loc[df["calificacion_media"] == 0, "calificacion_media"] = None
    df.loc[df["valor_mercado"] == 0, "valor_mercado"] = None

    # Tipos de datos: todo lo que es un conteo, a entero
    enteras = ["partidos_seleccion", "partidos_jugados", "minutos_jugados", "goles",
               "asistencias", "tiros", "tarjetas_amarillas", "tarjetas_rojas",
               "paradas", "goles_concedidos"]
    df[enteras] = df[enteras].astype(int)
    return df


def limpiar_eventos(df):
    """
    Limpieza general del DataFrame eventos (paso 4).

    - index_partido venía como decimal (1.0, 2.0...) porque el csv tenía filas
      vacías -> se pasa a entero.
    - tipo_evento: se traduce y se unifica. 'VAR Review' y 'Review VAR' son el
      mismo evento escrito de dos formas -> 'Revisión VAR'.
    - Se quitan espacios sobrantes en los textos.
    Los minutos anómalos se tratan aparte en el paso 5 (eventos_anomalos).
    """
    df = df.copy()
    df["index_partido"] = df["index_partido"].astype(int)
    for col in ["nombre_jugador", "tipo_evento", "seleccion_evento"]:
        df[col] = df[col].str.strip()
    print("Tipos de evento antes:\n", df["tipo_evento"].value_counts())
    df["tipo_evento"] = df["tipo_evento"].replace(TIPOS_EVENTO)
    print("Tipos de evento después:\n", df["tipo_evento"].value_counts())
    return df


# 5. VALORES ANÓMALOS DEL DATAFRAME EVENTOS

def eventos_anomalos(eventos, partidos):
    """
    Detecta y elimina los eventos anómalos (paso 5).

    Un evento se considera anómalo si cumple alguna de estas condiciones:
      1. Minuto negativo (ej. -45, -10): es imposible.
      2. Minuto mayor que el máximo posible para ese partido:
           - partido sin prórroga  -> más de 90 + 15 de descuento (105')
           - partido con prórroga  -> más de 121' (la tanda se registra en el 121')
      3. Tipo de evento que no está en la lista de tipos válidos.
      4. Coherencia del tipo con el partido: un penalty de tanda en un partido
         que no ha llegado a penaltis.
      5. Coherencia de la selección: la selección del evento no es ninguna de
         las dos que juegan ese partido (o el partido no existe).

    Los eventos SIN minuto (nulos) NO se eliminan: se imputan por interpolación
    en el paso 7, como pide el enunciado.

    Nota: hay 14 goles en los que el jugador es del equipo rival. No son
    errores: son goles en propia puerta (el gol cuenta para el otro equipo),
    por eso NO se consideran anómalos.

    Devuelve el DataFrame sin los eventos anómalos y con index_evento de 1 a n.
    """
    df = eventos.copy()

    # Información del partido de cada evento (se busca por index_partido)
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

    # Condiciones de anomalía (los minutos nulos dan False -> no se eliminan)
    tipos_validos = set(TIPOS_EVENTO.values())
    es_tanda = df["tipo_evento"].isin(["Penalty marcado", "Penalty fallado"])
    condiciones = pd.DataFrame({
        "Minuto negativo": df["minuto_evento"] < 0,
        "Minuto mayor que el máximo": df["minuto_evento"] > minuto_max,
        "Tipo de evento no válido": ~df["tipo_evento"].isin(tipos_validos),
        "Penalty de tanda sin tanda": es_tanda & ~hubo_tanda,
        "Selección que no juega el partido": (df["seleccion_evento"] != local) & (df["seleccion_evento"] != visitante),
    })

    # Resumen de cuántos eventos cumple cada condición
    print("\nEventos anómalos por motivo:\n", condiciones.sum())
    print("\nEventos anómalos detectados:")
    display(df[condiciones.any(axis=1)])

    # Eliminamos los anómalos y quitamos la columna auxiliar
    df = df[~condiciones.any(axis=1)].drop(columns="prorroga")
    print(f"Eventos eliminados: {len(eventos) - len(df)}  |  Eventos finales: {len(df)}")
    print(f"Eventos sin minuto (se imputan en el paso 7): {df['minuto_evento'].isna().sum()}")

    # index_evento consecutivo empezando en 1
    df = df.reset_index(drop=True)
    df.index = df.index + 1
    df.index.name = "index_evento"
    return df


# MAIN

if __name__ == "__main__":

    # PASO 4 · Diagnóstico antes de limpiar
    print("\n" + "#" * 80)
    print("PASO 4 · DIAGNÓSTICO DE DUPLICADOS, NULOS Y ANÓMALOS")
    print("#" * 80)
    # Duplicados exactos (solo informan)
    duplicados_generales(partidos, "partidos")
    duplicados_generales(jugadores, "jugadores")
    duplicados_generales(eventos, "eventos")
    # Nulos y anómalos de jugadores y eventos (los de partidos ya se ven arriba)
    nulos(jugadores, "jugadores")
    nulos(eventos, "eventos")
    # Gráficos de nulos antes de la limpieza
    grafico_nulos(partidos, "partidos (antes)")
    grafico_nulos(jugadores, "jugadores (antes)")
    grafico_nulos(eventos, "eventos (antes)")

    # PASO 4 · Limpieza
    print("\n" + "#" * 80)
    print("PASO 4 · LIMPIEZA")
    print("#" * 80)
    print("\n--- partidos ---")
    partidos = limpiar_partidos(partidos)
    print("\n--- jugadores ---")
    jugadores = limpiar_jugadores(jugadores)
    print("\n--- eventos ---")
    eventos = limpiar_eventos(eventos)

    # PASO 5 · Eventos anómalos
    print("\n" + "#" * 80)
    print("PASO 5 · EVENTOS ANÓMALOS")
    print("#" * 80)
    eventos = eventos_anomalos(eventos, partidos)


    print("\n" + "#" * 80)
    print("RESULTADO TRAS LOS PASOS 1-5")
    print("#" * 80)
    exploration(partidos, "partidos (limpio)")
    exploration(jugadores, "jugadores (limpio)")
    exploration(eventos, "eventos (limpio)")
    grafico_nulos(partidos, "partidos (después)")
    grafico_nulos(jugadores, "jugadores (después)")
    grafico_nulos(eventos, "eventos (después)")
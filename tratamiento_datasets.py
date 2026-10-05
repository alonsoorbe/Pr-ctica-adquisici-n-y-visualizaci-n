import pandas as pd
from IPython.display import display
import matplotlib.pyplot as plt



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


# Primero hacemos una función que nos permite ver y analizar el contenido de los ficheros
def exploration(df, nombre):
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

# Creamos los tres dataframes pedidos vacíos
partidos = pd.DataFrame()
eventos = pd.DataFrame()
jugadores = pd.DataFrame()

caracteristicas_partidos = ["fecha_partido", "ronda", "estadio", "ciudad_partido", "pais_partido", "seleccion_local", "seleccion_visitante", "marcador_local", "marcador_visitante", "prorroga", "penalty_local", "penalty_visitante", "arbitro_partido"]
caracteristicas_jugadores = ["seleccion_nacional", "club_jugador", "partidos_seleccion", "posicion", "valor_mercado", "partidos_jugados", "minutos_jugados", "goles", "asistencias", "tiros", "tarjetas_amarillas", "tarjetas_rojas", "paradas", "goles_concedidos", "calificacion_media"]
caracteristicas_eventos = ["minuto_evento", "index_partido", "nombre_jugador", "tipo_evento", "seleccion_evento"]

# DataFrame de partidos
# Mediante merges, cogeremos DataFrame a DataFrame para ver que relación tiene e ir haciendo merges poco a poco
# Primero cogemos de base el matches_mundial_seis_df, que es el que más datos tiene
# Cogeremos ciertos DataFrames basandonos el DataFRames que tengan información que necesitamos y alguna relación con nuestro DataFrame base, lo hacemos observando todos los csv
national_teams_df = national_teams_df.dropna(subset=["team_id"]).drop_duplicates(subset="team_id")
match_register_df = match_register_df.dropna(subset=["match_id"])                    # 15 filas vacías
match_register_df = match_register_df.drop_duplicates(subset="event_id", keep="first")  # mismo evento repetido

partidos = matches_mundial_seis_df.merge(index_referees_df, on = "referee_id", how = "left")
partidos = partidos.rename(columns= {"country": "ref_country"})
partidos = partidos.merge(tournament_stages_df, on = "stage_id", how = "left")
partidos = partidos.merge(worldcup_venues_df, on = "venue_id", how = "left")
partidos = partidos.merge(national_teams_df, left_on = "home_team_id", right_on = "team_id", how = "left")
partidos = partidos.rename(columns = {"team_name": "seleccion_local"})
partidos = partidos.merge(national_teams_df, left_on = "away_team_id", right_on = "team_id",how = "left", suffixes=("", "_away"))
partidos = partidos.rename(columns = {"team_name": "seleccion_visitante"})
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
partidos = partidos[caracteristicas_partidos]
partidos.index.name = "index_partido"


# DataFrame de jugadores
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
jugadores = jugadores.set_index("player_name")
jugadores.index.name = "nombre_jugador"
jugadores = jugadores[caracteristicas_jugadores]

# DataFrame de eventos
eventos = match_register_df.merge(national_teams_df, on = "team_id", how = "left")
eventos = eventos.merge(player_stats_df, on = "player_id", how = "left")
eventos = eventos.rename(columns = {
    "minute": "minuto_evento",
    "match_id": "index_partido",
    "player_name": "nombre_jugador",
    "event_type": "tipo_evento",
    "team_name": "seleccion_evento"})
eventos = eventos[caracteristicas_eventos]
eventos.index.name = "index_evento"


# Limpiaza de datos, duplicados, nulos...

#Primero observamos visualmente los nulos con una gráfica
claves = {
    "partidos":  (partidos,  ["index_partido"]),
    "jugadores": (jugadores, ["nombre_jugador"]),
    "eventos":   (eventos,   ["index_partido", "minuto_evento", "nombre_jugador", "tipo_evento"]),
}

resumen = pd.DataFrame({
    nombre: {
        "Duplicados exactos": df.reset_index().duplicated().sum(),
        "Duplicados de negocio": df.reset_index().duplicated(subset=clave).sum(),
    }
    for nombre, (df, clave) in claves.items()
})

display(resumen)

ax = resumen.plot(kind="bar", rot=0, title="Duplicados por DataFrame antes de la limpieza")
ax.set_ylabel("Nº de filas")
for cont in ax.containers:
    ax.bar_label(cont)
plt.tight_layout()
plt.show()

#Empezamos con valores duplicados generales
def duplicados_generales(df, nombre):
    print(f"Número de duplicados exactos en {nombre}: {df.duplicated().sum()}")
    df = df.drop_duplicates()
    print(f"Número de duplicados después: {df.duplicated().sum()}")

# Ahora iremos DataFrame a DataFrame quitando los duplicados de negocio en las columnas índices
def duplicados_negocio_index(df, columna, nombre_df):
    print(f"Número de duplicados de negocio en {nombre_df}: {df.index.duplicated().sum()}")
    df = df.reset_index()
    df["nulos"] = df.isna().sum(axis = 1)
    df = df.sort_values(by= "nulos", ascending = True)
    df = df.drop_duplicates(subset = columna, keep = "first")
    df = df.drop(columns = "nulos").set_index(columna)
    print(f"Número de duplicados de negocio en {nombre_df} después de eliminarlos: {df.index.duplicated().sum()}")

duplicados_negocio_index(partidos, "index_partido", "partidos")
duplicados_negocio_index(jugadores, "nombre_jugador", "jugadores")
eventos = eventos.drop_duplicates(subset=["index_partido", "minuto_evento", "nombre_jugador", "tipo_evento"],keep="first")

def anomalos_numerica(df, nombre):
    num = df.select_dtypes(include="number") # solo columnas numéricas
    print(f"\n===== {nombre} (numéricas) =====")
    print(num.describe())
    print("Nulos:\n", num.isna().sum())
    print("Negativos:\n", (num < 0).sum())

def anomalos_categorica(df, nombre):
    cat = df.select_dtypes(exclude="number") # columnas no numéricas
    print(f"\n===== {nombre} (categóricas) =====")
    print((cat.isna().mean() * 100).round(2))
    for col in cat.columns:
        print(f"\n--- {col} ---\n", cat[col].map(repr).value_counts(dropna=False).head(10))

def nulos(df, nombre):
    anomalos_categorica(df, nombre)
    anomalos_numerica(df, nombre)

nulos(partidos, "partidos")
#Empezamos limpiando los datos anomalos de partidos
partidos["pais_partido"] = partidos["pais_partido"].replace("USA", "usa")
for col in ["penalty_local", "penalty_visitante"]:
    partidos[col] = (partidos[col] / 10).fillna(0).astype(int)


#if __name__ == "__main__":
    #exploration(worldcup_venues_df, "worldcup")
    #display(partidos.head())
    #display(jugadores.head())
    #display(eventos.head())
    #duplicados_generales(partidos, "partidos")
    #duplicados_generales(jugadores, "jugadores")
    #duplicados_generales(eventos, "eventos")

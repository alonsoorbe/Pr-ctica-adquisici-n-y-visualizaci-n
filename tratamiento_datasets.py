import pandas as pd
from IPython.display import display



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

#Creamos los tres dataframes pedidos vacíos
partidos = pd.DataFrame()
eventos = pd.DataFrame()
jugadores = pd.DataFrame()

caracteristicas_partidos = ["fecha_partido", "ronda", "estadio", "ciudad_partido", "pais_partido", "selccion_local", "selccion_visitante", "marcador_local", "marcador_visitante", "prorroga", "penlty_local", "pelanty_visitante", "arbitro_partido"]
caracteristicas_jugadores = ["seleccion_nacional", "club_jugador", "partido_seleccion", "posicion", "valor_mercado", "partidos_jugados", "minutos_jugados", "goles", "asistencias", "tiros", "tarjetas_amarillas", "tarjetas_rojas", "paradas", "goles_concedidos", "calificacion_media"]
caracteristicas_eventos = ["minuto_evento", "index_partido", "nombre_jugador", "tipo_evento", "seleccion_evento"]



if __name__ == "__main__":
    exploration(worldcup_venues_df, "worldcup")

"""
Geolocalización de estadios con OpenStreetMap (Nominatim).

Uso:
    python geolocalizar_estadios.py [excel_entrada] [excel_salida]

El Excel de entrada debe tener una columna «estadio» y, opcionalmente, «ciudad» y «pais»
(códigos de 3 letras: USA, MEX, CAN). El de salida añade latitud, longitud y la consulta usada.
"""
import re
import sys
import time

import pandas as pd
import requests

URL_NOMINATIM = "https://nominatim.openstreetmap.org/search"
HEADERS = {"User-Agent": "imat-adquisicion-mundial2026-grupo3/1.0 (proyecto docente, Comillas ICAI)"}
CODIGOS_PAIS = {"USA": "us", "MEX": "mx", "CAN": "ca"}
PAUSA = 1.1                          


# Algunos estadios llevan su nombre en paréntesis con un nombre anterior el cual no es el habitual, por lo que separamos los nombres
def separar_nombres(estadio):
    """'Dallas Stadium (AT&T Stadium)' -> ('Dallas Stadium', 'AT&T Stadium')."""
    coincidencia = re.match(r"^\s*(.+?)\s*\((.+)\)\s*$", estadio)
    if coincidencia:
        return coincidencia.group(1), coincidencia.group(2)
    return estadio.strip(), None


def consultar(texto, codigo_pais=None):
    """Hace una búsqueda en Nominatim y devuelve el primer resultado (o None)."""
    params = {"q": texto, "format": "jsonv2", "limit": 1}
    if codigo_pais:
        params["countrycodes"] = codigo_pais
    r = requests.get(URL_NOMINATIM, params=params, headers=HEADERS, timeout=10)
    r.raise_for_status()
    time.sleep(PAUSA)
    resultados = r.json()
    return resultados[0] if resultados else None


def geolocalizar(estadio, ciudad=None, pais=None):
    """Prueba varias consultas, de la más precisa a la más general."""
    nombre_fifa, nombre_comercial = separar_nombres(estadio)
    codigo_pais = CODIGOS_PAIS.get(str(pais).upper()) if pais else None

    # Vemos que nombre es el adecuado
    candidatas = []
    if nombre_comercial:
        candidatas += [f"{nombre_comercial}, {ciudad}" if ciudad else nombre_comercial, nombre_comercial]
    candidatas += [f"{nombre_fifa}, {ciudad}" if ciudad else nombre_fifa]

    for consulta in candidatas:
        resultado = consultar(consulta, codigo_pais)
        if resultado:
            return {"latitud": float(resultado["lat"]), "longitud": float(resultado["lon"]),
                    "consulta": consulta, "nombre_osm": resultado.get("display_name")}
    return {"latitud": None, "longitud": None, "consulta": None, "nombre_osm": None}


def main(entrada, salida):
    estadios = pd.read_excel(entrada)
    if "estadio" not in estadios.columns:
        raise ValueError("El Excel de entrada debe tener una columna 'estadio'")

    filas = []
    for i, fila in estadios.iterrows():
        info = geolocalizar(fila["estadio"], fila.get("ciudad"), fila.get("pais"))
        estado = "Bien" if info["latitud"] is not None else "Mal"
        print(f"{estado} [{i + 1}/{len(estadios)}] {fila['estadio']} -> {info['latitud']}, {info['longitud']}")
        filas.append(info)

    resultado = pd.concat([estadios, pd.DataFrame(filas)], axis=1)

    # Comprobación: todos los estadios del Mundial 2026 están en Norteamérica
    fuera = ~(resultado["latitud"].between(14, 60) & resultado["longitud"].between(-130, -60))
    if fuera.any():
        print(" Revisar (sin resultado o fuera de Norteamérica):", resultado.loc[fuera, "estadio"].tolist())

    resultado.to_excel(salida, index=False)
    print(f"\nGuardado en {salida}: {resultado['latitud'].notna().sum()} de {len(resultado)} estadios localizados")


if __name__ == "__main__":
    entrada = sys.argv[1] if len(sys.argv) > 1 else "estadios_WC26.xlsx"
    salida = sys.argv[2] if len(sys.argv) > 2 else "estadios_WC26_coordenadas.xlsx"
    main(entrada, salida)

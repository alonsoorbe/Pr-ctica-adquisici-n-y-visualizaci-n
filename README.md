# Adquisición y Visualización de Datos – Análisis del Mundial 2026

Proyecto colaborativo (Grado IMAT, Comillas ICAI, curso 2026/27) – Grupo 3.
Integrantes (usuarios de GitHub): `alonsoorbe`, `dsegarraseco-lgtm`.

El proyecto analiza los partidos, eventos y jugadores del Mundial 2026 y lo complementa con datos de APIs externas. Se ha desarrollado de forma colaborativa con una rama por bloque (`bloque-1` … `bloque-4`), integradas en `main`.

## Estructura

| Carpeta | Contenido |
|---|---|
| `Bloque1/` | `tratamiento_datasets.py` (limpieza e imputación), `datasetsWC26/` (CSV originales) y los 3 Excel resultantes |
| `Bloque2/` | `visualizacion.py` (Streamlit + Plotly), presentación `.pptx` y los 3 Excel de entrada |
| `Bloque3/` | Cuadro de mando de Power BI (`.pbix`) y los 3 Excel |
| `Bloque4/` | `conexion_api.ipynb` (APIs), `geolocalizar_estadios.py`, `dashboard_estadios.py`, Excel de estadios y `cache_api/` |

## Instalación

```
pip install -r requirements.txt
```

## Cómo ejecutar cada bloque

Ejecuta cada comando desde la carpeta del bloque correspondiente.

- **Bloque 1:** `cd Bloque1` y `python tratamiento_datasets.py` (genera `partidosWC26.xlsx`, `eventosWC26.xlsx` y `jugadoresWC2026.xlsx`).
- **Bloque 2:** `cd Bloque2` y `streamlit run visualizacion.py`.
- **Bloque 3:** abrir `Bloque3/bloque_3_powwrbi.pbix` con Power BI Desktop.
- **Bloque 4:**
  1. `cd Bloque4`
  2. Copiar `.env.example` a `.env` y escribir tu clave de football-data.org en `API_FOOTBALL_KEY` (el `.env` no se sube al repositorio).
  3. Abrir y ejecutar `conexion_api.ipynb`. Las respuestas de la API ya guardadas en `cache_api/` se reutilizan para no gastar llamadas.
  4. Geolocalizar estadios: `python geolocalizar_estadios.py estadios_WC26.xlsx estadios_WC26_coordenadas.xlsx`
  5. Dashboard de estadios: `streamlit run dashboard_estadios.py`

## Flujo de trabajo con Git

Una rama por bloque, commits por cambio e integración en `main` mediante merge. `main` contiene la versión final completa del proyecto.

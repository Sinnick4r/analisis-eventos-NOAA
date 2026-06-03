import os
from pathlib import Path
from typing import Final

import pandas as pd
import streamlit as st

from noaa_eventos.presentacion import graficos_altair as graficos
from noaa_eventos import metricas
from noaa_eventos.metricas import calcular_kpis

# ruta de datos configurable, sin hardcodear nada absoluto
DIR_PROCESADO: Final[Path] = Path(
    os.environ.get("NOAA_DIR_PROCESADO", "data/processed")
)
ARCHIVO_DETAILS: Final[str] = "StormEvents_details_Limpio.csv"
ARCHIVO_FATALITIES: Final[str] = "StormEvents_fatalities_Limpio.csv"

TOP_N: Final[int] = 10


@st.cache_data
def cargar_csv(ruta: Path) -> pd.DataFrame:
    # cachea la lectura del disco para no releer en cada interaccion
    return pd.read_csv(ruta)


def cargar_dataset(
    nombre_archivo: str,
    archivo_subido: object | None,
) -> pd.DataFrame | None:
    # prioriza lo que suba el usuario; si no, cae al CSV procesado local
    if archivo_subido is not None:
        return pd.read_csv(archivo_subido)

    ruta = DIR_PROCESADO / nombre_archivo
    if not ruta.exists():
        return None  # degradacion elegante: sin dato, sin crash

    return cargar_csv(ruta)


def mostrar_kpis(details: pd.DataFrame, fatalities: pd.DataFrame) -> None:
    kpis = calcular_kpis(details, fatalities)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Eventos", f"{kpis.total_eventos:,}")
    col2.metric(
        "Daños estimados",
        f"USD {kpis.danios_estimados_totales / 1_000_000:,.1f} M",
    )
    col3.metric("Muertes", f"{kpis.muertes_totales:,}")
    col4.metric("Lesiones", f"{kpis.lesiones_totales:,}")


def mostrar_charts(
    details: pd.DataFrame,
    fatalities: pd.DataFrame | None,
) -> None:
    # el grafico protagonista (danios) va primero y a todo el ancho
    st.altair_chart(
        graficos.grafico_top_estados_danios(
            metricas.top_estados_danios(details, n=TOP_N)
        ),
        width="stretch",
        theme=None,
    )

    izquierda, derecha = st.columns(2)
    with izquierda:
        st.altair_chart(
            graficos.grafico_top_tipos_evento(
                metricas.top_tipos_evento(details, n=TOP_N)
            ),
            width="stretch",
            theme=None,
        )
    with derecha:
        st.altair_chart(
            graficos.grafico_top_estados_eventos(
                metricas.top_estados_eventos(details, n=TOP_N)
            ),
            width="stretch",
            theme=None,
        )

    st.altair_chart(
        graficos.grafico_eventos_por_mes(metricas.eventos_por_mes(details)),
        width="stretch",
        theme=None,
    )

    if fatalities is None:
        st.caption("Sin dataset de fatalities: se omite ese gráfico.")
        return

    st.altair_chart(
        graficos.grafico_fatalidades_por_tipo(
            metricas.fatalidades_por_tipo(fatalities)
        ),
        width="stretch",
        theme=None,
    )


def main() -> None:
    st.set_page_config(
        page_title="NOAA Storm Events",
        layout="wide",
    )
    st.title("NOAA Storm Events")
    st.write("Dashboard reproducible sobre datos oficiales de NOAA/NCEI.")

    with st.sidebar:
        st.header("Datos")
        st.write("Subí tus CSV procesados o usá los del repo.")
        details_subido = st.file_uploader("details (CSV)", type="csv")
        fatalities_subido = st.file_uploader("fatalities (CSV)", type="csv")

    details = cargar_dataset(ARCHIVO_DETAILS, details_subido)
    fatalities = cargar_dataset(ARCHIVO_FATALITIES, fatalities_subido)

    if details is None:
        st.warning(
            "No encontré el dataset de details. Subí el CSV en la barra "
            "lateral o corré el pipeline para generarlo."
        )
        st.stop()

    # fatalities es opcional: si falta, KPIs sin esa fuente
    fatalities_kpis = (
        fatalities
        if fatalities is not None
        else pd.DataFrame({"event_id": []})
    )

    mostrar_kpis(details, fatalities_kpis)
    st.divider()
    mostrar_charts(details, fatalities)


main()

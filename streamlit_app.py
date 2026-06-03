import os
from collections.abc import Callable
from pathlib import Path
from typing import Final

import altair as alt
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
ARCHIVO_LOCATIONS: Final[str] = "StormEvents_locations_Limpio.csv"

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


def construir_filtros(details: pd.DataFrame) -> tuple[list[str], list[str]]:
    # las opciones salen del dataset completo, no del filtrado
    estados = sorted(details["state"].dropna().unique())
    tipos = sorted(details["event_type"].dropna().unique())

    with st.sidebar:
        st.header("Filtros")
        sel_estados = st.multiselect("Estado", estados)
        sel_tipos = st.multiselect("Tipo de evento", tipos)

    return sel_estados, sel_tipos


def chart_o_aviso(
    datos: pd.DataFrame,
    constructor: Callable[[pd.DataFrame], alt.Chart],
) -> None:
    # muestra el grafico o un aviso corto si la seleccion quedo vacia
    if datos.empty:
        st.info("Sin datos para esta selección")
        return

    st.altair_chart(constructor(datos), width="stretch", theme=None)


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


def mostrar_mapa(
    locations: pd.DataFrame | None,
    details: pd.DataFrame,
) -> None:
    if locations is None:
        st.caption("Sin dataset de locations: se omite el mapa.")
        return

    # el cruce con details ya filtrado aplica los filtros al mapa
    chart_o_aviso(
        metricas.puntos_mapa(locations, details),
        graficos.mapa_eventos,
    )


def mostrar_charts(
    details: pd.DataFrame,
    fatalities: pd.DataFrame | None,
) -> None:
    # el grafico protagonista (danios) va primero y a todo el ancho
    chart_o_aviso(
        metricas.top_estados_danios(details, n=TOP_N),
        graficos.grafico_top_estados_danios,
    )

    izquierda, derecha = st.columns(2)
    with izquierda:
        chart_o_aviso(
            metricas.top_tipos_evento(details, n=TOP_N),
            graficos.grafico_top_tipos_evento,
        )
    with derecha:
        chart_o_aviso(
            metricas.top_estados_eventos(details, n=TOP_N),
            graficos.grafico_top_estados_eventos,
        )

    chart_o_aviso(
        metricas.eventos_por_mes(details),
        graficos.grafico_eventos_por_mes,
    )

    if fatalities is None:
        st.caption("Sin dataset de fatalities: se omite ese gráfico.")
        return

    chart_o_aviso(
        metricas.fatalidades_por_tipo(fatalities),
        graficos.grafico_fatalidades_por_tipo,
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
    locations = cargar_dataset(ARCHIVO_LOCATIONS, None)

    if details is None:
        st.warning(
            "No encontré el dataset de details. Subí el CSV en la barra "
            "lateral o corré el pipeline para generarlo."
        )
        st.stop()

    sel_estados, sel_tipos = construir_filtros(details)
    details_filtrado = metricas.filtrar_eventos(
        details,
        estados=sel_estados,
        tipos_evento=sel_tipos,
    )

    # fatalities sigue al filtro de details; si falta, queda None
    fatalities_filtrado = (
        metricas.filtrar_fatalities_por_eventos(fatalities, details_filtrado)
        if fatalities is not None
        else None
    )

    st.caption(f"{len(details_filtrado):,} eventos en la selección")

    # KPIs: fatalities vacio si falta el dataset
    fatalities_kpis = (
        fatalities_filtrado
        if fatalities_filtrado is not None
        else pd.DataFrame({"event_id": []})
    )

    mostrar_kpis(details_filtrado, fatalities_kpis)
    st.divider()
    mostrar_mapa(locations, details_filtrado)
    mostrar_charts(details_filtrado, fatalities_filtrado)


main()

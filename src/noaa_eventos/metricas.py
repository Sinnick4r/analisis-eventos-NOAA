from dataclasses import dataclass
from typing import Final

import pandas as pd

# NOAA codifica el tipo de fatalidad con una sola letra
ETIQUETAS_FATALIDAD: Final[dict[str, str]] = {
    "D": "Directa",
    "I": "Indirecta",
}


def filtrar_eventos(
    details: pd.DataFrame,
    *,
    estados: list[str] | None = None,
    tipos_evento: list[str] | None = None,
) -> pd.DataFrame:
    # filtra details por estado y/o tipo; None o lista vacia = sin filtro
    filtrado = details

    if estados:
        filtrado = filtrado[filtrado["state"].isin(estados)]

    if tipos_evento:
        filtrado = filtrado[filtrado["event_type"].isin(tipos_evento)]

    return filtrado


def filtrar_fatalities_por_eventos(
    fatalities: pd.DataFrame,
    details_filtrado: pd.DataFrame,
) -> pd.DataFrame:
    # se queda con las fatalidades de los eventos que pasaron el filtro
    ids = details_filtrado["event_id"].unique()

    return fatalities[fatalities["event_id"].isin(ids)]


def eventos_por_mes(details: pd.DataFrame) -> pd.DataFrame:
    # cuenta eventos por mes, ordenado cronologicamente
    conteo = (
        details.assign(mes=details["begin_yearmonth"].astype(str))
        .groupby("mes")
        .size()
        .sort_index()
    )

    return conteo.rename("eventos").reset_index()


def top_tipos_evento(
    details: pd.DataFrame,
    *,
    n: int = 10,
) -> pd.DataFrame:
    # top N tipos de evento por cantidad
    conteo = details["event_type"].value_counts().head(n)

    return conteo.rename("eventos").rename_axis("event_type").reset_index()


def top_estados_eventos(
    details: pd.DataFrame,
    *,
    n: int = 10,
) -> pd.DataFrame:
    # top N estados por cantidad de eventos
    conteo = details["state"].value_counts().head(n)

    return conteo.rename("eventos").rename_axis("state").reset_index()


def top_estados_danios(
    details: pd.DataFrame,
    *,
    n: int = 10,
) -> pd.DataFrame:
    # top N estados por danios totales, con columna en millones de USD
    danios = details["damage_property"].fillna(0) + details[
        "damage_crops"
    ].fillna(0)

    agregado = (
        details.assign(danios_totales=danios)
        .groupby("state", as_index=False)["danios_totales"]
        .sum()
        .nlargest(n, "danios_totales")
    )
    agregado["danios_millones"] = agregado["danios_totales"] / 1_000_000

    return agregado


def fatalidades_por_tipo(fatalities: pd.DataFrame) -> pd.DataFrame:
    # cuenta fatalidades por tipo, con la letra NOAA mapeada a texto
    # fillna preserva cualquier valor inesperado en vez de descartarlo
    etiquetas = (
        fatalities["fatality_type"]
        .map(ETIQUETAS_FATALIDAD)
        .fillna(fatalities["fatality_type"])
    )
    conteo = etiquetas.value_counts()

    return (
        conteo.rename("registros").rename_axis("tipo_fatalidad").reset_index()
    )


@dataclass(frozen=True, slots=True)
class KpisBi:
    # KPIs principales

    total_eventos: int
    estados_afectados: int
    tipos_evento: int
    danios_estimados_totales: float
    muertes_totales: int
    lesiones_totales: int
    eventos_con_fatalidades: int


def calcular_kpis(
    details: pd.DataFrame,
    fatalities: pd.DataFrame,
) -> KpisBi:
    # calcula KPIs principales

    danios_propiedad = details.get(
        "damage_property",
        pd.Series(dtype="float64"),
    ).fillna(0)

    danios_cultivos = details.get(
        "damage_crops",
        pd.Series(dtype="float64"),
    ).fillna(0)

    muertes_directas = details.get(
        "deaths_direct",
        pd.Series(dtype="int64"),
    ).fillna(0)

    muertes_indirectas = details.get(
        "deaths_indirect",
        pd.Series(dtype="int64"),
    ).fillna(0)

    lesiones_directas = details.get(
        "injuries_direct",
        pd.Series(dtype="int64"),
    ).fillna(0)

    lesiones_indirectas = details.get(
        "injuries_indirect",
        pd.Series(dtype="int64"),
    ).fillna(0)

    return KpisBi(
        total_eventos=len(details),
        estados_afectados=int(details["state"].nunique()),
        tipos_evento=int(details["event_type"].nunique()),
        danios_estimados_totales=float(
            danios_propiedad.sum() + danios_cultivos.sum()
        ),
        muertes_totales=int(muertes_directas.sum() + muertes_indirectas.sum()),
        lesiones_totales=int(
            lesiones_directas.sum() + lesiones_indirectas.sum()
        ),
        eventos_con_fatalidades=int(fatalities["event_id"].nunique()),
    )

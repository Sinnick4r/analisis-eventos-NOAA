from typing import Final

import pandas as pd

# NOAA codifica el tipo de fatalidad con una sola letra
ETIQUETAS_FATALIDAD: Final[dict[str, str]] = {
    "D": "Directa",
    "I": "Indirecta",
}


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

    return conteo.rename("registros").rename_axis("tipo_fatalidad").reset_index()

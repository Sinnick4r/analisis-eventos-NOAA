import pandas as pd

from noaa_eventos.limpieza import (
    limpiar_strings_vacios,
    normalizar_columnas,
)
from noaa_eventos.validacion import (
    validar_columnas_obligatorias,
    validar_columnas_sin_nulos,
)

COLUMNAS_OBLIGATORIAS_LOCATIONS: frozenset[str] = frozenset(
    {
        "event_id",
        "location_index",
    }
)


def procesar_locations(datos: pd.DataFrame) -> pd.DataFrame:
    # Procesa el dataset NOAA Storm Events locations.

    datos_procesados = normalizar_columnas(datos)
    datos_procesados = limpiar_strings_vacios(datos_procesados)

    validar_columnas_obligatorias(
        datos_procesados,
        COLUMNAS_OBLIGATORIAS_LOCATIONS,
    )
    validar_columnas_sin_nulos(
        datos_procesados,
        COLUMNAS_OBLIGATORIAS_LOCATIONS,
    )
    validar_clave_locations_unica(datos_procesados)

    return datos_procesados


def validar_clave_locations_unica(datos: pd.DataFrame) -> None:
    # Valida unicidad de la clave event_id + location_index.

    columnas_clave = ["event_id", "location_index"]
    mascara_duplicados = datos.duplicated(
        subset=columnas_clave,
        keep=False,
    )

    if not mascara_duplicados.any():
        return

    claves_duplicadas = datos.loc[
        mascara_duplicados,
        columnas_clave,
    ].to_dict(orient="records")

    raise ValueError(
        "Locations contiene claves duplicadas "
        f"event_id + location_index: {claves_duplicadas}"
    )

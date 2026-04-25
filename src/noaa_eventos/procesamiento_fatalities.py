import pandas as pd

from noaa_eventos.limpieza import (
    limpiar_strings_vacios,
    normalizar_columnas,
)
from noaa_eventos.validacion import (
    validar_columna_sin_duplicados,
    validar_columnas_obligatorias,
    validar_columnas_sin_nulos,
)

COLUMNAS_OBLIGATORIAS_FATALITIES: frozenset[str] = frozenset(
    {
        "fatality_id",
        "event_id",
        "fatality_type",
        "fatality_date",
    }
)


def procesar_fatalities(datos: pd.DataFrame) -> pd.DataFrame:
    #Procesa el dataset NOAA Storm Events fatalities.

    datos_procesados = normalizar_columnas(datos)
    datos_procesados = limpiar_strings_vacios(datos_procesados)

    validar_columnas_obligatorias(
        datos_procesados,
        COLUMNAS_OBLIGATORIAS_FATALITIES,
    )
    validar_columnas_sin_nulos(
        datos_procesados,
        COLUMNAS_OBLIGATORIAS_FATALITIES,
    )
    validar_columna_sin_duplicados(datos_procesados, "fatality_id")

    return datos_procesados

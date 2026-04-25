import pandas as pd

from noaa_eventos.danios import convertir_danio_estimado
from noaa_eventos.limpieza import (
    limpiar_strings_vacios,
    normalizar_columnas,
)
from noaa_eventos.validacion import (
    validar_columna_sin_duplicados,
    validar_columnas_obligatorias,
    validar_columnas_sin_nulos,
)

COLUMNAS_OBLIGATORIAS_DETAILS: frozenset[str] = frozenset(
    {
        "event_id",
        "episode_id",
        "event_type",
        "state",
        "begin_date_time",
        "end_date_time",
    }
)

COLUMNAS_DANIO_DETAILS: tuple[str, ...] = (
    "damage_property",
    "damage_crops",
)


def procesar_details(datos: pd.DataFrame) -> pd.DataFrame:
    """Procesa el dataset NOAA Storm Events details.

    Side effects:
        No tiene. No modifica el DataFrame recibido.

    Raises:
        ValueError: Si faltan columnas críticas, hay nulos críticos,
        event_id duplicado o daños con formato inválido.
    """
    datos_procesados = normalizar_columnas(datos)
    datos_procesados = limpiar_strings_vacios(datos_procesados)

    validar_columnas_obligatorias(
        datos_procesados,
        COLUMNAS_OBLIGATORIAS_DETAILS,
    )
    validar_columnas_sin_nulos(
        datos_procesados,
        COLUMNAS_OBLIGATORIAS_DETAILS,
    )
    validar_columna_sin_duplicados(datos_procesados, "event_id")

    return convertir_columnas_danio_details(datos_procesados)


def convertir_columnas_danio_details(datos: pd.DataFrame) -> pd.DataFrame:
    """Convierte columnas de daños de details si están presentes.

    Side effects:
        No tiene. No modifica el DataFrame recibido.
    """
    datos_convertidos = datos.copy()

    for columna in COLUMNAS_DANIO_DETAILS:
        if columna not in datos_convertidos.columns:
            continue

        datos_convertidos[columna] = datos_convertidos[columna].map(
            convertir_danio_estimado
        )

    return datos_convertidos

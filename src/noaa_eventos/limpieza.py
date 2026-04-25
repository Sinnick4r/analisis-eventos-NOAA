import re
import unicodedata
from typing import Final

import pandas as pd

PATRON_CARACTERES_NO_VALIDOS: Final[re.Pattern[str]] = re.compile(
    r"[^a-z0-9_]+"
)
PATRON_GUIONES_BAJOS_MULTIPLES: Final[re.Pattern[str]] = re.compile(r"_+")


def normalizar_nombre_columna(nombre_columna: str) -> str:
    #Normaliza un nombre de columna a formato snake_case simple

    nombre_normalizado = unicodedata.normalize("NFKD", nombre_columna)
    nombre_ascii = nombre_normalizado.encode("ascii", "ignore").decode("ascii")
    nombre_limpio = nombre_ascii.strip().lower()
    nombre_limpio = re.sub(r"\s+", "_", nombre_limpio)
    nombre_limpio = PATRON_CARACTERES_NO_VALIDOS.sub("_", nombre_limpio)
    nombre_limpio = PATRON_GUIONES_BAJOS_MULTIPLES.sub("_", nombre_limpio)

    return nombre_limpio.strip("_")


def normalizar_columnas(datos: pd.DataFrame) -> pd.DataFrame:
    #Devuelve una copia del DataFrame con columnas normalizadas

    columnas_normalizadas = {
        columna: normalizar_nombre_columna(str(columna))
        for columna in datos.columns
    }

    return datos.rename(columns=columnas_normalizadas)


def limpiar_strings_vacios(datos: pd.DataFrame) -> pd.DataFrame:
    #Reemplaza strings vacíos o solo espacios por valores nulos.
    return datos.replace(r"^\s*$", pd.NA, regex=True)

from pathlib import Path

import pandas as pd


def leer_csv(
    ruta: Path,
    *,
    encoding: str = "utf-8",
) -> pd.DataFrame:
    # Lee un archivo CSV y devuelve un DF

    if not ruta.exists():
        raise FileNotFoundError(f"No existe el archivo: {ruta}")

    return pd.read_csv(ruta, encoding=encoding)


def guardar_csv(
    datos: pd.DataFrame,
    ruta: Path,
    *,
    encoding: str = "utf-8",
) -> None:
    # Guarda un DataFrame como CSV sin indice

    ruta.parent.mkdir(parents=True, exist_ok=True)
    datos.to_csv(ruta, index=False, encoding=encoding)

import pandas as pd
import pytest

from noaa_eventos.validacion import (
    validar_columna_sin_duplicados,
    validar_columnas_obligatorias,
    validar_columnas_sin_nulos,
)


def test_validar_columnas_obligatorias_no_falla_si_estan_presentes() -> None:
    datos = pd.DataFrame(
        {
            "event_id": [1],
            "event_type": ["Flood"],
            "state": ["TEXAS"],
        }
    )

    validar_columnas_obligatorias(
        datos,
        frozenset({"event_id", "event_type"}),
    )


def test_validar_columnas_obligatorias_falla_si_faltan_columnas() -> None:
    datos = pd.DataFrame({"event_id": [1]})

    with pytest.raises(ValueError, match="Faltan columnas obligatorias"):
        validar_columnas_obligatorias(
            datos,
            frozenset({"event_id", "event_type", "state"}),
        )


def test_validar_columna_sin_duplicados_acepta_unicos() -> None:
    datos = pd.DataFrame({"event_id": [1, 2, 3]})

    validar_columna_sin_duplicados(datos, "event_id")


def test_validar_columna_sin_duplicados_falla_si_columna_no_existe() -> None:
    datos = pd.DataFrame({"episode_id": [10, 20]})

    with pytest.raises(ValueError, match="No existe la columna requerida"):
        validar_columna_sin_duplicados(datos, "event_id")


def test_validar_columna_sin_duplicados_falla_si_hay_duplicados() -> None:
    datos = pd.DataFrame({"event_id": [1, 2, 2, 3]})

    with pytest.raises(ValueError, match="contiene valores duplicados"):
        validar_columna_sin_duplicados(datos, "event_id")

def test_validar_columnas_sin_nulos_no_falla_si_no_hay_nulos() -> None:
    datos = pd.DataFrame(
        {
            "event_id": [1, 2],
            "event_type": ["Flood", "Hail"],
        }
    )

    validar_columnas_sin_nulos(
        datos,
        frozenset({"event_id", "event_type"}),
    )

def test_validar_columnas_sin_nulos_falla_si_columna_no_existe() -> None:
    datos = pd.DataFrame({"event_id": [1, 2]})

    with pytest.raises(ValueError, match="Faltan columnas obligatorias"):
        validar_columnas_sin_nulos(
            datos,
            frozenset({"event_id", "event_type"}),
        )


def test_validar_columnas_sin_nulos_falla_si_hay_nulos() -> None:
    datos = pd.DataFrame(
        {
            "event_id": [1, 2, 3],
            "event_type": ["Flood", None, "Hail"],
        }
    )

    with pytest.raises(ValueError, match="Columnas con valores nulos"):
        validar_columnas_sin_nulos(
            datos,
            frozenset({"event_id", "event_type"}),
        )

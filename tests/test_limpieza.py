import pandas as pd
import pytest

from noaa_eventos.limpieza import (
    limpiar_strings_vacios,
    normalizar_columnas,
    normalizar_nombre_columna,
)


@pytest.mark.parametrize(
    ("nombre_original", "nombre_esperado"),
    [
        ("EVENT_ID", "event_id"),
        ("Begin Date Time", "begin_date_time"),
        ("Daño Propiedad", "dano_propiedad"),
        ("  Tipo Evento  ", "tipo_evento"),
        ("MAGNITUDE-TYPE", "magnitude_type"),
        ("Damage ($)", "damage"),
        ("CZ Timezone", "cz_timezone"),
    ],
)
def test_normalizar_nombre_columna(
    nombre_original: str,
    nombre_esperado: str,
) -> None:
    assert normalizar_nombre_columna(nombre_original) == nombre_esperado


def test_normalizar_columnas_no_modifica_dataframe_original() -> None:
    datos = pd.DataFrame(
        {
            "EVENT_ID": [1],
            "Begin Date Time": ["2024-01-01"],
        }
    )

    datos_normalizados = normalizar_columnas(datos)

    assert list(datos.columns) == ["EVENT_ID", "Begin Date Time"]
    assert list(datos_normalizados.columns) == [
        "event_id",
        "begin_date_time",
    ]


def test_limpiar_strings_vacios_reemplaza_espacios_por_na() -> None:
    datos = pd.DataFrame(
        {
            "event_id": [1, 2, 3],
            "event_type": ["Flood", "   ", ""],
        }
    )

    datos_limpios = limpiar_strings_vacios(datos)

    assert datos_limpios["event_type"].isna().tolist() == [
        False,
        True,
        True,
    ]


def test_limpiar_strings_vacios_no_modifica_dataframe_original() -> None:
    datos = pd.DataFrame({"event_type": ["   "]})

    datos_limpios = limpiar_strings_vacios(datos)

    assert datos.loc[0, "event_type"] == "   "
    assert pd.isna(datos_limpios.loc[0, "event_type"])

import pandas as pd
import pytest

from noaa_eventos.procesamiento_locations import procesar_locations


def test_procesar_locations_normaliza_y_valida_clave_compuesta() -> None:
    datos = pd.DataFrame(
        {
            "EVENT_ID": [1, 1, 2],
            "LOCATION_INDEX": [1, 2, 1],
            "LOCATION": ["AUSTIN", "ROUND ROCK", "TULSA"],
            "LATITUDE": [30.2672, 30.5083, 36.1540],
            "LONGITUDE": [-97.7431, -97.6789, -95.9928],
        }
    )

    datos_procesados = procesar_locations(datos)

    assert list(datos_procesados.columns) == [
        "event_id",
        "location_index",
        "location",
        "latitude",
        "longitude",
    ]
    assert datos_procesados["event_id"].tolist() == [1, 1, 2]


def test_procesar_locations_no_modifica_dataframe_original() -> None:
    datos = pd.DataFrame(
        {
            "EVENT_ID": [1],
            "LOCATION_INDEX": [1],
            "LOCATION": ["AUSTIN"],
        }
    )

    procesar_locations(datos)

    assert list(datos.columns) == [
        "EVENT_ID",
        "LOCATION_INDEX",
        "LOCATION",
    ]


def test_procesar_locations_falla_si_falta_columna_obligatoria() -> None:
    datos = pd.DataFrame(
        {
            "EVENT_ID": [1],
            "LOCATION": ["AUSTIN"],
        }
    )

    with pytest.raises(ValueError, match="Faltan columnas obligatorias"):
        procesar_locations(datos)


def test_procesar_locations_falla_si_hay_nulos_criticos() -> None:
    datos = pd.DataFrame(
        {
            "EVENT_ID": [1, 2],
            "LOCATION_INDEX": [1, None],
            "LOCATION": ["AUSTIN", "TULSA"],
        }
    )

    with pytest.raises(ValueError, match="Columnas con valores nulos"):
        procesar_locations(datos)


def test_procesar_locations_falla_si_clave_compuesta_esta_duplicada() -> None:
    datos = pd.DataFrame(
        {
            "EVENT_ID": [1, 1],
            "LOCATION_INDEX": [1, 1],
            "LOCATION": ["AUSTIN", "ROUND ROCK"],
        }
    )

    with pytest.raises(
        ValueError,
        match="Locations contiene claves duplicadas",
    ):
        procesar_locations(datos)

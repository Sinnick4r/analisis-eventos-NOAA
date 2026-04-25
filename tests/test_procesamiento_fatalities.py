import pandas as pd
import pytest

from noaa_eventos.procesamiento_fatalities import procesar_fatalities


def test_procesar_fatalities_normaliza_y_valida() -> None:
    datos = pd.DataFrame(
        {
            "FATALITY_ID": [100, 200],
            "EVENT_ID": [1, 2],
            "FATALITY_TYPE": ["Direct", "Indirect"],
            "FATALITY_DATE": ["2024-01-01", "2024-01-02"],
            "FATALITY_AGE": [45, 70],
        }
    )

    datos_procesados = procesar_fatalities(datos)

    assert list(datos_procesados.columns) == [
        "fatality_id",
        "event_id",
        "fatality_type",
        "fatality_date",
        "fatality_age",
    ]
    assert datos_procesados["fatality_id"].tolist() == [100, 200]


def test_procesar_fatalities_no_modifica_dataframe_original() -> None:
    datos = pd.DataFrame(
        {
            "FATALITY_ID": [100],
            "EVENT_ID": [1],
            "FATALITY_TYPE": ["Direct"],
            "FATALITY_DATE": ["2024-01-01"],
        }
    )

    procesar_fatalities(datos)

    assert list(datos.columns) == [
        "FATALITY_ID",
        "EVENT_ID",
        "FATALITY_TYPE",
        "FATALITY_DATE",
    ]


def test_procesar_fatalities_falla_si_falta_columna_obligatoria() -> None:
    datos = pd.DataFrame(
        {
            "FATALITY_ID": [100],
            "EVENT_ID": [1],
            "FATALITY_TYPE": ["Direct"],
        }
    )

    with pytest.raises(ValueError, match="Faltan columnas obligatorias"):
        procesar_fatalities(datos)


def test_procesar_fatalities_falla_si_hay_nulos_criticos() -> None:
    datos = pd.DataFrame(
        {
            "FATALITY_ID": [100, 200],
            "EVENT_ID": [1, None],
            "FATALITY_TYPE": ["Direct", "Indirect"],
            "FATALITY_DATE": ["2024-01-01", "2024-01-02"],
        }
    )

    with pytest.raises(ValueError, match="Columnas con valores nulos"):
        procesar_fatalities(datos)


def test_procesar_fatalities_falla_si_fatality_id_esta_duplicado() -> None:
    datos = pd.DataFrame(
        {
            "FATALITY_ID": [100, 100],
            "EVENT_ID": [1, 2],
            "FATALITY_TYPE": ["Direct", "Indirect"],
            "FATALITY_DATE": ["2024-01-01", "2024-01-02"],
        }
    )

    with pytest.raises(ValueError, match="contiene valores duplicados"):
        procesar_fatalities(datos)

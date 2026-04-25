import pandas as pd
import pytest

from noaa_eventos.procesamiento_details import procesar_details


def test_procesar_details_normaliza_valida_y_convierte_danios() -> None:
    datos = pd.DataFrame(
        {
            "EVENT_ID": [1, 2],
            "EPISODE_ID": [10, 20],
            "EVENT_TYPE": ["Flood", "Hail"],
            "STATE": ["TEXAS", "OKLAHOMA"],
            "BEGIN_DATE_TIME": ["2024-01-01 00:00:00", "2024-01-02 00:00:00"],
            "END_DATE_TIME": ["2024-01-01 01:00:00", "2024-01-02 01:00:00"],
            "DAMAGE_PROPERTY": ["10K", "1.5M"],
            "DAMAGE_CROPS": ["0", ""],
        }
    )

    datos_procesados = procesar_details(datos)

    assert list(datos_procesados.columns) == [
        "event_id",
        "episode_id",
        "event_type",
        "state",
        "begin_date_time",
        "end_date_time",
        "damage_property",
        "damage_crops",
    ]
    assert datos_procesados["damage_property"].tolist() == [
        10_000.0,
        1_500_000.0,
    ]
    assert datos_procesados.loc[0, "damage_crops"] == 0.0
    assert pd.isna(datos_procesados.loc[1, "damage_crops"])


def test_procesar_details_no_modifica_dataframe_original() -> None:
    datos = pd.DataFrame(
        {
            "EVENT_ID": [1],
            "EPISODE_ID": [10],
            "EVENT_TYPE": ["Flood"],
            "STATE": ["TEXAS"],
            "BEGIN_DATE_TIME": ["2024-01-01 00:00:00"],
            "END_DATE_TIME": ["2024-01-01 01:00:00"],
            "DAMAGE_PROPERTY": ["10K"],
        }
    )

    procesar_details(datos)

    assert list(datos.columns) == [
        "EVENT_ID",
        "EPISODE_ID",
        "EVENT_TYPE",
        "STATE",
        "BEGIN_DATE_TIME",
        "END_DATE_TIME",
        "DAMAGE_PROPERTY",
    ]
    assert datos.loc[0, "DAMAGE_PROPERTY"] == "10K"


def test_procesar_details_falla_si_falta_columna_obligatoria() -> None:
    datos = pd.DataFrame(
        {
            "EVENT_ID": [1],
            "EPISODE_ID": [10],
            "EVENT_TYPE": ["Flood"],
            "STATE": ["TEXAS"],
            "BEGIN_DATE_TIME": ["2024-01-01 00:00:00"],
        }
    )

    with pytest.raises(ValueError, match="Faltan columnas obligatorias"):
        procesar_details(datos)


def test_procesar_details_falla_si_event_id_esta_duplicado() -> None:
    datos = pd.DataFrame(
        {
            "EVENT_ID": [1, 1],
            "EPISODE_ID": [10, 20],
            "EVENT_TYPE": ["Flood", "Hail"],
            "STATE": ["TEXAS", "OKLAHOMA"],
            "BEGIN_DATE_TIME": ["2024-01-01 00:00:00", "2024-01-02 00:00:00"],
            "END_DATE_TIME": ["2024-01-01 01:00:00", "2024-01-02 01:00:00"],
        }
    )

    with pytest.raises(ValueError, match="contiene valores duplicados"):
        procesar_details(datos)


def test_procesar_details_falla_si_danio_tiene_formato_invalido() -> None:
    datos = pd.DataFrame(
        {
            "EVENT_ID": [1],
            "EPISODE_ID": [10],
            "EVENT_TYPE": ["Flood"],
            "STATE": ["TEXAS"],
            "BEGIN_DATE_TIME": ["2024-01-01 00:00:00"],
            "END_DATE_TIME": ["2024-01-01 01:00:00"],
            "DAMAGE_PROPERTY": ["12T"],
        }
    )

    with pytest.raises(ValueError, match="Formato de daño inválido"):
        procesar_details(datos)

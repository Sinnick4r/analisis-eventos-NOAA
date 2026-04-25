from pathlib import Path

import pandas as pd
import pytest

from noaa_eventos.flujo import RutasFlujoLocal, ejecutar_flujo_local


def test_ejecutar_flujo_local_procesa_y_guarda_salidas(
    tmp_path: Path,
) -> None:
    raw_dir = tmp_path / "raw"
    processed_dir = tmp_path / "processed"
    raw_dir.mkdir()

    details_raw = raw_dir / "details.csv"
    locations_raw = raw_dir / "locations.csv"
    fatalities_raw = raw_dir / "fatalities.csv"

    pd.DataFrame(
        {
            "EVENT_ID": [1, 2],
            "EPISODE_ID": [10, 20],
            "EVENT_TYPE": ["Flood", "Hail"],
            "STATE": ["TEXAS", "OKLAHOMA"],
            "BEGIN_DATE_TIME": [
                "2024-01-01 00:00:00",
                "2024-01-02 00:00:00",
            ],
            "END_DATE_TIME": [
                "2024-01-01 01:00:00",
                "2024-01-02 01:00:00",
            ],
            "DAMAGE_PROPERTY": ["10K", "1.5M"],
            "DAMAGE_CROPS": ["0", ""],
        }
    ).to_csv(details_raw, index=False)

    pd.DataFrame(
        {
            "EVENT_ID": [1, 1, 2],
            "LOCATION_INDEX": [1, 2, 1],
            "LOCATION": ["AUSTIN", "ROUND ROCK", "TULSA"],
        }
    ).to_csv(locations_raw, index=False)

    pd.DataFrame(
        {
            "FATALITY_ID": [100, 200],
            "EVENT_ID": [1, 2],
            "FATALITY_TYPE": ["Direct", "Indirect"],
            "FATALITY_DATE": ["2024-01-01", "2024-01-02"],
        }
    ).to_csv(fatalities_raw, index=False)

    rutas = RutasFlujoLocal(
        details_raw=details_raw,
        locations_raw=locations_raw,
        fatalities_raw=fatalities_raw,
        details_procesado=processed_dir / "details_limpio.csv",
        locations_procesado=processed_dir / "locations_limpio.csv",
        fatalities_procesado=processed_dir / "fatalities_limpio.csv",
    )

    ejecutar_flujo_local(rutas)

    details_procesado = pd.read_csv(rutas.details_procesado)
    locations_procesado = pd.read_csv(rutas.locations_procesado)
    fatalities_procesado = pd.read_csv(rutas.fatalities_procesado)

    assert rutas.details_procesado.exists()
    assert rutas.locations_procesado.exists()
    assert rutas.fatalities_procesado.exists()

    assert "event_id" in details_procesado.columns
    assert "event_id" in locations_procesado.columns
    assert "event_id" in fatalities_procesado.columns

    assert details_procesado.loc[0, "damage_property"] == 10_000.0
    assert details_procesado.loc[1, "damage_property"] == 1_500_000.0


def test_ejecutar_flujo_local_falla_si_falta_archivo(
    tmp_path: Path,
) -> None:
    rutas = RutasFlujoLocal(
        details_raw=tmp_path / "details.csv",
        locations_raw=tmp_path / "locations.csv",
        fatalities_raw=tmp_path / "fatalities.csv",
        details_procesado=tmp_path / "out" / "details_limpio.csv",
        locations_procesado=tmp_path / "out" / "locations_limpio.csv",
        fatalities_procesado=tmp_path / "out" / "fatalities_limpio.csv",
    )

    with pytest.raises(FileNotFoundError, match="No existe el archivo"):
        ejecutar_flujo_local(rutas)

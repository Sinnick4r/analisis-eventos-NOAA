from pathlib import Path

import pandas as pd
import pytest

from noaa_eventos.io import guardar_csv, leer_csv


def test_guardar_y_leer_csv(tmp_path: Path) -> None:
    ruta = tmp_path / "salida" / "eventos.csv"
    datos = pd.DataFrame(
        {
            "event_id": [1, 2],
            "event_type": ["Flood", "Hail"],
        }
    )

    guardar_csv(datos, ruta)
    datos_leidos = leer_csv(ruta)

    pd.testing.assert_frame_equal(datos, datos_leidos)


def test_leer_csv_falla_si_archivo_no_existe(tmp_path: Path) -> None:
    ruta = tmp_path / "inexistente.csv"

    with pytest.raises(FileNotFoundError, match="No existe el archivo"):
        leer_csv(ruta)

from datetime import date

import pytest

from noaa_eventos.archivos_noaa import (
    parsear_nombre_archivo_noaa,
    seleccionar_archivo_mas_reciente,
)


def test_parsear_nombre_archivo_noaa_extrae_metadata() -> None:
    archivo = parsear_nombre_archivo_noaa(
        "StormEvents_details-ftp_v1.0_d2026_c20260421.csv.gz"
    )

    assert archivo.nombre == (
        "StormEvents_details-ftp_v1.0_d2026_c20260421.csv.gz"
    )
    assert archivo.tipo == "details"
    assert archivo.version_ftp == "1.0"
    assert archivo.anio_datos == 2026
    assert archivo.fecha_creacion == date(2026, 4, 21)


def test_parsear_nombre_archivo_noaa_rechaza_nombre_invalido() -> None:
    with pytest.raises(ValueError, match="Nombre de archivo NOAA inválido"):
        parsear_nombre_archivo_noaa("details.csv")


def test_seleccionar_archivo_mas_reciente_por_tipo_y_anio() -> None:
    nombres = [
        "StormEvents_details-ftp_v1.0_d2026_c20260401.csv.gz",
        "StormEvents_details-ftp_v1.0_d2026_c20260421.csv.gz",
        "StormEvents_locations-ftp_v1.0_d2026_c20260430.csv.gz",
        "StormEvents_details-ftp_v1.0_d2025_c20260430.csv.gz",
    ]

    archivo = seleccionar_archivo_mas_reciente(
        nombres,
        tipo="details",
        anio_datos=2026,
    )

    assert archivo.nombre == (
        "StormEvents_details-ftp_v1.0_d2026_c20260421.csv.gz"
    )


def test_seleccionar_archivo_mas_reciente_falla_si_no_hay_match() -> None:
    with pytest.raises(FileNotFoundError, match="No se encontró archivo NOAA"):
        seleccionar_archivo_mas_reciente(
            [],
            tipo="fatalities",
            anio_datos=2026,
        )

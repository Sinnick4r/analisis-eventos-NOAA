from pathlib import Path

from noaa_eventos.cli import construir_rutas_desde_args, crear_parser


def test_crear_parser_parsea_modo_explicito(tmp_path: Path) -> None:
    parser = crear_parser()

    args = parser.parse_args(
        [
            "--details",
            str(tmp_path / "details.csv"),
            "--locations",
            str(tmp_path / "locations.csv"),
            "--fatalities",
            str(tmp_path / "fatalities.csv"),
            "--salida",
            str(tmp_path / "processed"),
        ]
    )

    assert args.details == tmp_path / "details.csv"
    assert args.locations == tmp_path / "locations.csv"
    assert args.fatalities == tmp_path / "fatalities.csv"
    assert args.salida == tmp_path / "processed"
    assert args.encoding == "utf-8"


def test_construir_rutas_desde_args_modo_explicito(
    tmp_path: Path,
) -> None:
    parser = crear_parser()
    args = parser.parse_args(
        [
            "--details",
            str(tmp_path / "raw" / "details.csv"),
            "--locations",
            str(tmp_path / "raw" / "locations.csv"),
            "--fatalities",
            str(tmp_path / "raw" / "fatalities.csv"),
            "--salida",
            str(tmp_path / "processed"),
        ]
    )

    rutas = construir_rutas_desde_args(args)

    assert rutas.details_raw == tmp_path / "raw" / "details.csv"
    assert rutas.locations_raw == tmp_path / "raw" / "locations.csv"
    assert rutas.fatalities_raw == tmp_path / "raw" / "fatalities.csv"


def test_construir_rutas_desde_args_modo_raw_dir(
    tmp_path: Path,
) -> None:
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()

    (raw_dir / "StormEvents_details-ftp_v1.0_d2026_c20260421.csv.gz").touch()
    (raw_dir / "StormEvents_locations-ftp_v1.0_d2026_c20260421.csv.gz").touch()
    (
        raw_dir / "StormEvents_fatalities-ftp_v1.0_d2026_c20260421.csv.gz"
    ).touch()

    parser = crear_parser()
    args = parser.parse_args(
        [
            "--raw-dir",
            str(raw_dir),
            "--anio",
            "2026",
            "--salida",
            str(tmp_path / "processed"),
        ]
    )

    rutas = construir_rutas_desde_args(args)

    assert rutas.details_raw == (
        raw_dir / "StormEvents_details-ftp_v1.0_d2026_c20260421.csv.gz"
    )
    assert rutas.locations_raw == (
        raw_dir / "StormEvents_locations-ftp_v1.0_d2026_c20260421.csv.gz"
    )
    assert rutas.fatalities_raw == (
        raw_dir / "StormEvents_fatalities-ftp_v1.0_d2026_c20260421.csv.gz"
    )
    assert rutas.details_procesado == (
        tmp_path / "processed" / "StormEvents_details_Limpio.csv"
    )

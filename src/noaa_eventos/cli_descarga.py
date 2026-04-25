import argparse
from pathlib import Path

from noaa_eventos.descarga_noaa import descargar_archivos_noaa_por_anio


def crear_parser() -> argparse.ArgumentParser:

    parser = argparse.ArgumentParser(
        prog="noaa-descargar",
        description=(
            "Descarga los archivos RAW más recientes de NOAA Storm Events "
            "para un año determinado."
        ),
    )

    parser.add_argument(
        "--anio",
        required=True,
        type=int,
        help="Año de datos NOAA a descargar. Ejemplo: 2026.",
    )
    parser.add_argument(
        "--raw-dir",
        required=True,
        type=Path,
        help="Directorio donde se guardan los archivos RAW descargados.",
    )

    return parser


def main() -> None:
    # Ejecuta la descarga de archivos RAW NOAA.

    parser = crear_parser()
    args = parser.parse_args()

    descargas = descargar_archivos_noaa_por_anio(
        args.raw_dir,
        anio_datos=args.anio,
    )

    for descarga in descargas:
        print(descarga.ruta_local)


if __name__ == "__main__":
    main()

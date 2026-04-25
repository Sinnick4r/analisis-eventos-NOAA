import argparse
from pathlib import Path

from noaa_eventos.reporte_bi import RutasReporteBi, generar_reporte_bi


def crear_parser() -> argparse.ArgumentParser:
    """Crea el parser del CLI de reporte BI.

    Side effects:
        No tiene.
    """
    parser = argparse.ArgumentParser(
        prog="noaa-bi",
        description="Genera un reporte BI simple desde CSV procesados.",
    )

    parser.add_argument(
        "--processed-dir",
        required=True,
        type=Path,
        help="Directorio con CSV procesados.",
    )
    parser.add_argument(
        "--salida",
        required=True,
        type=Path,
        help="Directorio donde se guardan gráficos y resumen.",
    )

    return parser


def main() -> None:
    """Ejecuta la generación del reporte BI.

    Side effects:
        Lee argumentos de línea de comandos.
        Lee CSV procesados.
        Escribe gráficos PNG y resumen Markdown.
    """
    parser = crear_parser()
    args = parser.parse_args()

    rutas = RutasReporteBi(
        details=args.processed_dir / "StormEvents_details_Limpio.csv",
        locations=args.processed_dir / "StormEvents_locations_Limpio.csv",
        fatalities=args.processed_dir / "StormEvents_fatalities_Limpio.csv",
        salida=args.salida,
    )

    generar_reporte_bi(rutas)


if __name__ == "__main__":
    main()

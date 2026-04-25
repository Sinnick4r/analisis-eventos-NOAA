import argparse
from pathlib import Path

from noaa_eventos.archivos_noaa import seleccionar_archivo_mas_reciente
from noaa_eventos.flujo import RutasFlujoLocal, ejecutar_flujo_local


def crear_parser() -> argparse.ArgumentParser:

    parser = argparse.ArgumentParser(
        prog="noaa-procesar",
        description=(
            "Procesa archivos RAW locales de NOAA Storm Events "
            "y genera CSV limpios."
        ),
    )

    parser.add_argument(
        "--raw-dir",
        type=Path,
        help=(
            "Directorio RAW con archivos NOAA oficiales. "
            "Usar junto con --anio."
        ),
    )
    parser.add_argument(
        "--anio",
        type=int,
        help="Año de datos NOAA a procesar. Ejemplo: 2026.",
    )
    parser.add_argument(
        "--details",
        type=Path,
        help="Ruta explícita al CSV RAW de details.",
    )
    parser.add_argument(
        "--locations",
        type=Path,
        help="Ruta explícita al CSV RAW de locations.",
    )
    parser.add_argument(
        "--fatalities",
        type=Path,
        help="Ruta explícita al CSV RAW de fatalities.",
    )
    parser.add_argument(
        "--salida",
        required=True,
        type=Path,
        help="Directorio donde se guardan los CSV procesados.",
    )
    parser.add_argument(
        "--encoding",
        default="utf-8",
        help="Encoding de lectura/escritura de CSV. Default: utf-8.",
    )

    return parser


def construir_rutas_desde_args(
    args: argparse.Namespace,
) -> RutasFlujoLocal:

    salida: Path = args.salida

    if args.raw_dir is not None or args.anio is not None:
        return construir_rutas_desde_raw_dir(args)

    return construir_rutas_desde_archivos_explicitos(args, salida)


def construir_rutas_desde_raw_dir(
    args: argparse.Namespace,
) -> RutasFlujoLocal:

    if args.raw_dir is None:
        raise ValueError("Debe indicar --raw-dir junto con --anio.")

    if args.anio is None:
        raise ValueError("Debe indicar --anio junto con --raw-dir.")

    nombres_archivos = [
        ruta.name for ruta in args.raw_dir.iterdir() if ruta.is_file()
    ]

    details = seleccionar_archivo_mas_reciente(
        nombres_archivos,
        tipo="details",
        anio_datos=args.anio,
    )
    locations = seleccionar_archivo_mas_reciente(
        nombres_archivos,
        tipo="locations",
        anio_datos=args.anio,
    )
    fatalities = seleccionar_archivo_mas_reciente(
        nombres_archivos,
        tipo="fatalities",
        anio_datos=args.anio,
    )

    return RutasFlujoLocal(
        details_raw=args.raw_dir / details.nombre,
        locations_raw=args.raw_dir / locations.nombre,
        fatalities_raw=args.raw_dir / fatalities.nombre,
        details_procesado=args.salida / "StormEvents_details_Limpio.csv",
        locations_procesado=args.salida / "StormEvents_locations_Limpio.csv",
        fatalities_procesado=args.salida / "StormEvents_fatalities_Limpio.csv",
    )


def construir_rutas_desde_archivos_explicitos(
    args: argparse.Namespace,
    salida: Path,
) -> RutasFlujoLocal:

    if args.details is None:
        raise ValueError("Debe indicar --details o usar --raw-dir --anio.")

    if args.locations is None:
        raise ValueError("Debe indicar --locations o usar --raw-dir --anio.")

    if args.fatalities is None:
        raise ValueError("Debe indicar --fatalities o usar --raw-dir --anio.")

    return RutasFlujoLocal(
        details_raw=args.details,
        locations_raw=args.locations,
        fatalities_raw=args.fatalities,
        details_procesado=salida / "StormEvents_details_Limpio.csv",
        locations_procesado=salida / "StormEvents_locations_Limpio.csv",
        fatalities_procesado=salida / "StormEvents_fatalities_Limpio.csv",
    )


def main() -> None:
    # Ejecuta el CLI del procesamiento NOAA.

    parser = crear_parser()
    args = parser.parse_args()
    rutas = construir_rutas_desde_args(args)

    ejecutar_flujo_local(rutas, encoding=args.encoding)


if __name__ == "__main__":
    main()

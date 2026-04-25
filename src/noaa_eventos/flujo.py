from dataclasses import dataclass
from pathlib import Path

from noaa_eventos.io import guardar_csv, leer_csv
from noaa_eventos.procesamiento_details import procesar_details
from noaa_eventos.procesamiento_fatalities import procesar_fatalities
from noaa_eventos.procesamiento_locations import procesar_locations


@dataclass(frozen=True, slots=True)
class RutasFlujoLocal:
    details_raw: Path
    locations_raw: Path
    fatalities_raw: Path
    details_procesado: Path
    locations_procesado: Path
    fatalities_procesado: Path


def ejecutar_flujo_local(
    rutas: RutasFlujoLocal,
    *,
    encoding: str = "utf-8",
) -> None:

    details = procesar_details(leer_csv(rutas.details_raw, encoding=encoding))
    locations = procesar_locations(
        leer_csv(rutas.locations_raw, encoding=encoding)
    )
    fatalities = procesar_fatalities(
        leer_csv(rutas.fatalities_raw, encoding=encoding)
    )

    guardar_csv(details, rutas.details_procesado, encoding=encoding)
    guardar_csv(locations, rutas.locations_procesado, encoding=encoding)
    guardar_csv(fatalities, rutas.fatalities_procesado, encoding=encoding)

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Final

import httpx

from noaa_eventos.archivos_noaa import (
    ArchivoNoaa,
    TipoArchivoNoaa,
    ruta_archivo_raw,
    seleccionar_archivo_mas_reciente,
)

URL_BASE_NOAA: Final[str] = (
    "https://www.ncei.noaa.gov/pub/data/swdi/stormevents/csvfiles/"
)

PATRON_LINK_CSV: Final[re.Pattern[str]] = re.compile(
    r'href="(?P<nombre>StormEvents_'
    r'(?:details|locations|fatalities)-ftp_v'
    r'\d+\.\d+_d\d{4}_c\d{8}\.csv(?:\.gz)?)"'
)


@dataclass(frozen=True, slots=True)
class DescargaNoaa:

    archivo: ArchivoNoaa
    url: str
    ruta_local: Path


def listar_archivos_noaa_disponibles(
    *,
    url_base: str = URL_BASE_NOAA,
    timeout: float = 30.0,
) -> list[str]:
    #lista nombres de archivos NOAA disponibles en el índice HTTP

    respuesta = httpx.get(url_base, timeout=timeout)
    respuesta.raise_for_status()

    return [
        coincidencia.group("nombre")
        for coincidencia in PATRON_LINK_CSV.finditer(respuesta.text)
    ]


def descargar_archivo_noaa(
    archivo: ArchivoNoaa,
    raw_dir: Path,
    *,
    url_base: str = URL_BASE_NOAA,
    timeout: float = 60.0,
) -> DescargaNoaa:
    # Descarga archivo - Raises: httpx.HTTPError: Si falla

    raw_dir.mkdir(parents=True, exist_ok=True)

    url = f"{url_base}{archivo.nombre}"
    ruta_local = ruta_archivo_raw(raw_dir, archivo)

    with httpx.stream("GET", url, timeout=timeout) as respuesta:
        respuesta.raise_for_status()

        with ruta_local.open("wb") as archivo_salida:
            for chunk in respuesta.iter_bytes():
                archivo_salida.write(chunk)

    return DescargaNoaa(
        archivo=archivo,
        url=url,
        ruta_local=ruta_local,
    )


def descargar_archivos_noaa_por_anio(
    raw_dir: Path,
    *,
    anio_datos: int,
    url_base: str = URL_BASE_NOAA,
) -> list[DescargaNoaa]:
    #descarga los últimos details, locations y fatalities para un año.
    """
    Raises:
        FileNotFoundError: Si falta algún tipo de archivo para el año.
        httpx.HTTPError: Si falla alguna petición.
    """
    nombres_archivos = listar_archivos_noaa_disponibles(url_base=url_base)

    tipos: tuple[TipoArchivoNoaa, ...] = (
        "details",
        "locations",
        "fatalities",
    )

    archivos = [
        seleccionar_archivo_mas_reciente(
            nombres_archivos,
            tipo=tipo,
            anio_datos=anio_datos,
        )
        for tipo in tipos
    ]

    return [
        descargar_archivo_noaa(
            archivo,
            raw_dir,
            url_base=url_base,
        )
        for archivo in archivos
    ]

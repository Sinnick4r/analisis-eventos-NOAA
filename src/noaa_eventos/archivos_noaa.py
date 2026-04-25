import re
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Final, Literal

TipoArchivoNoaa = Literal["details", "locations", "fatalities"]

PATRON_ARCHIVO_NOAA: Final[re.Pattern[str]] = re.compile(
    r"^StormEvents_"
    r"(?P<tipo>details|locations|fatalities)"
    r"-ftp_v(?P<version>\d+\.\d+)"
    r"_d(?P<anio>\d{4})"
    r"_c(?P<fecha_creacion>\d{8})"
    r"\.csv(?:\.gz)?$"
)


@dataclass(frozen=True, slots=True)
class ArchivoNoaa:

    nombre: str
    tipo: TipoArchivoNoaa
    version_ftp: str
    anio_datos: int
    fecha_creacion: date


def parsear_nombre_archivo_noaa(nombre_archivo: str) -> ArchivoNoaa:

    #Extrae metadata 

    coincidencia = PATRON_ARCHIVO_NOAA.fullmatch(nombre_archivo)

    if coincidencia is None:
        raise ValueError(
            f"Nombre de archivo NOAA inválido: {nombre_archivo}"
        )

    fecha_creacion = datetime.strptime(
        coincidencia.group("fecha_creacion"),
        "%Y%m%d",
    ).date()

    return ArchivoNoaa(
        nombre=nombre_archivo,
        tipo=coincidencia.group("tipo"),  # type: ignore[arg-type]
        version_ftp=coincidencia.group("version"),
        anio_datos=int(coincidencia.group("anio")),
        fecha_creacion=fecha_creacion,
    )


def seleccionar_archivo_mas_reciente(
    nombres_archivos: list[str],
    *,
    tipo: TipoArchivoNoaa,
    anio_datos: int,
) -> ArchivoNoaa:
    # Agarra el archivo NOAA más reciente por tipo y año

    candidatos: list[ArchivoNoaa] = []

    for nombre_archivo in nombres_archivos:
        try:
            archivo = parsear_nombre_archivo_noaa(nombre_archivo)
        except ValueError:
            continue

        if archivo.tipo != tipo:
            continue

        if archivo.anio_datos != anio_datos:
            continue

        candidatos.append(archivo)

    if not candidatos:
        raise FileNotFoundError(
            "No se encontró archivo NOAA para "
            f"tipo={tipo!r}, anio_datos={anio_datos}"
        )

    return max(candidatos, key=lambda archivo: archivo.fecha_creacion)


def ruta_archivo_raw(
    raw_dir: Path,
    archivo: ArchivoNoaa,
) -> Path:

    return raw_dir / archivo.nombre

import re
from typing import Final

MULTIPLICADORES_DANIO: Final[dict[str, float]] = {
    "": 1.0,
    "K": 1_000.0,
    "M": 1_000_000.0,
    "B": 1_000_000_000.0,
}

PATRON_DANIO: Final[re.Pattern[str]] = re.compile(
    r"^\s*(?P<monto>\d+(?:\.\d+)?)(?P<sufijo>[KMB]?)\s*$",
    re.IGNORECASE,
)


def convertir_danio_estimado(valor_crudo: object) -> float | None:

    #Convierte valores de daño NOAA con sufijos K, M o B.

    if valor_crudo is None:
        return None

    valor_texto = str(valor_crudo).strip()

    if valor_texto == "":
        return None

    coincidencia = PATRON_DANIO.fullmatch(valor_texto)

    if coincidencia is None:
        raise ValueError(f"Formato de daño inválido: {valor_crudo!r}")

    monto = float(coincidencia.group("monto"))
    sufijo = coincidencia.group("sufijo").upper()
    multiplicador = MULTIPLICADORES_DANIO[sufijo]

    return monto * multiplicador

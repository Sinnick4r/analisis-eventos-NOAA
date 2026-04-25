from pathlib import Path

import httpx

from noaa_eventos.archivos_noaa import parsear_nombre_archivo_noaa
from noaa_eventos.descarga_noaa import (
    PATRON_LINK_CSV,
    descargar_archivo_noaa,
    listar_archivos_noaa_disponibles,
)


def test_patron_link_csv_detecta_archivos_noaa() -> None:
    html = """
    <a href="StormEvents_details-ftp_v1.0_d2026_c20260421.csv.gz">
    StormEvents_details-ftp_v1.0_d2026_c20260421.csv.gz</a>
    <a href="README">README</a>
    """

    nombres = [
        coincidencia.group("nombre")
        for coincidencia in PATRON_LINK_CSV.finditer(html)
    ]

    assert nombres == ["StormEvents_details-ftp_v1.0_d2026_c20260421.csv.gz"]


def test_listar_archivos_noaa_disponibles_con_mock(
    monkeypatch,
) -> None:
    html = """
    <a href="StormEvents_details-ftp_v1.0_d2026_c20260421.csv.gz">
    StormEvents_details-ftp_v1.0_d2026_c20260421.csv.gz</a>
    """

    def fake_get(url: str, timeout: float) -> httpx.Response:
        request = httpx.Request("GET", url)
        return httpx.Response(200, text=html, request=request)

    monkeypatch.setattr(httpx, "get", fake_get)

    nombres = listar_archivos_noaa_disponibles()

    assert nombres == ["StormEvents_details-ftp_v1.0_d2026_c20260421.csv.gz"]


def test_descargar_archivo_noaa_con_mock(
    monkeypatch,
    tmp_path: Path,
) -> None:
    archivo = parsear_nombre_archivo_noaa(
        "StormEvents_details-ftp_v1.0_d2026_c20260421.csv.gz"
    )

    class FakeStream:
        def __enter__(self) -> "FakeStream":
            return self

        def __exit__(self, *args: object) -> None:
            return None

        def raise_for_status(self) -> None:
            return None

        def iter_bytes(self) -> list[bytes]:
            return [b"EVENT_ID\n", b"1\n"]

    def fake_stream(
        method: str,
        url: str,
        timeout: float,
    ) -> FakeStream:
        return FakeStream()

    monkeypatch.setattr(httpx, "stream", fake_stream)

    resultado = descargar_archivo_noaa(archivo, tmp_path)

    assert resultado.ruta_local.exists()
    assert resultado.ruta_local.read_bytes() == b"EVENT_ID\n1\n"

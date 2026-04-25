import pytest

from noaa_eventos.danios import convertir_danio_estimado


@pytest.mark.parametrize(
    ("valor_crudo", "valor_esperado"),
    [
        ("0", 0.0),
        ("10", 10.0),
        ("10K", 10_000.0),
        ("1.5K", 1_500.0),
        ("2M", 2_000_000.0),
        ("3.25M", 3_250_000.0),
        ("1B", 1_000_000_000.0),
        ("2.5B", 2_500_000_000.0),
        (" 7K ", 7_000.0),
        ("4m", 4_000_000.0),
    ],
)
def test_convertir_danio_estimado_valores_validos(
    valor_crudo: str,
    valor_esperado: float,
) -> None:
    assert convertir_danio_estimado(valor_crudo) == valor_esperado


@pytest.mark.parametrize("valor_crudo", [None, ""])
def test_convertir_danio_estimado_valores_vacios(
    valor_crudo: object,
) -> None:
    assert convertir_danio_estimado(valor_crudo) is None


@pytest.mark.parametrize(
    "valor_crudo",
    [
        "ABC",
        "12T",
        "K10",
        "1,5M",
        "$10K",
    ],
)
def test_convertir_danio_estimado_rechaza_formatos_invalidos(
    valor_crudo: str,
) -> None:
    with pytest.raises(ValueError, match="Formato de daño inválido"):
        convertir_danio_estimado(valor_crudo)

import pandas as pd

from noaa_eventos import metricas


def test_eventos_por_mes_cuenta_y_ordena() -> None:
    details = pd.DataFrame(
        {"begin_yearmonth": [202602, 202601, 202601, 202602, 202602]}
    )

    resultado = metricas.eventos_por_mes(details)

    # el mes sale como texto y ordenado cronologicamente
    assert resultado["mes"].tolist() == ["202601", "202602"]
    assert resultado["eventos"].tolist() == [2, 3]


def test_top_tipos_evento_respeta_n_y_ordena_desc() -> None:
    details = pd.DataFrame(
        {
            "event_type": [
                "Flood",
                "Flood",
                "Flood",
                "Hail",
                "Hail",
                "Tornado",
            ]
        }
    )

    resultado = metricas.top_tipos_evento(details, n=2)

    assert resultado["event_type"].tolist() == ["Flood", "Hail"]
    assert resultado["eventos"].tolist() == [3, 2]


def test_top_estados_eventos_respeta_n() -> None:
    details = pd.DataFrame(
        {"state": ["TEXAS", "TEXAS", "OKLAHOMA", "OHIO", "OHIO", "OHIO"]}
    )

    resultado = metricas.top_estados_eventos(details, n=2)

    assert resultado["state"].tolist() == ["OHIO", "TEXAS"]
    assert resultado["eventos"].tolist() == [3, 2]


def test_top_estados_danios_suma_propiedad_y_cultivos() -> None:
    details = pd.DataFrame(
        {
            "state": ["TEXAS", "TEXAS", "OHIO"],
            "damage_property": [1_000_000.0, None, 500_000.0],
            "damage_crops": [None, 2_000_000.0, 0.0],
        }
    )

    resultado = metricas.top_estados_danios(details, n=2)

    # TEXAS suma 3M (los None cuentan como 0), OHIO 0.5M
    assert resultado["state"].tolist() == ["TEXAS", "OHIO"]
    assert resultado["danios_totales"].tolist() == [3_000_000.0, 500_000.0]
    assert resultado["danios_millones"].tolist() == [3.0, 0.5]


def test_fatalidades_por_tipo_mapea_codigos() -> None:
    fatalities = pd.DataFrame({"fatality_type": ["D", "I", "I"]})

    resultado = metricas.fatalidades_por_tipo(fatalities)
    conteo = dict(
        zip(resultado["tipo_fatalidad"], resultado["registros"], strict=True)
    )

    assert conteo == {"Directa": 1, "Indirecta": 2}


def test_fatalidades_por_tipo_preserva_valor_inesperado() -> None:
    # un codigo fuera de contrato no se descarta en silencio
    fatalities = pd.DataFrame({"fatality_type": ["D", "X"]})

    resultado = metricas.fatalidades_por_tipo(fatalities)

    assert "X" in resultado["tipo_fatalidad"].tolist()

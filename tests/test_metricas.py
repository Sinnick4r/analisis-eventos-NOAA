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


def test_filtrar_eventos_por_estado() -> None:
    details = pd.DataFrame(
        {
            "state": ["TEXAS", "OHIO", "TEXAS"],
            "event_type": ["Flood", "Hail", "Hail"],
        }
    )

    resultado = metricas.filtrar_eventos(details, estados=["TEXAS"])

    assert len(resultado) == 2
    assert set(resultado["state"]) == {"TEXAS"}


def test_filtrar_eventos_combinado() -> None:
    details = pd.DataFrame(
        {
            "state": ["TEXAS", "TEXAS", "OHIO"],
            "event_type": ["Flood", "Hail", "Hail"],
        }
    )

    resultado = metricas.filtrar_eventos(
        details,
        estados=["TEXAS"],
        tipos_evento=["Hail"],
    )

    assert len(resultado) == 1
    assert resultado.iloc[0]["state"] == "TEXAS"
    assert resultado.iloc[0]["event_type"] == "Hail"


def test_filtrar_eventos_sin_filtro_devuelve_todo() -> None:
    details = pd.DataFrame(
        {"state": ["TEXAS", "OHIO"], "event_type": ["A", "B"]}
    )

    resultado = metricas.filtrar_eventos(
        details, estados=None, tipos_evento=[]
    )

    assert len(resultado) == 2


def test_filtrar_fatalities_sigue_a_details() -> None:
    fatalities = pd.DataFrame(
        {"event_id": [1, 2, 3], "fatality_type": ["D"] * 3}
    )
    details_filtrado = pd.DataFrame({"event_id": [1, 3]})

    resultado = metricas.filtrar_fatalities_por_eventos(
        fatalities,
        details_filtrado,
    )

    assert set(resultado["event_id"]) == {1, 3}


def test_puntos_mapa_cruza_y_calcula_danio() -> None:
    locations = pd.DataFrame(
        {
            "event_id": [1, 2],
            "latitude": [34.5, 40.0],
            "longitude": [-87.0, -100.0],
        }
    )
    details = pd.DataFrame(
        {
            "event_id": [1, 2],
            "event_type": ["Flood", "Hail"],
            "state": ["TEXAS", "OHIO"],
            "damage_property": [1000.0, None],
            "damage_crops": [None, 500.0],
        }
    )

    resultado = metricas.puntos_mapa(locations, details)
    danios = dict(
        zip(resultado["event_type"], resultado["danio"], strict=True)
    )

    assert len(resultado) == 2
    assert danios == {"Flood": 1000.0, "Hail": 500.0}


def test_puntos_mapa_agrupa_tipos_en_otros() -> None:
    counts = {"A": 5, "B": 4, "C": 3, "D": 2, "E": 2, "F": 2, "G": 1}
    tipos: list[str] = []
    for tipo, n in counts.items():
        tipos += [tipo] * n
    ids = list(range(len(tipos)))

    details = pd.DataFrame(
        {
            "event_id": ids,
            "event_type": tipos,
            "state": ["TX"] * len(ids),
            "damage_property": [0.0] * len(ids),
            "damage_crops": [0.0] * len(ids),
        }
    )
    locations = pd.DataFrame(
        {
            "event_id": ids,
            "latitude": [34.0] * len(ids),
            "longitude": [-90.0] * len(ids),
        }
    )

    resultado = metricas.puntos_mapa(locations, details)
    g_rows = resultado[resultado["event_type"] == "G"]

    # G es el menos frecuente, cae en Otros (TOP_TIPOS_MAPA = 6)
    assert (g_rows["tipo_color"] == "Otros").all()
    assert "G" not in set(resultado["tipo_color"])
    assert "A" in set(resultado["tipo_color"])

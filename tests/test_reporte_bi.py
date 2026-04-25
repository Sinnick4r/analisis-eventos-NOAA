from pathlib import Path

import pandas as pd

from noaa_eventos.reporte_bi import (
    RutasReporteBi,
    calcular_kpis,
    generar_reporte_bi,
)


def test_calcular_kpis() -> None:
    details = pd.DataFrame(
        {
            "state": ["TEXAS", "TEXAS", "OKLAHOMA"],
            "event_type": ["Flood", "Hail", "Flood"],
            "damage_property": [1000.0, 2000.0, None],
            "damage_crops": [0.0, 500.0, 100.0],
            "deaths_direct": [1, 0, 0],
            "deaths_indirect": [0, 1, 0],
            "injuries_direct": [2, 0, 1],
            "injuries_indirect": [0, 1, 0],
        }
    )
    fatalities = pd.DataFrame({"event_id": [10, 20, 20]})

    kpis = calcular_kpis(details, fatalities)

    assert kpis.total_eventos == 3
    assert kpis.estados_afectados == 2
    assert kpis.tipos_evento == 2
    assert kpis.danios_estimados_totales == 3600.0
    assert kpis.muertes_totales == 2
    assert kpis.lesiones_totales == 4
    assert kpis.eventos_con_fatalidades == 2


def test_generar_reporte_bi_crea_archivos(
    tmp_path: Path,
) -> None:
    processed_dir = tmp_path / "processed"
    salida = tmp_path / "bi"
    processed_dir.mkdir()

    pd.DataFrame(
        {
            "begin_yearmonth": [202601, 202601, 202602],
            "state": ["TEXAS", "TEXAS", "OKLAHOMA"],
            "event_type": ["Flood", "Hail", "Flood"],
            "damage_property": [1000.0, 2000.0, 0.0],
            "damage_crops": [0.0, 500.0, 100.0],
            "deaths_direct": [1, 0, 0],
            "deaths_indirect": [0, 1, 0],
            "injuries_direct": [2, 0, 1],
            "injuries_indirect": [0, 1, 0],
        }
    ).to_csv(processed_dir / "StormEvents_details_Limpio.csv", index=False)

    pd.DataFrame(
        {
            "event_id": [1, 2],
            "location_index": [1, 1],
        }
    ).to_csv(processed_dir / "StormEvents_locations_Limpio.csv", index=False)

    pd.DataFrame(
        {
            "event_id": [1, 2, 2],
            "fatality_type": ["Direct", "Indirect", "Direct"],
        }
    ).to_csv(
        processed_dir / "StormEvents_fatalities_Limpio.csv",
        index=False,
    )

    rutas = RutasReporteBi(
        details=processed_dir / "StormEvents_details_Limpio.csv",
        locations=processed_dir / "StormEvents_locations_Limpio.csv",
        fatalities=processed_dir / "StormEvents_fatalities_Limpio.csv",
        salida=salida,
    )

    generar_reporte_bi(rutas)

    assert (salida / "resumen_kpis.md").exists()
    assert (salida / "eventos_por_mes.png").exists()
    assert (salida / "top_10_tipos_evento.png").exists()
    assert (salida / "top_10_estados_eventos.png").exists()
    assert (salida / "top_10_estados_danios.png").exists()
    assert (salida / "fatalidades_por_tipo.png").exists()
    assert (salida / "dashboard_ejecutivo.png").exists()

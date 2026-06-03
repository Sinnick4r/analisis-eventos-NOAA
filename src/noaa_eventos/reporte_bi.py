from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.axes import Axes

from noaa_eventos import metricas
from noaa_eventos.io import leer_csv


@dataclass(frozen=True, slots=True)
class RutasReporteBi:
    details: Path
    locations: Path
    fatalities: Path
    salida: Path


@dataclass(frozen=True, slots=True)
class KpisBi:
    # KPIs principales

    total_eventos: int
    estados_afectados: int
    tipos_evento: int
    danios_estimados_totales: float
    muertes_totales: int
    lesiones_totales: int
    eventos_con_fatalidades: int


def generar_reporte_bi(rutas: RutasReporteBi) -> KpisBi:
    # genera un reporte BI simple desde CSV procesados

    rutas.salida.mkdir(parents=True, exist_ok=True)

    details = leer_csv(rutas.details)
    locations = leer_csv(rutas.locations)
    fatalities = leer_csv(rutas.fatalities)

    kpis = calcular_kpis(details, fatalities)

    guardar_resumen_kpis(kpis, rutas.salida / "resumen_kpis.md")

    graficar_eventos_por_mes(
        details,
        rutas.salida / "eventos_por_mes.png",
    )
    graficar_top_tipos_evento(
        details,
        rutas.salida / "top_10_tipos_evento.png",
    )
    graficar_top_estados_eventos(
        details,
        rutas.salida / "top_10_estados_eventos.png",
    )
    graficar_top_estados_danios(
        details,
        rutas.salida / "top_10_estados_danios.png",
    )
    graficar_fatalidades_por_tipo(
        fatalities,
        rutas.salida / "fatalidades_por_tipo.png",
    )
    generar_dashboard_ejecutivo(
        details,
        fatalities,
        kpis,
        rutas.salida / "dashboard_ejecutivo.png",
    )

    _ = locations

    return kpis


def calcular_kpis(
    details: pd.DataFrame,
    fatalities: pd.DataFrame,
) -> KpisBi:
    # calcula KPIs principales

    danios_propiedad = details.get(
        "damage_property",
        pd.Series(dtype="float64"),
    ).fillna(0)

    danios_cultivos = details.get(
        "damage_crops",
        pd.Series(dtype="float64"),
    ).fillna(0)

    muertes_directas = details.get(
        "deaths_direct",
        pd.Series(dtype="int64"),
    ).fillna(0)

    muertes_indirectas = details.get(
        "deaths_indirect",
        pd.Series(dtype="int64"),
    ).fillna(0)

    lesiones_directas = details.get(
        "injuries_direct",
        pd.Series(dtype="int64"),
    ).fillna(0)

    lesiones_indirectas = details.get(
        "injuries_indirect",
        pd.Series(dtype="int64"),
    ).fillna(0)

    return KpisBi(
        total_eventos=len(details),
        estados_afectados=int(details["state"].nunique()),
        tipos_evento=int(details["event_type"].nunique()),
        danios_estimados_totales=float(
            danios_propiedad.sum() + danios_cultivos.sum()
        ),
        muertes_totales=int(muertes_directas.sum() + muertes_indirectas.sum()),
        lesiones_totales=int(
            lesiones_directas.sum() + lesiones_indirectas.sum()
        ),
        eventos_con_fatalidades=int(fatalities["event_id"].nunique()),
    )


def guardar_resumen_kpis(kpis: KpisBi, ruta_salida: Path) -> None:
    # Guarda un .md con los KPIs
    contenido = f"""# Resumen BI NOAA Storm Events

## KPIs principales

| KPI | Valor |
|---|---:|
| Total de eventos | {kpis.total_eventos:,} |
| Estados afectados | {kpis.estados_afectados:,} |
| Tipos de evento | {kpis.tipos_evento:,} |
| Daños estimados totales | USD {kpis.danios_estimados_totales:,.0f} |
| Muertes totales | {kpis.muertes_totales:,} |
| Lesiones totales | {kpis.lesiones_totales:,} |
| Eventos con fatalidades | {kpis.eventos_con_fatalidades:,} |

## Archivos generados

- `eventos_por_mes.png`
- `top_10_tipos_evento.png`
- `top_10_estados_eventos.png`
- `top_10_estados_danios.png`
- `fatalidades_por_tipo.png`
"""

    ruta_salida.write_text(contenido, encoding="utf-8")


def graficar_eventos_por_mes(
    details: pd.DataFrame,
    ruta_salida: Path,
) -> None:

    datos = metricas.eventos_por_mes(details)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(datos["mes"], datos["eventos"])
    ax.set_title("Eventos por mes")
    ax.set_xlabel("Mes")
    ax.set_ylabel("Cantidad de eventos")
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(ruta_salida, dpi=150)
    plt.close(fig)


def graficar_top_tipos_evento(
    details: pd.DataFrame,
    ruta_salida: Path,
) -> None:

    # se invierte para que la barra mas grande quede arriba
    datos = metricas.top_tipos_evento(details, n=10).iloc[::-1]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(datos["event_type"], datos["eventos"])
    ax.set_title("Top 10 tipos de evento")
    ax.set_xlabel("Cantidad de eventos")
    ax.set_ylabel("Tipo de evento")
    fig.tight_layout()
    fig.savefig(ruta_salida, dpi=150)
    plt.close(fig)


def graficar_top_estados_eventos(
    details: pd.DataFrame,
    ruta_salida: Path,
) -> None:

    datos = metricas.top_estados_eventos(details, n=10).iloc[::-1]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(datos["state"], datos["eventos"])
    ax.set_title("Top 10 estados por cantidad de eventos")
    ax.set_xlabel("Cantidad de eventos")
    ax.set_ylabel("Estado")
    fig.tight_layout()
    fig.savefig(ruta_salida, dpi=150)
    plt.close(fig)


def graficar_top_estados_danios(
    details: pd.DataFrame,
    ruta_salida: Path,
) -> None:

    datos = metricas.top_estados_danios(details, n=10).iloc[::-1]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(datos["state"], datos["danios_millones"])
    ax.set_title("Top 10 estados por daños estimados")
    ax.set_xlabel("Daños estimados, millones USD")
    ax.set_ylabel("Estado")
    fig.tight_layout()
    fig.savefig(ruta_salida, dpi=150)
    plt.close(fig)


def graficar_fatalidades_por_tipo(
    fatalities: pd.DataFrame,
    ruta_salida: Path,
) -> None:

    datos = metricas.fatalidades_por_tipo(fatalities).iloc[::-1]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.barh(datos["tipo_fatalidad"], datos["registros"])
    ax.set_title("Fatalidades por tipo")
    ax.set_xlabel("Cantidad de registros")
    ax.set_ylabel("Tipo de fatalidad")
    fig.tight_layout()
    fig.savefig(ruta_salida, dpi=150)
    plt.close(fig)


def generar_dashboard_ejecutivo(
    details: pd.DataFrame,
    fatalities: pd.DataFrame,
    kpis: KpisBi,
    ruta_salida: Path,
) -> None:
    """Genera un dashboard ejecutivo estático para README.

    Side effects:
        Escribe un archivo PNG.
    """
    fig = plt.figure(figsize=(16, 10))
    grilla = fig.add_gridspec(
        3,
        4,
        height_ratios=[0.8, 2.2, 2.2],
    )

    ejes_kpis = [fig.add_subplot(grilla[0, indice]) for indice in range(4)]
    eje_tipos_evento = fig.add_subplot(grilla[1, :2])
    eje_estados_eventos = fig.add_subplot(grilla[1, 2:])
    eje_estados_danios = fig.add_subplot(grilla[2, :2])
    eje_fatalidades = fig.add_subplot(grilla[2, 2:])

    fig.suptitle(
        "Dashboard ejecutivo NOAA Storm Events 2026",
        fontsize=18,
        fontweight="bold",
    )

    dibujar_kpi(
        ejes_kpis[0],
        "Eventos",
        f"{kpis.total_eventos:,}",
    )
    dibujar_kpi(
        ejes_kpis[1],
        "Daños estimados",
        f"USD {kpis.danios_estimados_totales / 1_000_000:,.1f} M",
    )
    dibujar_kpi(
        ejes_kpis[2],
        "Muertes",
        f"{kpis.muertes_totales:,}",
    )
    dibujar_kpi(
        ejes_kpis[3],
        "Lesiones",
        f"{kpis.lesiones_totales:,}",
    )

    dibujar_top_tipos_evento(details, eje_tipos_evento)
    dibujar_top_estados_eventos(details, eje_estados_eventos)
    dibujar_top_estados_danios(details, eje_estados_danios)
    dibujar_fatalidades_tipo(fatalities, eje_fatalidades)

    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(ruta_salida, dpi=150)
    plt.close(fig)


def dibujar_kpi(
    eje: Axes,
    titulo: str,
    valor: str,
) -> None:
    """Dibuja una tarjeta KPI.

    Side effects:
        Modifica un eje de Matplotlib.
    """
    eje.set_xticks([])
    eje.set_yticks([])
    eje.text(
        0.5,
        0.62,
        valor,
        ha="center",
        va="center",
        fontsize=22,
        fontweight="bold",
    )
    eje.text(
        0.5,
        0.25,
        titulo,
        ha="center",
        va="center",
        fontsize=12,
    )

    for borde in eje.spines.values():
        borde.set_visible(True)


def dibujar_top_tipos_evento(
    details: pd.DataFrame,
    eje: Axes,
) -> None:
    """Dibuja top tipos de evento en un eje.

    Side effects:
        Modifica un eje de Matplotlib.
    """
    datos = metricas.top_tipos_evento(details, n=8).iloc[::-1]

    eje.barh(datos["event_type"], datos["eventos"])
    eje.set_title("Top tipos de evento")
    eje.set_xlabel("Eventos")
    eje.set_ylabel("")


def dibujar_top_estados_eventos(
    details: pd.DataFrame,
    eje: Axes,
) -> None:

    datos = metricas.top_estados_eventos(details, n=8).iloc[::-1]

    eje.barh(datos["state"], datos["eventos"])
    eje.set_title("Top estados por eventos")
    eje.set_xlabel("Eventos")
    eje.set_ylabel("")


def dibujar_top_estados_danios(
    details: pd.DataFrame,
    eje: Axes,
) -> None:

    datos = metricas.top_estados_danios(details, n=8).iloc[::-1]

    eje.barh(datos["state"], datos["danios_millones"])
    eje.set_title("Top estados por daños")
    eje.set_xlabel("Millones USD")
    eje.set_ylabel("")


def dibujar_fatalidades_tipo(
    fatalities: pd.DataFrame,
    eje: Axes,
) -> None:

    datos = metricas.fatalidades_por_tipo(fatalities).iloc[::-1]

    eje.barh(datos["tipo_fatalidad"], datos["registros"])
    eje.set_title("Fatalidades por tipo")
    eje.set_xlabel("Registros")
    eje.set_ylabel("")

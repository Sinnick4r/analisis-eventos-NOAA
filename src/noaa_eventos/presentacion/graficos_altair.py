from typing import Final

import altair as alt
import pandas as pd

# acento para la barra protagonista, gris para el contexto
COLOR_FOCO: Final[str] = "#1f4e79"
COLOR_CONTEXTO: Final[str] = "#c8c8c8"
COLOR_TEXTO: Final[str] = "#3a3a3a"

ALTO_BARRA: Final[int] = 28

MESES_ABREV: Final[tuple[str, ...]] = (
    "Ene",
    "Feb",
    "Mar",
    "Abr",
    "May",
    "Jun",
    "Jul",
    "Ago",
    "Sep",
    "Oct",
    "Nov",
    "Dic",
)


def barras_ranking(
    datos: pd.DataFrame,
    *,
    campo_categoria: str,
    campo_valor: str,
    titulo: str,
    subtitulo: str,
    formato_valor: str = ",.0f",
) -> alt.Chart:
    # barras horizontales: la categoria top resaltada, el resto en gris
    categoria_foco = datos.loc[datos[campo_valor].idxmax(), campo_categoria]

    # headroom a la derecha para que la etiqueta de la barra top no se corte
    tope = datos[campo_valor].max() * 1.18

    base = alt.Chart(datos).encode(
        y=alt.Y(
            f"{campo_categoria}:N",
            sort="-x",
            title=None,
            axis=alt.Axis(labelColor=COLOR_TEXTO, ticks=False, domain=False),
        ),
        x=alt.X(
            f"{campo_valor}:Q",
            axis=None,
            scale=alt.Scale(domain=[0, tope]),
        ),
    )

    barras = base.mark_bar().encode(
        color=alt.condition(
            alt.FieldEqualPredicate(
                field=campo_categoria,
                equal=categoria_foco,
            ),
            alt.value(COLOR_FOCO),
            alt.value(COLOR_CONTEXTO),
        )
    )

    etiquetas = base.mark_text(
        align="left",
        dx=4,
        color=COLOR_TEXTO,
    ).encode(text=alt.Text(f"{campo_valor}:Q", format=formato_valor))

    return (
        (barras + etiquetas)
        .properties(
            title=_titulo(titulo, subtitulo),
            height=alt.Step(ALTO_BARRA),
            width="container",
        )
        .configure_view(stroke=None)
    )


def grafico_top_tipos_evento(datos: pd.DataFrame) -> alt.Chart:
    return barras_ranking(
        datos,
        campo_categoria="event_type",
        campo_valor="eventos",
        titulo="Tipos de evento mas frecuentes",
        subtitulo=_takeaway_lider(datos, "event_type", "eventos", "eventos"),
    )


def grafico_top_estados_eventos(datos: pd.DataFrame) -> alt.Chart:
    return barras_ranking(
        datos,
        campo_categoria="state",
        campo_valor="eventos",
        titulo="Estados con mas eventos",
        subtitulo=_takeaway_lider(datos, "state", "eventos", "eventos"),
    )


def grafico_top_estados_danios(datos: pd.DataFrame) -> alt.Chart:
    return barras_ranking(
        datos,
        campo_categoria="state",
        campo_valor="danios_millones",
        titulo="Danios estimados por estado",
        subtitulo=_takeaway_lider(
            datos,
            "state",
            "danios_millones",
            "M USD",
            formato=",.1f",
        ),
        formato_valor=",.1f",
    )


def grafico_fatalidades_por_tipo(datos: pd.DataFrame) -> alt.Chart:
    return barras_ranking(
        datos,
        campo_categoria="tipo_fatalidad",
        campo_valor="registros",
        titulo="Fatalidades por tipo",
        subtitulo=_takeaway_lider(
            datos,
            "tipo_fatalidad",
            "registros",
            "registros",
        ),
    )


def grafico_eventos_por_mes(datos: pd.DataFrame) -> alt.Chart:
    # serie temporal: linea sobria con el pico resaltado
    datos = datos.assign(mes_label=datos["mes"].map(_etiqueta_mes))
    fila_pico = datos.loc[datos["eventos"].idxmax()]

    # datos ya viene cronologico desde metricas, mantenemos ese orden
    orden_meses = datos["mes_label"].tolist()

    subtitulo = (
        f"Pico en {fila_pico['mes_label']} con "
        f"{int(fila_pico['eventos']):,} eventos"
    )

    base = alt.Chart(datos).encode(
        x=alt.X(
            "mes_label:N",
            title=None,
            sort=orden_meses,
            axis=alt.Axis(labelColor=COLOR_TEXTO, ticks=False, domain=False),
        ),
        y=alt.Y(
            "eventos:Q",
            title="Eventos",
            axis=alt.Axis(labelColor=COLOR_TEXTO, grid=False, domain=False),
        ),
    )

    linea = base.mark_line(color=COLOR_CONTEXTO, strokeWidth=2)

    puntos = base.mark_point(filled=True, size=70).encode(
        color=alt.condition(
            alt.FieldEqualPredicate(
                field="mes_label",
                equal=fila_pico["mes_label"],
            ),
            alt.value(COLOR_FOCO),
            alt.value(COLOR_CONTEXTO),
        )
    )

    return (
        (linea + puntos)
        .properties(
            title=_titulo("Eventos por mes", subtitulo),
            height=260,
            width="container",
        )
        .configure_view(stroke=None)
    )


def _etiqueta_mes(codigo: str) -> str:
    # pasa "202601" a "Ene 2026"; si no matchea, devuelve el codigo crudo
    texto = str(codigo)
    if len(texto) != 6 or not texto.isdigit():
        return texto

    anio = texto[:4]
    mes = int(texto[4:6])
    if not 1 <= mes <= 12:
        return texto

    return f"{MESES_ABREV[mes - 1]} {anio}"


def _titulo(texto: str, subtitulo: str) -> alt.TitleParams:
    # titulo alineado a la izquierda, subtitulo con la conclusion
    return alt.TitleParams(
        text=texto,
        subtitle=subtitulo,
        anchor="start",
        fontSize=16,
        subtitleColor=COLOR_TEXTO,
        subtitleFontSize=12,
    )


def _takeaway_lider(
    datos: pd.DataFrame,
    campo_categoria: str,
    campo_valor: str,
    unidad: str,
    *,
    formato: str = ",.0f",
) -> str:
    # arma "X lidera con N, Mx el segundo" comparando contra el 2do puesto
    ordenado = datos.sort_values(campo_valor, ascending=False)
    lider = ordenado.iloc[0]
    valor_lider = format(lider[campo_valor], formato)
    nombre = str(lider[campo_categoria]).title()

    if len(ordenado) < 2:
        return f"{nombre} con {valor_lider} {unidad}"

    segundo = ordenado.iloc[1][campo_valor]
    if segundo <= 0:
        return f"{nombre} lidera con {valor_lider} {unidad}"

    ratio = lider[campo_valor] / segundo
    return (
        f"{nombre} lidera con {valor_lider} {unidad}, {ratio:.1f}x el segundo"
    )

import pandas as pd


def validar_columnas_obligatorias(
    datos: pd.DataFrame,
    columnas_obligatorias: frozenset[str],
) -> None:
    # Valida que existan las columnas obligatorias
    columnas_faltantes = columnas_obligatorias.difference(datos.columns)

    if not columnas_faltantes:
        return

    raise ValueError(
        f"Faltan columnas obligatorias: {sorted(columnas_faltantes)}"
    )


def validar_columna_sin_duplicados(
    datos: pd.DataFrame,
    columna: str,
) -> None:
    # Valida que una columna no tenga valores duplicados
    if columna not in datos.columns:
        raise ValueError(f"No existe la columna requerida: {columna}")

    mascara_duplicados = datos[columna].duplicated(keep=False)

    if not mascara_duplicados.any():
        return

    valores_duplicados = sorted(
        datos.loc[mascara_duplicados, columna].unique()
    )

    raise ValueError(
        f"La columna {columna!r} contiene valores duplicados: "
        f"{valores_duplicados}"
    )


def validar_columnas_sin_nulos(
    datos: pd.DataFrame,
    columnas: frozenset[str],
) -> None:
    # valida que las columnas indicadas no tengan valores nulos

    validar_columnas_obligatorias(datos, columnas)

    columnas_con_nulos = {
        columna: int(datos[columna].isna().sum())
        for columna in columnas
        if datos[columna].isna().any()
    }

    if not columnas_con_nulos:
        return

    raise ValueError(
        f"Columnas con valores nulos no permitidos: {columnas_con_nulos}"
    )

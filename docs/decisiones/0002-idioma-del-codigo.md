# Decisión 0002 — Idioma del código

## Contexto

El proyecto fue desarrollado originalmente en español, incluyendo nombres de
funciones, comentarios y parte de la documentación. Esa decisión forma parte
de la historia del proyecto y de su identidad como trabajo de aprendizaje y
portfolio.

## Decisión

Se mantiene el español en:

- Módulos propios.
- Funciones internas.
- Variables de dominio.
- Documentación.
- Reportes del proyecto.
- Descripciones de commits.

Se mantienen en inglés:

- Columnas originales de NOAA.
- Nombres de archivos originales de NOAA.
- APIs externas.
- Dependencias.
- Convenciones técnicas estándar cuando corresponda.

- Eventualmente se hara un readme en ingles y u ndashboard bilingüe.

## Regla práctica

Usar nombres semánticos en español, sin acentos en identificadores Python.

Ejemplos:

```python
def normalizar_nombre_columna(nombre_columna: str) -> str:
    ...


def convertir_danio_estimado(valor_crudo: str) -> float:
    ...


def validar_eventos_detalle(datos_eventos: pd.DataFrame) -> None:
    ...


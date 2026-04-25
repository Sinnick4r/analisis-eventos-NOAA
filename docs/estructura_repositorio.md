# Estructura del repositorio

Este documento describe la estructura objetivo de la actuqalización.

## Carpetas principales

| Carpeta | Proposito |
|---|---|
| `src/noaa_eventos/` | Código reusable del proyecto. |
| `tests/` | Tests automatizados. |
| `config/` | Configuración del flujo de trabajo. |
| `data/raw/` | Datos RAW descargados localmente desde NOAA. No se versionan. |
| `data/processed/` | Datos procesados generados por el pipeline. No se versionan. |
| `data/samples/` | Muestras pequeñas versionables para tests o documentacion. |
| `reports/validacion/` | Reportes de validación generados. |
| `reports/powerbi/` | Salidas preparadas para Power BI. |
| `docs/` | Documentación metodologica y decisiones técnicas. |
| `legacy/` | Material histórico del proyecto original. |
| `notebooks/` | Exploración manual. No contiene lógica productiva. |

## Principio de diseño

La actualizacion no expande el alcance del proyecto. Solo ordena y prepara
la base para convertir la exploracion original en un proyecto de analisis
reproducible.

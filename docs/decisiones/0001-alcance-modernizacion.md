# Decisión 0001 — Alcance de la modernización/actualización

## Contexto

Este proyecto comenzó como una exploración personal de datos del dataset del NOAA 2024,
realizada durante una etapa de aprendizaje. La versión original incluye
limpieza de datos con Python, datasets procesados y una visualización
preliminar en Power BI.

La acualziacion no busca expandir el alcance analítico ni convertir el
proyecto en una plataforma de ingeniería de datos. El objetivo actual es
profesionalizar lo existente para presentarlo como proyecto en un portfolio

## Decisión

La etapa de modernización mantiene el foco en:

- Ordenar la estructura del repositorio.
- Preservar el origen del proyecto como evidencia de aprendizaje.
- Mantener nombres de funciones, módulos y documentación en español.
- Separar lógica reusable en `src/`.
- Agregar reproducibilidad local.
- Descargar datos RAW desde NOAA de forma manual/comandada.
- Validar datos críticos.
- Generar datasets procesados.
- Preparar salidas para Power BI.
- Documentar metodología, decisiones y limitaciones.

Todo lo que es aumentar el scope del proyecto queda afuera por ahora, por ejemplo:

- GitHub Actions.
- Ejecución programada.
- Cruce con fuentes externas.
- Orquestadores.
- APIs.
- Docker.
- Cloud.
- Machine Learning.
- etc 

## Consecuencias

El proyecto se moderniza como análisis de datos reproducible, no como
pipeline productivo de data engineering.

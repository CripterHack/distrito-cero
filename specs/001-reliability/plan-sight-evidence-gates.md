# Sight: rechazo de evidencia diagnóstica y guardas incompletas

> Ejecutar con superpowers:executing-plans. Regresión primero y revisión propia.

**Goal:** impedir que el runner acepte un informe comparativo o una partición sight sin las cinco guardas obligatorias.
**Architecture:** reforzar la validación del runner existente y centralizar los nombres de guardas en el contrato compartido con el productor. No crear otro productor, matriz gráfica ni sistema de CI.
**Tech Stack:** Python estándar y suites de QA existentes, sin dependencia de runtime.
**Spec:** [SPEC-001](spec.md), REL-01/02. Soporta la evidencia de [SPEC-003](../003-weapon-contact/spec.md), issue #6.

## Restricciones

Base remota cf7327750edd0c50dfda5f227345d80ac7ca74fb, árbol 56929d6acd902b1ce288f7929e24f357edb05006, producto 0.20.18. Conservar HTML, fuentes de juego, versión, capturas, 94 checks de sight, 61 estados por secuencia, tres particiones, 1800 s/productor y 40 min/job. Sin eliminación de ramas ni reintento de limpieza bloqueada. El historial local restaurado es sintético.

## Foco de revisión

Un exit 0 con `comparisonOnly: true` nunca acredita aceptación. Guardas ausentes, duplicadas, renombradas, mal tipadas o fallidas invalidan la partición. Base contiene guardas dentro de sus checks, no en una lista duplicada. Una partición no puede usar el nombre de otra para omitir validaciones. Las suites históricas sin contrato sight permanecen compatibles.

## Tareas

- [x] Restaurar los 949 archivos versionados y cotejar el árbol exacto. Baseline del runner: 15/15 tests. Revisar código real, contrato y productor.
- [x] Reproducir con procesos reales que escriben informes frescos de exit 0: comparación con checks aprobados y guardas fallidas/ausentes. Añadir pruebas al test existente antes de cambiar validación.
- [x] Rechazar informes comparativos y validar identidad de partición, nombres únicos y guardas completas mediante contrato único. Conservar evidencia fallida y compatibilidad fuera de sight.
- [x] Ejecutar tests Python vigentes, Node completo, build, revisión de diff y revalidación de informes reales de #55. Actualizar HANDOFF/STATE/QA con el cierre comprobado de #55 y el siguiente alcance.
- [ ] Publicar PR sobre padre remoto exacto. Revisar CI, artefactos y revisión propia, integrar sólo si aprueban. Comprobar push y Pages separadamente.

## Reversión y límites

Revertir esta unidad restaura únicamente herramientas/documentación de QA, no toca partidas ni gameplay. No prueba hardware, FPS, arte global ni las rutas de equipo aún sin medir. El gate valida el contrato de un productor, no es una frontera de seguridad contra código arbitrario que falsifique resultados.

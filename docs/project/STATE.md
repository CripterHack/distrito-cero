# Estado real del proyecto

## Versión del árbol: v0.20.11 · Coherencia

Canal prototype, fecha 2026-09-24. Identidad reproducible en
[version.json](../../version.json) y [build-info.json](../../build-info.json).
El PR de cada unidad registra su integración y despliegue. Esta página no
sustituye la CI ni acredita por sí sola una publicación.

## Unidad actual: cambio entre pistola y revólver

Base `5266cb7`, PR #46 y 0.20.10 integrados. Su Verify posterior `36061029294`
terminó con los cuatro jobs aprobados. Ese resultado no es la CI de esta unidad.

Se conserva la pose visible antes de cancelar inputs, también desde el selector
congelado. La transición existente ahora cubre pistola ↔ revólver disponibles
fuera de recarga, con 0.90 s cosméticos. Selección, acciones y disparo lógico
siguen inmediatos e independientes de la presentación. Sin cambios de mallas,
anclas, longitudes, física o formatos de guardado. [Contrato](SIDEARM-HANDOFF.md).

Siete regresiones Node y seis comprobaciones adicionales en la suite sight
acompañan el cambio. CI, evidencia y publicación se registran en su PR.
No confundir pruebas dirigidas o históricas con aprobación del nuevo HEAD.

## Backlog vigente

| Issue | Pendiente real |
| :--- | :--- |
| #5 | Arte global, fuentes/procedencia, materiales/UV y coste sobre hardware. Benchmark y exportaciones ya existen. |
| #6 | Integración del cambio entre armas cortas de esta unidad, cambios entre otras familias, recargas de armas cortas, interrupciones reales, giros/acciones/anatomías combinadas y coste por actor/LOD. |
| #7 | Escena/recorrido completo, playtests humanos y hardware de referencia. |

No cerrar criterios globales por una corrección acotada. Los observadores no
certifican toda la malla, CCD, ausencia universal de penetración ni GPU física.

## Integraciones previas

#46 (`5266cb7`): captura con actor de marcha, 0.20.10.
#45 (`6dd7a01`): salida de recarga 0.20.9. #44 (`3d6722e`): cambio libre 0.20.8.
#43 (`be26fa0`): preparación inicial. #42 (`c27282f`): guardia/recarga.
#39/#40: marcha/apoyo. #41: limpieza y continuidad. #30/#34–#38: rifle,
benchmark, familias y exportación portable. No recrear trabajo ya aceptado.
[Estado anterior completo](https://github.com/CripterHack/distrito-cero/blob/6dd7a01b29d3007377ccfe0d316cecf4235cc270/docs/project/STATE.md).

Campaña, creador, catálogo, vehículos, policía, datos y reglas se conservan.
[HANDOFF](HANDOFF.md), [QA](QA.md), [recursos](ASSETS.md),
[política de ramas](BRANCH-CLEANUP.md). Revisión propia, no independiente.

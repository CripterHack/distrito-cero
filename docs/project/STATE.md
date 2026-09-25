# Estado real del proyecto

## Versión del árbol: v0.20.12 · Coherencia

Canal prototype, fecha 2026-09-24. Identidad reproducible en
[version.json](../../version.json) y [build-info.json](../../build-info.json).
El PR de cada unidad registra su integración y despliegue. Esta página no
sustituye la CI ni acredita por sí sola una publicación.

## Unidad actual: salida de recarga entre pistola y revólver

Base `5c0248f`, PR #47 y producto 0.20.11 integrados. La candidata conserva pose
y pieza visible al cancelar una recarga entre esas armas cortas. Reutiliza la
captura de la UI y el retorno existente de cargador, con duración cosmética de
0.90 s. Selección/cancelación y acciones reales son inmediatas. El cilindro del
revólver permanece rígido, sin nueva apertura. [Contrato](SIDEARM-RELOAD-HANDOFF.md).

Cuatro regresiones Node nuevas y ocho checks adicionales en sight acompañan
el cambio. Sight se ejecuta separado de handoff y graphics con pruebas de unión
íntegra, sin duplicados ni tolerancias relajadas. Este árbol no acredita la CI
completa ni una publicación. Consultar el PR exacto.

## Backlog vigente

| Issue | Pendiente real |
| :--- | :--- |
| #5 | Arte global, fuentes/procedencia, materiales/UV y coste sobre hardware. Benchmark y exportaciones ya existen. |
| #6 | Aceptación de esta salida de recarga, cambios entre otras familias, interrupciones reales, giros/acciones/anatomías combinadas y coste por actor/LOD. |
| #7 | Escena/recorrido completo, playtests humanos y hardware de referencia. |

No cerrar criterios globales por una corrección acotada. Los observadores no
certifican toda la malla, CCD, ausencia universal de penetración ni GPU física.

## Integraciones previas

#47 (`5c0248f`): pistola↔revólver sin recarga, 0.20.11.

#46 (`5266cb7`): captura con actor de marcha, 0.20.10.
#45 (`6dd7a01`): salida de recarga 0.20.9. #44 (`3d6722e`): cambio libre 0.20.8.
#43 (`be26fa0`): preparación inicial. #42 (`c27282f`): guardia/recarga.
#39/#40: marcha/apoyo. #41: limpieza y continuidad. #30/#34–#38: rifle,
benchmark, familias y exportación portable. No recrear trabajo ya aceptado.
[Estado anterior completo](https://github.com/CripterHack/distrito-cero/blob/6dd7a01b29d3007377ccfe0d316cecf4235cc270/docs/project/STATE.md).

Campaña, creador, catálogo, vehículos, policía, datos y reglas se conservan.
[HANDOFF](HANDOFF.md), [QA](QA.md), [recursos](ASSETS.md),
[política de ramas](BRANCH-CLEANUP.md). Revisión propia, no independiente.

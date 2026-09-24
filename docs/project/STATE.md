# Estado real del proyecto

## Versión del árbol: v0.20.10 · Coherencia

Canal prototype, fecha 2026-09-24. Identidad reproducible en
[version.json](../../version.json) y [build-info.json](../../build-info.json).
El PR de cada unidad registra su integración y despliegue. Esta página no
sustituye la CI ni acredita por sí sola una publicación.

## Contexto de presentación al seleccionar durante marcha

Base `6dd7a01b29d3007377ccfe0d316cecf4235cc270`, 0.20.9 del PR #45 integrado.
Su Verify posterior 35977307974 terminó aprobado. No es el resultado de la nueva
unidad. Se corrige la diferencia entre el actor de MotionTracker dibujado y el
actor sin seguimiento usado al capturar la selección.

El cambio pasa explícitamente la lectura visual del renderer desde UI a la
captura. Reutiliza el mismo tracker y montaje. Gameplay y su origen de disparo
permanecen independientes, sin cambios de geometría, huesos, física o partidas.
Siete regresiones nuevas observaron RED/GREEN. Se conserva la batería anterior.
[Contrato, verificación y límites](TRACKED-HANDOFF.md).

La cobertura handoff pasa de 22 a 28 checks por dos casos nuevos de marcha.
La CI divide handoff y gráficos restantes en shards con fallos y artefactos
independientes. Conserva la selección completa/normal sin duplicados y todos los
controles HTTP. Los resultados finales del HEAD se registran en el PR.

## Backlog vigente

| Issue | Pendiente real |
| :--- | :--- |
| #5 | Arte global, fuentes/procedencia, materiales/UV y coste sobre hardware. Benchmark y exportaciones ya existen. |
| #6 | Integración de contexto de marcha de esta unidad, equipos sin dock, interrupciones reales, giros/acciones/anatomías combinadas y coste por actor/LOD. |
| #7 | Escena/recorrido completo, playtests humanos y hardware de referencia. |

No cerrar criterios globales por una corrección acotada. Los observadores no
certifican toda la malla, CCD, ausencia universal de penetración ni GPU física.

## Integraciones previas

#45 (`6dd7a01`): salida de recarga 0.20.9. #44 (`3d6722e`): cambio libre 0.20.8.
#43 (`be26fa0`): preparación inicial. #42 (`c27282f`): guardia/recarga.
#39/#40: marcha/apoyo. #41: limpieza y continuidad. #30/#34–#38: rifle,
benchmark, familias y exportación portable. No recrear trabajo ya aceptado.
[Estado anterior completo](https://github.com/CripterHack/distrito-cero/blob/6dd7a01b29d3007377ccfe0d316cecf4235cc270/docs/project/STATE.md).

Campaña, creador, catálogo, vehículos, policía, datos y reglas se conservan.
[HANDOFF](HANDOFF.md), [QA](QA.md), [recursos](ASSETS.md),
[política de ramas](BRANCH-CLEANUP.md). Revisión propia, no independiente.

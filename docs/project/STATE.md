# Estado real del proyecto

## Versión del árbol: v0.20.13 · Coherencia

Canal prototype, fecha 2026-09-27. Identidad reproducible en
[version.json](../../version.json) y [build-info.json](../../build-info.json).
El producto fue integrado por PR #49 en `0fa83b9`. La unidad de QA descrita
abajo sigue siendo candidata hasta verificar su propio PR. No confundir
los resultados del PR con la comprobación posterior del push a master.

## Unidad actual: terminar la verificación de sight sin perder cobertura

#49 integró rifle ↔ pistola libre y desde recarga, tras aprobar la CI de su
HEAD. No volver a implementar esa ruta. [Contrato](CROSS-FAMILY-HANDOFF.md).
El push de `0fa83b9` aprobó core, handoff, graphics, HTTP, benchmark,
exportación y Pages, pero sight agotó sus 1800 s sin completar el informe.
Ese fallo permanece documentado en [PR #49](https://github.com/CripterHack/distrito-cero/pull/49#issuecomment-5854155400).

La candidata sólo cambia QA: distribuye el mismo productor en `sight-base`
(40 checks) y `sight-cross-family` (18). El alias `sight` conserva ambos.
No cambia `src`, HTML, versión, mallas, shaders, resolución ni tolerancias.
Se conservan todos los pasos de 60 Hz preparados y las capturas. No son FPS.
[Plan y gates](../../specs/003-weapon-contact/plan-sight-ci-partitions.md).

No seguir ampliando cruces antes de verificar esta unidad. Rifle → revólver
fue reproducido con tecla real sobre `0fa83b9`, no corregido: salto inicial
572.778 mm en una sola escena preparada. Es una pareja fuera de #49, no una
regresión nueva demostrada. [Diagnóstico](https://github.com/CripterHack/distrito-cero/issues/6#issuecomment-5854143199).

## Backlog vigente

| Issue | Pendiente real |
| :--- | :--- |
| #5 | Arte global, fuentes/procedencia, materiales/UV y coste sobre hardware. Benchmark y exportaciones ya existen. |
| #6 | Verificación de esta unidad de QA; otros cruces, herramientas/pesados, suavidad de cortes prioritarios, giros/acciones/anatomías combinadas y coste por actor/LOD. |
| #7 | Escena/recorrido completo, playtests humanos y hardware de referencia. |

No cerrar criterios globales por una corrección acotada. Los observadores sólo
muestrean superficies seleccionadas: no certifican toda la malla, CCD, ausencia
universal de penetración, GPU física o una calidad artística ya alcanzada.

## Integraciones previas

#49 (`0fa83b9`): primer cruce rifle/pistola, 0.20.13. CI del PR aprobada,
post-merge sight agotado; los otros gates y Pages aprobaron.

#48 (`613c164`): salida de recarga entre pistola y revólver, 0.20.12.
#47 (`5c0248f`): intercambio libre entre esas armas cortas, 0.20.11.
#46 (`5266cb7`): captura con actor de marcha, 0.20.10.
#45 (`6dd7a01`): salida de recarga larga. #44 (`3d6722e`): cambio libre largo.
#43 (`be26fa0`): preparación inicial. #42 (`c27282f`): guardia/recarga.
#39/#40: marcha/apoyo. #41: limpieza y continuidad. #30/#34–#38: rifle,
benchmark, familias y exportación portable. No recrear trabajo ya aceptado.
[Estado anterior](https://github.com/CripterHack/distrito-cero/blob/613c16495d79e009587c56593ebe9c5a48591406/docs/project/STATE.md).

Campaña, creador, catálogo, vehículos, policía, datos y reglas se conservan.
[HANDOFF](HANDOFF.md), [QA](QA.md), [recursos](ASSETS.md),
[política de ramas](BRANCH-CLEANUP.md). Revisión propia, no independiente.

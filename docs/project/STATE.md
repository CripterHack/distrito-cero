# Estado real del proyecto

## Versión del árbol: v0.20.13 · Coherencia

Canal prototype, fecha 2026-09-27. Identidad reproducible en
[version.json](../../version.json) y [build-info.json](../../build-info.json).
Este árbol es una candidata hasta verificar el PR de su HEAD exacto. El PR
registra integración y comprobaciones posteriores de master/Pages por separado.

## Unidad actual: primer cruce rifle ↔ pistola

Base integrada `613c16495d79e009587c56593ebe9c5a48591406`, PR #48, 0.20.12.
No repetir la salida de recarga entre pistola y revólver. Esta unidad extiende
el montaje existente exclusivamente a rifle ↔ pistola, libre o desde recarga.
Conserva coordinación corporal, articulación inicial de los dedos y pieza
visible anterior. El arco cosmético de 0.90 s incorpora 4 cm adicionales hacia
delante para evitar la penetración muestreada al abandonar la recarga del rifle.
Selección, cancelación, disparo y nueva recarga siguen inmediatos.
[Contrato y límites](CROSS-FAMILY-HANDOFF.md).

Siete regresiones Node cubren la ruta y las invariantes; sight conserva sus
40 comprobaciones y añade 18 mediante cuatro secuencias de tecla real en el
renderer existente. No se crean otra matriz gráfica, solver, tracker o reloj.
Las suites completas, capturas y resultados definitivos pertenecen al PR del
HEAD comprobado, no a esta descripción ni a la CI de #48.

## Backlog vigente

| Issue | Pendiente real |
| :--- | :--- |
| #5 | Arte global, fuentes/procedencia, materiales/UV y coste sobre hardware. Benchmark y exportaciones ya existen. |
| #6 | Aceptación de esta unidad; otros cruces, herramientas/pesados, suavidad de cortes prioritarios, giros/acciones/anatomías combinadas y coste por actor/LOD. |
| #7 | Escena/recorrido completo, playtests humanos y hardware de referencia. |

No cerrar criterios globales por una corrección acotada. Los observadores sólo
muestrean superficies seleccionadas: no certifican toda la malla, CCD, ausencia
universal de penetración, GPU física o una calidad artística ya alcanzada.

## Integraciones previas

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

# Estado real del proyecto

## Versión activa del árbol: v0.20.3 · Coherencia

### Actualización: exportación de autoría

PR #36 integrado como `b96371e`, con Verify/exportación/benchmark aprobados antes del merge y Pages posterior aprobado. El GLB oficial revisado tiene 0 errores y 15 advertencias. Su cadena de hashes y avisos queda registrada en el PR.

La corrección siguiente promueve 14 instancias de malla a raíz sin alterar los huesos o buffers. Tiene RED/GREEN, 14 tests Python y 522 Node aprobados localmente. La validación oficial e integración se registran en su propio PR. El HTML de producto sigue idéntico. [Contrato](CURRENT-HUMAN-EXPORT.md), [plan](../../specs/002-character-benchmark/plan-portable-root.md).


Canal **prototype**, fecha 2026-09-23. Identidad en [version.json](../../version.json), huellas y tamaño en [build-info.json](../../build-info.json). Master `4c615090d7395bda048bee0d1ee2070702833808` integra PR #35. La publicación se confirma en Actions/Pages, no por la existencia de este documento. No cambian configuración de Pages, licencia o esquemas de partidas.

## Última unidad de producto integrada · PR #35

SMG, escopeta y sniper extienden el montaje cooperativo del rifle con miras y siluetas de culata propias. El rifle, anatomía humana, pesos, 49 huesos, anclas palmares, reglas y datos permanecen. El contrato de referencia usa la prenda realmente deformada y conserva la medida articular anterior como legacyStockError. [ADR 0004](../adr/0004-longarm-family-docks.md), [plan](../../specs/003-weapon-contact/plan-longarm-families.md).

Se observaron tres regresiones iniciales de 205–239 mm oculares. Las nuevas pruebas cubren 54 combinaciones centrales, ciclos a 60 Hz, transformaciones y geometría ajena intacta. Antes del merge aprobaron Verify 35843734280 y benchmark 35843734295 sobre b7362fb: 205 checks WebGL, 80 HTTP nativos y 36 de benchmark. Los artefactos, su merge de prueba y hashes se cotejaron. 519 Node y 98 Python aprobaron en reconstrucción exacta; la regresión local adicional aprobó 220 checks de juego con escenas preparadas.

La revisión visual comprendió 20 vistas estáticas y 28 muestras de ciclo. No es una aprobación artística global ni revisión de cada frame. El primer intento gráfico perdió contexto antes de capturar y se conserva como fallido. La repetición aislada utilizó los mismos controles. La comprobación posterior de master es una ejecución diferente.

HTML actual: e91218339a69d948f6af18a0ee43c1dc4874056d4b0ee67bc9353ab7a288b027, 8,866,152 bytes. GLB de equipo: c698c3301665a0a07a66d318f81e96c2c1984e94a4a8bb81e3b9ce3e3a69b329. Recurso humano intacto: 522a9a24e2cc70857a3ec5c18bf9c2126c7b59d9ce8e4c5601c3b8be2c911b54.

## Unidad de autoría integrada · PR #36

[Exportación humana actual](CURRENT-HUMAN-EXPORT.md), CHAR-06 de #5. Genera un perfil neutral con el contenido vigente sin sobrescribir los GLB históricos. Validación oficial separada y artefacto completo, workflow de lectura, sin nuevas dependencias en el juego.

El primer run oficial 35846902847 detectó 13 nodos hoja inválidos y 15,921 advertencias. Se reprodujeron y corrigieron children vacío e índices con peso cero en la salida portable, no en las fuentes. Nueve tests Python comprueban aislamiento y cambios permitidos. La revisión final 6327b1c aprobó Verify, exportación y benchmark; el PR se integró como b96371e tras revisar el reporte oficial de cero errores y 15 advertencias. Se mantienen los avisos de portabilidad, licencia propia sin decisión nueva y aceptación artística pendiente.

## Backlog vigente

| Unidad | Estado comprobado |
| :--- | :--- |
| #5 · Personaje patrón | Matriz completa previa ejecutada, aprobación artística/procedencia global pendientes. PR #36 añade una exportación actual verificable. |
| #6 · Contactos y recargas | Rifle y tres familias largas corregidos en unidades acotadas. Revisión global de superficies, acciones, vídeo y coste por actor/LOD pendiente. |
| #7 · Vertical slice | Escena, recorrido íntegro, playtest y GPU física pendientes. Los fixtures de campaña no sustituyen estos criterios. |
| #29 · Rifle neutral | Cerrada por PR #30, merge d6da75a, CI posterior aprobada. |
| #33 · Benchmark de apuntado | Cerrada por PR #34, merge 6d1b756, CI posterior aprobada. |
| #31 · Gates CI | Cerrada por PR #32, merge 37ab6f0. Node no oculta ni bloquea verificaciones independientes. |
| #2 / #3 / #4 | QA portable, guardados HTTP y recuperación WebGL integrados. |
| #19 / #21 / #23 / #25 / #27 | Publicación, mira corta, cancelación, recargas HTTP y auditor cooperativo integrados. |

## Sistemas e historia conservados

Campaña, creador, once peinados, doce partidas con nombres, arsenal, selector translúcido, vehículos/ocupantes, policía, daños y regiones procedurales. El suavizado visual no entra al serializador. Sin servicios remotos obligatorios ni cambios silenciosos de munición o permisos.

[Estado anterior completo](https://github.com/CripterHack/distrito-cero/blob/4c615090d7395bda048bee0d1ee2070702833808/docs/project/STATE.md), [rifle](RIFLE-COORDINATION.md), [benchmark](BENCHMARK-AIM.md), [mira corta](SIDEARM-SIGHT.md), [superficie palmar](THENAR-SURFACE.md), [HTTP](../../specs/003-weapon-contact/plan-native-reload.md), [auditor](../../specs/003-weapon-contact/plan-longarm-audit.md) y [rechazos](../../specs/003-weapon-contact/stock-surface-rejection.md) conservan las decisiones y mediciones previas. No repetir su diagnóstico como trabajo pendiente.

La base v0.19 conserva SOURCE-MANIFEST.json, docs/v019 y qa/v019 sin simular actualidad. [ACTIONS-RECOVERY](ACTIONS-RECOVERY.md) conserva fallos históricos. Escenas preparadas y GPU software no demuestran FPS físicos, aprobación artística o un recorrido íntegro. [Handoff](HANDOFF.md), [QA](QA.md), [recursos](ASSETS.md).

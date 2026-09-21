# Estado real del proyecto

## Versión activa del árbol: v0.20.2 · Coherencia

Canal **prototype**, fecha 2026-09-21. Identidad en [version.json](../../version.json), huellas y tamaño exactos en [build-info.json](../../build-info.json). El estado de integración y publicación se comprueba en el PR #30 y Actions, no se deduce de este documento. La configuración de Pages sobre master, permisos, licencia y esquemas de partidas no cambian.

## Última continuación: coherencia del benchmark · #33

PR #30 integrado como `d6da75a`, #29 cerrada. Los tres jobs del Verify posterior `35653621273` ya terminaron success. Se conserva ese resultado separado de cualquier nueva CI.

Se corrige el fixture de personajes que etiquetaba guardia baja como apuntado al dejar rifleAim sin asentar. Dos regresiones reproducidas antes del cambio. Resultado local de esta unidad: 502/502 Node, 9/9 tests de matriz y benchmark de 36 checks/30 PNG cotejados. No cambia el HTML, runtime ni versión. [Contrato, evidencia y límites](BENCHMARK-AIM.md). El PR de #33 registra su aprobación remota e integración.

## Corrección acotada del rifle · #29 / PR #30

Se implementa coordinación suave de torso, clavículas, cabeza y montaje único. La mira conserva sus vértices originales. Se ajustan únicamente dos cuboides cosméticos de la culata, conservando su extremo posterior, agarres, cargador y demás familias. El modelo humano, pesos y 49 huesos no cambian.

**Cambio explícito del contrato de referencia:** el rifle usa un triángulo verificado de la chaqueta y la cara posterior de la culata, no el desplazamiento heredado de una articulación. La distancia a esa referencia antigua sigue registrada como `legacyStockError`. Las tolerancias permanecen: ojo 10 mm, apoyo 30 mm, palmas 12 mm y penetración muestreada 2 mm. [Decisión y límites](../adr/0003-rifle-surface-dock.md), [evidencia y continuidad](RIFLE-COORDINATION.md).

La aceptación que fallaba por 238.64 mm de error ocular ahora aprueba localmente. **500/500 Node**, incluyendo las diez regresiones de superficie del PR y cinco nuevas de referencia, alcance y movimiento. Sin skips. Las 18 combinaciones centrales de cuello, agachado y elevación respetan los límites. No se afirma cobertura universal de anatomías o elevaciones extremas.

La batería gráfica local canónica `20260921T200921Z-9bf157915e17` completó **90 checks**: longarms 24, handling 51, thumbs 15. Las cuatro posturas estáticas de rifle exigen ahora también sus criterios de contacto y holgura. Sus 48 capturas longarms tienen hashes cotejados. En neutral: error ocular por debajo de 0.001 mm, separación de apoyo 10.00 mm, holgura facial 6.99 mm y de chaqueta 1.37 mm. Es medición de un modelo preparado, no precisión física del mundo real ni autocolisión completa.

El nuevo HTML es `acf4f05ccbb4a1a68008bd57876b9e7839628b4127a686715802ec47c7130be8` (8,865,702 bytes). El GLB regenerado es `b8536e990e251b63ba4fcd2c5fcf220d0088654c80f8a241bef594a7e110825c`. La CI del nuevo HEAD debe aprobar independientemente antes del merge. No se reutilizan los jobs verdes de otro commit.

## Backlog vigente

| Unidad | Situación |
| :--- | :--- |
| #29 · Rifle neutral | Cerrada mediante PR #30, merge `d6da75a`, CI posterior aprobada. |
| #33 · Benchmark de apuntado | Fixture corregido y probado localmente. Su PR registra CI e integración. |
| #6 · Contactos y recargas | Continúa abierta. Las otras familias largas y la revisión amplia de superficies, transiciones y anatomías no se consideran resueltas por #29. |
| #5 · Personaje patrón | Benchmark disponible. Aprobación artística, materiales y variantes pendientes. |
| #7 · Vertical slice | Escena, recorrido íntegro, playtest y rendimiento sobre GPU física pendientes. |
| #31 · Gates CI | Cerrada mediante PR #32, merge `37ab6f0`. El fallo Node no bloquea validaciones independientes ni se oculta bajo autoría. |
| #2 / #3 / #4 | QA portable, guardados HTTP y recuperación WebGL integrados. No garantizan cobertura universal de navegadores/drivers. |
| #19 / #21 / #23 / #25 / #27 | Unidades integradas. Publicación, mira corta, cancelación, recarga HTTP y auditor cooperativo conservados. |

El Verify de master `35643937627` y Pages `35643936002` del merge de #32 terminaron success. Son antecedentes de v0.20.1, no aprobación de v0.20.2. El run anterior del PR #30 `35643741627` terminó failure en Node, con WebGL/HTTP y benchmark aprobados. Su fallo permanece histórico.

## Sistemas y evidencia conservados

Campaña, creador, once estilos de cabello, hasta doce partidas con nombres, arsenal, selector translúcido, vehículos/ocupantes, policía, daños y regiones procedurales. Sin servicios remotos, dependencias de runtime o cambios de reglas/munición. El estado nuevo de suavizado es transitorio y no entra al serializador.

Recurso humano SHA-256 `522a9a24e2cc70857a3ec5c18bf9c2126c7b59d9ce8e4c5601c3b8be2c911b54`, intacto. Los GLB humanos anteriores siguen siendo históricos. Los detalles previos están en [SIDEARM-SIGHT](SIDEARM-SIGHT.md), [THENAR-SURFACE](THENAR-SURFACE.md), [plan nativo](../../specs/003-weapon-contact/plan-native-reload.md), [plan del auditor](../../specs/003-weapon-contact/plan-longarm-audit.md) y [variantes rechazadas](../../specs/003-weapon-contact/stock-surface-rejection.md).

La base importada v0.19 (`23f9e9d`) conserva `SOURCE-MANIFEST.json`, `docs/v019/` y `qa/v019/`. No se reescriben para simular evidencia actual. [ACTIONS-RECOVERY](ACTIONS-RECOVERY.md) mantiene los fallos históricos.

Escena/reloj/cámara preparados y GPU software no demuestran FPS, persistencia HTTP, aprobación artística global o una partida completa. La revisión de esta unidad es propia, no independiente. [Handoff](HANDOFF.md), [QA](QA.md), [recursos](ASSETS.md).

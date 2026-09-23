# Estado real del proyecto

## Versión activa del árbol: v0.20.7 · Coherencia

Canal **prototype**, fecha 2026-09-23. Identidad en [version.json](../../version.json)
y [build-info.json](../../build-info.json). La integración/publicación se confirma
en el PR de cada unidad y Actions. Esta página no acredita un despliegue.

## Preparación inicial, continuación del PR #42

Base `c27282f5ae830fe8f149d11396903d89c595acc9`, 0.20.6. PR #42 integrado tras
Verify 35917149375, exportación 35917149458 y benchmark 35917149485 aprobados.
Su revisión conserva 554 Node, 98 Python y los artefactos remotos comprobados.
No heredar esos resultados como aprobación de la nueva revisión.

La candidata 0.20.7 mantiene el mismo apoyo de guardia desde el primer fotograma
y evita interpolar por el origen interior durante ready menor que uno. Acota la
inclinación inicial sólo en rifle, SMG, escopeta y sniper. La curva nativa de ready,
apuntado estable, geometría, alcance, reglas y partidas permanecen. No incorpora
otro solver ni una animación de funda. [Causa y evidencia](INITIAL-PREPARATION.md).

Cinco regresiones con RED observado. **559/559 Node y 100 Python actuales**
aprobaron localmente. La prueba gráfica ampliada conserva los controles previos:
**28 checks y 76 PNG**, con las 28 observaciones iniciales nuevas y hashes cotejados.
Captura canónica adicional: 64 imágenes, vídeo de rifle de 46 frames, 24 instantes
revisados y un detalle. Los escenarios preparados no son un playtest humano.

HTML: `a4e30141a91d632b06db552cfcf5588da3d6fc9e423077dff972bcc20f9030b0`,
8,870,012 bytes. Fuente:
`1b90ec8dd6a48af70171a6e0a524e6837d0a81c2c6ceb6eb3ed07345ed542b4b`.
La CI propia del PR determina su integración. No se relajan tolerancias ni se
reescriben informes previos. La verificación posterior de master es distinta.

## Backlog vigente

| Issue | Pendiente real |
| :--- | :--- |
| #5 · Personaje patrón | Aceptación artística/procedencia global y materiales/UV. La matriz y las exportaciones ya existen. |
| #6 · Contactos y recargas | Integración de preparación inicial, revisión global de cambios de equipo, acciones/anatomías y coste por actor/LOD. La superficie muestreada no equivale a colisión completa. |
| #7 · Vertical slice | Escena/recorrido íntegro, playtests humanos y medición en equipo de referencia. |

No cerrar requisitos globales por el éxito de una unidad acotada. No fabricar
participantes, hardware, FPS o aceptación artística.

## Integraciones que no deben repetirse

#42 (c27282f): guardia/recarga de 0.20.6. #40 (8695273): apoyo dinámico de 0.20.5.
#41 (02e3a14): continuidad y limpieza de ramas. #30/#34–#39: rifle, benchmark,
familias, exportación, raíces, tangentes y marcha cerca del reposo.
[Estado anterior completo](https://github.com/CripterHack/distrito-cero/blob/c27282f5ae830fe8f149d11396903d89c595acc9/docs/project/STATE.md)
conserva sus verificaciones y limitaciones. #2/#3/#4 y las unidades ya cerradas
siguen resueltas dentro de sus alcances. Los registros históricos no son backlog.

La limpieza y [política de ramas](BRANCH-CLEANUP.md) permanecen: master es la única
rama permanente. Las ramas activas de producto/helper son temporales y se retiran
tras comprobar integración y ausencia de trabajo único. Sin nuevos permisos del
repositorio, licencia o dependencias del juego. Los helpers no entran en producto.

Campaña, creador, equipamiento, catálogo de partidas, vehículos, policía, daños y
regiones se conservan. [Handoff](HANDOFF.md), [QA](QA.md), [recursos](ASSETS.md).

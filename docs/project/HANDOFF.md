# Continuación vigente · v0.20.5, PR #40 integrado

## Punto de partida

`master` integra el PR #40 en `86952732d7231312bf305c362d6b07af5257a08b`.
La versión del producto es **0.20.5 · Coherencia**, canal prototype. Leer
[STATE](STATE.md), [QA](QA.md) y la especificación de la siguiente unidad.
No repetir los arreglos de los PRs #30/#32/#34–#40.

El HEAD de #40, `5f7cdc2586f51d9bdb21546323f2dd6a2e503a5d`, aprobó Verify
35883392226, exportación humana 35883392094 y benchmark 35883392101 antes del merge.
Se cotejaron los artefactos: 205 checks WebGL, 80 HTTP, 36 de benchmark y los dos
informes GLB. Una repetición local sobre un checkout de historial real aprobó
543 Node y build inmutable. [Apoyo dinámico](SUPPORT-RELEASE.md) conserva causa,
criterios y vídeos anteriores. La CI posterior se consulta por el SHA de master
en el PR, sin heredar el resultado de la rama revisada.

## Siguiente trabajo de producto

Prioridad de #6: reproducir y corregir penetraciones de culata/prenda durante
**guardia y recarga** con el montaje compartido. Partir de los vídeos y casos ya
medidos, no de la prueba neutral resuelta. Usar `tools/qa/stock_clearance.js`,
`longarm_contact.js` y las pruebas de familias existentes. Conservar superficies,
anclas de manos, alcance, continuidad de pies, munición y datos. Primero regresión
fallida, después corrección acotada y evidencia del renderer canónico.

#5 mantiene decisión artística global, procedencia y revisión de materiales/UV.
#7 mantiene escena y recorrido íntegro, playtests humanos y GPU física. No inventar
aprobaciones, participantes o mediciones para cerrar esos criterios. La matriz
completa previa y la exportación GLB ya existen: no recrearlas como nueva feature.

## Ramas y contexto

La limpieza autorizada retiró 31 ramas antiguas con respaldo Git completo,
comparación por contenido y borrado atómico condicionado a sus SHAs. Ver
[BRANCH-CLEANUP](BRANCH-CLEANUP.md) para el manifiesto y recuperación. Las ramas
auxiliares de esta operación no son líneas de desarrollo y se retiran al cerrar
el PR documental. `master` es la única rama permanente; conservar sólo trabajo
activo. El historial de PRs no es backlog pendiente.

El bundle verificado permite un checkout auténtico incluso donde falla DNS.
No volver a fabricar historia de un snapshot de Pages ni introducir helpers de
reconstrucción en producción. Toda nueva rama debe basarse en el `master` remoto
actual, no en el estado previo al respaldo.

## Verificación al retomar

```sh
python3 build.py --check
node --test tests/*.test.cjs
python3 tests/release_build.test.py
```

Ejecutar además los gates de [QA](QA.md) afectados, revisar diff/artefactos del HEAD
exacto y comprobar publicación separadamente. No cambiar permisos, licencia,
versión o datos por una limpieza documental. Revisión propia, no independiente.

[Handoff anterior completo](https://github.com/CripterHack/distrito-cero/blob/86952732d7231312bf305c362d6b07af5257a08b/docs/project/HANDOFF.md)
conserva la implementación, variantes rechazadas y fallos del helper de #40.

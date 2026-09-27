# Continuación vigente · QA de sight tras PR #49

## Base integrada y fallo real

Master `0fa83b9e024819821e135a9de540a3f897bc9c78`, producto 0.20.13,
árbol de producto `f5776e2c5fd2b05fe90ff477af1dcafeb7cef5d7`.
PR #49 está integrado tras aprobación de su HEAD, no repetir rifle ↔ pistola
libre/recarga. El push Verify `36304175245` falló sólo en sight: 1800.008 s,
exit 124, informe incompleto. Los 44 mensajes PASS no constituyen un resultado
aprobado. Core, handoff, graphics, HTTP, benchmark, exportación y Pages pasaron.
[Registro exacto](https://github.com/CripterHack/distrito-cero/pull/49#issuecomment-5854155400).

## Unidad actual

[Plan](../../specs/003-weapon-contact/plan-sight-ci-partitions.md): particiones
sin solapamiento del productor existente, base 40 y cruce 18. Alias `sight`
ejecuta ambas y deduplica selecciones explícitas. El productor directo sin
flag sigue ejecutando los 58 checks. Misma densidad, fotogramas, resolución,
renderer, umbrales y capturas. Cambia la distribución de CI, no el juego ni su
versión. Las particiones no son una matriz de escenarios nueva.
Ambas ejecutan las cinco guardas compartidas, también el selector tras acabar
con rifle; se cuentan sólo en base y quedan registradas sin doble conteo en
`guards` del cruce. Cualquier guarda fallida impide aprobar la partición.

No declarar terminado antes de comprobar la CI y artefactos de este HEAD.
La unión debe conservar los 58 nombres, ocho secuencias, 61 estados por
secuencia y sus imágenes. Todos los demás gates permanecen activos.
Después del merge verificar el push y Pages por separado. Registrar allí los
resultados finales, nunca convertir la ejecución fallida de #49 en aprobada.

## Pendientes reales

#6 conserva otros cruces, herramientas/pesados, cortes prioritarios visuales,
giros/anatomías combinadas, coste por actor/LOD y aceptación global. Una acción
real tiene prioridad: no retrasar disparo o recarga para ocultar un corte.
Rifle → revólver libre ya tiene un caso reproducido sobre esta base con la
tecla Digit2, sin avanzar simulación; no se ha implementado su transición.
[Diagnóstico](https://github.com/CripterHack/distrito-cero/issues/6#issuecomment-5854143199).

#5 mantiene arte/procedencia/materiales/UV. Los GLB de PR y push no son siempre
idénticos binariamente: se observaron variaciones sólo en animaciones de hasta
7.11e-15, no en mallas/texturas. [Registro y límites](https://github.com/CripterHack/distrito-cero/issues/5#issuecomment-5854086868).
#7 mantiene recorrido íntegro, playtests humanos y hardware. No fabricar evidencia.

## Verificación y recuperación

```sh
python3 build.py --check
node --test tests/*.test.cjs
python3 tests/qa_selection.test.py
python3 tests/ci_workflow.test.py
xvfb-run -a python3 -m tools.qa.run --suite sight --headed --timeout 1800
```

Ejecutar además [QA](QA.md). `--timeout` se aplica por productor, no al alias
completo. CI conserva 1800 s por partición; el tiempo agregado de runners
permitido aumenta al distribuirlas. No afirmar una mejora del rendimiento
físico del juego por este reparto.

[BRANCH-CLEANUP](BRANCH-CLEANUP.md): ramas de #49 retiradas con respaldo y SHA
exacto. Sólo master es permanente; conservar únicamente trabajo activo. El
bundle `pr49-backup-36304799177` contiene master y ambas ramas concluidas y se
restauró en un repositorio vacío. Ningún helper entra al árbol del producto.
Revisión propia, no independiente. Reversión de QA sin migrar ni borrar partidas.

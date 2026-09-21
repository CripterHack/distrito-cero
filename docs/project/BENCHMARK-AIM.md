# Benchmark: apuntado preparado del rifle

Issue #33. Refs #5 y #6. Base `d6da75a76201866fe7167fd0f8cbb46441c2c3c7`, producto 0.20.2. La integración del PR #30 y el cierre de #29 están confirmados. Su Verify posterior `35653621273` completó los tres jobs en success. El correctivo de este documento tiene su propio PR y no hereda esa aprobación.

## Defecto y corrección

El escenario de personajes preparaba `ready=1` y `aimWeight=1`, pero dejaba `rifleAim=0`, el valor inicial al equipar. Sin avanzar el reloj, la primera captura podía mostrar Guardia baja bajo la etiqueta Apuntado de fusil. No era una regresión del apuntado en la partida. Longarms ya preparaba ese filtro por separado.

`character_stage.js` asienta el filtro transitorio de rifle con el apuntado solicitado. Después de dibujar, exige la fase Apuntar para rifle con aim=1 sin recarga. Una discrepancia aborta la captura en vez de producir evidencia mal etiquetada. No se sustituye el renderer ni se modifica el juego.

Dos regresiones usan el fixture, simulación, montaje y rig reales con fronteras DOM/GPU simuladas. Detectan el filtro bajo y la ausencia de rechazo de una fase incorrecta. La prueba gráfica utiliza el renderer real, no esas fronteras simuladas.

## Verificación de esta continuación

RED: seis pruebas anteriores aprobadas y dos nuevas fallidas. GREEN: ocho aprobadas en el archivo y 502/502 en Node completo, sin skips/canceladas/todo. Matriz Python: 9/9. Build inmutable aprobado.

Benchmark canónico local `20260921T221156Z-44c19248a241`: 36 checks aprobados, 30 PNG con hashes cotejados, cero errores y peticiones externas. La captura neutral de apuntado registra Apuntar y fue revisada visualmente. Chromium del sistema, Xvfb, GPU software, escena/reloj preparados y Storage fixture. Commit local null: snapshot del artefacto Pages, no un checkout Git. No equivale a FPS físicos, persistencia HTTP o aprobación artística global.

HTML intacto: `acf4f05ccbb4a1a68008bd57876b9e7839628b4127a686715802ec47c7130be8`. Se conservan src, assets, versión, partidas, workflows y permisos. La nueva CI se comprueba por el HEAD del PR antes del merge y master/Pages por separado después. Las capturas anteriores no se reescriben.

## Reproducción y reversión

```sh
node --test tests/character-stage.test.cjs
node --test tests/*.test.cjs
python3 tests/character_matrix.test.py
python3 build.py --check
xvfb-run -a python3 -m tools.qa.run --suite characters --headed
```

Revertir fixture/tests y esta actualización documental, sin migrar partidas. El ensayo de sesión interactiva del laboratorio no estuvo disponible, por lo que el benchmark se ejecutó como proceso con log y código de salida dentro de la misma sesión. No fue un fallo de producto ni se relajó ningún gate.

## Siguiente paso

Usar la referencia corregida para la revisión artística de #5 y las siguientes familias de #6. #7 conserva sus condiciones de escena, recorrido íntegro, playtest y hardware físico. No repetir #29, construir otro auditor equivalente ni cerrar estos alcances por el éxito de este fixture. [Handoff](HANDOFF.md), [estado](STATE.md), [rifle](RIFLE-COORDINATION.md).

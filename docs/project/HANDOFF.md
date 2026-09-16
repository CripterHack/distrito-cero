# Handoff · v0.20 Coherencia y superficie palma/pulgar

Base publicada previa: `ef905ec`. Trabajo recuperado: `91ba765` de `fix/006-palm-webbing`, que había quedado sin PR. Versión activa del árbol: **v0.20 / 0.20.0**. Leer [STATE](STATE.md), [RELEASES](RELEASES.md) y [THENAR-SURFACE](THENAR-SURFACE.md).

## Unidad actual

Correctivo de contorno recuperado: máximo 4 mm en una zona de piel, sin cambiar pesos, rig, contactos o reglas. Las regresiones originales fallan sobre ef905ec y pasan con el recurso corregido. No repetir una modificación de pivotes para ocultar la superficie. Mantener apoyo palmar, dedos, pulgar y ambas manos.

`version.json` define número, nombre, canal y fecha. El build genera etiquetas, `DC.BuildInfo` y `build-info.json`. No cambiar esquemas de guardados al aumentar versión de producto. `--check` no repara archivos. README, STATE, changelog y guía vigente deben mantenerse coherentes sin reescribir informes históricos.

## Verificación

```sh
python3 tools/refine_thenar.py --check
python3 tests/thenar_contour.test.py
python3 tools/rebind_garment.py --check
python3 tests/garment_binding.test.py
python3 build.py --check
python3 tests/release_build.test.py
node --test tests/*.test.cjs
python3 -m tools.qa.run --suite all
python3 -m tools.qa.run --suite release --suite native --origin http
```

Revisar HEAD, CI y PR. Después comprobar la CI del push y Pages contra el hash del sidecar y las etiquetas de inicio/pausa. No borrar runs históricos ni atribuir un resultado viejo a una ejecución nueva. Leer cifras vigentes del run exacto.

## Issues y siguiente unidad

#2/#3/#4 mantienen su alcance cerrado. #5/#6/#7 están abiertos. #19 sólo se cierra tras comprobar identidad y publicación. El cambio de versión no acredita anatomía o contactos completos.

#6: fijar caso visual de ojo/mira y fases intermedias de liberación/retorno, con el montaje único y límites de alcance. Examinar superficies, no sólo pivotes. No deformar cara, alargar huesos o trasladar manos arbitrariamente. Conservar regresiones de contorno, falanges, mangas, codos, recargas y recuperación.

#5: revisión artística completa contra la matriz existente. #7: escena y recorrido íntegro sin posiciones preparadas. Hardware físico y playtest humano no se deducen del renderer por software.

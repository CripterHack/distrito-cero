# Handoff · contorno palma/pulgar y regresión de Actions

Base de esta unidad: master `ef905ece47bc8901c28c381ef081486e72fa8730`. #2/#3/#4 conservan su alcance resuelto. #5/#6/#7 continúan abiertos. Pages publica master, sin cambios de configuración.

## Unidad implementada

Leer [THENAR-SURFACE.md](THENAR-SURFACE.md) y el [plan](../../specs/003-weapon-contact/plan-thenar-surface.md). Dos tests reprodujeron penetración de la zona mixta que el filtro de influencias no medía. Se descartó un ajuste de pesos por pliegues nuevos. La corrección seleccionada reduce suavemente el volumen volar hasta 4 mm, manteniendo pesos, UV, topología, rig, anclas y reglas.

La semilla dispersa permite reproducir el recurso sin duplicarlo íntegro. Las normales reciben el mismo correctivo. `thenarContour` identifica la versión de autoría. Los GLB humanos anteriores siguen históricos, no se presentan como exportaciones nuevas.

Nueve tests Node, ocho Python de autoría y la suite gráfica `thenar` (15 checks/11 capturas). Los resultados actuales deben leerse en el PR y Actions, no deducirse del número de pruebas escritas. Mantener guardados HTTP nativos separados de fixtures gráficos.

## Verificación

```sh
python3 tools/refine_thenar.py --check
python3 tests/thenar_contour.test.py
python3 tools/rebind_garment.py --check
python3 tests/garment_binding.test.py
python3 build.py
node --test tests/*.test.cjs
python3 -m tools.qa.run --suite all
python3 -m tools.qa.run --suite native --origin http
```

Revisar HEAD, diff y CI del PR antes de integrar. Después comprobar la CI del push a master y la huella del HTML servido por Pages. Las ejecuciones fallidas históricas no se borran ni se reinterpretan como un fallo actual. El correctivo de generaciones WebGL retiradas de #17 permanece intacto.

## Siguiente unidad

#6: revisar alineación visual ojo/mira con el montaje único y restricciones de alcance. Localizar primero un caso y crear una referencia fija; no deformar la cara o mover la palma para forzar una mira. Continuar observando zonas mixtas y fases de recarga/liberación sin afirmar autocolisión completa. Preservar las regresiones de superficie, falanges, pulgar, ambas manos, mangas y codos.

#5 conserva revisión artística de proporciones, materiales y cabello con el benchmark. #7 mantiene escena, mundo, recorrido íntegro y playtests. No cerrar por cifras de QA ni recorridos con posiciones preparadas. No hay medición de FPS físicos en esta entrega.

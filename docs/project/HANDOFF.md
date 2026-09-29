# Continuación vigente · capacidad de QA, producto 0.20.19

## Producto integrado: no repetir #57

[PR #57](https://github.com/CripterHack/distrito-cero/pull/57) está integrado en
**5f222410ec48473c371c3e4a84052667d354cc7e**, árbol
**d168a059695c62be7b96da4ab6fcecd1eb2d3bc7**. Pistola ↔ SMG mantiene pose y
pieza, libre y desde recarga, selector congelado y retorno. Prioridad inmediata,
munición, partidas, geometría y rig intactos.

Su push **36480927360** aprobó siete jobs. Benchmark **36480927408**, exportación
**36480927618** y Pages **36480926757** aprobaron y se cotejaron por separado.
323 WebGL, 80 HTTP, 36 benchmark; 112 checks sight y veinte intercambios.
El cierre de #57 contiene evidencia y límites. El push de #56 también está cerrado.

## Unidad actual: medir antes de optimizar

[Plan REL-01/02](../../specs/001-reliability/plan-sight-capacity.md), issue #6.
Base de sight en el push de #57: 1766.227 s de 1800, sólo 33.773 s de margen.
Los otros productores tardaron 1673.322 y 1374.602 s. No añadir más escenarios
sin medir; estos tiempos no son FPS ni comparaciones controladas de hardware.

El productor existente registra secciones y operaciones mediante temporizadores
QA exclusivos. Cada operación se invoca una vez y sus excepciones se propagan.
Python mide segundos de pared del host. Las medidas del navegador separan draw
(incluye gl.finish), inspección ocular y culata; están contenidas en el tiempo
host y **no se suman a éste**. Logs SIGHT_TIMING indican inicio y cierre de cada
sección. Un timeout sigue siendo fallo, aunque existan secciones anteriores.

Se conservan HTML, versión, fuentes de juego, catálogos, orden, 112 checks,
veinte casos con 61 estados, 820×680, capturas, cinco guardas y límites de CI.
El verificador estricto de #56 sigue decidiendo aceptación, no los temporizadores.
No se ha atribuido una aceleración al mero hecho de añadir mediciones.

## Validación e integración

La base restaurada reconstruye los 951 archivos y su árbol exacto, con historia
local sintética. Baseline: build y 632/632 Node. Regresiones de temporizadores:
primero diez fallos esperados por ausencia de implementación y un fallo adicional
por metadatos ausentes. Las pruebas dirigidas posteriores aprobaron. Tras quitar
sólo instrumentación se contrastó el AST del productor con la base.

La medición completa, CI del HEAD, informes, imágenes y eventual merge se
registran en el PR vinculado en [issue #6](https://github.com/CripterHack/distrito-cero/issues/6).
Estas notas de implementación **no anticipan el resultado del navegador o CI**.
Los intentos interrumpidos o fallidos conservan su estado. Revisión propia,
no independiente. Consultar [Capacidad de sight](SIGHT-CAPACITY.md) para interpretar las mediciones.

```sh
python3 build.py --check
python3 tests/qa_reporting.test.py
python3 tests/qa_runner.test.py
python3 tests/qa_selection.test.py
python3 tests/ci_workflow.test.py
node --test --test-concurrency=4 tests/*.test.cjs
xvfb-run -a python3 -m tools.qa.run --suite sight --headed --timeout 1800
```

## Siguiente decisión

Revisar coste por sección/operación del productor completo antes de optimizar o
redistribuir. Exigir los mismos nombres, estados y observaciones de las veinte
secuencias, más revisión de imágenes. No extrapolar tiempos de otro navegador o
cambiar tolerancias, resolución o checks para mejorar una cifra.

#6 mantiene otras parejas, herramientas/pesados, giros/anatomías, cortes visuales
prioritarios y coste por actor/LOD. #5 conserva arte/procedencia/UV y #7 recorrido,
personas y hardware. No cerrar globales por conteos. Revertir esta unidad afecta
sólo QA/documentación, no juego ni partidas. No reintentar limpieza bloqueada,
borrar ramas, integrar helpers de transporte o modificar manifiestos históricos.

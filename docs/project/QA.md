# QA reproducible desde el repositorio

## Runner vigente (DC-001 / issue #2)

```sh
python3 -m tools.qa.run --suite handling
# Chromium instalado en una ruta explícita, con Xvfb en Linux:
xvfb-run -a python3 -m tools.qa.run --suite handling --browser /usr/bin/chromium --headed
# Las cinco suites de navegador heredadas, con sus aserciones conservadas:
xvfb-run -a python3 -m tools.qa.run --suite all --headed --timeout 600
python3 tests/qa_runner.test.py
```

Omitir `--browser` selecciona el Chromium instalado por Playwright. `--headed` utiliza un display existente o el proporcionado por `xvfb-run`; `--display` permite configurarlo explícitamente. No se instala ni se sustituye el navegador del sistema. Python 3.12, Node 22 y Playwright 1.57.0 son las versiones de referencia de CI, no dependencias para jugar.

El runner acepta `--root`, `--output`, `--browser`, `--origin`, `--headed`, `--display` y `--timeout`. La salida debe ser un directorio NUEVO bajo `<root>/artifacts/`. Rechaza rutas que escaparan mediante symlink, destinos existentes y suites de un modo de origen distinto. Cada ejecución genera un `runId` y usa una copia aislada sin los informes históricos. No modifica el checkout, sus partidas o `qa/v019/`.

`run.json` registra commit, hash del HTML, configuración, códigos de salida, duración y resultado por suite. Los logs se conservan incluso al fallar. El gate exige proceso satisfactorio, informe nuevo, número exacto de aserciones, cero fallos/errores/peticiones externas y el mismo HTML antes/después. Un timeout termina el grupo de procesos, incluido el navegador. Un JSON antiguo aprobado nunca sustituye una ejecución.

## Registro explícito de suites

| Suite | Comando original | Aserciones actuales |
| :--- | :--- | ---: |
| handling | contact_browser.py | 51 |
| arsenal | contact_arsenal.py | 78 |
| library | contact_library.py | 64 |
| campaign | contact_legacy.py | 52 |
| continuous | contact_continuous.py | 26 |

Estos casos usan `--origin fixture`: HTML inyectado y almacenamiento en memoria. La continua conserva RAF, renderer, cámara y simulación, pero también prepara posiciones iniciales. Las otras controlan keyframes para separar lógica y coste gráfico. **No son persistencia nativa ni un benchmark físico.** Las aserciones se conservaron al extraer la configuración de lanzamiento a `tests/qa_support.py`.

## Pruebas básicas

```sh
python3 build.py
node --test tests/*.test.cjs
python3 tools/export_contact.py
python3 tests/contact_exports.test.py
git diff --exit-code -- index.html assets/dc019-equipment.glb
```

En una feature con cambios de runtime, regenerar y versionar la salida revisada. La CI comprueba que el commit incluye el HTML correcto. No sumar recuentos de versiones viejas como resultados nuevos.

## Evidencia original y ejecución actual

`qa/v019/` y `SOURCE-MANIFEST.json` se mantienen como evidencia de la importación. Los auditores históricos que deducen la base del primer commit de Git no son gates universales de este repositorio. No ejecutar toda la colección de tests geométricos históricos con criterios contradictorios entre versiones.

La CI usa el mismo runner del desarrollador y publica sólo su directorio de artefactos. El número de tests no certifica anatomía, realismo, diversión, FPS ni cobertura completa del mundo abierto.

## Próximas puertas

Persistencia nativa HTTP con cierre/reapertura, dos pestañas, lifecycle WebGL, recursos bajo recorridos largos y dispositivos físicos. Cada una debe tener su propio informe y modo explícito. Un bloqueo de navegación del laboratorio se registra como bloqueo, no se elude ni se reemplaza con un fixture anunciado como nativo.

Referencias: documentación oficial de Playwright sobre BrowserType y persistent contexts, y MDN WebGL context lost/restored. Las pruebas de navegador pueden requerir herramientas de desarrollo instaladas; el juego no las requiere.

## Regresión de falanges

`python3 -m tools.qa.run --suite fingers` ejecuta 15 comprobaciones del renderer y produce 12 imágenes. El helper `tools/qa/finger_surfaces.js` no se incorpora al HTML. El modo fixture no demuestra persistencia nativa ni aprobación artística. Véase [alcance y límites](FINGER-CONTACTS.md).

## Regresión de oposición del pulgar

`--suite thumbs` produce quince checks y capturas en su directorio aislado. Utiliza proxies de arte y piel DQ del renderizador, con tiempo/cámara preparados y almacenamiento fixture. `tests/thumb-contact.test.cjs` añade once pruebas de contacto, envolvente digital, longitud, fases y no mutación. La CI ejecuta esta unidad junto a las falanges de PR #15, óptica y recuperación. No sustituye la suite `native --origin http`.

## Contacto entre manos

La suite `sidearms` añade veinte comprobaciones del renderer con seis poses de pistola/revólver, fases de recarga, selector y óptica. `tests/sidearm-support.test.cjs` contiene nueve pruebas. El helper usa piel real y envolventes segmentadas de la mano opuesta; no representa autocolisión completa. Al capturar comparaciones locales se mantiene un `report.json` por directorio, y sólo el harness escribe el informe canónico aislado.

## Superficie completa de la banda palma/pulgar

La suite `thenar` añade 15 comprobaciones gráficas y 11 capturas. `tests/thenar-surface.test.cjs` aporta nueve tests Node y `tests/thenar_contour.test.py` ocho de autoría. La cohorte permanece fija (806/803 puntos), independiente de los pesos. Regenerar con `tools/refine_thenar.py`, luego `build.py`; exigir `--check` en CI. Es una prueba gráfica con almacenamiento fixture, no persistencia nativa. Ver [alcance y límites](THENAR-SURFACE.md).

## Publicación vigente v0.20

`python3 build.py --check` verifica HTML y `build-info.json` sin escribir. `python3 tests/release_build.test.py` prueba identidad, build reproducible, cambios de fuentes, metadatos, plantillas inválidas y comprobación no mutante.

`python3 -m tools.qa.run --suite release --origin http` ejecuta 14 comprobaciones de versión visible/inmutable, huella, importación del JSON sintético v0.19, exportación y reapertura real. Usa almacenamiento nativo. `--suite all --origin http` incluye release, native y reload. La evidencia nueva de versión se escribe en `qa/v020/` de una copia aislada. Las suites anteriores conservan sus rutas dentro de copias efímeras con hash actual.

`thenar` aporta 15 comprobaciones gráficas/11 capturas, nueve tests Node y ocho Python de autoría. No elimina requisitos de palmas, falanges, oposición, ambas manos o recuperación. La procedencia del JSON antiguo está en `tests/fixtures/v019-slot-provenance.json`. No contiene datos personales.

## Parche 0.20.1: referencia ocular

La suite `sight` añade 24 comprobaciones de renderer, referencias oculares, alcance y transiciones, con almacenamiento fixture. `--suite all` en modo fixture incluye catorce suites; modo HTTP conserva `release`, `native` y `reload` sin mezclarlas. Las cifras de resultados deben leerse del run, no de esta lista. Ver [SIDEARM-SIGHT](SIDEARM-SIGHT.md).

Revisión PR #22: `tests/sidearm-draw-onset.test.cjs` incluye el fotograma inicial; `sight` suma 26 comprobaciones por los dos casos nuevos de inicio/fin de preparación visual. Los informes anteriores de 24 siguen siendo históricos.


## Recargas, pausa e inputs de navegador · #25

`xvfb-run -a python3 -m tools.qa.run --suite reload --origin http --headed --timeout 1800` ejecuta el [plan nativo](../../specs/003-weapon-contact/plan-native-reload.md). El contrato exige 31 checks: hash y Storage nativo, 21 checkpoints de rifle/revólver/escopeta, tres recargas por teclado con entrada retenida/nueva, dos cambios de equipo, cancelación Gauss, catálogo intacto y ausencia de errores/peticiones. Esta cifra describe cobertura requerida, no un resultado anticipado.

Se preparan mundo y temporizadores estando en pausa. Durante la observación se mantienen el RAF, el contador de frames, la simulación, los handlers UI, el renderer y Web Storage de producción. Los observadores de piezas y eventos sólo registran y delegan. La congelación debe coexistir con frames vivos y la reanudación debe transferir munición exactamente una vez. Los snapshots incluyen munición de todos los equipos y multiplicidad de piezas dibujadas.

`python3 tests/reload_contract.test.py` comprueba el validador con doce tests y controles negativos de reloj detenido, tiempo adelantado, inputs reactivados, piezas duplicadas, finalización repetida y munición incorrecta. `tests/qa_selection.test.py` impide ejecutar `reload` como fixture. La CI no retira las suites previas ni cambia permisos.

El informe nuevo es `reload.json`, con capturas y datos en `evidence/v020/reload/` del directorio de artefactos. No certifica persistencia tras reinicio (esa función sigue en `native`/`release`), Pointer Lock, inputs físicos, recorrido completo, autocolisión, calidad artística o GPU física. La ejecución HTTP local de esta unidad fue bloqueada con `ERR_BLOCKED_BY_ADMINISTRATOR`, sin sustituirla por HTML inyectado. Exigir el resultado y artefacto de GitHub Actions del HEAD exacto antes de integrar.


## Primer run HTTP de #26: presupuesto insuficiente

La CI [35425812835](https://github.com/CripterHack/distrito-cero/actions/runs/35425812835), HEAD `7bf024e`, aprobó `release` (14) y `native` (35). `reload` completó 27 de sus 31 checks sin una aserción fallida, pero el runner terminó el productor a los 900 s (`exitCode=124`). Las 25 capturas conservadas muestran avance secuencial de casos entre 06:11 y 06:24 UTC. No se declara aprobada esa ejecución ni se elimina su [artefacto fallido](https://github.com/CripterHack/distrito-cero/actions/runs/35425812835/artifacts/10579311131).

Se amplía el presupuesto de la suite a 1,800 s y el trabajo HTTP a 35 minutos. No cambian los 31 checks, temporizadores del juego, reglas, tolerancias, renderer, RAF, inputs o almacenamiento. El ajuste responde al tiempo observado de estos escenarios preparados, no es una corrección de gameplay ni una medición de GPU física.

Cada check guarda además `reload.progress.json` de forma atómica con snapshots y fecha de observación. Es un diario **in_progress**, nunca el informe final `reload.json` que exige el runner. Cuatro tests adicionales rechazan sobrescribir el informe canónico, borrar fallos, duplicar observaciones o modificar sus datos. `tests/reload_contract.test.py` suma 16 pruebas: doce del contrato y cuatro del diario. La aceptación exige una ejecución nueva completa del HEAD revisado.


## Auditor cooperativo de armas largas · #27

```sh
node --test tests/longarm-contact.test.cjs
python3 tests/longarm_gallery.test.py
xvfb-run -a python3 -m tools.qa.run --suite longarms --headed --timeout 600
```

`longarms` utiliza exclusivamente `--origin fixture`. Sus **24 checks** validan la medición y la captura, no la postura del juego. Produce 48 imágenes: cuatro poses, vista frontal y siete muestras del ciclo por cada familia. Registra además 72 poses numéricas de cuello/agachado/elevación y 60 pasos de simulación por familia. Sólo uno de cada diez pasos del ciclo se dibuja para la galería. No afirmar continuidad visual de cada fotograma.

`tools/qa/longarm_contact.js` consume la paleta dibujada, valida el ojo derivado de la malla, las miras de cada familia y la cara posterior de la culata. Los extremos de cada segmento del brazo se obtienen de matrices distintas. Trece pruebas Node incluyen controles negativos de paleta incompleta/no finita, geometría ausente o de otra familia, estiramiento, falsa alineación ocular, contactos no finitos y no mutación. Cuatro pruebas Python protegen etiquetas, rutas de imágenes y la separación entre una ejecución válida y la aceptación artística.

El informe canónico es `longarm-contact.json`. Galería, parámetros e imágenes se conservan bajo `evidence/v020/longarms/`, con `report.html` como entrada. El campo `screening.status` puede indicar `needs-coordination` aunque el proceso y los 24 checks aprueben. Es intencional: se ha medido válidamente un defecto pendiente. `artisticAcceptance` siempre es `false`. No usar este job para cerrar #6 ni presentar el contrafactual de traslación como una pose corregida.

El primer intento local sin ventana no pudo crear WebGL2 y terminó fallido sin checks. Se conservó su informe y se utilizó el modo headed/Xvfb ya existente en CI, sin variar umbrales o runtime. La primera ejecución headed aprobó los 24 checks en 116.661 s. Las repeticiones tienen su propio manifiesto y resultado. Esto no es persistencia nativa, rendimiento físico ni aceptación de la superficie del hombro. [Contrato, hallazgos y siguiente paso](LONGARM-CONTACT.md).

## Cambio entre armas cortas de 0.20.11

La suite `sight` pasa de 26 a 32 checks, conservando todos los anteriores y
agregando dos cambios por teclas reales de pistola ↔ revólver. Las secuencias
registran el inicio y 60 pasos, con nueve PNG por caso. Se comprueban palmas,
convergencia, selección y munición. [Contrato y límites](SIDEARM-HANDOFF.md).
El conteo esperado no equivale a ejecución aprobada: consultar el PR y sus
manifiestos propios. Las suites HTTP y los demás shards no se sustituyen.

## Salida de recarga de armas cortas · candidata 0.20.12

[SIDEARM-RELOAD-HANDOFF](SIDEARM-RELOAD-HANDOFF.md) conserva el contrato. Sight
pasa de 32 a 40 checks con dos cambios desde recarga, sin retirar los anteriores.
`reloadSwitchCases` incluye pieza, multiplicidad de modelo, targets y munición.
CI usa shards handoff/sight/graphics sin duplicados, fail-fast desactivado y
artefactos distintos. Presupuestos por suite: 1200/1800/900 s; cada job conserva
40 minutos. HTTP y permisos de lectura permanecen iguales. Los contratos
`ci_workflow.test.py` ejecutan la selección Bash normal/completa. Estas cifras
describen requisitos, no aprobación anticipada del nuevo HEAD.

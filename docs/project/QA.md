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

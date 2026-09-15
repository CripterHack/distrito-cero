# QA, CI y reproducción

## Dos niveles de evidencia

`qa/v019/` contiene los resultados que acompañaron al paquete original. Son archivos históricos y no deben sobrescribirse para simular una ejecución nueva. El workflow de CI prepara una copia aislada del checkout, elimina sus resultados antiguos de v0.19 y publica sólo los generados por el run actual.

La base documenta 328 tests Node, 271 aserciones de navegador y una prueba del kit GLB. Una comprobación de navegador no equivale a una sesión independiente ni a cobertura exhaustiva. Las cifras actuales se leen del run y del hash concreto.

## Puerta básica

```sh
python3 build.py
node --test tests/*.test.cjs
python3 tools/export_contact.py
python3 tests/contact_exports.test.py
git diff --exit-code -- index.html assets/dc019-equipment.glb
```

En una feature que cambia esos artefactos, regenerarlos y revisar sus diferencias antes de versionarlos. La CI comprueba después que el checkout ya contiene la salida correcta. No se deben versionar logs de otra máquina como si fueran resultado de la CI.

## Integración de navegador de la base

| Script actual | Resultado esperado de la base | Informe |
| :--- | :--- | :--- |
| `tests/contact_browser.py` | 51 aserciones | `handling-browser.json` |
| `tests/contact_arsenal.py` | 78 aserciones | `arsenal-browser.json` |
| `tests/contact_library.py` | 64 aserciones | `library-regression.json` |
| `tests/contact_legacy.py` | 52 aserciones | `legacy/browser-report.json` |
| `tests/contact_continuous.py` | 26 aserciones | `arsenal-continuous.json` |

Todos escriben bajo `qa/v019/`. La suite de manejo usa fotogramas WebGL reales y pasos controlados, con almacenamiento en memoria. La continua conserva el bucle original y sus inputs, pero también prepara posiciones iniciales. Ninguna demuestra persistencia nativa tras cerrar el navegador.

El CI inicial ejecuta manejo en cada PR/push y permite la batería completa por ejecución manual. Utiliza Python 3.12, Node 22 y Playwright 1.57.0 con su Chromium instalado. La ruta `/usr/bin/chromium` se adapta en el runner de CI porque las pruebas heredadas la fijan en código. El nuevo harness de la spec 001 debe eliminar esa restricción sin reescribir todas las aserciones.

Reproducción local en una copia de trabajo de QA, con Chromium compatible y Xvfb:

```sh
python3 -m pip install playwright==1.57.0
python3 -m playwright install --with-deps chromium
# Configurar /usr/bin/chromium para este entorno de desarrollo o usar el futuro harness.
xvfb-run -a python3 tests/contact_browser.py
```

No reemplazar el navegador personal del usuario ni elevar privilegios fuera de un runner administrado. Instalar dependencias es sólo para desarrollar, no para jugar. La documentación de [Playwright](https://playwright.dev/python/docs/browsers) explica la correspondencia entre la versión de la herramienta y sus binarios.

## Por qué no usar todos los scripts históricos como gate

`tools/audit_contact_release.py` deduce un commit base de la raíz del historial Git temporal de autoría. La raíz de este repositorio nuevo sólo tiene el importador. Por ello ese cálculo ya no representa la base de comparación. Sus informes originales siguen siendo válidos para su entrega, pero el script no es un auditor universal del repositorio publicado.

`tools/run_contact_browser.py` fija DISPLAY=:99 y escribe resultados históricos. La CI inicial no depende de él: usa procesos explícitos con estado de salida, verifica los informes nuevos y sus hashes. Los antiguos tests de cuello pueden exigir dimensiones deliberadamente cambiadas después. Seleccionar invariantes vigentes y registrar sustituciones, no borrar tests incómodos ni sumar pases incompatibles.

## Puertas nuevas por construir

1. Harness configurable con directorio de artefactos único, timeout, entorno y rechazo de informes obsoletos.
2. HTTP local real con perfil persistente: crear dos partidas, cerrar/reabrir, comprobar identidad y progreso, eliminar una sin que reaparezca.
3. Dos pestañas reales: rechazar revisión obsoleta y guardar copia sin perder la más reciente.
4. Pérdida/restauración de contexto y mensajes de recuperación, sin reinicio silencioso de la partida.
5. Sesión de 30 minutos con recambio de sectores y límites de recursos.
6. Matriz física de navegadores y dispositivos, comparaciones de personajes y playtest completo.

## Informes mínimos

Commit y SHA-256 de HTML, fecha UTC real, comandos y códigos, versión de navegador, renderer/GPU reportado, resolución y calidad, semilla, almacenamiento nativo/fixture, estado preparado/recorrido y fallos. No registrar tokens, rutas personales sensibles o partidas de usuarios.

Las fallas de infraestructura se clasifican y reintentan sólo después de inspeccionar la causa. No ocultar un CONTEXT_LOST_WEBGL con múltiples reintentos hasta lograr un verde. Mantener el primer fallo y el alcance de la recuperación.

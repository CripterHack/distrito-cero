# Capacidad del productor sight: diagnóstico, no FPS

`tests/sidearm_sight_browser.py` conserva el mismo catálogo, particiones,
resolución, imágenes y criterios. Añade `timing` al informe y líneas
`SIGHT_TIMING` al log. Sus secciones separan preparación, acciones base,
instalación de observadores, cada intercambio y guardas finales.

Cada sección contiene duración host en segundos y operaciones (`evaluate`,
`screenshot`, teclas y operaciones de preparación), con llamadas, fallos y máximo.
`browser` contiene milisegundos de render con `gl.finish`, inspección ocular y
culata. **Están dentro de los tiempos host, no se suman entre sí como coste total.**
El render temporizado incluye trabajo CPU/espera y no es una consulta GPU.
El informe identifica navegador, Python, sistema y CPU lógica visible.

Los temporizadores sólo ejecutan la llamada original una vez y relanzan la misma
excepción. No reintentan, filtran fallos ni deciden aceptación. Las líneas de
inicio permiten identificar la sección interrumpida; un productor matado no
dispone de un informe final válido. Los resúmenes de secciones terminadas no
sustituyen los 112 checks completos ni las cinco guardas estrictas.

Pruebas: `python3 tests/qa_reporting.test.py` y
`node --test tests/qa-timing.test.cjs`. Los relojes controlados de estas regresiones
prueban contabilidad/transparencia, no rendimiento del juego. Los helpers
`tools/qa/sight_timing.py` y `.js` nunca se incorporan al HTML autónomo.
[Plan y restricciones](../../specs/001-reliability/plan-sight-capacity.md).

Antes de ampliar cobertura, analizar una partición completa y comparable. No
interpretar un dato parcial, otro navegador o diferente carga de host como una
aceleración demostrada. Los límites siguen en 1800 s/productor y 40 minutos/job.

## Interpretación y límites

La CPU lógica visible (`logicalCpus`) no informa de la cuota efectiva del contenedor.
Comparar el mismo navegador, host y carga antes de atribuir cambios de rendimiento.
Las primeras medidas locales utilizaron Chromium 144 del sistema y tuvieron
sondas concurrentes, por lo que no constituyen una comparación controlada.
La instalación del navegador fijado por Playwright no terminó por un error DNS.

Se evaluó evitar las escrituras de estilos de caret durante capturas con UI oculta.
Los píxeles coincidieron en sondas alternadas, pero las muestras cálidas y las
realizadas tras dibujar no establecieron una aceleración controlada. **No se
cambiaron las opciones de captura.** La instrumentación no resuelve por sí sola
el pequeño margen de timeout observado en #57. Los informes completos de CI
son la siguiente base para decidir una optimización o redistribución.

El campo `timing` no sustituye `checks`, `guards`, identidad de HTML o modo de
aceptación. `completed` significa que una sección terminó, no que un juego o un
issue fue aceptado. Consultar [QA](QA.md), [HANDOFF](HANDOFF.md) y el cierre del PR
para los resultados reales de cada ejecución.


## Continuación 0.20.20: shader de materiales básicos

#58 ya está integrado y su push verificado. En la investigación posterior se
midió la espera de la cola gráfica mediante readback de diagnóstico. Un perfil
por malla señaló las cajas de la ciudad como coste principal, no la inspección
ocular o el cálculo de poses. Ni quitar la guarda GL ni rebajar la escena es
una corrección aceptable.

Las sondas de corte de luces, orden de chunks, shader de vértices rígidos y
eliminación de descartes no justificaron integrar esos cambios. La variante de
fragmentos para materiales básicos sí mostró un ahorro local con píxeles iguales.
[Plan y límites de la candidata](../../specs/001-reliability/plan-static-material-program.md).

Sólo se selecciona para lotes estáticos no deformados que registran prueba
explícita de IDs enteros 0–25 al subir los datos. La función GLSL detailMaterial
conserva las comparaciones originales en el programa general y retorna false
en la variante, excluyendo ramas 30–49 imposibles en el lote. No se cambia ninguna
fórmula o descarte alcanzable por materiales 0–25. Lotes no probados, dinámicos,
deformados o mixtos mantienen el programa original. Las sombras no se especializan.
Los uniforms se suben a ambos programas de escena, incluidos los de reflexión,
sin getUniform ni copias del driver en producción. Un programa GPU adicional,
registrado y liberado por el ledger existente, es el coste permanente explícito.

Regresión: `node --test tests/basic-material-program.test.cjs`.
Las sondas alternan ambas rutas reales sobre el mismo navegador/host y separan
calentamiento. Registran número de dibujos/instancias/vértices, paleta, montaje,
simulación, captura y tiempo host total. Sus muestras no sustituyen los tres
productores completos, la identidad del HTML ni la revisión de imágenes/CI.
No anunciar capacidad estable a partir de una sola escena ni extender cobertura
a ciegas. Consultar el PR de #6 para resultados actuales y verificables.

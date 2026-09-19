# Plan #25 · Cancelación y recargas con navegador HTTP

**Objetivo:** completar la comprobación de CONTACT-04/05 que la matriz Node de #23 no puede demostrar: reloj RAF vivo, pausa real, retorno del selector y handlers de entrada de producción.

**Especificación:** [SPEC-003](spec.md), [matriz Node](plan-reload-cancellation.md), issue #25. Base remota `61410a029c73e0f1efc91dc76a4ccaddbca5c38e`. Ejecutar secuencialmente en rama aislada con pruebas antes del cambio, revisión completa y PR.

## Decisión y restricciones

Añadir una suite HTTP al runner existente, no otro motor ni un sistema de entrada alternativo. Preparar escenas y siete temporizadores mientras el juego está pausado. Abrir/cerrar menús y reanudar con Playwright. Mantener RAF, `App.loop`, simulación, renderer y Web Storage de producción durante la observación. Los observadores de dibujo y eventos sólo registran y delegan al original.

Representantes: rifle (cargador), revólver (cilindro) y escopeta (puerto). Checkpoints `0, .14, .30, .52, .72, .90, .999`. La última fracción exige que ni el menú ni una captura avancen anticipadamente la munición. La matriz Node sigue siendo la cobertura lógica de los diez equipos.

No cambiar `src/`, versión, bundle, assets, duración, munición, guardados, licencia, permisos o publicación. No controlar manualmente frames ni sustituir `setMode`, `input`, `sim.step`, `localStorage` o `requestAnimationFrame`. Los escenarios preparados no son una partida íntegra ni una medición física.

## Tarea 1 · Contrato y controles negativos

Archivos: `tools/qa/reload_contract.py`, `tests/reload_contract.test.py`, `tests/qa_selection.test.py`, `tools/qa/run.py`.

Escribir pruebas que exijan una nueva suite `reload` de origen HTTP y rechacen etiquetarla como fixture. Observar el fallo antes de registrarla. Separar validadores `pause_errors(before, after)` y `completion_errors(before, after, capacity, selected=None)` del arranque de Playwright para probar errores de reloj, inputs, munición, duplicación visual y finalización.

Los snapshots contienen tiempo de simulación, contador real de frames, equipo, temporizador/ID de recarga, munición de todo el catálogo, disparos, carga, inputs, contador observado de finalización, piezas renderizadas y error GL. Un frame counter que no avanza invalida una supuesta prueba de pausa.

Comandos: `python3 tests/reload_contract.test.py` y `python3 tests/qa_selection.test.py`. Los controles deben fallar con el contrato ausente y pasar al implementar el validador, sin relajar sus criterios.

## Tarea 2 · Escenas del navegador

Archivo: `tests/reload_browser.py`.

Arrancar una página HTTP local aislada, crear una partida sintética desde la UI, observar errores/peticiones y verificar hash y Web Storage nativo. Ejecutar 21 checkpoints desde pausa, tres entradas al selector desde una recarga iniciada por teclado, dos cambios de equipo y una cancelación Gauss. Registrar cada snapshot y conservar capturas.

Cada checkpoint abre el selector desde pausa, verifica que tiempo/recarga/munición/piezas no cambian mientras avanzan frames, cierra a pausa y finalmente reanuda hasta completar exactamente una transferencia. Los casos desde juego prueban entrada retenida, suelta y entrada nueva. Los cambios usan tarjetas y confirmación reales y verifican que no reaparece la acción cancelada.

Observar los primeros fallos del harness sin modificar el runtime para acomodarlos. Un defecto de producto exige reproducción propia y una unidad de comportamiento explícita.

## Tarea 3 · Integración y revisión

Archivos: `.github/workflows/ci.yml`, `docs/project/QA.md`, `docs/project/STATE.md`, `docs/project/HANDOFF.md` y este plan.

Incluir la nueva suite en el trabajo HTTP existente y los tests del contrato en core. No cambiar permisos ni retirar suites. Corregir las referencias documentales de #21/#23 usando los resultados reales de #22/#24.

Ejecutar pruebas Node completas, tests Python vigentes de build/exportación/runner, `build.py --check` y navegador afectado. Revisar diff, ausencia de cambios de producción y enlaces. Exigir CI del HEAD exacto antes del merge autorizado, luego consultar los runs del push de master. Registrar evidencias y límites en #25 y el PR sin hashes autorreferenciales.

## Revisión prioritaria

Rechazar prueba verde por bucle detenido, reloj/munición adelantados durante pausa, renderizado obsoleto, pieza duplicada, falsa entrada nueva tras reanudar o modo de almacenamiento mal etiquetado. Comprobar también reserva insuficiente y temporizador a punto de finalizar.

## Reversión

Revertir únicamente el PR de esta unidad. El HTML y las partidas permanecen idénticos.

## Estado y evidencia

Implementación añadida, pendiente de verificar en navegador autorizado y CI del HEAD exacto. Doce tests del validador y once de selección pasan tras observar sus fallos iniciales. El primer intento HTTP local fue bloqueado con `ERR_BLOCKED_BY_ADMINISTRATOR`, sin reemplazarlo por un fixture. Base local comprobada: build idéntico y 471 tests Node aprobados. Copia de ejecución obtenida del artefacto Pages de `61410a0`, no un clon Git remoto. Los commits locales del snapshot no se publican. La integración usa una rama remota creada desde el SHA canónico.

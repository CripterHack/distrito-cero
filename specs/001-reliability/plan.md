# Plan de implementación · SPEC-001

Estado: preparado, ejecución posterior a la publicación. Goal: convertir QA en una herramienta portable y verificar datos nativos y recuperación sin reemplazar el juego. Stack: Python/Playwright sólo en desarrollo, JS/WebGL2 nativos en runtime.

## Estructura propuesta

| Archivo | Responsabilidad |
| :--- | :--- |
| `tools/qa/config.py` (nuevo) | Config validada: raíz, navegador, origen, salida, modo y timeout |
| `tools/qa/run.py` (nuevo) | Ejecución, códigos, freshness, hash y manifiesto |
| `tests/qa_runner.test.py` (nuevo) | Runner acepta/falla con procesos controlados y reportes viejos |
| `tests/native_saves.py` (nuevo) | Origen HTTP + perfil persistente + dos páginas |
| `tests/context_recovery.py` (nuevo) | Pérdida/restauración de contexto de producción |
| `src/graphics-lifecycle.js` (propuesto) | Ciclo explícito de recursos, sin propiedad de partida |
| `src/renderer.js` y capas | Crear/destruir/reconstruir recursos de cada nivel |
| `src/app.js` o adaptación acotada | Pausa de dibujo e interfaz de recuperación |
| `.github/workflows/ci.yml` | Pasar configuración y publicar evidencia fresca |

Antes de crear `graphics-lifecycle.js`, inventariar constructores y callbacks reales. Si una interfaz más pequeña resuelve el problema, documentar la decisión. No introducirla sólo por el nombre de este plan.

## Unidad A · Runner y manifiesto

Escribir un test con una suite que devuelve código no cero y un JSON viejo aprobado. El resultado debe fallar. Añadir test de timeout, salida ausente, HTML cambiado y directorio ajeno rechazado. Implementar el runner mínimo, con identificador de run y timestamps en UTC, y probarlo sin Chromium.

Consumir un listado explícito `Suite(name, command, report, expected_checks)` y producir un manifiesto con exit code, hash y estado por suite. La selección no toma todos los `.py` históricos. Una excepción no debe imprimir éxito en el resumen.

Portar primero `contact_browser.py`, conservando sus aserciones. Comparar sus 51 checks en el harness nuevo. Las cifras exactas cambian sólo al agregar/retirar requisitos documentados, no para aceptar un pase incompleto.

## Unidad B · Origen y almacenamiento nativos

Levantar HTTP ligado a localhost en puerto dinámico y un perfil temporal exclusivo. No interceptar ni reemplazar Web Storage. Probar crear/cerrar/reabrir, dos slots e importar copia. Añadir dos páginas concurrentes y una escritura obsoleta. Al finalizar, borrar únicamente el perfil temporal del test.

El usuario no debe aportar sus partidas ni credenciales. Un bloqueo del entorno se registra como skipped/blocked con causa, nunca como éxito. Mantener regresiones de quota/corrupción por fixture como evidencia distinta.

## Unidad C · Lifecycle gráfico

Inventariar VAOs, buffers, texturas de piel/poses/apariencia, framebuffers, sombras/reflejos y geometría por sectores. Proponer contrato idempotente de dispose/restore. Escribir caso fallido de pérdida de contexto antes de modificar renderer.

Al perder contexto, cancelar únicamente la programación gráfica y acciones que podrían dispararse al recuperar foco. No destruir la simulación ni guardar un mundo reiniciado. Restaurar con el mismo estado y volver a subir recursos de manera acotada. Mostrar progreso o error legible, con opción de conservar la partida.

## Unidad D · Recursos y regresión

Abrir/cerrar creador y selector repetidamente, recorrer nuevos sectores y volver. Medir contadores de recursos y heap disponible después del calentamiento. Distinguir crecimiento inicial de caché frente a fuga sostenida. Validar campaña, inventario, acceso a coche y transición de regiones con el bucle original.

## Cierre y reversión

Cada unidad es un PR separado. El runner no cambia gameplay. El lifecycle necesita una activación reversible mientras se valida. Revertir los commits no debe exigir convertir las partidas. Actualizar QA, STATE y HANDOFF con los runs efectivos. No reescribir la evidencia original.

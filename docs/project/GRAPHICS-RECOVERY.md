# Recuperación gráfica · issue #4

## Implementación

La app mantiene una sola cadena de requestAnimationFrame mediante `scheduleFrame` / `stopFrame`. Al perder WebGL, cancela la programación y las entradas activas, pausa audio/simulación y muestra un diálogo DOM que no depende de GPU. No reconstruye `Simulation`, `SaveStore`, los controles ni la instancia de App.

`GLResources` registra buffers, texturas, framebuffers, renderbuffers, VAOs, programas y shaders por generación de renderer. Borra cada handle vivo una vez, incluidos recursos compartidos, o abandona los handles inválidos de un contexto perdido. Un renderer descartado no puede seguir subiendo mapas cuando termina una imagen asíncrona.

La restauración construye la cadena completa `D.Renderer` sobre el mismo canvas, con el mundo/cámara/modo visual conservados. Espera los tres mapas de piel y comprueba un dibujo. Sólo publica la nueva generación si esa comprobación pasa. El usuario debe pulsar Reanudar para volver: no se reactiva el gatillo ni una carga Gauss. El tiempo transcurrido durante el fallo no se transforma en pasos de simulación acumulados.

El creador conserva su objeto de borrador, sus campos y su snapshot del mundo real. El selector de armas conserva selección pendiente, cámara y postura pausada. El catálogo anterior no se sobrescribe durante la recuperación. Exportar sesión produce un JSON estándar importable desde Mis partidas. Exportar borrador produce un JSON de valores de apariencia para recuperación **manual**, no un nuevo formato de importación automática.

## Fallos y límites

La reconstrucción automática sucede una vez por evento de restauración del navegador. Un fallo deja una opción de reintento explícita, hasta tres intentos por incidente, y exportación. No recarga la página ni reinicia silenciosamente. Si el navegador no permite restaurar el contexto, la exportación sigue siendo la vía segura. Un fallo inicial por ausencia de WebGL conserva el manejo de error de arranque anterior.

La reconstrucción es síncrona para geometría y puede causar una pausa visible. No garantiza sobrevivir al cierre de la pestaña o del proceso del navegador, ni repara todos los errores del driver. Los cambios no añaden nube, no modifican el formato del catálogo ni equivalen a un benchmark de rendimiento.

## Pruebas

`tests/graphics-recovery.test.cjs` verifica el ledger, idempotencia, fallo de construcción, pérdida durante una reconstrucción y presupuesto de reintentos. `tests/graphics_recovery.py` usa eventos reales de `WEBGL_lose_context`, el renderer real y la cadena RAF del juego. Revisa exportación durante pérdida, conservación de identidad/inventario, restauración repetida, selector, borrador, ancho móvil, fallo inyectado y reintento. Su almacenamiento es un fixture explícito; el caso nativo separado de #3 vuelve a ejecutarse en CI.

El primer test de exportación descubrió que el bloqueo de entradas del diálogo también bloqueaba el enlace de descarga creado fuera del diálogo. Se añadió un contenedor opcional a `download` y el enlace se crea dentro del diálogo. Una prueba posterior devolvía una función desde `page.evaluate`, que Playwright ejecutaba involuntariamente; se corrigió la prueba para no devolver esa asignación, sin alterar el juego.

Ejecutar mediante el runner portable: `python3 -m tools.qa.run --suite recovery --headed`. Los artefactos nuevos se guardan fuera de evidencia histórica y contienen hash del HTML, checks y capturas. La CI requiere manejo, recuperación, Node, exportación y persistencia nativa antes de integrar. Las capturas muestran el motor, no imágenes generadas.

## Reversión

Revertir el commit de integración y reconstruir `index.html`. No se requiere migración de partidas. `src/graphics-resources.js` se carga antes del renderer y `src/graphics-recovery.js` después de todas las capas de App. No cambiar ese orden.

Referencias: eventos `webglcontextlost` / `webglcontextrestored` y extensión `WEBGL_lose_context`, documentación de MDN y especificación WebGL. El test provoca una pérdida controlada, no demuestra la causa de un fallo espontáneo de un driver concreto.

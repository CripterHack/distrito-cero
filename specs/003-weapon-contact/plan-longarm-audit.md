# #27 · Auditoría cooperativa de armas largas

**Objetivo:** convertir el diagnóstico aislado de #6 en un auditor ejecutable sobre la paleta realmente dibujada, con evidencia comparable para CONTACT-03.

**Base:** `fecf117385941dabd4e22f13c04d45d4032fb042`, producto 0.20.1. [SPEC-003](spec.md). Trabajo secuencial y revisión propia, sin atribuir revisión independiente. Ejecutar con el flujo de `superpowers:executing-plans`.

## Diseño y límites

El auditor es código de desarrollo en `tools/qa/`, nunca se incorpora al HTML. Consume la geometría de cuatro familias (`smg`, `rifle`, `shotgun`, `sniper`), el montaje y la paleta del renderer. Reutiliza la referencia del ojo extraída de la malla por el helper vigente. Comprueba las referencias de cada mira contra sus vértices reales y distingue el tubo óptico del sniper de las miras abiertas.

Mide separación perpendicular ojo/eje, posición anterior de la mira, culata contra referencia articulada heredada del hombro, palmas contra anclas y longitud entre articulaciones de matrices diferentes. No interpreta una matriz de rotación rígida de un único hueso como prueba de que no existe estiramiento entre huesos.

Los criterios numéricos son un **cribado diagnóstico**, no aceptación artística. La suite puede aprobar la integridad de medición mientras el informe registra `needs-coordination`. No fijar como requisito que el juego siga defectuoso. No desplazar el objeto al ojo en producción sólo para mejorar una métrica si se separa la culata.

Se conservan runtime, rig, mallas, tiempos, inventario, datos, versión y publicación. El hombro medido es una referencia del rig, no toda la superficie de la prenda. No certifica autocolisión o FPS. Tiempo y cámara preparados, Storage fixture, no persistencia HTTP.

## Tarea 1 · Observador y controles negativos

Archivos: `tools/qa/longarm_contact.js`, `tests/longarm-contact.test.cjs`.

- [x] Escribir el contrato ausente y observar RED.
- [x] Implementar `landmarks`, `inspect`, `screen` y `translateToEye` como lecturas puras.
- [x] Probar cuatro familias, matriz de 72 poses, equivariancia, no mutación, ausencia de referencias y paletas inválidas.
- [x] Probar estiramiento entre articulaciones y la falsa solución de trasladar el objeto al ojo sin conservar la culata.

## Tarea 2 · Renderer y evidencia

Archivos: `tests/longarm_contact_browser.py`, `tools/qa/run.py`, `tests/qa_selection.test.py`, `.github/workflows/ci.yml`.

- [x] Registrar `longarms` como fixture, nunca HTTP, con contrato exacto de checks.
- [x] Capturar cuatro poses por familia y una cámara frontal neutral por familia.
- [x] Observar montaje y paleta tras el dibujo del personaje, mantener evidencia de frames y errores GL.
- [x] Separar resultados de integridad del auditor y resultados de cribado CONTACT-03.
- [x] Conservar JSON y galería local con los parámetros de reproducción, sin solicitudes externas.

## Tarea 3 · Integración y continuidad

Archivos: `docs/project/STATE.md`, `HANDOFF.md`, `QA.md`, `LONGARM-CONTACT.md` y este plan.

- [x] Registrar el cierre real de #25/#26 y CI posterior de master, conservando el timeout histórico.
- [ ] Ejecutar build inmutable, Node completo, tests Python vigentes y suites gráficas afectadas.
- [ ] Revisar capturas y diff. Publicar commits pequeños y PR con referencia al SHA revisado.
- [ ] No integrar sin CI aprobada. Mantener #6 abierta y documentar el siguiente cambio de pose, no otra matriz redundante.

## Reversión

Revertir el PR de auditoría. No hay migración de partidas ni cambios de comportamiento.

## Entorno de ejecución

Clon por Git no disponible por resolución DNS del laboratorio. Copia obtenida del artefacto Pages `10579658107` del commit canónico, ZIP SHA-256 `18cc18b2b11894f3f23dbe2e75dc6251379f67a1bcfcdf702843755659c28b7e`. La historia local es un snapshot de ejecución y no se publica. Base local: 471/471 Node y `build.py --check` aprobados. La primera ejecución headed produjo 24/24 checks y 48 capturas. La revisión del auditor suma trece tests Node, incluidos contactos no finitos. Los resultados finales de repetición/CI e integración se registran en el PR de #27. Se conserva el primer fallo headless por WebGL2 no disponible.


## Decisiones de ejecución

Se preservó el caso headless fallido y se usó headed/Xvfb, configuración ya presente en CI. No se modificó el runtime para acomodar el laboratorio. La galería escapa etiquetas y restringe rutas de imágenes locales. Un test de revisión reprodujo la falta de rechazo de contactos no finitos y aprobó tras añadir el guard. No se incluyó una falsa corrección de traslación ocular: el contrafactual mantiene explícito que rompe la referencia de culata. No se dispone de un revisor independiente, la revisión es propia.

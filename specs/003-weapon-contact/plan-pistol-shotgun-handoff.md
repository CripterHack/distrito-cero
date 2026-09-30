# Pistola ↔ escopeta: plan de implementación

> Ejecutar con superpowers:executing-plans y test-driven-development. Revisión propia.

**Goal:** conservar la pose y pieza mostradas al intercambiar pistola/escopeta, libre o desde recarga, sin retrasar acciones.
**Architecture:** ampliar sólo captureSwitch para la pareja medida. Reutilizar la captura, retorno cosmético y caché canónica. Rechazar un tercer modelo mostrado. Extender los bucles de regresión y el productor único de sight.
**Tech Stack:** JavaScript/WebGL2 nativos. Node/Python/Playwright para QA.
**Spec:** [SPEC-003](spec.md), CONTACT-04/05, issue #6.

## Base y restricciones

Base remota #59 bb2412283e55d77d92dadc703d62ea89c69709c2, árbol ffc69b9b88c7b76d10ea335ad3454a0808c7e62a, producto 0.20.20. Su CI posterior aprobó los siete jobs. Se restauraron 958 archivos y el árbol exacto, con historia local sintética que nunca se publica como ascendencia remota. No repetir #58 ni #59.

Conservar gameplay, munición, partidas, geometría, rig de 49 huesos, longitudes y memoria de pies. Inicio de palmas/paleta <1e-5, paso preparado <30 mm, alcance <12 mm, penetración muestreada máxima 2 mm. Retorno de 0.90 s, no enfundado mecánico certificado. No otro solver, tracker o reloj. No reintentar limpieza bloqueada ni borrar ramas.

## Foco de revisión

Selector congelado después de cancelar inputs. Reversión antes/después del reemplazo. Tercer modelo visible. Actor en movimiento. Caché fría/inicializada. Disparo/recarga y restore inmediatos. La escopeta usa su propio perfil y geometría, no una etiqueta de rifle.

## Tarea 1: comportamiento y regresiones

Archivos: src/weapon-handling.js, tests/cross-family-handoff.test.cjs, tests/finger-cache-order.test.cjs y exclusiones de tests/sidearm-handoff.test.cjs si corresponde.
Interfaz: captureSwitch(sim,next,actorOverride,shown), sin cambio de firma.

- [x] Extender bucles a dos direcciones, ocho estados y cuatro configuraciones. Añadir congelación, retorno y tercero mostrado. Ejecutar RED sobre la base sin modificar runtime.
- [x] Habilitar la pareja con captura y rechazo conservador. Medir trayectoria y separación con la cohorte fija y geometría de escopeta. No aumentar umbrales.
- [x] GREEN dirigido 34/34. Caché fría/inicializada incluida en la suite completa Node 658/658, sin skips ni cancelaciones. Fallos intermedios conservados.

## Tarea 2: renderer, entrega y continuidad

Archivos: tools/qa/sight_contract.py, tests/sidearm_sight_browser.py, tests/qa_selection.test.py, versión/build y documentación vigente.
El productor conservará el mismo renderer, escenas, resolución 820×680, 61 estados, capturas y cinco guardas por partición.

- [x] RED de catálogo y cobertura de escopeta antes de implementar las cuatro secuencias nuevas. Conservar los veinte casos previos en su orden.
- [x] Distribución prevista: dos libres en base, una recarga por otra partición. 130 checks =56+36+38, sujeto a ejecución. Sin nuevos runners ni elevar 1800 s/productor y 40 minutos/job.
- [ ] Revisar imágenes reales y las mediciones de estados/partes/culata. Comparar los veinte casos anteriores sin ocultar diferencias.
- [ ] Actualizar producto 0.20.21, build, STATE/HANDOFF/QA y guía. Ejecutar contratos vigentes y build reproducible.
- [ ] Publicar PR con padre remoto real, comprobar CI completa e imágenes del HEAD antes del merge. Verificar push por separado y actualizar cierre.

## Reversión y límites

Revertir esta unidad junto con versión/build no migra ni elimina partidas. Las fuentes/manifiestos históricos no se alteran. No atribuir toda la malla/CCD, FPS, GPU física ni aprobación artística. #5/#6/#7 mantienen sus requisitos globales.

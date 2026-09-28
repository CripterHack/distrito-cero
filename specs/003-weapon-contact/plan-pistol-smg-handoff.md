# Pistola ↔ SMG: plan de implementación

> Ejecutar con superpowers:executing-plans, TDD y revisión propia.

**Goal:** conservar la pose y pieza mostradas al intercambiar pistola/SMG, libre o desde recarga, sin retrasar acciones.
**Architecture:** ampliar únicamente las rutas medidas de captureSwitch, con rechazo de terceros modelos. Reutilizar montaje, captura, retorno y caché canónica existentes. Ampliar los tests y catálogo único de sight, sin otro productor.
**Tech Stack:** JavaScript/WebGL2 nativos. Node/Python/Playwright sólo para QA.
**Spec:** [SPEC-003](spec.md), CONTACT-04/05, issue #6. Base remota 5ab52d79c517bee5d54e6aa286f94dae044e84f4, árbol 6391e911af488970f71f3f2313081bf38411658f.

## Restricciones globales

HTML autónomo y rig de49 huesos. Gameplay, munición, físicas, geometría y partidas intactos. Retorno cosmético de 0.90 s. No otro solver, tracker, reloj o caché. Inicio de palmas/paleta <1e-5, paso preparado <30 mm, alcance <12 mm, penetración muestreada máxima 2 mm. Disparo y nueva recarga inmediatos. Conservar validación estricta de#56,94 checks previos y cinco guardas por partición. Presupuestos de 1800 s por productor y 40 minutos por job sin nuevos runners. No reintentar limpieza bloqueada.

## Foco de revisión

Selector congelado tras cancelar inputs. Reversión antes/después del reemplazo de modelo. Pieza retornando y tercer objeto mostrado. Actor moviéndose y memoria de pies. Caché fría/inicializada, acciones prioritarias y partidas.

## Tarea 1: transición y regresiones

**Archivos:** src/weapon-handling.js, tests/cross-family-handoff.test.cjs, tests/finger-cache-order.test.cjs, tests/sidearm-handoff.test.cjs.
**Interfaz:** captureSwitch(sim,next,actorOverride,shown) conserva su firma y devuelve la captura cosmética existente o null para rutas excluidas.

- [x] Extender primero bucles a ocho estados y cuatro configuraciones de pistola/SMG, más congelación, retorno, tercer modelo y caché. Observar RED antes del runtime.
- [x] Habilitar sólo esta pareja y medir su arco con pruebas de piel/chaqueta. No extrapolar distancia ni elevar tolerancias para aprobar.
- [ ] Ejecutar regresiones completas del proyecto, no sólo las nuevas, y revisar diff.

## Tarea 2: renderer y entrega

**Archivos:** tools/qa/sight_contract.py, tests/qa_selection.test.py, tests/qa_runner.test.py, documentación de continuidad, version.json, build-info.json e index.html.
**Interfaz:** el productor tests/sidearm_sight_browser.py conserva sus escenas y mediciones; sólo consume nuevos casos del contrato.

- [x] Añadir prueba de catálogo conservado y cuatro secuencias nuevas. Observar RED antes de modificar el contrato.
- [x] Usar capacidad existente: dos cambios libres en base y una recarga por cada otra partición. Preservar los dieciséis casos y94 checks anteriores, sin duplicaciones. Cobertura prevista112=48+31+33, pendiente de ejecución.
- [ ] Verificar capturas reales y61 estados por caso, baseline/candidata bajo los mismos parámetros. Mantener diagnóstico separado de aceptación.
- [ ] Actualizar versión0.20.19, build y documentación. Publicar PR desde padre remoto real, revisar CI/artefactos y merge condicionado. Verificar push separadamente.

## Reversión y límites

Revertir la unidad junto con versión/build no modifica partidas. El muestreo no es toda la malla/CCD, hardware físico, FPS ni aceptación artística. La revisión propia no es independiente. #5/#6/#7 conservan sus criterios globales. El estado final y los fallos se registran en el PR.

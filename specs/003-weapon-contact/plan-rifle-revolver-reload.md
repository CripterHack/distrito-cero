# Rifle ↔ revólver desde recarga: plan de implementación

> Ejecutar con superpowers:executing-plans, regresión primero y revisión propia.

**Goal:** preservar la pose y la pieza mostradas al cambiar rifle/revólver desde recarga, sin retrasar acciones reales.
**Architecture:** ampliar captureSwitch y su montaje existente, conservando la caché canónica. Un único productor de sight se distribuye en particiones disjuntas para mantener sus límites.
**Tech Stack:** JavaScript/WebGL2 nativos, Node/Python/Playwright sólo para QA.
**Spec:** [SPEC-003](spec.md), CONTACT-04/05, issue #6. Base remota d25baffca0f22e60a001f8f7f6e81ac8877cb9eb, árbol 1fd4f64fc57536034b6bd565cdd2a2793091f219 (#52).

## Restricciones globales

Mantener HTML autónomo, rig de 49 huesos, gameplay/munición/partidas, selección y acciones prioritarias inmediatas. Sin nuevas dependencias de runtime, solver, tracker, reloj o caché. Duración cosmética 0.90 s. No retirar ramas: la limpieza de #52 fue bloqueada y queda fuera de esta unidad.

## Foco de revisión

Captura congelada después de cancelar input. Retorno de pieza y reselección rápida. Caché fría frente a equipo mostrado antes. Disparo/nueva recarga y restore durante el cambio. Modelo realmente mostrado ajeno a la pareja. Cada condición se cubre en los tests existentes extendidos, sin nueva matriz paralela.

## Tareas

- [x] Verificar los 946 archivos de la instantánea contra su manifiesto y árbol remoto, leer continuidad y pasar baseline dirigida (14/14).
- [x] Extender tests/cross-family-handoff.test.cjs a las siete fases de recarga en ambas direcciones y cuatro configuraciones. Probar captura congelada, retorno/reselección y tercera pieza. Exigir primer frame <1e-5 m y matrices <1e-5, pasos preparados <30 mm, targets <12 mm y longitudes invariantes. Observar RED.
- [x] Retirar únicamente la exclusión de recarga/pieza retornando en src/weapon-handling.js:captureSwitch. Mantener tercera pieza excluida. Repetir regresión, caché, prioridad y culata frente a piel/chaqueta (mínimo −2 mm).
- [x] Añadir las dos secuencias de recarga al catálogo único tools/qa/sight_contract.py. Conservar las seis secuencias del shard cross-family y ejecutar sólo las dos nuevas en revolver-reload, conservando alias de selección anterior, base de 40 checks, cinco guardas comunes bloqueantes y 61 estados por intercambio. Contratos en tests/qa_selection.test.py y tests/ci_workflow.test.py primero en RED. No ampliar 1800 s por productor ni 40 min por job. El presupuesto agregado de runners aumenta explícitamente.
- [ ] Actualizar 0.20.16, build, CHANGELOG y documentos vigentes. Ejecutar Node completo, Python vigente, build/autoría/exportación. Revisar escenas antes/después y fallos sin ocultarlos.
- [ ] Crear PR sobre la base remota exacta, revisar CI y artefactos. Merge sólo con gates aprobados. Verificar push y Pages separadamente. No cerrar #5/#6/#7 por conteos.

## Evidencia y reversión

El directorio local parte de una instantánea de fuentes, no del historial remoto. Los commits locales son equivalentes por árbol y se distinguen del HEAD remoto en los informes. Registrar comandos, SHA del HTML, resultados, capturas y límites. Revertir esta unidad junto con versión/build no migra ni elimina partidas. La recarga del revólver no tiene un cilindro articulado independiente: no presentar su retorno cosmético como reinserción física certificada.

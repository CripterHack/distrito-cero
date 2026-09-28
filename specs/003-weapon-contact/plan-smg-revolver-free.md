# SMG ↔ revólver libre: plan de implementación

> **For agentic workers:** ejecutar con superpowers:executing-plans, TDD y revisión propia del diff completo.

**Goal:** conservar la pose visible en el cambio libre SMG/revólver sin retrasar selección, disparo o nueva recarga.
**Architecture:** habilitar únicamente la pareja medida en captureSwitch y reutilizar montaje, retorno y caché canónica. Extender los bucles y el productor gráfico existentes.
**Tech Stack:** JavaScript/WebGL2 nativos. Node, Python y Playwright sólo para QA.
**Spec:** [SPEC-003](spec.md), CONTACT-04/05, issue #6. Base remota 6ba8b86c6e18b160588caf75ecdb24c7e64f078f, árbol 7b099a58a4aab912cbe70d55f07907e9205f9d6e (#53).

## Restricciones globales

HTML autónomo, rig de 49 huesos, gameplay/munición/partidas intactos. Sin nuevas dependencias de runtime, solver, tracker, reloj o caché. Transición cosmética de 0.90 s. Mantener rechazo de recarga activa o visible y tercer objeto mostrado para esta nueva pareja. No repetir #53 ni reintentar la limpieza bloqueada.

## Foco de revisión

Selector congelado después de cancelar input. Reversión antes/después del reemplazo. Actor en movimiento y memoria de pies. Disparo/nueva recarga/restore. Inicialización fría frente a otra sesión previa. Cada condición debe tener una regresión en los archivos existentes. Comprobar la culata de SMG contra su propia geometría, no inferirla del rifle.

## Tareas

- [x] Verificar baseline del árbol #53 y registrar resultados separados de los de #52.
- [x] Extender tests/cross-family-handoff.test.cjs con ambos sentidos libres en cuatro configuraciones, selector, reversión, locomoción, prioridad, restore y exclusiones de recarga/pieza/tercer prop. Extender caché fría/inicializada sin otra matriz. Observar fallos antes de modificar runtime.
- [x] Ampliar sólo src/weapon-handling.js:captureSwitch. Medir el arco existente de 0.08 m contra face/jacket y no ampliarlo por analogía. Criterios conservados: primera palma/matriz <1e-5, pasos preparados <30 mm, objetivos <12 mm, culata >=−2 mm, longitudes invariantes.
- [x] Añadir ambos casos al catálogo único tools/qa/sight_contract.py. Conservar los 76 checks y doce secuencias existentes. Usar capacidad del job revolver-reload para los dos casos adicionales, sin crear otro job, aumentando explícitamente su contrato de 10 a 18. Mantener nombre compatible, aliases, 61 estados, imágenes y cinco guardas bloqueantes. Los ocho checks nuevos incluyen paleta completa y culata SMG. Observar RED de selección antes de cambiar el productor.
- [ ] Actualizar 0.20.17, build y continuidad. Repetir Node completo, Python vigente, build/autoría/exportación, medir productor ampliado y revisar imágenes del renderer.
- [ ] Publicar PR acotado sobre la base exacta. Merge sólo con CI/artefactos aprobados y revisión propia explícita. Verificar push/Pages separadamente. No cerrar #5/#6/#7 por esta unidad.

## Registro y reversión

La copia local tiene un commit sintético, pero su árbol completo coincide con #53. No atribuir ese commit a un checkout remoto. Registrar RED, comandos, hashes, capturas y límites en el PR. El nombre histórico sight-revolver-reload se conserva por compatibilidad y ahora agrupa sus recargas previas más la nueva pareja libre de revólver, con cobertura disjunta. No afirma menos cómputo total o FPS físicos. Revertir la unidad junto a versión/build no migra ni borra partidas.

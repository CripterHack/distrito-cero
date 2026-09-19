# Handoff · v0.20.1 / recargas nativas de navegador

Base remota de esta unidad: `61410a029c73e0f1efc91dc76a4ccaddbca5c38e`, merge del PR #24. Producto **0.20.1 · Coherencia**, prototype. Leer [STATE](STATE.md), [QA](QA.md), [SPEC-003](../../specs/003-weapon-contact/spec.md) y [plan nativo #25](../../specs/003-weapon-contact/plan-native-reload.md).

## Integraciones comprobadas

PR #22 se integró en `3629d18` y #24 en `61410a0`. #21/#23 están cerradas. La CI de master posterior a #24 [35423304841](https://github.com/CripterHack/distrito-cero/actions/runs/35423304841) y Pages [35423304003](https://github.com/CripterHack/distrito-cero/actions/runs/35423304003) terminaron aprobados. No convertir estos runs en evidencia del nuevo PR.

El HTML conserva SHA-256 `4a78bcca34cd40b2c406b0642362f30a6b71303d8a4a6ace659e0ba4afc9918d`, 8,862,957 bytes. Fuente `dfb16e65c1a64d991f2bedfbecf0892d69c8b2110e4be1403e31d7af739c4fdb`. Sin nueva versión, cambios de runtime, malla, pesos, rig, formatos, permisos o publicación. No borrar datos del sitio.

## Unidad #25

`tests/reload_browser.py` añade una suite HTTP con escenarios y temporizadores preparados, pero con RAF, simulación, UI, renderer y Storage nativos durante la observación. El contrato `reload` exige 31 checks y capturas. `tools/qa/reload_contract.py` valida pausa, finalización y cancelación. Doce tests Python contienen controles negativos; el runner impide mezclar esta suite con fixtures. La CI la incorpora al trabajo nativo sin retirar pruebas previas.

`cancelEquipment` cancela inputs y conserva una recarga. `equipWeapon` con otro ID descarta esa recarga sin transferir munición. Los siete checkpoints de las tres familias complementan, no reemplazan, las 490 combinaciones Node de #23. Los casos por teclado retienen J al atravesar el selector y exigen un nuevo input para disparar. Las piezas se cuentan en la salida real del renderer, no por llamadas inventadas a `mount`.

La ejecución local confirmó 471 Node y el build canónico. El primer intento HTTP fue bloqueado con `ERR_BLOCKED_BY_ADMINISTRATOR`; no se anuló la política ni se presentó HTML inyectado como prueba nativa. La copia local procede del artefacto Pages de master, su historia Git es un snapshot de trabajo y no se publica. La rama remota usa el SHA real.

## Puertas antes del merge

```sh
python3 tests/reload_contract.test.py
python3 tests/qa_selection.test.py
node --test tests/*.test.cjs
python3 tools/refine_thenar.py --check
python3 tools/rebind_garment.py --check
python3 build.py --check
python3 tests/release_build.test.py
python3 tests/release_checkout.test.py
python3 tools/export_contact.py
python3 tests/contact_exports.test.py
xvfb-run -a python3 -m tools.qa.run --suite reload --origin http --headed --timeout 1800
```

Exigir CI aplicable del HEAD exacto, revisar diff y capturas y conservar cualquier fallo encontrado. Registrar resultados, SHAs y artefactos en la issue #25 y su PR. No afirmar que el navegador aprobó por tener tests escritos. No relajar umbrales ni cambiar el runtime para satisfacer un fixture defectuoso. El merge está autorizado únicamente tras gates aprobados. Después consultar el push de master y distinguirlo de la CI del PR.

## Límites y continuidad

Esta suite usa una partida sintética y checkpoints preparados. No demuestra cada fotograma, entrada de hardware/Pointer Lock, persistencia tras reinicio, rendimiento de GPU física o una partida íntegra. #5/#6/#7 conservan sus gates generales.

Tras integrar #25, la siguiente unidad de #6 es reproducir un caso de coordinación culata/hombro/ojo en armas largas con el benchmark existente, manteniendo alcance, contactos y continuidad. #5 necesita aprobación artística, materiales, pelo y variantes. #7 exige escena, recorrido real y playtest. No alargar brazos, deformar cara o ampliar contenido para ocultar requisitos pendientes.


## Diagnóstico de CI de esta unidad

El primer run #26 (`35425812835`, HEAD `7bf024e`) pasó los 49 checks HTTP previos. La suite nueva completó 27/31 y alcanzó 900 s, sin una aserción fallida en los casos completados. **Resultado fallido, no apto para merge.** El nuevo límite es 1,800 s y 35 minutos para el trabajo HTTP, sin retirar o relajar pruebas. Ahora se preserva un diario separado `reload.progress.json` aunque el proceso sea terminado. Cuatro regresiones nuevas protegen esa separación. Ver [QA](QA.md) y el plan para artefacto, tiempos y límites. Exigir CI nueva del HEAD revisado, no reutilizar el primer run.

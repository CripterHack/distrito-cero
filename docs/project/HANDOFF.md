# Handoff · correctivo de Actions y lifecycle gráfico

Base de esta unidad: master `bbc26848ee0dd26a8193aa6dbfe4dfafc3a9e734`. El usuario solicitó comprobar Actions failed antes de seguir. Leer [ACTIONS-RECOVERY.md](ACTIONS-RECOVERY.md) y el [plan](../../specs/001-reliability/plan-actions-context-loss.md).

## Cambio actual

El run de master 35045749864 perdió contexto gráfico durante manejo y un render directo accedió a listas ya liberadas. Se reprodujo la misma excepción con WEBGL_lose_context. Ahora render/syncSectors rechazan generaciones inactivas antes de mutar estado. El harness de manejo usa app.stopFrame y fotogramas explícitos completos, sin sustituir RAF global ni reintentar pérdidas inesperadas. Los logs fallidos se muestran de forma acotada en Actions.

La unidad añade nueve tests Node de lifecycle, siete del helper de captura, cinco Python de diagnóstico y tres comprobaciones gráficas de recuperación. Mantener manejo en 51 y recuperación en 25. No interpretar un informe parcial con cero aserciones fallidas como una ejecución aprobada.

## Verificar integración y publicación

Leer HEAD remoto y AGENTS. Antes del merge exigir los checks del commit exacto. Después revisar también la CI del push a master y comparar el SHA-256 del HTML publicado en Pages. Los checks verdes del PR no garantizan que un runner posterior no sufra otra pérdida gráfica. Conservar cualquier fallo nuevo y su diagnóstico, sin borrarlo ni reintentar hasta ocultarlo.

```sh
python3 tools/rebind_garment.py --check
python3 build.py
node --test tests/*.test.cjs
python3 tests/qa_runner.test.py
python3 tests/qa_reporting.test.py
python3 tools/export_contact.py
python3 tests/contact_exports.test.py
python3 -m tools.qa.run --suite all --headed
python3 -m tools.qa.run --suite native --origin http --headed
```

## Continuidad del juego

Conservar mangas PR #12, codos ópticos PR #13, falanges PR #15 y oposición del pulgar PR #16. No se altera la malla humana, los 49 huesos, munición, física o formatos. #2/#3/#4 tienen sus alcances previos resueltos; esta unidad endurece #4. #5/#6/#7 conservan trabajo pendiente.

#6: contacto entre ambas manos en armas cortas y zonas mixtas palma/pulgar. El muestreo digital principal usa >=75% de influencia, no toda la superficie. Mantener las pruebas de oposición, falanges y continuidad óptica. Después revisar ojo/mira y cancelaciones por familia.

#5: revisión artística de proporciones, materiales, cabello y manos con la matriz existente. No aprobar hiperrealismo por recuentos de pruebas.

#7: escena, mundo, recorrido íntegro y playtests conservan sus requisitos. No cerrar por mover al jugador automáticamente entre objetivos. Las pruebas gráficas por software no acreditan FPS físicos; storage fixture y persistencia HTTP nativa son evidencias diferentes.

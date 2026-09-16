# Handoff · Actions verificados y apoyo entre manos

Base de esta unidad: master `e614ff98061b9454eb47680bea7875a745373f3b`. Conserva mangas PR #12, codos ópticos PR #13, falanges PR #15 y oposición PR #16. #2/#3/#4 conservan su alcance resuelto; #5/#6/#7 continúan abiertos. Pages publica master, sin cambios de configuración.

## Incidente de Actions

PR #17 ya integrado. La CI del push a master 35051259999 y el benchmark 35051260032 terminaron correctamente. El error era un render directo sobre listas de una generación WebGL ya liberada tras perder el contexto. No se conoce la causa exacta del reinicio del driver. Leer [ACTIONS-RECOVERY.md](ACTIONS-RECOVERY.md). Conservar guardas y diagnóstico, no borrar runs fallidos o relajar el gate.

## Unidad actual de #6

Leer [SIDEARM-SUPPORT.md](SIDEARM-SUPPORT.md) y el [plan](../../specs/003-weapon-contact/plan-sidearm-support.md). Se reproduce y reduce el cruce de los dedos entre ambas manos al usar pistola/revólver. La referencia incluye el gesto completo del índice dominante y continuidad de recarga. Sólo cambia `weapon-handling.js` y su HTML generado. Malla, pesos, anclas, longitudes, inventario y formatos permanecen iguales.

Nueve tests Node nuevos y suite gráfica `sidearms` de veinte checks. El helper muestrea piel real frente a envolventes digitales, no toda la superficie mixta. Las capturas son preparadas. Guardados nativos HTTP se verifican por separado.

## Verificar antes de integrar

```sh
python3 tools/rebind_garment.py --check
python3 build.py
node --test tests/*.test.cjs
python3 tests/qa_runner.test.py
python3 tests/qa_reporting.test.py
python3 tests/qa_selection.test.py
python3 tests/native_support.test.py
python3 tools/export_contact.py
python3 tests/contact_exports.test.py
python3 -m tools.qa.run --suite all
python3 -m tools.qa.run --suite native --origin http
```

Revisar el HEAD y su CI, integrar por PR y comprobar también el push a master y el HTML de Pages. No contar resultados locales de un hash como un run remoto diferente.

## Próxima unidad

#6: revisar zonas mixtas de palma/pulgar y fases intermedias de contacto/liberación, no sólo poses asentadas. Después coordinar ojo/mira sin deformar cara o brazo para forzar un pivote. Mantener las regresiones de disparo, recarga, cambio de equipo, mangas, óptica y recuperación gráfica. No declarar autocolisión completa.

#5: revisión artística del conjunto con la matriz de personajes, materiales y peinados. #7: escena, recorrido íntegro y playtests mantienen sus criterios propios. Ninguno se cierra por cifras de QA o recorridos que preparan posiciones.

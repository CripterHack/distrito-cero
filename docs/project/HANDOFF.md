# Continuación vigente · pistola ↔ SMG, candidata v0.20.19

## Base integrada y comprobada

[PR #56](https://github.com/CripterHack/distrito-cero/pull/56) está integrado en
**5ab52d79c517bee5d54e6aa286f94dae044e84f4**, árbol
**6391e911af488970f71f3f2313081bf38411658f**, juego 0.20.18.
Su push **36469943251** ya aprobó los siete jobs. Se descargaron y cotejaron
los seis artefactos: 305 WebGL, 80 HTTP, 94 comprobaciones sight y cinco guardas por partición.
Duraciones sight:1288.415 / 1468.463 / 1445.572 s. El cierre antes pendiente está
[registrado](https://github.com/CripterHack/distrito-cero/pull/56#issuecomment-5877275153).
No repetir #55 (recarga SMG/revólver), #56 (verificador), caché #51 o particiones #50.

## Unidad de este árbol

[Plan](../../specs/003-weapon-contact/plan-pistol-smg-handoff.md),
[SPEC-003](../../specs/003-weapon-contact/spec.md),CONTACT-04/05, issue #6.
Se habilita **pistola ↔ SMG**, libre y desde recarga, conservando la captura
visible antes de cancelar inputs. Incluye selector congelado y retorno.
Rechaza terceros modelos mostrados y reutiliza 0.90 s cosméticos. No cambia
acciones lógicas, munición, geometría,49 huesos, caché canónica o partidas.

RED:38 pruebas dirigidas,27 aprobadas y once fallos sobre runtime de #56. Arco inicial.08m:
37 aprobadas y un fallo, penetración−7.772 mm en chaqueta. Arco de 0.12 m:45/45 dirigidas con
pruebas de cambios cortos.256 selecciones y608 poses de culata, mínimo conjunto
−0.353 mm dentro del criterio original−2 mm. Máximos palmares nuevos28.240 y
26.550 mm por paso preparado. Es muestreo, no toda la malla o CCD.

La selección QA pasó RED por dos requisitos ausentes y después 20/20.
Sight exige **112 checks = 48 + 31 + 33**, veinte secuencias de 61 estados, manteniendo
los94 checks y dieciséis casos previos. Dos cambios libres se agregan a base
y una recarga a cada otra partición. Conservar el orden de casos anteriores,
las guardas estrictas de#56, escenas, imágenes y límites de 1800 s por productor y 40 minutos por job.
No nuevo runner ni aumento de presupuesto agregado permitido. La duración
real y el éxito de cada productor requieren su propia CI.

## Verificar antes de integrar

Consultar el PR vinculado en [issue #6](https://github.com/CripterHack/distrito-cero/issues/6)
para HEAD, CI, informes y merge reales. Esta nota registra implementación y
resultados dirigidos, **no anticipa aprobación de CI ni integración**.
La suite completa local, autoría/build/exportación y renderer real son gates
separados. Conservar intentos fallidos/incompletos y revisión propia explícita.

```sh
python3 build.py --check
node --test --test-concurrency=4 tests/*.test.cjs
python3 tests/qa_runner.test.py
python3 tests/qa_selection.test.py
python3 tests/ci_workflow.test.py
xvfb-run -a python3 -m tools.qa.run --suite sight --headed --timeout 1800
```

## Siguiente trabajo

Cerrar esta unidad con CI, revisión de imágenes y push verificados. Después
seleccionar otro cruce aún excluido, o una medición de coste por actor/LOD,
reproduciéndolo antes de cambiar runtime. No repetir pistola/SMG si su PR
ya está integrado. Herramientas/pesados, giros/anatomías y cortes prioritarios
siguen en #6. #5 conserva arte/procedencia/UV y #7 recorrido/personas/hardware.
No cerrar globales por conteos, no atribuir GPU física, FPS o aceptación AAA.

## Recuperación y límites

La base local restaura950 archivos y el árbol exacto, pero el historial local
es sintético. Los commits remotos deben usar 5ab52d79 como padre real.
Revertir esta unidad con versión/build no migra ni elimina partidas.
No reintentar la limpieza bloqueada ni borrar ramas. Ningún helper temporal
se integra al producto o a su ascendencia. No hay una prueba HTTP pública
nueva en esta unidad. Exportaciones históricas y evidencia anterior intactas.

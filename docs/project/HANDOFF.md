# Continuación vigente · caché canónica de dedos

## Base integrada, no repetir

Master de partida: `7231aa51457539d2e5345f2d98ab470ded656fc0`, PR #50,
árbol `738cedf4d6c983ef5bb13bb769aa166dca43ba97`, producto 0.20.13.
PR #49 integró rifle ↔ pistola libre/recarga. PR #50 integró la partición de
sight (40 + 18), con seis jobs aprobados tanto en PR `36307315376` como en
push `36308741157`, benchmark `36308741141` y Pages `36308740389` aprobados.
[Resultados finales de #50](https://github.com/CripterHack/distrito-cero/pull/50).
No tratar #50 como candidata ni reabrir su timeout ya resuelto. El fallo
histórico de #49 (`36304175245`) sigue siendo un fallo, no una suite aprobada.

## Unidad actual: candidata 0.20.14

[Plan](../../specs/003-weapon-contact/plan-finger-cache-order.md), SPEC-003.
La superficie del cargador anterior contaminaba el primer ajuste canónico de
la nueva arma. `mount` ahora conserva por separado el punto de autoría para
`fitFingers` y la superficie/pivote/transform mostrados. No modifica el solver,
las cuatro claves de caché, gameplay, huesos, geometría o partidas.
[Diagnóstico previo](https://github.com/CripterHack/distrito-cero/issues/6#issuecomment-5854636173).

Cuatro tests nuevos usan procesos independientes con caché fría/inicializada,
ambas direcciones rifle/pistola, libre/recarga y configuración neutral/agachada.
Exigen igualdad exacta de ajustes y muestras de matrices, palmas, piezas y
estado, además del primer frame, lecturas no mutantes y cuatro entradas.
Fallaron en la base antes del ajuste. No se precalienta el runtime ni el QA
normal para ocultar el caso, ni se añade una API de reset al juego.

**Estado al escribir este commit:** código y regresión local implementados.
Comprobar resultados completos, renderer, CI y revisión del PR de este HEAD
antes de considerar integrada esta unidad. El cierre real del PR prevalece
sobre esta nota previa de candidata. Verificar push y Pages separadamente.

```sh
python3 build.py --check
node --test tests/finger-cache-order.test.cjs
node --test tests/*.test.cjs
python3 tests/release_build.test.py
python3 tests/release_checkout.test.py
xvfb-run -a python3 -m tools.qa.run --suite sight --headed --timeout 1800
```

Ejecutar también [QA](QA.md), especialmente dedos, pulgares, manos, banda
palmar y conservación del cargador. No atribuir imágenes de 0.20.13 a esta
candidata. Revisión propia, no aprobación artística ni revisión independiente.

## Siguiente trabajo real

Tras integrar y verificar esta corrección, retomar rifle → revólver libre,
ya reproducido con Digit2 sobre 0fa83b9, no implementado. No extender el arco
a parejas no medidas. Otros cruces, herramientas/pesados, giros/anatomías,
cortes prioritarios visuales y coste por actor/LOD siguen pendientes en #6.
Las acciones reales prevalecen, no retrasarlas para disimular cortes.
#5 conserva arte, procedencia, materiales/UV y hardware. #7 conserva recorrido
íntegro, playtests humanos y hardware. No cerrar criterios por conteos de tests.

## Recuperación

Sólo master es permanente. #49/#50 retiraron sus ramas con respaldo previo,
leases exactos y verificación. Bundle #50: artefacto `10929250154` del run
`36310013208`, retención indicada hasta el 26 de diciembre de 2026. Su ZIP fue
descargado y restaurado en la conversación anterior. Conservar sólo trabajo
activo y retirar lo concluido con SHA comprobado y respaldo recuperable.
Revertir esta unidad con su versión/build, sin migrar ni borrar partidas.

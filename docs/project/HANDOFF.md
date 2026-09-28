# Continuación vigente · rifle ↔ revólver libre

## Base integrada, no repetir

#51 está integrado en `17f6086d4ec60c764cd58be62493ae12bd0e2c68`, árbol
`f82ac7205839239aa6826dfb26429e05cd3b543f`, producto 0.20.14. Verify posterior
`36320055066` aprobó sus seis jobs. Su caché de dedos canónica no se modifica
ni se oculta precalentando QA. #50 ya resolvió la distribución de sight.
El timeout histórico de #49 sigue registrado como fallo, no como aprobación.

## Unidad actual: candidata 0.20.15

[Plan y registro](../../specs/003-weapon-contact/plan-rifle-revolver-free.md),
[SPEC-003](../../specs/003-weapon-contact/spec.md), CONTACT-04/05, issue #6.
Rifle ↔ revólver libre reutiliza captura visible, montaje y 0.90 s cosméticos.
Palmas, matrices, dedos y pieza inicial se conservan sin retrasar selección,
disparo o nueva recarga. Se excluyen recargas activas/congeladas, devolución
cosmética pendiente y modelo mostrado fuera de esta pareja.

Cinco pruebas extendidas fallaron en la base. El arco inicial de 0.08 m fue
rechazado por chaqueta a −4.068 mm; se reutiliza 0.12 m sólo para la pareja
medida, conservando el límite de −2 mm. Los diez tests dirigidos aprueban.
No implica que se hayan verificado todas las anatomías, giros o toda la malla.

**Estado al escribir este commit:** cambio y regresión dirigida implementados.
El cierre del PR del HEAD exacto es el registro de suite completa, renderer,
revisión, CI, merge, push y Pages. No volver a implementar esta unidad sin
comprobar primero ese cierre. No atribuirle artefactos de 0.20.14.

```sh
python3 build.py --check
node --test tests/cross-family-handoff.test.cjs tests/finger-cache-order.test.cjs
node --test tests/*.test.cjs
python3 tests/release_build.test.py
python3 tests/release_checkout.test.py
python3 tests/qa_selection.test.py
xvfb-run -a python3 -m tools.qa.run --suite sight --headed --timeout 1800
```

Sight ahora exige 66 checks, 40 base y 26 cruces, con diez intercambios y
61 estados cada uno. Las cinco guardas compartidas se ejecutan en ambas
particiones y se cuentan una vez. Misma cámara, renderer y presupuesto.
Ejecutar además [QA](QA.md), exportación, geometría y persistencia afectadas.

## Siguiente trabajo real

Tras verificar esta unidad, elegir una fase concreta de recarga rifle/revólver
y reproducirla en UI/renderer antes de habilitarla. El revólver usa otro tipo
de pieza, no inferir una reinserción mecánica de un retorno cosmético genérico.
Otros cruces, herramientas/pesados, giros/anatomías, cortes prioritarios visuales
y coste por actor/LOD siguen pendientes en #6. Las acciones reales prevalecen.
#5 conserva arte/procedencia/materiales/UV; #7 recorrido/humanos/hardware.
No cerrar criterios globales por el conteo de tests.

## Recuperación

Sólo master es permanente. El bundle de #51, artefacto `10932299036` del run
`36321562419`, contiene tres referencias y toda su historia. ZIP SHA-256:
`03c63febabfeda2533abd390c9c0411401c66f447ebea2dd5ceee1d31cca9f50`.
Se restauró y verificó con `git fsck --full` para esta continuación. Retirar
sólo ramas concluidas tras respaldo y comprobación del SHA exacto.
Revertir esta unidad junto con versión/build sin migrar ni borrar partidas.

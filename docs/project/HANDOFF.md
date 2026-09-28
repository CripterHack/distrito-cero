# Continuación vigente · rifle ↔ revólver desde recarga

## Punto de partida

#52 ya está integrado y verificado en `d25baffca0f22e60a001f8f7f6e81ac8877cb9eb`,
árbol `1fd4f64fc57536034b6bd565cdd2a2793091f219`, producto 0.20.15.
[Su cierre](https://github.com/CripterHack/distrito-cero/pull/52) distingue CI del
PR, push y Pages. No repetir intercambio libre, caché de #51 o particiones de #50.

## Cambio implementado en este árbol (0.20.16)

[Plan](../../specs/003-weapon-contact/plan-rifle-revolver-reload.md),
[SPEC-003](../../specs/003-weapon-contact/spec.md), CONTACT-04/05, issue #6.
Ambas direcciones desde recarga conservan pose/pieza mostradas usando captura,
montaje y retorno existentes de 0.90 s. La única ampliación de runtime retira
la exclusión de recarga/pieza retornando; mantiene rechazado un tercer prop.
No modifica gameplay, duración lógica, munición, geometría, huesos o partidas.
El revólver no tiene un cilindro articulado independiente: el retorno es
cosmético y no una reinserción mecánica certificada.

Veinte pruebas dirigidas, siete fallos reproducidos antes del cambio. Se
amplían las matrices existentes, no se duplican. 128 casos de selección,
304 poses de culata, fases, congelación, reversión, acciones prioritarias,
caché fría/inicializada y restore. Mantener los límites y la pureza de lectura.

## Gate antes de ampliar producto

Consultar [issue #6](https://github.com/CripterHack/distrito-cero/issues/6) y el
PR vinculado para HEAD, CI, revisión y merge reales. Una implementación en el
árbol no demuestra por sí sola integración. No reutilizar capturas de #52.

```sh
python3 build.py --check
node --test --test-concurrency=2 tests/*.test.cjs
python3 tests/release_build.test.py
python3 tests/release_checkout.test.py
python3 tests/qa_selection.test.py
python3 tests/ci_workflow.test.py
xvfb-run -a python3 -m tools.qa.run --suite sight --headed --timeout 1800
```

El alias sight ejecuta 40 base + 26 cruces anteriores + 10 recarga nueva,
sin solapamiento, con doce secuencias de 61 estados. La partición
`sight-revolver-reload` añade un job, no un productor paralelo distinto ni
un nuevo catálogo. Cinco guardas comunes por partición, contadas una vez.
Ejecutar además [QA](QA.md), exportación, geometría y persistencia afectadas.
Mantener 1800 s/productor y 40 min/job. Mayor presupuesto agregado de runners,
no supuesta reducción de coste total o mejora de FPS.

## Siguiente trabajo real

Después de cerrar esta validación, elegir un cruce restante reproducible,
por ejemplo SMG/revólver, antes de ampliar el allowlist. No tratar otra vez
rifle/revólver libre o desde recarga como ruta ausente en este árbol. Quedan
herramientas/pesados, giros/anatomías combinados, continuidad visual de cortes
prioritarios y coste por actor/LOD. Una acción real siempre prevalece.
#5 mantiene arte/procedencia/materiales/UV y #7 recorrido/humanos/hardware.
No cerrar issues globales por conteos, ni atribuir revisión independiente.

## Recuperación y límites operativos

La limpieza de #52 fue bloqueada: sus ramas feature/helper se conservaron.
No reintentar el borrado por otra vía. Esta unidad no modifica esas ramas.
La copia local original es una instantánea de los 946 archivos y no historial
Git remoto. Los commits locales se distinguen por identidad y equivalencia
de árbol en los informes. Revertir esta unidad junto con versión/build no
migra ni borra partidas. Conservar los respaldos anteriores y los helpers
fuera de la ascendencia del producto.

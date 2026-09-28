# Continuación vigente · SMG ↔ revólver desde recarga

## Base integrada

#54 está integrado y verificado en **d50a60665638f43076b85739205d59c8ab2c1741**,
árbol a6375d6e8b589bc961a6565005101ec8b16cfc84, producto 0.20.17. Su Verify del
push **36395675734** aprobó siete jobs. [PR #54](https://github.com/CripterHack/distrito-cero/pull/54).
No repetir cambio libre SMG/revólver, recarga rifle/revólver #53 ni caché #51.

## Implementación de este árbol · v0.20.18

[Plan](../../specs/003-weapon-contact/plan-smg-revolver-reload.md),
[SPEC-003](../../specs/003-weapon-contact/spec.md), CONTACT-04/05, issue #6.
SMG/revólver desde recarga usa la captura visible y el retorno existentes.
Se retiran únicamente las condiciones de recarga activa/visible de la
exclusión de esta pareja; permanece el rechazo de un tercer prop mostrado.
No cambian munición, partidas, rig, geometría o prioridad de acciones.
No inventar un cilindro articulado del revólver ni llamar reinserción mecánica
al retorno cosmético del modelo.

Las pruebas existentes cubren siete fases y cuatro configuraciones, selector
congelado después de cancelar inputs, retorno/reselección, locomoción y caché
fría/inicializada. Se mantienen las anteriores tres selecciones lógicas.
Los puntos de la prueba de caché del revólver ahora observan su cuerpo real.

## Gate antes de ampliar

Leer el cierre del PR vinculado desde [issue #6](https://github.com/CripterHack/distrito-cero/issues/6)
para saber qué HEAD está integrado y qué comprobaciones terminaron. No inferir
merge de las notas de implementación, ni atribuir evidencia de #54 a este HTML.
La revisión es propia salvo identificación explícita de otra revisión.

```sh
python3 build.py --check
node --test --test-concurrency=4 tests/*.test.cjs
python3 tests/release_build.test.py
python3 tests/release_checkout.test.py
python3 tests/qa_selection.test.py
python3 tests/ci_workflow.test.py
xvfb-run -a python3 -m tools.qa.run --suite sight --headed --timeout 1800
```

Sight contiene 94 checks, tres particiones **40 +26 +28**, dieciséis secuencias.
Se conserva el tercer job histórico `sight-revolver-reload`, que ya contiene
SMG libre y ahora sus recargas. No hay otra matriz ni productor paralelo.
Mantener 61 estados, capturas, cinco guardas por partición y límites originales.
La concurrencia del comando Node local no altera el scheduling de CI.
Ejecutar las demás pruebas vigentes de [QA](QA.md), no todos los tests históricos.

## Siguiente trabajo real

Después de verificar este cierre, escoger y reproducir un cruce restante antes
de ampliar las rutas permitidas. Quedan herramientas/pesados, cortes visuales
prioritarios, giros/anatomías combinadas y coste por actor/LOD. No tratar otra
vez SMG/revólver libre o desde recarga como ausente sin consultar el cierre.
#5 mantiene arte/procedencia/materiales/UV y #7 recorrido, personas y hardware.
No cerrar issues globales por conteos de checks o por un paso de CI.

## Recuperación

La copia local es un snapshot de árbol con historia sintética. El commit
publicado debe usar el padre remoto real de #54, no el commit local.
No reintentar la limpieza bloqueada ni borrar ramas. Mantener los helpers
fuera del producto. Revertir esta unidad junto con versión/build no migra
ni elimina partidas. Conservar evidencia y fallos de cada ejecución.

# Continuación vigente · SMG ↔ revólver libre

## Base integrada, no repetir

#53 está integrado en **6ba8b86c6e18b160588caf75ecdb24c7e64f078f**, árbol
7b099a58a4aab912cbe70d55f07907e9205f9d6e, producto 0.20.16. Su Verify posterior
36387391877 terminó con siete jobs aprobados. Pages 36387391414 también aprobó
y su HTML fue cotejado con el árbol. [PR #53](https://github.com/CripterHack/distrito-cero/pull/53).
No repetir rifle/revólver desde recarga, cambio libre #52, caché #51 o particiones #50.

## Implementación de este árbol · v0.20.17

[Plan y alcance](../../specs/003-weapon-contact/plan-smg-revolver-free.md),
[SPEC-003](../../specs/003-weapon-contact/spec.md), CONTACT-04/05, issue #6.
SMG/revólver libre conserva la pose mediante captura/montaje existentes de
0.90 s. Se midió el arco de 0.12 m contra la culata real de SMG después de
rechazar 0.08 m a −4.068 mm de chaqueta. Tolerancia −2 mm sin cambios.

Sólo esta pareja libre se habilita. Se rechazan recarga activa, retorno visual
y tercer objeto mostrado. No cambian gameplay, geometría, rig, caché, munición,
partidas ni prioridad de disparo/nueva recarga. La transición es cosmética,
no una animación física certificada de enfundado.

Los bucles de regresión se amplían sin otra matriz: 136 casos de selección,
selector congelado, reversión, locomoción/memoria de pies, pureza y persistencia.
Dos pruebas nuevas de caché fría/inicializada conservan cuatro perfiles.
Los casos negativos de recarga y tercera pieza son obligatorios.

## Validación del HEAD e integración

Consultar el PR actual y [issue #6](https://github.com/CripterHack/distrito-cero/issues/6)
para los resultados completos y el estado de merge. Este commit no anticipa
la CI. El push real y Pages se comprueban separadamente. La copia local procede
de una instantánea exacta de árbol, con commit sintético distinto del remoto.

```sh
python3 build.py --check
node --test --test-concurrency=2 tests/*.test.cjs
python3 tests/release_build.test.py
python3 tests/release_checkout.test.py
python3 tests/qa_selection.test.py
python3 tests/ci_workflow.test.py
xvfb-run -a python3 -m tools.qa.run --suite sight --headed --timeout 1800
```

Sight suma **84 checks = 40 + 26 + 18**, catorce secuencias. El nombre histórico
sight-revolver-reload conserva sus dos recargas y usa capacidad disponible
para las dos rutas SMG libres, sin nuevo job. No se duplican las doce secuencias
anteriores. Mantener 61 estados, capturas, cinco guardas comunes bloqueantes y
1800 s/productor, 40 min/job. Ejecutar el resto de [QA](QA.md) aplicable.

## Siguiente trabajo real

Tras comprobar este cierre, reproducir SMG/revólver desde recarga antes de
habilitarlo. Permanecen otros cruces/herramientas/pesados, cortes prioritarios
visuales y coste por actor/LOD. #5 mantiene arte/procedencia/materiales/UV y
#7 recorrido, personas y hardware. No cerrar por conteo de pruebas.

## Límites operativos y reversión

La limpieza de #52 fue bloqueada. No reintentar por otra vía ni borrar ramas.
Las ramas concluidas de #52/#53 no son features pendientes. Los helpers se
mantienen fuera del árbol y ascendencia del producto. Conservar respaldos.
Revertir esta unidad junto con versión/build no migra ni elimina partidas.

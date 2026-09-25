# Cambio entre armas cortas · v0.20.11

Unidad de CONTACT-05 de [SPEC-003](../../specs/003-weapon-contact/spec.md), refs #6.
Base `5266cb7c45604d34e6f93dff21d2809da9247ee0`, PR #46 integrado.
La aceptación de esta unidad se registra en su PR y no cierra #5, #6 o #7.

## Defecto reproducido y decisión

La transición sólo aceptaba equipos con apoyo de culata. Cambiar pistola por
revólver reiniciaba la presentación y producía hasta 479.408 mm de salto palmar.
Además, la UI cancelaba el apuntado antes de capturar la pose. Compartir sólo el
actor de MotionTracker no conserva esa mezcla visual en las armas cortas.

Se extiende el montaje existente únicamente a pistola ↔ revólver disponibles y
sin recarga activa. La UI entrega el montaje que se veía antes de limpiar inputs.
Si el selector está pausado, toma su montaje congelado cuando la selección aún
coincide. `equipWeapon` acepta ese contexto opcional para `captureSwitch`, que
copia sólo datos de pose, no funciones del montaje, el actor o memoria de pies.
Las llamadas anteriores sin contexto siguen siendo válidas.

No se cambia el montaje lógico de disparo, física, cámara de juego, inventario,
selección, cancelación, disponibilidad, mallas, anclas o longitudes de huesos.
No se incorpora otro tracker, IK o reloj. Lectura gráfica no escribe gameplay.

## Contrato acotado

El cambio lógico es inmediato. La salida cosmética entre armas cortas dura
0.90 s de simulación y converge al montaje nativo. Las armas largas mantienen
sus 0.40 s de cambio libre y 0.60 s desde recarga. El arco y liberación del apoyo
reutilizan la transición existente. Se muestra un solo equipo: anterior en la
primera mitad, nuevo en la segunda. No es una animación física de funda.

Se exigen palmas iniciales a menos de 0.01 mm de la pose anterior, menos de
30 mm por paso preparado de 60 Hz y objetivos palmares a menos de 12 mm.
Los segmentos conservan su longitud. Pausa no avanza la memoria, restauración
la descarta y una acción real de disparo o recarga tiene prioridad inmediata.

Se probaron 0.60 s y 0.75 s antes de fijar el tiempo visual: preservaban el inicio,
pero fallaban el límite de velocidad de las palmas. La segunda variante alcanzó
31.262 mm en 36 casos de cuello/agachado/inclinación. No se relajó el umbral:
se ajustó exclusivamente la duración cosmética, sin retrasar los inputs.

## Verificación

`tests/sidearm-handoff.test.cjs` añade siete tests: ambas direcciones desde
apuntado y guardia, inclinación/agachado/cuello, selector congelado, reselección,
restauración, precedencia de acciones, rutas excluidas y actor seguido en marcha.
Cinco de los seis primeros tests fallaron en la base antes de tocar producción;
el test de rutas excluidas ya aprobaba. No atribuir RED a todos los controles.

La suite `sight` conserva sus 26 checks y añade seis para dos cambios por teclas
reales. Cada uno observa el instante previo, el inicial y 60 pasos posteriores,
con nueve capturas, incluyendo el cambio de modelo. Exige continuidad, contacto
con los objetivos renderizados, selección y munición intactas. Su contrato nuevo
es 32 checks. El resto de suites y los controles HTTP permanecen activos.

```sh
node --test tests/sidearm-handoff.test.cjs
node --test tests/*.test.cjs
python3 build.py --check
python3 tests/qa_selection.test.py
xvfb-run -a python3 -m tools.qa.run --suite sight --headed --timeout 900 --output artifacts/sidearm-handoff
```

Resultados completos, hashes y revisión gráfica en el PR de esta unidad.
Comparar evidencia del mismo HTML/cámara. GPU software y tiempo preparado no
son FPS físicos, playtest humano o aceptación artística global. Las aserciones
palmares no certifican colisión de toda la malla ni separación de toda la piel.

## Límites y reversión

Recargas activas entre armas cortas conservan cancelación inmediata, sin mezclar
el cargador de pistola con el cilindro del revólver. Cambios entre armas cortas y
largas, herramientas, equipos pesados, armas cuerpo a cuerpo y equipo no disponible
mantienen la ruta anterior. Son contratos pendientes, no suavidad prometida.
Las interrupciones por acciones reales no retrasan el disparo para ocultar cortes.

Revertir fuentes, pruebas, versión y build de esta unidad no requiere migración
ni borrado de partidas. [Estado](STATE.md), [continuidad](HANDOFF.md), [QA](QA.md).

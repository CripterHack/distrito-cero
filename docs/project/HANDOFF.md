# Continuación vigente · v0.20.10, contexto de marcha en la selección

## Base y unidad actual

Base remota `6dd7a01b29d3007377ccfe0d316cecf4235cc270`, PR #45 integrado con
0.20.9. Verify posterior 35977307974: todos los jobs aprobados, comprobado al
retomar. #42/#43/#44/#45 ya resolvieron guardia, preparación y cambios libres o
desde recarga dentro de sus alcances. No reabrir esas unidades ni sus ramas.

[TRACKED-HANDOFF](TRACKED-HANDOFF.md) y el
[plan](../../specs/003-weapon-contact/plan-tracked-handoff.md) describen el ajuste
actual. La captura usaba el jugador sin el MotionTracker que presentaba el
renderer, produciendo 92.171838 mm de salto en la reproducción de marcha.
La UI transfiere el actor filtrado como argumento opcional antes de cancelar
inputs. Dibujo, selector y captura comparten la misma instancia de seguimiento.
Sólo la presentación consume esa lectura, no el origen de disparo o gameplay.

Siete regresiones nuevas observaron RED y luego GREEN. La batería completa y
los artefactos exactos se registran en el PR de esta unidad. Su existencia, no
este texto previo a integración, acredita merge y publicación.

La suite gráfica handoff conserva su cobertura previa y añade dos casos con
marcha nativa/selección por tecla. Se separa en CI del resto de gráficos para no
acumular toda la carga bajo el mismo límite de tiempo. Sin pérdida de suites,
fallos ocultos o cambios de permisos. Los contratos ejecutan la selección Bash
y comprueban la unión normal/completa sin duplicar handoff.

## Siguiente trabajo después de integrar

No repetir el salto durante marcha resuelto en el contexto documentado. #6
conserva equipos sin dock, interrupciones por acciones reales, giros y acciones
combinadas con otras anatomías y coste por actor/LOD. Una acción real siempre
prevalece sobre la presentación. Reproducir un caso concreto antes de extender
el alcance y usar los observadores existentes, no otra matriz o solver.

#5 mantiene aceptación artística, fuentes/procedencia, materiales y UV. #7
mantiene escena/recorrido completo, playtests y hardware de referencia. No
fabricar resultados para cerrar issues globales.

## Verificación y ramas

```sh
python3 build.py --check
node --test tests/*.test.cjs
python3 tests/release_build.test.py
python3 tests/ci_workflow.test.py
```

Aplicar además [QA](QA.md) y revisar los artefactos del HEAD exacto. Comprobar
master/Pages por separado. [BRANCH-CLEANUP](BRANCH-CLEANUP.md): master es la única
rama permanente, conservar sólo trabajo activo, retirar ramas concluidas con
SHA exacto y respaldo. No integrar helpers de publicación al producto.

[Handoff anterior](https://github.com/CripterHack/distrito-cero/blob/6dd7a01b29d3007377ccfe0d316cecf4235cc270/docs/project/HANDOFF.md).
Revisión propia. Reversión sin migrar ni borrar partidas.

# Continuación vigente · candidata 0.20.12, salida de recarga de sidearms

## Base integrada

Master `5c0248f6674abfb39a304a20d407f886fa3a7957`, producto 0.20.11,
PR #47 integrado. Su CI anterior al merge aprobó cuatro jobs Verify, benchmark
y exportación. El PR registra separadamente el resultado posterior. Las dos
ramas concluidas se retiraron con respaldo. No repetir #42 a #47.

## Unidad actual

[SIDEARM-RELOAD-HANDOFF](SIDEARM-RELOAD-HANDOFF.md) y el
[plan](../../specs/003-weapon-contact/plan-sidearm-reload-handoff.md) describen
la salida desde recarga activa entre pistola y revólver. Se reutilizan captura,
retorno de cargador, montaje y duración de 0.90 s de las armas cortas.
Selección/cancelación y acciones reales siguen inmediatas. El cilindro del
revólver es geometría rígida existente, no una nueva animación mecánica.

Cuatro regresiones observaron RED. Sight conserva 32 checks y añade ocho con
dos secuencias de recarga. Se separa como job independiente sin perder suites,
alterar umbrales o permisos. Consultar el PR del HEAD para resultados finales.
Este documento no acredita integración.

## Pendientes reales

Tras verificar e integrar esta unidad, no repetir pistola↔revólver en recarga.
Antes del merge sigue pendiente su aceptación gráfica y CI exacta. #6 conserva
familias cruzadas, herramientas/pesados, cortes por acciones prioritarias,
giros/anatomías combinadas, revisión global y coste por actor/LOD. No retrasar
acciones reales para ocultar cortes ni escribir gameplay desde el renderer.
No crear matrices duplicadas: reproducir un caso concreto primero.

#5 conserva aceptación artística, fuentes/procedencia y materiales/UV. #7
mantiene recorrido íntegro, playtests humanos y hardware. No fabricar evidencia.

## Verificación y ramas

```sh
python3 build.py --check
node --test tests/*.test.cjs
python3 tests/release_build.test.py
python3 tests/ci_workflow.test.py
python3 tests/qa_selection.test.py
xvfb-run -a python3 -m tools.qa.run --suite sight --headed --timeout 1800 --output artifacts/sidearm-reload-check
```

Ejecutar además [QA](QA.md), revisar capturas/artefactos del HEAD y comprobar
master/Pages separadamente. [BRANCH-CLEANUP](BRANCH-CLEANUP.md): sólo master es
permanente. Conservar trabajo activo, retirar lo concluido con respaldo y SHA
exacto. Los helpers no pertenecen al árbol/ascendencia del producto.

[Handoff anterior](https://github.com/CripterHack/distrito-cero/blob/5c0248f6674abfb39a304a20d407f886fa3a7957/docs/project/HANDOFF.md).
Revisión propia, no independiente. Reversión sin migrar ni borrar partidas.

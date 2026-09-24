# Continuación vigente · v0.20.11, cambio entre armas cortas

## Base verificada y unidad actual

Base `5266cb7c45604d34e6f93dff21d2809da9247ee0`, PR #46 integrado, 0.20.10.
La ejecución posterior `36061029294` terminó con sus cuatro jobs aprobados.
No repetir las unidades #42 a #46: guardia/recarga, preparación, entrega libre,
salida desde recarga y contexto de MotionTracker ya tienen su evidencia.

La nueva unidad está descrita en [SIDEARM-HANDOFF](SIDEARM-HANDOFF.md).
Corrige la selección entre pistola y revólver disponibles fuera de recarga.
La UI conserva el montaje visible antes de limpiar inputs o toma el congelado
del selector. La simulación copia únicamente la instantánea de presentación.
El cambio lógico sigue inmediato, con salida cosmética de 0.90 s. No cambia
munición, origen lógico de disparo, disponibilidad, geometría ni partidas.

La suite sight conserva sus 26 checks anteriores y añade seis. Siete regresiones
Node cubren UI, pausa, reselección, marcha, prioridades y rutas excluidas.
La CI del HEAD y el PR de la unidad acreditan integración y publicación, no
la mera existencia de este documento. Conservar intentos fallidos como históricos.

## Pendientes reales

Después de integrar, no volver a tratar pistola ↔ revólver fuera de recarga como
pendiente. #6 conserva cambios entre familias distintas, herramientas y equipos
pesados, salida de recarga de armas cortas, interrupciones reales, giros y acciones
combinadas con otras anatomías, revisión global y coste por actor/LOD.
Una acción real siempre prevalece. Reproducir antes de ampliar el montaje.

#5 conserva aprobación artística global, procedencia, materiales/UV y coste
sobre hardware. #7 conserva escena/recorrido, playtests humanos y hardware.
No fabricar aprobaciones ni crear nuevas matrices equivalentes a las existentes.

## Verificación y ramas

```sh
python3 build.py --check
node --test tests/*.test.cjs
python3 tests/release_build.test.py
python3 tests/qa_selection.test.py
python3 tests/ci_workflow.test.py
```

Ejecutar además [QA](QA.md), revisar artefactos del HEAD exacto y verificar
master/Pages separadamente. [BRANCH-CLEANUP](BRANCH-CLEANUP.md): master es la
única rama permanente. Retirar trabajo concluido con respaldo y SHAs exactos.
Los helpers no pertenecen al árbol ni a la ascendencia del producto.

[Handoff anterior](https://github.com/CripterHack/distrito-cero/blob/5266cb7c45604d34e6f93dff21d2809da9247ee0/docs/project/HANDOFF.md).
Revisión propia, no independiente. Reversión sin migrar ni borrar partidas.

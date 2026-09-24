# Continuación vigente · v0.20.8, cambio visual entre equipos

## Base e implementación actual

Base remota `be26fa05612e3318ad764ca09ddd5f8ef7f6ad3f`. PR #43 integrado como
0.20.7 y Verify posterior 35926278907, benchmark 35926278952, exportación
35926278905 y Pages 35926277991 aprobados. Las ramas anteriores se retiraron con
respaldo. No volver a aplicar los parches de guardia/recarga/preparación #42/#43.

La nueva unidad de #6 corrige el salto al cambiar entre las cuatro familias con
dock. [EQUIPMENT-HANDOFF](EQUIPMENT-HANDOFF.md) describe contrato, alternativas
rechazadas, pruebas y límites. Selección y montaje de gameplay permanecen
inmediatos. El renderer entrega la pose durante 0.40 segundos, abriendo brevemente
la mano de apoyo mientras el objeto describe un arco exterior. Disparo/recarga
priorizan inmediatamente el montaje lógico. No se introduce funda ni segundo IK.

El PR de la unidad conserva los SHAs de código/documentación, las verificaciones
finales, revisión e integración. Este texto no acredita un merge o despliegue.
Usar los resultados de ese PR antes de tratar la candidata como publicada.

## Punto de continuidad

Tras verificar e integrar esta unidad, no repetir el cambio libre entre familias
ya cubierto. #6 conserva cambios desde una recarga activa o hacia familias sin
dock, acciones/anatomías/locomoción combinadas y coste por actor/LOD. Reproducir un
caso del renderer y preservar inputs, munición, alcance y persistencia antes de
extender el alcance. Reutilizar los observadores y suites existentes.

#5 mantiene decisión artística, materiales/UV y procedencia global. #7 mantiene
recorrido completo, pruebas humanas y hardware de referencia. No inventar
aprobaciones, participantes, FPS o ausencia universal de colisión para cerrar issues.

## Verificación y ramas

```sh
python3 build.py --check
node --test tests/*.test.cjs
python3 tests/release_build.test.py
xvfb-run -a python3 -m tools.qa.run --suite handoff --headed --output artifacts/handoff-check
```

Añadir los gates de [QA](QA.md), revisar capturas del HTML canónico y artefactos
exactos del HEAD. Verificar master/Pages separadamente. Revisión propia, no
independiente. El [respaldo y política](BRANCH-CLEANUP.md) siguen vigentes: master
es la única rama permanente, sólo conservar trabajo activo. Retirar ramas
concluidas/helper con SHAs exactos y respaldo sin integrarlos al producto.

[Handoff anterior](https://github.com/CripterHack/distrito-cero/blob/be26fa05612e3318ad764ca09ddd5f8ef7f6ad3f/docs/project/HANDOFF.md)
conserva 0.20.7. Reversión sin migraciones ni borrado de partidas.

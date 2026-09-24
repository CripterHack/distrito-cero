# Continuación vigente · candidata 0.20.9, salida de recarga

## Base integrada y cambio actual

Master verificado al iniciar: `3d6722e4e20b706c6a821b1866cf62c1f133784f`, 0.20.8,
PR #44 integrado. Verify posterior 35965293807 y Pages 35965293263 aprobaron.
Las ramas concluidas ya se retiraron. No reconstruir los trabajos #42/#43/#44.

La nueva unidad extiende el montaje visual existente a una selección entre las
cuatro familias con dock durante recarga. Mantiene cancelación lógica inmediata,
munición, inputs, disponibilidad y datos. Captura también la pieza extraída, que
vuelve a su asiento antes de reemplazar el único objeto mostrado. La salida de
recarga usa 0.60 s cosméticos, el cambio libre conserva 0.40 s. No hay otro IK.
[RELOAD-HANDOFF](RELOAD-HANDOFF.md) conserva el diseño, RED y ensayo rechazado.

El PR de esta unidad contiene la verificación final del HEAD y su estado real.
No atribuir aprobación remota a la candidata por existir esta documentación.
La suite handoff conserva los 16 checks previos y añade seis casos de aceptación
agrupados, sin sustituir HTTP o la comprobación de superficies por estadísticas.

## Continuidad

Tras integrar esta unidad, el cambio durante recarga entre estas familias no se
considera nuevamente pendiente. Siguen fuera la entrega hacia equipos sin dock,
suavidad de interrupciones por acciones reales, combinaciones de locomoción y
anatomías y coste por actor/LOD. Reproducir un caso concreto antes de ampliar el
montaje. No añadir solvers, matrices duplicadas o umbrales más laxos.

#5 conserva arte/procedencia/materiales/UV. #7 requiere recorrido completo,
playtests humanos y hardware de referencia. No inventar aprobación o mediciones.

## Verificación y ramas

```sh
python3 build.py --check
node --test tests/*.test.cjs
python3 tests/release_build.test.py
xvfb-run -a python3 -m tools.qa.run --suite handoff --headed --timeout 900 --output artifacts/reload-handoff-check
```

Ejecutar los otros gates de [QA](QA.md), revisar artefactos del HEAD y verificar
master/Pages por separado. [Política de ramas](BRANCH-CLEANUP.md): master es la
única rama permanente. Retirar ramas sólo tras integración verificada y conservar
trabajo recuperable. Los helpers no pertenecen al árbol o ascendencia del producto.

[Handoff anterior](https://github.com/CripterHack/distrito-cero/blob/3d6722e4e20b706c6a821b1866cf62c1f133784f/docs/project/HANDOFF.md).
Revisión propia, no independiente. Reversión sin migrar o borrar partidas.

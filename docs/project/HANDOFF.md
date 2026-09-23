# Continuación vigente · v0.20.7, preparación inicial

## Base verificada y unidad actual

Base remota `c27282f5ae830fe8f149d11396903d89c595acc9`, PR #42 integrado con
0.20.6. Su HEAD f52f75f aprobó Verify 35917149375, exportación humana 35917149458
y benchmark 35917149485. Los cuatro artefactos se cotejaron antes del merge:
205 checks WebGL, 80 HTTP y 36 de benchmark, además de original/derivado GLB.
El resultado posterior de master y Pages se consulta separadamente en #42.

La candidata 0.20.7 aborda el siguiente defecto, no repite guardia/recarga:
[preparación inicial](INITIAL-PREPARATION.md). Mantiene el apoyo y la referencia
superficial desde ready=0, con inclinación inicial acotada para las cuatro familias.
Los puntos finales asentados y equipos sin dock conservan sus resultados.
No cambia huesos, malla, cámara, física, munición o datos. No añade una funda.

Cinco regresiones nuevas con RED observado y **559 Node completos aprobados**.
**100 Python** actuales aprobados. El runner local nuevo pasó 28 checks y 76 PNG,
con hashes cotejados y separación explícita entre ciclos asentados e iniciales.
La evidencia adicional contiene 64 imágenes y un vídeo de rifle con 46 frames.
Se revisaron 24 instantes de las cuatro familias y un detalle, no todo el vídeo
como playtest humano. Escena/tiempo preparados y GPU software.

El PR registra HEAD, árbol exacto, CI e integración finales. La implementación
local o reconstrucción no equivalen a merge ni publicación. Las fuentes y el
HTML canónico tienen sus huellas en [INITIAL-PREPARATION](INITIAL-PREPARATION.md).

## Continuidad después de esta unidad

No tratar el desenvainado pendiente de las notas de 0.20.6 como trabajo nuevo
cuando el PR de esta unidad esté integrado. La preparación corregida empieza con
el objeto ya equipado, no valida todos los cambios entre familias o una animación
de funda. #6 conserva revisión global de transiciones/acciones/anatomías y coste
por actor/LOD, usando los observadores existentes y sin duplicar matrices.

#5 mantiene aceptación artística global, revisión de materiales/UV y procedencia.
#7 mantiene escena, recorrido completo, playtests humanos y hardware de referencia.
No inventar aprobaciones o FPS ni cerrar issues para reducir un recuento.

## Verificación y ramas

```sh
python3 build.py --check
node --test tests/*.test.cjs
python3 tests/release_build.test.py
```

Añadir los controles actuales de [QA](QA.md), revisar artefactos del HEAD exacto
y publicación separada. [BRANCH-CLEANUP](BRANCH-CLEANUP.md) sigue vigente: master
es la única rama permanente. Retirar las ramas ya integradas y el helper al
terminar, comprobando sus SHAs y conservando respaldo. Los helpers no entran en
el árbol ni el historial de producto. No restaurar ramas antiguas para continuar.

[Handoff anterior](https://github.com/CripterHack/distrito-cero/blob/c27282f5ae830fe8f149d11396903d89c595acc9/docs/project/HANDOFF.md)
conserva la aplicación del parche 0.20.6 y su límite inicial ya investigado aquí.
Revisión propia, no independiente. Reversión sin migraciones ni borrar partidas.

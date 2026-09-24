# Cambio de equipo durante marcha · v0.20.10

Unidad acotada de #6, [SPEC-003](../../specs/003-weapon-contact/spec.md),
[plan](../../specs/003-weapon-contact/plan-tracked-handoff.md).
Base remota `6dd7a01b29d3007377ccfe0d316cecf4235cc270`, PR #45 integrado, 0.20.9.
Su Verify posterior 35977307974 terminó con todos los jobs aprobados antes de
iniciar esta unidad. Ese resultado no sustituye la CI de este cambio.

## Causa y transferencia de contexto

La presentación usa el actor filtrado de MotionTracker, con velocidad suavizada,
aceleración y memoria de apoyo de pies. La captura de selección utilizaba el
jugador lógico sin ese contexto. Aun en el mismo instante, el montaje se calculaba
con dos alturas/poses distintas. El caso de rifle a SMG tras 30 pasos nativos con
throttle=0.60 reproducía un salto de 92.171838 mm en la palma izquierda.

`EquipmentRenderer.handlingActor(sim)` centraliza la lectura del tracker que ya
existía. Dibujo, congelación del selector y selección reutilizan esa instancia.
La UI obtiene el actor antes de cancelar entradas y lo pasa explícitamente como
argumento opcional a `equipWeapon(id, actorOverride)` y `captureSwitch`.
Sólo el montaje de presentación que captura la instantánea recibe el argumento.
No se instala otro tracker, solver, callback o reloj en la simulación.

El montaje lógico de gameplay, el origen de disparo, la selección, cancelación,
recarga y disponibilidad mantienen su ruta inmediata. La lectura no modifica
simulación, munición o memoria de pies ya muestreada en ese instante. La instantánea
sigue conteniendo sólo campos de entrega existentes, no el actor ni MotionTracker.
`restore` conserva su descarte de memoria transitoria. Las llamadas sin argumento
siguen siendo compatibles y usan el actor lógico: no se afirma seguimiento de
un renderer inexistente para clientes que no proporcionan contexto visual.

Al cambiar la simulación, el lector reinicia la misma instancia de tracking.
En estudio o sin tracker devuelve el actor de entrada sin tocar memorias de marcha.
No cambian huesos, anclas, geometría, física, cámara, datos o licencias.

## Regresiones

La base terminó 576/576 Node y build inmutable. Antes de editar producción, siete
regresiones fallaron: cuatro por familia, ruta UI, lector de renderer ausente y
salida desde recarga. Los casos numéricos registraron el salto original, no un
fallo de configuración. El test de la nueva API de renderer falló por ausencia
del método. La revisión GREEN de los siete completó sin skips.

Se comprueban los doce cambios ordenados entre familias a los 30 y 60 pasos de
aceleración, continuidad inicial menor que 1e-5 m, 50 pasos posteriores, contactos,
misma altura de apoyo, retiro de memoria, munición, trigger, serialización y origen
lógico independiente. El límite de continuidad posterior se aplica en coordenadas
relativas al jugador, restando únicamente su traslación física. No se etiqueta la
traslación al caminar como un salto de pose. Los casos de esta unidad no giran.

La prueba de UI utiliza el método de producción y exige obtener contexto antes
de cancelar inputs. El contrato del lector cubre escena nueva, idempotencia,
tracker compartido, estudio y ausencia de tracker. La recarga conserva los tres
puntos iniciales de la pieza mostrada y descarta la memoria al restaurar.

## Evidencia de navegador y presupuesto

La suite existente `handoff` conserva sus 22 checks/74 PNG anteriores. Añade dos
selecciones durante marcha con teclado real, 31 observaciones posteriores por
caso y siete PNG por caso. El contrato total pasa a 28 checks/88 PNG. El informe
separa `trackedCases` de cambios asentados y de recarga. Registra posición/yaw
para interpretar correctamente las distancias relativas. Se comprueban superficies
muestreadas, contactos, longitudes, munición, cámara/tiempo iniciales y continuidad.

La ejecución anterior de handoff tardó 871.424 s con presupuesto de 900 s, y el
job completo de gráficos se acercaba a sus 40 minutos. Con los nuevos casos,
la CI divide ese mismo trabajo en dos shards: handoff y gráficos restantes.
Fail-fast está desactivado y cada shard publica su propio artefacto. El primero
dispone de 1200 s por suite, el segundo conserva 900 s y ambos mantienen 40 min
por job. HTTP conserva su configuración. No se omiten suites ni se debilitan
criterios. Dos tests observaron RED y verifican en Bash la unión sin duplicados
para selección normal y completa, además de aislamiento de artefactos/permisos.

```sh
python3 build.py --check
node --test tests/tracked-handoff.test.cjs
node --test tests/*.test.cjs
python3 tests/ci_workflow.test.py
python3 tests/qa_selection.test.py
xvfb-run -a python3 -m tools.qa.run --suite handoff --headed --timeout 1200 --output artifacts/tracked-handoff-check
```

Repetición local completa: **583/583 Node y 103 Python vigentes** aprobados,
sin skips o cancelaciones. Autoría, build/export y enlaces de 78 documentos
aprobados. La primera ejecución agrupada de Python fue interrumpida por el
límite del laboratorio; la repetición completa conservó logs individuales.

Comparación canónica con la misma cámara, escena y tecla: 92.171838 mm iniciales
en 0.20.9 frente a 0 mm en ambas palmas de 0.20.10. Cuatro PNG con hashes
registrados, sin errores/peticiones externas, tiempo/munición conservados. Es una
comparación de dos instantes antes/después por build, no un vídeo completo.

HTML 0.20.10: `e8c527dd85bd412d089c9800bc6e70d4039c15b674bd990752acfb45785120b1`,
8,875,620 bytes. Fuente `a11c8d18e2ec8efec1c42f536033eb27c60faf761dce314dd1101e02eb968b57`.

La CI del HEAD exacto y los resultados completos del nuevo runner gráfico se
registran en el PR. No confundir el número esperado de checks con una ejecución
aprobada. El build y los 28 checks de handoff necesitan su propia evidencia.

## Límites y reversión

El seguimiento y la escena son preparados. El muestreo de piel/chaqueta frente
a volúmenes no demuestra colisión de toda la malla, CCD, GPU física o aceptación
artística. Permanecen equipos sin dock, cortes por acciones prioritarias, giros,
combinaciones de apariencia/locomoción y coste por actor/LOD. No se retrasan
acciones reales para ocultar esos cortes. #5 conserva arte/procedencia/UV y #7
recorrido/playtests/hardware. No cerrar requisitos globales por este subconjunto.

Revertir los archivos asociados de producto, pruebas, versión y build no migra
ni borra partidas. Helpers de publicación fuera de la ascendencia del producto.
Revisión propia, no independiente. [STATE](STATE.md), [HANDOFF](HANDOFF.md).

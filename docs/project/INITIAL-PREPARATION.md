# Preparación inicial con apoyo continuo · v0.20.7

Unidad de #6, [SPEC-003](../../specs/003-weapon-contact/spec.md). Base remota
`c27282f5ae830fe8f149d11396903d89c595acc9`: PR #42 integrado, versión 0.20.6.
El PR de esta unidad registra su CI, revisión e integración propias.

## Causa y corrección

El cambio de [guardia y recarga](STOCK-TRANSITIONS.md) conservó deliberadamente
la preparación inicial como pendiente. Con ready menor que uno, el montaje aún
interpolaba desde el antiguo origen interior y retiraba el apoyo del hombro.
La proyección al alcance de ambas manos podía devolver la culata hacia el pecho.
La reproducción nativa anterior midió hasta 23.70 mm de penetración muestreada.

Las cuatro familias con dock comienzan ahora en guardia baja apoyada. El mismo
montaje se mantiene referido a la chaqueta desde el primer fotograma, sin pasar
por el origen interior. El apoyo del torso no se desvanece al equipar. La inclinación
adicional de preparación se limita a 0.08 radianes en estas familias, frente a los
0.18 anteriores. Otros equipos conservan su rama. No se añade un sistema de funda,
una segunda pose, otro solver o un temporizador nuevo.

La curva nativa de ready, el filtro de apuntado y la disponibilidad del equipo
permanecen. Con ready=1, los resultados de la unidad previa se conservan. No se
modifican mallas, huesos, longitudes, anclas palmares, munición, cámara, posición
física o formatos de partidas. Sí cambia la presentación inicial del equipo.

## Pruebas y alternativas rechazadas

Cinco regresiones nuevas fallaron contra las fuentes 0.20.6. Mover sólo el origen
no bastó: cuatro familias fallaron. Mantener también el apoyo corrigió dos, pero
rifle/SMG aún fallaron por 2.334 mm con la inclinación inicial anterior. La revisión
final acota esa inclinación, sin cambiar el límite vigente de penetración de 2 mm.
Los fallos y las variantes se conservan en la evidencia, no como perfiles activos.

Cuatro tests inspeccionan rifle, SMG, escopeta y sniper durante 91 pasos nativos
por entrada de apuntado activada/desactivada, desde ready=0. Comprueban superficie,
palmas, longitudes, continuidad palmar menor que 30 mm por paso a 60 Hz y pureza.
La curva de ready se compara con su solución exponencial original. Un quinto test
cubre 448 instantáneas de cuello, agachado, inclinación y entrada de apuntado.
La peor distancia de chaqueta en ese barrido es aproximadamente -0.836 mm, dentro
del criterio existente. No significa ausencia absoluta de toda intersección.

Suite local completa: **559/559 Node**, sin fallos, omisiones, cancelaciones o todo.
Python: **100 pruebas aprobadas**, 91 del core actual y nueve de matriz. Autoría,
build reproducible y exportación de equipo aprobados. La ampliación de galería
observó primero dos fallos RED y después GREEN. La selección pasó a exigir 28
checks sólo después de añadir los cuatro casos, no para esconder pruebas antiguas.

Un contraste separado de 136 casos preserva todos los campos no numéricos y
14,352 campos numéricos del montaje asentado y de las otras familias a distintos
valores de ready. Diferencia máxima: 1.39e-17. Es una comparación de resultados de
código, no una certificación universal de trayectorias o equivalencia artística.

## Renderer canónico y cobertura gráfica

El runner local `20260923T210534Z-c019013a9334` aprobó **28 checks y 76 capturas**.
Conserva los 24 checks previos y las 48 capturas de poses/ciclos asentados. Añade
una comprobación y siete capturas de preparación por familia, 28 imágenes nuevas,
con ready=0 al inicio y mayor que 0.99 al final. Las dos series se guardan en
campos distintos, cycles e initialCycles. Se cotejaron los 76 hashes PNG.

El fixture admite ready explícito y observa el valor del montaje dibujado. La
galería lo muestra escapado y nombra la referencia actual de chaqueta para las
cuatro familias. No cambia los puntos o cuboides del observador de superficie.

Una captura adicional del HTML canónico 0.20.7 generó **64 imágenes**: 46 pasos
del rifle a 30 muestras/s y seis instantes de cada una de las otras tres familias.
La simulación avanza a 60 Hz. Se cotejaron todos los hashes. El margen mínimo de
chaqueta de estos casos neutrales fue aproximadamente +1.251 mm, sin errores GL,
excepciones o peticiones externas en los informes. Se revisaron visualmente 24
instantes en cuatro hojas y el detalle del primer apoyo, no todos los píxeles de
las 64 imágenes. El vídeo de rifle contiene 46 frames a 30 fps, verificados con
ffprobe. El primer intento VFR perdió frames; se conserva aparte y no se cuenta.

El informe anterior de 48 capturas del prototipo usa una identidad intermedia y
se conserva como exploración, no como evidencia del release. La evidencia final
identifica el HTML de este apartado. No se sustituyen módulos en memoria para
capturar una imagen que se atribuye al producto canónico.

HTML 0.20.7: `a4e30141a91d632b06db552cfcf5588da3d6fc9e423077dff972bcc20f9030b0`,
8,870,012 bytes. Fuente:
`1b90ec8dd6a48af70171a6e0a524e6837d0a81c2c6ceb6eb3ed07345ed542b4b`.

## Procedencia, reproducción y límites

La ejecución local inicial conserva en run.json el commit 5f7cdc del bundle
anterior y un árbol modificado. No son los bytes de ese commit: las huellas de
contenido identifican la candidata. Antes de publicar se recupera la ascendencia
auténtica de c27282f, se coteja el árbol completo y se publican padres remotos
reales. La reconstrucción temporal almacena objetos verificados y no entra en la
rama de producto. Su aprobación no sustituye la CI propia del PR.

El primer comando gráfico rechazó el directorio de salida antes de abrir un
navegador. La repetición usa un directorio nuevo dentro de artifacts. Las pruebas
del producto no se relajaron por esa condición del laboratorio.

```sh
node --test tests/stock-draw-clearance.test.cjs
node --test tests/*.test.cjs
python3 build.py --check
python3 tests/release_build.test.py
python3 tests/qa_selection.test.py
python3 tests/longarm_gallery.test.py
xvfb-run -a python3 -m tools.qa.run --suite longarms --headed --output artifacts/draw-check
```

No es una animación completa de sacar el objeto de una funda ni una revisión de
todos los cambios entre equipos. El test por fotograma sigue siendo un muestreo,
no detección continua entre instantes. El observador comprueba cara/cuello y la
selección de chaqueta superior contra dos cuboides, no toda la malla o toda la
geometría del equipo. Cámara/escena/tiempo preparados, Storage fixture y GPU
software no acreditan persistencia HTTP, FPS físicos o aprobación artística.

El PR exige Verify, benchmark y exportación humana del HEAD exacto, con revisión
de diff e informes. Master/Pages se comprueban después. #6 conserva revisión global
de superficies/acciones/anatomías, coste por actor/LOD y limitaciones declaradas.
#5 conserva arte, UV/materiales y procedencia. #7 conserva recorrido íntegro,
playtests humanos y hardware. Revisión propia, no independiente.

Revertir fuentes, pruebas y versión/build asociados no requiere migrar o borrar
partidas. [Handoff](HANDOFF.md), [estado](STATE.md), [QA](QA.md).

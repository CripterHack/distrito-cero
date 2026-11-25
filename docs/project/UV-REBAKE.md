# UV invertibles y mapas reproyectados · derivado portable

Refs #5 / CHAR-05/06. [Plan y contrato](../../specs/002-character-benchmark/plan-uv-rebake.md).
Esta unidad repara la parametrización del derivado de autoría del humano actual.
No sustituye aún el recurso canónico del juego.

[Procedencia y huellas](../../assets/uv-rebake-provenance.json).

## Qué cambia y qué se conserva

Blender genera cartas para los 9,672 triángulos de face y reproyecta los tres
mapas a PNG de 2048². Usa las tangentes explícitas del derivado anterior,
incluido su fallback declarado, para definir el sombreado de origen.
Color y ORM se hornean como emisión sin iluminación; las normales incorporan
la fuerza .30 de origen y se aplican con fuerza 1 en el derivado nuevo.
La fuente repite U y limita V: el baker conserva ese borde para no mezclar
los extremos del atlas en el cuello.

El empaquetador conserva posición, normal, articulaciones y pesos exactamente
por esquina. Los 49 huesos, once clips, nodos, escenas y las otras trece mallas
se conservan. Las 29,016 esquinas de face se expanden para evitar conflictos
entre las cartas; este aumento es explícito y no se presenta como optimización.
Se regeneran tangentes con MikkTSpace y se valida el nuevo GLB por separado.

Resultado técnico: **984 → 0 triángulos UV degenerados**, sin fallback de
tangentes y con cero errores/advertencias del validador glTF completo.
Los bytes originales permanecen como prefijo del binario derivado. Mapas y
atributos nuevos se añaden; el recurso histórico no se sobrescribe.

## Revisión visual y límites

Un visor local Three.js 0.180.0 carga los GLB con sus tangentes y animaciones.
Se comparan reposo y giro cervical en frontal, lateral y posterior, con una
vista de color y otra de normales: 24 capturas, 12 parejas a 800².
La comprobación del visor original contra sí mismo dio diferencias de cero
en los doce pares. Es un visor de autoría, no el renderer DQ del juego.

El pase final con controles de shader/consola y hashes posteriores aprobó
24/24 capturas, cero errores y cero peticiones externas. Una tentativa previa
fue rechazada por un recurso HTTP ausente; se declaró un favicon vacío local
y se repitió sin omitir errores. Las imágenes finales son idénticas a las
parejas ya inspeccionadas; no se contabilizan como escenarios nuevos.

Las vistas revisadas conservan la silueta, los contactos de las piezas y la
dirección general de las normales. Hay diferencias de remuestreo del detalle.
**La costura de color del cuello sigue presente en ambos modelos.** Una carta
invertible no repara la discontinuidad que ya contenían los mapas de origen.
No se cambia un umbral visual para declarar aceptación artística.

El mip chain RGBA8 completo de tres mapas 2048² ocupa aproximadamente 64 MiB
antes de compresión GPU; es un cálculo de presupuesto, no una medición.
No añadir este coste al juego sin revisar resolución, LOD y hardware.
La equivalencia entre skinning lineal portable y DQ nativo sigue pendiente.

## Reproducción

Herramientas de autoría: Blender 4.3.2 (Cycles CPU, sin denoising), Node,
Python/Playwright, Chromium, MikkTSpace 1.1.1 y glTF Validator 2.0.0-dev.3.10.
Las dependencias JavaScript quedan bajo artifacts; no entran en el juego.

Regresiones específicas:

```sh
node --test tests/human-uv-repack.test.cjs tests/uv-audit.test.cjs tests/human-tangents.test.cjs tests/glb-validation-contract.test.cjs
python3 tests/uv_bake_integration.test.py
python3 tests/uv_rebake_viewer.test.py
```

```sh
mkdir -p artifacts/uv-rebake
python3 tools/export_current_human.py --output artifacts/uv-rebake/current
npm install --prefix artifacts/gltf-tools --ignore-scripts --no-audit --no-fund --no-package-lock --save-exact mikktspace@1.1.1 gltf-validator@2.0.0-dev.3.10
node tools/export_human_tangents.cjs artifacts/uv-rebake/current artifacts/uv-rebake/baseline artifacts/gltf-tools/node_modules/mikktspace
blender -b -t 4 --python-exit-code 1 --python tools/bake_human_uv.py -- artifacts/uv-rebake/baseline/dc-human-0.20.22-neutral-tangents.glb artifacts/uv-rebake/bake
node tools/repack_human_uv.cjs artifacts/uv-rebake/baseline artifacts/uv-rebake/bake/recipe.json artifacts/uv-rebake/repacked
node tools/export_human_tangents.cjs artifacts/uv-rebake/repacked artifacts/uv-rebake/final artifacts/gltf-tools/node_modules/mikktspace
node tools/qa/validate_glb.cjs artifacts/uv-rebake/final artifacts/gltf-tools/node_modules/gltf-validator
node tools/qa/audit_uv.cjs artifacts/uv-rebake/final/dc-human-0.20.22-neutral-tangents-uv-rebaked-tangents.glb > artifacts/uv-rebake/final/uv-audit.json
npm install --prefix artifacts/uv-rebake/viewer-deps --ignore-scripts --no-audit --no-fund --no-package-lock --save-exact three@0.180.0
python3 tools/qa/render_uv_rebake.py artifacts/uv-rebake/baseline/dc-human-0.20.22-neutral-tangents.glb artifacts/uv-rebake/final/dc-human-0.20.22-neutral-tangents-uv-rebaked-tangents.glb --output artifacts/uv-rebake/comparison
```

Todos los destinos deben ser nuevos. El paquete de revisión conserva las
salidas efectivas, sus hashes, receta, capturas y reportes; las rutas anteriores
son una receta para otra ejecución, no una orden de sobrescribir evidencia.

## Siguiente unidad

Corregir la transición de color cervical mediante una receta de materiales
revisable y adaptar los contratos del renderer nativo antes de integrar UV.
El shader actual usa pigmento en V=.095 y una mezcla cervical propia; no puede
consumir el nuevo atlas sin adaptación. El PR continúa siendo una mejora de
autoría. #5/#6/#7 no se cierran por este derivado.

## Verificación de la unidad

- Repack: seis regresiones RED antes de implementar, seis aprobadas después.
  Suite Node completa actual: **686/686**, sin omitidos.
- Blender: **2/2** integraciones; el plano de control mide aproximadamente
  **0.303°** de error angular y rechaza la inversión incorrecta del verde.
  También comprueba escala de normal aplicada una sola vez y no mutación.
- Visor: **4/4** regresiones. Un shader inválido se reprodujo en Chromium;
  ahora los errores de consola/compilación rechazan el informe. Cambiar
  cualquiera de los GLB durante la captura también rechaza su aceptación.
- Build intacto; release **12/12** y exportación de equipos **1/1**.
- El GLB final tiene SHA-256
  `2066cf494d6df9bb356cbccd7299f0197009362978a603789560b755730f8560`.
  Las 29,016 esquinas conservan POSITION/NORMAL/JOINTS_0/WEIGHTS_0 byte a byte;
  se verificó el prefijo de 4,454,420 bytes y los contratos del rig/animaciones.

El primer bake se descartó por envolver V al muestrear el borde del atlas.
La segunda y tercera ejecución produjeron UV y PNG idénticos. La tercera
registra el script definitivo y guarda rutas relativas en el archivo Blender.
Los intentos descartados no se cuentan como entregas aprobadas.

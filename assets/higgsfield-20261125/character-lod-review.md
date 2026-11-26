# Personaje urbano de Higgsfield · detalle intermedio de autoría

La versión intermedia conserva **28.391 de 47.321 triángulos** en la pose estática. El GLB portátil original pesa 11.422.896 bytes. La entrega ocupa 9.416.484 bytes con tres imágenes 4K incrustadas idénticas a las de origen. La reducción de triángulos es del 40,0 %. Parte de la reducción de bytes procede de descartar los buffers históricos que la primera exportación conservaba. El presupuesto de texturas permanece en tres imágenes 4K.

La receta parte del [manifiesto de Higgsfield](manifest.json). Meshoptimizer toma en cuenta normales y UV al reducir la geometría. Se bloquean la zona superior de la cabeza y los extremos de ambas manos. El exportador recalcula tangentes MikkTSpace para usar el mapa normal original sobre los triángulos resultantes.

Durante la primera reducción una arista adquirió más de dos caras incidentes. La receta definitiva examina las incidencias con posiciones coincidentes soldadas, el sentido de las UV y la concordancia de las normales. Ante un defecto nuevo conserva las caras fuente vecinas y repite la simplificación. El resultado conserva exactamente 4.179 caras protegidas con las mismas posiciones, normales y UV por esquina. Los 17.040 sistemas tangentes pasan las pruebas de longitud y perpendicularidad. Hay cero triángulos UV colapsados o invertidos respecto a la orientación del atlas fuente. El validador oficial glTF registra cero errores y cero advertencias.

La malla resultante conserva un borde abierto y dos aristas con más de dos caras incidentes en las mismas posiciones que el original. De las 51 caras originales cuya normal geométrica se opone a la media de sus normales de vértice, permanecen 46. La revisión de retopología y pesos debe atender al espacio entre dedos y a la deformación de las axilas antes de preparar un personaje animado.

| Cámara de Blender, 512 × 512 | Coincidencia de máscara* | Diferencia RGB media, niveles de 255 |
| --- | ---: | ---: |
| Cuerpo en tres cuartos | 99,794 % | 1,466 |
| Rostro y cuello | 99,952 % | 1,352 |
| Mano y puño | 99,795 % | 0,834 |

\* Intersección dividida por unión de píxeles con alfa ≥128. Para RGB se comparan los píxeles donde ambas vistas tienen alfa ≥250. Las capturas usan Cycles CPU, semilla 73, luz y cámaras fijas. La repetición independiente de la fuente dio diferencias de cero píxeles en las tres vistas. En las comparaciones se distinguen cambios leves de sombreado en chaqueta y mandíbula. Los puentes de geometría entre dedos ya aparecen en el original. El personaje sigue siendo un modelo estático de revisión, pendiente de rig y medición en el juego.

## Reproducir desde el GLB portátil

Desde la raíz del repositorio, disponer el GLB del paquete de originales bajo `artifacts/higgsfield-20261125/character-portable/`. Se usaron Node 24.22.3 y Blender 4.3.2. El comparador de imágenes requiere Python con Pillow y NumPy. Usar directorios de salida nuevos.

```sh
work=artifacts/character-review
source_glb=artifacts/higgsfield-20261125/character-portable/urban-character-tangents.glb
mkdir -p "$work"
npm install --prefix "$work/deps" --ignore-scripts --no-audit --no-fund --no-package-lock --save-exact meshoptimizer@0.23.0 mikktspace@1.1.1 gltf-validator@2.0.0-dev.3.10
mods="$work/deps/node_modules"
node tools/prepare_higgsfield_character_lod.cjs "$source_glb" "$work/model" "$mods/meshoptimizer" "$mods/mikktspace"
lod_glb="$work/model/urban-character-intermediate.glb"
node tests/higgsfield_character_lod.cjs "$source_glb" "$lod_glb"
node tools/qa/validate_glb.cjs "$work/model" "$mods/gltf-validator"
blender -b -t 4 --python-exit-code 1 -P tools/prepare_higgsfield_character_views.py -- "$source_glb" "$work/before"
blender -b -t 4 --python-exit-code 1 -P tools/prepare_higgsfield_character_views.py -- "$lod_glb" "$work/after"
python3 tools/prepare_higgsfield_character_compare.py "$work/before" "$work/after" "$work/comparison.json"
```

SHA-256 del GLB intermedio: `075460e2524f882d3dc852c0aca900d18b9d09489991306e7a8d34b94b6d3057`.

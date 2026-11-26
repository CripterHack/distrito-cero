# Modelo de calle del personaje Higgsfield

El peatón utiliza la malla vestida del [GLB de autoría](character-walk.glb). Los dos niveles de detalle comparten un atlas y un conjunto de vértices de origen. En ambos se conservan las posiciones originales en metros, los cuatro índices y pesos de piel por vértice, los extremos de los pliegues posteriores de ambas rodillas y las 1.062 caras que dan grosor a las paredes entre los índices y los dedos medios. Las dos claves de flexión individual siguen disponibles en el GLB para autoría. La malla de calle representa la forma de reposo de los dedos y sigue sus huesos.

El LOD cercano contiene 9.773 triángulos y el lejano, 5.331. Los dos aprovechan un conjunto común de 8.143 vértices. El módulo integrado ocupa 716.567 bytes, de los que 131.180 corresponden al WebP antes de su codificación en base64.

La reducción tiene en cuenta normales, UV e influencias de las piernas, pies, antebrazos y manos. Si una contracción genera una cara invertida, cambia la orientación UV o altera la incidencia de una arista, la receta conserva los vértices de las caras fuente afectadas y repite. La receta conserva además la superficie exterior de la rodilla izquierda, donde dos capas cercanas del pantalón necesitan su propia triangulación al flexionar. Las coordenadas y las UV usan precisión de 32 bits. El redondeo de posición a 16 bits hacía coincidir vértices distintos entre los dedos. La regresión contrasta cada triángulo de ambos niveles con la geometría de origen y exige las mismas aristas abiertas y no-manifold heredadas.

## Superficie y movimiento

El atlas WebP de 512 × 1.536 incluye albedo, rugosidad/metal y normales. Cada tesela tiene bordes extruidos para dos niveles adicionales de mipmap. La malla principal usa 504 × 476 píxeles por mapa. Una banda aparte representa el color de vértice de las paredes interdigitales. El canal verde de las normales compensa el cambio de orientación de V entre glTF y el shader nativo. El GLB conserva las imágenes originales 4K.

Los datos de animación almacenan las claves locales del GLB y el bind de sus 49 huesos. El reproductor mezcla las rotaciones locales con cuaterniones, recorre la jerarquía y escribe las matrices finales en el formato de la paleta WebGL. La traslación de la pelvis está en metros. La fase de piernas relaciona la marcha y la carrera. La respiración utiliza su propio ciclo. Las pruebas comparan la paleta contra una lectura independiente de la animación del GLB y comprueban las transiciones y el cierre de los ciclos.

## Reproducir

Ejecuta estos comandos desde la raíz del proyecto. La conversión publicada usa meshoptimizer 0.23.0, NumPy 2.3.5, Pillow 13.0.0 y libwebp 1.6.0.

```sh
mkdir -p artifacts/peaton
npm install --no-save --prefix artifacts/peaton meshoptimizer@0.23.0
node tools/prepare_market_ped.cjs artifacts/peaton/node_modules/meshoptimizer artifacts/peaton/market-ped-data.js
cmp artifacts/peaton/market-ped-data.js src/market-ped-data.js
node --test tests/market-ped-asset.test.cjs tests/market-ped-pose.test.cjs
blender -b --python-exit-code 1 --python tests/check_market_ped_knees.py
```

La receta emite la huella SHA-256 del GLB de origen, los triángulos por nivel y los bytes del módulo generado. Blender comprueba la banda de 30 cm alrededor de cada rodilla de ambos LOD durante 129 fases por ciclo en reposo, marcha, carrera y una transición al 50 %. La prueba usa los mismos vértices y matrices que la calle. El juego carga el módulo desde su HTML autónomo.

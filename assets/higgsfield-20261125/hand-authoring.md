# Taller de manos del personaje de Higgsfield

Abrir `hand-edit.blend` en Blender. Contiene la malla intermedia de 28.391 triángulos con sus tres mapas empaquetados. Ambas manos se pueden editar en la misma malla. La escena arranca con la mano derecha encuadrada, ambas muestras de flexión a cero y la clave de forma `Basis` activa.

En Propiedades de datos, seleccionar el grupo `R.Puente.IM`. En modo Edición, pulsar **Seleccionar** para localizar los vértices del puente índice–medio. Cada lado dispone de nueve grupos que identifican la mano, los cinco dedos y las tres regiones entre los dedos largos. Los diez objetos `Punta.*` señalan vértices de la superficie. Las cámaras `Palma.L`, `Dorso.L`, `Palma.R` y `Dorso.R` permiten comparar los dos lados. L designa el lado izquierdo del personaje, que en esta importación mira hacia +X de Blender.

Para inspeccionar la deformación, cambiar `Prueba.Indice.L` o `Prueba.Indice.R` de 0 a 1. Cada muestra flexiona una región de 64 vértices del índice hasta 30° hacia la palma. Las caras compartidas con el dedo medio se estiran visiblemente. La arista medida con mayor alargamiento crece **40,52 mm a la izquierda y 42,30 mm a la derecha**. Son desplazamientos de esta prueba local preparada. Las marcas y grupos siguen siendo referencias de autoría. El personaje está pendiente de pesos y rig. Para editar el reposo, restablecer ambas claves a cero y seleccionar `Basis`.

## Medición de la superficie

Se intersectaron con planos las dos manos del GLB portátil original y las dos del modelo intermedio. En las cinco estaciones de cada lado se obtuvieron las mismas cantidades de contornos cerrados.

| Distancia lateral al centro del modelo | 0,77812 m | 0,83012 m | 0,85012 m | 0,87512 m | 0,89312 m |
| --- | ---: | ---: | ---: | ---: | ---: |
| Contornos por mano | 2 | 1 | 2 | 1 | 2 |

En la estación de 0,83012 m los cuatro dedos largos comparten una misma sección. Las coordenadas de las intersecciones de las cuatro estaciones exteriores coinciden entre los dos niveles de detalle al cuantizar a 10 nm. En la interior coincide la cuenta de contornos y difieren las muestras. Los ocho renders del intermedio muestran las cuatro vistas en reposo y bajo la prueba de flexión. Cuatro imágenes adicionales documentan el reposo del original con esas mismas cámaras. Los JSON conservan las secciones, las huellas de las imágenes y los índices de cara de cada región.

El siguiente paso de retopología es reconstruir las caras laterales de índice y medio en las regiones `Puente.IM` y crear los bucles en la inserción de los dedos. Hay que completar UV y normales de las paredes nuevas, volver a probar la flexión y comprobar que los contornos se separan en las estaciones distales. Esta entrega conserva el puente para que el artista pueda localizarlo y comparar la reparación frente a la geometría de referencia.

## Reproducción

Usar Blender 4.3.2, el GLB portátil original y el [personaje intermedio identificado por SHA](character-lod-review.md). Guardar el trabajo en una carpeta nueva.

```sh
original=artifacts/higgsfield-20261125/character-portable/urban-character-tangents.glb
intermedio=artifacts/character-followup/final/urban-character-intermediate.glb
salida=artifacts/hand-workshop-replay
blender -b -t 4 --python-exit-code 1 -P tools/prepare_higgsfield_hand_scene.py -- "$intermedio" "$salida/edit-ready"
blender -b -t 4 --python-exit-code 1 -P tools/prepare_higgsfield_hand_sections.py -- "$original" "$intermedio" "$salida/source-review"
blender -b -t 2 --python-exit-code 1 -P tests/higgsfield_hand_scene.py -- "$intermedio" "$salida/edit-ready/hand-edit.blend"
```

La verificación abre el archivo guardado en un proceso independiente. Compara todas las posiciones de reposo, índices, normales de esquina, UV, transformación y bytes de los mapas empaquetados con una importación nueva. Comprueba los marcadores de punta, grupos, cámaras, estado inicial y el efecto de activar cada muestra por separado. El GLB de origen permanece disponible para restaurar la geometría.

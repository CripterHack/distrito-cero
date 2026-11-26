# Retopología de los índices del personaje de Higgsfield

Abrir `hand-index-retopology.blend` en Blender. La malla del personaje tiene una hendidura entre índice y medio en ambas manos. Para ver su efecto, activar `Prueba.Indice.L` o `Prueba.Indice.R` hasta 1 y comparar las cámaras `Palma` y `Dorso` del mismo lado. El índice gira hasta 30°. La porción distal se mueve con independencia del dedo medio.

Para editar el reposo, restablecer ambas claves a cero y seleccionar `Basis`. Los grupos `L.Paredes reconstruidas` y `R.Paredes reconstruidas` seleccionan los dos lados y el extremo proximal de cada hendidura. Los grupos `Indice movil` identifican los vértices de la muestra de flexión. Se conservan los grupos de los cinco dedos, las otras dos regiones de unión y las diez marcas `Punta.*`. La referencia anterior permite comparar las mismas cámaras, poses y puntos de superficie. [Escena de referencia](hand-authoring.md).

Las comparativas muestran la referencia a la izquierda y la nueva malla a la derecha con la misma cámara, iluminación y escala. [Palma derecha](indice-palma-derecha.jpg) · [Dorso izquierdo](indice-dorso-izquierdo.jpg).

## Geometría y material

La operación recorta 151 triángulos originales. La nueva malla suma **30.099 triángulos**. De ellos, 28.240 conservan las mismas posiciones y UV exteriores, 797 reconstruyen los fragmentos de las caras cortadas y 1.062 forman las paredes interdigitales. Las nuevas caras exteriores tienen coordenadas UV y normales interpoladas de su cara de origen, identificada en el atributo `DC_fuente_cara`. El valor −1 identifica la pared. Las 458 aristas de unión conectan las superficies por índices compartidos.

Los tres mapas 4K empaquetados, color, normal y ORM, conservan sus bytes. El material exterior toma rugosidad y metalicidad de los canales verde y azul del ORM. La pared usa un segundo material con colores de vértice tomados de la piel palmar y rugosidad 0,68. Sus seis islas UV, dos superficies y su remate en cada mano, permiten pintarla. La revisión palmar de cerca muestra un filete claro sobre el medio y una sombra triangular en el extremo proximal, especialmente en flexión derecha. La banda oscura escalonada del índice ya aparece en la referencia.

| Medición en el personaje | Antes | Después |
| --- | ---: | ---: |
| Contornos a 0,83012 m del centro, en cada mano y en reposo | 1 | 2 |
| Mayor alargamiento de arista en la región medida, izquierda | 40,52 mm | 5,05 mm |
| Mayor alargamiento de arista en la región medida, derecha | 42,30 mm | 5,49 mm |
| Desplazamiento máximo del índice izquierdo / derecho | 46,25 / 46,32 mm | 46,25 / 46,32 mm |

En las cinco estaciones de cada mano (0,77812, 0,83012, 0,85012, 0,87512 y 0,89312 m desde el centro), los contornos pasan de 2/1/2/1/2 a 2/2/3/2/3. La regresión verifica los bordes abiertos y los compartidos por más de dos caras frente al modelo fuente. Se conservan sus defectos anteriores (un borde abierto y dos de incidencia múltiple). No se crean bordes abiertos en el área editada.

## Reproducción y comprobación

Usar Blender 4.3.2 y la carpeta de la escena de referencia, con `hand-edit.blend` y `hand-review.json` juntos. La receta comprueba la huella de la escena y su modelo de origen. Escribir en un directorio nuevo. Los ocho PNG muestran las dos manos desde palma y dorso, al inicio y al máximo de la flexión.

```sh
fuente=artifacts/hand-authoring-next/edit-ready
salida=artifacts/indices-reconstruidos
blender -b -t 4 --python-exit-code 1 -P tools/prepare_index_retopology.py -- "$fuente" "$salida"
blender -b -t 2 --python-exit-code 1 -P tests/index_retopology_scene.py -- "$fuente/hand-edit.blend" "$salida/hand-index-retopology.blend" "$salida/regression.json"
blender -b -t 2 --python-exit-code 1 -P tools/export_index_retopology.py -- "$salida/hand-index-retopology.blend" "$salida/portable/character-index-retopo.glb"
blender -b -t 2 --python-exit-code 1 -P tests/index_retopology_glb.py -- "$salida/hand-index-retopology.blend" "$salida/portable/character-index-retopo.glb"
node tools/qa/validate_glb.cjs "$salida/portable" "$validador"
```

`validador` apunta a la carpeta local del paquete `gltf-validator` 2.0.0-dev.3.10. `index-retopology.json` registra entradas, receta, escena y ocho vistas. La escena revisada tiene SHA-256 `a6f4f548f9a7073c548424321dc8f5d9ac0d300d8547d9b78d735eabd50becc2`. El GLB revisado mide 9.963.516 bytes y tiene SHA-256 `9b74d3e839623de66f5ccffb822cd74dad85f4afa0dd6d18a333c911095c06e7`. Khronos registró cero errores y cero advertencias. Al reimportar, las posiciones del GLB coincidieron con el `.blend` en los tres estados (reposo y cada flexión por separado) y en los 30 cortes de control. La primitiva exterior toma su color de la textura y la pared de los vértices. Para recuperar la superficie completa de entrada, abrir la escena de referencia.

La siguiente intervención de arte es suavizar el remate proximal y pintar la transición de la pared con la piel palmar. Tras ello quedan las uniones medio–anular y anular–meñique y la deformación con el esqueleto de 49 huesos. El GLB porta las dos muestras de flexión como claves de forma, sin rig ni animación de juego.

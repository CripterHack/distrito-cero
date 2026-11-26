# Marcha y reposo del personaje de Higgsfield

Abrir `character-motion.blend` del paquete de autoría y pulsar **Espacio**. La primera marca de la línea de tiempo muestra cuatro zancadas completas en el sitio. La segunda reproduce la respiración en reposo. Las cámaras **Estudio · oblicua** y **Estudio · perfil** permiten comparar la silueta y el contacto de los zapatos. En el GLB portátil, seleccionar la animación **Marcha** (0,7654 s) o **Reposo** (4 s) en el visor. [Descargar el GLB](character-walk.glb) · [Ver referencia y fases de marcha](marcha-personaje.jpg).

Para trabajar los pesos en Blender, seleccionar el esqueleto y activar las superposiciones del visor. La posición de reposo del esqueleto devuelve al personaje a su pose en T. Las claves de forma `Prueba.Indice.L` y `Prueba.Indice.R` siguen disponibles en la malla y permiten comprobar cada flexión de manera independiente. La escena de retopología conserva las cámaras de primeros planos y los grupos de selección de la mano. [Escena de manos](index-retopology.md).

## Qué se ajustó

El civil de Higgsfield/Tripo mide 1,85 m. La malla portátil usa metros, suelo en Y = 0 y avance +Z. La receta parte del GLB de índices de #71 y conserva sus 30.099 triángulos, ambas primitivas, UV, materiales y tres texturas 4K empaquetadas. La base de cada hueso se sitúa en las secciones del cuerpo del personaje, incluidos los pies originalmente escalonados y los dedos reparados. Los 49 nombres y padres coinciden con `DC.SkinRig.bones`. Cada vértice tiene de uno a cuatro pesos normalizados y los 49 huesos influyen sobre la malla. [Procedencia y condiciones de los recursos](../../docs/project/HIGGSFIELD-ASSETS.md).

La marcha toma del juego la cadencia a 1,35 m/s, el balanceo del tronco y de los brazos, el cabeceo de los zapatos y la trayectoria de cada tobillo. La adaptación conserva las etiquetas izquierda y derecha del modelo. Una corrección de reposo baja los brazos desde la T y gira las palmas. La cinemática inversa ajusta cada rodilla a las longitudes del muslo y de la pierna del modelo, y sitúa la superficie de la suela sobre el plano de contacto. El movimiento horizontal del personaje corresponde a quien reproduzca el clip. En reposo se muestrea de ida y vuelta la respiración del juego sobre un período de cuatro segundos.

## Comprobación después de exportar

La prueba reimporta el GLB en Blender 4.3.2, reproduce 33 fases por clip y evalúa las posiciones de la superficie deformada. La separación entre los 3.456 pares de vértices coincidentes en reposo y la diferencia de posición al cerrar cada ciclo fueron de 0 mm. Los pies alternan el avance y las manos lo acompañan en sentido contrario (correlación −0,935). La suela izquierda sube 11,8 cm y la derecha 12,0 cm. La penetración máxima bajo el plano fue de 0,3 mm en la marcha y 0,9 mm en reposo. La flexión animada de cada índice desplaza su extremo 46,25 mm y 46,32 mm respectivamente y conserva inmóvil la mano opuesta. En otras 17 fases por clip se comprobó por pares cada mano contra el tronco y los muslos, y un zapato contra el otro. Las caras de esas regiones registraron cero intersecciones.

Al bajar el brazo, la primera distribución de pesos estiraba de 63,9 a 117,5 mm una arista del hombro derecho. Tras repartir los pesos sobre la manga, en reposo mide 89,2 mm. En la marcha, la mayor variación se concentra ahora detrás de la rodilla derecha. Al 37,5 % del ciclo, una arista del pliegue del pantalón se comprime de 54,9 a 8,8 mm. El siguiente correctivo debe recuperar volumen al flexionar la rodilla. Quedan las uniones medio–anular y anular–meñique, las poses de agarre, la carrera y las transiciones entre clips. Estos ciclos emplean el skinning lineal del GLB. Su incorporación al juego requiere convertir y medir el recurso en las cámaras y los LOD del renderer nativo con cuaterniones duales.

## Reproducción

Desde la raíz del repositorio, con Blender 4.3.2, Python de Blender con NumPy y SciPy, Node.js y el paquete `gltf-validator` 2.0.0-dev.3.10. Las dos recetas crean sus directorios de salida. La opción `--frames` reproduce y renderiza la referencia, doce fases oblicuas y cuatro de perfil para la marcha y ocho fases oblicuas para el reposo. Las vistas miden 464 × 576 px. Cycles usa 32 muestras para la referencia y diez para cada fase.

```sh
original=/ruta/character-index-retopo.glb
salida=artifacts/movimiento-personaje
estudio=artifacts/estudio-movimiento
validador=artifacts/gltf-tools/node_modules/gltf-validator

blender -b -t 2 --python-exit-code 1 -P tools/rig_higgsfield_character.py -- "$original" "$salida"
node tools/qa/validate_glb.cjs "$salida" "$validador"
blender -b -t 2 --python-exit-code 1 -P tests/higgsfield_body_motion.py -- "$original" "$salida/character-walk.glb" "$salida/playback.json"
blender -b -t 2 --python-exit-code 1 -P tools/review_higgsfield_motion.py -- "$original" "$salida/character-walk.glb" "$estudio" --frames
```

El GLB de entrada tiene SHA-256 `9b74d3e839623de66f5ccffb822cd74dad85f4afa0dd6d18a333c911095c06e7`. El GLB animado mide 10.159.852 bytes y tiene SHA-256 `95515d51d7ba05df27cd9dcbddc9ffa0a496eac240bc0eb509c68768b702682c`. El validador de Khronos registró cero errores y cero advertencias.

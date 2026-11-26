# Rodillas del personaje de Mercado

La costura posterior derecha del pantalón mide 54,94 mm en la postura de referencia. Al 37,5 % de la marcha de v0.20.28, la arista se plegaba hasta medir 8,82 mm. En el modelo entregado mide 41,09 mm en esa misma fase y conserva al menos 38,92 mm en las 33 poses medidas. La corrección distribuye la flexión entre el muslo y la espinilla, con transiciones distintas delante y detrás de ambas rodillas.

[Marcha antes y después](marcha.jpg) · [Marcha completa](marcha.webp) · [Carrera antes y después](carrera.jpg) · [Mediciones](medidas.json)

| Clip y modelo | Pares de caras que se cruzan, izquierda / derecha | Muestras con cruces, izquierda / derecha |
| --- | ---: | ---: |
| Marcha de v0.20.28 | 1 / 58 | 6 / 83 |
| Marcha entregada | 0 / 0 | 0 / 0 |
| Carrera con los primeros pesos de marcha | 5 / 2 | 19 / 41 |
| Carrera entregada | 0 / 0 | 0 / 0 |
| Reposo entregado | 0 / 0 | 0 / 0 |

La prueba reimporta el GLB en Blender 4.3.2. En 129 muestras equidistantes por clip comprueba las intersecciones entre caras de cada rodilla, cuyo baricentro en la postura de referencia está a menos de 15 cm de la altura de la rodilla. Inspecciona 826 triángulos izquierdos y 717 derechos. Las caras contiguas se reconocen también a través de las costuras UV.

Una segunda prueba mide las aristas posteriores de al menos 8 mm en 33 muestras por clip. La arista que más se acorta en la carrera conserva el 55,2 % de su longitud a la derecha y el 57,6 % a la izquierda. Durante la marcha esos mínimos son el 67,9 % y el 69,5 %, respectivamente. La galería de marcha compara v0.20.28 con la entrega. La galería de carrera muestra la fase de flexión al 18,75 % frente al primer candidato de tres clips. Los dos paneles de cada comparación comparten cámara, luz y fase.

| GLB | SHA-256 |
| --- | --- |
| Marcha publicada en v0.20.28 | `95515d51d7ba05df27cd9dcbddc9ffa0a496eac240bc0eb509c68768b702682c` |
| Primer candidato con carrera | `939385363f1d2dd66e04050265cc3d5380d326e61b387965ed4cda8c4c107156` |
| Entrega con Marcha, Reposo y Carrera | `55f8152dfdbb9553bdd443ef3ae01b5ee032cc1b1e1de6ae1a1a5a60d7889bc7` |

Entre el primer candidato con carrera y la entrega cambiaron las influencias óseas de 2.090 vértices entre 0,184 y 0,779 m de altura. Los demás datos binarios son idénticos, incluidas las tres animaciones, la malla de 30.099 triángulos, los mapas y los controles independientes de los índices. El validador glTF de Khronos informó de cero errores y cero advertencias. La galería muestra el GLB importado en Blender. El juego también utiliza mallas simplificadas para los peatones.

## Reproducir las pruebas

Desde la raíz del repositorio, con Blender 4.3.2 y Node instalados, esta secuencia inspecciona el archivo jugable publicado y genera los tres informes. La prueba de aristas y contactos de pies requiere además el modelo anterior al rig corporal. [Documentación de animación](../../assets/higgsfield-20261125/body-motion.md)

```bash
mkdir -p artifacts/knee-review
modelo=assets/higgsfield-20261125/character-walk.glb
for clip in Marcha Reposo Carrera; do
  blender -b -t 2 --python-exit-code 1 -P tests/higgsfield_knee_surface.py -- \
    "$modelo" "artifacts/knee-review/$clip.json" --clip "$clip" || exit 1
done
```

Para reconstruir las vistas de marcha, se necesita el GLB de v0.20.28. El siguiente comando lo recupera del historial. Blender y Pillow generan los dos paneles a partir de los materiales incrustados.

```bash
git show bfa14da4:assets/higgsfield-20261125/character-walk.glb > artifacts/knee-review/v028.glb
blender -b -t 2 --python-exit-code 1 -P tools/qa/capture_higgsfield_knee.py -- \
  artifacts/knee-review/v028.glb artifacts/knee-review/anterior
blender -b -t 2 --python-exit-code 1 -P tools/qa/capture_higgsfield_knee.py -- \
  "$modelo" artifacts/knee-review/entrega --before artifacts/knee-review/anterior
```

Para reconstruir el «antes» de la carrera, la receta de `c654494` parte de `distrito-cero-personaje-indices.glb` y genera el primer candidato de tres clips. Al ejecutar la captura sobre ese GLB y sobre la entrega se añade `--clip Carrera` a ambos comandos y se usan directorios de salida nuevos.

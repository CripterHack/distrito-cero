# Barrio del Mercado · v0.20.28

## Recorrido en el juego

Desde el marcador de campaña del Taller del Mercado (168, 96), mirar al este hacia la persiana. El taller sustituye la primera edificación de esa parcela. La generación sigue consumiendo la misma secuencia aleatoria y mantiene los otros 391 edificios del distrito de origen. Las marquesinas están en (−13,5; 58) y (154,5; 130). Mirando desde la calzada se ven el banco, el panel perforado y la cubierta. La colisión del banco llega hasta el respaldo y deja libre la franja cubierta delantera. Ninguna coordenada de misión ni esquema de guardado cambia.

## Modelos del entorno

| Malla | Ancho × alto × fondo de autoría | Triángulos de autoría | Triángulos cercanos / lejanos | Cambio de detalle en equilibrado |
| --- | --- | ---: | ---: | ---: |
| Taller | 6,53 × 6,50 × 8,53 m | 17.648 | 6.529 / 1.853 | 72 m |
| Marquesina | 3,03 × 2,50 × 1,74 m | 8.372 | 4.604 / 1.339 | 40 m |

[Comparación de las dos calles en WebGL2](../../qa/mercado-v02028/README.md).

Los originales contienen color, rugosidad/metal y normales a 4096 × 4096. Los GLB editables se exportan con pivote en el suelo, tangentes y fachada hacia +Z. El HTML usa un atlas compartido de 1280 × 1920 con seis teselas, bordes extruidos y tres niveles adicionales de mipmap. Reutiliza las mallas y el atlas para ambas marquesinas y los reconstruye con el contexto WebGL. Los detalles de procedencia, prompts y huellas están en [generacion.json](../../assets/mercado-20261126/generacion.json) y las mediciones en [metrics.json](../../assets/mercado-20261126/metrics.json).

## Reproducción

Desde la raíz, Blender 4.3.2 con Pillow genera los GLB y los dos niveles embebidos. Para comprobar la fuente nativa:

```sh
blender -b --python-exit-code 1 --python tools/prepare_mercado_assets.py -- assets/mercado-20261126/originales artifacts/mercado-export
cmp artifacts/mercado-export/mercado-models.js src/mercado-models.js
python3 build.py --check
node --test tests/mercado-landmarks.test.cjs
```

Para repetir la comparación de calle con Playwright y Chromium, usar una carpeta de salida nueva:

```sh
git show e2e383c:index.html > artifacts/mercado-antes.html
DC_QA_BROWSER=/usr/bin/chromium python3 tools/qa/capture_mercado.py --before artifacts/mercado-antes.html --after index.html --output artifacts/mercado-calle
```

## Revisión pendiente

Comparar la lectura de los materiales de noche, el cambio de detalle al conducir y el coste de las vitrinas en GPU física. Validar vestuario, apariencias y presupuesto del GLB de personaje antes de sustituir un actor de campaña. El rendimiento de una captura en SwiftShader depende del equipo de QA.

## Vehículo, escaparates y personaje

- Las cuatro ruedas del sedán conservan el centro del neumático al girar. El disco y los radios ruedan juntos y la pinza sigue al portamangueta. [Comparativa y coste por distancia](../../qa/sedan-wheel-assembly/README.md).
- Los bajos comerciales tienen dos vitrinas con una cámara de 1,12 m de profundidad. El detalle de los estantes se dibuja al aproximarse. [Cámaras, recorrido y control rural](../../qa/street-corner-architecture/README.md).
- El personaje Higgsfield de autoría conserva 30.099 triángulos y los dos controles independientes de flexión de los índices. La marcha dura 0,765 s y el reposo 4 s. El siguiente correctivo de superficie identificado está detrás de la rodilla derecha. [Ficha de animación](../../assets/higgsfield-20261125/body-motion.md) · [GLB animado](../../assets/higgsfield-20261125/character-walk.glb).
- La animación de entrada del personaje jugable utiliza la manilla del panel móvil como objetivo de la palma. El paso alrededor de la puerta conserva el apoyo de los pies. [Vídeos y mediciones de la mano](../../qa/boarding-hand/README.md) · [Regresiones de trayectoria y cancelación](../../tests/boarding-handle.test.cjs).

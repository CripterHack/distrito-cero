# Evidencia del residente del Mercado

| Artefacto | SHA-256 |
| --- | --- |
| GLB de autoría con índices articulados, entrada al rig | `9b74d3e839623de66f5ccffb822cd74dad85f4afa0dd6d18a333c911095c06e7` |
| GLB de entrega con Marcha, Reposo y Carrera | `55f8152dfdbb9553bdd443ef3ae01b5ee032cc1b1e1de6ae1a1a5a60d7889bc7` |
| HTML v0.20.29 con luz de marquesina, apoyo del jugador y acceso al sedán | `eea706081b10f04383614db3dd9456277dbb85e0a48ac69a056c2013f086b8eb` |

El validador de Khronos 2.0.0-dev.3.10 completó el GLB con cero errores y cero advertencias. El rig y la conversión a mallas de calle reprodujeron su salida byte a byte. La escena de Blender 4.3.2 reabrió con las tres imágenes empaquetadas, los 49 huesos y las tres acciones sobre las pistas de animación. [Modelo y poses del estudio](../../assets/higgsfield-20261125/body-motion.md).

En el GLB se comprobaron 33 poses por clip para contacto de suela, cierre de ciclo y continuidad de la superficie. Otra prueba buscó intersecciones en dos bandas de la rodilla en 129 fases por clip. En las mallas de calle se utilizaron sus propios vértices y matrices, con 129 fases por pierna y LOD para cada una de las tres acciones y la mezcla de marcha y carrera al 50 %. [Comparación de las rodillas](../../qa/higgsfield-knee/README.md) · [Prueba de ambas mallas](../../tests/check_market_ped_knees.py).

El muestreo de una paleta de 49 huesos en un AMD EPYC 9V74 con Node v24.22.3 consumió una mediana de 3,36 µs de CPU de hilo en reposo, 3,16 µs en marcha, 2,74 µs en carrera y 4,76 µs mezclando las tres acciones. Para cada medición se descartaron dos tandas de calentamiento y se ejecutaron 25 tandas de 1.500 paletas, sin dibujar. La memoria de los buffers y la textura se especifican por separado. [Presupuesto de la malla](README.md).

La prueba de iluminación aisló la lámpara comparando los HTML de `7155ff7` y `5b97127`. El ajuste de apoyo del jugador se comprobó después en la misma cámara. Las capturas de Chromium utilizan WebGL2 y SwiftShader. La aceptación artística y las mediciones en GPU física quedan pendientes. [Mediciones de noche](../../qa/mercado-luz/README.md).

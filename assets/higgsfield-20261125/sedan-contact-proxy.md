# Guía de contacto de las cuatro ruedas del sedán

El archivo `wheel-contact-proxy.glb` sitúa cuatro cilindros en los pivotes del [sedán articulado](sedan-review.md). Para revisar el ajuste en Blender, importa el sedán y la guía en el origen, conserva las transformaciones de importación y activa la visualización de alambre para los objetos `contact_wheel_*`. El suelo del modelo está a Y = 0 en glTF, equivalente a Z = 0 en Blender. El eje de cada rueda es X.

Se escogió la altura de cada pivote como radio del cilindro analítico. Así la superficie circular queda en contacto con suelo horizontal durante todo el giro con el chasis en reposo. El ancho procede de los extremos en X de los vértices referenciados por cada rueda. Los cuatro nodos comparten una malla cerrada de 64 lados, 130 vértices y 256 triángulos. La guía completa tiene 4.988 bytes.

| Rueda | Centro en metros (X, Y, Z) | Ancho en m | Altura inferior del neumático en una vuelta, mm |
| --- | --- | ---: | ---: |
| Delantera izquierda | −0,772195 / 0,360303 / 1,341826 | 0,259553 | −0,741 a +5,230 |
| Delantera derecha | 0,771114 / 0,360514 / 1,342187 | 0,259919 | +0,467 a +4,659 |
| Trasera izquierda | −0,772061 / 0,360286 / −1,265229 | 0,259469 | −1,058 a +4,793 |
| Trasera derecha | 0,771494 / 0,360365 / −1,265657 | 0,260353 | −0,615 a +4,227 |

La última columna mide la malla visual respecto al plano del cilindro analítico. Un valor positivo deja un espacio bajo la banda de rodadura y uno negativo atraviesa el plano. Los extremos abarcan todos los ángulos. Al proyectar los vértices en el plano YZ, la mayor distancia al eje da el radio máximo y la menor distancia a las rectas de los lados de la envolvente convexa da el soporte mínimo. La malla poligonal de la guía añade hasta 0,435 mm de variación por sus facetas.

El render nativo detallado coloca las ruedas a X = ±0,920 m, Y = 0,365 m y Z = 1,360 o −1,390 m. La vía del sedán generado es de 1,5433 m delante y 1,5436 m detrás frente a 1,840 m en ese render. Su batalla media es de 2,6075 m frente a 2,750 m. Trasladar los neumáticos del modelo directamente a las coordenadas nativas desplazaría cada rueda unos 148 mm hacia fuera. La guía conserva el eje medido del modelo. La futura adaptación debe resolver la correspondencia con suspensión, giro, topografía y huella del chasis.

En Blender 4.3.2 se importaron los dos GLB por separado. Al girar una guía 17° las otras tres conservaron sus posiciones. Una segunda medición sobre los vértices importados situó el error máximo de soporte entre el neumático y el cilindro analítico en 5,2303 mm durante la vuelta completa. Al comparar las dos mallas poligonales, neumático frente a guía, el error máximo medido fue 5,1971 mm. Las vistas de perfil del paquete muestran la fuente y el contorno del proxy superpuesto con la misma cámara.

## Reproducción

Con el sedán articulado del PR #66 y el validador glTF de desarrollo instalado, ejecutar desde la raíz del repositorio. La segunda orden crea una carpeta de salida nueva.

```sh
node --test tests/sedan_contact_proxy.test.cjs
node tools/prepare_sedan_contact_proxy.cjs /ruta/urban-sedan-native-authoring.glb artifacts/contacto-sedan
node tools/qa/validate_glb.cjs artifacts/contacto-sedan artifacts/gltf-tools/node_modules/gltf-validator
```

`wheel-contact.json` registra los centros y radios en metros, los errores continuos por rueda y el RMS muestreado a pasos de 1°. Los manifiestos conservan las huellas de entrada, receta, salida y validación. El derivado parte del sedán de autoría con SHA-256 `1b3d9ef2f0824f18a9ef0146031deee55cde568b722456bda246ff81ade74a89`. El archivo auxiliar entregado tiene SHA-256 `2d7ab70f6e37a3c4fb7209b29115d3535c905ef5ab3227214fab5c1e50539be2`. El validador glTF registra cero errores y cero advertencias.

La geometría y las mediciones son referencias de autoría de rueda rígida. El motor sigue usando su sistema de vehículos y colisiones. Para revertir la preparación se retira la guía auxiliar de la escena de autoría.

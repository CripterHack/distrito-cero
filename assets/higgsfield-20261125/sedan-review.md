# Sedán articulado para autoría

El GLB preparado mide **4,400 m de largo**, **2,068 m de ancho con espejos** y **1,530 m de alto**. El origen queda en el suelo y en el centro de la planta. La escala uniforme conserva las proporciones del sedán generado. En glTF la vertical es +Y y el frontal apunta a +Z.

Al agrupar las posiciones coincidentes de la malla aparecen cinco componentes. La carrocería contiene 36.620 triángulos. Los cuatro conjuntos de neumático y llanta reúnen los 8.125 restantes. Cada conjunto tiene un nodo de pivote en el centro de sus límites geométricos y gira localmente alrededor de X. La posición de esos centros es una aproximación de autoría al eje mecánico.

La separación mantiene las texturas 4K, el material, las normales y las tangentes. Los cinco conjuntos usan listas de índices individuales. Se dibujarían cinco primitivas frente a una en el original. La adaptación del interior, las puertas, la colisión y los buffers del renderer sigue pendiente.

En Blender 4.3.2 se compararon los tres vértices de cada uno de los 44.745 triángulos. Las coordenadas UV y el orden se conservan. Después de aplicar la transformación de referencia, el error máximo medido en posición es inferior a 0,00000028 m. El contacto más alto de los cuatro neumáticos está a 0,812 mm del plano del suelo. En Blender se aplicaron 37° a las cuatro ruedas. Se movieron 5.175 vértices de rueda y los 23.648 de la carrocería conservaron su posición. En una vuelta con el chasis fijo, el mínimo teórico del neumático respecto al suelo es −1,06 mm y el máximo observado cada grado es +5,20 mm. Esta variación afecta al futuro proxy de contacto. La prueba Node también gira una rueda individualmente y comprueba el reposo de las otras tres. Los informes y los renders de perfil y tres cuartos acompañan el GLB en el paquete de revisión.

## Reproducción

Partir de la carpeta `sedan-portable` del paquete original de Higgsfield. Incluye el GLB con tangentes y su manifiesto. Desde la raíz de un checkout, con un directorio de salida nuevo:

```sh
node --test tests/prepare_higgsfield_sedan.test.cjs
node tools/prepare_higgsfield_sedan.cjs artifacts/higgsfield-20261125/sedan-portable artifacts/sedan-review-model
node tools/qa/validate_glb.cjs artifacts/sedan-review-model artifacts/gltf-tools/node_modules/gltf-validator
```

La versión del validador y los comandos de instalación están en el [registro de autoría](../../docs/project/HIGGSFIELD-ASSETS.md). El GLB entregado pesa 11.082.652 bytes. Su SHA-256 es `1b3d9ef2f0824f18a9ef0146031deee55cde568b722456bda246ff81ade74a89`. El validador oficial registró cero errores, cero advertencias y cinco avisos informativos sobre datos de la fuente retenidos. Al retirar el derivado se recupera el modelo estático de origen. Las condiciones de uso registradas para la fuente siguen aplicándose.

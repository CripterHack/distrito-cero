# Alineación del habitáculo y la puerta del conductor

Abrir `sedan-cabin.blend` en Blender y alternar las colecciones de referencias, corte de carrocería y pose del conductor. El archivo conserva los cinco objetos de malla del sedán articulado, sus pivotes y tres texturas 4K empaquetadas. La colección del conductor muestra las 49 articulaciones de una pose sentada de Distrito Cero. La línea de entrada muestrea 17 posiciones del origen del actor durante la fase de sentarse. Ese origen es una referencia de animación y queda por debajo del cojín.

El corte de la carrocería a X = −0,38 m permite comparar el coche con la postura antes de construir colisión y transferir movimientos. En la pose muestreada, ambas articulaciones de tobillo quedan **8,43–8,47 cm por debajo** de la primera superficie de carrocería encontrada al lanzar un rayo desde abajo en su posición XZ. La superficie superior del techo se encuentra **21,30 cm sobre la articulación de la cabeza**. La longitud de cabeza y calzado, el espesor del revestimiento y el movimiento afectan al espacio libre del ocupante. La adaptación del piso y del asiento debe resolver el cruce inferior.

En el lateral izquierdo, la bisagra nativa se sitúa **4,74 cm** por fuera de la primera superficie del modelo a esa altura y longitud. El centro del tirador nativo en reposo queda **10,42 cm** por fuera y el objetivo de la mano durante la apertura, **19,40 cm**. Cada cifra se obtiene con un rayo horizontal independiente desde fuera del vehículo. El objetivo de apertura y el tirador cerrado difieren en **1,09 m longitudinales**. Antes de animar la puerta del sedán conviene fijar su manilla sobre la pieza articulada y evaluar el alcance en la misma fase del movimiento.

## Reproducción

Usar el GLB articulado del PR #66 junto a Node y Blender 4.3.2. El exportador llama a la simulación de acceso, al muestreador de pose y a los métodos de dibujo del coche nativo con un coche detenido y sin daños. Para el conductor de variante 1, el ajuste cervical de apariencia es de 39,27 mm. El muestreador aplica ese ajuste a los pivotes y a la pose en el instante 1,25 s. Registra la variante, el instante y el ajuste en `cabin.json`. Los marcadores se colocan en el sistema local del vehículo con +Z hacia delante. El script de Blender convierte los ejes una sola vez. Conserva el corte de 913 segmentos, índices de las caras impactadas, coordenadas y huellas de los datos en `section.json`. Las pruebas verifican independencia de la traslación global, lado del volante y posiciones de cabeza y cuello de la pose sentada.

```sh
node --test tests/sedan_cabin_guides.test.cjs
mkdir -p artifacts/cabin-review
node tools/sample_sedan_cabin.cjs artifacts/cabin-review/cabin.json
blender -b --python-exit-code 1 -P tools/prepare_sedan_cabin.py -- \
  /ruta/urban-sedan-native-authoring.glb artifacts/cabin-review/cabin.json artifacts/cabin-review/scene
```

La preparación del archivo es reversible eliminando el derivado. El paquete de autoría incluye el corte ilustrado y la prueba de reapertura en Blender.

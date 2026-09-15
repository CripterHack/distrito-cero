# Distrito Cero v0.9 · Anatomía y materiales

Base única: v0.8 Presencia. No reescribir mundo, ocupación ni campaña.

## Entrega focalizada
1. Sustituir la cabeza de anillos por anatomía facial con párpados, nariz, labios y orejas modelados. Integrar geometría real de MakeHuman HM08 y un target adulto CC0, con atribución y huella de los bytes usados. No confundir la herramienta de transferencia con autoría original.
2. Incorporar mapas de piel, normal y rugosidad acotados y embebidos. Conservar UV al simplificar. Ajustar ojos con iris, pupila, humedad y apertura acotada. Cabello adaptado al cráneo con mechones cortos.
3. Refinar silueta de hombros y mangas, costuras, cierres y manos sin cambiar los puntos de apoyo de las interacciones.
4. Aplicar el recurso a protagonista, peatones y conductores mediante el mismo sistema de instancias/LOD. Variar tintes de forma relativa, no multiplicar la piel dos veces.
5. Mantener las secuencias de ocupación, atlas y guardados. Añadir revisión de materiales dentro del juego y capturas equivalentes de antes/después.
6. Verificar lógica, pesos, UV, carga de texturas sin red, shader color/sombra, poses, multitudes y bucle real. Exportar las fuentes y HTML realmente comprobados.

## Límites
No mocap, no simulación de pelo, no escaneo de una persona real, no promesa de AAA alcanzado. La comparación visual real decide el resultado, no el número de polígonos. Los recursos externos serán datos artísticos CC0 preparados durante construcción, no librerías de ejecución.

## Decisiones de ejecución

Se completó la cabeza con geometría artística CC0 real, en lugar de aumentar otra vez los anillos del modelo anterior. La simplificación preserva la costura UV y el sistema de instancias permite compartir los mapas en todo el reparto. El cuerpo mantiene la familia original con hombros, mangas, cuello y costuras refinados. La articulación individual de los dedos y una reconstrucción anatómica de las manos se dejan explícitamente para otra entrega, no se consideran implementadas.

Las reglas de juego y el esquema de persistencia se conservaron. La validación incluye el bucle nativo de entrada/extracción/salida y cruces del mundo, además de capturas preparadas bajo luz de día y noche. Se añadió exportación GLB texturada como recurso de autoría, sin convertirlo en dependencia de carga.

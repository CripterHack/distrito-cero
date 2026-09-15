# Distrito Cero v0.19 · Contacto articulado

## Inicio y compatibilidad

Abrir el HTML en el navegador, fuera de la vista previa del chat. Se mantienen creador de personaje, once peinados, proporciones y doce espacios independientes con nombres. El personaje y el inventario pertenecen a cada espacio. Exportar los JSON desde v0.18 e importarlos en v0.19 antes de seguir, sin asumir que dos archivos HTML comparten automáticamente almacenamiento.

## Cómo revisar la actualización

1. Equipar el fusil desde Tab, cerrar y alternar Z. Comparar la postura baja con el apoyo al hombro. Caminar y agacharse con X para revisar la adaptación de codos y apoyos.
2. Equipar una pistola y apuntar. Ambas manos se desplazan hacia delante, en lugar de permanecer recogidas contra el pecho. El índice no adopta su máxima flexión por el simple hecho de apuntar.
3. Disparar con J y recargar con L. La mano izquierda se abre al abandonar el apoyo, vuelve a cerrarse sobre la pieza y acompaña su desplazamiento e inclinación antes de regresar.
4. Abrir Tab mientras se apunta o recarga. El mundo y la recarga permanecen pausados. Cerrar sin cambiar de equipo permite regresar sin un salto inmediato al montaje bajo. Las entradas de disparo y cargas no se reactivan.
5. Probar Gauss con 9, EMP con 0 y binoculares con B. Los perfiles utilizan apoyos distintos. Los binoculares se sostienen a ambos lados de los tubos.

## Controles conservados

| Acción | Entrada |
| :--- | :--- |
| Caminar o conducir | WASD o flechas |
| Correr, agacharse | Shift, X |
| Entrar/salir/cancelar acceso | F |
| Interactuar | E |
| Usar arma o herramienta | Clic izquierdo o J |
| Apuntar/observar | Clic derecho mantenido o Z |
| Mirar con arma | Arrastrar con clic derecho |
| Recargar | L |
| Selector de equipo | Tab |
| Gauss, EMP, binoculares | 9, 0, B |
| Zoom binocular y marca GPS | Rueda o +/−, H |
| Rendición | Mantener R |
| Atlas, foto y pausa | M, P, Esc |

Los botones táctiles permanecen disponibles. No se puede disparar mientras se conduce, se manipula un objeto, se repara o transcurre el acceso a un coche. La reposición y los costes de moneda del juego siguen siendo los de v0.18.

## Qué es nuevo y qué no

El controlador trata la palma y la muñeca como referencias distintas. La posición del arma, ambas palmas, el cargador y sus orientaciones derivan del mismo montaje. La postura utiliza el mismo actor de locomoción que el renderer, evitando que el arma se apoye en un torso calculado con otro estado de movimiento.

La culata se aproxima al hombro articulado durante el apuntado normal. A elevaciones extremas se prioriza el alcance de los brazos antes que forzar un apoyo rígido al hombro. Los segmentos óseos no se alargan para alcanzar un arma.

Se conservan los tiempos de recarga y la transferencia de munición al terminar. Pistola, subfusil, fusil, rifle de precisión, Gauss y EMP tienen una pieza separada. Revólver, escopeta y lanzador mantienen gestos simplificados, no una reproducción mecánica completa.

El modelo humano conserva su geometría, texturas y pelo de v0.18. Las empuñaduras del equipo son más redondeadas, pero el conjunto continúa siendo estilizado. El sistema no resuelve colisiones individuales de todos los dedos, contacto óptico exacto ojo/mira, tejidos o manos físicas. Puede haber intersecciones en combinaciones extremas. Los NPCs no reciben inteligencia de combate armado nueva.

## Partidas y archivos

No cambia el formato de guardado. Los estados visuales de retroceso, inercia, preparación e índice no se serializan. Cada partida conserva las cantidades de munición y su equipo. Importar agrega espacios independientes, no reemplaza por nombre.

El GLB opcional es una galería estática de trece equipos, con empuñaduras y seis piezas de recarga identificadas. La recarga, las palmas y la interacción dependen del código y no son clips incluidos en el GLB. No es un plano de fabricación.

## Evidencia

Las comparaciones cargan el HTML v0.18 original y el nuevo con la misma cámara, pose de referencia y luz. El vídeo avanza explícitamente el tiempo de simulación antes de capturar cada fotograma real. Su velocidad de reproducción no indica los FPS de ejecución. Consultar VERIFICACION.md para cifras, alcance y límites de esta entrega.

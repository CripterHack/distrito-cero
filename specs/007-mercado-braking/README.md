# Último paso en la acera del Mercado · v0.20.31

El residente debe reunir los pies antes de dar media vuelta en los dos extremos de su ruta. En v0.20.30, cuando el origen ya estaba detenido, el centro de una suela próxima al suelo recorría hasta 55,58 mm al mezclar la marcha con reposo. Desde la marquesina del Taller del Mercado se puede seguir toda la maniobra a pie o desde el coche.

| Escenario | Criterio de aceptación |
| --- | --- |
| Último paso hacia la esquina o la marquesina | La frenada empieza en marcha y termina en reposo sobre el punto de llegada. El talón y la puntera del pie de apoyo permanecen plantados durante la transferencia. |
| Salida de la frenada | Comprobar el empalme en movimiento, los primeros 0,5 s tras llegar y las cinco fases de la media vuelta. Comparar los dos extremos y los dos niveles de detalle del personaje. |
| Claxon, pausa o cambio de distancia | Mantener continuidad de posición y pose, y la respuesta del residente a un vehículo cercano. |
| Autoría | Las dos frenadas se pueden examinar por separado en el GLB y la escena Blender, con la malla, el rig y las cuatro acciones previas como referencia. |

[Modelo de partida y medición anterior](../006-mercado-turn/evidence.md) · [Procedencia del civil de Higgsfield](../../assets/higgsfield-20261125/manifest.json).

## Modelo y escena

En el visor glTF, seleccionar `FrenadaL` o `FrenadaR` y reproducir una sola vez. En Blender, las marcas 273 y 298 permiten comparar los apoyos. Desde el marcador del Taller (168, 96), caminar hasta la marquesina y seguir al residente entre las coordenadas Z = 130 y Z = 149 de la acera X = 155,5. El último paso dura 0,490 s sin alarma. [GLB del civil](../../assets/higgsfield-20261125/character-walk.glb) · [Escena editable y cámaras](../../assets/higgsfield-20261125/frenada-estudio.md).

Al llegar en coche, el sedán que cruza el umbral de distancia conserva los ejes de sus ruedas. De noche, en la esquina comercial del Mercado, la luz superior ilumina las cajas y las baldas detrás del cristal. [Modelo del sedán y reproducción](../../qa/sedan-axles-v02031/README.md) · [Comparación de los escaparates](../../qa/mercado-vitrinas-noche/README.md).

## Coste de la animación

El módulo del civil embebido en el HTML suma 53.334 bytes y alcanza 802.665 bytes. Las dos nuevas acciones tienen 61 claves y 20 canales cada una. Las mallas de 9.773 y 5.331 triángulos, el atlas y las cuatro acciones anteriores conservan sus datos originales. [Pruebas y límites](evidence.md).

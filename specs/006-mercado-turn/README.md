# Media vuelta del residente del Mercado · v0.20.30

Al llegar a la marquesina o a la esquina, el residente debe cambiar de dirección recolocando cada pie y trasladando el peso al otro. En v0.20.29 cambiaba la orientación de toda la instancia mientras reproducía el reposo. El punto donde apoyar cada suela debe poder comprobarse en el mundo y en ambos niveles de detalle.

| Escena | Criterio |
| --- | --- |
| Llegada a cualquiera de los dos extremos | Una media vuelta completa dentro de la parada de 2,4 s. El origen del actor permanece en su acera. |
| Pasos de giro | Cada pie se despega y vuelve a apoyar. El otro sostiene el cuerpo sin barrer el suelo. Comprobar el desplazamiento horizontal de las suelas y la altura respecto al pavimento. |
| Claxon durante el giro | Se conserva la fase y el residente acelera la salida hacia el tramo disponible. |
| Reproducir el GLB fuera del juego | La cuarta acción se puede seleccionar por separado y mantiene su orientación final en la última clave. |

La malla de referencia proviene de la generación de Higgsfield ya integrada. [Procedencia](../../assets/higgsfield-20261125/manifest.json) · [Residente y recorrido anteriores](../005-mercado-character/README.md).

# Ojo articulado y montaje de armas cortas · v0.20.1

Unidad #21, parcial de #6 / CONTACT-03, sobre `687ead2` (0.20.0). Sólo pistol/revolver. No cambia la pose de culata de armas largas ni la referencia de binoculares.

## Defecto reproducido

Los valores fijos de altura y separación del montaje no acompañaban al ojo, que sí se transforma con cuello, torso, respiración y agachado. La prueba independiente del centro geométrico de la esclerótica y las superficies superiores de las miras mide 51.39 mm de separación perpendicular en neutral y 103.12 mm en cuello corto con elevación -0.30. Ambos casos fallaron antes del cambio.

## Solución

El montaje ya calcula una paleta de torso/cabeza para los hombros. Se reutiliza para transformar la referencia ocular, después del ajuste cervical. La corrección mueve el objeto rígidamente en el plano transversal al eje de las miras. Muñecas, palmas, piezas y boca acompañan el mismo marco. No cambia posiciones de manos relativas al objeto, geometría, pesos, longitudes de huesos, esqueleto o cara.

Una mezcla suave depende de apuntado, equipamiento y recarga. El desplazamiento de alineación tiene un límite de 22 cm y se aplica antes del ajuste de alcance bilateral existente: en extremos se admite error de mira antes que estirar brazos. No se añade otra evaluación de pose ni una búsqueda iterativa de alineación por actor. Hay operaciones vectoriales adicionales, no coste cero.

El retroceso usa una referencia sin el impulso angular y después gira alrededor de la empuñadura dominante. La primera propuesta desactivaba la alineación al disparar y producía una caída visible: la boca bajaba 44.53 mm. Una prueba nueva reprodujo esa regresión y el candidato se descartó. La versión integrada conserva elevación y recuperación del retroceso en lugar de volver de golpe a la postura anterior.

## Continuidad temporal y tolerancias

Las pruebas a 1/60 separan el movimiento heredado del nuevo correctivo. La animación base de levantar/equipar ya alcanzaba 63.85 mm por paso; exigir 30 mm a toda esa trayectoria no aislaba la nueva unidad. Se documentó esa comparación antes de fijar límites: total <75 mm, correctivo nuevo <15 mm por paso, recarga <30 mm. Los tests antiguos no se alteraron.

El criterio visual de neutral es <3 mm de separación entre la línea y el ojo muestreado. La matriz moderada usa cuello [-1,0,1], agachado [0,1] y elevación [-.30,0,.30], con <10 mm y contactos palmares <12 mm. El muestreo utiliza la geometría del ojo y dimensiones de los elementos visibles, no lee las constantes del correctivo para certificarse a sí mismo.

## Pruebas y evidencia

`tests/sidearm-sight.test.cjs` añade doce pruebas: alineación, referencias, matriz, transformaciones, geometría rígida, datos intactos, continuidad, retroceso y locomoción con MotionTracker. `tools/qa/sidearm_sight.js` no se empaqueta en el juego.

`tests/sidearm_sight_browser.py` utiliza el renderer real y su paleta DQ, con cámaras/tiempo preparados y almacenamiento de prueba. Produce veinte capturas y 26 comprobaciones. Se ejecuta mediante `python3 -m tools.qa.run --suite sight`. No es la prueba nativa de persistencia ni un benchmark de GPU física.

Comparación y parámetros en [qa/sidearm-sight](../../qa/sidearm-sight/README.md). Los resultados efectivos de cada commit están en Actions y los artefactos nuevos del harness. No atribuir una ejecución antigua al parche final.

## Límites deliberados

La referencia es el centro de la malla ocular, no la pupila móvil ni óptica física. No se añade seguimiento ocular, primera persona o inclinación nueva de cabeza. El modelo humano sigue estilizado, y su piel/prendas no se remodelan. No se certifica toda la autocolisión o los tránsitos de cada triángulo. Alineación de armas largas, superficies mixtas restantes y revisión artística conservan sus tareas en #5/#6.

El punto de emisión dibujado cambia junto al objeto y el sistema de disparo existente lo consulta. Las comprobaciones de oclusión desde la cámara y desde el arma, consumo de munición y daño deben seguir pasando. La versión de producto no es la del esquema de datos. Sin cambios en claves de guardado, cámara de juego, permisos, Pages, licencia o librerías externas.

## Revisión del primer intervalo al equipar (18 de septiembre)

La prueba temporal anterior empezaba después del primer paso y no comparaba con el fotograma inicial. Una nueva regresión que conserva ese fotograma detectó 76.70 mm de desplazamiento en un único paso de 1/60 al equipar y apuntar simultáneamente. No era un fallo de anclas ni de malla: la elevación de apuntado avanzaba antes que la preparación visual del equipo.

En armas cortas, el montaje mezcla la solicitud de apuntado con el cuadrado de su preparación. Esta preparación tiene una respuesta más gradual (coeficiente 6 en lugar de 11); no afecta las otras familias. No se añade estado persistente o una interpolación independiente para cada mano. El primer candidato, sin reducir la rapidez de preparación, sólo desplazaba el máximo a 43.04 mm en otro intervalo y se rechazó.

El nuevo límite de revisión es <35 mm por paso de 1/60, incluyendo el primero. La versión corregida registra 26.21 mm en el caso neutral y cumple la matriz moderada de cuello/agachado/elevación. A un segundo la postura ya supera 99% de apuntado visual. Son medidas del montaje del avatar en escenas controladas, no velocidades biomecánicas prescritas o FPS reales.

`tests/sidearm-draw-onset.test.cjs` añade cuatro casos de regresión, incluidos alcance, tiempo de preparación, disparo inmediato, contabilidad de munición, inmutabilidad de datos y familias no afectadas. La suite gráfica agrega dos comprobaciones y cinco capturas durante los primeros sesenta pasos. Mantiene las pruebas y tolerancias anteriores. La cámara y los inputs continúan respondiendo inmediatamente; el sistema de disparo sigue consultando la boca del modelo en su posición visual actual.

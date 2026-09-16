# Contacto digital con objetos del juego

Unidad parcial de issue #6, sobre master `f9998523492bf29ff276cf85c3f282d32163821a`.

## Defecto y corrección

Tres tests iniciales reprodujeron piel de los dedos dentro de los volúmenes del equipo, aunque las palmas llegaban correctamente. La flexión uniforme no contemplaba la longitud distinta de cada dedo.

El ajuste nuevo utiliza cuatro perfiles compartidos en espacio local del objeto. Encuentra el primer contacto de las falanges, después permite curvar las articulaciones distales libres. La búsqueda es acotada y sus resultados se almacenan. No se ejecuta una búsqueda por actor y fotograma.

Se corrigen los dedos medio, anular y meñique de nueve empuñaduras dominantes. Los cuatro dedos no pulgares de apoyo se ajustan en tres apoyos delanteros y seis piezas extraíbles. El índice dominante conserva su animación previa. Las palmas, muñecas, longitudes, pesos y mallas no cambian.

## Transiciones

La prueba del renderer detectó un cambio de aproximadamente 0.264 radianes en un paso al liberar una pieza. Un test a 1/60 s reprodujo el problema. Se amplió solamente la ventana visual de apertura y recuperación de los dedos ajustados, sin modificar las reglas o duraciones de la acción.

## Verificación

`tests/finger-contact.test.cjs` contiene 14 pruebas. `python3 -m tools.qa.run --suite fingers` ejecuta 15 comprobaciones del renderer y produce 12 capturas. Se utiliza la paleta DQ real y el montaje dibujado, no sólo puntos de muñeca. El helper `tools/qa/finger_surfaces.js` es exclusivamente de QA y no entra en el HTML.

Los vértices medidos tienen al menos 75% de influencia del dedo correspondiente. Las cajas son proxies de las piezas de arte; la distancia al contorno elíptico es aproximada. La tolerancia no implica exactitud anatómica ni autocolisión completa. Cámara y tiempo son preparados. El almacenamiento es fixture; la persistencia nativa HTTP se comprueba aparte.

## Límites

Pulgar y oposición de su base no se modifican. Su exploración no produjo una solución convincente sólo con rotación y se reserva para otra unidad. Tampoco se garantiza contacto entre manos, todos los espacios interdigitales, piezas decorativas o todas las superficies en tránsito. Puede haber intersecciones residuales.

Se conservan las correcciones de mangas y codos ópticos anteriores. No cambia el esquema de partidas, no hay dependencias nuevas de runtime ni pretensión de calidad AAA. #5, #6 y #7 siguen abiertos por sus criterios restantes. Revertir esta unidad no requiere migrar datos.

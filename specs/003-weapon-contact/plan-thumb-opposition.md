# Unidad de oposición del pulgar · issue #6

Base: `71fd53aed765bdb1d450ecba274bd2fd5522026c`. Estado: implementación y verificación en curso.

## Defecto reproducido

Tres pruebas de piel cuantizada/DQ fallan sobre master: pulgar dominante dentro del agarre, apoyo dentro del guardamanos y apoyo dentro de pieza extraíble. Las muestras peores están ligadas a thumb1/thumb2, no a la muñeca. Las longitudes e influencias de los otros dedos no causan este fallo. Una rotación limitada alrededor del root antiguo deja parte de su envolvente dentro del objeto.

## Hipótesis y cambio acotado

El rig no distingue el movimiento de oposición de la base del pulgar de la flexión de sus tres segmentos. Añadir un pivote virtual metacarpal fijo relativo a la muñeca y una rotación acotada, sólo para los perfiles de contacto cubiertos. Recalcular la cadena desde la muñeca definitiva tras el IK. No añadir huesos, cambiar su longitud, mover el ancla palmar, regenerar la malla o cambiar el inventario.

Los perfiles son referencias de animación del avatar ficticio, no datos médicos. Se obtuvieron con una búsqueda offline limitada de rotación/oposición que penaliza penetración de piel y separación distal. En runtime son cuatro constantes reutilizadas, no una optimización por fotograma. La base se combina gradualmente con las fases de recarga. El modo sin contacto conserva exactamente su comportamiento anterior.

## Aceptación

- [ ] Piel muestreada de pulgar fuera de los cuatro proxies revisados, manteniendo cercanía (<9 mm) y tolerancia de penetración existente (<3 mm).
- [ ] Longitud de cada falange constante, matrices no digitales y anclas palmares sin cambios.
- [ ] Los otros dedos conservan PR #15 y su transición de índice, y óptica conserva PR #13.
- [ ] Recarga a 60 pasos/s sin salto del extremo del pulgar ni modificación del inventario.
- [ ] Capturas antes/después con mismos parámetros y revisión de la unión a la palma, no sólo distancias.
- [ ] CI y datos HTTP nativos aprobados antes de integrar. Pages coincide con la salida versionada.

## Límites y reversión

No es autocolisión de toda la mano, no incluye mano-mano ni todas las superficies decorativas. Dejar #5/#6/#7 abiertos por sus requisitos pendientes. Revertir esta unidad no necesita migrar partidas. No publicar una versión numerada ficticia para un cambio parcial.

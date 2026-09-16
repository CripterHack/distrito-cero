# Oposición del pulgar en contactos del avatar

Unidad de #6 sobre `71fd53a` (PR #15). No es una versión nueva del juego ni un modelo anatómico clínico.

## Causa y alcance

La flexión anterior actuaba alrededor de tres segmentos pero no distinguía la oposición de la base. Las muestras peores estaban influidas por thumb1/thumb2 y penetraban los proxies de arte aunque muñeca y palma alcanzaran sus anclas. Tres pruebas de superficie reprodujeron el defecto antes de modificar fuentes.

Se añade un pivote virtual metacarpal, fijo respecto de la muñeca. Su rotación desplaza y orienta el arranque de la cadena; las tres falanges mantienen sus longitudes. El sistema no añade huesos ni estira dedos. Se recalcula tras el IK de la mano definitiva. No cambia malla, pesos, las anclas palmares, los otros dedos, el inventario o las reglas de recarga.

Cuatro referencias offline cubren nueve empuñaduras dominantes, tres apoyos delanteros y seis piezas extraíbles. `tools/qa/calibrate_thumb.cjs` conserva la búsqueda acotada de diagnóstico sobre piel DQ y proxies. El runtime usa las referencias constantes de `weapon-handling.js`, sin búsqueda nueva por fotograma. La oposición se combina gradualmente con las fases existentes de recarga.

La primera propuesta eliminaba intersecciones con los objetos pero acercaba demasiado el pulgar a otros dedos. Una regresión de envolventes digitales rechazó esa propuesta. La calibración posterior incluye esa restricción. No se presenta como colisión física de cada triángulo.

## Verificación reproducible

`node --test tests/thumb-contact.test.cjs` ejecuta once pruebas: contactos reales muestreados, envolventes respecto a los otros dedos, variantes de postura y objetos, continuidad a 1/60 s, rig, valores inválidos, preservación de óptica/objetos de contacto y ausencia de mutación. Las catorce regresiones previas de falanges se conservan. Su antiguo literal de flexión del pulgar se reemplaza por independencia respecto del disparo: este cambio sí modifica intencionalmente esa pose.

`python3 -m tools.qa.run --suite thumbs` ejecuta quince comprobaciones sobre el renderizador real. Las capturas usan tiempo y cámara preparados y almacenamiento fixture. La prueba de recarga parte de apuntado ya asentado para no confundir el movimiento de equipar/apuntar con discontinuidad digital. Su primera configuración mezclaba esas dos acciones; el caso independiente de recarga Node pasó antes de ajustar el fixture. El perfil HTTP nativo se valida aparte.

## Limitaciones

La distancia a la sección elíptica del agarre es aproximada. La prueba principal muestrea vértices con al menos 75% de peso del pulgar y una envolvente simplificada frente a otros dedos. No es autocolisión general, aprobación artística de todas las manos o verificación exhaustiva de espacios interdigitales. La unión a la palma sigue usando los pesos DQ existentes.

Los binoculares, objetos de contacto y granadas no reciben una nueva pose de pulgar. Mano-mano, coordinación ojo/mira, prendas, pelo y diversidad corporal conservan trabajo pendiente. La malla no se retoca para ocultar las intersecciones. No se anuncia física de tejidos, mocap o calidad AAA. #5/#6/#7 permanecen abiertos.

Rollback: revertir la unidad sin migrar partidas. No se modifica SOURCE-MANIFEST ni evidencia histórica. Revisar PR y runs del hash exacto antes de afirmar publicación o aprobación de CI.

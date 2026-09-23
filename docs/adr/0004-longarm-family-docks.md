# ADR 0004 · Referencias por familia para armas largas

Fecha: 2026-09-23. Refs #6, SPEC-003. Amplía [ADR 0003](0003-rifle-surface-dock.md) a SMG, escopeta y sniper. Es una decisión de arte y presentación de objetos ficticios dentro de la continuación autónoma solicitada, no ingeniería de armamento.

## Decisión e invariantes

Se reutiliza el montaje único y el apoyo de chaqueta verificado del rifle. Los perfiles declaran explícitamente su mira abierta o tubular. Sniper conserva su eje horizontal y altura óptica, no reutiliza la pendiente de la mira abierta. La escopeta mantiene su palma inferior y la secuencia de recarga por puerto. El rifle conserva sus coordenadas, geometría y filtro `rifleAim`.

SMG y escopeta reciben una culata cosmética reducida, equivalente a la familia de miras abiertas ya revisada. Sniper tiene un perfil de culata desplazado verticalmente respecto a esa variante para corresponder a su óptica. Se conservan los extremos posteriores, miras, agarres, apoyos delanteros y cargadores. Los triángulos completos de cada variante se validan de forma independiente, incluidos controles que rechazan usar la variante de mira abierta como geometría de sniper.

La referencia heredada de articulación permanece visible como `legacyStockError`, pero no se presenta como apoyo de superficie. El observador lee el triángulo 8898 de la chaqueta y deforma sus vértices con la paleta recibida. La cohorte de cara/cuello y chaqueta no se reduce. No se escalan rostro, extremidades o vestuario. El recurso humano y el rig de 49 huesos no cambian.

Las tres nuevas familias utilizan `longarmAim`, un filtro transitorio con la misma dinámica ya existente. No entra al serializador ni modifica munición, duración de acciones, trigger o estado persistente. La preparación de pruebas estáticas asienta explícitamente el filtro. Las pruebas de ciclo lo dejan evolucionar mediante `equipmentStep`, no asignan la pose final.

## Contrato de aceptación

Se mantienen ojo <10 mm, apoyo <30 mm, palmas <12 mm, variación de segmentos <1e-6 m, mira delante del ojo >50 mm y penetración muestreada <=2 mm. Los nuevos casos abarcan 54 combinaciones centrales y las transiciones nativas de las tres familias. La batería gráfica existente pasa de exigir aceptación estática sólo en rifle a exigirla en las cuatro familias, sin retirar las observaciones del ciclo.

Las dos pruebas que exigían el pivote antiguo en SMG se conservan sobre Gauss, que mantiene ese contrato. Las tres familias nuevas salen de la prueba que exige un apuntado inalterado porque ahora tienen filtro propio. Su comportamiento se sustituye por pruebas de asentamiento, bajada, recarga y continuidad, no por skips. No cambia el patrón completo de CI.

## Alcance y reversión

Versión de producto 0.20.3, canal prototype. Mismos esquemas de datos. Revertir fuentes y salidas HTML/GLB juntas, sin migrar ni borrar partidas. No se aprueban todos los cuerpos, ángulos extremos, colisiones continuas, FPS físicos ni calidad artística global por estas comprobaciones. #5 y #7 tienen criterios separados. El cierre total de #6 requiere revisar sus restantes criterios además de esta unidad.

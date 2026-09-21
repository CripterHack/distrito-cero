# ADR 0003 · Apoyo superficial y silueta cosmética del rifle

Fecha: 2026-09-21. Alcance: #29, PR #30, v0.20.2. Decisión de implementación dentro de la continuación autónoma solicitada. Revisión propia, no aprobación artística independiente. Sustituye únicamente el contrato de apoyo del rifle, no los límites de aceptación ni el montaje compartido.

## Problema

La referencia heredada era `upperArmR + [0.010,-0.040,0.024]` en coordenadas del actor. El caso neutral daba 6.18 mm a ese punto pero penetraba 15.53 mm en la chaqueta y tenía 238.64 mm de error ocular. Un punto de articulación no representa una superficie. Las variantes A/B/C que optimizaban esa distancia forzaban anatomía, invadían superficies o rompían la continuidad. Se conservan en [el informe anterior](../../specs/003-weapon-contact/stock-surface-rejection.md).

La combinación de ese punto bajo/lateral y los dos bloques altos de la culata dejaba poco espacio entre cara y prenda. Se cambia la autoría cosmética antes de aceptar una postura forzada. No se afirma que todas las alternativas con la geometría antigua sean imposibles.

## Decisión

El rifle utiliza el centro del triángulo 8898 de la chaqueta canónica, vértices 26694–26696. QA lee sus bytes y pesos, verifica que corresponden al pecho y aplica forma, ajuste cervical y DQ con la paleta realmente dibujada. El runtime conserva tres puntos de bind equivalentes para evitar decodificar el recurso por fotograma. Los tests contrastan ambas rutas y modifican la paleta suministrada como control negativo.

La referencia del objeto es el punto más cercano sobre la cara posterior del apoyo, cuyos límites se verifican contra la geometría. Se conserva `legacyStockError`, que muestra explícitamente la distancia a la referencia antigua. No se etiqueta como cumplimiento del contrato de articulación anterior.

Se remodelan sólo los dos cuboides de culata del rifle. Se conserva el extremo posterior, las miras, el agarre dominante, el apoyo de la mano libre, el cargador y el resto del catálogo. No cambian recurso humano, huesos, longitudes, pesos, UV, reglas, cámara, munición ni formatos persistentes. El GLB es regenerado con el exportador existente.

La alineación ocular fija la colocación transversal. La referencia de prenda determina la distancia longitudinal. La proyección existente de alcance de ambas manos mantiene prioridad en elevaciones extremas. Torso y clavículas reciben incrementos moderados, la cabeza utiliza los límites cervicales ya existentes. El filtro de presentación del rifle y la liberación gradual durante recarga evitan saltos. No se añade otro solver ni se escribe la simulación desde el renderer.

## Límites que no se relajan

Ojo <10 mm, separación de apoyo <30 mm, palmas <12 mm, variación de segmentos <1e-6 m, mira delante del ojo >50 mm y penetración muestreada <=2 mm. La separación neutral de 10 mm no equivale a contacto físico perfecto. La cohorte de cara/cuello y chaqueta sigue completa, con sus controles de rechazo. Los volúmenes de QA se actualizan para coincidir con las piezas realmente dibujadas, no para reducir un defecto sin cambiar el producto.

Dos tests del contrato antiguo pasan a la SMG, que conserva ese contrato. El rifle se prueba contra la prenda mediante la nueva referencia independiente. Se retira del caso que exige una presentación inalterada porque ahora tiene filtro propio, cubierto por el ciclo nativo de elevación, bajada y recarga. Se conserva el patrón completo `tests/*.test.cjs`, la aceptación original del rifle y sus diez tests de rechazo de superficies. No hay skips ni supresión de errores.

## Coste, alcance y reversión

La geometría cosmética y el significado de la distancia de apoyo cambian y por eso la versión sube a 0.20.2. No es una corrección puramente numérica ni una aprobación de todas las armas largas. Permanecen #5/#6/#7, anatomías/elevaciones extremas, autocolisión completa, movimiento emergente y GPU física. Revertir el cambio con su HTML y GLB asociados, sin migrar ni borrar partidas.

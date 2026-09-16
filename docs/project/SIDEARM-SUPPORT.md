# Contacto entre manos en armas cortas

Unidad parcial de #6 sobre `e614ff98061b9454eb47680bea7875a745373f3b`, posterior al correctivo de Actions #17. No constituye aprobación artística de #5 ni cierre de #6.

## Defecto

La mano de apoyo utilizaba una flexión genérica, como si sujetase otro objeto aislado. Con pistola o revólver, su índice/medio/anular podían cruzar los dedos de la mano dominante. También había penetración de la piel de apoyo en el mango. Dos regresiones de piel reprodujeron ambos problemas antes del cambio.

El diagnóstico mide vértices reales de la malla cuantizada frente a envolventes segmentadas de los dedos opuestos. Se evalúan ambas direcciones (izquierda contra derecha y derecha contra izquierda) y el volumen del objeto, no sólo la distancia entre muñecas.

## Solución acotada

Una postura de apoyo precalculada para pistola/revólver considera ambas manos y el objeto. Mantiene las posiciones de palmas y muñecas y sólo cambia flexión/oposición de los dedos de apoyo. No se modifican malla, pesos, 49 huesos, longitudes, campos de partida, munición o reglas de uso. No hay búsqueda nueva por fotograma ni entradas nuevas en la caché de cuatro perfiles anterior.

La primera calibración funcionaba al apuntar pero cruzaba el índice dominante al ejecutar su gesto de disparo. La matriz de autoría se amplió a reposo, transición y flexión completa de ese índice. Una prueba de recarga a 1/60 s detectó además una recuperación demasiado brusca: se amplió exclusivamente la ventana visual de retorno en armas cortas, sin cambiar tiempos o transferencia de munición. No se relajaron umbrales para aceptar el cambio.

Las familias largas, Gauss/EMP, binoculares y herramientas conservan sus referencias anteriores. La mano de apoyo interpola hacia la manipulación existente durante la recarga y vuelve a la nueva postura de apoyo. No se introduce otra fuente de estado del arma.

## Pruebas y herramientas

`tests/sidearm-support.test.cjs`: nueve pruebas de penetración, contacto cercano, disparo/agachado/movimiento, transformaciones, longitudes, datos, cambio de equipo y continuidad de recarga. `tests/sidearm_support_browser.py`: veinte comprobaciones con paleta DQ y montaje del renderizador real, seis poses estáticas y fases temporales. La suite se integra con `python3 -m tools.qa.run --suite sidearms`.

`tools/qa/hand_support_surfaces.js` es sólo QA. Su distancia es aproximada: radios de envolvente por segmento y vértices con al menos 75% de influencia digital. Las zonas mixtas de palma/pulgar no están cubiertas completamente. La tolerancia no certifica toda la malla ni colisión física.

`node tools/qa/calibrate_sidearm.cjs` reproduce el estudio offline acotado con semilla fija. Es una herramienta artística, no parte del runtime. Los resultados sin redondear se escriben en `artifacts/sidearm-calibration/` y no se publican como partidas.

## Estado de Actions y límites

El PR #17 se integró como `e614ff9`. La nueva CI de master [35051259999](https://github.com/CripterHack/distrito-cero/actions/runs/35051259999), el benchmark [35051260032](https://github.com/CripterHack/distrito-cero/actions/runs/35051260032) y Pages finalizaron correctamente. Los cinco runs rojos históricos no fueron eliminados ni relabelados. El nuevo cambio requiere sus propios checks antes de integrarse.

Las capturas usan cámara y reloj preparados; no son FPS reales ni una aventura completa. Las pruebas de guardado HTTP nativo son independientes del almacenamiento fixture gráfico. La anatomía de manos, unión palma/pulgar y superficies próximas siguen simplificadas. No hay autocolisión general, nuevos modelos ni alineación ojo/mira completa.

Reversión sin migrar guardados. No cambia la configuración de Pages ni agrega librerías de runtime. Consultar el PR y el hash de cada ejecución para resultados efectivos, no inferirlos de la existencia de esta documentación.

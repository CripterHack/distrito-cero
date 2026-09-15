# Distrito Cero · Horizonte v0.7 · Verificación

11 de septiembre de 2026. Base recuperada: fuentes de v0.5. Esta es una expansión del mundo, no una recuperación del código incompleto de v0.6 ni una certificación AAA.

## Resultados actuales

| Grupo | Comprobaciones satisfactorias | Fallos finales |
| :--- | ---: | ---: |
| Lógica con Node, incluidas regresiones y mundo procedural | 125 | 0 |
| Atlas, sectores, seed, importación, teclado y controles táctiles | 84 | 0 |
| Campaña, conducción e interfaz heredadas ejecutadas en v0.7 | 52 | 0 |
| Bucle de render y simulación sin sustituciones | 10 | 0 |

**146 comprobaciones de navegador**, además de las 125 de lógica. Son aserciones, no 146 sesiones independientes ni cobertura de todas las combinaciones de mundo abierto. No se han sumado resultados históricos de v0.5 o v0.4.

Se capturaron cinco entornos con Chromium y WebGL, uno por contexto de revisión. Todos terminaron con `gl.getError() === 0` y sin excepciones JavaScript. Las suites finales no registraron solicitudes de recursos externos. Los datos y la huella del HTML están en `qa/v07/release-report.json`.

## Mundo y coherencia

La lógica comprueba determinismo por semilla/coordenada, semillas diferentes, estabilidad de la geometría al reconstruir un sector descartado, coordenadas negativas, carreteras coincidentes entre vecinos y edificios fuera de los corredores viales. Se recorrieron por consulta 240 sectores dispersos para verificar cachés de 64 sectores y 768 parcelas, y 180 sectores intermedios antes de volver al primero.

Se verifican los cinco estilos iniciales, rutas conectadas de nodos adyacentes y cálculo de un tramo acotado hacia un destino a 100 millones de metros. No se generó ese recorrido completo. La prueba de renderer prepara una posición a 20 millones de metros para comprobar origen relativo, proyección finita y ausencia de error GL. No equivale a conducir físicamente esa distancia ni a demostrar precisión para cada posible coordenada.

Los cambios de objetos externos se conservan al salir, volver y restaurar un guardado. Se prueba importación de guardados anteriores, recuperación de otra semilla, rechazo de datos corruptos sin cambiar la semilla original y cobro único de una entrega regional.

## Lo que se probó en el navegador

La suite del atlas inicia el HTML, usa teclas reales y eventos táctiles emulados, selecciona destinos, marca un GPS fuera del límite antiguo, modifica zoom y semilla con confirmación, cambia la iluminación y verifica el rechazo de un viaje bajo persecución. Comprueba acceso de botones en 390 × 844 y 844 × 390.

Para aislar las verificaciones de estado del coste de SwiftShader, la suite del atlas detiene sólo renderer y cámara entre fotogramas explícitamente dibujados. No reemplaza la lógica de simulación. Los encuadres de inspección de entornos son estados preparados en modo foto y no se presentan como recorridos espontáneos.

La suite continua mantiene los métodos originales de render, cámara y paso de simulación. Parte de dos posiciones preparadas, conduce mediante teclado, supera el borde original de la ciudad y atraviesa un límite de sector. Confirma cambio de generación, recambio de buffers, llenado de los 25 sectores, mapa, viaje permitido después de frenar y ausencia de errores.

La regresión de campaña recorre llamada, coche, recogida, refugio, transmisión y desenlace público. Comprueba conducción, freno, mapa, guardado/continuación, un encargo con recompensa y los controles táctiles heredados.

## Revisión visual y correcciones

Se inspeccionaron capturas reales de ciudad, distrito futurista, barrio retro, pueblo y cultivos. Una cámara de revisión inicialmente quedó dentro de una construcción: se recolocó en el corredor vial antes de volver a capturar.

Los nuevos planos de terreno, muy cercanos al asfalto, revelaron una pérdida de precisión del depth buffer heredado de 16 bits, visible como franjas verdes/parpadeo sobre las calles. Se comprobó el formato real del renderbuffer, se añadió la aserción que fallaba y se cambió a profundidad de 24 bits. El terreno superficial también se recorta para no quedar debajo de la calzada. Las capturas finales muestran la corrección.

## Incidencias del laboratorio

La navegación HTTP a localhost devolvió `ERR_BLOCKED_BY_ADMINISTRATOR`. Las pruebas, como las versiones anteriores, cargan el HTML mediante `set_content`. El almacenamiento se proporciona con un objeto aislado en memoria porque esa página no tiene un origen normal. Por ello no se afirma haber verificado persistencia nativa entre aperturas de `file://`.

Las primeras ejecuciones a mayor tamaño, acumulando varias capturas y contextos SwiftShader, agotaron el límite del proceso. No se cuentan como pases. La suite funcional final utiliza 900 × 640 en escritorio y los dos tamaños móviles. Las capturas de revisión se aislaron en un contexto nuevo por entorno, a 1120 × 720 y calidad equilibrada. La suite continua usa 640 × 420 y calidad económica. Las ejecuciones finales cerraron su navegador normalmente.

La primera pasada de la regresión heredada esperaba desplazamiento tras un tiempo fijo de pared y falló bajo la carga gráfica inicial. Se sustituyeron esas esperas por el estado esperado con timeout, conservando la pulsación real y las mismas aserciones de movimiento, aceleración y dirección. La suite final completó sus 52 comprobaciones.

## Límites de cobertura y del producto

Entorno: Chromium 144.0.7559.96 en Linux, Xvfb, ANGLE SwiftShader. No se probaron Safari, Firefox, teléfonos físicos, GPUs del usuario, sesiones de varias horas, despliegue público ni recuperación de pérdida del contexto gráfico. No se promete un FPS ni rendimiento de hardware a partir del laboratorio.

El territorio transitable es plano, con retícula ortogonal, variación de centros y transiciones de usos. No hay ríos regionales ni topografía física. El generador usa un dominio numérico finito enorme, no infinito matemático. La memoria geométrica activa está acotada, pero la generación se hace en el hilo principal por lotes y puede causar tirones en equipo lento. La persistencia exterior tiene un límite explícito de 4096 objetos modificados y 2048 centros registrados.

Se mantienen los modelos y animaciones de v0.5. No se afirma haber mejorado a los NPCs hasta fotorrealismo ni integrado la extracción de conductores. Esas tareas siguen separadas en `docs/v07/CONTINUIDAD.md`.

## Reproducir

```bash
python build.py
node --test tests/*.test.cjs
DISPLAY=:99 python tests/horizon_browser.py
DISPLAY=:99 python tests/horizon_continuous.py
DISPLAY=:99 python tests/legacy_horizon.py
DISPLAY=:99 python tests/horizon_capture.py future
DISPLAY=:99 python tests/horizon_capture.py retro
DISPLAY=:99 python tests/horizon_capture.py village
DISPLAY=:99 python tests/horizon_capture.py farmland
DISPLAY=:99 python tests/horizon_capture.py home
```

Playwright y Chromium se utilizan sólo para desarrollo. El juego sigue siendo un HTML sin dependencias externas.

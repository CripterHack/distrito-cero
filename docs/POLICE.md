# Policía e interacciones · v0.3

## Qué causaba el bloqueo

`vehicleContacts()` multiplicaba la velocidad del jugador por 0.91 en cada contacto, incluso si ambos coches se desplazaban juntos o ya se separaban. La IA perseguía el centro del jugador y omitía su coche al frenar ante obstáculos. La combinación producía contacto permanente y pérdida de aceleración. La captura a pie, además, consultaba una propiedad `speed` que el personaje no tenía y usaba cero como sustituto. La proximidad para capturar no exigía visión directa.

## Corrección

La huella del vehículo es un rectángulo orientado de 2 × 4.46 metros. El test SAT obtiene la normal y la penetración. La corrección de posición se realiza con `world.move()` para respetar los edificios. La respuesta de velocidad aplica un impulso solo a la componente normal que está cerrando el contacto. Un roce tangencial o una separación no reduce arbitrariamente la velocidad. El contacto exacto entre centros tiene una normal determinista, no se ignora.

La resolución incluye pares próximos de tráfico y patrullas, no solo el coche del jugador. El registro de contactos limita los daños repetidos y se limpia después de tres segundos sin contacto. Los impactos iniciados por una patrulla contra un jugador detenido no suben su nivel de búsqueda. Embestir voluntariamente conserva sus consecuencias.

La IA frena con una separación de seguimiento, tiene en cuenta el coche del jugador al evitar obstáculos y ejecuta una maniobra breve de recuperación tras el contacto. La recuperación usa desplazamiento físico normal. No teletransporta patrullas ni desactiva sus colisiones.

## Captura y rendición

La captura exige proximidad, visibilidad y velocidad baja. A pie se mide el desplazamiento real antes de los impulsos externos, no la velocidad deseada de la animación. Correr contra una pared no cuenta como escapar. Moverse o romper la visibilidad reduce el medidor.

Mantener **R**, o mantener pulsado el botón de rendición, permite terminar voluntariamente un encuentro cerca de una patrulla visible y con el personaje o coche detenidos. Soltar, intentar moverse, cancelar el puntero, cambiar a un menú o perder el foco cancela la rendición. No hay un cargo por una rendición incompleta.

| Ajuste | Valor |
| --- | --- |
| Captura estando detenido en coche | 6 segundos continuos desde medidor vacío |
| Captura estando detenido a pie | 4.5 segundos continuos desde medidor vacío |
| Umbral de velocidad de captura en coche | 1.15 m/s |
| Umbral a pie | 0.65 m/s |
| Distancia máxima de captura en coche / a pie | 7.2 m / 3.6 m, con visión |
| Ventana sin acumulación de captura tras un contacto policial elegible | 1.6 s |
| Maniobra de recuperación de la patrulla | 1.25 s |
| Intervalo mínimo entre recuperaciones de una patrulla | 3 s |
| Distancia máxima para rendirse | 18 m, con visión |
| Tiempo de pulsación para rendirse | 1.8 s |
| Costo base de rendición / arresto | $150 / $300 del juego |
| Espera tras perder contacto antes de reducir búsqueda | 6 s |
| Reducción de alerta durante ocultación | 3.2 puntos por segundo |

Los costos no dejan el saldo negativo. La rendición y el arresto conservan el capítulo, pero cancelan el encargo temporal y la transmisión en curso. La barra puede conservar progreso parcial de una inmovilización previa mientras se reduce.

## Búsqueda

Un incidente reportado proporciona una posición inicial. El contacto visual actualiza `policeState.lastSeen`. Al perder contacto, las rutas usan esa posición conocida y calles próximas. No se consultan nuevas coordenadas ocultas para trazar una ruta hacia el jugador. La percepción sigue pudiendo detectarlo si entra de nuevo en la línea de visión de una patrulla.

El HUD diferencia persecución, búsqueda, captura y rendición. El mapa marca el último contacto. El contador de ocultación es una estimación que se reinicia si vuelven a verte o se reporta otro incidente. Las patrullas comparten la última observación, como una radio de despacho simplificada.

## Arquitectura y límites

`src/police.js` contiene geometría y constantes ajustables en `DC.POLICE`. `src/simulation.js` conserva la autoridad del estado. `src/app.js` solo comunica entradas y presenta información. Los modelos y animaciones del personaje de v0.2 no se sustituyen.

Se mantiene el formato de guardado `version: 1`. La carga reinicia medidores y contactos transitorios, conservando historia, dinero, alerta y vehículo. Exporta la partida antes de cambiar de archivo, pues la disponibilidad del almacenamiento local depende del navegador y del origen.

Sigue siendo una simulación arcade. No incluye agentes policiales a pie, negociación dialogada, combate armado, una física de chasis completa ni garantía de escapar de cualquier encierro. La corrección elimina el frenado artificial y da opciones de maniobra, no invulnerabilidad. Rodearse de vehículos y edificios todavía puede acabar en captura.

## Pruebas

`tests/police.test.cjs` añade 32 casos de regresión, incluido contacto frontal, trasero y lateral, dos patrullas en ambos extremos, diferentes pasos de simulación, colisión entre patrullas, visión, captura en movimiento, rendición, rutas sin información oculta y compatibilidad de guardado.

`tests/police_browser.py` verifica entradas reales, cambios del HUD, rendición con ratón y tacto, cancelación de gestos, búsqueda, recuperación visual del sospechoso y disposición en 1280 × 800, 390 × 844 y 844 × 390.

`tests/police_continuous.py` mantiene el renderizador y la simulación reales durante una maniobra con contacto policial. Los detalles y límites están en `docs/QA.md`.

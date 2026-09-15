# Horizonte · implementación v0.7

## Base y objetivo
Fuente recuperada: ZIP de v0.5. Los directorios de v0.6 accesibles contienen imágenes, no fuentes ejecutables. Se conserva la base recuperable. No se etiqueta la entrega como AAA ni como recuperación de v0.6.

Construir una expansión procedural continua fuera de los 840 m centrales. Una misma semilla y coordenada debe generar siempre la misma parcela. La ciudad original y sus misiones conservan posiciones. No habrá un borde jugable diseñado: los sectores se crean según avance el jugador, con límites numéricos explícitos.

## Diseño
- Sectores de 336 m, parcelas de 84 m, centros regionales espaciados con variación reproducible.
- Jerarquía de usos: centros contemporáneos, tecnológicos o patrimoniales, periferia, núcleos rurales, cultivos y arbolado. No asignar edificios arbitrarios aislados en cada celda.
- Carreteras arteriales compartidas cada 336 m. Calles secundarias según ambos vecinos. Parcelas y accesos respetan estos corredores.
- Generación pura sin WebGL. Caché CPU acotada y vecindario GPU descargable. Coordenadas GPU relativas a la cámara, no floats globales.
- Props y cambios persistentes por identificadores. Geometría base regenerada, no guardada. Persistencia modificada con presupuesto y aviso.
- Atlas regional, semilla editable, destinos de demostración y viaje bloqueado bajo búsqueda, encargo o transición. El usuario puede seguir conduciendo entre zonas.
- Tráfico local reutilizable sin teletransportar vehículos visibles ni coches que persiguen. Misiones del centro se mantienen. Encargos regionales fuera del centro.

## Unidades de trabajo
1. Pruebas fallidas de determinismo, vecindades, caminos, cobertura de zonas, coordenadas negativas y límites de caché.
2. `frontier-world.js`: generador, clasificación, rutas y consultas espaciales.
3. `frontier-simulation.js`: carga de props, tráfico, guardado y viaje.
4. `frontier-renderer.js`: sectores con edificios, caminos, huertas, señalización, almacenamiento GPU acotado.
5. `renderer.js`: origen relativo, día/noche, luz consistente. `frontier-ui.js`: atlas y controles accesibles.
6. Regresión heredada, cruce continuo de sector y antiguo límite, importación, viaje cancelable, capturas reales de cinco entornos y emulación móvil.

## Criterios de entrega
HTML autónomo, sin recursos de red durante juego. Mapa no anuncia contenido ya generado sin comprobarlo. Cambios de semilla no contaminan una partida. Memoria geométrica acotada incluso después de recorrer muchas regiones. Las cifras de pruebas son las ejecutadas en esta versión.

## Límites deliberados
No se promete infinito matemático, ni paisajes únicos para siempre, ni streaming asíncrono en segundo plano. Mundo práctico de coordenadas entre -10^9 y +10^9 m. Terreno transitable plano: montaña física, erosión, ríos regionales e interiores quedan pendientes. Animación facial fotorrealista y la secuencia de extracción de conductor de v0.6 no se consideran recuperadas.

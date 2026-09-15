# Distrito Cero · Plan integral de evolución

Fecha: 9 de septiembre de 2026. Base: v0.3. Entrega incremental prevista: v0.4, Ciudad reactiva.

## Objetivo y límites no negociables

Convertir la ciudad decorativa en un espacio con objetos persistentes, colisiones legibles, interacciones reutilizables y consecuencias mecánicas. Conservar campaña, guardados anteriores, conducción, controles táctiles y la corrección de contacto policial. El runtime seguirá siendo JavaScript y WebGL2 nativos, sin CDN, motor externo, instalación ni conexión obligatoria. Un HTML autónomo y fuentes separadas.

El objetivo artístico a largo plazo es el realismo. La entrega v0.4 no se presentará como hiperrealismo cinematográfico, simulación de carrocería deformable ni captura de movimiento. Un render de Blender no equivale a una captura del juego. Cada recurso tendrá procedencia, formato, coste geométrico y estado de integración documentados.

## Diagnóstico de la base

Los postes, árboles y mobiliario se dibujan en buffers estáticos y no participan en la simulación. Los impactos reducen un número de salud y no identifican qué pieza recibió el golpe. La locomoción mueve instantáneamente al personaje aunque el ciclo visual interpola velocidad. Los neumáticos no utilizan todavía el ángulo de rueda acumulado. La entrada al coche cambia instantáneamente el actor. Estos son los puntos de mayor impacto inmediato, antes de multiplicar misiones o ampliar la ciudad.

## Arquitectura de la actualización

- `src/dynamics.js`: definiciones de materiales, hash espacial, daño localizado, objetos móviles, caída por bisagra, partículas y huellas con límites estrictos. Estado por partida, nunca en el mundo compartido.
- `src/interactions.js`: extensión de la simulación, contexto de recoger, lanzar, empujar, reparar y restaurar, movimiento suavizado, reacción corporal y transición visual de vehículos.
- `src/vehicle-asset.js`: geometría original preparada en Higgsfield/Blender y convertida al formato nativo. No es una biblioteca ni necesita un cargador remoto.
- `src/renderer.js`, `src/reactive-renderer.js`: instancias de objetos dinámicos, piezas de carrocería, humo, cristales, suspensión, ruedas y poses corporales. No decide salud ni premios.
- `src/app.js`, `page.html`, `style.css`: acciones de teclado y táctiles, telemetría contextual sin cubrir el centro del juego.
- `tools/convert_vehicle.py`: convierte el subconjunto geométrico extraído a buffers nativos. El GLB completo y la escena editable quedan en Higgsfield, con enlaces de procedencia en `assets/README.md`. No es un importador glTF general.
- `tests/dynamics.test.cjs` y `tests/reactive_browser.py`: lógica determinista, integración, controles reales y capturas con WebGL.

## Orden de ejecución y criterios de aceptación

### 1. Seguridad de regresión y recursos

Ejecutar la batería heredada, conservar copias de v0.3, crear pruebas nuevas antes de implementar. Generar un coupé original en Higgsfield con piezas semánticas, escala métrica y materiales portables. Inspeccionar el render, validar y convertir el GLB. No utilizar un modelo descargado cuyo permiso de redistribución sea desconocido.

Aceptación: las partidas previas se importan. HTML sin solicitudes externas. Cambios desacoplados del controlador policial. Modelo descargable y procedencia real registrada.

### 2. Ciudad reactiva

Postes con bisagra y apagado al romperse. Árboles con tronco sólido y caída. Cajas, botes y conos con masa y rebote. Bancas como obstáculos bajos. Umbrales de resistencia por material. Un mismo roce sostenido no debe aplicar un impacto nuevo en cada fotograma. Las posiciones de los objetos deben conservarse al exportar una partida.

Aceptación: atravesar la posición de un poste intacto no es posible. Un impacto suficientemente fuerte lo derriba, apaga su luz y genera fragmentos. La caída llega a reposo. Una nueva partida reconstruye el entorno. Límite de partículas y residuos independiente del tiempo jugado. Sin recompensas por destruir árboles.

### 3. Autos con consecuencias visibles

Daño frontal, posterior y lateral. Piezas se hunden o desalinean visualmente, cristales dañados, faros afectados y humo con deterioro elevado. Balanceo de suspensión e impulso breve al chocar. Ruedas giran con distancia recorrida y dirección. Reducción moderada y explícita de prestaciones, sin volver a inmovilizar al jugador por un roce policial.

Aceptación: impactos opuestos dañan zonas distintas. Estar tocando un auto sin velocidad relativa no acumula daño. Reparar restablece tanto salud como aspecto. Maniobra de escape policial sigue funcionando. No se promete soft-body: deformación visual paramétrica y respuesta de cuerpo rígido simplificada.

### 4. Interacciones y personaje

Recoger y soltar objetos pequeños, lanzarlos, empujar mobiliario y vehículos parados, reparar junto al coche con progreso cancelable. Agacharse y esquivar. Aceleración/desaceleración con velocidad real. Reacción de impacto y recuperación, salto sin repetición por mantener la tecla, transición visual de puerta y ocupante. Contexto con distancia y visibilidad, sin acciones a través de paredes.

Aceptación: el objeto no se duplica, la reparación se cobra una sola vez y se cancela al alejarse. Las animaciones no sustituyen la física. La transición visual de entrada es breve. En v0.4 el cambio lógico de actor permanece inmediato para no bloquear la huida. El bloqueo sincronizado con manos, puerta y asiento se reserva al controlador posterior. Las acciones se alcanzan también con botones táctiles.

### 5. Juego y lectura

Distribuir un pequeño conjunto de objetos interactivos cerca del inicio, sin bloquear la llamada ni el coche. Mostrar el nombre de la acción y el estado del vehículo. Consecuencias policiales limitadas y relacionadas con incidentes, no con mantener contacto. Posibilidad de restaurar mobiliario para recuperar calles transitables. Mantener misiones existentes y libertad de exploración.

Aceptación: se puede descubrir al menos una interacción nueva sin usar comandos de depuración. Los botones no se superponen en 390×844 ni en 844×390. Se conserva el mapa, la fotografía y el guardado.

### 6. Verificación y entrega

Pruebas unitarias de geometría, umbrales, daño, reposo, persistencia y cancelación. Escenarios de choque a velocidad alta y salida tras contacto. Batería heredada más escenarios nuevos. Revisión visual de objetos intactos/rotos, modelo limpio/dañado, personaje recogiendo y entrada/salida. Render WebGL continuo separado de las pruebas que congelan gráficos para acelerar controles.

Aceptación: informes con recuentos reales, cero excepciones de JavaScript en la prueba, `gl.getError() === 0`, capturas reales del juego. Las limitaciones de GPU por software y dispositivos no probados deben aparecer en la entrega.

## Evolución posterior, no confundida con la implementación v0.4

| Etapa | Mejora | Dependencia | Puerta de calidad |
| :--- | :--- | :--- | :--- |
| v0.5 | Personaje con malla continua, skinning GPU y cinemática inversa de pies/manos | Rig y malla con pesos, animaciones originales/licenciadas | Plantado de pie estable, codos/rodillas sin inversiones, mezcla de clips sin saltos |
| v0.6 | Deformación por vértice, piezas desprendibles y ragdoll articulado | Solver iterativo y colisiones continuas generalizadas | Sin explosiones numéricas, límites de articulaciones y recuperación del control |
| v0.7 | Materiales PBR completos, normales y oclusión, LOD de personajes/vehículos | Texturas con permiso, cargador glTF validado, gestión de memoria | Comparación de materiales en tres luces, presupuesto medido por dispositivo |
| v0.8 | Interiores, puertas, escalar/vault, agarre con IK, NPC con estados sociales | Navegación interior y reservas de interacción | NPC no cruzan paredes, misiones no quedan bloqueadas por destrucción |
| v0.9 | Contratos emergentes, reputación y consecuencias barriales persistentes | Eventos y simulación desacoplados, diseño de economía | Rejugabilidad sin grind obligatorio ni explotación de recompensas |
| Beta | Perfilado en GPU real y móviles, accesibilidad, guardados robustos y distribución | Dispositivos, sesiones de prueba y publicación elegida por el usuario | Objetivos de rendimiento medidos y recuperación ante pérdida de contexto WebGL |

## Presupuestos y política de decisión autónoma

Objetivos de diseño, no resultados medidos todavía: paso fijo 1/60 s, consultas locales mediante hash, máximo 180 partículas visibles activas y 120 marcas, menos de 8 MB para el HTML de esta entrega, modelo de detalle sólo cerca de cámara. Evitar allocations crecientes por segundo y transparencias costosas en muchos objetos.

Ante fallo: reproducir, añadir test, corregir la causa y repetir regresiones. No reconstruir el motor ni añadir dependencias por comodidad. Si una pieza de la visión no alcanza su puerta de calidad, etiquetarla pendiente y entregar el incremento verificado. No publicar en un hosting ni hacer compras o suscripciones sin autorización específica.

## Referencias técnicas consultadas

Khronos glTF 2.0, coordenadas, materiales, nodos y animación: https://github.com/KhronosGroup/glTF/blob/main/specification/2.0/Specification.adoc
WebGL2 instancing: https://developer.mozilla.org/en-US/docs/Web/API/WebGL2RenderingContext/drawArraysInstanced
Las API de Higgsfield/3D Jutsu y el estado del proyecto se consultaron directamente mediante el conector autenticado.


## Decisiones verificables de v0.4

| Bloque | Resultado implementado | Límite deliberado |
| :--- | :--- | :--- |
| Entorno | 555 props, seis clases, resistencia, caída, movimiento y restauración | Edificios y elementos de misión siguen estáticos |
| Contactos | Hash de 12 m, pasos de 1/60, impulsos separados del roce | Proxies geométricos simples, sin fractura arbitraria ni CCD general |
| Autos | Cuatro zonas de daño, piezas desplazadas, cristal/faros, humo y suspensión | La malla aplica la deformación de la zona dominante, sin soft-body |
| Personaje | Aceleración, agacharse, esquiva, salto por flanco, agarre y reacción | Piezas articuladas, no malla humana continua |
| Apoyos | IK analítica de dos segmentos sobre suelo plano | Sin adaptación a desniveles o superficies móviles |
| Acceso a vehículos | Puerta y ocupante interpolados | Cambio lógico inmediato, agarre de manija todavía aproximado |
| Higgsfield | Proyecto original, GLB y 820 triángulos realmente convertidos | Parte de las piezas nativas son reconstrucciones simplificadas |
| Persistencia | Props alterados y autos desocupados dañados | No se guardan fragmentos ni la instantánea exacta del tráfico |
| Regresión | Campaña, policía, controles, exportación y carga probados | Dispositivos físicos pendientes |

## Camino técnico hacia el realismo visual

### Personaje continuo antes de añadir más animaciones

El siguiente cambio estructural debe reemplazar piezas rígidas por una malla humana continua, con topología adecuada en hombros, codos, caderas y rodillas. Mantener una convención estable de huesos y una pose de referencia. Un importador propio y acotado puede empezar por POSITION, NORMAL, TEXCOORD_0, JOINTS_0, WEIGHTS_0, inverseBindMatrices y transformaciones de nodos. Rechazar explícitamente extensiones no soportadas en lugar de cargar silenciosamente un personaje roto.

Separar locomoción, torso/manos y reacciones. Mezclar clips de reposo, marcha, carrera y frenado por velocidad medida. Sincronizar los pies por fase de contacto, no simplemente por el tiempo global. Comparar inicio, contacto, paso, recuperación, bucle y cambio de dirección. Mantener el esqueleto procedural de v0.4 como fallback hasta pasar esa revisión.

La interacción con coches necesita posiciones de acceso y salida, reserva del asiento, prueba de espacio libre, una trayectoria corta alrededor de la carrocería y puntos de mano para puerta y volante. La cámara y las entradas deben conocer el estado transitorio. La cancelación debe devolver a un punto válido, no dejar al personaje dentro del coche.

### Materiales antes de aumentar indiscriminadamente polígonos

Establecer material base, metalness, roughness, normal y ambient occlusion, con espacios de color y escalas consistentes. Verificar piel, tela, caucho, vidrio, metal pintado y corteza en un pequeño escenario de prueba con tres condiciones de luz. Usar texturas originales o con licencia comprobada. No introducir megatexturas ni un servicio de red obligatorio en la versión autónoma.

Un cargador propio puede ampliar la ruta de construcción a glTF validado y recursos embebidos. El runtime debe conservar límites de texturas, vértices, huesos e instancias y un fallback cuando falle una carga. El plan no presupone que un servicio de imágenes entregue automáticamente una malla, un rig y animaciones listas para jugar.

### Destrucción más rica sin romper la simulación

Evolucionar a piezas semánticas con uniones: base, tronco y ramas principales, mástil y luminaria, puertas y defensas. La rotura de una unión debe cambiar el estado físico y visual una sola vez. Los fragmentos relevantes necesitan colisión, sueño y un presupuesto por cercanía. El daño por vértice requiere conservar forma base, zonas de impacto, límites de deformación y normales coherentes.

Para choques rápidos, añadir barridos continuos a los proxies actuales antes de aumentar velocidades. Un ragdoll necesita masas, límites articulares, subpasos y recuperación hacia una animación controlada. No se mezclará la posición autoritativa del jugador con una ragdoll sin un estado de recuperación y una salida segura.

### Jugabilidad y consecuencias

Después de estabilizar los sistemas anteriores, los contratos deben poder consultar sucesos de la ciudad: un acceso bloqueado, un vehículo averiado o un contacto que exige discreción. No convertir cada objeto roto en una recompensa. Introducir recuperación de espacio público, ayuda y reparación como alternativas opcionales, junto a evasión, infiltración y conducción. Las misiones críticas necesitan vías alternativas cuando un objeto ya no exista.

Las primeras pruebas de jugabilidad deben observar si el jugador descubre E/G/V sin explicación externa, si comprende qué causó su daño y si puede recuperarse de una maniobra fallida. Medir sesiones y rutas de forma local durante pruebas consentidas, sin añadir telemetría remota por defecto.

## Protocolo de implementación autónoma para las siguientes iteraciones

1. Partir del último HTML y fuente verificados, no de una reescritura paralela.
2. Escoger una unidad funcional con estado, entradas y prueba de aceptación explícitos.
3. Crear el caso fallido, implementar el cambio mínimo y ejecutar regresiones afectadas.
4. Revisar la imagen real del juego. Un test de estado no valida una mano, una rueda o una copa enterrada.
5. Perfilar por separado simulación, envío de instancias y GPU. Un FPS de SwiftShader no se usará como promesa de rendimiento doméstico.
6. Documentar diferencias, formato de guardado, coste de recursos y limitaciones. Construir el HTML desde fuentes.
7. Publicar una entrega sólo con archivos existentes, informes y capturas. No desplegar ni consumir nuevas suscripciones sin autorización.

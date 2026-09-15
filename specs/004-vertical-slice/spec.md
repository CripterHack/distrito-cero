# SPEC-004 · Vertical slice de calidad

Estado: **proposed**, no implementada. Dependencias: gates de fiabilidad, personaje/contactos y escena/mundo. Duración objetivo de diseño: 10–15 minutos, a validar mediante playtest.

## Intención y propuesta narrativa

Un encargo en un barrio del consorcio Vértice conduce al jugador a observar un punto de intercambio, conversar o conseguir un acceso, obtener una prueba y abandonar la zona con una decisión final. Debe poder resolverse mediante observación/sigilo/tecnología o una alternativa más directa. Es una propuesta original que se integra con la campaña existente sin sustituir sus guardados.

## Espacio acotado

Una calle principal con dos rutas laterales, un interior pequeño accesible, un punto de vehículos y una conexión a periferia. Un protagonista personalizable, NPCs con roles claros y dos tipos de coche bastan para evaluar calidad. No necesita una ciudad nueva entera.

## Recorrido y aceptación

**SLICE-01 Inicio:** desde menú, crear o cargar personaje y comprender el objetivo sin consultar documentación externa. Controles se presentan de manera contextual, no con un muro de texto sobre la escena.

**SLICE-02 Observación:** binoculares o desplazamiento a pie permiten identificar el destino. La información respeta oclusión y no depende de conocer coordenadas.

**SLICE-03 Interacción:** un diálogo o interacción contextual abre dos rutas comprensibles. Rechazar/cancelar no bloquea el progreso ni repite recompensas.

**SLICE-04 Movimiento:** caminar, correr, subir/bajar del coche y sostener equipo conservan calidad de contacto en cámara habitual. No se cambia la pose por un render ajeno.

**SLICE-05 Consecuencias:** los incidentes producen reacciones claras de NPCs/policía. Hay una salida viable que no depende de explotar un bug. La derrota explica lo ocurrido y permite reintentar sin perder todo el progreso.

**SLICE-06 Datos:** guardar antes y después del objetivo, cerrar/reabrir y continuar mantiene decisiones e inventario. La misión temporal debe definir explícitamente qué se serializa.

**SLICE-07 Cierre:** el jugador reconoce su resolución y consecuencias. Se registra feedback del playtest sobre ritmo, control, confusión y defectos.

## Presentación

Materiales y escala coherentes entre personaje, vehículo y calle. Audio situacional, mezcla y señales de estado. Textos legibles, subtítulos para información sonora relevante y movimiento reducido. No depende de música o voz de licencia pendiente.

## Criterio de aceptación

Recorrido íntegro grabado sin teletransportar a objetivos, cero bloqueadores conocidos en las rutas definidas, presupuesto de rendimiento medido en un equipo aprobado y pruebas de reanudación. Investigación inicial propuesta con cinco participantes, sin anunciar porcentajes de éxito poblacionales. Cada fallo de comprensión genera una tarea concreta y un segundo ensayo.

## Fuera de alcance

Multijugador, doblaje completo, economía comercial, ciudad ilimitada con contenido narrativo único y publicación de pago. El objetivo es un estándar replicable de calidad, no una promesa de producción completa.

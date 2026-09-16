# Unidad: continuidad de superficie palma/pulgar

Base: master `ef905ece47bc8901c28c381ef081486e72fa8730`. Issue #6, CONTACT-01/02/05. Estado: verificación. No cierra #5/#6/#7. Se mantiene la publicación de master mediante Pages.

## Defecto y diagnóstico

El filtro digital de >=75% de influencia no medía toda la almohadilla que une palma y pulgar. La cohorte previa mixta de 164 puntos dejaba 33 dentro del apoyo delantero. Una cohorte geométrica fija más amplia (806 puntos izquierdos y 803 derechos), independiente de pesos, reproduce penetración máxima aproximada de 3.113 mm bajo el fusil y 3.596 mm en el cargador sostenido.

La superficie procedural incluye un exceso de volumen volar entre los contactos ya calibrados. Aumentar la influencia del pulgar en esa almohadilla redujo las penetraciones, pero provocó cambios de hasta aproximadamente 22 mm y nuevos pliegues/estiramientos en otras poses. Se rechaza ese candidato, no se publica su rebinding y no se cambia otra vez la oposición para compensarlo.

## Solución seleccionada

Correctivo de autoría de hasta 4 mm en el volumen volar de ambas almohadillas, con desvanecimiento continuo hacia muñeca, dorso y dedos. No cambia y/z, pesos, UV, topología o rig. Las normales se transforman con la inversa transpuesta de la misma deformación; su Jacobiano tiene determinante positivo. Las posiciones cuantizadas mantienen los vértices únicos y sus costuras. No es una simulación muscular.

Una semilla dispersa conserva las filas originales y rechaza modificaciones concurrentes desconocidas. Regeneración y comprobación reproducibles con biblioteca estándar. El motor consume el mismo formato y no ejecuta un correctivo por fotograma. Los GLB de versiones anteriores siguen siendo exportaciones históricas, no se reemplazan silenciosamente.

## Plan y aceptación

1. Reproducir el fallo con cohorte fija antes de modificar el recurso. Dos tests deben fallar en la base.
2. Diagnosticar geometría frente a pesos y descartar cambios que sólo trasladen el defecto.
3. Regenerador acotado, simétrico e idempotente. Peso/UV/rig intactos y desplazamiento <=4 mm en reposo y en las poses muestreadas.
4. Probar los tres apoyos largos, seis piezas extraíbles, ambas manos de armas cortas, movimiento, recarga, otras poses y serialización. Umbral de penetración de la nueva cohorte: 1 mm, sin modificar los umbrales existentes.
5. Capturas con renderer real, misma cámara/luz/reloj, métricas de superficie del dibujo y regresión completa. Guardados HTTP nativos aparte.
6. Revisar, exigir CI del PR y del push a master, comprobar Pages, registrar estado y límites. No borrar runs fallidos ni confundir una galería de estudio con FPS físicos o una aventura completa.

## Límites

Las distancias corresponden a proxies de arte, no a autocolisión completa. Existen pliegues e intersecciones heredadas en flexiones extremas. La mejora de contorno es localizada, no aprobación anatómica hiperrealista. Ojo/mira y transiciones/contactos mixtos más amplios siguen pendientes.

## Preservación del apoyo palmar

La regresión original de superficie neutral detectó que el primer correctivo de contorno alejaba la piel del ancla medida. Se añadió un área central preservada con transición suave. El test original de 2 mm permanece intacto y vuelve a pasar junto al criterio nuevo de 1 mm de penetración. No se movió el ancla ni se relajaron tolerancias.

# CONTACT · Hundimiento al detener marcha lenta

Base a7c13a8, refs #6. Continuación autónoma dentro del montaje/rig existentes.

## Contrato

Dado el avatar cerca del reposo, cuando la frecuencia de marcha tiende a cero,
el pie no conserva una excursión de paso completo ni obliga a bajar la raíz.
Dada una velocidad de envolvente completa, se conserva la trayectoria anterior.
Se mantienen inputs, física, dimensiones, normalización de pesos, contactos,
formatos persistentes y configuración de publicación.

## Plan y decisiones

1. Reproducir en el renderer y aislar cámara/posición física de rootY.
2. Añadir tests de baja velocidad/fase y la secuencia de detención nativa. Observar RED.
3. Atenuar únicamente la excursión z con el peso de marcha ya existente. No variar clamps.
4. Añadir controles de trayectoria a velocidad normal, pureza e identidad espacial.
5. Ejecutar Node completo, build/checkout y pruebas gráficas/HTTP aplicables.
6. Comparar protocolo nativo idéntico sobre los HTML canónicos antes/después.
7. Actualizar identidad/documentación. Publicar PR desde base remota exacta,
   revisar CI/artefactos y merge con HEAD protegido. Verificar master separadamente.

RED observado: tres fallos, incluido rootY=-0.5735982762684599 en frame 97.
GREEN: cinco regresiones y 536 Node aprobadas. Revisión propia, no independiente.
La evidencia gráfica y CI finales se registran con el commit correspondiente.

Decisión: corregir el factor de amplitud ausente, no la cámara, la culata o el
límite de suelo. Coste si el diagnóstico fuera incompleto: los tests de apoyo y
la comparación en movimiento deben detectar deriva de pies o nuevos saltos.
La penetración de chaqueta en recarga sigue separada, no se oculta con este PR.

Los binarios de build se reconstruyen sobre el padre remoto real. No publicar
historia sintética de un snapshot local, helpers temporales o permisos ampliados
en los workflows normales. La reversión incluye fuente, identidad y salidas.

# Unidad parcial: contacto entre ambas manos en armas cortas

Base: master `e614ff98061b9454eb47680bea7875a745373f3b`, posterior al correctivo de Actions #17. Issue #6, CONTACT-01/02/04/05. Estado: implementación en progreso.

## Problema reproducido

Con pistola y revólver apuntando, las palmas llegan a sus anclas, pero los dedos de apoyo se cruzan con los dominantes. Las muestras de piel y las envolventes segmentadas de la mano contraria detectan penetración. También hay dedos de apoyo dentro del mango. No atribuirlo a los pesos de manga ya corregidos.

## Alcance

Calibrar una postura de apoyo de la mano izquierda considerando a la vez el objeto y la mano derecha. Mantener malla, 49 huesos, pesos, anclas palmares y reglas del juego. No resolver el contacto separando arbitrariamente toda la mano. Constantes de autoría, sin optimización por fotograma. Interpolar el apoyo con la manipulación y retorno existentes.

## Unidades verificables

1. Pruebas fallidas de piel contra mano contraria y mango, usando las poses reales y referencias del mismo modelo.
2. Calibración offline de falanges/oposición, con restricciones de contacto y separación, sin desplazar anclas.
3. Pruebas de apuntado, agachado, giro, disparo, recarga, cancelación y no modificación de datos. Mantener familias anteriores.
4. Capturas comparables y fases de recarga con renderer real. Una métrica de cápsulas no aprueba por sí sola la anatomía.
5. Build, regresiones, revisión, CI del PR y del push, Pages y handoff. #6 permanece abierto por requisitos restantes.

## Límites

Las envolventes digitales son proxies de QA y no autocolisión completa. La selección por influencia no cubre toda la zona mixta de palma/pulgar. No se afirma acabado hiperrealista ni coste GPU físico.

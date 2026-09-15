# Unidad de implementación: unión de prenda y brazo

Base `072750b`. Refs #5 y #6, requisito CONTACT-03. Es una corrección localizada sobre el rig vigente, no aprobación global del personaje ni implementación de todos los contactos digitales.

## Plan ejecutable

1. Reproducir el caso neutral/aim/front y medir vértices de la prenda además de pivotes.
2. Escribir regresiones que fallen para mangas ligadas al torso, tronco ligado a brazos y deformación de superficie.
3. Conservar las influencias originales como insumo compacto con atributos identificados por hash.
4. Corregir pertenencia de superficies y transición del hombro en autoría; no tocar montaje, física, munición ni longitudes óseas.
5. Comprobar geometría/UV/normales intactas, puños separados de pantalón y reconstrucción idempotente.
6. Revisar capturas de frente/perfil, recarga, agachado, binoculares y la matriz vigente de personajes.
7. Integrar sólo con CI aprobada. Comprobar Pages contra el HTML de master. Actualizar handoff e issue con el resultado real.

## Criterios de salida de esta unidad

No contaminación de torso en la región inferior desconectada de mangas, ni de brazos en la región inferior del tronco. La muestra de superficie permanece dentro de la envolvente de 9 cm de su brazo en los casos documentados. Contratos de manos, armas, guardados y recuperación intactos. Ausencia de membrana amplia bajo el brazo en el caso fijado y revisión comparativa de los demás casos.

## Pendientes que esta unidad no cierra

Correctivos anatómicos de hombro/axila, contacto de falanges, alineación de ojo/mira, todas las recargas/cancelaciones, continuidad exhaustiva y aprobación artística del conjunto. No aumentar el alcance mezclando una nueva misión o sistema de guardado con esta corrección.

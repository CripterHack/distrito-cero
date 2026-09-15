# Handoff · benchmark y siguiente corrección visual

## Estado integrado

#2 y #3 cerrados mediante PRs #8 y #9: runner portable y persistencia HTTP nativa con 35 checks. #4 cerrado mediante PR #10, commit `a752e9ecdbc5ef6f077cbcdca75cb09c77b55ce9`: recuperación WebGL, conservación de sesión/borrador y reanudación explícita. CI de ese PR: `34940253023`, todos los jobs aprobados.

HTML con recuperación: `3f1f5ac6a6d3aa7a74b8046a89f0a5f13b06d9982899131a8351a9909df67318`. Master publica Pages según configuración del usuario. No cambiar permisos, origen ni formato de partidas.

## Unidad actual #5

Primera fase técnica: matriz versionada, 30 capturas smoke / 586 full, medidas canónicas y por LOD, galería y aprobación artística separada. Leer [CHARACTER-BENCHMARK.md](CHARACTER-BENCHMARK.md). No modifica el runtime. Revisar su PR/CI antes de atribuir resultados al HEAD actual. #5 sigue abierto por el gate artístico y los demás criterios pendientes.

## Siguiente unidad #6

Usar los casos fijos de apuntado/recarga para analizar deformación de chaqueta y brazos, además de contactos palmares. La primera referencia del HTML original mostró un pliegue amplio en el tórax bajo el brazo de apoyo aunque pasaran las tolerancias de muñecas. Reproducir sobre el HEAD aceptado, escribir una regresión de superficie/pose y localizar la causa antes de cambiar pesos o anclas. No reemplazar el montaje único ni tocar munición para corregir una captura.

## #7

Sigue pendiente la vertical slice y sus gates de mundo, escena, rendimiento y playtest. No cerrar por añadir una propuesta ni por mover automáticamente al jugador junto a los objetivos.

## Entrada para el siguiente agente

Leer HEAD remoto, AGENTS, STATE, spec002/003 y resultados actuales. Crear rama por unidad. Ejecutar build/Node, tests de matriz, suite characters, manejo, recuperación y guardados nativos según alcance. Mantener informes nuevos en artifacts, nunca encima de qa histórico. Comparar el mismo hash, cámara, luz y caso. Actualizar decisión artística y handoff sólo con evidencia real.

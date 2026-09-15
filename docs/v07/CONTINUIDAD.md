# Continuación desde Horizonte

## Primera prioridad: humano y ocupantes pendientes
La fuente actual es v0.5 más Horizonte, no las capturas de v0.6. Implementar un controlador de ocupación con identificadores estables, estados acercarse/abrir/extraer/entrar/sentarse/cerrar/cancelar y transferencia de control al final. Un conductor desalojado debe aparecer una sola vez en el mundo. No intentar recuperar un rig o una secuencia de animación a partir de una imagen.

Separar el estado lógico de la pose, reservar el asiento, verificar espacio libre y definir puntos de mano/asiento/manija. Hacer legible el conductor mediante una pasada de cristal apropiada. Añadir pruebas de cancelación, vehículo móvil, bloqueo lateral, guardado durante transición y persecución. La escena de revisión debe mostrar simultáneamente puerta, ocupante y jugador, sin ocultar penetraciones con la cámara.

## Mundo posterior
La altura de terreno debe convertirse en dato autoritativo usado por colisiones, apoyo del pie, suspensión y navegación, no sólo una deformación visual. Empezar por una colina y un puente con acceso continuo antes de habilitar relieve en todas las regiones. Introducir jerarquía vial con cruces canónicos conservados, para no desconectar el mundo existente.

## Rendimiento
Medir por separado generación CPU, física, subida de instancias y tiempos GPU en equipo real. Pasar descriptores de sector a un Worker y limitar el número de vertices creados por lote. Conservar los presupuestos de memoria y añadir histéresis de LOD. No convertir el FPS del laboratorio SwiftShader en una promesa para el usuario.

## Persistencia
Versionar generadores y semillas antes de modificar radicalmente la distribución. Para guardar más de 4096 cambios, incorporar una política explícita de archivo regional local, recuperación y exportación. Mantener compatibilidad de los guardados anteriores con migraciones verificadas.

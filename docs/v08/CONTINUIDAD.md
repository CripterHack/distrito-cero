# Continuidad · siguiente incremento

## Fuente única
Partir del ZIP v0.8 y verificar el manifiesto. No volver a reconstruir Horizonte sobre v0.5. Conservar la rama y el HTML de esta entrega como base de regresión. Las variantes históricas «territorio» y «horizonte» no se mezclarán sin revisar IDs, unidades, clases y guardados.

## Siguientes unidades de calidad
1. **Arte humano verificable.** Antes de ampliar polígonos, reemplazar la anatomía de cabeza por topología y texturas originales o con redistribución comprobada. Comparar en tres iluminaciones y distancias. Ropa con siluetas y rostros distintos, no sólo tintes. Un render de autoría no demuestra integración.
2. **Contacto de cuerpo completo.** Resolver pelvis, columna, muñecas y dedos en manilla, marco y volante. Reservar el volumen de apertura, mantener pies apoyados durante tracción, variar reacción según dirección. Sólo después añadir ragdoll con límites articulares y recuperación.
3. **Streaming y rendimiento.** Mover generación de sectores a Worker, medir CPU/GPU por dispositivo, precargar LOD y evaluar skinning/overdraw. Mantener budgets reales, no prometer FPS a partir de SwiftShader.
4. **Profundidad de NPC.** Diferenciar retirarse, pedir ayuda, testificar, perseguir a pie y recuperar el vehículo, con navegación, prioridades y modos no letales. No inventar simulación policial ya implementada.
5. **Validación externa.** Safari/Firefox, móvil físico, GPU real, sesiones de una hora, contexto WebGL perdido/restaurado, almacenamiento real y accesibilidad.

Cada unidad requiere pruebas fallidas, implementación, revisión de frames y regresión de campaña/policía/atlas. No añadir dependencias de runtime sin cambiar explícitamente el contrato con el usuario. No reemplazar escenarios o publicar en servicios de hosting sin autorización.

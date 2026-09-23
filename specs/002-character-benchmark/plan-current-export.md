# CHAR-06 · Exportación neutral actual

**Objetivo:** producir una exportación identificada con el contenido vigente, sin sustituir los GLB históricos ni confundir estructura con aprobación artística.

**Arquitectura:** reutilizar la receta existente en un staging temporal de sólo sus entradas. Actualizar únicamente identidad y procedencia del JSON de salida. Validación Khronos separada, completa y enlazada mediante hashes. Cero dependencias o cambios de runtime.

**Especificación:** [SPEC-002](spec.md), CHAR-06. Herramientas: Python, NumPy/SciPy/Pillow fijados por el proyecto, Node y glTF-Validator 2.0.0-dev.3.10.

## Unidades

- [x] Escribir cuatro regresiones de disponibilidad, aislamiento, entradas y protección de históricos. Observar RED antes de implementar.
- [x] Implementar exportación actual sin editar el exportador histórico ni buffers de la receta.
- [x] Escribir tres controles de rechazo de reportes vacíos, truncados y con errores, sin suprimir advertencias. Observar RED y GREEN.
- [x] Definir workflow con permisos de lectura, dependencias de desarrollo fijadas y artefactos de diagnóstico.
- [ ] Ejecutar el validador oficial sobre el GLB real y revisar todos sus mensajes. No heredar éxito de los tests de estructura.
- [ ] Revisar diff, integridad histórica y CI completa del HEAD. Publicar/integrar sólo cuando los gates aplicables aprueben.

La licencia propia sigue siendo una decisión del titular. DQ, shaders, variantes y coreografías no portables permanecen explícitos. Esta unidad no declara satisfechos los requisitos artísticos o físicos de #5. No hay migraciones ni nuevos recursos descargados por el jugador.

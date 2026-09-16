# Identidad de producto y proceso de publicación

`version.json` es la única fuente de número de producto, nombre, canal y fecha. No cambiar los números de esquemas de datos al publicar un cambio visual. El nombre de un GLB histórico tampoco define la versión actual del juego.

`python3 build.py` genera `index.html` y `build-info.json`. El HTML incorpora `DC.BuildInfo` inmutable, metadatos y etiquetas visibles. El sidecar contiene tamaño y SHA-256 del HTML, además de la huella de sus insumos explícitos. `--check` no escribe: falla si falta o está desactualizada una salida. No introduce una llamada HTTP en runtime.

Una publicación exige pruebas aplicables, revisión de diferencias, documentación vigente, CI del PR, CI del push a master y comprobación del sitio público. El estado success de un PR no equivale al resultado de otro runner posterior. Conservar los fallos históricos, no reetiquetarlos ni reintentar hasta ocultarlos.

El número completo usa tres componentes, como `0.20.0`. La UI muestra `v0.20` cuando el parche es cero y muestra el parche cuando no lo es. La etapa sigue siendo `prototype`; aprobar otro canal requiere decisión de producto, no sólo editar el manifiesto.

Al actualizar versión, revisar README, índice de recursos, STATE, guía vigente, changelog y handoff. Los tests comparan las etiquetas vigentes con el manifiesto, sin exigir que los archivos históricos pierdan sus versiones originales. Los resultados nuevos de CI siempre identifican el SHA del HTML.

Para soporte, solicita la versión y el identificador que muestra Pausa. Recargar conserva datos del mismo origen. Borrar el almacenamiento local no es un procedimiento de actualización. GitHub Pages publica master por configuración existente, no cambiada por este proceso.

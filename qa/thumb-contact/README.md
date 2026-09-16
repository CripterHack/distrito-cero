# Comparación de oposición del pulgar

`comparison.jpg` conserva tres pares de capturas del renderer real. Izquierda: HTML de master `71fd53a`. Derecha: la unidad de oposición del pulgar. Cámara, reloj, luz y tamaño son iguales en cada par. Sólo se añadieron encabezados fuera de la imagen. `preview*.jpg` son reducciones idénticas de los pares, sin retoque.

En `reference.json`, `baselineComparativeReport` es deliberadamente el informe del HTML anterior. Sus seis fallos de contacto reproducen el defecto, no son resultados de la versión corregida. Los informes de la nueva versión se generan mediante `--suite thumbs` y se publican como artefactos de su ejecución de CI.

La clave histórica `fit[].base` registra la posición de la raíz antes de cada ensayo de calibración. No es la raíz final ajustada, ni el pivote virtual metacarpal. `tip`, `worst`, `padGap` y `collisionMin` sí pertenecen a la solución evaluada. Se conservan los valores originales en vez de reemplazar evidencia. El script de diagnóstico ahora usa el nombre explícito `initialRootBeforeTrial` y añade `fittedRoot` para las nuevas ejecuciones.

La inspección del par dominante muestra el pulgar menos enterrado, pero su base aún tiene una lectura gruesa y angular. Esta mejora localizada no equivale a una aprobación hiperrealista ni a la aceptación artística completa del issue #5. La revisión del conjunto continúa pendiente.

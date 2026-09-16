# Correctivo de CI y dibujo durante pérdida de contexto

Base: `bbc26848ee0dd26a8193aa6dbfe4dfafc3a9e734`. Estado: implementación en curso.

## Evidencia y alcance

El run de master 35045749864 falló después de 27 comprobaciones de manejo satisfactorias. El informe contiene `contextlost: software GPU`; la instrucción de render directo posterior lanza `Cannot read properties of undefined (reading 'push')` en buildSector/add. thumbs y fingers aprobaron, al igual que build, datos nativos, benchmark y Pages. No se ha demostrado una causa específica del driver que originó la pérdida.

La app bloquea su RAF durante recuperación, pero los entrypoints del renderer y el harness de imágenes aún permiten dibujo directo sobre una generación ya liberada. Es un defecto reproducible de lifecycle independiente de cómo se pierde la GPU.

## Unidad

1. Reproducir el acceso a generación liberada/con contexto perdido mediante tests Node y evento WEBGL_lose_context real.
2. Rechazar render/sync de generaciones inactivas antes de mutar listas, sectores, contadores o emitir GL. Mantener visibles los errores de una generación viva.
3. Hacer determinista la suite de fotogramas: detener RAF por su API, observar cada dibujo y registrar errores en vez de sobreescribir RAF global o continuar durante recuperación. No recuperar/reintentar silenciosamente una pérdida inesperada.
4. Mostrar diagnóstico de la suite fallida directamente en Actions, preservando informes frescos, límites y salida no cero.
5. Ejecutar las suites afectadas y master tras integrar. Conservar el historial rojo, no borrar runs ni actualizarlo como si una regresión no hubiera existido.

## Invariantes y rollback

Sin cambios de rig, anatomía, equipamiento, física, misión, formatos o configuración de Pages. No añadir librerías de runtime. Revertir el PR no exige migrar partidas. Éxito del renderer/harness no demuestra solución universal del driver ni FPS en hardware físico.

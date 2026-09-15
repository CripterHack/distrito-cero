# Handoff · continuidad después de recuperación gráfica

## Estado verificado antes de esta unidad

Master al retomar: `e23835a24e792248c95ad08520e2e6068d4757bc`. #2 y #3 quedaron cerrados mediante #8 y #9: runner portable y 35 comprobaciones de guardado HTTP nativo con reapertura/conflictos. GitHub Pages está activado por el usuario desde master y no se modifica su configuración.

## Unidad #4

Implementados ledger de recursos, restauración por generaciones, programación RAF única, bloqueo de entradas y exportación mientras el contexto está perdido. El diálogo conserva la sesión y el borrador y requiere reanudación explícita. Leer `GRAPHICS-RECOVERY.md` y consultar el PR/CI para resultados del commit exacto. No considerar las capturas de la ejecución interrumpida como evidencia de esta implementación.

## Siguiente trabajo

#5: preparar benchmark reproducible de personajes con cámaras/luces/perfiles/poses declarados. La captura de referencia no significa que la anatomía actual esté aprobada como hiperrealista. Registrar aprobación visual por separado.

#6: depende de referencias del rig y superficies. Extender el montaje de v0.19, no crear uno paralelo. Primero medir contactos completos de palma/falanges y cancelaciones, después corregir los defectos reproducidos.

#7: depende de los gates de escena, mundo, personajes y datos. Diseñar la muestra de 10–15 minutos y validar recorrido íntegro y playtests físicos cuando estén disponibles. No cerrar por añadir otra propuesta o por teletransportar objetivos.

## Comandos

`python3 build.py`, `node --test tests/*.test.cjs`, `python3 tests/qa_runner.test.py`, exportación GLB, `python3 -m tools.qa.run --suite handling --suite recovery`, y `python3 -m tools.qa.run --suite native --origin http`.

No eliminar evidencia histórica. Antes de escribir, leer HEAD remoto y AGENTS. Integrar sólo tras checks y revisar Pages después del merge. No quedan operaciones de recuperación corriendo por una promesa en el chat: revisar los procesos y acciones existentes antes de repetirlos.

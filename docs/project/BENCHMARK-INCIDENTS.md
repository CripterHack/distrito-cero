# Incidencias verificadas de la integración del benchmark

## Run de CI 34991261427

El contrato y los tests unitarios pasaron. La ejecución del productor terminó con error antes de arrancar el navegador. El harness histórico excluía cualquier directorio llamado `qa` mediante `shutil.ignore_patterns`, incluyendo **tools/qa**, que contiene los módulos usados por la nueva suite. No era una falla de anatomía ni de WebGL.

Se reprodujo con una copia temporal mínima que contenía `tools/qa/character_matrix.py` y `qa/old.json`: el helper desaparecía igual que los informes antiguos. Se añadió `tools/qa/workspace.py` para distinguir el `qa/` histórico de la raíz frente al código anidado, conservando exclusión de artefactos, secretos, cachés y dependencias.

Tres regresiones comprueban que se conserva el código legítimo, se excluyen historia/entorno y no se sobrescribe una salida existente. El workflow ahora muestra también el log del productor al fallar. El intento inicial permanece rojo y no se cuenta como verificación satisfactoria.

Los resultados de las ejecuciones posteriores se consultan en los checks del PR #11, asociados a sus respectivos commits. No se reescribe el reporte inicial ni se reemplazan pruebas por un resultado antiguo.

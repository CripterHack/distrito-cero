# CI: pasos independientes y fallos identificables

Issue #31. Base de producto `32a8cca590b83a5b2a1b3efabad5723d3c9d6757`, versión 0.20.1. Este cambio corrige el diagnóstico y la cobertura del workflow, no la postura del rifle de #29 ni la aceptación pendiente del PR #30.

## Causa y corrección

En el run `35637033697` de PR #30 (HEAD `a1062639dd92769f3b7c8d678159d40359f46700`), Node estaba dentro del mismo bloque de 17 comandos que la autoría de la palma. Su fallo se mostraba bajo el primer comando y evitaba ejecutar los contratos Python, exportación y enlaces posteriores. Los jobs WebGL y HTTP terminaron success, pero el workflow completo terminó failure.

Se separan ocho gates: autoría thenar, mangas, build/checkout, Node completo, contratos QA/workflow, exportación, inmutabilidad de recursos y enlaces. Todos requieren checkout, Node y Python listos y ausencia de cancelación. Después de un fallo de pruebas continúan las comprobaciones independientes. No se usa `continue-on-error`, no se cambia el código de salida ni se omiten pruebas. El job permanece fallido cuando cualquier gate falla.

Los jobs WebGL/HTTP y sus comandos se conservan byte por byte. Permisos `contents: read`, dependencias, runtime, HTML, recursos, datos y versión sin cambios.

## Verificación reproducible

```sh
python3 tests/ci_workflow.test.py
python3 build.py --check
node --test tests/*.test.cjs
```

Seis tests de estructura reprodujeron el fallo antes de separar los pasos y aprobaron después. Verifican comandos conservados, Node sin filtros, prerrequisitos, cancelación, propagación del fallo y permisos. Son controles de esta estructura concreta, no un emulador de GitHub Actions.

La copia local de master proviene del artefacto Pages verificado. El workflow original y `.gitattributes` coinciden con sus blobs remotos. Verificación local de esta unidad: 484 Node, 87 Python incluyendo seis tests nuevos, autoría/build/export aprobados. HTML y GLB se compararon byte por byte con el archivo de Pages. Sintaxis YAML comprobada localmente. Dos ejecuciones agrupadas excedieron el tiempo de la herramienta del laboratorio; los comandos restantes se ejecutaron separadamente con sus salidas completas. No se presentan esas ejecuciones interrumpidas como aprobadas.

La CI de esta rama se consulta en su PR. No hereda como aprobación el resultado de master o de #30. Un merge sólo procede tras revisar el HEAD exacto y sus jobs. Al actualizar #30 con este workflow, su requisito de rifle debe seguir fallando hasta una corrección real, ahora en el paso Node correcto.

## Continuidad y reversión

Mantener #29 y #6 abiertas. No eliminar o marcar skip en `rifle-coordination.test.cjs`. El defecto necesita coordinación y revisión de superficies, no una modificación de CI. Revertir el PR de #31 devuelve la organización anterior, sin migración ni cambio de partidas.

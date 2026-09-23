# Exportación humana actual y verificable

Refs #5, CHAR-06. Exportación de autoría, no sustitución del runtime ni aprobación artística.

## Contrato

El comando nuevo reutiliza `export_traits_glb.py` sobre una copia temporal y completa de sus entradas actuales. Esa receta produce el rig neutral, mapas incrustados y once clips procedurales. Sólo se actualiza el JSON de identidad/procedencia al empaquetarlo con la versión presente. Los buffers geométricos y de animación de la receta se conservan. No se modifica el exportador histórico ni se sobrescriben `assets/dc016-human-traits.glb` o sus informes.

La salida exige un directorio nuevo. Rechaza destinos dentro de `assets/`, directorios existentes y cambios en las entradas durante el proceso. `source-manifest.json` identifica las fuentes, mapas, scripts, versión y build por SHA-256. Ese manifiesto deja `officialValidation=not-run` y `artisticAcceptance=pending` de manera intencional.

La validación separada utiliza **Khronos glTF-Validator 2.0.0-dev.3.10**. Revisa los recursos incrustados sin filtros de issues o cambios de severidad y conserva el reporte completo, incluso si falla. Un error, resultado incompleto o contenido diferente impide producir `validated-manifest.json`. Las advertencias no se suprimen y necesitan revisión. Cada validación queda enlazada por hash al GLB y al manifiesto fuente.

## Ejecución

```sh
python3 tools/export_current_human.py --output artifacts/human-export
npm install --prefix artifacts/gltf-tools --ignore-scripts --no-audit --no-fund --no-package-lock --save-exact gltf-validator@2.0.0-dev.3.10
node tools/qa/validate_glb.cjs artifacts/human-export artifacts/gltf-tools/node_modules/gltf-validator
python3 tests/current_human_export.test.py
node --test tests/glb-validation-contract.test.cjs
```

NumPy, SciPy y Pillow se toman de las versiones ya fijadas en `requirements-dev.txt`. Node y el validador son herramientas de desarrollo. El HTML no incorpora dependencias o peticiones nuevas. El workflow `Current human authoring export` tiene `contents: read`, genera un artefacto y nunca escribe commits, refs o Pages. No se añaden nuevos GLB pesados al historial de código.

## Límites de intercambio

El GLB representa un solo perfil neutral ajustado y peinado clásico, 49 huesos y once clips de la receta. No incluye todas las variantes del creador o nuevas coreografías de equipo. El juego usa DQ y el glTF estándar de esta receta usa skinning lineal, por lo que las superficies animadas pueden diferir. Materiales portátiles son una aproximación y no exportan todo el detalle, parpadeo y mirada de shaders. Validar la estructura no aprueba estas diferencias visuales ni el rendimiento físico.

`assets/ATTRIBUTION-v09.md` mantiene la declaración de terceros. No se concede una licencia nueva al contenido propio. La decisión global del titular y la revisión artística de #5 siguen pendientes. Esta unidad no permite cerrar automáticamente #5, #6 o #7.

## Estado y reversión

Las cuatro regresiones de exportación y tres del contrato de reporte fallaron antes de implementar y pasan localmente. La validación oficial depende del resultado real del workflow del PR, no de esas pruebas unitarias. Consultar su artefacto y HEAD exacto antes de aceptar una exportación. Revertir esta unidad retira herramientas/tests/workflow/documentación, sin cambios en partidas ni recursos históricos.

Documentación del validador: [repositorio oficial](https://github.com/KhronosGroup/glTF-Validator), [API Node](https://github.com/KhronosGroup/glTF-Validator/blob/main/node/README.md).

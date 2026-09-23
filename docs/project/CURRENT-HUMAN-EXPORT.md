# Exportación humana actual y verificable

Refs #5, CHAR-06. Exportación de autoría, no sustitución del runtime ni aprobación artística.

## Contrato

El comando nuevo reutiliza `export_traits_glb.py` sobre una copia temporal y completa de sus entradas actuales. Esa receta produce el rig neutral, mapas incrustados y once clips procedurales. Se actualiza la identidad/procedencia y se normalizan dos defectos de intercambio heredados: se omite children vacío en nodos hoja y se pone a cero el índice de articulaciones cuyo peso ya era cero. Posiciones, normales, UVs, pesos, índices de triángulos, matrices y clips permanecen idénticos a la receta. La jerarquía de articulaciones también se conserva; sólo las instancias hoja de malla con skin se promueven a raíz de sus escenas. Los índices de influencia nula modificados se cuentan en portableNormalization. No se modifica el exportador histórico ni se sobrescriben `assets/dc016-human-traits.glb` o sus informes.

La salida exige un directorio nuevo. Dentro del repositorio sólo permite `artifacts/`. Rechaza destinos en fuentes o históricos, directorios existentes y cambios en las entradas durante el proceso. `source-manifest.json` identifica las fuentes, mapas, scripts, versión y build por SHA-256. Ese manifiesto deja `officialValidation=not-run` y `artisticAcceptance=pending` de manera intencional.

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

## Registro de la primera unidad · PR #36

Las cuatro regresiones iniciales de exportación y tres del contrato de reporte observaron RED/GREEN. El primer validador oficial, run 35846902847, rechazó el GLB con 13 errores EMPTY_ENTITY y registró 15,921 advertencias. Se conservaron su artefacto 10743459045 y reporte completo. Dos regresiones nuevas reprodujeron los 13 nodos hoja inválidos y 15,906 índices no nulos con peso cero. Tras la normalización, nueve pruebas Python pasan, incluidas preservación byte a byte y controles de formato/rango. La nueva validación oficial se consulta por el HEAD correspondiente, no se deduce de esos tests. El primer reporte también identifica 14 nodos de malla bajo el nodo raíz animado y una dependencia de tangentes generadas por el visor. Se conservan esa jerarquía/material y los avisos para una revisión de portabilidad separada, no se filtran. Los avisos informativos de UV sin uso y 52 triángulos degenerados cuantizados tampoco se eliminan modificando la anatomía. Consultar el artefacto y HEAD exacto antes de aceptar una exportación. Revertir esta unidad retira herramientas/tests/workflow/documentación, sin cambios en partidas ni recursos históricos.

Documentación del validador: [repositorio oficial](https://github.com/KhronosGroup/glTF-Validator), [API Node](https://github.com/KhronosGroup/glTF-Validator/blob/main/node/README.md).

## Reproducibilidad numérica

El manifiesto registra versiones reales de Python, Node, NumPy, SciPy y Pillow. Una comparación entre el primer artefacto remoto y el laboratorio encontró diferencias binarias en muestras de animación, además de los índices normalizados, pese a descripciones de accessors idénticas. No se atribuye identidad binaria a entornos distintos. La regresión coteja la salida contra la receta exacta de la misma ejecución: en el binario únicamente pueden cambiar índices de peso cero. Las normalizaciones JSON y de enlaces de instancia se comprueban por separado, conservando todos los ancestros de las articulaciones. Los hashes de cada artefacto siguen siendo su identidad, no una promesa de igualdad entre plataformas.


## Continuación de jerarquía · 23 de septiembre de 2026

PR #36 integrado en `b96371e`. Su artefacto oficial `10744701650` tiene 0 errores y 15 advertencias. Se comprobaron GLB, manifiestos y hashes. La siguiente corrección retira la ambigüedad de 14 instancias bajo un padre: glTF ignora los transforms de ese padre para la instancia, pero sigue aplicándolos a las articulaciones. Se mueven las hojas a raíz de las escenas originales, no los huesos.

`portableHierarchy.promotedMeshNodes` registra cada índice promovido. Sólo cambian enlaces de padre y raíces de escena. No se modifican buffers, animación del contenedor, índices/atributos de nodos ni jerarquía del esqueleto. La transformación es idempotente y no agrega mallas a escenas ajenas. Grafos cíclicos, doble padre, índices inválidos e instancias con hijos, transforms propios, animación propia o función de articulación se rechazan antes de mutar.

La prueba real falló primero con los 14 índices 50–63. Después del correctivo pasan 14 tests Python y 522 Node completos, sin omitidos. El build sigue intacto. La primera llamada a Node fue interrumpida antes de su resumen y no cuenta como aprobación; la repetición completa terminó con exitCode 0. La validación oficial de esta revisión se consulta en su PR, no se deduce de los tests.

El aviso de tangentes y los informativos de UV/triángulos permanecen fuera de este cambio y no se filtran. No se afirma cero advertencias totales, identidad entre DQ/LBS o aprobación artística. [Plan y criterio](../../specs/002-character-benchmark/plan-portable-root.md). Revertir sólo esta unidad devuelve la jerarquía portable anterior, sin afectar el juego.

## Variante con tangentes · continuación de PR #37

PR #37 está integrado como c49ed085 y su CI/exportación/Pages posterior aprobó.
Las 14 advertencias de jerarquía quedaron corregidas. El GLB original mantiene una
advertencia de tangentes generadas por el visor. La [variante separada](PORTABLE-TANGENTS.md)
incorpora bases MikkTSpace con política declarada para UV degeneradas, conserva
atributos originales por esquina y añade su propia validación. El artefacto incluye
ambos archivos y ambos reportes. No se sobrescriben históricos ni se declara que
el fallback haya reparado UV, materiales o equivalencia DQ/LBS.

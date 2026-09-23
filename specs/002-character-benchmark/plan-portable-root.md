# CHAR-06 · Jerarquía portable sin transformaciones ambiguas

**Base:** master b96371e, PR #36 integrado. **Spec:** [SPEC-002](spec.md), CHAR-06.
**Ejecución:** secuencial con pruebas antes del correctivo y revisión propia.

## Problema y decisión

El GLB revisado tiene 14 avisos NODE_SKINNED_MESH_NON_ROOT. Sus nodos de malla son hojas bajo el contenedor animado que también contiene el esqueleto. glTF ignora los transforms de las instancias con skin y utiliza los de sus articulaciones. Promover sólo esas instancias a raíz de sus escenas elimina la jerarquía ambigua sin mover articulaciones ni alterar animaciones.

Se reutiliza tools/export_current_human.py. No se modifica la receta histórica ni el runtime. La tangente ausente y los informativos de UV/triángulos quedan fuera de esta unidad, visibles en el reporte oficial. No se pretende cero warnings totales o aprobación artística.

## Contrato

La operación conserva los buffers completos, índices de nodos, atributos de malla, skins, jerarquía de articulaciones y canales de animación. Sólo quita enlaces padre→instancia y añade la instancia a las escenas donde ya era alcanzable. Es idempotente. Rechaza antes de mutar ciclos, índices inválidos, doble padre, instancias que son articulaciones, nodos no hoja, transforms locales, instancias animadas y mallas que no pertenecen a ninguna escena.

## Pasos y comprobación

1. Añadir una prueba a la exportación real que exige cero padres en sus 14 instancias. Ejecutarla sobre el exportador anterior y conservar RED.
2. Añadir casos de raíces, varias escenas, invariantes y rechazos atómicos. Implementar normalize_skinned_roots(description) y registrar los índices promovidos en portableHierarchy.
3. Actualizar el test de preservación para permitir exclusivamente esos enlaces de jerarquía. Mantener idénticos buffers, articulaciones y canales, incluida la animación del contenedor original.
4. Ejecutar python3 tests/current_human_export.test.py, node --test tests/*.test.cjs y python3 build.py --check. Inspeccionar el GLB de salida y los hashes de históricos.
5. Publicar PR desde master con los cambios acotados. Exigir el validador Khronos sin filtros, cero errores y cero NODE_SKINNED_MESH_NON_ROOT antes del merge. Verificar que el aviso de tangentes y los informativos restantes sigan visibles.
6. Actualizar STATE/HANDOFF y CURRENT-HUMAN-EXPORT con evidencia y límites. Verificar CI del HEAD exacto y después master/Pages.

## Reversión

Revertir esta unidad devuelve la jerarquía portable anterior. No migra ni borra partidas. No modifica assets históricos, fuente humana, HTML, licencia o permisos. Una exportación aceptada estructuralmente no cierra #5, #6 o #7.

## Fuente normativa

[glTF 2.0, instanciación](https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html#skins). [Caso de referencia Khronos](https://github.com/KhronosGroup/glTF-Sample-Assets/issues/263).

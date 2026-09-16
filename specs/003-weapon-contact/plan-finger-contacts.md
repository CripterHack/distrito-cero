# Plan de la unidad · contacto digital

Base: `f9998523492bf29ff276cf85c3f282d32163821a`. Avance parcial de CONTACT-01/02/04/05 e issue #6. No cierra la aprobación artística de #5.

## Secuencia ejecutada

1. Medir piel cuantizada de falanges frente a volúmenes de arte, independientemente de los pivotes de muñeca. Tres regresiones fallaron en la base.
2. Mantener todo el rig, malla, pesos y montaje. Corregir únicamente las flexiones de los dedos no pulgares con una búsqueda acotada del primer contacto.
3. Permitir curvatura distal cuando la articulación proximal ya toca el objeto. Almacenar cuatro perfiles finitos, no perfiles por coordenada o actor.
4. Probar tres posturas por nueve empuñaduras, seis piezas extraíbles, invariancia espacial y continuidad de recarga. Conservar el índice de disparo y pulgar anteriores.
5. Examinar los vértices realmente deformados por la paleta del renderer en seis casos focales y capturar sus fases.
6. Reproducir a 1/60 s el tirón de apertura detectado en navegador. Ampliar la ventana visual de liberación, sin relajar el test ni cambiar la lógica de la acción.
7. Integrar la suite con el harness existente. Ejecutar regresiones y publicar mediante PR sólo con comprobaciones aprobadas.

## Contratos y aceptación

El único módulo de runtime editado es `src/weapon-handling.js`; el HTML se regenera. Helpers y pruebas no se distribuyen al juego. Las superficies de prueba se comparan con los modelos existentes y no cambian sus atributos. Las palmas y matrices de brazos permanecen, los huesos no se estiran y el catálogo no se escribe durante la inspección.

Se verifican distancias con tolerancia de 3 mm en la muestra declarada, no contacto físico exacto de toda la mano. La distancia elíptica es aproximada. Un pase de métricas no aprueba hiperrealismo. Los 14 tests Node y 15 checks del navegador tienen alcance explícito en [FINGER-CONTACTS.md](../../docs/project/FINGER-CONTACTS.md).

## Trabajo siguiente y reversión

El pulgar requiere tratar su base/oposición por separado. Permanecen pendientes interacción entre manos, ojo/mira y revisión global de animaciones. No añadir una deformación artificial para ocultarlo. Revertir este PR y reconstruir el HTML no exige migración y conserva PR #12/#13.

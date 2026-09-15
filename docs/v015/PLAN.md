# Distrito Cero v0.15 · Integración cervical

Base comprobada: v0.14, SHA-256 del HTML 82c535a0d25d3f5ba1753ae2248cb284745608bd53e2590b1e07237be8d40883.

## Diagnóstico y alcance aprobado
El perfil anterior alcanza sólo unos 92 mm de ancho en el cuello medio, frente a la cabeza y la chaqueta ancha de este avatar. La complexión modifica las prendas pero no el volumen cervical. Los límites absolutos de antiguas pruebas (<53 y <59 mm de semiancho) preservaban precisamente la delgadez que el usuario pide corregir. Se sustituyen únicamente esos criterios históricos por proporciones, suavidad y pruebas de deformación. No son límites antropométricos universales.

## Plan de implementación
1. Reproducir el fallo de masa cervical y desacoplamiento de complexión con pruebas fallidas.
2. Partir del recurso v0.14 congelado. Construir un perfil elíptico diferenciado de garganta, laterales y nuca, más ancho y profundo, con continuidad a mandíbula y raíz. Conservar ojos, nariz, labios y orejas.
3. Adaptar la abertura de chaqueta y la caída trapecio/hombro, sin subir el collar para esconder el defecto. Recalcular normales y comprobar costuras, pesos y geometría.
4. Acoplar moderadamente complexión y volumen cervical y conservar el ajuste independiente del cuello, con límites. CPU y GPU deben producir la misma forma y normales. No cambiar huesos, estatura, colisionadores ni esquema de guardados.
5. Reequilibrar giro y flexión entre cuello/cabeza sólo si la revisión de poses lo justifica. Revisar malla real deformada, no sólo matrices finitas.
6. Capturar frontal, perfil, tres cuartos, nuca, izquierda/derecha, arriba/abajo, extremos del creador, carrera, conducción y extracción. Misma cámara y luz para comparativas.
7. Ejecutar regresión de creador, doce espacios, campaña y bucle continuo. Construir HTML, GLB y paquete con informes de la ejecución actual y límites explícitos.

## Criterios de aceptación
Proporción de cuello medio respecto a cabeza dentro de una banda artística definida para este modelo. Ningún abultamiento local discontinuo; manos, cara superior y suelas no se desplazan por grosor/complexión cervical. Base adherida al pecho, mentón a cabeza, normales/UV/pesos válidos. Control de cuello coherente a distintas complexiones, sin perder partidas o identidad. No presentar un screenshot como garantía de fotorrealismo.

## Referencia de orientación
OpenStax, Anatomy and Physiology 2e, 11.3, músculos axiales de cabeza/cuello/espalda, consultada 2026-09-14: https://openstax.org/books/anatomy-and-physiology-2e/pages/11-3-axial-muscles-of-the-head-neck-and-back
Se usa para orientar las inserciones y siluetas, no para atribuir normas poblacionales a las medidas de este avatar. Recursos y licencias anteriores se conservan.

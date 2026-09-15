# SPEC-002 · Personaje patrón y calidad anatómica

Estado: **ready para benchmark**, remodelado pendiente de la referencia revisada. Prioridad P1. Relación QG-004/009/011. Dependencia: base reproducible; no depende de terminar todo M1 para preparar cámaras y referencias.

## Problema e intención

El usuario ha observado repetidamente inconsistencias en cuello, hombros, manos, cabello y sujeción. Corregir sólo una dimensión en una captura produjo cambios que luego se percibieron demasiado delgados, largos o artificiales. Se necesita una base estable que funcione en reposo, personalización y movimiento.

Como jugador quiero que mi personaje y los NPCs tengan proporciones, superficies y animaciones creíbles en la cámara habitual y el creador. Como artista quiero saber qué referencia y qué límites aprobamos antes de cambiar la geometría otra vez.

## Alcance por fases

**A. Benchmark:** conjunto fijo de cámaras, iluminación, poses y perfiles, con modo de material neutro y mapas reales. Ficha métrica de altura total, cabeza, cuello visible, anchura de hombros, proporciones de brazos/manos y separación de prendas. No son valores clínicos universales.

**B. Anatomía:** topología y pesos editables, cuello/trapecio/clavícula/hombro como conjunto, mano con articulación coherente y correctivos de compresión. Mantener las interfaces del rig o migrarlas explícitamente.

**C. Superficie:** consistencia entre cara/cuello/manos, ojos y párpados, roughness y normal correctos, cabello con nacimiento y silueta menos uniformes, prendas con pliegues vinculados a construcción y pose.

**D. Reparto:** variaciones anatómicas reales compatibles con el creador, no sólo tintes. Todas comparten infraestructura de rig y LOD cuando sea viable, pero no deben confundirse con escaneos individuales inexistentes.

## Escenarios de aceptación

**CHAR-01:** al revisar neutral, ligero, robusto y extremos permitidos en frontal/perfil/3⁄4, la cabeza está integrada con torso sin cuello tubular, malla abierta o prenda usada para esconder una unión rota. Aprobación artística registrada por par de imágenes, no sólo un test de radio.

**CHAR-02:** en doce poses acordadas, las superficies mantienen continuidad, las matrices son finitas y los segmentos no se alargan para alcanzar un apoyo. Verificar aristas, volúmenes muestreados y siluetas en movimiento; declarar autointersecciones residuales.

**CHAR-03:** cambiar un parámetro del creador produce el mismo resultado en estudio, partida, guardado recargado y NPC que usa el perfil. El control no altera colisiones o ventajas de juego sin requisito explícito.

**CHAR-04:** cada peinado tiene silueta reconocible, raíz con cobertura y LOD coherentes, sin cabeza atravesando en las poses aprobadas. Los estilos largos necesitan proxies/contactos propios o un límite visual documentado, no una afirmación de física inexistente.

**CHAR-05:** materiales se revisan en tres luces y distancias. No esconder artefactos cambiando sólo exposición o antialiasing. El detalle fino se filtra al alejarse y el coste se registra.

**CHAR-06:** cada recurso y exportación tiene autor, fuente, licencia, rig, unidades, mapas y checksum. GLB con cero errores del validador oficial antes de considerarlo formato de intercambio aceptado, con warnings revisados.

## Módulos

`src/hero-asset.js` (generado), `hair-geometry.js`, `human-materials.js`, `appearance.js`, `character-fit.js`, `skin-rig.js`, `dual-quaternion.js`, `cast-renderer.js`, `identity-ui.js` y recetas de `tools/`. No editar un blob geométrico sin regenerador. El nuevo benchmark de captura debe vivir en tests y usar el renderer real.

## No objetivos y límites

No crear un cuerpo completamente nuevo, facial rig, cloth y hair physics en un único PR. No incorporar un escaneo de persona o asset de pago sin permiso. No cambiar armas o economía para demostrar el personaje. El presupuesto inicial por humano se compara con la base <100k de detalle alto, pero el objetivo es calidad por coste, no maximizar triángulos.

## Evidencia final

Galería comparable, clips de locomoción/contacto, fallos iniciales y correcciones, mapa de parámetros, coste por LOD, registro de aprobación artística y reporte de exportación. El benchmark es un deliverable previo a la remodelación y no constituye por sí mismo una mejora del asset.

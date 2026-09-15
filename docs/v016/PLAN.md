# Rasgos v0.16 · Plan de implementación

**Objetivo:** Acortar la región cervical y ofrecer peinados distinguibles, editables y persistentes sobre v0.15.
**Base:** HTML y fuentes entregados de v0.15, no una recuperación de ensayos de otras ramas.
**Arquitectura:** Mantener las coordenadas canónicas para materiales/UV. Aplicar un ajuste cervical anterior al skinning y evaluar los dos pivotes cervicales en ese mismo espacio ajustado. Las extremidades, contactos, simulación y guardados mantienen sus contratos. Cabello como geometría nativa compartida por estilo/LOD, con cejas separadas y cobertura concordante en color/sombra.
**Tecnologías:** JavaScript/WebGL2 nativos. Python/Node/Playwright sólo para autoría y pruebas.

## Decisiones y alcance
- Reducir la separación cabeza-tórax nominal en 45 mm, con ajuste acotado de 12 mm por lado. No comprimir rostro, ojos, orejas o cráneo.
- Conservar el ancho cervical de v0.15, el anclaje torácico y las capacidades/cápsula física.
- Preservar IDs 0–3 de los peinados de perfiles anteriores. Añadir siete estilos, con variantes claramente diferentes en vista frontal y lateral.
- Volumen del cabello y cejas vinculadas opcionales. Las combinaciones de laterales/flequillo se resuelven por estilo, no mediante controles incompatibles ilimitados.
- Añadir controles al creador y persistencia de nuevos campos opcionales. No sustituir SaveStore ni duplicar el catálogo.
- Aplicar a jugador, peatones y ocupantes. No prometer AAA ni cabello/tela físicos.

## Unidades verificables
1. [x] Pruebas rojas: ajustes cervicales, rig, opciones de pelo, migración y aislamiento entre slots.
2. [x] Ajuste cervical y retarget de bind/pose consistente con GPU.
3. [x] Cabello con raíz anatómica, mechones, estilos y tres LOD acotados.
4. [x] Creador, validación, migración y preferencias guardadas.
5. [x] Capturas antes/después, galería de estilos y secuencias en movimiento.
6. [x] Regresión de lógica, creador/catálogo, campaña y bucle continuo. Empaquetado e informe con hashes.

## Verificación de alcance
La cápsula física conserva sus dimensiones. La altura modificada es la del modelo visible y sus pivotes cervicales. La topología canónica y los mapas faciales previos se conservan. No se añadieron miniaturas de partidas, prendas nuevas, simulación de cabello ni un rig facial. Las variantes nuevas sí se guardan por espacio y se aplican a los actores.

# Arquitectura actual y dirección de evolución

## Contrato vigente

Metros, Y vertical, avance +Z. Simulación de paso fijo de 1/60 s según el diseño existente. Namespace `DC`, archivos clásicos concatenados por `build.py`, sin imports de red. DOM para interfaz, Canvas 2D para mapas, WebGL2 para escena, Web Audio para sonido. La salida es `index.html`.

## Mapa real de responsabilidades

| Responsabilidad | Archivos principales |
| :--- | :--- |
| Utilidades y mundo base | `src/core.js`, `src/world.js` |
| Regiones, carreteras y consultas | `src/frontier-world.js` |
| Simulación, misión, conducción y policía | `src/simulation.js`, `src/police.js` |
| Daño, objetos y acciones | `src/dynamics.js`, `src/interactions.js` |
| Estado regional y continuidad | `src/frontier-simulation.js` |
| Asientos, conductores y acceso | `src/occupancy.js` |
| Apariencia y catálogo local | `src/appearance.js`, `src/save-store.js` |
| Ajuste anatómico y locomoción | `src/character-fit.js`, `src/character-motion.js` |
| Pose, palmas e IK | `src/skin-rig.js`, `src/weapon-handling.js` |
| DQ y simplificación | `src/dual-quaternion.js`, `src/crowd-geometry.js` |
| Assets y materiales | `src/hero-asset.js`, `src/hair-geometry.js`, `src/human-materials.js`, `src/visual-geometry.js`, `src/vehicle-asset.js` |
| Equipamiento | `src/equipment.js`, `src/equipment-simulation.js`, `src/equipment-geometry.js` |
| Render | `src/renderer.js` y las capas reactive, realism, frontier, cast y equipment |
| App e interfaz | `src/app.js`, `src/frontier-ui.js`, `src/identity-ui.js`, `src/equipment-ui.js`, `src/page.html`, `src/style.css` |
| Audio | `src/audio.js` y adaptación de arsenal en `equipment-ui.js` |

## Dependencia de construcción

No son módulos ES intercambiables. Cada capa captura una clase `Base`, la extiende y puede reemplazar la referencia pública que usarán las capas siguientes. Cambiar el orden de `build.py` puede alterar serialización, construcción y comportamiento aunque todos los archivos tengan sintaxis válida.

La cadena de simulación incorpora base, objetos reactivos, regiones, ocupación, identidad y equipamiento. La cadena visual incorpora renderer base, objetos, realismo, regiones, reparto y equipo. La app incorpora base, horizonte, identidad y arsenal. Los nombres efectivos se deben comprobar en las fuentes antes de refactorizar.

## Propiedad y fronteras

La simulación produce instantáneas serializables. La pose transforma una muestra del actor, sin consumir munición ni conceder dinero. El renderer mantiene buffers, cámaras y estados temporales de presentación. El catálogo valida una instantánea antes de escribirla. El creador utiliza una simulación de borrador separada.

Las referencias de arma, palmas, muñecas, boca y cargador deben proceder del mismo montaje y del mismo actor de locomoción. La identidad de un conductor no puede depender de una malla dibujada. Los efectos EMP son temporales y no se serializan como destrucción permanente.

## Evolución propuesta, no implementada

1. Hacer explícitos lifecycle, configuraciones y contratos sin reemplazar las capas de golpe.
2. Introducir una frontera de recursos con `create`, `dispose`, `onContextLost` y `restore`, sin pérdida del estado de simulación.
3. Centralizar consultas de superficies y anclas para pies, manos, asientos y props. Conservar soluciones económicas para LOD lejanos.
4. Separar una receta de autoría editable del formato compacto que consume el motor. Adoptar GLB validado como intercambio, no un cargador general innecesario en runtime.
5. Trasladar generación pesada a trabajos acotados o Worker, manteniendo semilla y orden de aplicación deterministas.
6. Versionar el contrato de guardado cuando cambie su semántica, no sólo porque cambie el render.

Cada paso necesita un PR reversible, fixture y comparación. No introducir un ECS, otro motor o un framework UI completo por preferencia personal del agente. Una prueba de viabilidad puede medir alternativas, pero no sustituye la autorización para cambiar las restricciones del producto.

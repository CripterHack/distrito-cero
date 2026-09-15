# Postura óptica y continuidad de hombros · issue #6

## Base y alcance

Unidad CONTACT-03/05/06 sobre `ac3cf5b3ef78e42f50eee173a8200b9e3d2e4286`, después de corregir las influencias de mangas. Se recuperó trabajo no publicado de la sesión anterior y se volvió a comprobar contra esta base. Sólo cambia la presentación de binoculares y la selección de referencias de codo por perfil. No se remodela el cuerpo ni se cambia el solver de manos.

HTML resultante: 8,851,747 bytes, SHA-256 `fe47dfa3ef9b2bff6d415b6f6fb0b64e0d0b0c0df7193b135c59e4fc3fe7b93b`. Los modelos humanos y de equipo, sus pesos, UVs, normales y exportaciones conservan sus bytes respecto de la base.

## Defecto y causa

Con binoculares levantados, especialmente al agacharse, los codos se abrían y elevaban de forma excesiva. Durante la subida y bajada podían cambiar de dirección bruscamente aunque las muñecas alcanzaran exactamente su destino.

`SkinRig.applyArmTarget` proyecta una referencia de codo sobre el plano perpendicular al vector hombro-muñeca. La referencia genérica orientada hacia atrás y abajo quedaba cerca de la dirección opuesta a ese vector para una herramienta sostenida junto al rostro. La proyección pequeña hacía que cambios leves de la muñeca produjeran variaciones grandes del plano de flexión. El interpolador rápido utilizado también por las armas de fuego acentuaba el movimiento al iniciar y soltar la observación.

## Implementación

El perfil de binoculares define dos referencias de codo en espacio local del actor, orientadas hacia delante, algo hacia abajo y lateralmente. Se consumen en el montaje existente. Los demás perfiles mantienen exactamente sus referencias anteriores. No hay un segundo sistema de IK, escalado de huesos ni nuevas posiciones palmares.

La elevación visual de binoculares utiliza amortiguación 6 en lugar de 12. Desde reposo alcanza aproximadamente 95% de su pose en 0.5 segundos de simulación; al soltar, baja con el mismo tratamiento. El resto de armas conserva amortiguación 12. No cambian la activación lógica de observación, los factores 2x/4x/8x/12x, inventario, recarga, daño, captura policial o guardados.

## Regresión y evidencia

`tests/shoulder-motion.test.cjs` contiene ocho casos. Se ejecutaron primero contra las fuentes anteriores: seis fallaron y dos invariantes ya pasaban. Luego los ocho pasaron con la corrección. El workflow de traslado a la rama repitió ese ciclo antes de reconstruir el HTML, y se retiró del árbol final.

Se verifican barrido de elevación, ciclo de subir/bajar con `equipmentStep`, codos bajo muñecas en el rango central de observación, longitudes óseas, contacto palmar y orientación, lectura determinista, referencias de otras familias, separación respecto de la colinealidad y superficie superior de la chaqueta.

En la ejecución local corregida, el máximo desplazamiento de codo durante un incremento de 1/180 de elevación fue 0.002960 m. Con pasos de simulación de 1/60 s, el ciclo probado alcanzó 0.034807 m por paso en codos y 0.022979 m en 284 muestras de superficie superior. La prueba anterior se detenía al encontrar una muestra de prenda con 0.104956 m por paso; **no se presenta ese primer fallo como un máximo global**. Son métricas de continuidad del caso preparado, no umbrales universales de anatomía o FPS.

La suite `optical` añade catorce comprobaciones WebGL, trece capturas y veinte muestras renderizadas del ciclo óptico, además de revisar la recarga del fusil. Usa el motor real con reloj/cámara/estado inicial preparados y almacenamiento fixture. No graba todos los pasos en vídeo ni prueba persistencia nativa: esa propiedad pertenece a la suite `native` separada.

```sh
node --test tests/shoulder-motion.test.cjs
python3 -m tools.qa.run --suite optical --suite handling --suite recovery --headed
python3 -m tools.qa.run --suite characters --headed
python3 -m tools.qa.run --suite native --origin http --headed
```

El runner conserva la evidencia nueva en `artifacts`, ligada al hash. La CI requiere la suite óptica en cada PR y mantiene las pruebas de modelos, manejo, recuperación y guardados. Consultar los resultados de su commit antes de afirmar un pase. La ejecución local utilizó Chromium por software con Xvfb; una ausencia inicial de `xauth` se resolvió iniciando Xvfb directamente, sin alterar el juego ni relajar pruebas.

## Límites y siguiente unidad

La geometría de hombros, manos y cabello sigue siendo estilizada. No se implementan autocolisiones de tejidos, agarres físicos por falange, alineación óptica exacta entre ojos y oculares ni simulación muscular. La mejora de binoculares no representa una revisión nueva de todas las armas ni añade equipamiento a NPCs.

Los barridos cubren muestras de los rangos documentados; no equivalen a probar infinitas combinaciones de poses, proporciones y velocidades. #5 sigue abierto para sus criterios artísticos y de autoría, #6 para contactos/recargas restantes y #7 para la muestra jugable completa. La siguiente unidad debe medir dedos y zonas de contacto de otras familias antes de modificar anclas o anatomía.

Reversión: revertir la integración y ejecutar `python3 build.py`. No hay migración de partidas, cambios de Pages, servicios nuevos ni dependencias del runtime.

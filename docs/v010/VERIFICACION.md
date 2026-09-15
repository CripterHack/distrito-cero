# Distrito Cero v0.10 · Constitución · Verificación

Base: **v0.9 Anatomía**. La fuente y el runtime mantienen la continuidad del juego. No se presenta la entrega como AAA terminado.

## Identidad

HTML: **8,061,625 bytes**. SHA-256:

`426a2f1baaa8960956e5c8d48aa50d546e48d75a13455a87ca275e0e302eece3`

GLB: **2,942,460 bytes**. SHA-256:

`b23294d0e65c7a5bf5edf542d547a05bb4366d61ce1f9ea9e7b8720d4feb9f3f`

`qa/v010/release-report.json` contiene el manifiesto de esta ejecución. Los informes de integración y bucle continuo, y las nueve capturas nuevas, registran la huella exacta del HTML. La décima captura corresponde al HTML v0.9 original para comparación.

## Ejecuciones finales

| Grupo | Pases | Fallos |
| :--- | ---: | ---: |
| Lógica Node, núcleo, policía, ocupación, mundo y rig nuevo | 171 | 0 |
| WebGL, reparto, dedos, ocupación, atlas y controles táctiles | 87 | 0 |
| Campaña, movimiento e interfaz heredada ejecutadas sobre v0.10 | 52 | 0 |
| Render y simulación continuos con teclado real | 16 | 0 |
| Geometría corporal cuantizada | 7 | 0 |
| Regresión de cabeza, mapas, UV y cuero cabelludo | 6 | 0 |
| Estructura, pesos, jerarquía y clips del GLB actual | 1 | 0 |

Total: **155 comprobaciones de navegador**, además de 171 pruebas de lógica y 14 pruebas de geometría/exportación. Son aserciones, no 155 sesiones independientes ni cobertura exhaustiva del mundo abierto. No se incluyen los pases históricos de v0.9 ni las 161 comprobaciones de baseline como resultados adicionales.

Las tres suites de navegador terminaron sin excepciones JavaScript, errores de shader/WebGL registrados ni solicitudes HTTP/HTTPS. Las texturas `data:` ya embebidas no son una descarga de red.

## Anatomía y esqueleto

Se verificó que las 49 matrices de reposo son identidad, que se preservan las longitudes de falanges al flexionar y que los treinta huesos de dedos tienen vértices influenciados. La prueba de muñeca coloca un objetivo IK real y comprueba que los dedos permanecen cerca de su nueva posición, no en el origen anterior.

La topología de piel de las manos tiene exactamente dos componentes conectados, uno por mano: palma, espacio interdigital y dedos no son segmentos flotantes. Se comprobaron longitud, transición con puño de manga, suela plana, normales, suma de pesos e índices válidos. Esto no es una prueba de toda posible autointersección de triángulos durante una pose extrema.

El renderer compiló ambos programas con 49 huesos, sometió distintas paletas a la GPU para mano abierta/cerrada y mantuvo la transformación de muñeca. La prueba del reparto verifica distintas matrices por persona, LOD decreciente y buffers acotados. Los 196 texeles de cada fila de paleta derivan del número real de huesos, no de la constante antigua de 17.

## Integración y sistemas anteriores

La suite de estados inicia extracción de conductor, pausa y reanuda, cancela antes de liberarlo, completa la secuencia, sale y vuelve a entrar a un coche vacío. Comprueba que no hay duplicados, que los policías siguen siendo ocupantes y que las reglas de búsqueda siguen activas. Se revisan acceso remoto, viaje, regiones y persistencia del vehículo.

La suite continua usa el RAF y los métodos originales de simulación, cámara y render. Parte de posiciones preparadas y utiliza teclado real para extraer, entrar, conducir, frenar, salir, caminar, cruzar un límite de sector y usar el atlas. No se sustituye el renderer durante esta suite. No equivale a jugar una sesión completa de horas ni a medir FPS de una GPU física.

La suite heredada comprueba el desenlace público de la campaña, conducción, mapa, diálogo, guardado/continuación y mandos táctiles. Prepara posiciones cerca de objetivos para verificar sus transiciones, no afirma completar todos los recorridos de manera espontánea.

Los archivos `core.js`, `world.js`, `police.js`, `simulation.js`, `dynamics.js`, `interactions.js`, `frontier-world.js`, `frontier-simulation.js`, `frontier-renderer.js`, `frontier-ui.js`, `occupancy.js`, `character-motion.js`, `audio.js`, `app.js` y `human-materials.js` conservaron sus huellas respecto del manifiesto base. La comparación no sustituye la integración, por eso se ejecutaron ambas verificaciones.

## Revisión visual

Se revisaron capturas WebGL de cuerpo completo frontal y de perfil, correr, agacharse, mano extendida y flexión máxima, reparto, conductor y extracción. La captura anterior y la nueva de cuerpo completo usan los mismos parámetros de cámara, luz, viewport y reposo. La composición sólo añade rótulos y el mismo recorte/escalado a cada mitad, no retoca al personaje.

Se corrigieron el pulgar demasiado extendido durante el agarre y el cierre de chaqueta mal apoyado en la tela. La prueba de regresión del pulgar falla al restituir temporalmente la fórmula antigua y pasa con la nueva, con registro en `thumb-red-replay.txt`. La primera generación excedió el presupuesto de 100,000 triángulos: se redujo el muestreo de las manos, se reconstruyó la malla y se repitieron las pruebas. No se elevó ese límite para hacer pasar la prueba.

La inspección final muestra una constitución más esbelta, menor volumen excesivo de hombros y suelas y manos conectadas con uñas. El agarre de flexión máxima aún puede comprimir la superficie y no reproduce contacto físico preciso. Las pruebas de estado no convierten ese límite visual en un resultado AAA.

## Recursos y exportación

| Recurso | Valor |
| :--- | ---: |
| Triángulos de detalle alto | 79,278 |
| Triángulos de detalle medio | 16,874 |
| Triángulos lejanos | 5,919 |
| Huesos / grupos de material | 49 / 13 |
| Paleta compartida | 196 × 128 RGBA32F |
| Memoria de esa textura exclusivamente | 401,408 bytes |
| Texturas de piel conservadas | 512² / 256² / 128² |

La capacidad de 128 filas no significa 128 personajes visibles a 60 FPS. La estimación no incluye mallas, buffers del mundo, sombras, reflejos ni memoria JavaScript.

Se reconstruyeron geometría, HTML y GLB desde los insumos incluidos. Sus huellas antes/después son idénticas, según `qa/v010/rebuild.json`. La lectura independiente del GLB con trimesh recuperó 13 mallas, 79,278 triángulos y límites métricos finitos. La prueba estructural comprueba buffers, normales, pesos y siete estudios de animación.

No se ejecutó el validador oficial de Khronos ni una reproducción visual completa en editores externos. Los clips son procedurales y los dos estudios de mano muestran poses. Parpadeo, mirada, microdetalle, contactos de volante y secuencias de vehículos siguen siendo código de runtime. El GLB es una aproximación portable de esos materiales, no una copia del shader completo.

## Entorno y límites

Chromium 144.0.7559.96, Linux, Xvfb y ANGLE SwiftShader. La suite de estados usa fotogramas WebGL reales controlados y almacenamiento aislado en memoria. El bucle continuo usa 680 × 440, las capturas finales 900 × 740 y los controles táctiles se emulan en 390 × 844 y 844 × 390. Las ejecuciones finales cerraron sus navegadores normalmente.

No se probaron Safari, Firefox, teléfonos físicos, GPU del usuario, pérdida de contexto WebGL, persistencia nativa entre reaperturas `file://`, sesiones de horas o despliegue público. No se han inferido promesas de rendimiento doméstico de la velocidad del laboratorio.

La cabeza y piel de v0.9 se conservan. Cuerpo, prendas, manos y zapatos son modelado original paramétrico, no escaneo corporal. La familia morfológica sigue compartida por los NPCs. No hay simulación muscular, tela física, mocap, contacto individual de dedos ni expresiones faciales completas. Los detalles de procedencia están en `assets/ATTRIBUTION-v010.md`.

## Reproducción

Los comandos actuales están en `README.md`. Los scripts Python históricos que esperan 17 huesos no constituyen la suite de v0.10. El juego final no necesita las dependencias de autoría ni las de prueba.

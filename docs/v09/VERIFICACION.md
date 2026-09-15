# Distrito Cero v0.9 · Anatomía · Verificación

11 de septiembre de 2026. Base: v0.8 Presencia. HTML: **5,642,919 bytes**.

SHA-256: `ae268d154df28868f07e69e0adfd60d024b39eac38e41abc14f45df2100f1f26`.

## Resultados de esta entrega

| Grupo | Pases | Fallos finales |
| :--- | ---: | ---: |
| Lógica con Node, regresiones y materiales/LOD | 161 | 0 |
| Integración de piel, reparto, ocupación, mapas y entrada táctil | 79 | 0 |
| Campaña, conducción e interfaz heredada sobre v0.9 | 52 | 0 |
| Bucle continuo, renderer y teclado sin sustituciones | 16 | 0 |
| Geometría cuantizada, UV, cuello, cuero cabelludo y mapas | 6 | 0 |
| GLB actual con materiales, rig y animación | 1 | 0 |

Son **147 comprobaciones de navegador**, no 147 sesiones independientes ni un ensayo de todas las situaciones posibles. No se suman resultados de v0.8. Los JSON `qa/v09/human-browser.json`, `human-continuous.json`, `legacy/browser-report.json` y `release-report.json` registran el resultado. El modelo GLB se leyó además mediante trimesh como parser independiente.

En las tres suites finales no se registraron excepciones JavaScript, errores WebGL detectados ni peticiones HTTP/HTTPS. Las imágenes `data:` embebidas no se cuentan como solicitudes externas.

## Alcance anatómico y visual

La cara no es otra reconstrucción a partir de una captura: la cabeza proviene de vértices reales HM08 y un target adulto, con licencia CC0. La topología se adapta al esqueleto nativo, se conecta al cuello y recibe UV para albedo, normal y rugosidad. Nariz, labios, párpados y orejas pertenecen a esa superficie. Los ojos y el groom son geometría original adicional. Los autores de los recursos están en `assets/ATTRIBUTION-v09.md`.

Las mallas de cuerpo y ropa siguen siendo originales/procedurales. Se modificaron hombros, mangas, pantalones, cuello y costuras, pero no se añadió un esqueleto de dedos ni anatomía de manos escaneada. Las variantes de NPC comparten familia facial y mapas con tintes relativos. No son decenas de personas escaneadas únicas.

Se capturaron rostro diurno, nocturno, parpadeo, reparto, conductor y extracción con el motor real. Las cámaras y posiciones de revisión se preparan directamente. La comparación antes/después carga el HTML v0.8 original y el nuevo HTML con la misma cámara, luz, viewport y pose. Sólo se compone el marco de rotulación; no se retoca la apariencia de los personajes.

La comparación contiene una mejora visible de anatomía facial, ojos y detalle de superficie. El resultado sigue siendo un personaje de juego estilizado. No se afirma equivalencia con un estudio AAA, fotogrametría de una persona, animación facial expresiva o simulación física del pelo/tela.

## Presupuesto

| Elemento | Valor |
| :--- | ---: |
| Triángulos LOD alto | 54,119 |
| Triángulos LOD medio | 16,121 |
| Triángulos LOD lejano | 5,732 |
| Huesos / materiales | 17 / 12 |
| Albedo / normal / rugosidad | 512² / 256² / 128² |
| Tres texturas RGBA8 con mipmaps, estimación | 1,835,008 bytes |
| Capacidad de paletas compartidas | 128 actores |

La estimación de texturas no es una medición de memoria total, VRAM ni rendimiento. La capacidad de 128 actores tampoco promete ese número en pantalla a 60 FPS. Los mapas y la geometría de cada LOD se comparten entre los personajes.

## Regresiones

El bucle continuo no sustituye RAF, métodos de simulación, cámara ni renderer. Usa teclado para iniciar extracción, esperar el cierre, conducir, frenar, salir, caminar y cruzar un límite de sector. Su posición inicial se prepara para que el caso sea repetible. La suite por estados congela render/RAF entre pasos explícitos, pero dibuja keyframes WebGL reales. La suite heredada recorre el desenlace público, coloca el jugador cerca de objetivos y comprueba diálogo, captura de progreso, guardado, mapa y controles.

Se verificó binariamente contra el commit base que `core.js`, `world.js`, `police.js`, `simulation.js`, `dynamics.js`, `interactions.js`, `frontier-world.js`, `frontier-simulation.js`, `frontier-renderer.js`, `frontier-ui.js`, `occupancy.js`, `skin-rig.js`, `character-motion.js`, `audio.js` y `app.js` no cambiaron. `qa/v09/behavior-unchanged.json` enumera esos archivos. Esto no sustituye las pruebas de integración.

Se reconstruyeron mapas, geometría y HTML con los scripts distribuidos. Las huellas de `hero-asset.js`, `human-materials.js` e `index.html` quedaron idénticas antes y después. `qa/v09/rebuild.json` conserva la comparación. La reproducción offline parte del insumo compacto versionado, no del paquete completo original.

## Defectos corregidos y límites del laboratorio

El primer bake presentaba una mancha orbital y pequeños píxeles oscuros espurios. Se reparó una región con simetría de la zona limpia y feathering, preservando el insumo original. La primera unión del cuello tenía bordes visibles: se añadió una transición geométrica, pesos graduales, collar más alto y transición de material. El cabello inicial tenía un borde continuo de casco: se separó su superficie para aplicar cobertura gradual también en sombras.

Una aserción de separación del cuero cabelludo exigía 1.7 mm respecto del vértice anatómico más próximo, confundiendo el margen de la función de autoría con la distancia del modelo cuantizado y remuestreado. Se cambió al criterio comprobable de cuatro pasos de cuantización (0.4 mm). El mínimo observado supera 0.65 mm respecto de las muestras anatómicas vecinas. Es una prueba de separación entre muestras, no una demostración de colisión exacta entre cada triángulo de ambas superficies.

Una captura anterior de comparación agotó el límite del proceso en el laboratorio. Se repitieron los dos retratos a **840 × 555**, manteniendo los mismos parámetros entre versiones, y cada captura final terminó con código 0 y GL 0. No se contabiliza el intento interrumpido como pase. Otras capturas de detalle son de 1120 × 740.

Entorno: Chromium, Xvfb, Linux y ANGLE SwiftShader. Las páginas se inyectan con `set_content` y localStorage aislado en memoria. No se probaron Safari, Firefox, persistencia nativa entre aperturas `file://`, GPU física, teléfonos físicos, sesiones de horas ni pérdida/restauración del contexto WebGL. No se ha convertido una cifra de SwiftShader en promesa de FPS.

## Modelo exportado

`assets/dc09-human-textured.glb`, **1,946,576 bytes**, contiene 12 mallas, 17 huesos, tres PNG embebidos y cinco estudios procedurales: reposo, caminata, carrera, agacharse y sujetar. Se comprueban tamaños/rangos de buffers, índices, normales, pesos, huesos, tiempos crecientes y cuaterniones de los clips. Trimesh recupera 54,119 triángulos y una caja métrica finita.

No se ejecutó el validador oficial Khronos ni una reproducción visual completa en todos los editores. Mirada, parpadeo, tramado del cuero cabelludo, variaciones de rostro y la secuencia de extracción son código de runtime, no clips o efectos incluidos en el GLB. Por ello la apariencia de un visor externo es una aproximación portable, no necesariamente idéntica al navegador del juego.

## Reproducir

Consultar los comandos en `README.md`. Las dependencias de autoría y pruebas no son dependencias del HTML. No hay nuevos permisos, pagos, suscripciones ni despliegue público en esta entrega.

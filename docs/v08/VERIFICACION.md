# Distrito Cero v0.8 · Presencia · Verificación

11 de septiembre de 2026. Incremento sobre **Horizonte v0.7**, con ocupantes integrados en la simulación regional y una revisión del reparto. Esta entrega no está certificada como AAA ni como fotorrealista.

## Identidad de la entrega

HTML: **4,580,240 bytes**. SHA-256:

`771fcc31fd4477face0c941b3fbb80428717d95a9e501dacf22a11eb6b31e92a`

El manifiesto comprobable está en `qa/v08/release-report.json`. Los informes actuales de integración y bucle continuo contienen esta misma huella. No se suman pases de versiones antiguas.

## Resultado de las ejecuciones finales

| Grupo | Comprobaciones satisfactorias | Fallos |
| :--- | ---: | ---: |
| Lógica con Node, núcleo, policía, territorio y sistemas de v0.8 | 157 | 0 |
| Ocupación, NPCs, mallas, cristales y acceso táctil | 71 | 0 |
| Regresión de campaña, conducción e interfaz | 52 | 0 |
| Regiones, semilla, atlas, persistencia y sectores | 84 | 0 |
| Render y simulación continuos con teclado real | 15 | 0 |
| Geometría final del cabello respecto al cráneo | 1 | 0 |
| Estructura, rig y clips de los GLB locales | 2 | 0 |

**222 comprobaciones de navegador**, además de las 157 pruebas de lógica y tres pruebas de geometría/exportación. Son aserciones automatizadas, no 222 sesiones independientes ni una certificación exhaustiva del mundo abierto. Las ejecuciones finales terminaron sin excepciones JavaScript registradas, sin errores WebGL detectados y sin solicitudes de recursos de red.

## Qué se comprobó

**Ocupación.** Un coche civil en circulación o una patrulla tiene un conductor identificable. El coche inicial del jugador está vacío. El acceso distingue extracción y entrada vacía. El asiento se reserva mientras transcurre la secuencia y el control no se transfiere hasta terminar. Se prueban cancelación por F, movimiento, salto, desplazamiento brusco del coche, salida cancelada, puerta bloqueada y rechazo de vehículos rápidos. El conductor liberado no se duplica al repetir una acción.

**Persistencia.** Identidades de vehículos y conductores, conductor expulsado, estado de ocupación y daño de las cuatro zonas se recuperan. Se añade regresión del defecto que aplicaba el daño de un coche ocupado al coche inicial al cargar. Un guardado a mitad de transición restaura un estado lógico seguro, no la pose intermedia. Las partidas anteriores sin sección `occupancy` se admiten. Esto no valida compartir automáticamente localStorage entre archivos HTML diferentes.

**Animación y mallas.** Tres niveles de detalle deterministas, pesos normalizados y normales válidas. Matrices independientes por actor y geometría compartida, postura sentada sin encoger el cuerpo, alcance acotado de manos por IK, continuidad de trayectorias durante extracción y recolocación, parpadeo desfasado y materiales ligados a la malla. Se comprueba que los pasos de color y sombra consumen la pose. El hueco de la puerta se aplica también a la sombra.

**Navegador.** Entradas nativas de teclado y eventos táctiles emulados en 390 × 844 y 844 × 390. El botón de acceso cambia a CANCELAR durante la transición. Se inspeccionaron fotogramas de coche ocupado, extracción, reparto, rostro y uniformes. La escena de multitudes usa mallas compartidas y las distancias seleccionan los niveles de detalle, sin una copia completa de geometría por persona.

**Campaña y mundo.** La suite heredada vuelve a recorrer el desenlace público de la campaña, conducción, freno, pausa, exportación/continuación, encargo y controles. La suite de Horizonte recorre sus 84 comprobaciones, incluidos atlas, semilla, destinos, objetos restaurados y límites de sectores. Se mantuvieron las 25 celdas activas y el origen relativo. Las ubicaciones de inspección y objetivos pueden prepararse directamente para comprobar una transición, no se presenta esto como una partida íntegra espontánea.

**Bucle continuo.** Sin sustituir métodos de simulación, cámara, render o RAF: tecla F real para extracción y entrada, control posterior del coche, freno y salida, movimiento a pie y conducción cruzando un límite de sector. El escenario parte de posiciones preparadas para reproducirlo. También verifica atlas, viaje y límites de recursos. No es una prueba de rendimiento en GPU física.

## Presupuesto geométrico de esta versión

| Recurso | Cantidad |
| :--- | ---: |
| Personaje de detalle alto | 43,579 triángulos |
| Personaje de detalle medio | 15,206 triángulos |
| Personaje lejano | 3,335 triángulos |
| Huesos por personaje | 17 |
| Capacidad de la textura de paletas | 128 actores |
| Memoria de esa textura, exclusivamente | 139,264 bytes |
| NPCs desalojados persistentes | Máximo 24 |

La cifra de la textura **no es la memoria total del juego**. No incluye geometría, sectorización, framebuffer, sombras, reflejos, almacenamiento JavaScript ni otros buffers. La capacidad no es una promesa de 128 personajes simultáneos a 60 FPS. El mundo utiliza población local acotada.

## Recursos y procedencia

Las mejoras del rostro, cabello y ropa de esta entrega son modelado original procedural local. No se importó un escaneo, MakeHuman ni un GLB remoto nuevo de Higgsfield. El historial anterior de autoría permanece descrito en `assets/README.md`.

Los modelos `assets/dc08-hero-native.glb` y `assets/dc08-coupe-native.glb` se exportaron de los datos locales. La prueba comprueba cabecera y tamaños de GLB, rangos de buffers, índices, normales unitarias, pesos, huesos, tiempos de animación y bucles. El humano tiene 17 huesos y cinco estudios de locomoción/postura. La extracción, los objetivos IK y el parpadeo del shader son del runtime, **no clips incluidos en esos GLB**. No se ejecutó el validador oficial Khronos y no se afirma compatibilidad certificada con todos los programas 3D.

## Revisión visual y correcciones

Se corrigió el salto del jugador entre la extracción y la entrada, incorporando una trayectoria de recolocación. Se redujo la superposición de los torsos durante el tirón. Esto no elimina todas las intersecciones de manos, cuerpo y ropa en poses extremas.

La carrocería tenía una puerta cerrada detrás de la pieza móvil. Ahora la abertura está en color y sombra. Se corrigió el detalle de tela que se deslizaba al usar coordenadas después de deformar la malla.

La primera revisión del vídeo reveló parches del cráneo atravesando el cabello. Una prueba sobre los vértices reales cuantizados reprodujo el problema. El cabello final se ajusta al perfil anatómico y la prueba vuelve a pasar. Después de ese cambio se regeneraron los GLB y se ejecutó **otra vez toda la batería final**, no sólo la prueba del pelo.

## Entorno e incidencias del laboratorio

Chromium bajo Xvfb, Linux y ANGLE SwiftShader. Las páginas se inyectan con `set_content`; el almacenamiento se aísla en memoria por las restricciones del origen del laboratorio. No se valida persistencia nativa `file://` entre aperturas, Safari, Firefox, teléfonos físicos ni la GPU del usuario.

Las suites por estados congelan la programación de fotogramas o el renderer entre pasos controlados de simulación y capturas WebGL reales. Se conservan las reglas del juego. La suite continua usa el bucle original para comprobar la integración temporal. Es una distinción deliberada, no una medición artificial de FPS.

Una ejecución larga iniciada mediante el lanzador del contenedor se interrumpió por el proceso anfitrión. Se repitió con proceso local aislado y registros conservados. Las ejecuciones finales cerraron sus navegadores normalmente. Las capturas iniciales que encontraron defectos no se usan como evidencia del modelo final.

## Evidencia de animación

`tests/presence_clip.py` reproduce los estados con pasos de simulación de 1/60 s y exporta fotogramas reales del renderer a 24 FPS. La captura de cada frame puede tardar más que ese intervalo. El vídeo está rotulado **tiempo de animación controlado**, no es una grabación de rendimiento en tiempo real ni contiene interpolación o imágenes generadas. `qa/v08/clip-report.json` registra las fases capturadas.

Las capturas `review-*.png` usan posiciones y cámaras de inspección, no encuadres espontáneos de una partida. No se usó un render de Blender para representar el resultado del navegador.

## Archivos de comportamiento conservados

La comparación binaria contra el commit base `e61b0fe` comprueba que siguen intactos `core.js`, `world.js`, `police.js`, `simulation.js`, `dynamics.js`, `interactions.js`, `character-motion.js`, `frontier-world.js`, `frontier-simulation.js`, `frontier-renderer.js`, `frontier-ui.js`, `visual-geometry.js` y `audio.js`. Las extensiones nuevas se integran después. Esto mantiene las reglas anteriores y no sustituye la verificación de las interacciones entre ellas.

## Limitaciones vigentes

El resultado sigue siendo estilizado. No hay texturas faciales fotográficas, pelo por mechones, rig de dedos, captura de movimiento, ragdoll físico con recuperación ni colisiones exactas de cada miembro. Las variantes de reparto comparten familia corporal, no rostros únicos escaneados. La policía desalojada reacciona y se aleja, y el incidente puede elevar la búsqueda, no tiene un sistema nuevo de combate a pie.

El territorio conserva relieve transitable plano, retícula vial principalmente ortogonal y generación por lotes en el hilo principal. No se verificaron sesiones de horas, explotación de todas las misiones emergentes, pérdida/restauración del contexto WebGL, todos los extremos del dominio espacial ni rendimiento de dispositivos físicos.

## Reproducir

```bash
python build.py
node --test tests/*.test.cjs
python tests/presence_mesh.test.py
python tests/presence_exports.test.py
DISPLAY=:99 python tests/presence_browser.py
DISPLAY=:99 python tests/legacy_presence.py
DISPLAY=:99 python tests/horizon_presence.py
DISPLAY=:99 python tests/presence_continuous.py
DISPLAY=:99 python tests/presence_clip.py
DISPLAY=:99 python tests/presence_capture.py driver
```

Chromium, Playwright, Xvfb, ffmpeg y las bibliotecas de autoría Python se usan sólo al desarrollar o producir evidencia. No se requieren para abrir el HTML. Ajustar las rutas de Chromium/display al sistema de pruebas. No se distribuyen fuentes tipográficas.

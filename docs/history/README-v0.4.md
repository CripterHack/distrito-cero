# DISTRITO CERO
## v0.4 · Ciudad reactiva

9 de septiembre de 2026. Aventura criminal original de navegador, en tercera persona, con campaña, exploración, conducción y persecuciones. Esta actualización convierte parte del decorado en objetos físicos e incorpora daño localizado e interacciones del personaje.

**Jugar:** abre `index.html` en un navegador con WebGL2. No requiere npm, bibliotecas externas, recursos remotos, cuenta ni conexión durante el juego. Para publicarlo, basta ese HTML como `index.html` en un alojamiento estático. La vista previa de un chat o gestor de archivos puede no ejecutar WebGL.

**Estado:** versión jugable de desarrollo. Geometría de detalle contenida, animación procedural y física simplificada. No es hiperrealismo AAA, captura de movimiento, destrucción volumétrica ni un motor de carrocerías deformables.

## Empezar

Pulsa **Entrar a la ciudad** para la historia, o **Explorar sin historia**. Cerca del cruce inicial hay cajas y un cono. Acércate, recoge una caja con **E** y lánzala con **G**. También puedes empujar el coche parado sin subirte, entrar con **F**, conducir y comprobar la reacción del mobiliario. El teléfono iluminado conserva el inicio de la campaña.

Pausa permite suspender y retomar la historia. El menú **I · Interacciones** explica los verbos nuevos sin mantener un panel grande sobre el escenario.

## Controles

| Acción | Control |
| :--- | :--- |
| Caminar, acelerar, reversa y dirección | WASD o flechas |
| Correr | Shift |
| Entrar o salir de un coche próximo | F, a velocidad suficientemente baja |
| Recoger, soltar, restaurar o interactuar con objetivos | E |
| Lanzar lo que sostienes, empujar mobiliario o un coche parado | G |
| Agacharse o incorporarse | X |
| Esquivar a pie / bocina al conducir | Q |
| Saltar a pie / freno de mano al conducir | Espacio |
| Reparar junto a un coche dañado | Mantener V durante 3 segundos |
| Ayuda de interacciones | I |
| Mirar | Arrastrar sobre el escenario |
| Cambiar cámara | C |
| Mapa y destino GPS | M y clic en el mapa |
| Modo foto / radio sintetizada | P / T |
| Rendición voluntaria | Mantener R durante 1.8 segundos ante una patrulla visible |
| Pausa, ajustes, guardado | Esc |

Los controles táctiles ofrecen joystick, subir/bajar, acción, empujar/lanzar, correr/freno, esquivar/bocina y salto. Agacharse está en el panel de interacciones. Reparación y rendición tienen botones que deben mantenerse pulsados. Soltar el dedo, recibir una cancelación de puntero o perder el foco cancela la pulsación.

## Implementado en v0.4

### Entorno físico

**555 objetos** de seis clases: postes, árboles, cajas, botes de reciclaje, conos y bancas. Tienen identificadores estables y estado independiente en cada partida. Las consultas cercanas utilizan una cuadrícula espacial. No se ha convertido toda la ciudad en destruible: edificios, semáforos, refugios y elementos de misión siguen siendo estáticos.

Postes y árboles sólidos resisten contactos leves. Un impacto suficientemente fuerte los derriba con una animación de caída por bisagra. El brazo de la luminaria o la copa detienen la caída antes de quedar enterrados en el suelo. La lámpara pierde su emisión y deja de iluminar el entorno. El sistema conserva daños y posiciones en el guardado.

Cajas, botes, conos y bancas pueden desplazarse. Los objetos pequeños se recogen y lanzan, con gravedad y rebote. Un objeto lanzado puede dañar un coche. Los fragmentos son efectos visuales limitados, no cuerpos rígidos permanentes. Los troncos y postes rotos dejan de bloquear al jugador para evitar encerrarlo. No hay fractura arbitraria de mallas ni colisión de cada hoja o esquirla.

**Restaurar:** pulsa E cerca de la base de un objeto roto. Cuesta **$60 del juego**, requiere no tener búsqueda y que la base esté libre. No hay premios por destruir árboles.

### Vehículos

Daño separado en frente, parte trasera, izquierda y derecha. Los impactos alteran la salud y el aspecto. Hay hundimiento paramétrico de la zona dominante de la carrocería, capó y defensas desalineados, marcas, cristal dañado, faros apagados cuando el frente se deteriora y humo con transparencia. No se promete simulación soft-body.

Las ruedas giran con el desplazamiento y las delanteras responden al giro. La carrocería cabecea al acelerar/frenar y se inclina durante los giros. Los impactos producen impulsos visuales breves. El freno deja marcas a velocidad suficiente. El daño frontal reduce moderadamente las prestaciones, sin reintroducir el frenado acumulativo por roce corregido en v0.3.

La reparación manual requiere estar a pie, parado cerca del coche, sin ser visto por la policía y disponer de **$90 del juego**. Se cobra sólo al completar los 3 segundos. Moverse, soltar el control o perder las condiciones reinicia el progreso sin cobro. El taller anterior sigue costando $200 e incluye pintura. Ambos restablecen la apariencia dañada. El daño de vehículos desocupados también se conserva.

### Personaje

Aceleración y desaceleración amortiguadas. La marcha se alimenta con distancia realmente recorrida, no sólo con la intención de avanzar contra una pared. Agacharse reduce la velocidad y mezcla la postura. Hay esquiva con recuperación, reacción corporal a impactos, agarre/lanzamiento y reparación. Mantener salto no genera saltos repetidos automáticamente.

El apoyo de los pies usa un solucionador analítico de dos segmentos para ajustar cadera, rodilla y tobillo sobre el suelo plano. No es IK de terreno arbitrario ni un personaje con piel continua. El cuerpo sigue siendo un rig procedural de piezas articuladas.

Entrar y salir presenta interpolación del ocupante y apertura/cierre de la puerta. Son transiciones visuales simplificadas: la asignación lógica del coche continúa siendo inmediata. No hay todavía alcance exacto de manos a manijas, marcha completa alrededor del coche ni un clip de mocap retargeteado.

### Higgsfield integrado, no sólo una ilustración

Se creó un coupé original y editable con **Higgsfield 3D Jutsu / Blender**, dividido en 154 objetos semánticos. La carrocería y cuatro piezas de cristal del GLB se extrajeron, validaron y convirtieron al formato del motor: **820 triángulos importados**. Se incluyen esos datos geométricos y el conversor.

El resto de las piezas visibles del coche son reconstrucciones procedurales nativas: ruedas, capó, defensas, techo, asientos, puertas y luces. La animación del juego también es procedural. El modelo de detalle se usa cerca del jugador y se conserva la versión económica a distancia.

`assets/README.md` contiene la procedencia, el proyecto editable y la descarga del GLB completo con su render de referencia. Ese ZIP externo es opcional para edición: el juego NO lo descarga. El ZIP de código contiene la geometría nativa incorporada, no una copia del archivo `.blend` del servicio.

## Conservado de las versiones anteriores

Ciudad de 840 × 840 metros con 392 edificios, parques, tráfico y peatones de comportamiento básico. Campaña de seis etapas y dos desenlaces, entregas repetibles, circuito nocturno, talleres, refugios y 16 alijos. Mapa, minimapa, GPS, modo foto, audio sintetizado, dinero y estadísticas.

Se conservan las reglas de contacto policial de v0.3. La captura requiere baja velocidad real, proximidad y visibilidad. Las patrullas pierden las coordenadas actuales cuando no ven al jugador, buscan la última posición conocida y se recolocan tras un impacto. Rendirte cuesta $150, ser arrestado $300. La historia se conserva.

## Guardado y privacidad

El esquema externo permanece en `version: 1`, con campos nuevos opcionales. v0.4 puede importar partidas antiguas. Se guardan historia, saldo, salud, posición, vehículo ocupado, búsqueda, alijos, estadísticas, objetos alterados y vehículos desocupados dañados o empujados.

No se restaura el instante exacto de toda la simulación. No se guardan velocidades de fragmentos, objetos en las manos, reparación a medias, temporizadores de contratos ni animaciones a mitad de ciclo. Los objetos móviles cargan en reposo. Las posiciones y daños persistentes se validan antes de aplicar la extensión.

**Exporta la partida en v0.3 y luego impórtala en v0.4.** Dos HTML locales no necesariamente comparten almacenamiento. El navegador puede restringir localStorage. El guardado automático se intenta cada 25 segundos y hay respaldo JSON en Pausa. No hay cuentas, analítica, telemetría ni envío de partidas.

## Estructura y construcción

| Archivo | Responsabilidad |
| :--- | :--- |
| `src/core.js`, `world.js` | Matemáticas, poses base, ciudad, rutas y capítulos |
| `src/police.js`, `simulation.js` | Núcleo heredado de juego y reglas policiales |
| `src/dynamics.js` | Props, hash espacial, contactos, daño, caída, partículas y persistencia |
| `src/interactions.js` | Extensión de simulación, movimiento, recoger/lanzar, reparación, transiciones |
| `src/character-motion.js` | Poses adicionales y apoyo analítico de pies |
| `src/vehicle-asset.js` | Datos de malla propios, generados por el conversor |
| `src/renderer.js` | WebGL2, materiales, sombras, reflejos y pases de dibujo |
| `src/reactive-renderer.js` | Vehículo modular, objetos, puertas y humo transparente |
| `src/audio.js`, `app.js` | Síntesis, entradas, interfaz, mapa y bucle |
| `src/page.html`, `style.css` | Plantilla e interfaz adaptable |
| `assets/higgsfield-body.json` | Subconjunto validado de la malla GLB original |
| `tools/convert_vehicle.py` | Conversión del subconjunto JSON a buffers nativos |
| `build.py` | Empaquetado autónomo, biblioteca estándar de Python |

El orden de carga es importante. Las extensiones sustituyen `DC.Simulation` y `DC.Renderer` después de definir el núcleo y antes de crear la aplicación. La simulación decide daños y estados. El render sólo los representa.

```bash
python tools/convert_vehicle.py
python build.py
node --test tests/*.test.cjs
```

Python y Node sólo son herramientas de desarrollo. Para jugar basta `index.html`.

## Pruebas

Los resultados y límites se describen en `docs/v04/QA.md` y `qa/v04/release-report.json`. Incluyen lógica determinista, campaña, controles, persecuciones, móvil emulado y un pase con renderer continuo real. Playwright es exclusivamente herramienta de pruebas, no dependencia de distribución.

```bash
# Linux, con Playwright, Chromium y Xvfb ya instalados.
xvfb-run -a python tests/reactive_browser.py
xvfb-run -a python tests/browser_qa.py
# Procesos separados evitan acumulación de contextos SwiftShader en el laboratorio.
xvfb-run -a python tests/police_browser.py desktop
xvfb-run -a python tests/police_browser.py 390
xvfb-run -a python tests/police_browser.py 844
xvfb-run -a python tests/continuous_reactive.py
```

Las rutas de Chromium están documentadas en los scripts. La prueba continua termina únicamente su propio navegador al finalizar las aserciones porque el cierre normal del Chromium/SwiftShader del laboratorio puede bloquearse. Esto no modifica el juego ni sus bucles durante la medición.

## Límites y plan siguiente

No se han probado Safari, un iPhone físico, Android físico ni una GPU de escritorio real. No hay una promesa medida de 60 FPS. Usa calidad Económica y desactiva reflejos si hace falta. La geometría y los shaders permanecen deliberadamente contenidos.

El plan completo está en `docs/v04/PLAN-INTEGRAL.md`. Quedan pendientes malla humana continua con skinning, materiales PBR completos y texturas de detalle, manos sobre manijas, IK de pendientes, ragdoll, piezas verdaderamente desprendibles, interiores transitables y comportamiento social avanzado de NPC. El plan no implica que esos sistemas ya estén en esta entrega.

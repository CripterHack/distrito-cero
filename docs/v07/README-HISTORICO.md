# Distrito Cero · Horizonte v0.7

Expansión procedural de Distrito Cero, construida sobre la fuente recuperable de v0.5. Un HTML autónomo, JavaScript y WebGL2 nativos. No hay bibliotecas de runtime, CDN, login, instalación, telemetría ni peticiones de recursos durante una partida.

## Jugar

Abre `index.html` directamente en un navegador con WebGL2 y aceleración gráfica. También puede publicarse como un único archivo en alojamiento estático. Las herramientas de desarrollo no son requisitos para jugar.

Pulsa **Entrar a la ciudad** para la campaña o **Explorar sin historia** para pausar sus objetivos. La opción **Atlas de regiones** inicia o continúa la partida y abre el atlas.

**M** abre el mapa. Hay dos vistas, Calles y Regiones, zoom, recentrado, cinco destinos iniciales y viaje a un punto marcado. Toca una carretera para marcar un GPS. Puedes seguir conduciendo de una región a otra sin usar el viaje rápido. Una ruta muy lejana se calcula por tramos y se actualiza al avanzar.

Los viajes rápidos llevan al jugador y a su vehículo actual. No conceden dinero, reparación ni otro coche. No están disponibles mientras el vehículo se mueve, hay persecución, encargo activo, transmisión o transición del personaje. Detente para utilizarlos.

### Regiones

| Ruta inicial | Tipo | Escenario |
| :--- | :--- | :--- |
| Distrito Cero | Urbano | Ciudad original y localizaciones de la campaña |
| Nueva Aurora | Futurista | Torres curvas, bandas luminosas y paneles solares |
| Santa Cobalto | Retro | Edificios de menor altura, balcones, tejados y comercios |
| San Lucero | Rural | Casas, patios, caminos y servicios locales |
| Vega Abierta | Campo | Parcelas de cultivos, graneros, invernaderos y canales de riego |

También se generan periferias y corredores forestales. Los estilos coexisten en una misma geografía ficticia, no representan saltos temporales. Los centros regionales, densidades y materiales varían con la semilla. El terreno transitable sigue siendo plano.

### Controles

| Acción | Control |
| :--- | :--- |
| Caminar / conducir | WASD o flechas |
| Entrar / salir del vehículo | F |
| Interactuar, recoger, restaurar | E |
| Lanzar / empujar | G |
| Agacharse | X |
| Esquivar a pie / bocina al volante | Q |
| Reparar junto al vehículo | Mantener V |
| Rendirse ante una patrulla | Mantener R |
| Correr a pie | Shift |
| Saltar / freno de mano | Espacio |
| Mirar | Arrastrar sobre la escena |
| Cambiar cámara | C |
| Atlas / foto / radio | M / P / T |
| Pausa | Escape |

Los controles táctiles se activan automáticamente o desde ajustes. El atlas y sus destinos son accesibles también con botones. En Pausa, **Luz · noche a día** modifica la iluminación. El mundo no cambia cuando eliges calidad económica.

## Semillas y guardados

En el atlas, abre **Semilla y generación**. Escribe un entero de 32 bits y selecciona **Crear nueva partida**. La confirmación informa que se reemplazará el guardado. Exporta primero una copia para conservarlo.

Se puede importar una partida de v0.5. Exporta desde el HTML anterior e importa desde Pausa en la nueva versión, sin asumir que el navegador comparte almacenamiento entre archivos locales. No se garantiza migración inversa: la versión antigua no entiende ubicaciones lejanas ni estados de la expansión.

La geometría se vuelve a generar a partir de la semilla. Los objetos exteriores modificados tienen identificadores estables y un archivo disperso de hasta **4096 cambios**, con aviso al alcanzar el límite. Los 555 objetos originales mantienen su guardado anterior. Hasta 2048 centros visitados se registran como descubrimientos. Los fragmentos temporales no se guardan.

## Qué significa expansión indefinida

No es un mapa pregenerado enorme ni una promesa de infinito matemático. El generador crea parcelas por coordenadas cuando son necesarias, sin una frontera de diseño alrededor de la ciudad original. El límite numérico deliberado está cerca de ±1 000 000 000 m por eje, con un margen técnico de seguridad. No se han recorrido físicamente todas esas coordenadas ni se promete que cada parcela sea visualmente única.

La malla activa usa una ventana de **5 × 5 sectores de 336 m**, con hasta 25 sectores residentes. La caché CPU se limita a 64 descriptores de sector y 768 parcelas. Los buffers GPU de sectores salientes se liberan. La generación geométrica se reparte por fotogramas, con dos sectores nuevos por render, pero no se ejecuta en un Worker: en hardware lento puede haber tirones. Las posiciones autoritativas usan números de doble precisión y el renderer recibe coordenadas relativas al origen cercano a la cámara.

## Arquitectura

`frontier-world.js` genera centros, zonas, edificios, props, carreteras y rutas con semilla. `frontier-simulation.js` conecta los sectores con colisiones, objetos, guardado, tráfico y encargos. `frontier-renderer.js` construye y libera los buffers de cada sector. `frontier-ui.js` implementa el atlas y los controles nuevos. La geometría no decide dinero ni misiones.

Los caminos compartidos se calculan con una función canónica de borde, por lo que dos parcelas vecinas coinciden. Las arterias conectan regiones, las calles secundarias dependen del uso de ambos vecinos y los edificios respetan la reserva vial. Esta versión conserva una retícula ortogonal, no una red vial orgánica guiada por topografía.

## Construir y probar

```bash
python build.py
node --test tests/*.test.cjs
DISPLAY=:99 python tests/horizon_browser.py
DISPLAY=:99 python tests/horizon_continuous.py
DISPLAY=:99 python tests/legacy_horizon.py
DISPLAY=:99 python tests/horizon_capture.py future
```

Las suites gráficas utilizan Python, Playwright, Chromium y un display de pruebas. Chromium se configura por defecto como `/usr/bin/chromium`, con SwiftShader para el laboratorio. No son dependencias del juego. La navegación del navegador está bloqueada por políticas de este entorno, por lo que las suites inyectan el HTML y usan almacenamiento aislado en memoria. El bucle continuo no sustituye renderer, cámara ni simulación.

Consulta `docs/v07/VERIFICACION.md` y `qa/v07/release-report.json` para resultados, alcance, reintentos y límites de cobertura. Las imágenes `region-*.png` son capturas del renderer con cámaras de inspección preparadas, no imágenes generadas por IA.

## Estado artístico y tareas pendientes

Es una expansión funcional de un prototipo estilizado, no un juego AAA terminado. Mantiene el personaje skinned de v0.5 y sus NPCs. La implementación incompleta de v0.6 no se recuperó a partir de sus capturas. No se afirma que estén integradas la nueva anatomía, la extracción de conductores o los conductores civiles visibles.

Quedan pendientes terreno con desniveles físicos, ríos regionales, interiores, red vial orgánica, LOD más fino, generación en Workers, persistencia regional más amplia y mejora artística de humanos y vehículos. Los árboles/objetos destruibles y el daño de vehículos conservan la física simplificada existente. El arte de la ciudad, iluminación y geometría procedural tampoco equivalen a fotogrametría o fotorrealismo.

Los recursos heredados y su procedencia están en `assets/README.md`. En esta entrega no se generaron modelos nuevos en Higgsfield ni se incorpora una biblioteca de mapas o modelos de terceros.

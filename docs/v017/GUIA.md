# Distrito Cero v0.17 · Arsenal

Extensión directa de Rasgos v0.16. JavaScript y WebGL2 nativos, un HTML autónomo y cero librerías de ejecución externas. Esta versión añade equipamiento jugable, no un rediseño de personajes. Todos los nombres, cifras de potencia, carga, alcance e interrupción son reglas ficticias para un videojuego.

## Comenzar

Abrir `index.html` descargado en el navegador, fuera de la vista previa del chat. Para un hosting estático basta publicar ese archivo como `index.html`. Crear personaje o importar una partida desde Mis partidas. Se comienza con manos libres. El catálogo completo está disponible para experimentar, pero los consumibles se agotan.

Pulsar **Tab** o el botón **▦ / TAB** para abrir el selector. Filtrar una categoría, elegir una tarjeta y pulsar **Equipar**. La selección pausa el mundo. Cerrar con Escape o × descarta la elección pendiente. También está en Pausa → Equipamiento.

## Controles

| Acción | Teclado y ratón |
| :--- | :--- |
| Abrir equipamiento | Tab |
| Usar equipo | Clic izquierdo o J |
| Apuntar / observar | Mantener clic derecho o alternar Z |
| Mover la vista armado | Arrastrar con clic derecho |
| Recargar | L |
| Elegir arma con acceso directo | 1 a 9 y 0 |
| Elegir equipo anterior o siguiente | [ y ] |
| Manos libres | Tecla de acento grave (Backquote) |
| Alternar binoculares / manos libres | B |
| Zoom de binoculares | Rueda, + o − |
| Marcar lo observado en GPS | H, botón GPS o disparo mientras observas |
| Abrir mapa / pausa | M / Escape |

**R sigue siendo rendición policial, no recarga.** F conserva entrada/salida/cancelación de coche, E interactúa, G empuja/lanzar objetos, X agacha, Q esquiva, V mantiene reparación y Espacio salta/frena. Con arma, el jugador puede moverse y apuntar, pero no dispara desde vehículos, durante acceso, con una caja en las manos, al esquivar, al rendirse o al reparar.

En táctil, abrir ▦, seleccionar y equipar. Los botones **FUEGO/CARGAR/PULSO** y **APUNTAR/OBSERVAR** se mantienen pulsados. Se mira arrastrando directamente sobre el mundo, sin disparar con ese arrastre. Hay recarga, alternancia de apuntado, zoom y marcador GPS en el panel de equipo. Soltar CARGAR libera Gauss. Cancelar el gesto, perder el foco o abrir una pantalla cancela la carga sin dispararla.

## Catálogo

| Categoría | Opciones y comportamiento |
| :--- | :--- |
| Esenciales | Manos libres |
| Cuerpo a cuerpo | Bastón y hoja táctica, con alcance corto y contacto bloqueado por edificios |
| Armas cortas | Pistola Vector (1) y Revólver Nexo (2), semiautomáticos |
| Armas largas | Subfusil Kestrel (3), escopeta Umbral (4), fusil Horizonte (5) y precisión Faro (6) |
| Explosivos | Lanzador Atlas (7) y granada con mecha de 2.4 s (8) |
| Tecnología | Cañón Gauss (9) y emisor EMP (0) |
| Observación | Binoculares (B) |

El subfusil y el fusil repiten disparos al mantener el control. Las armas semiautomáticas requieren una nueva pulsación. La escopeta genera ocho impactos dispersos. Precisión Faro reduce el campo de visión a una óptica 4× mientras apuntas. Lanzador y granada tienen proyectiles visibles y colisión barrida. La granada describe un arco, rebota o reposa, y detona al vencer la mecha. Los explosivos pueden dañar al jugador si está cerca.

### Cañón Gauss

Mantener clic izquierdo, J o CARGAR. La carga completa tarda **1.5 segundos de simulación**. Soltar dispara con la potencia acumulada, siempre que se haya alcanzado el mínimo del 23 %. Las cargas inferiores se descartan sin gastar una celda. Cada tiro consume una celda de las tres cargadas. Puede atravesar hasta tres vehículos, objetos o personajes alineados con potencia decreciente, pero **un edificio o el terreno detiene el tiro**. La recarga usa la reserva de 21 celdas iniciales.

Abrir el selector, cambiar equipo, pausar, perder el foco o iniciar otra interacción cancela la carga. Una pulsación nueva después de seleccionar equipo puede utilizarlo aunque no hubiera ocurrido aún un fotograma neutral. No se reciclan entradas que estaban mantenidas antes de cancelar.

### Emisor EMP

Pulso de **26 metros**, con oclusión por edificios, que interrumpe durante **8 segundos** la propulsión de coches y patrullas y apaga luces cercanas compatibles. Los coches que ya se mueven desaceleran, no se teletransportan. El daño de los vehículos y objetos se conserva. El pulso no daña la salud de personas ni repara vehículos.

**La búsqueda no desaparece.** Los policías todavía pueden verte y el sistema de captura existente sigue funcionando cerca de una patrulla. El EMP es una regla de juego, no una simulación física de electromagnetismo, blindaje o electrónica real.

### Binoculares

Activar apuntado con Z, clic derecho sostenido o OBSERVAR. Hay **2×, 4×, 8× y 12×** mediante cambio real del campo de visión, no sólo un recorte CSS. Indican azimut de la vista y distancia al primer volumen o superficie detectada dentro de 600 metros. Un edificio impide consultar lo que queda detrás. En el horizonte sin retorno no se inventa una medición.

H marca en el GPS la superficie observada. Los binoculares no consumen munición ni generan búsqueda. La medición utiliza los colisionadores simplificados del mundo, no el contorno exacto de cada triángulo visible. No hay visión térmica o a través de paredes.

## Munición y consecuencias

Cada equipo tiene cargador, reserva, cadencia y recarga. Una recarga termina transfiriendo únicamente las unidades que faltan y no consume munición al iniciarse. Cambiar de arma cancela una recarga sin conceder unidades extra. Con un cargador vacío se puede iniciar recarga automáticamente al intentar usar un arma convencional, o manualmente con L para cualquier arma, incluido Gauss.

Se puede **reponer munición y celdas por $120 del juego** en la taquilla del cruce inicial, talleres o refugios. Hay que estar a menos de nueve metros, detenido y sin búsqueda. El selector muestra el punto más próximo y puede marcarlo en GPS. Estar dentro de un menú no elimina la condición de detenerse antes. No se cobran recursos externos ni dinero real.

Disparar/golpear/pulsar EMP puede generar búsqueda y alarma de peatones. Los impactos reutilizan el daño localizado del vehículo y la destrucción de objetos existente. Los edificios siguen siendo estáticos. Los NPCs reciben una reacción no gráfica y, tras agotar su resistencia, quedan temporalmente incapacitados y se recuperan después de 12 s. No se añadió sangre, un ragdoll físico o combate armado policial.

## Guardados y compatibilidad

El equipamiento se serializa dentro de cada partida independiente: selección, munición, reservas, zoom y contadores. El catálogo conserva sus nombres, IDs, doce espacios máximos sujetos a cuota, claves y funciones de copiar/importar/exportar. Los JSON anteriores sin sección de equipamiento se cargan con manos libres e inventario inicial.

**Exportar antes de cambiar de HTML.** Los datos continúan siendo locales al navegador, sin nube. No se garantiza que un HTML distinto comparta el almacenamiento del anterior. Esta entrega prueba serialización y restauración con almacenamiento aislado en memoria, no persistencia nativa después de cerrar y reabrir un archivo local.

Los proyectiles en vuelo, cargas, recargas en curso, impactos visuales, EMP activo y resistencias/reacciones temporales de los NPCs no se guardan. Al cargar se conserva la munición gastada y el daño permanente serializable, no la continuación exacta de esos efectos transitorios.

## Alcance visual

Las armas son modelos originales procedurales compartidos, con materiales diferenciados, iluminación de carga, fogonazos, trazos y ondas visibles. El jugador tiene objetivos de muñeca para sujetarlas, animación aproximada de retroceso, golpe, lanzamiento/recarga. No hay manipulación mecánica completa de cargadores, contactos por falange, balística avanzada, disparos desde coches ni nuevos modelos de personaje. El peinado, cuerpo, cuello y las animaciones de base de Rasgos v0.16 se conservan.

`assets/dc017-equipment.glb` contiene trece modelos de equipo sin el personaje, en una galería por grupos. Está generado desde la misma geometría del juego, con materiales portables. El HTML no necesita descargarlo. No contiene esquemas, despieces ni parámetros para fabricar armas.

## Desarrollo y verificación

```
python build.py
node --test tests/*.test.cjs
python tools/export_equipment.py
python tests/arsenal_exports.test.py
DISPLAY=:99 python tools/run_arsenal_browser.py
DISPLAY=:99 python tests/arsenal_capture.py gauss
DISPLAY=:99 python tests/arsenal_capture.py emp
DISPLAY=:99 python tests/arsenal_capture.py optics
```

Python, Node, Chromium, Playwright y Xvfb se utilizan al desarrollar, no al jugar. La suite por estados pausa la programación de RAF después del arranque, aplica entradas DOM reales, avanza la simulación y dibuja fotogramas WebGL explícitos. La suite continua mantiene el bucle sin sustituciones. Adaptar display/ruta de Chromium al entorno. No se anuncian FPS de una GPU física a partir del laboratorio por software.

# Verificación de Distrito Cero v0.4

9 de septiembre de 2026. Informe del incremento «Ciudad reactiva». Los recuentos son **aserciones**, no sesiones independientes ni una certificación de producción. Los datos estructurados y la huella del HTML están en `qa/v04/release-report.json`.

## Resultado de la entrega

| Grupo | Comprobaciones satisfactorias | Fallos en la ejecución final |
| :--- | ---: | ---: |
| Lógica con Node: núcleo, policía y sistemas nuevos | 96 | 0 |
| Interacciones, daño, destrucción e interfaz nueva | 137 | 0 |
| Regresión de campaña e interfaz anterior | 52 | 0 |
| Policía en escritorio | 26 | 0 |
| Policía en pantalla vertical | 25 | 0 |
| Policía en pantalla horizontal | 25 | 0 |
| Bucle continuo de render, teclado y simulación | 10 | 0 |

Las suites de navegador suman **265 comprobaciones**, más las **10 del bucle continuo**. Las tres ejecuciones de policía repiten sus comprobaciones globales de ausencia de errores y de peticiones externas. No se presentan como 76 escenarios policiales distintos. No hubo errores JavaScript/WebGL ni solicitudes de recursos externos en las ejecuciones finales.

## Qué se ejecutó

**Lógica.** Los 70 casos heredados se mantuvieron, junto con 26 casos nuevos. La suite prueba estado independiente de objetos, choque de alta y baja velocidad, lámparas que dejan de iluminar, contactos que no dañan cada fotograma, caída y límites de suelo, paso temporal finito, selección de zonas de daño, restauración, recogida, lanzamiento, empuje, reparación y cancelación, guardados inválidos y persistencia de autos desocupados. También cubre la solución geométrica de las piernas y el apoyo de los pies.

**Navegador.** Se cargó el HTML construido mediante `set_content` en Chromium 144.0.7559.96, Linux, Xvfb y SwiftShader. Las suites por fotogramas detienen sólo el render entre capturas explícitamente dibujadas por WebGL. Usan el juego real, entradas reales de teclado y eventos táctiles del navegador. El almacenamiento de esas suites usa un objeto aislado en memoria porque la página inyectada no tiene un origen normal.

**Regresión.** Se recorrió la campaña hasta el desenlace público, la aceptación y cobro de una entrega, el guardado y continuación, la pausa, mapa y modo foto. Las comprobaciones policiales ejercitan salida tras contacto, captura, pérdida de visión, búsqueda, rendición y cancelación en tamaños de escritorio, 390 × 844 y 844 × 390. No equivalen a probar cada combinación posible de tráfico y misiones.

**Render continuo.** `continuous_reactive.py` no sustituye renderer, métodos de simulación ni almacenamiento. Prepara posiciones iniciales de revisión, después usa teclado real y el bucle normal para escapar de un contacto policial y chocar con un poste. Comprueba que los fotogramas avanzan, que se dibujan los buffers de malla importados, que se registra el daño y se apaga la lámpara, y que la caída se asienta. Termina con una captura de detalle alto de 1280 × 800. El escenario de persecución corre a 640 × 400 en calidad económica.

## Evidencia visual

Las imágenes son **capturas del renderer del juego**, no ilustraciones de IA. Algunas usan posiciones preparadas para inspeccionar una pieza concreta. El render de autoría de Higgsfield se identifica por separado en `assets/`.

| Captura | Uso |
| :--- | :--- |
| `03-carry.png` | Personaje sosteniendo una caja |
| `04-jump.png` | Postura de salto |
| `05-lamp-impact.png` | Estado tras un contacto real con un poste |
| `06-damaged-coupe.png` | Daño y humo del vehículo |
| `08-mobile-390.png`, `08-mobile-844.png` | Acceso a controles y reparación táctil |
| `09-live-coupe.png` | Vehículo y ciudad en modo foto, detalle alto |
| `10-tree-ground-review.png` | Revisión dirigida del árbol caído y su apoyo sobre el suelo |

La última revisión del árbol devolvió `angle: 1.1`, `angularVelocity: 0`, `broken: true` y `gl: 0`. Se inspeccionó su imagen. La caída se resuelve mediante una bisagra y un ángulo final conservador, no con contactos físicos de cada rama.

## Defectos encontrados y corregidos

La integración inicial dejó fuera del mapa de entrada la reparación, agacharse y el salto táctil. Se conectaron las acciones y se comprobaron pulsación, mantenimiento y cancelación. Se corrigió la distancia real usada en la marcha cuando el personaje queda bloqueado por una colisión.

La primera versión del humo tenía esferas opacas. Se reemplazó por superficies orientadas hacia la cámara, con transparencia, orden y prueba de profundidad. Los postes rotos dejan de aportar emisión y luz, incluso cuando se carga una partida cuyo tiempo es anterior al de la anterior simulación.

La caída podía enterrar la luminaria o parte de la copa. Se ajustaron las transformaciones y el ángulo de reposo. El taller restauraba la salud pero no todos los daños visuales al usarse a pie. Se unificó la reparación. También se añadió el guardado validado de autos alterados no ocupados.

## Ajustes del laboratorio, no del juego

SwiftShader tuvo bloqueos intermitentes al repetir capturas de calidad alta o cerrar varios contextos. Las ejecuciones incompletas se repitieron por separado. La regresión de campaña usa ahora render económico para revisar sus pantallas. Los pases equilibrado y alto se verifican en las suites nueva y continua. La policía se ejecuta en tres procesos separados.

Una aserción de dirección se leía después de soltar la tecla, cuando los fotogramas de la aplicación ya podían devolver las ruedas al centro. La prueba ahora captura el ángulo y el balanceo en el mismo paso de simulación con la tecla pulsada. No se eliminó la comprobación ni se cambió la amortiguación para hacerla pasar.

Después de **todas** las aserciones del bucle continuo, el script finaliza únicamente el PID de su propio navegador de pruebas para evitar el bloqueo de cierre de ese controlador gráfico de software. La simulación y el render no se reemplazan durante la prueba. Esto no valida el cierre normal de Chromium en ese laboratorio. Los reintentos y este ajuste impiden considerar los resultados una prueba de estabilidad o rendimiento prolongado.

## Límites de cobertura

No se probaron Safari, Firefox, un iPhone, Android físico ni GPUs de usuario. Los tamaños móviles son emulación de viewport y entrada táctil en Chromium. No se promete un objetivo de FPS a partir de SwiftShader. Tampoco se verificó persistencia nativa entre aperturas de archivos locales, pérdida y recuperación del contexto gráfico, migración inversa a versiones antiguas, sesiones prolongadas ni despliegue público.

La versión sigue usando física simplificada, deformación paramétrica, animación procedural y geometría estilizada. Los fragmentos visuales no son cuerpos rígidos persistentes. No hay malla humana continua con skinning, mocap, soft-body ni fotorrealismo AAA. Las fases correspondientes están **pendientes** en el plan.

## Reproducir

```bash
python tools/convert_vehicle.py
python build.py
node --test tests/*.test.cjs
python tests/reactive_browser.py
python tests/browser_qa.py
python tests/police_browser.py desktop
python tests/police_browser.py 390
python tests/police_browser.py 844
python tests/continuous_reactive.py
```

Las pruebas de navegador requieren Python, Playwright y Chromium como herramientas de desarrollo, no como dependencias del juego. En el contenedor se usó `/usr/bin/chromium`, `DISPLAY=:99` y un Xvfb de 1280 × 800. Cambia esa ruta al ejecutar en otro sistema. El HTML sigue siendo autónomo.

# Fijación del tirador en el panel de puerta · v0.20.26

En el sedán detallado, el tirador tenía el ángulo correcto pero su centro se desplazaba respecto al panel cuando se abría la puerta. Con la puerta izquierda abierta a 1,12 rad, la desviación entre su centro y el punto de montaje alcanzaba aproximadamente 0,51 m. Con la puerta cerrada y daño lateral 0,65, era de 78 mm.

La colocación del tirador parte del centro de la instancia de panel que dibuja el renderer. El punto de montaje queda a 23 mm hacia fuera, 150 mm hacia arriba y 480 mm hacia atrás en los ejes de esa instancia. La transformación sigue el orden del shader con cabeceo, balanceo y giro. La malla distante del sedán representa la puerta cerrada.

## Verificación

La regresión Node recupera los ejes locales del panel a partir de los parámetros de dibujo de producción. Comprueba ambas puertas durante apertura y cierre, daño lateral, el temporizador de apertura, giro del coche y suspensión inclinada. La base dio un control aprobado y dos fallos. La candidata aprueba los tres casos.

```sh
node --test tests/vehicle-door-handle.test.cjs
mkdir -p artifacts/door-review-input
git show ba9997df:index.html > artifacts/door-review-input/before.html
python3 tools/qa/capture_vehicle_door.py --before artifacts/door-review-input/before.html --after index.html --output artifacts/door-review-pairs
```

Se comparó el HTML de `ba9997df` con el de `fd6ed02b` con Chromium 156, WebGL2 y SwiftShader, en un estudio con coche estático, cámara fija y lienzo de 960 × 600. En la puerta completamente abierta, el centro proyectado del tirador pasó de (353,5; 324,2) a (341,3; 355,1) píxeles. En el fotograma corregido se ve el tirador sobre la superficie exterior, cerca del borde posterior del panel.

| Apertura de puerta izquierda | Píxeles RGB diferentes entre las dos versiones |
| --- | ---: |
| Cerrada | 0 |
| 25 % | 874 |
| 50 % | 1.536 |
| 100 % | 1.539 |
| 100 %, con daño 0,65 e inclinación | 1.411 |

Los dos PNG de la puerta cerrada tienen el mismo SHA-256. Ocultar el tirador corregido a apertura completa cambia 739 píxeles, incluidas sus contribuciones a iluminación y sombras. El [informe completo](report.json) contiene las posiciones 3D y 2D, las diferencias RGB de cada caso y las huellas de ambos HTML y sus diez PNG. El comando anterior vuelve a producir las imágenes en `artifacts/door-review-pairs/{before,after}/`.

El productor utiliza Playwright y Chromium con WebGL2. Para un Chromium instalado localmente definir `DC_QA_BROWSER`. Compara cinco instantes preparados, conserva los diez PNG y repite cada dibujo ocultando sólo el tirador izquierdo para medir su contribución en pantalla.

El anclaje de mano de la simulación durante la apertura se mide aparte. Con coche en origen, yaw cero y puerta izquierda a media apertura sin daño ni inclinación, la manilla corregida está en (−1,670; 0,960; −0,335) m y el objetivo de la mano está en (−0,990; 1,000; 0,540) m. Su separación es 1,109 m. La posición de la palma deformada y el contacto durante la trayectoria de acceso quedan pendientes de medir.

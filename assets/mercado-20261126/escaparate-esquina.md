# La Esquina · fachada del Mercado

El modelo reproduce el escaparate en esquina del Mercado de Distrito Cero v0.20.31. Incluye sus dos vitrinas, la puerta con tirador, cuatro baldas, tres bandejas, quince productos, la tira de luz de 5,40 m y el rótulo impreso. La cámara de Blender encuadra el frente y el lateral para mostrar cómo continúa la exposición en la esquina. [Descargar el modelo](./escaparate-esquina.glb) · [Ver el render de Blender](./escaparate-esquina.jpg)

| Propiedad | Valor |
| --- | --- |
| Semilla y celda del juego | 1337 · (1, 2) |
| Ancho × alto × fondo | 10,735 × 4,080 × 6,335 m |
| Origen en coordenadas del juego (X, Y, Z) | (150,750616; 0,260000; 185,214932) |
| Escena glTF | Metros, eje Y vertical, tres grupos editables y 47 objetos de malla |
| Geometría en escena | 532 triángulos, 15 materiales y un rótulo PNG de 512 × 256 píxeles integrado |
| SHA-256 del GLB | `a9c9e3d9aaec9bf76d95b2553938814a6370f4078272db400fe614adb0148c18` |
| SHA-256 del HTML de origen | `ed3324c77cf501ba91bad3079a0f787068dd2e6f655191cb0c2106a0fae5b268` |

La captura lee en WebGL2 los vértices, las instancias estáticas de la fachada y los objetos de detalle que el juego carga al acercarse. Recorta la baldosa «LA ESQUINA» del atlas usado en esa escena. El archivo conserva las escalas y orientaciones de producción. El cuerpo de la torre y su basamento quedan fuera del módulo de escaparate.

La luminaria usa un material emisivo cálido y el cristal usa transparencia. El juego calcula la atenuación de luz sobre baldas y productos en su shader de fachada. En Blender, el aspecto de esas superficies depende de las luces de la escena y del motor de render.

## Reproducción

Desde la raíz del proyecto, con Python, Pillow, Playwright, Chromium con WebGL2 y Node.js disponibles, se puede repetir la extracción sobre el HTML de la versión. `DC_QA_BROWSER` permite indicar dónde está instalado Chromium.

```sh
python3 tools/export_native_shop.py --html index.html --output /tmp/escaparate-esquina.glb
node --test tests/market-shop-export.test.cjs
```

Dos capturas de WebGL2 con Chromium produjeron el mismo GLB. Khronos glTF Validator 2.0.0-dev.3.10 registró cero errores y cero advertencias. Blender 4.3.2 abrió el archivo y confirmó las dimensiones y los 532 triángulos de la escena.

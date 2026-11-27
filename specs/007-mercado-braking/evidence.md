# Evidencia · v0.20.31

| Recurso | SHA-256 |
| --- | --- |
| HTML de referencia v0.20.30 | `c29717f5178dfff47f0a63b93b26c7d350b1d4e1eaab2e9a307aa70027b0df05` |
| HTML jugable v0.20.31 | `ed3324c77cf501ba91bad3079a0f787068dd2e6f655191cb0c2106a0fae5b268` |
| GLB de autoría con las seis acciones | `d4eb91068346abf0406584ed826756864fe2ac8f63dc1c05f30ef6658f7c9c0d` |
| Paquete del residente en `src/market-ped-data.js` | `645ecd39df721708bff7c0a4c1e0306778134b66f0f2d881fba7507826b34e2e` |
| GLB de la malla lejana del sedán | `e9090eac52108701fcfe5def07df25b22fd9d9d2a62ea6798a60873046a777d2` |
| GLB del escaparate de la esquina | `a9c9e3d9aaec9bf76d95b2553938814a6370f4078272db400fe614adb0148c18` |

Al reimportar el personaje en Blender 4.3.2, el talón y la puntera del pie de apoyo se desplazaron menos de 0,002 mm en 101 muestras por frenada. El pie que avanza alcanzó 81,35 mm. Las pruebas de superficies registraron cero cruces entre zapatos y en las dos rodillas. Se reprodujeron las cuatro acciones anteriores, los pesos y las texturas byte a byte. Khronos verificó el GLB de las seis acciones y el del sedán distante con cero errores y cero advertencias.

En la acera se registraron 1.736 muestras entre dos versiones, dos mallas y dos extremos de la ruta. Durante el primer medio segundo de espera, el desplazamiento máximo del talón o la puntera pasó de 55,585 mm a menos de 0,001 mm. Durante el último paso, el pie portante se movió 0,002 mm y el otro zapato se levantó entre 81 y 84 mm. Si se incluyen los 1,2 s anteriores a la llegada, la mayor excursión de un marcador a menos de 10 mm del suelo pasó de 37,185 a 37,470 mm. Esta medida incluye el despegue de los dedos al caminar. [Trayectorias, cámaras y vídeo](../../qa/market-brake-v02031/README.md).

Las pruebas de simulación se repitieron a 30, 60 y 120 Hz. Si el claxon se oye durante la frenada, el residente acelera la maniobra y sale hacia el tramo disponible. Si recupera la calma antes de llegar, puede preparar el apoyo dentro del recorrido restante. Cuando quedan sólo 12,25 cm, conserva la transición de carrera anterior. El clip de frenada desde marcha necesita 16,53 cm.

El HTML ocupa 11.606.306 bytes, un aumento de 58.289 frente a v0.20.30. La misma copia arrancó en Chromium desde un servidor local con las conexiones externas bloqueadas. Se creó una sesión de exploración libre desde el menú y se cargaron el residente y sus seis clips sin errores de JavaScript.

El contraste de la mercancía nocturna frente al fondo pasó de 17,70 a 23,98 en la vista frontal y de 18,34 a 22,91 en la diagonal, en una escala de luma de 0 a 255. Se preservaron las imágenes diurnas de ambas cámaras y los dos controles de noche fuera del comercio. [Vistas y controles de coste](../../qa/mercado-vitrinas-noche/README.md).

El módulo desmontable de «La Esquina» conserva los 46 elementos que componen las dos vitrinas, baldas, mercancía y rótulo en el juego. El GLB cuenta 532 triángulos con las instancias y usa materiales PBR para revisarlo en un editor. Las medidas de contraste proceden del HTML jugable. [Modelo de la fachada](../../assets/mercado-20261126/escaparate-esquina.glb).

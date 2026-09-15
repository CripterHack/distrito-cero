# Distrito Cero v0.15 · Integración cervical · Verificación

Continuación de v0.14 sobre su HTML y fuentes originales. El manifiesto `qa/v015/release-report.json` identifica la entrega y vincula informes y capturas a la misma huella del HTML. No se presenta como personaje hiperrealista o juego AAA terminado.

## Identidad de los archivos

HTML: **8,710,995 bytes**. SHA-256 `c421ef6da3790652e7ad2642e9a87e0b816b71cd3174982179f86421f87b7d11`.

GLB neutral: **4,216,984 bytes**. SHA-256 `9c0b59c33e4f05b6b01d9c22aa6ec6b30fbab2d168b3136aafa701f780f05585`.

## Resultado de las ejecuciones finales

| Grupo | Comprobaciones satisfactorias |
| :--- | ---: |
| Lógica Node, incluyendo cinco casos nuevos de integración cervical | 239 |
| Creador, formas/normales de GPU y estudios cervicales | 18 |
| Partidas/editor, fallos de escritura y pantallas táctiles emuladas | 64 |
| Campaña, controles, conducción y guardado heredados | 52 |
| Bucle original, extracción, conducción, salida y cruce de sectores | 16 |
| Geometría, deformación y exportación de la entrega | 43 |

Son **239 pruebas de lógica, 150 comprobaciones de navegador y 43 pruebas de geometría/exportación**, no sesiones independientes. No se suman pases de v0.14 o ensayos intermedios. Las suites finales de navegador no registraron excepciones JavaScript, errores WebGL detectados ni solicitudes HTTP/HTTPS. Los mapas embebidos no se cuentan como descargas externas.

## Problemas reproducidos y correcciones

**Masa.** La banda transversal media del cuello del modelo anterior medía aproximadamente 92.2 mm. En el nuevo recurso mide 128.4 mm. La razón entre ancho cervical y ancho de cabeza en las bandas definidas pasa de aproximadamente 0.51 a 0.70. Son medidas del avatar y decisiones artísticas, no promedios de una población ni valores clínicos. El volumen aumenta en ancho y profundidad, sin cambiar la estatura.

**Silueta.** Los perfiles anterior y posterior se diferencian. La nuca retrocede suavemente hacia el cráneo, en lugar de crecer como un cilindro uniforme. La primera revisión de volumen mostraba una protuberancia posterior y otra lateral bajo la oreja. Se añadieron pruebas de secciones reales de triángulos y se corrigieron ambas. Una primera prueba de nuca elegía una banda sin vértices; se reemplazó la selección por intersecciones de plano, de modo que midiera realmente el contorno. Los fallos reproducidos y sus correcciones se conservan en los registros.

**Pesos.** En la malla más ancha, una transición muy corta entre cuello y cabeza comprimía ciertas aristas bajo el mentón al combinar giro y flexión. La distribución de influencias ahora ocupa una región oblicua más amplia. Se mantiene el mentón anterior anclado a la cabeza y la raíz inferior al pecho. Los 49 huesos y sus dimensiones, las trayectorias y los límites del controlador se conservan; cambia cómo la superficie acompaña esas poses.

**Ropa.** Se adapta la abertura de la chaqueta y la transición hacia los hombros. Las piezas del cierre cercanas acompañan el cambio en lugar de quedar enterradas. No se sube una prenda para ocultar el problema. El cuello de piel conserva su extremo inferior en 1.447 m. Las manos, uñas, cabello, ojos, pantalones y calzado conservan su geometría de v0.14.

**Complexión.** El volumen cervical deja de estar desconectado del cuerpo. Se incorpora una contribución moderada de complexión y se conserva el control independiente de grosor, con amplitud más contenida alrededor de la base nueva. No se ensanchan el mentón anterior, las muñecas o las suelas. Se mantiene la versión del perfil y la clave de almacenamiento.

**Normales.** La prueba ampliada de GPU encontró que dividir la normal por una escala uniforme no representaba el cambio de forma de la chaqueta en regiones de transición. Se calcula el Jacobiano de la complexión y se encadena con el cervical. El transform feedback recupera el vertex shader real de producción, no un shader de prueba que dibuje otra malla.

## Cobertura geométrica y animada

Las pruebas actuales verifican topología, normales unitarias y continuas, pesos cuantizados que suman 255, rangos de huesos, ojos/labios/orejas conservados, cierre cervical sin bordes abiertos expuestos y preservación de superficies ajenas al alcance.

La malla real se deforma en **99 combinaciones** de once poses y nueve ajustes de complexión/grosor. Se comprueban posiciones finitas y conservación de diámetro en muestras cervicales. Otra prueba recorre esas complexiones en seis poses del cuello, acotando compresión/estiramiento de aristas, anclaje al pecho y distancia mentón/frente. Son pruebas de geometría acotadas, no una demostración de ausencia de todas las autointersecciones ni validación biomecánica.

El shader real se prueba en **72 combinaciones** de punto, material, complexión y grosor. La posición se compara con `Appearance.shapePoint` y la normal con una derivada numérica independiente. Los errores máximos observados se guardan en `gpu-transform-feedback.json`. Color, sombra y reflejo comparten el programa de vértices.

El máximo detalle mantiene **85,209 triángulos, 49 huesos y trece grupos de material**. Los LOD se comparten entre los actores. No se presenta la capacidad de paletas como una promesa de población o FPS en hardware.

## Creador, datos y juego

Se vuelven a ejecutar creación/edición/cancelación de identidad, espacios separados con nombres, renombrado, copias, exportación/importación, cuota, datos inválidos, conflicto de revisión y sesión voluntaria sin guardado. Doce sigue siendo el límite de diseño sujeto a cuota. No hay sincronización en nube.

La suite de campaña prepara posiciones junto a los objetivos y recorre las transiciones del desenlace público; no equivale a conducir espontáneamente todos los recorridos. La suite continua conserva RAF, cámara, renderer y simulación originales y usa teclado real del navegador para extraer al conductor, entrar, conducir, frenar, salir, caminar y atravesar un límite de sector. Sus posiciones iniciales se preparan para repetir la situación.

## Evidencia visual

La selección actual incluye frontal, perfil, tres cuartos, nuca, giro a izquierda/derecha, flexión/extensión, complexiones y grosores extremos, conductor, extracción, carrera y reparto. Se obtienen **15 capturas nuevas y dos anteriores**. Las anteriores proceden del HTML original v0.14. Las comparaciones usan las mismas cámaras, iluminación, pose, tamaño y resolución. Sólo se recortan y rotulan, no se retoca al personaje.

El vídeo contiene **160 fotogramas reales a 20 FPS de reproducción**, ocho segundos. El tiempo de animación se avanza explícitamente y la captura puede tardar más que un fotograma. No contiene generación de imágenes o interpolación de vídeo, y no mide rendimiento en tiempo real.

Una tanda de capturas intermedias fue detenida de forma deliberada al detectar la protuberancia lateral pendiente. Después del ajuste se volvieron a ejecutar las cuatro suites y la tanda final completa sobre la misma huella. Esos ensayos no se cuentan como evidencia final.

## Pruebas históricas y alcance

Los tests antiguos que exigían un cuello menor de 53 o 59 mm de semiancho preservaban la proporción delgada que el usuario pidió cambiar. Permanecen en sus archivos históricos, pero la selección nueva sustituye esos criterios por proporción y continuidad del contorno. También quedan fuera las antiguas exigencias de no cambiar cara/prenda/cierre respecto a versiones previas. Los otros invariantes aplicables se vuelven a ejecutar. `geometry-suite.json` enumera cada caso incluido y excluido.

El código de física, misiones, policía, ocupación, mapa procedural, guardados y controlador óseo no se reescribe. `behavior-scope.json` compara cada archivo de fuente con la base original. La igualdad de archivos no sustituye las pruebas de integración.

## Exportación, integridad y límites

Se reconstruyen geometría, HTML y GLB desde `hero-v014-baseline.js` con huellas idénticas antes y después. El exportador produce el modelo neutral, tres mapas embebidos y once estudios procedurales. La prueba estructural comprueba buffers, índices, pesos, normales, jerarquía, tiempos y cuaterniones. Se añade lectura independiente mediante trimesh. No se ha ejecutado el validador oficial Khronos ni una comparación visual en todos los editores.

El GLB usa materiales portables y puede usar skinning lineal en un visor externo. El juego utiliza DQ. Apariencia individual, mirada, parpadeo, material cervical, contactos y secuencias interactivas no están exportados como funciones completas del GLB.

Entorno: Chromium, Linux, Xvfb y ANGLE SwiftShader. HTML inyectado y fixture explícito de almacenamiento en memoria. Las suites de estado aparcan el renderer entre fotogramas WebGL; la continua no sustituye sus métodos. Los tamaños móviles se emulan. No se valida persistencia nativa tras cerrar/reabrir archivos `file://`, Safari, Firefox, GPU física, teléfonos reales, sesiones de horas ni pérdida/restauración del contexto gráfico. No se promete FPS.

El resultado conserva un acabado estilizado. La referencia hiperrealista sigue pendiente. No hay un escaneo nuevo, simulación muscular, autocolisión general de tejidos, nuevas manos/cabello, tela física o mocap. La corrección está centrada en proporción, continuidad y deformación cervical de la familia de personajes actual.

Comandos en README y GUIA. `audit_integration_release.py` comprueba reconstrucción, vuelve a ejecutar lógica/geometría y coteja informes de navegador y capturas previamente ejecutados; no vuelve a ejecutar el navegador por sí mismo.

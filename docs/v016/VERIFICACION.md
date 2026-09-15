# Distrito Cero v0.16 · Rasgos · Verificación

Continuación directa de los archivos entregados de v0.15. La actualización conserva el juego y modifica su representación de personajes, peinados y atributos de apariencia. No se anuncia fotorrealismo ni un juego AAA terminado.

## Identidad

HTML autónomo: **8,757,362 bytes**. SHA-256:

`7ccaff6042669755fdb18e920099519cda5af785113be9807bc952f3ee4f320c`

GLB neutral: **4,360,272 bytes**. SHA-256:

`2154216a0e1246c7d9e7ffe4a326e92b7240c84555102bb36714221dd73ed5d2`

El HTML original v0.15 de comparación tiene SHA-256 `c421ef6da3790652e7ad2642e9a87e0b816b71cd3174982179f86421f87b7d11`. No se reconstruyó una versión anterior artificialmente peor. `qa/v016/release-report.json` coteja las fuentes, la entrega y la evidencia.

## Ejecuciones completadas

| Grupo | Comprobaciones satisfactorias | Fallos finales |
| :--- | ---: | ---: |
| Lógica Node, incluidas doce pruebas nuevas de Rasgos | 251 | 0 |
| Creador, once estilos, atributos y GPU de producción | 39 | 0 |
| Catálogo/editor, importación, escritura e interfaces móviles | 64 | 0 |
| Campaña, controles, conducción y guardado heredados | 52 | 0 |
| Bucle original: extracción, conducción, salida y sectores | 16 | 0 |
| Geometría canónica, ajuste cervical animado y exportación | 47 | 0 |

Son **251 pruebas de lógica, 171 comprobaciones de navegador y 47 pruebas de geometría/exportación**. No son sesiones independientes ni cobertura exhaustiva del mundo abierto. No se suman los 239 pases de baseline, los ensayos fallidos o las capturas como si fueran pruebas adicionales.

Las cuatro suites finales de navegador terminaron sin excepciones JavaScript registradas, errores WebGL detectados ni solicitudes HTTP/HTTPS. Usaron la misma huella de HTML. `browser-execution.json` contiene el código de salida de cada suite.

## Cuello más corto y esqueleto coherente

El ajuste neutro acerca la cabeza al torso **45 mm** respecto de v0.15. Los extremos del nuevo control corresponden a 57 mm y 33 mm de reducción. Son decisiones métricas de autoría para este avatar, no valores anatómicos poblacionales.

La transformación trabaja entre las cotas canónicas 1.447 y 1.550 m. Por debajo conserva el anclaje torácico. Por encima traslada por igual rostro, cráneo, orejas, ojos y demás superficies de la cabeza. No comprime esos rasgos ni altera el ancho cervical. La relación previa entre grosor, complexión y abertura de la chaqueta permanece.

Los pivotes y las posiciones de referencia del esqueleto se transforman al mismo espacio. La geometría se ajusta antes del skinning DQ, y las matrices se calculan para ese bind adaptado. Se mantienen 49 huesos, sus nombres y las referencias no cervicales. La postura de cabeza cambia de posición visual, pero **la cápsula física, la fuerza, las velocidades y las reglas del juego no cambian**.

Para giros explícitos grandes, el controlador reparte parte del giro con columna y tórax. Evita concentrar toda la torsión en la sección ahora más corta. El giro restante se distribuye entre cuello y cabeza, manteniendo la orientación solicitada dentro de los límites anteriores. La compensación es menor sentado. No es captura de movimiento ni una simulación muscular.

### Defecto reproducido durante el ajuste

La primera interpolación concentraba demasiada compresión en el centro de la sección. Las pruebas de aristas deformadas fallaron: la razón máxima de longitud alcanzó aproximadamente 4.04. Se sustituyó el perfil por una función C1 con pendiente más distribuida y se añadió participación torácica para los giros deliberados. El límite de aceptación no se elevó para hacer pasar el test.

La prueba final de la malla real deforma **297 combinaciones** de pose, complexión, grosor y longitud. En la muestra de aristas, las razones extremas observadas fueron aproximadamente **0.506 y 1.989**. Comprueba también finitud, preservación del diámetro muestreado, traslado rígido de puntos faciales y anclaje inferior relativo al tórax. No demuestra ausencia de cada posible autointersección de triángulos ni exactitud biomecánica.

## Cabello modular y cejas

Se sustituyen los peinados limitados de la representación anterior por un catálogo de once opciones. Los índices 0–3 mantienen el significado de los perfiles antiguos. Siete índices nuevos añaden texturizado, degradado, media melena, flequillo, undercut, recogido y melena recta.

`hair-geometry.js` genera una base ajustada a la envolvente del cráneo y cintas curvas para los mechones. La parte superior, laterales, caída frontal y piezas posteriores se construyen según el estilo. El recogido se aprecia especialmente desde atrás. No es una misma malla reescalada para todas las opciones.

Cada estilo tiene tres LOD. Los buffers se reutilizan entre actores y la caché no puede superar las 33 combinaciones. El estilo sin cabello no genera piezas de pelo, pero conserva las cejas. El color de las cejas puede vincularse al tinte o permanecer castaño. El control de volumen modifica sólo el pelo y se desactiva en rapado/sin cabello.

La cobertura de raíz y bordes de mechones se utiliza tanto en color como en sombras. Las normales, la rugosidad y una variación direccional aproximada reducen la uniformidad de su superficie. No se implementó dispersión óptica completa de fibras, física de cabello o autocolisión con la ropa.

### Presupuesto observado

| Recurso dibujado | Triángulos |
| :--- | ---: |
| Cuerpo/cabeza/cejas, sin el peinado, LOD alto | 77,481 |
| El mismo conjunto, LOD medio | 15,838 |
| El mismo conjunto, LOD lejano | 5,957 |
| Personaje neutral con corto clásico, LOD alto | 89,433 |
| Máximo entre los once estilos, LOD alto | 93,393 |

El dato histórico `visualStats.heroTriangles = 85,209` describe el recurso canónico, no el total final con el nuevo peinado. `castStats.triangles` registra el total dibujado. La textura de apariencia pasa a dos texeles por actor. La capacidad de 128 filas no equivale a prometer 128 personajes simultáneos a 60 FPS. Estas cifras no son una medición de VRAM total.

## CPU, shader y normales

La prueba de transform feedback utiliza **el vertex shader efectivo de producción**, con el modo de crowd skinning, la textura de apariencia de dos texeles y una paleta DQ de identidad. Recorre **432 combinaciones** de punto, material, complexión, longitud y volumen.

Compara las posiciones con las funciones CPU y las normales con derivadas numéricas independientes. Los errores máximos registrados fueron aproximadamente **8.40e-8 m** en posición y **8.98e-6** en normal. Esto se cuenta dentro de las 39 comprobaciones del nuevo navegador, no como 432 sesiones adicionales. La deformación ósea real se cubre además por las pruebas de pose y las capturas del motor.

## Creador y partidas

Los campos nuevos `neckLength`, `hairVolume` y `browMatch` se validan antes de restaurar una partida. Los perfiles anteriores sin esos campos reciben valores neutros. Se conserva la versión del perfil, los IDs de las partidas y la clave del catálogo. Los nuevos campos se serializan con el personaje de cada espacio.

Las pruebas crean y cargan dos partidas con estilos distintos y descargan un respaldo JSON real del navegador. Verifican que aplicar desde comparación conserva el borrador, cancelar deja la apariencia anterior, la importación sigue siendo íntegra y un atributo inválido no modifica la sesión previa. La lógica también recorre once estilos por once espacios independientes y su restauración.

Se vuelven a ejecutar los casos de nombres iguales, renombrado, copia, borrado, búsqueda, orden, importación/exportación, cuota, corrupción, sesión volátil y conflictos de revisión. Doce sigue siendo el límite de diseño sujeto a cuota. No hay sincronización de nube ni nuevas miniaturas de partida.

Los controles nuevos se comprobaron accesibles en **390 × 844 y 844 × 390**, además de escritorio. Son viewports y eventos emulados, no teléfonos físicos. La cámara del creador acompaña el acortamiento sin cambiar la cámara o el tiempo de la partida real.

## Juego y evidencia visual

La campaña se verifica con posiciones preparadas junto a objetivos para comprobar sus transiciones. La suite continua conserva RAF, simulación, cámara y renderer, usando teclado real para extraer un conductor, completar el acceso, acelerar, frenar, salir, caminar y cruzar un límite de sector. No representa una partida espontánea de horas.

Las capturas finales revisan las once siluetas de peinado, cuello frontal/de perfil, giro, flexión/extensión, grosores mínimo/máximo, carrera, cuerpo, reparto, conductor civil y policía, extracción y creador. Las dos capturas anteriores usan el HTML original v0.15. Las comparaciones aplican el mismo encuadre, tamaño, luz y recorte por par, sin retocar los personajes.

El clip contiene **120 fotogramas reales**, reproducidos a 20 FPS durante seis segundos. El tiempo de animación se avanza explícitamente. No utiliza imágenes generadas, interpolación de vídeo o captura de movimiento y no mide rendimiento real. La galería conserva el mismo modelo, cámara y color para poder comparar las siluetas.

Una captura de galería inicial utilizó un nombre de propiedad incorrecto en el script de inspección. Se corrigió el script, no el juego, y la galería final se ejecutó completa. Un timeout del transporte al lanzar las capturas se resolvió comprobando el proceso ya existente, sin lanzar una segunda tanda. Los intentos intermedios no se cuentan como evidencia final.

## Integridad, exportación y límites

`audit_traits_release.py` reconstruye el HTML y el GLB con hashes idénticos, vuelve a ejecutar lógica/geometría y coteja los informes de navegador ya ejecutados. No ejecuta el navegador por sí mismo. `SOURCE-MANIFEST.json` y el empaquetador verifican cada archivo del ZIP.

El GLB contiene **14 mallas, 49 huesos, tres mapas embebidos y once estudios procedurales**, con el ajuste neutro y el peinado corto clásico. La lectura independiente con trimesh recuperó 89,433 triángulos y una caja finita en metros. No se ejecutó el validador oficial Khronos ni se validó la apariencia en todos los editores. Un visor de skinning lineal puede deformar distinto del DQ del juego. El material de pelo, la apariencia individual, las cejas, el parpadeo y las secuencias de vehículos son aproximaciones portables o funciones exclusivas del runtime, no una exportación de todo el editor.

Entorno: Chromium en Linux, Xvfb y ANGLE SwiftShader. HTML inyectado con almacenamiento de prueba en memoria. Las suites de estado aparcan el renderer entre fotogramas reales; la continua conserva sus métodos. No se valida persistencia nativa tras cerrar/reabrir `file://`, GPU física, Safari, Firefox, teléfonos físicos, sesiones de horas o pérdida/restauración del contexto gráfico. No se promete un FPS.

**El acabado sigue siendo estilizado y no iguala la referencia hiperrealista.** Se acorta e integra la región cervical, pero no se añade un cuerpo escaneado nuevo. El cabello tiene siluetas más diversas, aunque conserva una lectura de cintas y piezas modeladas. El pelo largo es rígido respecto de la cabeza y puede cruzar ropa/carrocería en poses extremas. Siguen pendientes materiales más ricos, expresiones completas, contacto individual de dedos, nuevas prendas, tela física y mayor diversidad anatómica.

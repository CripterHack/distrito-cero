# Distrito Cero v0.14 · Equilibrio cervical · Verificación

14 de septiembre de 2026. Continuación directa de **v0.13 Movimiento orgánico**. El HTML original de comparación tiene SHA-256 `2cfc9ae5cc85087d8d21ded739a10c955cce37b831f029467e314b25acdefbc3`.

## Archivos exactos

HTML autónomo: **8,709,664 bytes**, SHA-256 `82c535a0d25d3f5ba1753ae2248cb284745608bd53e2590b1e07237be8d40883`.

GLB neutral: **4,216,976 bytes**, SHA-256 `1a4a5ec1303befa0fa16ad5757c87d603cac37eb6c34b288fbd88970927f18fb`.

`qa/v014/release-report.json` relaciona las huellas con todos los informes de esta entrega. Catorce capturas actuales y cuatro suites de navegador apuntan al mismo HTML. Las dos capturas anteriores corresponden al HTML v0.13 original, no a una reconstrucción destinada a hacer parecer mayor el cambio.

## Ejecuciones completadas

| Grupo | Comprobaciones satisfactorias | Fallos finales |
| :--- | ---: | ---: |
| Lógica Node, núcleo, mundo, catálogo, DQ y nueva coordinación cervical | 234 | 0 |
| Creador cervical y morph/normal real de GPU | 18 | 0 |
| Catálogo/editor anteriores, fallos de escritura y pantallas móviles | 64 | 0 |
| Campaña, conducción, interfaz y guardado anteriores | 52 | 0 |
| Bucle original de simulación/render, acceso, conducción y sectores | 16 | 0 |
| Geometría corporal anterior | 7 | 0 |
| Cabeza, mapas y unión cervical anteriores | 6 | 0 |
| Continuidad, uñas, pesos y presupuesto anteriores | 7 | 0 |
| Tres invariantes de superficies de v0.13 aplicables a la entrega | 3 | 0 |
| Perfil cervical, mandíbula, pesos, normales y topología | 7 | 0 |
| Deformación sobre la malla cuantizada en seis poses | 4 | 0 |
| Estructura del GLB, rig, materiales y once estudios | 1 | 0 |

Total: **234 pruebas de lógica, 150 comprobaciones de navegador y 35 pruebas de geometría/exportación**. No son sesiones independientes ni cobertura exhaustiva del mundo abierto. No se suman resultados de versiones anteriores, ensayos incompletos o las comprobaciones del clip como pruebas adicionales.

Las cuatro suites finales de navegador cerraron sus procesos normalmente. No registraron excepciones JavaScript, errores WebGL detectados ni solicitudes HTTP/HTTPS. Las texturas embebidas `data:` no son descargas de red.

## Causas reproducidas y corrección

**Contorno.** El cuello se estrechaba y después se ensanchaba bruscamente debajo de la mandíbula, con semiancho de 60.1 mm en una banda lateral de esta malla. Se reconstruye esa sección sobre la topología existente con un perfil continuo de garganta, lados y nuca. La aceptación acota esa banda a menos de 53 mm para este avatar, no como norma anatómica poblacional. La guía incorpora relieves musculares discretos y una transición submentoniana. La base permanece debajo de la abertura de la prenda y las zonas de labios, ojos y orejas conservan sus posiciones.

**Mandíbula.** El peso de cabeza de un conjunto del mentón era de apenas 27.1 % porque se distribuía por altura. Ahora la región anterior de la mandíbula se protege por ubicación, no sólo por su altura, y sigue a la cabeza. El cuello recibe una transición gradual entre pecho, cuello y cabeza. La base inferior queda anclada al pecho al girar. No se añade simulación muscular.

**Personalización.** El grosor ya no infla el mentón. El centro de la abertura de la prenda responde al mismo parámetro, con caída gradual a cero fuera de esa zona. La normal se corrige mediante el Jacobiano completo del ajuste, en lugar de asumir un escalado uniforme. El esquema de apariencia y sus valores válidos no se modifican.

**Superficie.** El shader mezclaba material y normales con una rama abrupta a una altura determinada. Ahora interpola color, rugosidad y normales, utilizando pigmento filtrado del atlas existente para el cuello. No se incorporan mapas nuevos ni un escaneo cervical. Se suaviza moderadamente la caída del hombro vestido, sin modificar manos, uñas, cabello, prendas inferiores o calzado.

Los registros `cervical-red.txt` y `motion-red.txt` muestran dos fallos de geometría y cuatro de lógica antes de la implementación. Las suites correspondientes completas vuelven a pasar después. Las pruebas geométricas de la entrega verifican ausencia de bordes abiertos expuestos en el cuello, normales compartidas, pesos que suman 255, índices de huesos válidos y caras cervicales no degeneradas.

## Animación y comprobación de GPU

La coordinación reparte el giro entre cuello y cabeza y compensa de manera limitada la inclinación del torso. Las peticiones de giro/flexión son visuales y no modifican posición, colisionadores ni datos de partida. Los nuevos estudios del creador son **Cuello · giro suave** y **Cuello · flexión y extensión**. Cambiar a otra pose elimina las peticiones del estudio anterior. El borrador y la sesión real permanecen separados.

La geometría cuantizada real se deforma mediante DQ en seis estados: reposo, giro a ambos lados, flexión, extensión y giro combinado. Se comprueban límites acotados de estiramiento de aristas, continuidad del anclaje inferior y distancia mentón/frente. Esto no es una verificación de cada par de triángulos contra todas las autointersecciones posibles ni una validación biomecánica.

La prueba `cervical_gpu.js` recupera el vertex shader efectivo del renderer y ejecuta transform feedback sobre dieciséis combinaciones de punto/material/grosor. Compara posiciones con `Appearance.shapePoint` y normales con una derivada numérica independiente. El error máximo de posición fue 4.11e-8 m y el de normal menor de 7.66e-5 en las muestras. No es un shader simplificado dibujando otra malla. Los cambios de este programa se utilizan en color, sombra y reflejo.

## Regresiones y cobertura

Se vuelven a ejecutar creación, edición/cancelación de apariencia, partidas independientes, renombrado, duplicado, exportación/importación, cuotas, corrupción y conflictos de revisión. Los doce espacios siguen sujetos al almacenamiento disponible. El catálogo no cambia de esquema o clave.

La campaña utiliza posiciones preparadas para comprobar sus transiciones. La prueba continua mantiene RAF, simulación, cámara y renderer originales, usando teclado para extracción del conductor, entrada, conducción, freno, salida, caminar y cruzar un sector. Se capturaron conductor, extracción, carrera, manos y reparto después de los cambios.

El manifiesto `behavior-scope.json` identifica exactamente los 6 archivos de fuente modificados y los 24 conservados. Simulación, ocupación, policía, daño, mundo procedural, mapas de piel, controlador de marcha y almacenamiento conservan sus bytes de v0.13. La igualdad binaria no sustituye las pruebas de integración.

**Pruebas históricas.** Dos restricciones de `surface-polish.test.py` exigían conservar toda la cara y limitar prendas respecto de v0.12. Esa exigencia histórica entra en conflicto con la corrección cervical y deltoidea solicitada. No se borraron ni se declararon satisfactorias: se ejecutan sus otras tres invariantes aplicables y se añaden las siete comprobaciones cervicales y las cuatro de deformación. El detalle de selección está en el manifiesto. Los otros constructores/exportadores históricos tampoco representan la suite actual.

## Evidencia visual y recursos

Las comparaciones de tres cuartos y perfil usan la misma cámara, luz, entradas de pose, tamaño y calidad. Su composición sólo hace recortes y ampliaciones idénticas y añade rótulos. Catorce capturas actuales revisan cuello, nuca, giro a ambos lados, flexión/extensión, grosor mínimo/máximo, manos, carrera, reparto, conductor y extracción. La imagen sigue siendo la de un personaje estilizado, no un render hiperrealista.

El clip contiene **160 fotogramas del motor**, reproducidos a 20 FPS durante ocho segundos: giro y flexión/extensión. Se prepara la cámara y se avanza el tiempo explícitamente antes de capturar. No utiliza imágenes generadas, interpolación de vídeo ni captura de movimiento. No se mide el rendimiento de juego mediante su reproducción.

La malla de detalle alto conserva **85,209 triángulos**, 49 huesos y trece grupos de material. Los niveles de detalle observados son 85,209 / 17,519 / 6,209. La reconstrucción modifica 6,393 vértices de esquina de cara/cuello (contando duplicados), con desplazamiento máximo de 28.9 mm en la zona corregida, y 2,544 del hombro vestido con máximo de 7.2 mm. No se infla el presupuesto geométrico. La memoria compartida de paletas mantiene los presupuestos anteriores.

La cabeza y el atlas conservan su procedencia MakeHuman HM08/Aksel Skin y atribuciones anteriores. No se hizo una operación nueva en Higgsfield ni se añadió un recurso remoto al runtime. El GLB se leyó también mediante trimesh: trece mallas, 85,209 triángulos y caja envolvente métrica finita. Sus once estudios incluyen giro y flexión cervical. No se ejecutó el validador oficial Khronos ni una revisión visual de todos los importadores. El skinning lineal de un visor puede diferir del DQ del juego; material cervical procedural, personalización y secuencias interactivas no se exportan como efectos completos.

## Reconstrucción y límites

`audit_cervical_release.py` reconstruyó geometría, HTML y GLB con huellas idénticas antes/después. Después volvió a ejecutar todas las suites de lógica y geometría seleccionadas y cotejó las cuatro suites de navegador, capturas y vídeo con el HTML final. No vuelve a ejecutar el navegador: debe ejecutarse separadamente antes del cotejo. La reconstrucción se ha comprobado en este entorno, no en toda plataforma o versión futura de dependencias.

Entorno: Chromium, Linux, Xvfb y ANGLE SwiftShader. HTML inyectado y fixture explícito de localStorage en memoria. Las pruebas por estados aparcan el renderer entre fotogramas reales para separar la lógica del coste gráfico; la suite continua no lo reemplaza. Los tamaños móviles son emulación. No se valida persistencia nativa después de cerrar/reabrir `file://`, GPU física, Safari, Firefox, teléfonos reales, sesiones de horas o pérdida/restauración de contexto WebGL. No se promete FPS.

**La corrección elimina el defecto concreto de contorno y deformación observado, no convierte el conjunto en un personaje AAA.** Continúan los límites de rostro, cabello, materiales y variedad corporal. No hay rig facial completo, pelo/tela físicos, contacto individual de dedos ni autocolisión general de tejidos. La dirección anatómica es artística, no una simulación clínica.

Referencias de orientación consultadas: OpenStax Anatomy and Physiology 2e, sección 11.3, y especificación oficial Khronos glTF 2.0. No se han usado imágenes ajenas como capturas del juego.

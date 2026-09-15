# Distrito Cero v0.11 · Identidad · Verificación

14 de septiembre de 2026. Base: Constitución v0.10. HTML autónomo de **8,115,422 bytes**, SHA-256 `3ea547854a050db63da4159cffb4f5d087b0898c278e1e7d1e46d59b15f3f44c`.

## Resultado ejecutado

| Grupo | Comprobaciones satisfactorias | Fallos finales |
| :--- | ---: | ---: |
| Lógica Node, incluyendo núcleo, policía, rig, territorio, identidad y catálogo | 197 | 0 |
| Editor, partidas, exportación/importación, fallos y controles táctiles | 64 | 0 |
| Campaña y controles anteriores ejecutados sobre el nuevo HTML | 52 | 0 |
| Bucle continuo original, extracción, conducción y cruce de sectores | 16 | 0 |
| Geometría corporal de la entrega | 7 | 0 |
| Regresión de cabeza, mapas, cuello y cuero cabelludo | 6 | 0 |

Son **132 comprobaciones de navegador**, además de 197 de lógica y 13 de geometría. No son sesiones independientes ni cobertura de todas las combinaciones del mundo abierto. No se suman pases históricos. Los informes funcional y continuo y las capturas de estilo registran la huella exacta de este HTML.

Los tres grupos finales de navegador no registraron excepciones JavaScript, errores de shader/WebGL detectados ni solicitudes HTTP/HTTPS externas. Las texturas `data:` se incluyen en el archivo. El motor conserva 49 huesos y 79,278 triángulos en el humano de máximo detalle, con tres LOD compartidos.

## Personalización y anatomía

Se prueban cuatro estilos distintos, límites y validación estricta de índices, forma, nombres y versiones. Complexión y contorno facial producen posiciones distintas con límites finitos. La altura, muñecas, dedos y suelas no se desplazan en el morph de volumen. El esqueleto y los objetivos IK mantienen sus dimensiones originales.

El refinamiento geométrico es moderado: perfil de hombros menos abultado, facilidad abdominal, profundidad torácica y collar de chaqueta más bajo. Conserva la topología de cuerpo/manos y la cara texturizada anteriores. Los peinados son variantes del groom existente, no nuevas simulaciones de pelo. La rugosidad de piel de manos y uñas se diferencia, pero no se añadieron mapas fotográficos específicos para las manos. Los personajes siguen estilizados.

El editor crea otra simulación para posar. La partida real conserva apariencia, dinero, historia y mundo mientras se edita. Cancelar restaura el renderer y la cámara anteriores. Aplicar guarda la identidad únicamente en el espacio activo. Un fallo de escritura durante la edición revierte la apariencia de la sesión.

Se revisaron capturas reales del editor completo, rostro, cuatro estilos, partidas y pantallas de 390 × 844 y 844 × 390. La selección llega a la textura de apariencia de la GPU. No se sustituyen los modelos por renders de Blender, imágenes generadas o un visor ajeno al motor. La lámina de variantes sólo recorta y rotula las cuatro capturas con el mismo encuadre.

## Catálogo y datos

La suite crea dos historias con distintos nombres, apariencia, dinero y estado de misión. Cambia entre ambas, renombra, duplica, guarda una bifurcación y confirma/cancela borrados. Eliminar el espacio activo deja la sesión sin autoguardado y no vuelve a crearlo.

Se comprueban descargas JSON reales del navegador (individual y grupo), importación de JSON antiguo sin identidad, nombres iguales con distintos IDs y anexado sin reemplazo. Los tests de lógica verifican el ciclo completo del respaldo de grupo, validación íntegra antes de escribir y el límite de doce espacios. La importación incorrecta deja las mismas cadenas de almacenamiento.

Se inyectan fallos de cuota y permisos de escritura. Se confirma que los bytes anteriores permanecen intactos y se muestra un error, no una confirmación de éxito. El usuario puede elegir explícitamente jugar sin guardado local. Los tests de lógica también cubren denegación de lectura, catálogo ilegible y migración no destructiva/idempotente de la clave anterior. El marcador de migración impide resucitar una partida borrada.

Un conflicto se detecta comparando la revisión de la sesión con la revisión guardada. **No se afirma bloqueo distribuido o resolución automática de escrituras simultáneas entre procesos.** Se ofrece guardar otra copia o recargar la nueva revisión con confirmación. El defecto encontrado era que «Reanudar» retornaba el estado vivo obsoleto incluso tras detectar conflicto. La prueba falló en `conflict-red.json` y ahora pasa tras distinguir reanudar de recargar.

Los nombres se insertan en controles y nodos de texto, no como HTML. Se verifica un nombre con sintaxis de etiqueta sin crear contenido ejecutable.

## Cobertura anterior conservada

La batería de campaña vuelve a recorrer el desenlace público con posiciones preparadas junto a objetivos. Comprueba movimiento, entrada y salida, conducción, pausa, mapa, exportación/continuación, encargo y controles táctiles. No equivale a completar cada recorrido espontáneamente.

La suite continua mantiene RAF, simulación, renderer y cámara sin reemplazarlos. Usa teclas reales para extraer al conductor, terminar el acceso, conducir, frenar, salir, caminar y cruzar un límite de sector. Las posiciones iniciales se preparan para reproducir la situación. Comprueba límites del streaming, población y acceso al atlas.

Se verificó binariamente que núcleo, mundo, policía, simulación base, daño, interacciones, ocupación, animación, rig de 49 huesos, audio, app base, atlas y mapas de piel coinciden con v0.10. Las extensiones se cargan después. La lista está en `qa/v011/behavior-unchanged.json`.

## Entorno e incidencias

Chromium, Linux, Xvfb, ANGLE SwiftShader. Las pruebas por estados aparcan únicamente el renderer entre fotogramas WebGL reales para no hacer depender cada click de la GPU por software. La suite continua usa el bucle original a 680 × 440 en calidad económica. Las capturas editoriales usan 1280 × 840 y calidad alta en la vista de estudio.

Se intentó usar un origen HTTPS interceptado localmente con Playwright, pero la política devolvió `ERR_BLOCKED_BY_ADMINISTRATOR`. Las ejecuciones usan `set_content` y un **fixture explícito de localStorage en memoria**. La rehidratación carga los bytes de ese fixture en otra página. **No se verificó persistencia nativa entre aperturas de archivos `file://` ni almacenamiento real tras cerrar el navegador.** El juego de distribución sí llama al localStorage del navegador, no al fixture.

Los primeros ensayos del editor excedieron el tiempo por render continuo de software. Se separaron los tests funcionales y el bucle continuo. Una prueba buscaba una clase CSS de renombrado inexistente y otra devolvía desde `page.evaluate` la función de fallo de cuota, que Playwright ejecutaba como resultado. Se corrigieron los scripts de prueba, no las reglas del juego. Los intentos incompletos no cuentan como pases.

No se probaron Safari, Firefox, dispositivos táctiles físicos, GPU del usuario, almacenamiento de nube, sesiones prolongadas o pérdida/restauración de contexto WebGL. No se promete un objetivo de FPS. localStorage puede ser bloqueado por configuración o agotar su cuota. Doce es el límite de diseño, no una garantía de capacidad para doce instantáneas del tamaño máximo.

Referencias consultadas: MDN Window.localStorage y WHATWG HTML, sección Web Storage. La conducta de file:// varía por navegador y la escritura puede fallar por cuota o permisos.

## Reproducción e integridad

`python tools/audit_identity_release.py` regeneró el refinamiento y el HTML, comprobó que las huellas se mantuvieron idénticas, volvió a ejecutar Node y geometría y cotejó los informes de navegador con el HTML. Su manifiesto está en `qa/v011/release-report.json` y la prueba de reconstrucción en `qa/v011/rebuild.json`.

Comandos y alcance en `README.md`. El ZIP contiene código, recursos, licencias y pruebas. Los GLB antiguos se conservan identificados por su versión y no se presentan como exportaciones de cada perfil personalizable nuevo. No se distribuyen archivos de fuentes tipográficas ni se hacen compras, suscripciones o despliegues.

# Distrito Cero v0.19 · Contacto articulado · Verificación

Continuación del HTML y las fuentes originales de v0.18. El manifiesto `qa/v019/release-report.json` identifica los bytes finales y vincula las suites y capturas al mismo HTML. No se presenta como personaje hiperrealista, réplica mecánica de armamento o acabado AAA.

## Resultados de la entrega

| Grupo | Comprobaciones satisfactorias |
| :--- | ---: |
| Lógica Node: núcleo, rig, palmas, animación, inventario, catálogo y mundo | 328 |
| Manejo, superficies palmares, recarga, selector y controles | 51 |
| Arsenal: Gauss, EMP, óptica, impactos e inventarios | 78 |
| Creador y partidas: persistencia, importación, errores y táctil | 64 |
| Campaña y controles heredados | 52 |
| Bucle original: equipamiento, ocupación, conducción y sectores | 26 |
| Kit GLB actual: estructura, geometría y piezas | 1 |

Total: **328 pruebas de lógica, 271 comprobaciones de navegador y una prueba de exportación**. No son 271 sesiones independientes. Las dos pruebas de superficie palmar pertenecen a Node y no se suman otra vez como una batería independiente. No se incluyen los pases del baseline, los intentos parciales ni los fotogramas del clip como resultados adicionales.

Las cinco suites finales de navegador deben finalizar con código cero, sin excepciones JavaScript, errores WebGL detectados ni solicitudes HTTP/HTTPS, y corresponder a los mismos bytes. El auditor no acepta sus recuentos si cambió el HTML. Las imágenes `data:` embebidas no son recursos descargados de la red.

## Sujeción y anatomía

El punto de contacto de la palma ya no se confunde con el centro de giro de la muñeca. Se define una referencia palmar en el espacio de reposo, se orienta hacia la superficie del equipo y se deriva el objetivo de muñeca mediante esa transformación. Las manos de soporte y dominante tienen orientaciones y flexiones independientes.

La referencia se compara con la piel de la malla existente, no sólo con un pivote inventado. La prueba `palm-surface.test.cjs` toma una intersección sobre triángulos reales de ambas palmas, aplica las influencias DQ y verifica su proximidad a los contactos en una muestra de armas/poses. El límite de 13 mm es una tolerancia de autoría para estas muestras. No equivale a validar toda la superficie de la mano ni cada contacto de dedo.

El montaje consume el mismo actor de movimiento que el renderer, con apoyos/crouch y ajuste cervical. La prueba de locomoción recorre 140 muestras. Las pruebas de todas las familias recorren postura de pie/agachado, elevaciones y fases de recarga, verificando finitud, marcos ortonormales, alcance de muñecas inferior a 12 mm de error y conservación de longitudes óseas.

El apoyo de las armas largas utiliza el hombro articulado y una participación del tórax. En apuntado neutral se comprueba una separación inferior a 35 mm entre la referencia de culata y su apoyo. Ante ángulos extremos se prioriza un montaje alcanzable por ambos brazos, no se alargan los segmentos para mantener una culata fija. No se garantiza contacto exacto al hombro en todos los ángulos.

La revisión añadió una regresión de equivariancia al girar el personaje: una componente local del desplazamiento de hombro no rotaba íntegramente con el cuerpo. Se reprodujo el fallo y se corrigió en ambos ejes horizontales. La prueba también compara palmas y boca visible al rotar el conjunto.

## Dedos, recarga y movimiento secundario

El índice tiene una mezcla temporal propia. Apuntar sin disparar no equivale a cerrar el dedo al máximo. Medio, anular, meñique y pulgar mantienen perfiles diferentes. Los valores son poses procedurales, no una detección física del gatillo o de las falanges.

La recarga distingue aproximación, extracción, inserción, asentamiento y retorno. En el trayecto libre la mano de apoyo se abre. Durante la manipulación se cierra sobre la misma superficie del cargador/celda que desplaza el renderer. La pieza tiene traslación y giro acotados. Las pruebas comparan el punto de contacto y la composición matricial visible, y recorren 301 muestras por secuencia para detectar discontinuidades de posición.

Los seis cargadores/celdas separados se conservan. No se añade una segunda pieza estática detrás de la móvil. Revólver, escopeta y lanzador mantienen gestos simplificados. No se anuncian recámaras, cartuchos individuales o mecanismos internos completos. Los tiempos y la transferencia de munición no cambian.

Se añade inercia angular pequeña y recuperación de retroceso por familia. Los estados visuales quedan fuera de la serialización. El montaje no escribe munición, dinero, salud o posición del jugador.

## Selector y transiciones

El selector conserva fondo exterior alfa 0.18 y panel alfa 0.38, con el texto a opacidad 1. La escena real permanece debajo y el mundo queda pausado. El foco está contenido, Escape cancela y confirmar no dispara a través del diálogo.

Al cerrar sin cambiar de arma se retiene únicamente la mezcla visual de apuntado para poder bajar el equipo progresivamente. No se restauran trigger, aiming, carga Gauss ni entradas de puntero. Los retornos a Pausa y las selecciones de un arma distinta no heredan ese apuntado.

Equipar o restaurar una partida inicia la presentación baja antes del primer render, evitando mostrar una pose elevada un fotograma antes de iniciar su transición. El inventario serializado permanece idéntico tras restaurar. La recarga pausada en el selector sigue transfiriendo munición una única vez al terminar.

## Geometría y recursos

Nueve empuñaduras principales reciben sección redondeada en lugar de una caja simple. El kit contiene **13 equipos, 78 mallas y 9,888 triángulos**, con nueve grupos `grip` y seis `magazine`. Las pruebas revisan vértices finitos, normales unitarias, caras válidas y presupuesto por equipo. El GLB es una galería estática con materiales portables, no exporta la interacción del personaje ni la recarga. La lectura independiente con trimesh recuperó las mismas 78 mallas y 9,888 caras triangulares. No se ejecutó el validador oficial Khronos ni se verificó cada visor.

No se incorporan recursos remotos, escaneos nuevos o dependencias externas. Cuerpo, cabeza, piel, cabello, perfiles y catálogo de partidas conservan sus fuentes. `behavior-scope.json` enumera modificaciones y conservación respecto del commit base. Esa igualdad no sustituye la integración.

## Integración y evidencia

Se vuelven a probar el arsenal completo, entradas, creador, espacios independientes, nombres iguales, copias, importación/exportación, rechazo de escrituras, sesiones sin guardado y conflictos. La campaña prepara posiciones junto a los objetivos para comprobar las transiciones, no completa cada trayecto espontáneamente.

La suite continua mantiene RAF, cámara, renderer y simulación. Usa teclado real para Gauss, EMP, binoculares y selector, seguido de extracción de conductor, acceso, aceleración, frenado, salida, caminata y cruce regional. Sus posiciones iniciales se preparan para reproducibilidad.

Las capturas actuales revisan fusil, pistola, Gauss, recarga, binoculares y selector. Las comparaciones usan el HTML v0.18 original, idéntica cámara, luz, tiempo e inputs de apuntado. La pose resultante cambia por el nuevo controlador. Sólo se recortan por igual y se rotulan las imágenes, sin retocar personajes o armas.

El clip tiene **120 fotogramas reales**, a 20 FPS de reproducción durante seis segundos. El tiempo de simulación avanza de forma controlada antes de capturar. No mide FPS reales, no usa captura de movimiento, generación de imágenes ni interpolación de vídeo.

## Incidencias y alcance del laboratorio

Ensayos tempranos que acumulaban fotogramas de estado a 1120 × 740 perdieron el contexto gráfico. El diagnóstico confirmó `isContextLost() === true` y el código WebGL `CONTEXT_LOST_WEBGL`; la llamada posterior de uniformes recibió un programa nulo. No hubo un evento OOM en el contenedor. No se afirma haber determinado por completo la causa interna del driver ni haber añadido recuperación de contexto al producto.

Las verificaciones funcionales finales se ejecutan a **900 × 640**, con fotogramas de estrés espaciados y `gl.finish()` de prueba. Las capturas de inspección se aíslan en contextos nuevos a 1120 × 740. No se reduce la geometría ni se sustituye el renderer para aprobar esos contactos. La suite continua separada conserva el bucle original a 680 × 440. Los intentos interrumpidos no cuentan como pases.

Las demás suites por estados aparcan RAF o renderer entre keyframes reales, para separar el coste de SwiftShader de las comprobaciones funcionales. Las pantallas táctiles de 390 × 844 y 844 × 390 son emulación.

Entorno: Chromium, Linux, Xvfb y ANGLE SwiftShader. HTML inyectado y fixture explícito de localStorage en memoria. El juego distribuido utiliza el almacenamiento del navegador. No se valida persistencia nativa al cerrar/reabrir archivos locales, GPU física, Safari, Firefox, teléfonos reales, sesiones de horas o pérdida/restauración de contexto. No se anuncia un FPS.

## Límites e integridad

El resultado sigue siendo estilizado. Las pruebas acreditan coordinación y continuidad en muestras, no calidad artística AAA ni ausencia de cada intersección. No hay autocolisión completa, contacto físico por falange, alineación óptica exacta ojo/mira, tela física o mecánica completa de cada arma. Tampoco se añade combate armado autónomo de NPCs. El controller es reutilizable, pero la lógica de uso del arsenal continúa siendo la del jugador.

`audit_contact_release.py` reconstruye HTML y kit GLB con huellas idénticas, vuelve a ejecutar Node y exportación y coteja las cinco suites y las capturas previamente realizadas. No ejecuta el navegador por sí mismo. `package_contact.py` coteja los archivos del ZIP con su manifiesto y excluye fuentes tipográficas, cachés y secuencias de fotogramas sin comprimir. Los comandos están en README.

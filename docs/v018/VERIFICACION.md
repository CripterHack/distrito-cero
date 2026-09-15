# Distrito Cero v0.18 · Manejo y contacto · Verificación

Continuación directa de los archivos entregados de Arsenal v0.17. Se mantienen los personajes de Rasgos, el mundo, la campaña, el inventario y las partidas. No se presenta como acabado hiperrealista.

## Identidad y reproducción

El HTML final ocupa **8,831,750 bytes**. `qa/v018/release-report.json` registra su SHA-256, el kit GLB y las huellas de fuentes/evidencias. El empaquetador coteja cada archivo del ZIP con `SOURCE-MANIFEST.json`.

El auditor reconstruye el HTML y el kit GLB y exige las mismas huellas antes/después. Vuelve a ejecutar Node y la prueba GLB. Coteja los informes de navegador y capturas ejecutados previamente; **no ejecuta el navegador por sí mismo**.

## Resultados de la entrega

| Grupo | Comprobaciones satisfactorias |
| :--- | ---: |
| Lógica Node, núcleo, mundo, inventario, rig, creador, catálogo y manejo | 303 |
| Contactos, recarga, superposición, transparencia, foco e inputs | 40 |
| Regresión del arsenal, Gauss, EMP, óptica e inventarios | 78 |
| Creador, biblioteca de partidas, fallos e interfaces táctiles | 64 |
| Campaña, conducción e interfaz anteriores | 52 |
| Bucle normal con teclado, equipo, ocupantes y cruce regional | 26 |
| Estructura y piezas del kit GLB actual | 1 |

Total: **303 pruebas de lógica, 260 comprobaciones de navegador y una prueba de exportación**. Son aserciones, no 260 sesiones independientes. No se suman los pases del baseline ni de ejecuciones intermedias. Los cinco informes finales de navegador deben corresponder al mismo HTML y no registrar excepciones JavaScript, errores WebGL detectados ni solicitudes externas.

## Problema de sujeción y correcciones

Antes se resolvía la posición de muñeca, pero no su orientación hacia la empuñadura. La mano copiaba la transformación del antebrazo. La mano de apoyo también se desplazaba durante recarga sin un objeto móvil correspondiente.

Ahora un único montaje produce la transformación visible del arma, los contactos orientados de ambas manos, la posición del cargador/celda y la boca de salida. Cada familia define referencias propias. El ajuste usa un polo de codo y una orientación terminal de palma/dedos, con torsión parcial limitada del antebrazo. Los dedos se actualizan desde la muñeca final.

Las pruebas recorren las trece opciones utilizables, apuntado/guardia baja, agachado, elevaciones y fases de recarga. Verifican objetivos alcanzables con error menor a 12 mm, matrices finitas, bases ortogonales, longitudes óseas conservadas y dedos próximos a la muñeca. No prueban colisión entre cada triángulo de la mano y el objeto.

El retroceso usa un muelle analítico amortiguado que no escribe en los datos serializables. Se prueba estabilidad frente a distintas particiones temporales, independencia entre actores y lectura sin efectos secundarios del montaje. Arma y manos comparten la misma recuperación. La animación de alzar el equipo también queda dentro del alcance en los estados muestreados.

## Recargas y piezas

La recarga tiene aproximación, manipulación y retorno al apoyo. La mano sigue el mismo desplazamiento local que la pieza separada. Pistola, subfusil, fusil, rifle de precisión, Gauss y EMP tienen un grupo de cargador/celda independiente, sin segunda copia estática superpuesta.

Las pruebas verifican continuidad de posición entre muestras, desplazamiento real del cargador y regreso al montaje neutro. La recarga mantiene los tiempos y la transferencia de munición del juego anterior. Se prueba pausa del selector a mitad del gesto, reanudación y transferencia única al finalizar. Revólver, escopeta y lanzador usan gestos hacia zonas de carga, no animación mecánica completa.

## Selector translúcido

Se comprueba el fondo exterior con alfa 0.18 y el panel principal con alfa 0.38. Tarjetas y detalle usan fondos translúcidos. La opacidad de los elementos con texto permanece en 1, de modo que los textos no se desvanecen con el fondo.

Se dibuja la escena real bajo el diálogo y se mantienen la cámara, FOV y pose de arma registrados antes de cancelar las entradas. No se sustituye la escena por una imagen. El mundo permanece pausado. La transparencia se inspeccionó visualmente en las capturas de escritorio y móvil, además de comprobar el CSS efectivo.

Tab/Shift+Tab quedan dentro del selector. Esc o × cierran sin confirmar. Elegir tarjeta no equipa hasta confirmar. J/F/M y el clic de confirmar no disparan ni acceden al vehículo detrás del menú. Cancelar una carga Gauss mantenida no la descarga. Se verifica el retorno del foco al canvas y la accesibilidad de los botones en 390 × 844 y 844 × 390.

## Defectos encontrados durante la iteración

Las pruebas iniciales fallaron al no existir contactos orientados, pieza de recarga o recuperación amortiguada. El registro `handling-red.txt` conserva esa ejecución.

Se corrigieron contactos que excedían el alcance durante elevaciones o recarga de equipo pesado. La primera pose de alzar el equipo retiraba demasiado el origen del alcance del brazo, y la amplitud se redujo. La interpolación de orientación del apoyo durante recarga necesitaba ortogonalización para no producir marcos sesgados.

La revisión de imagen mostró que el primer agarre de binoculares colocaba las muñecas por encima de los oculares y los dedos colgaban sobre los tubos. La prueba `optics-contact-red.txt` reproduce esa condición. Los contactos finales quedan más abajo, con los dedos orientados a lo largo de los tubos. Después de esa corrección se repitieron las suites finales y capturas.

Un primer lanzador heredó `DISPLAY=:0`, mientras el Xvfb del laboratorio estaba en `:99`. Chromium no pudo abrirse antes de ejecutar comprobaciones. Se corrigió la configuración del lanzador, no el juego. Esa ejecución de cero comprobaciones no se cuenta. Una llamada corta al contenedor se interrumpió después de completar Node y antes de completar una captura; se comprobó que no quedaba un proceso de captura antes de repetirla.

## Regresiones y alcance

Las pruebas de arsenal, creador/catálogo y campaña conservan las aserciones anteriores y cargan el nuevo HTML. La de campaña prepara al jugador cerca de objetivos para comprobar sus transiciones, no una partida espontánea íntegra.

El bucle continuo mantiene RAF, métodos de simulación, cámara y renderer. Usa teclado real para Gauss, EMP, binoculares, selector, extracción del conductor, conducción, salida, marcha y cruce de un sector. Las posiciones iniciales están preparadas para reproducibilidad.

`behavior-scope.json` enumera las fuentes modificadas y conservadas. Las mallas humanas, peinados, perfiles, textura de piel, catálogo de partidas, mundo procedural y controlador de ocupación no se reemplazan. El cambio de IK es opcional: los contactos heredados sin orientación conservan su trayectoria anterior. No se añade inteligencia de combate armado a los NPCs.

## Evidencia y recursos

Las imágenes son del renderer WebGL. Las cámaras de inspección y posiciones se preparan. La comparación utiliza el HTML v0.17 original y el final con la misma cámara, iluminación, pose y recorte. Sólo se añaden rótulos, sin retocar modelos.

El vídeo usa fotogramas WebGL con tiempo de simulación controlado. Se rotula como tal y no es medición de rendimiento en tiempo real, captura de movimiento ni vídeo generado. Su informe registra cada fase, disparo, desplazamiento de cargador y error GL.

El kit GLB tiene **trece equipos, 71 mallas y 8,196 triángulos**. Seis piezas se identifican como `magazine` en sus extras. Es geometría estática portable, no una exportación de los personajes o de las recargas. La prueba revisa buffers, índices implícitos, normales, finitud y estructura; no se ejecutó el validador oficial Khronos ni cada importador externo.

## Límites

Chromium, Linux, Xvfb, ANGLE SwiftShader. Las suites por estados aparcan RAF o renderer entre fotogramas reales; la continua no los sustituye. Se utiliza un fixture explícito de localStorage en memoria. El juego distribuido utiliza el almacenamiento nativo.

No se probaron Safari, Firefox, teléfonos físicos, GPU del usuario, pérdida/restauración de contexto, sesiones de horas ni persistencia nativa tras cerrar/reabrir archivos locales. No se promete FPS.

Los agarres y la recarga siguen siendo procedurales. No hay contacto físico individual por falange, alineación óptica exacta ojo/mira, autocolisión completa, tejidos físicos ni representación mecánica completa de cada arma. Algunas mangas y culatas pueden mostrar intersecciones en ángulos extremos. El cambio mejora la coordinación del equipamiento; no sustituye el modelo humano por uno AAA.

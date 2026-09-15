# Distrito Cero v0.17 · Arsenal · Verificación

Continuación directa de **Rasgos v0.16**. Selector y equipamiento integrados en el juego, no una demostración separada. No se afirma hiperrealismo, acabado AAA ni equivalencia física con armas reales.

## Identidad de la entrega

HTML autónomo: **8,820,950 bytes**. SHA-256:

`fc2679da41268f6be0264c96f54a83ed77886157d67a27e87dbd125aa06d6f93`

Kit de equipamiento GLB: **829,940 bytes**. SHA-256:

`733eab087d1c1df4fc6a88f201040d6fe2080f33d89c894aed841798de9fddd7`

Base HTML v0.16: `7ccaff6042669755fdb18e920099519cda5af785113be9807bc952f3ee4f320c`.

`qa/v017/release-report.json` relaciona estas huellas con fuentes, suites y capturas. Los cuatro procesos finales de navegador finalizaron con código 0 y sus informes registran el mismo HTML.

## Ejecuciones finales

| Grupo | Comprobaciones satisfactorias | Fallos |
| :--- | ---: | ---: |
| Lógica Node, incluidas 37 pruebas nuevas de equipamiento | 288 | 0 |
| Selector, disparos, Gauss, EMP, óptica, poses, dos partidas y táctil | 78 | 0 |
| Creador/catálogo, importación, errores y controles anteriores | 64 | 0 |
| Campaña, conducción e interfaz anteriores sobre el nuevo HTML | 52 | 0 |
| Bucle normal con teclado real, equipo y recorrido posterior | 26 | 0 |
| Estructura del kit GLB exportado | 1 | 0 |

Total: **288 pruebas de lógica, 220 comprobaciones de navegador y una prueba de exportación**. Las pruebas geométricas de todas las armas están incluidas en las de lógica, no sumadas otra vez. Son aserciones, no sesiones independientes ni una certificación exhaustiva de un mundo abierto. La lectura independiente del GLB con trimesh tampoco se suma como otra suite de aceptación.

Los cuatro informes finales de navegador registran cero excepciones JavaScript, cero errores WebGL detectados y cero solicitudes HTTP/HTTPS. Las texturas embebidas anteriores siguen dentro del HTML. No se sumaron pases históricos, baseline o intentos interrumpidos.

## Equipamiento y colisiones

Catorce opciones de catálogo, incluida la posición sin equipo. Trece modelos de utilería original: dos de contacto, dos armas cortas, cuatro largas, lanzador, granada, Gauss, EMP y binoculares. Se comprueba independencia de inventarios, reservas/cargadores acotados, cadencia semiautomática y automática, recarga con transferencia al terminar, cancelación y rechazo de datos inválidos.

Los rayos ordenan impactos contra edificios, vehículos orientados, objetos y personajes. Se prueba que una pared próxima bloquea un blanco situado detrás y que el segmento entre cuerpo y boca del arma no atraviesa una esquina aunque la cámara vea el objetivo. Los colisionadores son volúmenes aproximados, no cada triángulo de la escena.

Gauss acumula carga mientras se mantiene la entrada, consume una celda sólo al disparar y exige un mínimo del 23 %. La pausa, cambio de equipo, pérdida de foco e interacciones cancelan sin disparar. Puede atravesar hasta tres objetivos con daño decreciente y se detiene en paredes/terreno. La geometría no contiene una representación de funcionamiento físico o ingeniería real.

Lanzador y granada usan segmentos barridos de movimiento para no saltarse una pared delgada entre muestras. La granada mantiene su mecha de 2.4 s al rebotar o reposar, no detona por acumular arbitrariamente rebotes. Las explosiones se atenúan por distancia y comprueban oclusión opaca. También pueden afectar al jugador.

Los impactos reutilizan las zonas de daño de coches y las reglas de ruptura/marcado de cambios de objetos. Los personajes tienen una respuesta no gráfica y recuperación tras incapacitación temporal. Se comprueba que un conductor desalojado incapacitado no continúa avanzando por el controlador heredado mientras está inmóvil.

## EMP y observación

El EMP interrumpe durante 8 s la propulsión y las luces compatibles dentro de 26 m, con oclusión por edificios. La simulación conserva salud de coches y NPCs, estado de ocupación y alerta policial. Los coches que están en marcha desaceleran de manera continua. La luz vuelve al vencer el temporizador sin marcar el poste como permanentemente roto. El renderer y el audio omiten emisión/propulsión/sirenas correspondientes durante la interrupción, no todo el sonido policial del mundo.

El pulso no elimina la percepción o la captura policial. Un policía cercano aún puede verte. No se simula electromagnetismo físico ni blindaje de componentes reales.

Los binoculares usan cuatro campos de visión equivalentes a 2×, 4×, 8× y 12×. La suite comprueba el valor de proyección real, no sólo una capa de interfaz. La observación consulta el primer volumen/superficie dentro de 600 m, respeta los obstáculos y marca ese punto en GPS. Terreno sin entidad asociada no provoca una excepción de interfaz. No hay lectura a través de paredes, visión térmica ni detección ilimitada.

## Modelos, poses y recursos

Los trece equipos procedurales se agrupan en **65 mallas de material y 8,184 triángulos en total**. Gauss usa 2,148 triángulos. Cada equipo queda por debajo de 4,000. La caché comparte recursos entre usos; no crea copias completas cada vez que se selecciona una tarjeta.

Se verifican vértices finitos, áreas no nulas, orientación de triángulos y normales unitarias. Los objetivos de muñeca se prueban para los trece equipos, tres elevaciones y dos posturas, acotando el error por debajo de 12 mm. Esto no verifica contacto individual de falanges. Retroceso, recarga, lanzamiento y ataque son aproximaciones procedurales, no una animación mecánica completa de cargadores y recámaras.

Las mallas, texturas, once peinados, proporciones y esqueleto humano de v0.16 conservan sus bytes. No se presenta esta entrega como otra revisión anatómica. `behavior-scope.json` documenta los cambios y la nueva capa de equipamiento. La igualdad de fuentes no reemplaza las pruebas de integración.

## Entradas, creador y partidas

Tab abre la selección y pausa el mundo. Elegir una tarjeta no equipa hasta confirmar. Escape y × cancelan la elección. Se verifican categorías, tarjetas, confirmación, controles numéricos y botones accesibles en 390 × 844 y 844 × 390. Son tamaños y eventos táctiles emulados.

Un clic breve se conserva hasta que lo consume el siguiente paso de simulación. Una pulsación nueva justo después de cambiar de equipo se distingue de una entrada vieja que seguía mantenida al cancelar. Se comprueban pérdida de foco, cancelación de puntero y pausa: no descargan accidentalmente Gauss ni dejan disparando un arma automática. L recarga; R conserva su acción de rendición policial. El movimiento de cámara armado usa arrastre derecho o táctil sin confundir mirar con disparar.

El equipo se serializa por partida con selección, munición, reserva y zoom. Partidas anteriores sin `equipment` reciben valores iniciales. Las importaciones inválidas se rechazan antes de modificar dinero, historia o inventario. Dos partidas con equipos distintos se crean/cargan y se descarga un JSON real del navegador. El catálogo conserva IDs y nombres, con hasta doce espacios sujetos a la cuota anterior.

Se repiten creación/edición/cancelación de personajes, copia, renombrado, eliminación, importación/exportación, errores de cuota y conflictos. No se guardan proyectiles, recarga en curso, carga Gauss, EMP activo ni reacciones temporales de NPC. La munición gastada y el daño permanente serializable sí se conservan. No hay nube ni comprobación de persistencia nativa después de cerrar y reabrir el navegador.

## Bucle continuo y evidencia visual

La suite continua utiliza el RAF, la simulación, la cámara y el renderer originales sin sustituirlos. Con teclas reales selecciona Gauss, carga/libera, daña un blanco, pulsa EMP, observa con binoculares, cambia zoom, marca GPS, abre/cierra equipamiento y vuelve a manos libres. Después extrae al conductor, entra, conduce, frena, sale, camina, cruza un sector y utiliza el atlas.

Sus posiciones iniciales y algunos blancos se preparan para reproducibilidad. La campaña coloca al jugador junto a objetivos para comprobar las transiciones del desenlace público. No equivale a completar una partida espontánea ni una sesión de horas.

Las otras suites separan el tiempo de simulación del coste gráfico: la de arsenal pausa RAF después del arranque y dibuja keyframes explícitos; la de catálogo/campaña aparca el renderer entre fotogramas. Todas siguen usando WebGL real. Las capturas preparadas muestran Gauss cargado, onda EMP, observación, recarga y selector de escritorio/táctil. No se usan renders de otro programa ni imágenes generadas para representar el juego.

## Defectos encontrados y corregidos

1. Clics más breves que un frame podían perderse. Se añadió una entrada pendiente que se consume exactamente una vez.
2. La primera pulsación tras cambiar de equipo se descartaba esperando un frame neutral. Se diferencia una pulsación física nueva de un disparo mantenido previamente cancelado.
3. La mecha de la granada se acortaba por el número de rebotes. Ahora puede quedar en reposo y detona por tiempo.
4. El controlador de conductores expulsados desplazaba a NPCs incapacitados. Se preserva su posición durante la reacción y se recupera después.
5. Algunos objetivos de la mano izquierda excedían el alcance y las culatas largas sobresalían por la espalda. Se acercaron los puntos de sujeción y se acortó esa geometría; las capturas finales usan la versión corregida.
6. La interfaz óptica consultaba `police` en una referencia nula al observar suelo. Se distingue la superficie sin entidad.

Los registros de fallos anteriores se conservan en `qa/v017/*red*`. Dos esperas de la suite continua suponían un número de frames o una actualización de FOV inmediata en vez del estado observable. Se ajustaron las esperas de prueba, no se promete FPS ni se interpreta el renderer por software como hardware del usuario.

## Integridad y reproducción

`python tools/audit_arsenal_release.py` reconstruye HTML y kit GLB y exige huellas idénticas. Vuelve a ejecutar Node y el test de exportación; coteja los cuatro informes de navegador ya ejecutados, sus códigos de salida y las capturas contra la huella del HTML. **No ejecuta el navegador por sí mismo.**

El kit GLB no necesita extensiones ni descargas externas. Se verifican cabecera, buffers, posiciones/normales y trece grupos de equipo. Trimesh recupera 65 geometrías y 8,184 triángulos, con límites finitos. No se ejecutó el validador oficial de Khronos ni se revisó cada editor 3D. Los materiales portables no incluyen toda la emisión contextual del juego.

El ZIP contiene código, recursos, pruebas, evidencia y documentación histórica identificada por versión. `SOURCE-MANIFEST.json` enumera las huellas de cada archivo del paquete, salvo el propio manifiesto. No se distribuyen fuentes tipográficas. Los comandos de reproducción están en README y GUIA.

Entorno: Chromium en Linux, Xvfb y ANGLE SwiftShader. HTML inyectado y almacenamiento aislado en memoria. No se probaron Safari, Firefox, teléfonos físicos, GPU del usuario, nubes, sesiones prolongadas, pérdida de contexto gráfico ni persistencia nativa `file://`. No se anuncia una tasa de FPS.

## Límites de producto

Se dispone del catálogo completo para experimentar, con munición finita y reposición por $120 de moneda del juego en puntos permitidos. No hay compra real, selección de productos reales, desbloqueos narrativos o economía de armas nueva.

La representación es estilizada. No se añadieron disparos desde coches, combate armado autónomo de NPCs, autocolisión de manos contra cada arma, ragdoll físico, destrucción de edificios ni balística o electromagnetismo avanzados. Las poses de apuntado/recarga son aproximadas y pueden mostrar intersecciones en algunos encuadres o combinaciones extremas.

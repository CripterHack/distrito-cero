# Distrito Cero v0.13 · Movimiento orgánico

Continúa el juego completo de v0.12. El objetivo de esta iteración es mejorar movimiento, apoyos, agarres y lectura de superficies. No es una entrega AAA terminada ni una sustitución de todos los recursos humanos.

## Jugar y conservar progreso

Abrir `index.html` fuera de la vista previa del chat, en un navegador con WebGL2. Un archivo, sin CDN, instalación, cuenta o recursos que deban descargarse mientras se juega. Para hosting estático se publica ese mismo archivo.

Exportar los JSON desde v0.12 antes de cambiar de archivo. En v0.13, **Mis partidas → Importar JSON** los añade sin sobrescribir por nombre. La selección inicial, cuatro estilos, colores, complexión, rostro, cuello y el límite de doce espacios permanecen. El nombre del personaje es distinto del de la partida. El guardado sigue siendo local, sujeto a permisos y cuota, no nube.

## Qué revisar

**Crear personaje → Revisar en movimiento** incluye las poses anteriores y dos nuevas: **Conducir · inspección** y **Alcanzar**. La primera es una pose sentada en el estudio, no la representación de un vehículo de prueba dentro del editor.

En **Inspección** se puede enfocar **Piernas y apoyos**, además de cuerpo, rostro, cuello y manos. **Reproducción** permite 0.25×, 0.5× o 1×. Afecta sólo a la vista previa, nunca a la velocidad de la partida ni a su guardado. Las transiciones de locomoción se interpolan. Una nueva pose seleccionada mientras está pausado se presenta directamente para inspección.

En el juego, caminar, correr, girar y frenar utilizan cadencia ligada a distancia real. Hay apoyos analíticos de pie, despegue y contacto de talón/punta, codos más flexionados al correr, respiración torácica leve y compensación de cabeza. La memoria visual por persona conserva apoyos durante la fase de contacto. Se reinicia al cambiar de simulación, teleportar o detectar discontinuidades. No modifica colisiones, daño, posición de física ni recompensas.

Los conductores y el jugador sentado usan objetivos de muñeca compartidos con la posición del volante. Los perfiles de dedos distinguen reposo, carrera, carga, alcance y conducción. Esto es cinemática, no un solver físico de cada dedo contra la superficie.

Las superficies de hombros y zonas de flexión de la ropa se suavizaron con desplazamiento acotado, sin añadir triángulos. Se unificaron normales de vértices coincidentes de las manos para reducir facetas de sombreado. Se mantiene la forma de las manos, uñas, rostro y sus mapas. La tela y la piel tienen microdetalle filtrado, los ojos mantienen su volumen al parpadear y la mirada cambia de dirección por intervalos en vez de oscilar continuamente.

## Controles conservados

WASD o flechas para moverse y conducir. Shift para correr. F para iniciar o cancelar acceso/salida del coche. E para interactuar. G para lanzar o empujar. X para agacharse. Q para esquivar o usar bocina. Espacio para saltar/frenar. V mantenida para reparar. R mantenida para rendirse. M para atlas, P para foto y Esc para pausa.

Para probar conducción y agarre: acércate al lado de un vehículo casi detenido, pulsa F y espera al cierre de la puerta. Los autos ocupados conservan la extracción del conductor. No se añadieron ventajas de combate, invulnerabilidad ni cambios de coste.

## Límites visibles

Se conserva el rig de 49 huesos, los tres LOD y la misma familia corporal. El acabado sigue estilizado. No hay mocap, músculos físicos, ropa simulada, pelo por fibras físicas, escaneos nuevos ni expresiones faciales completas. La precisión de las manos y contactos en poses extremas sigue siendo limitada.

Los apoyos se calculan para el terreno transitable plano. No adaptan los pies a cada escalón, objeto móvil o rama. Un giro extremo puede liberar y recolocar un apoyo para evitar una torsión excesiva. La vista de estudio reproduce marcha en el sitio, sin fingir que el personaje viaja por el mundo.

Los GLB son opcionales y no se cargan al jugar. El modelo neutral exportado tiene nueve estudios: Idle, Walk, Run, Crouch, Carry, HandRelaxed, HandGrip, Seated y Reach. Incluye las traslaciones locales necesarias para el movimiento torácico. La mayoría de efectos de material, mirada, parpadeo, contacto persistente y las secuencias de acceso siguen siendo código de runtime. Un visor puede usar skinning lineal, distinto al DQ del juego.

## Verificación y entorno

Consultar `VERIFICACION.md`. El vídeo se construye con fotogramas reales del renderer a tiempo de animación controlado. No son imágenes generadas ni un benchmark de FPS. Las pruebas continuas mantienen el bucle original por separado.

No se afirma persistencia nativa después de cerrar/reabrir `file://`, rendimiento de GPU real, teléfonos físicos, Safari, sesiones prolongadas o sincronización en nube.

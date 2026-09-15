# Distrito Cero v0.18 · Manejo y contacto

Continuación directa de Arsenal v0.17. HTML autónomo con JavaScript y WebGL2 nativos. Sin instalación, CDN, conexión obligatoria ni librerías de runtime.

## Jugar y conservar las partidas

Abrir `index.html` en un navegador con WebGL2. También puede publicarse en hosting estático. Exportar los JSON de la versión anterior e importarlos desde Mis partidas antes de continuar. El almacenamiento es local y sujeto a permisos/cuota. No hay nube ni garantía de compartir datos entre dos archivos HTML distintos.

## Selector sobre la escena

**Tab** abre el selector en una capa translúcida. Se mantiene la escena real del juego debajo, con la misma cámara, proyección y postura del equipo. El tiempo del mundo se pausa. El desenfoque es moderado y la transparencia está en los fondos, no en los textos.

Elegir una tarjeta sólo modifica la selección pendiente. **Equipar** la confirma; **Esc** o **×** cancelan y conservan el equipo anterior. Al abrir se cancelan el gatillo y la carga Gauss sin dispararlos, y la imagen de la pose previa se conserva mientras el menú esté abierto. Una recarga en curso queda pausada y continúa si se cierra sin cambiar de equipo. Al cambiar de equipo la recarga anterior se cancela, como en v0.17.

Los clics y las teclas de juego no atraviesan el selector. Tab y Shift+Tab recorren sus botones, y el foco vuelve al juego al cerrar. El diseño se adapta a pantallas verticales y horizontales.

## Sujeción y manejo

El arma, la mano dominante, el apoyo y las piezas móviles consultan el mismo montaje. Cada familia tiene puntos de contacto y orientación de palma/dedos propios. Las muñecas ya no copian simplemente la orientación del antebrazo. Una parte acotada de su torsión se distribuye sobre el antebrazo, conservando las longitudes óseas.

Se distinguen pistolas/revólver, armas largas, equipo pesado, armas de contacto, granadas y binoculares. Los dedos tienen flexión diferenciada por mano y contexto. No hay colisión física individual por falange.

Hay una pose de transporte bajo que se eleva al apuntar, un pequeño balanceo ligado al movimiento y un retroceso con recuperación amortiguada. Las manos acompañan el mismo movimiento que el arma, sin tener un retroceso independiente.

Las recargas tienen fases coordinadas de aproximación, manipulación y retorno al apoyo. Pistola, subfusil, fusil, rifle de precisión, Gauss y EMP muestran una pieza de cargador/celda separable. El modelo no conserva a la vez una segunda copia fija en su lugar. El revólver, la escopeta y el lanzador utilizan gestos simplificados hacia su zona de carga.

Son animaciones de videojuego. No simulan todos los mecanismos, contactos o pasos físicos de cada arma. No se añadió captura de movimiento, combate armado autónomo de NPCs, disparo desde coches ni nuevas animaciones humanas escaneadas.

## Controles conservados

**J / clic izquierdo:** usar el equipo. **Z / clic derecho:** apuntar u observar. **L:** recargar. **9:** Gauss. **0:** EMP. **B:** binoculares. **Rueda o +/−:** zoom de binoculares. **H:** marcar observación. **R:** rendición policial. **F:** entrar, salir o cancelar acceso a vehículos.

Los modelos humanos, los once peinados, los 49 huesos y el creador se conservan. También las partidas con nombres, el inventario por partida, las persecuciones y el territorio procedural. El nuevo estado de amortiguación es transitorio y no cambia el formato de guardado.

## Desarrollo

```sh
python build.py
node --test tests/*.test.cjs
python tools/export_handling.py
python tests/handling_exports.test.py
DISPLAY=:99 python tools/run_handling_browser.py
DISPLAY=:99 python tests/handling_capture.py rifle
DISPLAY=:99 python tests/handling_capture.py gauss
DISPLAY=:99 python tests/handling_capture.py reload
python tools/audit_handling_release.py
```

Las herramientas de pruebas/autoría son dependencias de desarrollo, no del juego. Ajustar DISPLAY y la ruta de Chromium al sistema local. Los scripts históricos siguen identificados por versión. El kit GLB opcional es utilería estática con piezas nombradas, no una exportación del personaje ni de sus secuencias de recarga.

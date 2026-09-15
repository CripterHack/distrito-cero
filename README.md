# Distrito Cero v0.19 · Contacto articulado

Juego de navegador en un HTML autónomo, con JavaScript y WebGL2 nativos. Continuación de v0.18, sin CDN, instalación ni descargas durante la partida. Creador, peinados, campaña, territorio procedural, arsenal y biblioteca de partidas conservados.

## Jugar

Abrir `index.html` en un navegador con WebGL2 o publicarlo como sitio estático. **Tab** abre el selector translúcido. **J / clic izquierdo** usa el equipo, **Z / clic derecho** apunta, **L** recarga. **9** Gauss, **0** EMP, **B** binoculares. **R** conserva la rendición y **F** el acceso a vehículos.

Exportar las partidas JSON antes de cambiar de HTML. La versión mantiene los doce espacios con nombres, sujetos a la cuota y permisos del navegador. No hay guardado de nube. No se cambia la clave ni el esquema de inventario.

## Cambios

El montaje utiliza anclas de superficie de palma y deriva desde ellas la muñeca. El torso participa en la postura de las armas largas y la culata consulta el hombro articulado. Las pistolas se extienden al apuntar. La mano de apoyo se abre durante los trayectos libres de recarga, acompaña el giro de la pieza y vuelve al apoyo. El índice tiene transición propia y no se cierra simplemente por apuntar. El equipo utiliza inercia leve y recuperación de retroceso por familia.

Los nueve modelos con empuñadura principal reciben una pieza de sección redondeada. El selector permanece translúcido sobre el juego pausado. Al cerrarlo se conserva sólo el estado visual necesario para bajar progresivamente el arma, nunca la carga o el disparo. El cambio de arma inicializa la postura baja antes del primer render.

Estas son animaciones y utilería ficticias. No hay contacto físico por cada falange, réplica de mecanismos reales ni combate armado autónomo de NPCs. No se anuncia fotorrealismo o acabado AAA. Las mallas humanas y el catálogo de peinados no se sustituyen.

## Fuentes

`src/weapon-handling.js` define montaje, contactos, estados visuales y piezas móviles. `src/skin-rig.js` integra el torso armado y expone la referencia palmar. `equipment-renderer.js` comparte el actor de movimiento con el montaje, y coloca las piezas animadas. `equipment-simulation.js` inicializa el estado visual al equipar sin cambiar la economía del inventario. `equipment-ui.js` conserva el retorno progresivo desde el selector.

`docs/v019/GUIA.md`, `VERIFICACION.md` y `PLAN.md` documentan esta versión. `qa/v019/release-report.json` vincula los bytes del HTML con pruebas y capturas. Las versiones históricas tienen sus propios directorios y no se suman como pases actuales.

## Construcción y comprobación

```sh
python build.py
node --test tests/*.test.cjs
python tools/export_contact.py
python tests/contact_exports.test.py
DISPLAY=:99 python tools/run_contact_browser.py
DISPLAY=:99 python tools/capture_contact_release.py
DISPLAY=:99 python tests/contact_clip.py
python tools/compose_contact_evidence.py
python tools/audit_contact_release.py
python tools/package_contact.py /mnt/data/distrito-cero-v0.19-codigo.zip
```

El build usa la biblioteca estándar de Python. Playwright, Chromium, Xvfb, Pillow y ffmpeg sirven sólo para desarrollo y evidencia. `requirements-dev.txt` conserva las herramientas de autoría. Nada de ello se necesita para abrir el HTML. El GLB `assets/dc019-equipment.glb` es un kit estático opcional, no incluye al personaje ni la animación del runtime.

Las pruebas de navegador usan HTML inyectado y un almacenamiento explícito en memoria. No certifican persistencia nativa al cerrar/reabrir un archivo local, Safari, teléfonos físicos o una tasa de FPS. Las capturas y el vídeo son fotogramas reales del motor con cámaras preparadas, no imágenes generadas. No se distribuyen fuentes tipográficas.

El HTML de referencia v0.18 se conserva en `assets/baseline-v018.html` exclusivamente para comparaciones. `DC_BASELINE_HTML` permite usar otra ruta de ese mismo archivo. No se carga desde el juego.

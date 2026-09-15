# Distrito Cero v0.15 · Integración cervical

## Abrir y conservar progreso
Abrir `index.html` en un navegador con WebGL2, fuera de la vista previa del chat. El HTML no requiere librerías, CDN, servidor de juego ni descargas durante la partida. Para publicar, el mismo archivo puede servirse desde un hosting estático.

Antes de cambiar de versión, exportar los JSON de las partidas anteriores. En la versión nueva, abrir **Mis partidas → Importar JSON**. Los doce espacios con nombres, copias y exportación/importación se conservan, sujetos a cuota y permisos. El formato no cambia, pero las proporciones visuales del cuello sí se actualizan. No es guardado en nube. No se ha comprobado persistencia nativa entre cierres y reaperturas de archivos locales.

## Examinar el cambio
Abrir **Crear personaje → Revisar en movimiento**. Seleccionar **Cuello y hombros** en Inspección y comparar reposo, **Cuello · giro suave** y **Cuello · flexión y extensión**. Usar 0.25× o 0.5× para revisar la deformación. Orbitar para examinar tres cuartos, perfil y nuca. También se conserva la edición desde Pausa.

La **Complexión** ahora cambia moderadamente el volumen del cuello, además del cuerpo vestido. **Grosor del cuello** sigue permitiendo una variación independiente, con un rango más contenido alrededor de la nueva base anatómica. No cambia estatura, esqueleto, fuerza, velocidad o colisionadores. La mandíbula anterior no se ensancha mediante ese control.

La personalización es un borrador: **Cancelar** no modifica la apariencia guardada. **Aplicar** actualiza el espacio activo. El editor, búsqueda y orden de partidas, los colores y los peinados no se han reemplazado.

## Controles conservados
WASD/flechas: caminar y conducir. Shift: correr. F: iniciar o cancelar acceso/salida de coche. E: interactuar. G: lanzar/empujar. X: agacharse. Q: esquivar/bocina. Espacio: saltar/freno. V mantenida: reparar. R mantenida: rendición. M: atlas. P: modo foto. Esc: pausa. Los controles táctiles siguen disponibles.

## Alcance visual
El cuello tiene más masa, una nuca que se estrecha hacia el cráneo y una transición de deformación menos concentrada bajo el mentón. La abertura de la chaqueta y parte del cierre acompañan la nueva forma. Protagonista, peatones y conductores comparten el cambio con sus parámetros individuales.

Se conservan 49 huesos y 85,209 triángulos de detalle alto. No es una nueva anatomía de manos, un peinado nuevo ni captura de movimiento. No hay autocolisión general de tejidos, tela/pelo físicos ni contactos individuales de cada falange. El resultado sigue estilizado y no alcanza la referencia hiperrealista/AAA. Algunas poses extremas pueden mostrar limitaciones.

## Reconstruir y verificar

```bash
python tools/integrate_cervical_v015.py
python build.py
python tools/export_integration_glb.py
node --test tests/*.test.cjs
python tools/run_integration_geometry.py
DISPLAY=:99 python tools/run_integration_browser.py
DISPLAY=:99 python tools/run_integration_captures.py
DISPLAY=:99 python tests/integration_clip.py
```

Python/NumPy/SciPy, Node, Chromium/Playwright, Xvfb y ffmpeg son herramientas de desarrollo, no requisitos del HTML. Las rutas de Chromium y display del laboratorio deben adaptarse en otros sistemas. Los constructores antiguos son históricos, no se usan para producir v0.15.

# Distrito Cero v0.16 · Rasgos

Continuación directa de v0.15 Integración cervical. Juego completo en un HTML autónomo, JavaScript y WebGL2 nativos. No necesita CDN, motor externo, librerías de runtime o conexión durante la partida.

## Cambios actuales

La cabeza se acerca al tórax 45 mm en el ajuste neutro. `character-fit.js` transforma la región cervical y los pivotes del esqueleto al mismo espacio antes de deformarla. El rostro y el cráneo se trasladan, no se aplastan. El control **Longitud del cuello** permite una reducción total de 33 a 57 mm respecto de v0.15. El grosor previo y la relación moderada con complexión se conservan. La cápsula física y las capacidades del jugador no cambian.

El cabello se separa de las cejas y pasa a un catálogo de once opciones con geometría compartida y tres niveles de detalle. Siete son nuevos estilos. El editor añade volumen y vinculación del color de las cejas. Se preservan los índices anteriores 0–3 y se completan campos nuevos al importar perfiles antiguos. Los NPCs y conductores usan la misma familia de modelos, con parámetros independientes.

El resultado sigue estilizado. No se anuncia equivalencia AAA, cabello físico, escaneo nuevo o simulación muscular.

**Jugar:** abrir `index.html` fuera de la vista previa del chat. **Conservar partidas:** exportar JSON desde la versión anterior e importar desde **Mis partidas**. **Inspeccionar:** Crear personaje → Rasgos y materiales, o Revisar en movimiento → Cuello y hombros. La edición desde Pausa también está disponible.

## Desarrollo

```bash
python build.py
python tools/export_traits_glb.py
node --test tests/*.test.cjs
python tools/run_traits_geometry.py
DISPLAY=:99 python tools/run_traits_browser.py
DISPLAY=:99 python tests/traits_gallery.py
DISPLAY=:99 python tools/capture_traits_release.py
python tools/compose_traits_gallery.py
python tools/audit_traits_release.py
python tools/package_traits_release.py
```

`python build.py` utiliza la biblioteca estándar. Las dependencias de `requirements-dev.txt`, Chromium, Xvfb y ffmpeg son de autoría/verificación, no requisitos del HTML. Ajustar las rutas de ejecutables y display a otro sistema.

El recurso canónico de cuerpo/cara `src/hero-asset.js` conserva los bytes de v0.15. El ajuste cervical de distribución vive en `src/character-fit.js`, su equivalente GLSL y la evaluación de bind en `skin-rig.js`. `src/hair-geometry.js` contiene el generador y la envolvente craneal; el mismo insumo numérico está separado en `assets/hair-scalp-grid-v016.json`. No requiere acceso a un servicio remoto para reconstruir los estilos.

El exportador aplica el ajuste neutro y el peinado clásico a los buffers portables. Produce `assets/dc016-human-traits.glb`, con 49 huesos y once estudios de pose. No ejecutar un constructor histórico para sustituir la malla de esta entrega. Los GLB de versiones anteriores siguen identificados por su versión.

## Evidencia y límites

Guía: `docs/v016/GUIA.md`. Plan ejecutado: `docs/v016/PLAN.md`. Informe: `docs/v016/VERIFICACION.md`. Resultados actuales: `qa/v016/`. Procedencia: `assets/ATTRIBUTION-v016.md` y atribuciones conservadas.

Las suites por estados usan fotogramas WebGL reales, HTML inyectado y almacenamiento aislado en memoria. La suite continua conserva RAF, simulación, cámara y renderer. No se verificó persistencia nativa después de cerrar/reabrir `file://`, GPU física, Safari, teléfonos físicos o sesiones de horas. No se promete un FPS. Las cifras son aserciones, no sesiones completas ni una certificación artística.

Los peinados largos siguen la cabeza como geometría rígida. No hay colisión individual de hebras contra ropa/carrocería ni simulación de inercia. Las opciones de flequillo/laterales están incorporadas en cada estilo, no son controles independientes ilimitados. El color de cejas desvinculado es castaño, no otro selector de paleta. El volumen no se aplica a rapado o ausencia de cabello. Las partidas conservan las opciones, no imágenes en miniatura nuevas.

## Integridad del paquete

El ZIP incluye fuentes, recursos, herramientas, documentación y evidencia de v0.16. `SOURCE-MANIFEST.json` relaciona sus huellas. Las carpetas `.git`, capturas históricas, ensayos iniciales, archivos tipográficos e imágenes intermedias del vídeo no se distribuyen. El vídeo final y los scripts de captura sí se incluyen. El exportador GLB aproxima materiales del motor con PBR portable: no reproduce íntegramente DQ, cabello tramado, mirada, parpadeo, personalización y acciones con vehículos.

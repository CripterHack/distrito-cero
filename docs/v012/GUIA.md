# Distrito Cero v0.12 · Continuidad anatómica

Continuación de Identidad v0.11. HTML autónomo, JavaScript y WebGL2 nativos. Sin CDN, conexión obligatoria, cuenta, telemetría remota ni bibliotecas externas de ejecución. Es una iteración de modelado y deformación, no una entrega AAA terminada.

## Empezar o conservar tu historia

Abrir `index.html` en un navegador con WebGL2. Para alojamiento estático publicar el mismo archivo como `index.html`. Fuera de la vista previa del chat.

Antes de cambiar de versión, exportar los JSON de v0.11. En la nueva versión, **Mis partidas → Importar JSON** añade las historias sin reemplazarlas por nombre. Las identidades antiguas sin el parámetro `neck` reciben el valor neutro. Se conserva la clave de catálogo `distrito-cero:saves:v2`, su estructura y el límite de 12 espacios sujeto a la cuota que permita el navegador.

## Creador y selección inicial

**Crear personaje** abre el editor antes de comenzar. Los cuatro estilos base siguen siendo Nómada, Nácar, Aurora y Asfalto, con complexión, contorno de rostro, cabello, colores de piel, iris y ropa. Nombre del personaje y nombre de partida son independientes. No se han añadido nuevos tipos de ropa ni cuatro anatomías escaneadas diferentes.

Nuevo en v0.12:

* **Grosor del cuello**: variación acotada de volumen, sin cambiar estatura, huesos, muñecas, colisión ni capacidades del personaje.
* **Revisar en movimiento → Inspección**: cuerpo, rostro, cuello/hombros y mano/muñeca.
* **Iluminación**: estudio neutro, luz lateral o exterior suave, aplicados sólo a la vista del creador. Al cerrar vuelve la luz del juego.
* **Pose**: se añaden manos abiertas y agarre suave a reposo, caminar, correr y agacharse. La inspección de mano sigue su punto de muñeca articulado.
* **Comparar con el inicio**: alterna temporalmente con la apariencia con la que abriste el editor, no con una versión antigua del motor. El borrador sigue intacto. Aplicar desde la comparación guarda tus cambios, no la vista temporal.

El editor tiene su propia simulación y cámara. Cancelar no modifica el mundo ni la apariencia de la partida real. Aplicar afecta solamente al espacio activo, con reversión ante fallo de almacenamiento. También disponible desde **Pausa → Editar personaje**.

## Partidas con nombre

**Mis partidas** permite crear historias independientes, cargar, renombrar, duplicar lo guardado, guardar una copia de la sesión actual, exportar una historia o toda la biblioteca y borrar con confirmación. El autoguardado sólo actualiza el espacio activo. Nombres iguales no equivalen a un mismo ID.

Ahora se puede **buscar por nombre de partida o personaje**, sin distinguir mayúsculas o tildes, y ordenar por **último guardado, nombre o progreso de historia**. Ordenar no escribe ni altera las partidas. La exportación completa permanece disponible aunque la búsqueda no muestre coincidencias.

No es almacenamiento en la nube. Exportar el JSON antes de cambiar de dispositivo, navegador, ruta del HTML o borrar datos locales. La cuota y los permisos pueden impedir guardar. La aplicación informa del fallo y no presenta una escritura fallida como éxito. Los conflictos de revisión permiten recargar con confirmación o conservar una copia. No hay bloqueo distribuido entre pestañas. Se conserva la opción explícita de jugar sin guardado si el almacenamiento está bloqueado.

## Qué cambió en los personajes

Cuello ensanchado hacia el tórax, transición de pesos pecho/cuello/cabeza, abertura real de la chaqueta, hombros y axilas suavizados, silueta de muñeca y palma más contenida, uñas ajustadas a la superficie de cada dedo y detalle de piel procedural. La cabeza y sus tres mapas de v0.9 se conservan. Los cambios se usan también en peatones y conductores.

La deformación de las mallas compartidas usa **cuaterniones duales** calculados a partir de las mismas matrices de 49 huesos. Color, sombra y reflejos consumen la misma pose. El objetivo es reducir pérdida de volumen durante giros y mezcla de articulaciones. No es simulación muscular, no elimina todas las intersecciones y puede producir abultamientos en flexiones extremas.

## Controles del juego conservados

WASD/flechas: movimiento y conducción. Shift: correr. F: iniciar o cancelar entrada/salida. E: interactuar. G: lanzar/empujar. X: agacharse. Q: esquivar. Espacio: saltar/freno de mano. V mantenida: reparar. R mantenida: rendirse. M: atlas. P: foto. Esc: pausa. Las entradas táctiles siguen disponibles.

Se conservan campaña, extracción de conductores, daños de vehículos, destrucción/restauración de objetos y expansión procedural. El territorio sigue siendo plano y principalmente ortogonal.

## Construcción reproducible

El HTML distribuido ya está construido. No se requiere Python, Node, Blender ni instalación para jugar.

```bash
# Sólo empaquetar las 28 fuentes, Python estándar.
python build.py

# Reproducir la malla y su exportación actual con herramientas de desarrollo.
python tools/build_hero_v012.py
python build.py
python tools/export_continuity_glb.py
```

Los scripts históricos `refine_identity.py` y `build_hero_v010.py` reconstruyen sus versiones antiguas. **No ejecutarlos como constructor de v0.12**, pues reemplazarían la geometría actual.

Dependencias de desarrollo en `requirements-dev.txt`. El GLB nuevo `assets/dc012-human-continuity.glb` contiene la geometría actual, 49 huesos, mapas y siete estudios procedurales. Un visor glTF convencional puede usar skinning lineal en lugar de cuaterniones duales. Parpadeo, mirada, material procedural y acceso a coches pertenecen al runtime. El archivo portable no replica todos los efectos del juego ni exporta cada apariencia personalizada.

## Pruebas actuales

```bash
node --test tests/*.test.cjs
python tests/body_geometry.test.py
python tests/continuity_anatomy_regression.test.py
python tests/continuity_geometry.test.py
python tests/continuity_export.test.py
DISPLAY=:99 python tests/continuity_browser.py
DISPLAY=:99 python tests/continuity_library_regression.py
DISPLAY=:99 python tests/legacy_continuity.py
DISPLAY=:99 python tests/continuity_continuous.py
```

Las rutas de Chromium/display se adaptan al equipo de desarrollo. En el laboratorio se utilizaron Chromium, Xvfb y SwiftShader. La navegación `file://` fue bloqueada por la política del entorno, así que las pruebas cargan HTML con almacenamiento aislado en memoria. No se verificó persistencia nativa tras cerrar y reabrir archivos locales, Safari, Firefox, teléfonos físicos ni GPU del usuario. Los números de comprobaciones no son sesiones completas, certificación AAA ni promesas de FPS. Informe detallado en `VERIFICACION.md`.

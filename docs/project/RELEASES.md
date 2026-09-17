# Identidad de producto y proceso de publicación

`version.json` es la única fuente de número de producto, nombre, canal y fecha. No cambiar los números de esquemas de datos al publicar un cambio visual. El nombre de un GLB histórico tampoco define la versión actual del juego.

`python3 build.py` genera `index.html` y `build-info.json`. El HTML incorpora `DC.BuildInfo` inmutable, metadatos y etiquetas visibles. El sidecar contiene tamaño y SHA-256 del HTML, además de la huella de sus insumos explícitos. `--check` no escribe: falla si falta o está desactualizada una salida. No introduce una llamada HTTP en runtime.

Una publicación exige pruebas aplicables, revisión de diferencias, documentación vigente, CI del PR, CI del push a master y comprobación del sitio público. El estado success de un PR no equivale al resultado de otro runner posterior. Conservar los fallos históricos, no reetiquetarlos ni reintentar hasta ocultarlos.

El número completo usa tres componentes, como `0.20.0`. La UI muestra `v0.20` cuando el parche es cero y muestra el parche cuando no lo es. La etapa sigue siendo `prototype`; aprobar otro canal requiere decisión de producto, no sólo editar el manifiesto.

Al actualizar versión, revisar README, índice de recursos, STATE, guía vigente, changelog y handoff. Los tests comparan las etiquetas vigentes con el manifiesto, sin exigir que los archivos históricos pierdan sus versiones originales. Los resultados nuevos de CI siempre identifican el SHA del HTML.

Para soporte, solicita la versión y el identificador que muestra Pausa. Recargar conserva datos del mismo origen. Borrar el almacenamiento local no es un procedimiento de actualización. GitHub Pages publica master por configuración existente, no cambiada por este proceso.

## Checkouts con distintas políticas de saltos de línea

La revisión previa a publicar v0.20 reprodujo otro caso: al clonar con `core.autocrlf=true`, Git convertía fuentes y HTML a CRLF. Aunque el código fuese equivalente, las huellas dejaban de coincidir y `build.py --check` fallaba. `.editorconfig` no controla el checkout de Git.

`.gitattributes` conserva LF en los archivos de texto y desactiva la conversión para medios/datos binarios. No modifica la configuración global del usuario, no introduce LFS ni altera el juego. `tests/release_checkout.test.py` crea repositorios temporales y comprueba las tres políticas `true`, `input` y `false`, los hashes del HTML/sidecar y una muestra binaria. El caso `true` falló antes del ajuste y los tres pasan después. Este ensayo reproduce la política de Git, no acredita el juego en un equipo Windows físico.

Ejecutar `python3 tests/release_checkout.test.py` junto a las pruebas de build antes de aceptar cambios de distribución. Una rama ya clonada puede conservar un archivo modificado localmente; no realizar resets destructivos para actualizarla.

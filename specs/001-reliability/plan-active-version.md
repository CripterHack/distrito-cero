# Unidad de publicación v0.20 · Coherencia

Issue #19, solicitud explícita de versión activa. Base publicada `ef905ec`; integra el correctivo de autoría pendiente de `91ba765` sin duplicarlo. Avance parcial de #6, sin cerrar #5/#6/#7.

## Contrato

Una sola fuente `version.json` para versión de producto, nombre, canal y fecha. `build.py` genera título, etiquetas de inicio/pausa/interacciones, objeto inmutable `DC.BuildInfo` y `build-info.json` con SHA-256 del HTML y fuentes. Fecha declarada, sin timestamp de construcción, ruta de máquina o SHA de Git autorreferencial. Reconstrucción idéntica desde el mismo árbol, con o sin .git.

La versión de producto es independiente del esquema de partidas, inventario y recursos. No reemplazar sus números ni las claves de localStorage. Conservar archivos históricos y sus hashes. Actualizar únicamente documentación rectora y notas de la nueva versión.

## Tareas

1. Revisar rama de autoría, fuente, tests y regresión original sobre ef905ec. Completar su QA gráfico.
2. Pruebas fallidas de identidad canónica, marcas sin resolver y modo --check no mutante.
3. Build validado y determinista, identidad visible en los tres lugares e identificación exacta por fuente.
4. Prueba de navegador HTTP nativo con interfaz, pausa, guardados/importación, descarga JSON y ausencia de consultas de versión en runtime.
5. Notas v020, changelog y estado actual que separen historia de producto. CI conserva suites existentes y añade contratos nuevos.
6. PR revisado y CI, merge y verificación del push/Pages. Cerrar #19 sólo con prueba de publicación. No presentar la existencia del plan como ejecución.

## Fuera de alcance

Nuevas armas, otro rig, físicas, aprobación artística AAA, cambio de licencia, despliegue de otro sitio, telemetría o compras. El refinado de contorno no implica contactos exactos de toda la mano. Reversión sin migrar datos.

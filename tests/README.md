# Pruebas actuales y pruebas históricas

Para v0.8 ejecutar todos los `*.test.cjs` con Node, `presence_mesh.test.py`, `presence_exports.test.py`, `presence_browser.py`, `legacy_presence.py`, `horizon_presence.py` y `presence_continuous.py`. La lista exacta y el alcance están en `docs/v08/VERIFICACION.md`.

Los scripts cuyo nombre hace referencia a v0.5 o a versiones anteriores permanecen para consultar la evolución. No todos representan las expectativas del acceso con F, que dejó de ser instantáneo. No sumar sus informes históricos al resultado de v0.8. `legacy_presence.py` es la regresión adaptada a las transiciones actuales, no una eliminación de las comprobaciones heredadas.

`presence_capture.py` y `presence_clip.py` producen imágenes WebGL para revisar el arte. El vídeo muestrea simulación a tiempo controlado y no mide rendimiento de hardware. La carpeta `qa/v08/clip-frames` es temporal y queda fuera de Git y del ZIP.

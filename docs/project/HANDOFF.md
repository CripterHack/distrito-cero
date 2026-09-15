# Handoff · ejecución de los issues iniciales

## Base y publicación

Base remota al iniciar: `d34751c22eccf519efc5386a6c8f87e5407d99df` en master. El usuario confirmó GitHub Pages publicado desde master. No se cambia esa configuración. Los cambios se proponen y verifican en ramas antes de integrar.

## Unidad actual: #2 / DC-001

Implementado el runner portable de `tools/qa/`, sus tests y el adaptador de navegador compartido por las cinco suites vigentes. Las aserciones se conservan. La evidencia nueva queda bajo `artifacts/`, con copia aislada, timeouts y rechazo de informes viejos. Consultar el PR y Actions para los resultados exactos de su commit.

## Siguiente unidad: #3 / DC-002 y DC-003

Añadir origen HTTP local real y perfil de navegador temporal persistente, sin sustituir localStorage. Crear dos partidas con identidades/inventarios distintos, cerrar y reabrir, renombrar/borrar, comprobar importación y conflicto entre dos páginas reales. Los tests de fixtures se conservan como evidencia separada.

Después abordar #4: recuperación WebGL sin reiniciar simulación, duplicar RAF/listeners o perder el borrador del creador. Primero inventariar constructor, recursos e imágenes pendientes.

## Frente de presentación

#5 prepara benchmark de anatomía, cámaras, luces y poses. #6 depende de referencias estables para las mejoras de contactos. #7 depende de los gates del roadmap y requiere una partida íntegra y playtest humano; no se cierra por redactar una propuesta.

## Verificación mínima

`python3 build.py`, `node --test tests/*.test.cjs`, `python3 tests/qa_runner.test.py`, exportación GLB y `python3 -m tools.qa.run --suite handling`. Leer QA.md para navegador/display. No modificar evidencias históricas ni inferir resultados de otro commit.

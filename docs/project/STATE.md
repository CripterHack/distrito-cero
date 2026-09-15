# Estado real del proyecto

## Estado actual, 15 de septiembre de 2026

El gameplay sigue basado en v0.19, con endurecimiento posterior en master. El usuario activó GitHub Pages desde master. No se modificó su configuración ni se asignó una licencia global.

| Capacidad / issue | Estado comprobado |
| :--- | :--- |
| #2 · Runner de QA | Cerrado por PR #8. Copia aislada, configuración explícita y rechazo de informes antiguos. |
| #3 · Guardados nativos | Cerrado por PR #9. 35 checks Chromium HTTP con perfil persistente, reapertura y dos páginas reales. |
| #4 · Recuperación WebGL | Cerrado por PR #10 (`a752e9e`). Reconstrucción del renderer sin reiniciar la sesión y reanudación explícita. |
| #5 · Personaje patrón | Primera unidad técnica implementada: matriz/capturas/medidas/galería. Aprobación artística y resto de gates pendientes. |
| #6 · Contactos/recargas | Pendiente de nuevas correcciones. Las tolerancias de muñeca no certifican ausencia de deformaciones de prenda o dedos. |
| #7 · Vertical slice | Pendiente de implementación integral y validación de juego/hardware. |

El HTML del commit de recuperación tiene **8,851,321 bytes**, SHA-256 `3f1f5ac6a6d3aa7a74b8046a89f0a5f13b06d9982899131a8351a9909df67318`. El benchmark se incorpora sólo como herramienta de desarrollo, no modifica ese HTML.

## Madurez y sistemas

**Prototipo integrado, no calidad AAA demostrada.** Se conservan personajes de 49 huesos/DQ/LOD/once peinados, creador, doce slots por ID, catálogo de equipo, conductores, acceso ocupado/vacío, objetos, daño, policía, campaña y regiones procedurales.

Persisten brechas de anatomía, prendas, materiales, pelo, dedos y expresiones; contactos y recargas siguen siendo aproximaciones. No existe combate armado autónomo de NPCs, mundo con terreno transitable avanzado ni una vertical slice nueva completa. La matriz ahora sirve para detectar fallos que un recuento de tests no puede aprobar artísticamente.

## Evidencia reciente

PR #10 run `34940253023`: 337 Node, comprobación de exportación, manejo WebGL, 22 checks de pérdida/restauración y la suite nativa de 35 checks. La recuperación utiliza contexto WebGL real pero fixture de almacenamiento; el job HTTP separado no sustituye localStorage. No se suman ambas modalidades como prueba de una misma propiedad.

El benchmark nuevo tiene smoke de 30 capturas/36 checks y pruebas unitarias de matriz y medidas. Los resultados del HEAD se leen de su workflow y artefactos. La cobertura full de 586 casos disponible no se declara ejecutada por el simple hecho de generar su matriz. La aprobación artística permanece separada y pendiente.

## Origen preservado

Importación íntegra original: commit `23f9e9d031c7a0ad270cd74ce0805ea0dfc385da`. ZIP original: 80,607,113 bytes y SHA-256 `307c8fd0d3093eb7d16a3468470a2dfd20ffa12a654ecbe306f07f8aea8a1241`. Se importaron 730 archivos, con 729 hashes en SOURCE-MANIFEST, que permanece histórico.

El HTML original v0.19 tenía SHA-256 `3aa9a27f4941ea1c701069c61db133ab3c93087e35d833d4921ba25b8a4b059f`. Sus 328 tests Node y 271 aserciones de navegador son evidencia de aquella entrega, no el recuento universal de todas las revisiones posteriores. No se reescribe ese manifiesto para ocultar cambios.

## Arquitectura y límites

El build actual concatena 38 JS en orden significativo, incluyendo recursos/recuperación. Las capas sustituyen referencias públicas de DC; no reorganizar sin contratos. Los datos grandes de hero-asset se regeneran, no se editan como arrays manuales. Conservar bases y atribuciones que permiten reproducir recursos.

No hay benchmark en GPU física, cobertura universal de Safari/Firefox/file://, supervivencia al cierre del proceso del navegador, simulación completa de tejidos o manos, multijugador ni certificación fotorrealista. La recuperación síncrona puede producir una pausa. Las imágenes de tiempo preparado no prueban FPS. Consultar [handoff](HANDOFF.md), [QA](QA.md) y [benchmark](CHARACTER-BENCHMARK.md).

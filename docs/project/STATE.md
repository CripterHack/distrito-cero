# Estado real del proyecto

## Estado actual, 15 de septiembre de 2026

El gameplay sigue basado en v0.19 con endurecimiento posterior y correcciones de presentación. El usuario activó GitHub Pages desde master. No se modifica su configuración ni se asigna una licencia global.

| Capacidad / issue | Estado y alcance |
| :--- | :--- |
| #2 · Runner de QA | Cerrado por PR #8. Copia aislada, configuración explícita y rechazo de informes antiguos. |
| #3 · Guardados nativos | Cerrado por PR #9. 35 checks Chromium HTTP con perfil persistente, reapertura y dos páginas reales. |
| #4 · Recuperación WebGL | Cerrado por PR #10 (`a752e9e`). Reconstrucción del renderer sin reiniciar la sesión y reanudación explícita. |
| #5 · Personaje patrón | PR #11 (`072750b`) integró matriz, capturas, medidas y galería. Aprobación artística y resto de gates pendientes. |
| #6 · Contactos/recargas | Primera corrección de prenda: mangas y tronco dejan de compartir influencias incorrectas. Contactos de falanges, coordinación completa y resto de gates pendientes. |
| #7 · Vertical slice | Pendiente de implementación integral y validación de juego/hardware. |

El HTML con pesos corregidos y recuperación tiene **8,851,413 bytes**, SHA-256 `47cbc618241b3419e300d76480176f77287ca80ee449edf14c78d1af4f32e875`. El asset humano es `a4f5a6522f0012290bd2fca8d573ca5243388474f72fb026cf5766924e3c8b7d`. Las ramas sólo se publican en master después de su verificación: consultar el PR y Actions del commit exacto.

## Corrección localizada de presentación

La deformación de la chaqueta al apuntar procedía de pesos que vinculaban parte de las mangas al torso y del tronco a los brazos. La receta de autoría identifica superficies conectadas y conserva una transición gradual en el hombro. Sólo cambian pesos e IDs de influencia de la prenda y sus puños, no posiciones, UVs, normales, articulaciones o montaje de armas. La semilla de autoría preserva las influencias anteriores sin duplicar toda la geometría. Ver [GARMENT-BINDING.md](GARMENT-BINDING.md).

La corrección utiliza los mismos recursos compartidos para protagonista, peatones y conductores. Los niveles de detalle siguen el pipeline existente. No añade simulación física de tela, anatomía nueva ni un solver de dedos. Los GLB humanos previos siguen identificados como exportaciones históricas.

## Madurez y sistemas

**Prototipo integrado, no calidad AAA demostrada.** Se conservan personajes de 49 huesos/DQ/LOD/once peinados, creador, doce slots por ID, catálogo de equipo, conductores, acceso ocupado/vacío, objetos, daño, policía, campaña y regiones procedurales.

Persisten brechas de anatomía, prendas, materiales, pelo, dedos y expresiones; contactos y recargas siguen siendo aproximaciones. No existe combate armado autónomo de NPCs, mundo con terreno transitable avanzado ni una vertical slice nueva completa. La matriz detecta fallos que un recuento de tests no puede aprobar artísticamente.

## Evidencia y modalidades

La corrección de pesos añade tres regresiones Node de superficie y cinco Python de integridad/reconstrucción. El workflow de autoría reprodujo primero los tres fallos y verificó el asset resultante, todas las pruebas Node y el build. Las ejecuciones gráficas del PR tienen sus propios hashes y artefactos. No se deduce un pase de la mera existencia de las pruebas.

El benchmark tiene smoke de 30 capturas/36 checks; la cobertura full de 586 casos no se declara ejecutada sin su informe. Manejo y recuperación utilizan renderer WebGL real y almacenamiento fixture. El job nativo separado prueba HTTP y reapertura sin sustituir localStorage. Ninguno mide FPS de GPU física.

PR #10 run `34940253023` y PR #11 runs `34992345086` / `34992345168` son evidencia histórica de sus respectivos commits, no de todos los cambios posteriores. La aprobación artística permanece separada.

## Origen preservado

Importación original: `23f9e9d031c7a0ad270cd74ce0805ea0dfc385da`. ZIP: 80,607,113 bytes y SHA-256 `307c8fd0d3093eb7d16a3468470a2dfd20ffa12a654ecbe306f07f8aea8a1241`. Se importaron 730 archivos, con 729 hashes en SOURCE-MANIFEST, que permanece histórico.

El HTML original v0.19 tenía SHA-256 `3aa9a27f4941ea1c701069c61db133ab3c93087e35d833d4921ba25b8a4b059f`. El de recuperación previo a esta corrección era `3f1f5ac6a6d3aa7a74b8046a89f0a5f13b06d9982899131a8351a9909df67318`. No se reescribe el manifiesto original para ocultar cambios.

## Arquitectura y límites

El build concatena 38 JS en orden significativo. Las capas sustituyen referencias públicas de DC; no reorganizar sin contratos. Los datos grandes de hero-asset se regeneran, no se editan como arrays manuales. Conservar bases y atribuciones que permiten reconstruir recursos.

No hay benchmark físico, cobertura universal de Safari/Firefox/file://, supervivencia al cierre del proceso, simulación completa de tejidos o manos, multijugador ni certificación fotorrealista. La recuperación síncrona puede producir una pausa. Las imágenes de tiempo preparado no prueban FPS. Consultar [handoff](HANDOFF.md), [QA](QA.md) y [benchmark](CHARACTER-BENCHMARK.md).

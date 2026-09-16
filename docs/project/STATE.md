# Estado real del proyecto

## Estado actual, 15 de septiembre de 2026

El gameplay sigue basado en v0.19 con endurecimiento posterior y correcciones de presentación. El usuario activó GitHub Pages desde master. No se modifica su configuración ni se asigna una licencia global.

| Capacidad / issue | Estado y alcance |
| :--- | :--- |
| #2 · Runner de QA | Cerrado por PR #8. Copia aislada, configuración explícita y rechazo de informes antiguos. |
| #3 · Guardados nativos | Cerrado por PR #9. 35 checks Chromium HTTP con perfil persistente, reapertura y dos páginas reales. |
| #4 · Recuperación WebGL | Cerrado por PR #10 (`a752e9e`). Reconstrucción del renderer sin reiniciar la sesión y reanudación explícita. |
| #5 · Personaje patrón | PR #11 (`072750b`) integró matriz, capturas, medidas y galería. Aprobación artística y otros gates pendientes. |
| #6 · Contactos/recargas | PR #12 (`ac3cf5b`) corrigió pesos de mangas/tronco. La nueva unidad estabiliza codos y hombros en subida/bajada de binoculares. Falanges, alineación y otros gates pendientes. |
| #7 · Vertical slice | Pendiente de implementación integral y validación de juego/hardware. |

HTML con la corrección óptica: **8,851,747 bytes**, SHA-256 `fe47dfa3ef9b2bff6d415b6f6fb0b64e0d0b0c0df7193b135c59e4fc3fe7b93b`. El asset humano sigue siendo `a4f5a6522f0012290bd2fca8d573ca5243388474f72fb026cf5766924e3c8b7d`. Consultar el PR y Actions del commit exacto antes de atribuir una publicación o un pase a una rama.

## Presentación y contratos

La corrección anterior de chaqueta identificó superficies por conectividad y conservó una transición gradual del hombro. Sólo cambiaron los pesos de la prenda/puños, sin alterar posiciones, UVs, normales o huesos. Ver [GARMENT-BINDING.md](GARMENT-BINDING.md).

La nueva corrección no vuelve a tocar ese asset. Utiliza referencias propias de flexión del codo para los binoculares, evitando una inversión del plano durante la elevación. Su presentación alcanza aproximadamente el 95% de la pose en 0.5 segundos. Las armas de fuego conservan el ritmo anterior. No cambian anclas palmares, zoom, munición, tiempos de recarga o formato de partidas. Ver [OPTICAL-SHOULDERS.md](OPTICAL-SHOULDERS.md).

Se mantienen el montaje único, los recursos compartidos y los LOD existentes. No hay nueva física de tela, escaneo, rig ni solver de dedos. Los GLB humanos previos siguen siendo exportaciones históricas.

## Madurez

**Prototipo integrado, no calidad AAA demostrada.** Se conservan 49 huesos/DQ/LOD/once peinados, creador, doce slots por ID, catálogo de equipo, conductores, acceso ocupado/vacío, objetos, daño, policía, campaña y regiones procedurales.

Persisten brechas de anatomía, materiales, pelo, dedos y expresiones. No existe combate armado autónomo de NPCs, terreno transitable avanzado ni una vertical slice nueva completa. El benchmark detecta problemas que los tests de pivotes no aprueban artísticamente.

## Evidencia y modalidades

La unidad óptica añade ocho tests Node y 14 checks de navegador con 13 capturas. La suite Node local completa pasa 354 pruebas. Seis tests nuevos reproducen fallos con las fuentes anteriores. Una regresión muestrea 284 posiciones del hombro/axila durante subida y bajada, no sólo muñecas. La prueba remota usa el renderer y controlador actuales, tiempo preparado y almacenamiento fixture.

El benchmark tiene smoke de 30 capturas/36 checks; la matriz full de 586 casos no se declara ejecutada sin su informe. Manejo y recuperación también usan almacenamiento fixture. El job nativo separado prueba HTTP y reapertura sin sustituir localStorage. Ninguno mide FPS de GPU física.

Cada ejecución CI tiene sus propios hashes y artefactos. Los runs de PR #10 (`34940253023`), #11 (`34992345086` / `34992345168`) y #12 (`35002270205` / `35002270043`) son evidencia histórica de esos commits, no una aprobación de todos los cambios posteriores. La decisión artística permanece separada.

## Origen preservado

Importación: `23f9e9d031c7a0ad270cd74ce0805ea0dfc385da`. ZIP original: 80,607,113 bytes, SHA-256 `307c8fd0d3093eb7d16a3468470a2dfd20ffa12a654ecbe306f07f8aea8a1241`. Se importaron 730 archivos y 729 huellas en SOURCE-MANIFEST, que permanece histórico.

HTML original: `3aa9a27f4941ea1c701069c61db133ab3c93087e35d833d4921ba25b8a4b059f`. HTML con recuperación: `3f1f5ac6a6d3aa7a74b8046a89f0a5f13b06d9982899131a8351a9909df67318`. HTML PR #12: `47cbc618241b3419e300d76480176f77287ca80ee449edf14c78d1af4f32e875`. No reescribir el manifiesto inicial para ocultar cambios.

## Arquitectura y límites

El build concatena 38 JS en orden significativo. Las capas sustituyen referencias de DC; no reorganizar sin contratos. Los datos grandes de hero-asset se regeneran, no se editan como arrays manuales. Conservar bases y atribuciones para reconstrucción.

No hay benchmark físico, cobertura universal de Safari/Firefox/file://, supervivencia al cierre del proceso, simulación completa de tejidos o manos, multijugador ni certificación fotorrealista. La recuperación síncrona puede causar una pausa. Consultar [handoff](HANDOFF.md), [QA](QA.md) y [benchmark](CHARACTER-BENCHMARK.md).

## Contacto digital posterior a PR #13

Avance parcial de #6 mediante cuatro perfiles no pulgares compartidos, sin cambiar malla humana, anclas o formato de partida. Ver [FINGER-CONTACTS.md](FINGER-CONTACTS.md) para cobertura y resultados. Pulgar/oposición, contacto entre manos y ojo/mira siguen pendientes. Consultar el PR/CI del commit exacto, no cifras heredadas.

## Oposición del pulgar posterior a PR #15

Unidad parcial de #6: pivote virtual metacarpal y cuatro referencias de contacto, preservando rig, mallas, falanges no pulgares y reglas de juego. Once regresiones Node y suite gráfica de quince checks. Ver [THUMB-CONTACTS.md](THUMB-CONTACTS.md) para alcance, fallos reproducidos y limitaciones. La integración y sus runs deben comprobarse en GitHub, no inferirse del documento. #5/#6/#7 siguen abiertos.

## Correctivo de Actions y apoyo entre manos

El PR #17 está integrado como `e614ff9`. CI de master 35051259999, benchmark 35051260032 y Pages aprobaron, sin borrar el historial rojo. El siguiente avance parcial calibra la mano de apoyo de pistola/revólver contra la mano dominante, conservando las correcciones anteriores. Ver [SIDEARM-SUPPORT.md](SIDEARM-SUPPORT.md) para cobertura y límites. #5/#6/#7 siguen abiertos; consultar los checks del commit nuevo antes de considerarlo integrado.

## Correctivo de superficie de palma/pulgar, posterior a PR #18

Sobre `ef905ec`, se implementa una reducción volar acotada de hasta 4 mm en las almohadillas de ambas manos. Sólo cambia el recurso humano canónico y su HTML generado; el controlador y los contactos de armas se mantienen. Se amplía la QA a una cohorte geométrica fija sin filtro de influencia, evitando omitir la zona mixta. Ver [THENAR-SURFACE.md](THENAR-SURFACE.md). Los estados y resultados CI efectivos se comprueban en el PR/commit, y la aceptación artística general sigue pendiente.

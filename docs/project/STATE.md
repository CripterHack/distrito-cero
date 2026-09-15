# Estado real del proyecto

## Estado actual, 15 de septiembre de 2026

El juego sigue basado en v0.19 con correcciones posteriores de fiabilidad y presentación. GitHub Pages publica desde master por configuración del usuario. No se modifica esa configuración ni se asigna una licencia global.

| Capacidad / issue | Estado y alcance |
| :--- | :--- |
| #2 · Runner de QA | Cerrado por PR #8: ejecución aislada y rechazo de informes antiguos. |
| #3 · Guardados nativos | Cerrado por PR #9: 35 checks HTTP con perfil persistente, reapertura y dos páginas reales. |
| #4 · Recuperación WebGL | Cerrado por PR #10: renderer reconstruido sin reiniciar sesión y reanudación explícita. |
| #5 · Personaje patrón | Benchmark integrado por PR #11; revisión artística y otros criterios pendientes. |
| #6 · Contactos/recargas | PR #12 corrigió pesos de mangas/tronco. La unidad óptica estabiliza codos y su transición. Falanges, coordinación completa y criterios restantes pendientes. |
| #7 · Vertical slice | Pendiente de implementación integral y validación de juego/hardware. |

HTML con postura óptica corregida: **8,851,747 bytes**, SHA-256 `fe47dfa3ef9b2bff6d415b6f6fb0b64e0d0b0c0df7193b135c59e4fc3fe7b93b`. Asset humano conservado desde la corrección de mangas: `a4f5a6522f0012290bd2fca8d573ca5243388474f72fb026cf5766924e3c8b7d`. Sólo los cambios verificados de una rama se integran en master; consultar el PR y Actions del commit exacto.

## Presentación actual

Los pesos de chaqueta y puños se reconstruyen por conectividad y transición gradual, sin deformar el tronco con las referencias del brazo. Ver [GARMENT-BINDING.md](GARMENT-BINDING.md).

Los binoculares tienen referencias propias de codo para evitar el cambio brusco del plano de flexión al llevarlos junto al rostro. Su elevación y bajada visual es más gradual, sin alterar la activación lógica de zoom ni los factores ópticos. Las armas de fuego conservan sus referencias y tiempos. Ver [OPTICAL-POSTURE.md](OPTICAL-POSTURE.md).

Esta unidad no modifica anatomía, mallas, esqueleto, mapas, pesos, geometría de equipo ni sus exportaciones. No añade física de tejidos/dedos o un segundo montaje de armas. Los NPCs no reciben una nueva IA de combate o equipamiento por esta corrección.

## Madurez y sistemas

**Prototipo integrado, no calidad AAA demostrada.** Conserva personajes de 49 huesos/DQ/LOD/once peinados, creador, doce espacios de guardado por ID, arsenal, conductores, acceso ocupado/vacío, objetos, daño, policía, campaña y regiones procedurales.

Siguen existiendo brechas de anatomía, materiales, cabello, dedos, expresiones y continuidad de algunas interacciones. No existe combate armado autónomo de NPCs, relieve transitable avanzado ni una nueva vertical slice completa. Las pruebas numéricas no sustituyen una aceptación artística.

## Evidencia y modalidades

La unidad óptica añade ocho tests Node; seis reproducían defectos/criterios incumplidos en la base y los ocho pasan después del cambio. La suite Node local completa suma 354 tests. Hay catorce checks ópticos de navegador, además de manejo (51), recuperación (22), personajes (36) y guardados nativos (35), que se ejecutan y reportan por separado. Los resultados vigentes se leen de la CI del hash específico, no se deducen de esta lista.

El benchmark smoke genera 30 capturas y su matriz full disponible tiene 586 casos, sin declararse ejecutada por estar definida. Óptica/manejo/recuperación usan renderer real y almacenamiento fixture; la suite nativa no sustituye localStorage. Las poses, cámaras y tiempo preparados no demuestran FPS de GPU física ni un recorrido completo de campaña.

## Origen e historial preservados

Importación original `23f9e9d031c7a0ad270cd74ce0805ea0dfc385da`: 730 archivos con 729 hashes en SOURCE-MANIFEST. Ese manifiesto y qa histórico no se reescriben.

HTML original v0.19: `3aa9a27f4941ea1c701069c61db133ab3c93087e35d833d4921ba25b8a4b059f`. Con recuperación: `3f1f5ac6a6d3aa7a74b8046a89f0a5f13b06d9982899131a8351a9909df67318`. Con mangas corregidas, base de esta unidad: `47cbc618241b3419e300d76480176f77287ca80ee449edf14c78d1af4f32e875`.

## Arquitectura y límites

El build concatena 38 JS en orden significativo. Las capas sustituyen referencias públicas de DC; no reorganizar sin contratos. Los datos de hero-asset se regeneran y sus bases/atribuciones se conservan.

No hay benchmark físico, cobertura universal Safari/Firefox/file://, supervivencia al cierre del proceso, simulación completa de tejidos o manos, multijugador ni certificación fotorrealista. La recuperación gráfica síncrona puede pausar el dibujo. Consultar [handoff](HANDOFF.md), [QA](QA.md) y [benchmark](CHARACTER-BENCHMARK.md).

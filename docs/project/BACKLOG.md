# Backlog priorizado

Los estados de esta tabla son de planificación. La importación/CI inicial no marca terminadas las mejoras del juego. Cada entrada se implementa como PR pequeño con su spec y evidencia.

| ID | Prioridad | Estado | Capacidad / salida | Dependencia |
| :--- | :--- | :--- | :--- | :--- |
| DC-001 | P0 | ready | Harness portable y artefactos por run sin depender del historial temporal | M0 |
| DC-002 | P0 | ready | Guardado nativo HTTP, cierre/reapertura y dos partidas reales | DC-001 |
| DC-003 | P0 | proposed | Conflicto de dos pestañas, cuotas y recuperación de catálogo | DC-002 |
| DC-004 | P0 | proposed | Lifecycle de pérdida y restauración de WebGL | DC-001 |
| DC-005 | P1 | ready | Escena fija de anatomía y aprobación de referencia corporal | M0 |
| DC-006 | P1 | proposed | Receta editable de personaje, topología/UV y correctivos de cuello/hombro | DC-005 |
| DC-007 | P1 | proposed | Materiales de manos/ojos/piel y costuras compartidas | DC-006 |
| DC-008 | P1 | proposed | Peinados con silueta, LOD y overdraw medidos | DC-005 |
| DC-009 | P1 | proposed | Contactos de falanges y transición de índice para equipo | DC-006 |
| DC-010 | P1 | proposed | Recarga y cancelación por familia sin saltos de montaje | DC-009 |
| DC-011 | P1 | proposed | Arranque, frenado, giro en sitio y transición al asiento | DC-006 |
| DC-012 | P1 | proposed | Calle patrón y coherencia de materiales/exposición/sombras | DC-005 |
| DC-013 | P1 | proposed | Streaming por trabajos acotados y memoria medida | DC-001 |
| DC-014 | P1 | proposed | Superficie unificada de terreno, vías, pies y colisiones | DC-013 |
| DC-015 | P1 | proposed | Tráfico/peatones con recuperación de bloqueos y cruces | DC-014 |
| DC-016 | P1 | proposed | Percepción policial y oportunidades de escape reproducibles | DC-015 |
| DC-017 | P1 | proposed | Daño/destrucción coherente con sonido, proxy y persistencia | DC-014 |
| DC-018 | P1 | proposed | Vertical slice narrativa de 10–15 minutos sin saltar objetivos | DC-010–017 |
| DC-019 | P1 | proposed | Audio situacional, mezcla, pasos y señales accesibles | DC-012 |
| DC-020 | P1 | proposed | Remapeo, gamepad y auditoría móvil/teclado | DC-001 |
| DC-021 | P1 | blocked | Benchmark en GPU/dispositivos reales con perfiles aprobados | Selección y disponibilidad de hardware |
| DC-022 | P2 | blocked | Licencia global y política de contribuciones/distribución | Decisión del titular |
| DC-023 | P2 | proposed | Beta, migraciones, sesiones largas y rollback de release | Gates M1–M8 |

## Qué no priorizar todavía

Multijugador, más armas, nuevos biomas masivos, simulación física completa de pelo/tela y destrucción total de edificios. Pueden investigarse en ramas de prueba, pero no deben desplazar pérdida de datos, contactos visibles, rendimiento y la muestra jugable de calidad.

## Criterio de selección del siguiente PR

Elegir un resultado verificable que elimine el mayor riesgo actual. No mezclar anatomía, economía y migración de almacenamiento en un mismo PR. Las tareas `ready` habilitan su preparación; una dependencia aún no satisfecha bloquea su implementación final.

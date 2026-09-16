# Backlog priorizado

Estado actualizado tras los PRs #8, #9 y #10. Los resultados históricos no se suman como nuevas ejecuciones. Cada capacidad tiene una salida comprobable y las aprobaciones artísticas permanecen separadas.

| ID | Prioridad | Estado | Capacidad / salida | Dependencia |
| :--- | :--- | :--- | :--- | :--- |
| DC-001 | P0 | accepted | Harness portable, evidencia fresca; PR #8. Corrección adicional del staging en PR #11 | M0 |
| DC-002 | P0 | accepted | Guardado HTTP y reapertura nativa; PR #9 | DC-001 |
| DC-003 | P0 | accepted en alcance #3 | Conflicto entre páginas nativas y recuperación por copia/recarga; cuotas/corrupción conservan sus fixtures | DC-002 |
| DC-004 | P0 | accepted en alcance #4 | Recuperación WebGL con reanudación explícita; PR #10 | DC-001 |
| DC-005 | P1 | in-progress | Benchmark implementado; revisión artística y gates restantes pendientes | M0 |
| DC-006 | P1 | proposed | Receta editable y correctivos de anatomía/topología/UV | DC-005 |
| DC-007 | P1 | proposed | Materiales de manos/ojos/piel y costuras | DC-006 |
| DC-008 | P1 | proposed | Peinados, silueta, LOD y overdraw medidos | DC-005 |
| DC-009 | P1 | proposed | Contactos de falanges e índice, sin deformación de ropa ignorada | DC-006 |
| DC-010 | P1 | proposed | Recarga/cancelación por familia sin saltos | DC-009 |
| DC-011 | P1 | proposed | Arranque, frenado, giro en sitio y asiento | DC-006 |
| DC-012 | P1 | proposed | Calle patrón y coherencia de materiales/luz | DC-005 |
| DC-013 | P1 | proposed | Streaming por trabajos acotados y memoria | DC-001 |
| DC-014 | P1 | proposed | Superficie común de terreno, vías, pies y colisiones | DC-013 |
| DC-015 | P1 | proposed | Tráfico/peatones, cruces y recuperación de bloqueos | DC-014 |
| DC-016 | P1 | proposed | Percepción policial y escape reproducible | DC-015 |
| DC-017 | P1 | proposed | Destrucción, sonido, proxy y persistencia | DC-014 |
| DC-018 | P1 | proposed | Vertical slice de 10–15 minutos sin saltar objetivos | DC-010–017 |
| DC-019 | P1 | proposed | Audio situacional y señales accesibles | DC-012 |
| DC-020 | P1 | proposed | Remapeo, gamepad y auditoría táctil/teclado | DC-001 |
| DC-021 | P1 | blocked | Benchmark de rendimiento en GPU/dispositivos físicos | Hardware identificado disponible |
| DC-022 | P2 | blocked | Licencia global y política de contribuciones | Decisión del titular |
| DC-023 | P2 | proposed | Beta, migraciones, sesiones largas y rollback | Gates M1–M8 |

## Interpretación de los cierres

#2, #3 y #4 están cerrados para sus criterios verificados. No certifican todos los navegadores, cuotas de todo dispositivo o supervivencia al cierre del proceso. #5, #6 y #7 siguen abiertos. La primera unidad de #5 produce una referencia; no sustituye las mejoras visuales ni una aceptación artística.

## Siguiente defecto acotado

Reproducir `neutral--aim--neutral--front` del benchmark: deformación amplia de chaqueta bajo el brazo de apoyo, aunque el contacto de muñeca pase. Evaluar la superficie y pesos antes de cambiar anclas. El test matemático de contacto no debe esconder el problema visual.

## Prioridad

Primero pérdida de datos/crashes, luego acciones bloqueadas y defectos visibles repetidos, después coste y variedad. No introducir más armas, biomas masivos, multijugador o física completa de pelo/tela antes de esos gates. No mezclar una migración de guardados con remodelado en el mismo PR.

## Avance parcial DC-009/DC-010

Cuatro perfiles no pulgares y apertura visual de recarga documentados en [FINGER-CONTACTS.md](FINGER-CONTACTS.md). No cierra #6. Próxima regresión: oposición/base del pulgar, preservando las correcciones de falanges, mangas y codos.

Avance de DC-009: oposición del pulgar integrada en la unidad descrita en [THUMB-CONTACTS](THUMB-CONTACTS.md), con cobertura limitada a referencias de empuñadura, apoyo delantero y pieza extraíble. No implica cierre de DC-009/010: mano-mano, zonas mixtas, ojo/mira y fases por familia siguen pendientes. Consultar PR/CI para estado efectivo de integración.

Actualización posterior a PR #17: la CI de master y Pages aprobaron la corrección de generaciones WebGL liberadas. DC-009/010 incorpora una unidad parcial de apoyo entre manos en armas cortas, con regresiones de contacto, disparo y recarga. Las zonas mixtas y coordinación ojo/mira siguen pendientes. No cerrar #6 ni adelantar la vertical slice por este cambio.

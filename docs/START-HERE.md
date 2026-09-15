# Inicio y navegación documental

## Para jugar

Construir o abrir `index.html`. Leer [controles de v0.19](v019/GUIA.md). Exportar partidas antes de cambiar de origen o versión.

## Para continuar el desarrollo

Leer en este orden: [estado](project/STATE.md), [handoff](project/HANDOFF.md), [constitución](../.specify/memory/constitution.md), [método](spec-game-development.md), [roadmap](project/ROADMAP.md) y la especificación seleccionada.

## Documentos rectores

| Documento | Pregunta que resuelve |
| :--- | :--- |
| [STATE](project/STATE.md) | Qué existe y qué no está demostrado |
| [ARCHITECTURE](project/ARCHITECTURE.md) | Dónde vive cada responsabilidad y qué contratos conservar |
| [ASSETS](project/ASSETS.md) | Qué recurso es canónico, derivado o histórico |
| [QUALITY](project/QUALITY.md) | Cómo evaluar realismo, animación, coste y experiencia |
| [QA](project/QA.md) | Qué ejecutar y cómo interpretar la evidencia |
| [ROADMAP](project/ROADMAP.md) | Orden de desarrollo, dependencias y puertas de calidad |
| [BACKLOG](project/BACKLOG.md) | Trabajo priorizado con salida comprobable |
| [RISKS](project/RISKS.md) | Riesgos, decisiones y acciones manuales |
| [HANDOFF](project/HANDOFF.md) | Primera tarea a retomar sin reconstruir contexto |
| [LICENSING](project/LICENSING.md) | Procedencia y decisión de licencia aún no tomada |

`specs/` contiene las especificaciones de evolución, no descripciones retrospectivas. `docs/v019/` explica la última entrega del juego. Las versiones anteriores permanecen para trazabilidad.

## Qué no hacer

No empezar por reescribir el motor, añadir más mapas o cambiar el cuello a ojo en cada iteración. Primero fijar un benchmark repetible y una referencia anatómica aprobada, comprobar la cadena asset/rig/material/cámara y medir el coste. No repetir como actuales las cifras de pruebas de una entrega anterior.

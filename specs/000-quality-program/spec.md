# SPEC-000 · Programa de calidad integral

Estado: **ready para planificación**, no implementación completa. Base de producto: v0.19. Titular: CripterHack. Método: `docs/spec-game-development.md`.

## Intención

Como jugador quiero que la exploración, conducción, personajes e interacciones formen una experiencia consistente, creíble y estable. Como desarrollador quiero continuar el mismo proyecto sin rehacer sistemas ni perder evidencia o partidas.

## Alcance

Fiabilidad, benchmark artístico, anatomía/materiales, animación/contactos, mundo/vehículos/NPCs, experiencia narrativa, audio, accesibilidad y rendimiento. La entrega objetivo es una vertical slice pequeña y completa que sirva de referencia para el mundo ampliado.

## No objetivos

Cambiar de motor sin aprobación, implantar dependencias externas de runtime, multijugador, producir infinitos assets únicos, emular física clínica o armamento real, garantizar FPS sin hardware o declarar un juego AAA por el número de pruebas.

## Requisitos trazables

| Requisito | Resultado observable | Spec / trabajo | Evidencia exigida |
| :--- | :--- | :--- | :--- |
| QG-001 | Un clon limpio construye el mismo HTML de su commit | M0 / DC-001 | Hash, build y CI |
| QG-002 | Dos partidas nombradas sobreviven una reapertura real | SPEC-001 | Browser con origen/almacenamiento nativos |
| QG-003 | Una pérdida gráfica no destruye datos ni dispara acciones | SPEC-001 | Evento controlado y recuperación |
| QG-004 | Proporciones y deformación aceptadas para todo el rango del creador | SPEC-002 | Matriz anatómica y revisión registrada |
| QG-005 | Equipo y manos mantienen continuidad en uso y cancelación | SPEC-003 | Trayectorias, contactos y vídeo |
| QG-006 | Generación y colisión comparten superficie y vecindades | DC-013/014 | Determinismo y recorrido continuo |
| QG-007 | NPCs/vehículos se recuperan de bloqueos y la policía es legible | DC-015/016 | Escenarios reproducibles y playtest |
| QG-008 | Existe un encargo completo con ritmo y resolución | SPEC-004 | Partida íntegra sin mover al jugador por script |
| QG-009 | Rendimiento cumple el perfil aprobado | DC-021 | Hardware, frame times y memoria |
| QG-010 | UI y controles funcionan sin entradas accidentales | DC-020 | Teclado/táctil/remapeo y foco |
| QG-011 | Cada asset distribuido tiene procedencia verificable | ASSETS / DC-022 | Manifiesto y permisos |
| QG-012 | Todo cambio aceptado permite continuación y reversión | AGENTS / PR | Spec, tests, handoff y commit |

## Criterio de programa

Todos los gates aplicables deben tener evidencia ligada a un hash. Si una función aún no existe, marcarla como propuesta. Si el hardware no está disponible, no aprobar QG-009. El roadmap define dependencias, no fechas ficticias.

La publicación en GitHub satisface el traspaso de código y el arranque documental, no los requisitos posteriores de realismo. El marco se revisa cuando cambian alcance, recursos o restricciones, mediante ADR.

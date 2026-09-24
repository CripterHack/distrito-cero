# Estado real del proyecto

## Versión activa del árbol: v0.20.8 · Coherencia

Canal **prototype**, fecha 2026-09-23. Identidad exacta en
[version.json](../../version.json) y [build-info.json](../../build-info.json).
El PR de cada unidad y Actions acreditan integración/publicación, no este texto.

## Unidad actual: entrega visual entre familias

Base `be26fa05612e3318ad764ca09ddd5f8ef7f6ad3f`, PR #43 y su CI/despliegue
posteriores aprobados. 0.20.8 separa selección lógica inmediata de presentación
cosmética al cambiar rifle, SMG, escopeta y sniper. Mantiene el montaje existente
de gameplay y suaviza la entrega visual con alcance óseo sin escalar huesos.
La mano de apoyo se libera durante el arco exterior y regresa al agarre final.
Disparo y recarga interrumpen la curva cosmética para mostrar la acción real.

[EQUIPMENT-HANDOFF](EQUIPMENT-HANDOFF.md) registra causa, diseño, alternativas
rechazadas y cobertura. Se amplía QA con una suite de 16 checks de teclado/renderer,
sin sustituir las pruebas anteriores o relajar tolerancias. Los resultados finales
locales/remotos y los hashes se registran por separado en el PR y sus artefactos.
No se atribuye a GPU física el resultado de una escena preparada.

No cambian geometría, rig, longitudes, anclas originales, física, reglas de
munición ni esquemas de partidas. El estado de entrega es transitorio y no se
serializa. Los workflows normales sólo añaden la suite correspondiente, sin
cambios a controles de acceso, licencia o dependencias del juego.

## Backlog vigente

| Issue | Pendiente real |
| :--- | :--- |
| #5 · Personaje patrón | Aceptación artística/procedencia global y materiales/UV. Matriz y exportaciones ya existen. |
| #6 · Contactos y recargas | Integración de la entrega entre familias, cambios desde recarga/no dock, acciones/anatomías/locomoción y coste por actor/LOD. |
| #7 · Vertical slice | Escena/recorrido íntegro, playtests humanos y medición en equipo de referencia. |

No cerrar criterios globales por el éxito de una unidad acotada ni fabricar
participantes, hardware, FPS o aceptación artística.

## Historia integrada que no debe repetirse

#43 (be26fa0): preparación desde ready=0 de 0.20.7. #42 (c27282f): guardia y
recarga de 0.20.6. #40 (8695273): apoyo dinámico. #41 (02e3a14): limpieza y
continuidad. #30/#34–#39: rifle, benchmark, familias, exportación/raíces/tangentes
y marcha cerca del reposo. Las issues ya resueltas conservan su alcance original.

[Estado anterior completo](https://github.com/CripterHack/distrito-cero/blob/be26fa05612e3318ad764ca09ddd5f8ef7f6ad3f/docs/project/STATE.md)
conserva evidencia y límites. La [política de ramas](BRANCH-CLEANUP.md) exige master
como única rama permanente. Sólo trabajo activo en otras ramas y helpers fuera
del árbol y ascendencia del producto. No restaurar ramas antiguas para continuar.

Campaña, creador, catálogo, equipamiento, vehículos, policía, daños y regiones se
conservan. [Handoff](HANDOFF.md), [QA](QA.md), [recursos](ASSETS.md).

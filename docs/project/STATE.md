# Estado real del proyecto

## Versión activa del árbol: v0.20.6 · Coherencia

Canal **prototype**, fecha 2026-09-23. Identidad en [version.json](../../version.json)
y [build-info.json](../../build-info.json). La integración y publicación definitivas
se consultan en el PR de esta unidad y en Actions. No se deducen de esta página.

## Guardia y recarga: parche aplicado para revisión

Base `02e3a140baa8994a02fbcb5943b9a4c8258915df`, publicada como 0.20.5 y con Verify
35903012951 aprobado. La candidata 0.20.6 conserva la culata de rifle, SMG,
escopeta y sniper delante de la referencia de chaqueta cuando disminuye la
coordinación ocular. El arco exterior desaparece al alcanzar el apuntado estable.
Torso y equipo comparten la envolvente de preparación existente.

Las once regresiones del parche cubren guardia, recarga, inclinación, cuello,
agachado, pureza, transformaciones, contactos y transferencia real de munición.
Diez reprodujeron el defecto al repetir contra la fuente original en esta sesión.
Nueva repetición local: **554/554 Node**. Reconstrucción remota 35916388833:
554 Node y seis objetos exactos comprobados. La CI propia del PR es independiente.

El parche completo se aplicó desde el master exacto en un checkout de historial
real. [STOCK-TRANSITIONS](STOCK-TRANSITIONS.md) conserva implementación, evidencia
anterior y límites. HTML: `ff8db64a6c9f10549fb346320725efc97539813f6da83852bcbc279d7680b86f`,
8,870,022 bytes. Fuente: `08dc02e50fbdce141e2cbbc0d55c2b089b5d437c84c8f340383a4c3a2a54c493`.
Geometría humana/equipo, huesos, cámara, física, munición y formatos intactos.

La aceptación empieza con equipo preparado. El desenvainado inicial todavía
muestra penetración muestreada de hasta 23.70 mm; no se declara corregido.
Las pruebas de superficie no son colisión de toda la malla ni hardware físico.

## Backlog vigente

| Issue | Pendiente real |
| :--- | :--- |
| #5 · Personaje patrón | Revisión artística/procedencia global, materiales y UV degeneradas. La matriz técnica y las exportaciones ya existen. |
| #6 · Contactos y recargas | Integración del parche de guardia/recarga, después desenvainado inicial, revisión amplia de acciones/anatomías y coste por actor/LOD. |
| #7 · Vertical slice | Escena, recorrido íntegro sin teletransportes, playtests humanos y equipo de referencia. |

No cerrar un issue global por la aprobación de una unidad acotada ni inventar
participantes, FPS físicos o aprobación artística.

## Integraciones previas y contexto

PR #40 (`8695273`) conserva continuidad del apoyo dinámico en 0.20.5. PR #41
(`02e3a14`) consolidó el handoff y retiró ramas obsoletas con respaldo verificable.
PRs #30/#34–#39 ya están integrados: rifle, benchmark, familias, exportación
portable, raíces, tangentes y marcha cerca de reposo no se vuelven a implementar.
[Registro anterior completo](https://github.com/CripterHack/distrito-cero/blob/02e3a140baa8994a02fbcb5943b9a4c8258915df/docs/project/STATE.md)
conserva SHAs, errores históricos, resultados y alcance de cada unidad.

[BRANCH-CLEANUP](BRANCH-CLEANUP.md) conserva inventario y recuperación. Master es
la única rama permanente; las ramas actuales son temporales de esta unidad.
No se integran herramientas auxiliares, se cambian permisos normales o licencia,
ni se reescriben galerías/manifiestos históricos.

Campaña, creador, once peinados, doce partidas, equipamiento, selector translúcido,
vehículos/ocupantes, policía, daños y regiones se conservan. No se incorporan
servicios remotos. [Handoff](HANDOFF.md), [QA](QA.md), [recursos](ASSETS.md).

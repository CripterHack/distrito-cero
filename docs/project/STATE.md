# Estado real del proyecto

## Base integrada: v0.20.21 · Coherencia · prototype

[PR #60](https://github.com/CripterHack/distrito-cero/pull/60), master
**39b7647f1c763ab9e35e8c507723fc4cf5cfc57f**, árbol
**1820cda051434f5596c20c2b3c5fa9de2afc7661**. Pistola/escopeta libre y desde
recarga está resuelto en el alcance del PR. Su push Verify 36663085382,
benchmark 36663085782, exportación 36663085359 y Pages 36663084925 están
comprobados. No repetir temporizadores #58 ni shader estático #59.

## Unidad del árbol: candidata v0.20.22

[Plan](../../specs/003-weapon-contact/plan-shotgun-revolver-handoff.md).
Escopeta ↔ revólver usa la captura y retorno existentes, libre y desde recarga,
con selector congelado, caché canónica y reselección. Acciones lógicas inmediatas,
partidas, munición, rig de 49 huesos, geometría y renderer se conservan.

Regresión dirigida: cuatro fallos y una salvaguarda ya aprobada sobre la base,
después cinco aprobadas. QA: tres fallos sobre 22 tests, después 22/22. La suite
completa y el renderer/CI son comprobaciones separadas que no se anticipan aquí.
Sight mantiene las 130 comprobaciones anteriores y añade dieciocho: **148**,
**28 intercambios**, 61 estados más before, 820×680 y cinco guardas por partición.
Base conserva su coste/catálogo. Las nuevas rutas se distribuyen en las otras dos
particiones. Tres productores, 1800 s/productor, 40 minutos/job, sin nuevos runners.
[HANDOFF](HANDOFF.md), [QA](QA.md), [issue #6](https://github.com/CripterHack/distrito-cero/issues/6).

## Ramas y recuperación

La autorización renovada permitió retirar las **16 ramas antiguas** y el auxiliar
creado para auditarlas. Sólo master quedó en remoto antes de abrir esta nueva
unidad. El historial completo se respaldó, clonó y validó con fsck antes de las
bajas atómicas por SHA exacto. [Registro](BRANCH-CLEANUP.md). Las fuentes locales
actuales tienen historia Git real recuperada del bundle, no padres sintéticos.

## Backlog global

| Issue | Pendiente real |
| :--- | :--- |
| #5 | Aceptación artística, fuentes/procedencia, materiales/UV y hardware |
| #6 | Integración de esta unidad, otras parejas/herramientas, giros, cortes y coste por actor/LOD |
| #7 | Recorrido íntegro, playtests humanos y hardware de referencia |

No cerrar estos requisitos globales por contar pruebas. No inventar aceptación
artística, participantes, GPU física o FPS. Los assets y manifiestos históricos
conservan sus versiones. La CI e integración final se registran en el PR de #6,
no se deducen de estas notas de implementación anteriores a la CI.

## Comprobación local de esta candidata

667/667 Node completos, 148/148 Python vigentes, autoría/build/export e invariancia
aprobados. 96 documentos sin enlaces locales rotos. El primer pase Python detectó
dos fixtures de conteos antiguos, que se corrigieron antes de repetir las quince
suites. El renderer y la CI siguen siendo gates separados.

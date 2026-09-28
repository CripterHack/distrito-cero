# Estado real del proyecto

## Árbol de trabajo: v0.20.15 · Coherencia · prototype

Identidad en [version.json](../../version.json) y [build-info.json](../../build-info.json).
Base integrada: #51, `17f6086d4ec60c764cd58be62493ae12bd0e2c68`, producto 0.20.14,
árbol `f82ac7205839239aa6826dfb26429e05cd3b543f`. Su Verify posterior
`36320055066` terminó con seis jobs aprobados. Las ramas concluidas se
retiraron en `36321562419`, con bundle recuperable. No repetir su caché.

## Unidad de producto actual: rifle ↔ revólver libre

Se extiende la captura/montaje existente a ambos sentidos libres, con 0.90 s
cosméticos. La selección y cancelación lógica no esperan a la animación.
Se conserva la pose realmente mostrada, incluyendo cuerpo y dedos, un único
modelo y las acciones prioritarias. Se excluyen recarga activa, pose que todavía
devuelve una pieza y modelo mostrado ajeno a esta pareja. No se cambian rig,
geometría, munición, partidas, cámara ni caché canónica.
[Plan y registro](../../specs/003-weapon-contact/plan-rifle-revolver-free.md).

Baseline dirigida: 11 tests aprobados. Cinco pruebas extendidas fallaron antes
del cambio. La prueba de chaqueta rechazó el arco de 0.08 m a −4.068 mm;
el arco existente de 0.12 m pasa sin ampliar el criterio de −2 mm. Diez tests
dirigidos aprobados, 72 casos de selección y 228 poses de culata muestreadas.
Esto no acredita separación universal, CCD o toda la malla.

**Estado de este commit:** implementación/regresión dirigida verificadas;
renderer, suite completa y CI se registran en el PR del HEAD exacto. Consultar
su cierre para integración y push/Pages, no inferirlos de la identidad del árbol.

## Backlog vigente

| Issue | Pendiente real |
| :--- | :--- |
| #5 | Arte global, fuentes/procedencia, materiales/UV y coste sobre hardware. |
| #6 | Verificar esta unidad libre; recarga rifle/revólver y demás cruces, herramientas/pesados, cortes prioritarios, giros/anatomías y coste por actor/LOD. |
| #7 | Recorrido íntegro, playtests humanos y hardware de referencia. |

## Integraciones que no deben repetirse

#51 (`17f6086`): caché canónica independiente de la pieza transitoria, cuatro
perfiles, sin precalentamiento. #50 (`7231aa5`): productor sight particionado,
40 + 18 checks históricos y cinco guards compartidos. Esta unidad añade ocho
checks sin redistribuir otra vez la CI ni elevar sus límites.
#49 (`0fa83b9`): rifle ↔ pistola libre/recarga. Su timeout posterior a 1800 s
sigue siendo fallo histórico, corregido por #50. #48/#47: armas cortas desde
recarga/libres. #46: actor de marcha. #45/#44: recarga/intercambio largo.
#43/#42: preparación/guardia. #39/#40: marcha/apoyo. #30/#34–#38: coordinación,
benchmark, familias y exportación portable.

Campaña, creador, catálogo, vehículos y reglas permanecen intactos.
[HANDOFF](HANDOFF.md), [QA](QA.md), [recursos](ASSETS.md),
[política de ramas](BRANCH-CLEANUP.md). Revisión propia, no independiente.

# Estado real del proyecto

## Árbol de trabajo: v0.20.17 · Coherencia · prototype

Identidad en [version.json](../../version.json) y [build-info.json](../../build-info.json).
Base integrada #53: 6ba8b86c6e18b160588caf75ecdb24c7e64f078f, árbol
7b099a58a4aab912cbe70d55f07907e9205f9d6e. Verify posterior 36387391877 aprobó
siete jobs. Pages 36387391414 aprobó y su HTML fue cotejado. No repetir #53
ni rifle/revólver libre (#52), caché canónica (#51) o particiones (#50).

## Unidad de este árbol: SMG ↔ revólver libre

[Plan](../../specs/003-weapon-contact/plan-smg-revolver-free.md).
Reutiliza captura y montaje cosmético de 0.90 s, preservando la pose realmente
mostrada. Mantiene excluidas recargas, piezas retornando y terceros modelos
para esta pareja. Acciones lógicas inmediatas, sin alterar rig, geometría,
munición, gameplay, partidas o la caché de cuatro perfiles.

RED dirigido: siete fallos de 26 tests en base, más dos expectativas de QA.
La primera trayectoria de 0.08 m falló contra chaqueta a −4.068 mm. La variante
0.12 m se contrasta contra geometría SMG, conservando −2 mm y pasos palmares
preparados menores a 30 mm. No extrapolar este muestreo a toda la malla/CCD.

Sight conserva 76 checks y doce secuencias previas, agrega ocho y dos: 84,
40 base +26 cruces +18 en el grupo histórico revolver-reload. Sin nuevo job,
con 61 estados por caso y cinco guardas compartidas bloqueantes contadas una vez.
Se mantienen límites y permisos del producto. Cómputo total y FPS físicos son
cuestiones distintas de aprobar los checks.

**Validación/integración:** consultar el cierre del PR del HEAD exacto y
[issue #6](https://github.com/CripterHack/distrito-cero/issues/6). No atribuir CI
previa a este árbol. La copia local tiene historial sintético, aunque su base
se cotejó contra el árbol remoto completo. [HANDOFF](HANDOFF.md).

## Backlog vigente

| Issue | Pendiente real |
| :--- | :--- |
| #5 | Arte global, fuentes/procedencia, materiales/UV y coste en hardware. |
| #6 | Validar esta unidad libre; recarga SMG/revólver, otros cruces, herramientas/pesados, cortes prioritarios visuales y coste por actor/LOD. |
| #7 | Recorrido íntegro, playtests humanos y hardware de referencia. |

## Integraciones que no deben repetirse

#53: rifle/revólver desde recarga y tercer grupo gráfico.

#52: rifle/revólver libre. #51 (`17f6086`): caché canónica de cuatro perfiles,
sin precalentamiento. #50 (`7231aa5`): partición del productor sight.
#49 (`0fa83b9`): rifle/pistola libre/recarga. Su timeout posterior se conserva
como fallo histórico. #48/#47: armas cortas. #46: actor de marcha.
#45/#44: recarga/intercambio largo. #43/#42: preparación/guardia.
#39/#40: marcha/apoyo. #30/#34–#38: coordinación, benchmark y exportación.

La limpieza de las dos ramas concluidas de #52 fue bloqueada y no se ejecutó.
No reintentar esa operación mediante otra vía. Los helpers quedan fuera del
árbol y ascendencia del producto. Campaña, creador, catálogo y vehículos intactos.
[HANDOFF](HANDOFF.md), [QA](QA.md), [recursos](ASSETS.md), [política de ramas](BRANCH-CLEANUP.md).

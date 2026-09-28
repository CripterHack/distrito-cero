# Estado real del proyecto

## Árbol de trabajo: v0.20.16 · Coherencia · prototype

Identidad en [version.json](../../version.json) y [build-info.json](../../build-info.json).
Base integrada #52: `d25baffca0f22e60a001f8f7f6e81ac8877cb9eb`, árbol
`1fd4f64fc57536034b6bd565cdd2a2793091f219`, producto 0.20.15. Verify del PR
`36377938175` y push `36379800131` aprobaron seis jobs cada uno. Benchmark,
exportación y Pages también aprobaron. [Cierre de #52](https://github.com/CripterHack/distrito-cero/pull/52).
No repetir su intercambio libre ni la caché canónica integrada en #51.

## Unidad de este árbol: rifle ↔ revólver desde recarga

Se retira sólo la exclusión de recarga/pieza retornando de esta pareja en
captureSwitch. La captura visible existente conserva cuerpo, dedos y la pieza
anterior, y reutiliza su retorno cosmético de 0.90 s. Continúa excluido un
tercer modelo mostrado ajeno a la pareja. Selección, cancelación, disparo y
nueva recarga siguen inmediatos. No cambia rig, geometría, gameplay, caché,
munición, cámara ni partidas. [Plan](../../specs/003-weapon-contact/plan-rifle-revolver-reload.md).

La ampliación dirigida observa primero siete regresiones fallidas en la base
y después 20/20 pruebas aprobadas. El catálogo Node cubre 128 selecciones,
cuatro configuraciones y siete fases de recarga por pareja, más sus casos
libres. Incluye selector congelado, retorno/reselección, prioridad, restore y
caché fría/inicializada. Muestreo de 304 poses de culata, mínimo combinado
−0.353 mm frente al límite conservado −2 mm. No acredita toda la malla/CCD.

Sight mantiene los 66 checks anteriores y añade diez: 40 + 26 + 10,
doce intercambios de 61 estados. La nueva partición no duplica los anteriores.
Cinco guardas comunes bloqueantes en las tres particiones, contadas una vez.
Límites 1800 s/productor y 40 min/job conservados; presupuesto agregado mayor.
La corrección de código no equivale a menor coste GPU ni a FPS medidos.

**Validación:** los resultados completos de renderer, suite completa y CI,
la revisión propia y el merge se registran en el PR de este cambio y en
[issue #6](https://github.com/CripterHack/distrito-cero/issues/6). Consultar su
cierre antes de repetir una unidad o asumir que una candidata está integrada.
Push y Pages se comprueban separadamente. No atribuir evidencia de 0.20.15
al HTML de esta versión.

## Backlog vigente

| Issue | Pendiente real |
| :--- | :--- |
| #5 | Arte global, fuentes/procedencia, materiales/UV y coste en hardware. |
| #6 | Cierre de validación de esta unidad; cruces restantes, herramientas/pesados, cortes prioritarios visuales, giros/anatomías y coste por actor/LOD. |
| #7 | Recorrido íntegro, playtests humanos y hardware de referencia. |

## Integraciones que no deben repetirse

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

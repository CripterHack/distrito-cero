# Estado real del proyecto

## Árbol de trabajo: v0.20.18 · Coherencia · prototype

Identidad en [version.json](../../version.json) y [build-info.json](../../build-info.json).
Base integrada #54: **d50a60665638f43076b85739205d59c8ab2c1741**, árbol
a6375d6e8b589bc961a6565005101ec8b16cfc84, producto 0.20.17. Su Verify posterior
36395675734 aprobó siete jobs. Benchmark, exportación y Pages también aprobaron.
[Cierre de #54](https://github.com/CripterHack/distrito-cero/pull/54).
No repetir #54 libre, recarga rifle/revólver #53 o caché canónica #51.

## Unidad de este árbol: SMG ↔ revólver desde recarga

[Plan](../../specs/003-weapon-contact/plan-smg-revolver-reload.md).
Se elimina únicamente el rechazo de recarga lógica/visible en captureSwitch
para esta pareja. Mantiene excluido un tercer modelo mostrado. Reutiliza la
pose capturada, retorno cosmético de 0.90 s y arco de 0.12 m, sin alterar rig,
geometría, caché, gameplay, munición, física o partidas. Las acciones reales
siguen inmediatas. El revólver se observa sobre su cuerpo realmente dibujado.

Las regresiones amplían los bucles existentes a fases de extracción/retorno,
selector congelado tras cancelar inputs, reversión, tres selecciones lógicas,
actor en movimiento, prioridades y caché fría/inicializada. Se preservan los
criterios de paso palmar <30 mm, objetivos <12 mm y penetración muestreada <=2 mm.
No se presenta el muestreo como toda la malla, CCD o aprobación artística.

Sight mantiene 84 checks previos y añade diez: **94 = 40 +26 +28**, dieciséis
secuencias de 61 estados. Cinco guardas por partición, contadas una vez.
Sin nuevos jobs ni elevar 1800 s/productor o 40 min/job. Más cobertura no
significa menos cómputo ni mejores FPS. [QA](QA.md).

**Verificación e integración:** consultar el PR de este cambio vinculado en
[issue #6](https://github.com/CripterHack/distrito-cero/issues/6). El cierre
identifica el HEAD, informes, revisión propia y merge reales. PR, push y Pages
son comprobaciones separadas. La historia local restaurada es sintética,
pero los 948 archivos base reconstruyeron el árbol remoto exacto.

## Backlog vigente

| Issue | Pendiente real |
| :--- | :--- |
| #5 | Arte global, fuentes/procedencia, materiales/UV y coste en hardware. |
| #6 | Cierre de esta unidad, cruces restantes, herramientas/pesados, cortes prioritarios visuales, anatomías/giros y coste por actor/LOD. |
| #7 | Recorrido íntegro, playtests humanos y hardware de referencia. |

## Continuidad y límites operativos

#54: SMG/revólver libre. #53: rifle/revólver desde recarga. #52: cambio libre
rifle/revólver. #51: caché canónica de cuatro perfiles, sin precalentar QA.
#50: distribución de sight. #49: rifle/pistola libre/recarga. El timeout
histórico posterior a #49 sigue registrado, no se reetiqueta como aprobación.
Las demás integraciones y sus límites permanecen en los PRs del issue #6.

No se reintenta la limpieza bloqueada ni se eliminan ramas. Los helpers no
pertenecen al árbol ni a la ascendencia del producto, ni son features pendientes.
Campaña, creador, catálogo y vehículos intactos. [HANDOFF](HANDOFF.md),
[recursos](ASSETS.md), [política de ramas](BRANCH-CLEANUP.md).

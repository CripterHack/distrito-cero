# Estado real del proyecto

## Base integrada: 0.20.20 · Coherencia · prototype

[PR #59](https://github.com/CripterHack/distrito-cero/pull/59), commit
**bb2412283e55d77d92dadc703d62ea89c69709c2**, árbol
**ffc69b9b88c7b76d10ea335ad3454a0808c7e62a**. Variante conservadora de shader para
materiales estáticos integrada. Verify posterior 36656252962 aprobó siete jobs.
No repetir #58 instrumentación, #59 implementación ni #57 pistola/SMG.

## Unidad del árbol: candidata v0.20.21

Identidad en [version.json](../../version.json) y [build-info.json](../../build-info.json).
Pistola ↔ escopeta conserva pose/pieza en cambio libre y al cancelar recarga,
selector congelado y reselección. Acciones, munición, partidas, geometría, rig
y shader anteriores intactos. No incorpora otro solver, tracker o reloj.
[Plan](../../specs/003-weapon-contact/plan-pistol-shotgun-handoff.md).

TDD dirigido: siete fallos en 27 tests sobre base, después 34/34 con sidearm.
QA de selección: tres fallos, después 21/21. Esas pruebas no sustituyen la suite
completa, el renderer o la CI del HEAD. La corrida completa Node posterior aprobó
658/658, sin skips ni cancelaciones. [HANDOFF](HANDOFF.md), [QA](QA.md).

Catálogo sight: 130 checks, 24 intercambios, 61 estados más before y todas las
capturas 820×680. Conservar veinte casos previos y cinco guardas por partición.
Tres productores, 1800 s/productor y 40 minutos/job sin cambios de workflow.
El estado de CI, revisión e integración de esta unidad está en su PR vinculado
desde [#6](https://github.com/CripterHack/distrito-cero/issues/6). No presentar
la candidata como integrada por estas notas anteriores a CI.

## Backlog global

| Issue | Pendiente real |
| :--- | :--- |
| #5 | Aceptación artística, fuentes/procedencia, materiales/UV y hardware |
| #6 | Cierre pistola/escopeta, otras parejas, herramientas/pesados, giros, cortes y coste por actor/LOD |
| #7 | Recorrido íntegro, playtests humanos y hardware de referencia |

No se reintenta limpieza bloqueada ni se borran ramas. Helpers fuera del producto
y su ascendencia. Restauración local con historia sintética, no historial remoto.
No afirmar GPU física, FPS, revisión independiente o aceptación artística global.
Los tests y exportaciones históricos conservan sus propias versiones y límites.

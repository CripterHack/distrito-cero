# Estado real del proyecto

## Árbol candidato: v0.20.20 · Coherencia · prototype

Identidad en [version.json](../../version.json) y [build-info.json](../../build-info.json).
Base integrada [#58](https://github.com/CripterHack/distrito-cero/pull/58):
**f65a9e6218e2c3b6b3bf3a2d55671c6591512627**, árbol
**99f6edda835f838c921faece5754aecd2c240aaa**, producto 0.20.19.
Instrumentación y push de #58 ya verificados. No volver a tratarlos como ausentes.

## Unidad de capacidad

El shader de fragmentos general comparte caminos costosos de piel/cabello con la
ciudad. Una variante para lotes estáticos con IDs comprobados 0–25 elimina sólo
comparaciones de materiales 30–49 imposibles en esos lotes. El shader original
permanece para datos mixtos, desconocidos, dinámicos y deformados. No modifica
geometría, iluminación, sombras, partidas, rig ni acciones de juego.

Prueba de clasificación al subir datos, uniforms por programa, reflexión, orden
transparente y liberación de recursos cubiertos por regresiones. TDD dirigido:
13/13 nuevas y 9/9 lifecycle. Las sondas y las suites completas se registran por
separado en el PR vinculado desde [#6](https://github.com/CripterHack/distrito-cero/issues/6).
No anticipar merge, CI aprobada o capacidad estable desde esta nota de implementación.
[Plan](../../specs/001-reliability/plan-static-material-program.md),
[HANDOFF](HANDOFF.md), [capacidad](SIGHT-CAPACITY.md), [QA](QA.md).

Sight mantiene 112 checks, veinte secuencias, 61 estados más before y todas las
capturas 820×680. Cinco guardas canónicas por partición. Presupuesto ordinario
inalterado: tres productores con 1800 s y jobs de 40 minutos. Cualquier coste de
transporte de fuentes se documenta por separado y no cuenta como ahorro de QA.

## Backlog global

| Issue | Pendiente real |
| :--- | :--- |
| #5 | Arte global, fuentes/procedencia, materiales/UV y hardware |
| #6 | Verificar capacidad, otras parejas, herramientas/pesados, anatomías/giros, cortes y coste por actor/LOD |
| #7 | Recorrido íntegro, playtests humanos y hardware de referencia |

No repetir #58 temporizadores, #57 pistola/SMG, #56 verificador, #55/#54
SMG/revólver, #53/#52 rifle/revólver, #51 caché ni #50 particiones.
No reetiquetar el timeout histórico 36304175245 como aprobado.

No se reintenta limpieza bloqueada ni se borran ramas. Helpers fuera del producto
y de su ascendencia. Restauración local con historia sintética, no historial remoto.
No afirmar GPU física, FPS, revisión independiente o aceptación artística global.

# Estado real del proyecto

## Producto integrado: v0.20.19 · Coherencia · prototype

Identidad en [version.json](../../version.json) y [build-info.json](../../build-info.json).
[PR #57](https://github.com/CripterHack/distrito-cero/pull/57) integrado en
**5f222410ec48473c371c3e4a84052667d354cc7e**, árbol
**d168a059695c62be7b96da4ab6fcecd1eb2d3bc7**. Pistola ↔ SMG libre y desde recarga,
selector congelado y pieza retornando ya están resueltos dentro del alcance medido.

Verify del push 36480927360, benchmark 36480927408, exportación 36480927618 y
Pages 36480926757 aprobados y artefactos contrastados en el cierre de #57.
323 WebGL, 80 HTTP y 36 benchmark. 112 checks sight, veinte secuencias de 61 estados.
No queda pendiente ese push. Exportación original con una advertencia conocida,
derivada sin errores/advertencias; no es aprobación artística. Pages verificado
por artefacto/despliegue, no por HTTP público.

## Unidad actual de QA: diagnóstico de capacidad

Se instrumenta el productor sight existente sin cambiar juego, versión, workflows,
permisos, particiones, cobertura, imágenes ni límites. Temporizadores locales
transparentes registran host y navegador por sección/operación. Sus valores no
autorizan aceptación y no representan GPU física o FPS. [Plan](../../specs/001-reliability/plan-sight-capacity.md).

Base de #57 dejó sólo 33.773 s frente al límite de 1800 s. Medir antes de ampliar,
optimizar o redistribuir. No se declara una mejora de velocidad sin medirla.
La CI y el estado real de integración de esta unidad se consultan en
[issue #6](https://github.com/CripterHack/distrito-cero/issues/6) y su PR, separados
de los resultados del producto anterior. [HANDOFF](HANDOFF.md), [QA](QA.md), [capacidad](SIGHT-CAPACITY.md).

## Backlog

| Issue | Pendiente real |
| :--- | :--- |
| #5 | Arte global, fuentes/procedencia, materiales/UV y hardware |
| #6 | Capacidad QA medida, otras parejas, herramientas/pesados, cortes prioritarios, anatomías/giros y coste por actor/LOD |
| #7 | Recorrido íntegro, playtests humanos y hardware de referencia |

## Continuidad

No repetir #57 pistola/SMG, #56 verificador, #55/#54 SMG/revólver, #53/#52
rifle/revólver, #51 caché, #50 particiones ni #49 rifle/pistola. Cada PR conserva
su evidencia propia. No reetiquetar el timeout histórico 36304175245.

No se reintenta limpieza bloqueada ni se borran ramas. Helpers fuera del
producto. Los snapshots locales tienen historia sintética; los commits publicados
requieren padres remotos reales y cotejo de árboles. No declarar revisión
independiente, GPU física, toda la malla/CCD o aceptación artística global.

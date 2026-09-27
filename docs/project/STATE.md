# Estado real del proyecto

## Árbol de trabajo: v0.20.14 · Coherencia · prototype

Identidad en [version.json](../../version.json) y [build-info.json](../../build-info.json).
La última base integrada es #50 (`7231aa5`, producto 0.20.13). La corrección
de caché descrita aquí es candidata hasta el cierre verificado de su propio PR.
No confundir un manifiesto del árbol con una publicación ya aprobada.

## Unidad actual: independencia del orden en los dedos

La caché podía memorizar el perfil de la nueva arma contra el cargador anterior.
Se separa el punto canónico de ajuste de `magazine.surface`, que conserva el
objeto mostrado durante el handoff. Sin cambiar solver, huesos, geometría,
munición, partidas o acciones prioritarias. Caché limitada a cuatro perfiles.
[Plan](../../specs/003-weapon-contact/plan-finger-cache-order.md).

Cuatro regresiones de procesos independientes comparan caché fría/inicializada,
ambas direcciones, libre/recarga y dos configuraciones. Las cuatro fallaron
antes del cambio y el primer ensayo corregido pasó. El resultado completo de
la candidata, renderer y CI debe consultarse en su PR, no inferirse de esta nota.

## Backlog vigente

| Issue | Pendiente real |
| :--- | :--- |
| #5 | Arte global, fuentes/procedencia, materiales/UV y coste sobre hardware. Benchmark y exportaciones existen. |
| #6 | Verificar e integrar caché canónica; otros cruces, herramientas/pesados, cortes prioritarios, giros/anatomías y coste por actor/LOD. |
| #7 | Recorrido íntegro, playtests humanos y hardware de referencia. |

Rifle → revólver libre está reproducido con tecla real, no implementado. Las
superficies observadas no acreditan toda la malla, CCD, separación universal,
GPU física o calidad artística global. No cerrar #5/#6/#7 por esta unidad.

## Integraciones que no deben repetirse

#50 (`7231aa5`): sight 40 + 18 con cinco guardas compartidas, mismo productor,
58 nombres, ocho intercambios y 61 estados por intercambio. PR y push Verify,
benchmark y Pages aprobados. [Cierre real](https://github.com/CripterHack/distrito-cero/pull/50).
El límite de 1800 s por productor se conserva. Aumenta el máximo agregado de
runners, sin afirmar mejora de FPS ni menor cómputo total.

#49 (`0fa83b9`): rifle ↔ pistola libre/recarga. Su CI previa aprobó. Sight del
push `36304175245` falló por timeout, conservado como fallo histórico.
#48 (`613c164`): recarga corta. #47 (`5c0248f`): intercambio corto libre.
#46 (`5266cb7`): actor de marcha. #45/#44: cambio largo desde recarga/libre.
#43/#42: preparación/guardia/recarga. #39/#40: marcha/apoyo. #41: continuidad.
#30/#34–#38: coordinación, benchmark, familias y exportación portable.

Campaña, creador, catálogo, vehículos, policía y reglas permanecen intactos.
[HANDOFF](HANDOFF.md), [QA](QA.md), [recursos](ASSETS.md),
[política de ramas](BRANCH-CLEANUP.md). Revisión propia, no independiente.

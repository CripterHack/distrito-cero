# Continuación actual · apoyo dinámico continuo, v0.20.5

Base remota `bfa26cd629afbc5a4295d8afdbbf833cddd587c2`, árbol
`f60e128f9dea2f17ef40ace6373a623fa71086af`. PR #39 integrado y los cuatro workflows
posteriores terminaron success: Verify 35870590860, exportación 35870591093,
benchmark 35870591062 y Pages 35870589780. No repetir los PRs #30/#34–#39.

[Apoyo dinámico](SUPPORT-RELEASE.md) y
[plan](../../specs/003-weapon-contact/plan-support-release.md) describen esta unidad.
La reproducción local con simulación nativa localizó saltos de +109.59 y -84.91 mm
al cambiar entre apoyo y balanceo. No eran cambios de cámara. El ajuste conserva
el desfase del último apoyo y lo desvanece con una curva quintica. Un muestreador
compartido exige alcance en balanceo, anticipa el siguiente talón y suaviza sólo
la recuperación ascendente, siempre por debajo del techo geométrico.

Siete nuevas regresiones y 543 Node completos aprobaron, sin skips. Los 89 tests
Python del core, autoría, build y exportación también aprobaron. Las cuatro
secuencias canónicas antes/después contienen 282 frames verificados y 52 revisados
visualmente. Trayectoria física y cámara idénticas, Storage fixture y GPU software.
El nuevo PR registra la CI y revisión del HEAD antes de cualquier merge. No
confundir esta nota de implementación con integración o despliegue.

Cambian character-motion.js y skin-rig.js, además de pruebas, versión y build.
No se toca montaje, armamento, malla, longitudes, reglas, trayectoria física o datos.
HTML nuevo: `4307c76139bc4f4b8178a16792ecb6c490bd1b0633d98a4a4a86336036cf3641`.

El siguiente pendiente real sigue siendo la penetración de culata/prenda durante
guardia y recarga. No se considera resuelto por este ajuste de pies. #5 requiere
decisión artística/procedencia global y #7 recorrido/playtests/hardware. No cerrar
issues para satisfacer sólo un recuento ni fabricar evidencia humana o física.

Copia local de Pages 10754299290, digest
`d66ec2269f2cf24040f25777aa029100acdbab3690f4771760c0b50a31f0bc79`.
Git no resolvió DNS. Los commits usan padres remotos reales y el helper de
reconstrucción se excluye del producto. Su primer fallo por checkout superficial
queda conservado. Revisión propia, no independiente.

[Handoff anterior completo](https://github.com/CripterHack/distrito-cero/blob/bfa26cd629afbc5a4295d8afdbbf833cddd587c2/docs/project/HANDOFF.md)
conserva historia de tangentes, fuentes portables y marcha lenta. Es registro,
no trabajo pendiente. [Estado](STATE.md), [QA](QA.md), [exportación](CURRENT-HUMAN-EXPORT.md).
Revertir fuentes y build asociados no requiere migración ni borrado de partidas.

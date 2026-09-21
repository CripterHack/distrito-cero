# Handoff · v0.20.1 / rechazo de superficies, rifle todavía en RED

**Base de master:** `32a8cca590b83a5b2a1b3efabad5723d3c9d6757`, PR #28 integrado y #27 cerrada. **Trabajo actual:** PR #30, `fix/029-rifle-coordination`, issue #29, requisito pendiente de #6. Producto **0.20.1 · Coherencia**, canal prototype. Leer [STATE](STATE.md), [QA](QA.md), [plan #29](../../specs/003-weapon-contact/plan-rifle-coordination.md) y [rechazo de superficies](../../specs/003-weapon-contact/stock-surface-rejection.md).

## Última continuación

Se restauró el runtime original después de rechazar una variante C que acercaba la mira a 1.8818 mm, pero atravesaba cara/cuello 31.2559 mm y chaqueta 16.3883 mm. Esa variante también provocó un salto de 41.55 mm en la prueba Node de continuidad del pulgar al iniciar recarga. No copiarla al producto.

Nuevo control QA `stock_clearance.js`: superficies reales deformadas por la paleta suministrada contra los dos volúmenes gráficos de culata, verificados por sus triángulos. Mantiene 4,863 vértices de cara/cuello y 2,993 de chaqueta superior. Diez tests Node cubren geometría ausente, falsos contactos, no mutación, transformación, marco inválido y datos no finitos. Dos tests Python hacen visible el rechazo en la galería sin atribuir aceptación artística.

La observación reutiliza las doce capturas de rifle del escenario existente. No añade otro montaje ni otra matriz. El rifle canónico ya penetra 15.53 mm en la chaqueta aunque su distancia al punto heredado sea pequeña. Por eso no se aprueba un apoyo sobre un único punto de superficie.

**Resultado local actual: 495 Node, 494 aprobados y uno fallido.** El fallo sigue siendo `rifle neutral coordinates the mesh eye and stock without stretching arms`, `eye/sight: 0.238643317922643 m`. Se conservan sus umbrales y se añade rechazo de penetración. Sin skips. 83 Python, autoría, build/export y la integridad gráfica de longarms aprobaron. No integrar esta rama en RED.

La suite gráfica local `20260921T175615Z-a8b5616788c5` completó 24 checks y 48 PNG con hashes cotejados, sin errores/peticiones, sobre el HTML canónico. Usa fixture, tiempo/cámara preparados y GPU software. El commit local es `null` porque la copia procede de Pages. El replay de C sustituye módulos en memoria y está separado de esa evidencia canónica. La CI del nuevo HEAD se consulta en #30, no se deduce de los resultados locales.

## Lo que ya se integró

PR #28 fue revisado sobre HEAD `6d2effd65868a921422cbe9099c5c633f474f07d`. Verify `35457549479` y benchmark `35457549514` terminaron success. Artefacto WebGL `10589016422`, SHA-256 `d1d7c2de18bc2eb0b648c8a4fd9933519a4597bce4bf63ebd0a3bc89603047b0`: nueve suites, 205 checks, 133 PNG, cero errores/peticiones. La revisión fue propia, no independiente.

Después del squash terminaron success [Verify 35623114643](https://github.com/CripterHack/distrito-cero/actions/runs/35623114643), [benchmark 35623114699](https://github.com/CripterHack/distrito-cero/actions/runs/35623114699) y [Pages 35623112646](https://github.com/CripterHack/distrito-cero/actions/runs/35623112646). El artefacto Pages `10649968865` contiene el HTML canónico. No confundir despliegue/artefacto con una nueva consulta HTTP pública desde el laboratorio.

#25/#26 están cerradas: no repetir la cobertura HTTP de recarga. Sus fallos históricos y verificaciones se conservan en [plan nativo](../../specs/003-weapon-contact/plan-native-reload.md). El cierre del auditor #27 está en [su plan](../../specs/003-weapon-contact/plan-longarm-audit.md). Ese auditor no corrigió las posturas.

El primer HEAD de #30, `f2dc994`, terminó con Verify `35626695314` fallida por el requisito ocular. WebGL y HTTP de ese run sí terminaron success. No reutilizarlos como verificación del nuevo HEAD.

## Decisión pendiente para continuar

Las variantes A/B anteriores fueron rechazadas por cabeza/hombro forzados. C también falla por superficies y recarga. El [informe de rechazo](../../specs/003-weapon-contact/stock-surface-rejection.md) conserva las diferencias y propone revisar el espacio cosmético de la culata, no seguir optimizando sólo ojo y punto del hombro.

La geometría del rifle y el contrato original no se han cambiado. Antes de autoría nueva, definir explícitamente geometría/referencias y comparación. Una alternativa de pose con el modelo actual sigue siendo posible de investigar, pero debe satisfacer también el control de superficies. No se demostró que no exista. Faltan límites/revisión artística de postura y una corrección real con continuidad en toda la acción. No crear otra matriz diagnóstica equivalente.

## Invariantes y entorno

No hay corrección de producción aceptada en #29. Se conservan `src/`, HTML, assets, rig, reglas, partidas, permisos, workflows y versión. HTML SHA-256 `4a78bcca34cd40b2c406b0642362f30a6b71303d8a4a6ace659e0ba4afc9918d`, 8,862,957 bytes. Fuente `dfb16e65c1a64d991f2bedfbecf0892d69c8b2110e4be1403e31d7af739c4fdb`. No borrar datos del sitio.

Copia local del ZIP Pages `10649968865`, SHA-256 `d14dbc643645e4121f757a6a958fd432510de98885efa3821deb41e22c0394c7`. Git volvió a fallar por DNS. Los commits del conector parten de padres remotos reales. No se publica historia sintética ni se atribuye hardware físico al fixture. Revisión propia, sin un segundo revisor independiente.

## Comandos al retomar

```sh
node --test tests/rifle-surface-rejection.test.cjs
python3 tests/longarm_gallery.test.py
# RED conocido: no ocultar este requisito para integrar.
node --test tests/rifle-coordination.test.cjs
node --test tests/*.test.cjs
python3 build.py --check
xvfb-run -a python3 -m tools.qa.run --suite longarms --headed
```

Después de una corrección real, ejecutar autoría, build/export, Python vigente, Node completo, suites gráficas y HTTP según QA. Revisar preparación, recarga/cancelación, agachado, pitch, cuello, movimiento y otros equipos. Exigir capturas del runtime nuevo sin sustituciones en memoria y CI del HEAD exacto antes del merge. Master y Pages se verifican por separado.

#5 requiere revisión artística/materiales/variantes. #6 sigue abierta por coordinación, superficies y movimiento. #7 necesita escena/recorrido íntegro, playtest y GPU física. Ni un control de rechazo verde ni un perfil que sólo satisface distancias cierran esos gates.

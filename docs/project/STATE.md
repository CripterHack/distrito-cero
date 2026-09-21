# Estado real del proyecto

## Versión activa del árbol: v0.20.1 · Coherencia

Producto `0.20.1`, canal **prototype**, fecha declarada 2026-09-18. Identidad canónica en [version.json](../../version.json), hash y tamaño exactos del HTML en [build-info.json](../../build-info.json). Guía vigente en [v020](../v020/GUIA.md). La publicación de un commit se confirma en Actions y comparando Pages, no por la existencia de este documento.

GitHub Pages sigue configurado sobre master. No se cambia esa configuración, la licencia ni los esquemas de datos. Una pestaña abierta necesita recarga para ejecutar código nuevo, sin borrar datos del sitio.

| Issue | Estado y alcance |
| :--- | :--- |
| #2 · QA portable | Cerrado por PR #8. Copias aisladas, informes frescos y diagnóstico. |
| #3 · Guardados nativos | Cerrado por PR #9. Persistencia HTTP, reapertura y conflictos reales. |
| #4 · Recuperación WebGL | Cerrado por PR #10. PR #17 protege generaciones retiradas. No garantiza que un driver no vuelva a reiniciarse. |
| #5 · Personaje patrón | Benchmark #11 integrado. Aprobación artística y otros gates pendientes. |
| #6 · Contactos/recargas | Mangas #12, óptica #13, falanges #15, oposición #16, ambas manos #18, contorno palma/pulgar #20 y mira de armas cortas #22 integrados. Armas largas y revisión visual de transiciones pendientes. |
| #7 · Vertical slice | Pendiente de escena, recorrido íntegro y evaluación de juego/hardware. |
| #19 · Publicación v0.20 | Cerrado tras PR #20, CI de master y comprobación de Pages y guardados. |
| #21 · Mira de armas cortas | Cerrada. PR #22 integrado por squash en `3629d18`; verificación registrada en la issue. |
| #23 · Cancelación por fases | Cerrada mediante PR #24, integrado en `61410a0`. CI del push y Pages aprobados. No cierra #6. |
| #25 · Recargas en navegador | Cerrada mediante PR #26, integrado en `fecf117`. CI, benchmark y Pages posteriores aprobados. No cierra #6. |
| #27 · Auditor cooperativo | Cerrada mediante PR #28, integrado en `32a8cca`. CI, benchmark y Pages posteriores aprobados. Auditor QA, no corrección visual. |
| #29 · Rifle neutral | PR #30 en RED: 494/495 Node. Control de rechazo de superficies añadido, pero ninguna pose aceptada. [Hallazgo y límites](../../specs/003-weapon-contact/stock-surface-rejection.md). |

## Última continuación de #29 · 21 de septiembre de 2026

Se descartó una tercera variante de superficie: error ocular de 1.8818 mm, pero penetración de 31.2559 mm en cara/cuello y 16.3883 mm en chaqueta. También rompía la continuidad del pulgar en el primer paso de recarga Node, con 41.55 mm de salto. Se restauraron las fuentes de producción y los umbrales originales. No se aprobó un nuevo contrato de apoyo.

`stock_clearance.js` añade un control QA de las superficies reales y la geometría verificada de la culata, integrado en las capturas existentes de rifle. No es otra matriz o solver. La pose canónica ya muestra 15.53 mm de penetración en chaqueta. Se añadieron diez pruebas Node y dos Python de galería, sin ocultar la prueba ocular fallida.

Resultado local actual: **495 Node, 494 aprobados y uno fallido**, 83 Python aprobados, autoría/build/export aprobados. Suite gráfica `20260921T175615Z-a8b5616788c5`: 24 checks de integridad, 48 PNG con hashes cotejados, cero errores/peticiones. El replay de la variante rechazada está separado de la ejecución canónica. La nueva CI se consulta por el HEAD del PR, no se infiere de este documento. [Evidencia, limitaciones y decisión pendiente](../../specs/003-weapon-contact/stock-surface-rejection.md).

El HTML y todos los recursos de producción permanecen sin cambios. No hubo merge ni despliegue nuevo en esta continuación. #29 y #6 siguen abiertas.

## Parche 0.20.1

Alineación de pistola/revólver con la referencia ocular del avatar y retroceso que no abandona bruscamente esa referencia. Preparación visual gradual, incluyendo el primer intervalo. Sin cambios en malla, pesos, rig, equipo relativo a las manos ni formatos. [Detalle y límites](SIDEARM-SIGHT.md).

PR #22 se integró como `3629d1876e160bd32c9e94eec70ce947043e7c66` después de revisar `87e3dd39b94066ece9003e310e8291966c722e20`. La CI del PR `35388020900` aprobó 429 Node, 181 checks gráficos seleccionados, guardados nativos y build/exportación. El benchmark `35388020903` también aprobó. Estas cifras no se reutilizan como si fueran la CI del push posterior.

## Unidad de verificación #23 · integrada

[Plan de cancelación](../../specs/003-weapon-contact/plan-reload-cancellation.md). Diez equipos, siete puntos del temporizador real y rutas de cancelación de inputs, cambio de equipo, restauración y cierre del selector. 490 combinaciones agrupadas en 40 tests, más catálogo y control negativo. Las cifras describen cobertura implementada, no sustituyen el resultado de ejecución del PR.

PR #24 se integró en `61410a029c73e0f1efc91dc76a4ccaddbca5c38e`. La CI posterior de master [35423304841](https://github.com/CripterHack/distrito-cero/actions/runs/35423304841) y el despliegue [35423304003](https://github.com/CripterHack/distrito-cero/actions/runs/35423304003) terminaron aprobados. La ejecución local de esta base confirmó 471 tests Node y el hash canónico del build. Estos resultados no se reutilizan como evidencia del HEAD de #25.

No cambia código de producción, versión, HTML, assets o reglas. Cancelar inputs conserva una recarga pendiente. Cambiar de equipo la descarta. La restauración descarta acciones transitorias y la UI es propietaria de cancelar inputs al reanudar. El setMode mínimo del test no certifica el reloj pausado del navegador ni sus eventos físicos.

## Unidad de navegador #25 · integrada

[Plan y límites](../../specs/003-weapon-contact/plan-native-reload.md). PR #26 integrado en `fecf117385941dabd4e22f13c04d45d4032fb042` tras la CI del HEAD revisado. Añade `reload` con 31 checks/27 escenarios y 16 tests Python de contrato/diario. Conserva el producto 0.20.1. Prepara escenas y temporizadores, pero no sustituye el bucle ni Storage. La evidencia HTTP procede de Actions, no del intento local bloqueado.

La CI de master [35428128166](https://github.com/CripterHack/distrito-cero/actions/runs/35428128166), el benchmark [35428128169](https://github.com/CripterHack/distrito-cero/actions/runs/35428128169) y Pages [35428127755](https://github.com/CripterHack/distrito-cero/actions/runs/35428127755) terminaron `success`. Sus resultados se consultaron al iniciar #27, separados de la CI previa del PR.

El primer run de #26 (`35425812835`, HEAD `7bf024e`) pasó `release`/`native` (49 checks), pero `reload` alcanzó el límite de 900 s después de 27/31 checks correctos. Ese resultado sigue fallido. La revisión amplía el presupuesto a 1,800 s, preserva un diario parcial separado y añade cuatro pruebas del diario. No cambia las aserciones de aceptación. [Diagnóstico y artefacto](QA.md#primer-run-http-de-26-presupuesto-insuficiente).

## Unidad de diagnóstico #27 · integrada

[Auditor, resultados y límites](LONGARM-CONTACT.md), [plan](../../specs/003-weapon-contact/plan-longarm-audit.md). Se implementó un observador QA que consume la paleta y el montaje dibujados, comprueba las referencias geométricas por familia y registra ojos, culata, palmas y longitudes entre articulaciones independientes. Los 24 checks verifican la integridad del auditor, **no aprueban CONTACT-03**.

La ejecución gráfica local produjo 48 capturas, una matriz numérica de 72 poses y 240 muestras del ciclo. El desajuste ocular neutral sigue en 205.53–238.64 mm. La traslación aislada al ojo separaría la culata de la referencia del hombro entre 209.63 y 242.56 mm. Es un cálculo contrafactual, no una corrección renderizada. No se cambian `src/`, HTML, assets, versión o guardados. La siguiente unidad debe corregir la coordinación de la pose usando este auditor, no construir otra matriz equivalente.

## Primera reanudación del 21 de septiembre de 2026

PR #28 integrado por squash en `32a8cca590b83a5b2a1b3efabad5723d3c9d6757`. Se revisó el artefacto WebGL del HEAD exacto antes del merge: nueve suites, 205 checks, 133 PNG y cero errores/peticiones registrados. Se comprobaron los 48 hashes PNG del auditor y se revisaron sus poses/ciclos. Eso valida el observador, no corrige la postura.

Después del merge terminaron `success` [Verify 35623114643](https://github.com/CripterHack/distrito-cero/actions/runs/35623114643), [benchmark 35623114699](https://github.com/CripterHack/distrito-cero/actions/runs/35623114699) y [Pages 35623112646](https://github.com/CripterHack/distrito-cero/actions/runs/35623112646). Se cotejó el HTML del artefacto Pages con el hash canónico. No se afirma una nueva consulta HTTP a la URL pública desde el laboratorio.

La siguiente unidad #29 reutiliza el auditor. La base pasa build inmutable y 484 Node. El nuevo test de aceptación del rifle neutral falla por 0.238643317922643 m de separación ocular, dejando inicialmente la rama en **484 aprobadas y una fallida**. Dos prototipos temporales acercaron ojo y mira pero se rechazaron visualmente por la postura de cabeza/hombro. No entran en `src/`, HTML o assets. Esta rama no debe integrarse hasta resolver el requisito sin perder naturalidad, contactos y continuidad. [Plan y evidencia del bloqueo](../../specs/003-weapon-contact/plan-rifle-coordination.md).

## Base consolidada 0.20.0

Se recuperó el trabajo sin PR de `fix/006-palm-webbing` (`91ba765`) sobre `ef905ec`. La zona compartida entre palma y pulgar penetraba apoyos que las pruebas digitales no cubrían. El correctivo reduce suavemente hasta 4 mm de profundidad en 1,166 posiciones de piel. Mantiene el parche palmar medido, pesos, UV, topología, 49 huesos, uñas y otros buffers. [Detalle](THENAR-SURFACE.md).

El build genera la identidad de inicio, pestaña, pausa e interacciones, y `DC.BuildInfo`. `build-info.json` identifica las fuentes y el HTML. `python3 build.py --check` detecta salidas ausentes o diferentes sin modificarlas. [Publicación](RELEASES.md).

## Sistemas conservados

Campaña, creador, once estilos de cabello, catálogo de hasta doce partidas con nombres, equipamiento, selector translúcido, vehículos/ocupantes, policía, daños y regiones procedurales. No se añade combate autónomo nuevo, simulación de tejidos, terreno avanzado o una vertical slice completa.

El recurso humano tiene SHA-256 `522a9a24e2cc70857a3ec5c18bf9c2126c7b59d9ce8e4c5601c3b8be2c911b54`. El kit GLB de equipamiento conserva sus bytes. Los GLB humanos anteriores son exportaciones históricas, no modelos nuevos de v0.20.

## Evidencia y límites

Los proxies gráficos no son autocolisión completa. Tiempo/cámara preparados no demuestran FPS. El benchmark smoke tiene 30 capturas/36 comprobaciones, la matriz completa requiere su propio informe. La prueba de versión importa por HTTP nativo un JSON sintético producido por el serializador de v0.19. Los guardados nativos se verifican por separado de los fixtures gráficos y de roundtrips unitarios.

Los fallos históricos permanecen documentados en [ACTIONS-RECOVERY.md](ACTIONS-RECOVERY.md). Cada commit nuevo exige sus propias ejecuciones. El cierre de #25 está registrado en #26. El cierre de #27 y sus verificaciones posteriores están registrados en #28. La nueva rama de #29 sigue en RED y no hereda esos resultados como aprobación propia.

## Historia preservada

Base importada v0.19: `23f9e9d`, 730 archivos y 729 huellas. HTML original `3aa9a27f4941ea1c701069c61db133ab3c93087e35d833d4921ba25b8a4b059f`. `SOURCE-MANIFEST.json`, `docs/v019/` y `qa/v019/` conservan su función histórica. No se actualizan para simular resultados actuales.

Runtime nativo, 38 fuentes JS con orden significativo y un HTML autónomo. Sin validación universal de GPU física, Safari/Firefox, móviles, tejidos, multijugador o fotorrealismo. [Handoff](HANDOFF.md), [QA](QA.md), [recursos](ASSETS.md).

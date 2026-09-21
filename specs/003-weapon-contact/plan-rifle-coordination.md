# #29 · Coordinación del rifle neutral

**Estado: RED, no integrable.** Base remota `32a8cca590b83a5b2a1b3efabad5723d3c9d6757`, rama `fix/029-rifle-coordination`, PR #30. Producto 0.20.1 sin cambios. [SPEC-003](spec.md), [auditor existente](../../docs/project/LONGARM-CONTACT.md). Continuación de #6, no cierre de #5/#6/#7. Ejecución secuencial y revisión propia, sin atribuir revisión independiente.

## Actualización posterior: control de rechazo

El resultado actual es 494/495 Node, con el mismo fallo ocular pendiente. Diez pruebas nuevas protegen una observación de cara/cuello y chaqueta contra la culata real. Dos pruebas Python hacen visible su resultado en la galería. La variante C se rechazó por penetraciones y discontinuidad de recarga y se restauró el producto. [Contrato del control, resultados y siguiente decisión](stock-surface-rejection.md). Las secciones A/B y el RED inicial siguientes se conservan como historia, no como resultados actuales.

## Objetivo y contrato

Corregir el rifle neutral reutilizando el montaje único y el observador de #27. El requisito pendiente queda en `tests/rifle-coordination.test.cjs`, dentro del patrón normal de CI, no oculto tras skip, todo o un selector especial. Exige ojo/eje <10 mm, culata/referencia <30 mm, mira más de 50 mm por delante del ojo, palmas <12 mm, segmentos <1e-6 m de variación y serialización sin cambios. Se añade ausencia de penetración mayor de 2 mm en el muestreo real de cara/cuello y chaqueta superior. Pasar ese muestreo no acredita colisión completa.

La medida de culata usa la cara realmente visible. La referencia del hombro sigue siendo la articulación con el desplazamiento heredado, **no la superficie completa de la chaqueta**. No desplazar esa referencia, elevar umbrales o remodelar una mira sólo para conseguir verde. Una futura revisión de referencias debe demostrar su relación con la superficie y conservar la comparación anterior explícita. El contrato experimental de apoyo en un solo triángulo no se aprobó.

## Estado inicial comprobado el 21 de septiembre de 2026

La base aprueba `python3 build.py --check` y 484/484 Node. Tras añadir el requisito pendiente, la suite completa produce inicialmente **484 aprobadas y una fallida de 485**, sin canceladas, omitidas o todo. El fallo es `rifle neutral coordinates the mesh eye and stock without stretching arms`, `eye/sight: 0.238643317922643 m`.

No se modificaron `src/`, HTML, assets, versión, guardados, munición, permisos ni workflows. El código de exploración no se incorpora al juego. La CI de esta rama no debe usarse como una aprobación de producción mientras esa prueba siga fallando.

## Exploraciones A/B descartadas

Se probaron rotaciones rígidas temporales sobre el renderer existente, en memoria, con los helpers y cámaras de `longarm_stage.js`. No fueron una ejecución del runtime canónico sin modificar. Se capturaron el original y dos variantes, cada uno frontal y tres cuartos. La revisión visual no aceptó la elevación del hombro y la inclinación de cabeza resultantes.

| Observación renderizada | Ojo/eje | Culata/referencia | Decisión |
| --- | ---: | ---: | --- |
| Original | 238.6433 mm | 6.1807 mm | Defecto reproducido |
| Variante A | 0.1569 mm | 8.1158 mm | Rechazada visualmente |
| Variante B | 2.7697 mm | 26.9531 mm | Rechazada visualmente |

Estas cifras **no aprueban** CONTACT-03. El HTML base conserva su hash porque las sustituciones eran instrumentación temporal. Sus resultados no son evidencia de un producto corregido. El cuello y el hombro necesitan límites visuales y de superficie, además de las distancias del auditor.

Para evitar repetir las mismas variantes, los incrementos ensayados, en radianes, fueron:

| Parámetro de presentación | A | B |
| --- | ---: | ---: |
| Yaw de torso | -0.075 | -0.15 |
| Yaw de clavícula derecha | -0.8 | -1.098 |
| Roll de clavícula derecha | 1.0 | 0.935 |
| Pitch cervical añadido | -0.028 | -0.031 |
| Yaw cervical añadido | 0.418 | 0.166 |
| Roll cervical añadido | -0.7 | -0.65 |
| Pitch de torso añadido | 0 | 0.011 |
| Roll de torso añadido | 0 | 0.293 |

El yaw de torso se distribuyó 35/65% entre spine/chest. Pitch y roll de torso, 40/60%. Los incrementos cervicales de pitch/roll se repartieron 65/35% entre neck/head y yaw 40/60%. Son recetas descartadas, **no perfiles para copiar al producto**.

Una exploración numérica posterior incluyó ambas clavículas y continuó necesitando correcciones amplias. También se exploró un desplazamiento local de la pieza posterior del objeto, sin aceptarlo, renderizarlo como producto ni modificar su asset. No se publica ninguna de esas alteraciones. No se realizó una búsqueda exhaustiva ni se concluye que no exista una solución mejor.

## Causa y decisión de continuidad

El montaje fija la culata con la pose del torso anterior al IK y después proyecta el objeto dentro de las dos esferas de alcance. Ajustar sólo cabeza/hombro dominante puede dejar el brazo de apoyo sin alcance. Esa proyección vuelve a desplazar el objeto y modifica a la vez la alineación ocular y el apoyo de culata. Las palmas pueden seguir coincidiendo gracias al solver, sin que la postura sea aceptable.

La continuación demostró además que una distancia pequeña al punto del hombro no impide que la culata atraviese chaqueta o cara. Por eso el rechazo de superficies se integra antes de seleccionar otro perfil. No reemplaza las métricas anteriores ni la revisión artística.

**Decisión:** conservar el requisito fallido y no integrar los prototipos. Coste: el rifle sigue desalineado, pero master no recibe una postura que sólo pasa números. No crear otra matriz QA equivalente. Retomar desde esta regresión y el nuevo control. La propuesta de revisar la geometría cosmética debe definir su contrato antes de cambiar modelos o referencias.

## Trabajo y puertas pendientes

- [x] Recuperar base exacta, verificar build y suite anterior.
- [x] Reproducir RED con el auditor existente, antes de editar producción.
- [x] Contrastar dos variantes renderizadas y registrar su rechazo sin cambiar umbrales.
- [x] Incorporar un control de rechazo de penetración contra superficies reales, con negativos e integración en las capturas existentes.
- [x] Rechazar C por superficies/recarga, restaurar el runtime y preservar su replay separado.
- [ ] Fijar límites de postura y definir el contrato de geometría/referencias permitido antes de otra corrección. La revisión artística no se deduce del nuevo control.
- [ ] Implementar una coordinación aceptable dentro del montaje existente, no otro solver. Las fuentes humanas y longitudes se conservan. Un cambio cosmético del objeto requiere contrato explícito y comparación.
- [ ] Llevar a GREEN el caso neutral, comprobar yaw/traslación, tiempo, cuellos, agachado, pitch, preparación, recarga/cancelación y equipos no afectados. No deducir su éxito del caso estacionario.
- [ ] Build/export, Node completo, Python vigente, suites gráficas y HTTP aplicables sobre una corrección real. Comparación del mismo renderer sin sustituir módulos, superficies y continuidad.
- [ ] Actualizar STATE/HANDOFF/QA con una corrección real, revisar diff y CI del HEAD exacto antes del merge. Después verificar master y Pages por separado.

## Reproducción del bloqueo

```sh
node --test tests/rifle-surface-rejection.test.cjs
python3 tests/longarm_gallery.test.py
node --test tests/rifle-coordination.test.cjs
node --test tests/*.test.cjs
python3 build.py --check
```

Los controles nuevos deben aprobar. La aceptación del rifle y la suite Node completa siguen fallando por el requisito ocular mientras no exista corrección. El build debe aprobar sin mutar archivos. El PR permanece en borrador. No usar skip, bajar el criterio, retirar el test de CI ni integrar sólo porque las suites antiguas sigan pasando.

La copia local procede del artefacto Pages `10649968865`, ZIP SHA-256 `d14dbc643645e4121f757a6a958fd432510de98885efa3821deb41e22c0394c7`. Git remoto no resolvió DNS. Se publican commits por el conector sobre padres remotos reales. La continuación no fabricó historia local: el manifiesto gráfico registra commit null. Los prototipos se ejecutaron con Chromium del sistema, Xvfb y GPU software, sin benchmark físico ni prueba nueva de navegación HTTP pública.

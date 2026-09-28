# SMG ↔ revólver desde recarga: plan de implementación

> Ejecutar con superpowers:executing-plans, TDD y revisión propia del cambio completo.

**Goal:** conservar pose y pieza visibles al cambiar SMG/revólver desde recarga, sin retrasar acciones lógicas.
**Architecture:** retirar sólo la exclusión de recarga/retorno de esta pareja en captureSwitch. Reutilizar captura, montaje, retorno y caché canónica. Ampliar los bucles Node y el catálogo único de sight.
**Tech Stack:** JavaScript/WebGL2 nativos. Node/Python/Playwright para QA.
**Spec:** [SPEC-003](spec.md), CONTACT-04/05, issue #6. Base #54 d50a60665638f43076b85739205d59c8ab2c1741, árbol a6375d6e8b589bc961a6565005101ec8b16cfc84.

## Restricciones globales

HTML autónomo, 49 huesos, munición/partidas/gameplay intactos. Sin nuevo solver,
tracker, reloj, caché, geometría o dependencias de runtime. Retorno cosmético de
0.90 s y arco de 0.12 m ya medido, sin elevar tolerancias. Conservar rechazo de
tercer prop mostrado y prioridad inmediata de disparo/nueva recarga. La limpieza
anterior está bloqueada y no se reintenta en esta unidad.

## Foco de revisión

Fases activas y selector congelado después de cancelar inputs. Reversión antes y
después del cambio de modelo. Pieza retornando tras pasar por una tercera selección
lógica. Actor en movimiento/memoria de pies. Caché fría o inicializada y guardados.
Los puntos del revólver se observan sobre el cuerpo real, no un cargador o cilindro
articulado inexistente.

## Tareas

- [x] Verificar snapshot/base y continuidad. CI del master exacto 36395675734 aprobó sus siete jobs. La repetición local completa agotó el wrapper de 900 s, exit124: no se cuenta como aprobación local.
- [x] Extender tests/cross-family-handoff.test.cjs a siete fases de recarga de SMG/revólver en cuatro configuraciones, selector congelado, retorno/reselección, movimiento, prioridades y tercera pieza. Extender tests/finger-cache-order.test.cjs a ambas nuevas salidas. Observar los fallos antes de modificar runtime.
- [x] Retirar sólo recarga lógica/visual de la exclusión SMG en src/weapon-handling.js. Mantener third-prop guard. Ejecutar regresiones, longitudes, palmas, piezas y culata. Límites: inicial <1e-5, paso preparado <30 mm, objetivos <12 mm, penetración muestreada máxima 2 mm.
- [x] Primero modificar tests/qa_selection.test.py y observar RED. Añadir dos recargas a tools/qa/sight_contract.py: 94 checks = 40 +26 +28, dieciséis secuencias. Conservar los 84 nombres y catorce casos anteriores, cinco guardas por partición contadas una vez, 61 estados/caso, resolución/capturas/inputs. Usar el tercer job existente sin elevar 1800 s/productor ni 40 minutos/job.
- [ ] Actualizar versión 0.20.18, build y documentación vigente. Verificar pruebas locales dirigidas, Python/autoría/exportación y toda la suite Node en CI del HEAD. Revisar antes/después en el renderer real y medir la partición ampliada.
- [ ] Publicar PR sobre la base remota exacta. Verificar CI y artefactos, revisión propia explícita y merge condicionado. Verificar push y Pages separadamente. No cerrar #5/#6/#7 por conteos.

## Registro y reversión

La copia local tiene historia sintética pero sus 948 archivos reconstruyen el
árbol remoto base exacto. Mantener esa distinción en evidencia. Conservar comandos,
fallos, HTML SHA-256, informes y capturas. Revertir esta unidad con versión/build
no migra ni elimina partidas. La continuidad cosmética no acredita manipulación
mecánica, toda la malla/CCD, aceptación artística o FPS en hardware físico.

## Registro local previo al PR

RED: 20/29 aprobadas y nueve fallidas en un fixture aislado del árbol base.
GREEN dirigido: 29/29, cero fallos, omisiones o cancelaciones, 202.281 s.
192 casos de selección y 456 poses de culata, mínimo muestreado −0.353 mm.
El timeout local de baseline no equivale a un fallo de aserción ni a una
aprobación. La CI completa del HEAD sigue siendo obligatoria antes del merge.
La primera ejecución gráfica perdió su contexto antes de completar checks,
con una captura previa oscura. Se conserva como fallida, sin cambiar criterios.
Resultados posteriores e integración se registran en el PR, no se anticipan.

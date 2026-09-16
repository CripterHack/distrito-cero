# Actions: contexto perdido y renderizador liberado

Base: `bbc26848ee0dd26a8193aa6dbfe4dfafc3a9e734`.

## Incidente confirmado

El [run de master 35045749864](https://github.com/CripterHack/distrito-cero/actions/runs/35045749864) falló después de integrar PR #16, cuyos checks habían aprobado. Son ejecuciones distintas. Build, guardados nativos, benchmark y Pages aprobaron sus jobs separados.

El [artefacto del fallo](https://github.com/CripterHack/distrito-cero/actions/runs/35045749864/artifacts/10426703485) contiene handling.log y el informe de manejo. Completó 27 comprobaciones y luego registró `contextlost: software GPU` y `TypeError: Cannot read properties of undefined (reading 'push')` en buildSector/add. thumbs y fingers habían pasado. El harness rechazó correctamente el informe incompleto.

No se ha demostrado qué condición concreta del driver/host causó la pérdida. El mismo HTML completó manejo al ejecutarlo aisladamente. No se atribuye el incidente a la postura del pulgar sin evidencia.

## Defecto reproducible

La app ya detenía el bucle y dispose vaciaba las listas de la generación anterior. Sin embargo, render y syncSectors aún permitían acceso directo a esa generación. Un callback tardío o una captura preparada podían construir sectores sobre listas vacías. También puede detectarse isContextLost antes del evento DOM.

Siete tests Node reprodujeron entradas inválidas; dos controles comprobaron que errores de una generación viva siguen visibles. Un evento WEBGL_lose_context real reprodujo exactamente el mismo error de push, sin esperar un fallo espontáneo del driver.

## Corrección

Renderer.render, FrontierRenderer.render y syncSectors rechazan la generación inactiva antes de modificar listas, buffers, frame u origen. La generación nueva dibuja; la referencia anterior permanece inerte incluso tras la restauración. Los defectos de un renderer vivo no se silencian.

El test de manejo deja de sustituir el RAF global. Usa app.stopFrame y un helper exclusivo de QA que completa y verifica cada dibujo directo. Una pérdida inesperada sigue fallando, sin recuperación o reintento silencioso. Un no-op no cuenta como fotograma capturado. gl.finish sólo se usa en las pruebas; no se añade al bucle de producción. La suite continua conserva el RAF de la app.

El harness ahora muestra la cola acotada del log fallido en Actions, además de conservarla como artefacto. Neutraliza comandos de workflow y escapes de terminal. No cambia los requisitos ni admite informes antiguos o incompletos.

## Verificación

Nueve pruebas Node de lifecycle, siete del helper y cinco Python de diagnóstico. Manejo conserva sus 51 comprobaciones. Recuperación pasa de 22 a 25: dibujo durante pérdida, referencia antigua tras restauración y dibujo efectivo de la generación nueva.

```sh
node --test tests/render-lifecycle.test.cjs tests/manual-frames.test.cjs
python3 tests/qa_reporting.test.py
python3 -m tools.qa.run --suite all --headed
python3 -m tools.qa.run --suite native --origin http --headed
```

Consultar PR y Actions para resultados del commit exacto. Los tests gráficos usan storage fixture; la persistencia HTTP nativa se verifica aparte. No es un benchmark de GPU física.

## Historial rojo revisado

Al iniciar esta revisión había cinco runs con conclusión failure. Cuatro eran de ramas de preparación anteriores, con implementaciones posteriores aprobadas:

| Run | Contexto histórico | Paso fallido verificado |
| :--- | :--- | :--- |
| [34933402111](https://github.com/CripterHack/distrito-cero/actions/runs/34933402111) | Importador temporal de QA, retirado | Commit/publicación de la adaptación |
| [34934444269](https://github.com/CripterHack/distrito-cero/actions/runs/34934444269) | Primera batería de guardados nativos | Reapertura de perfil en la suite nativa |
| [34939385744](https://github.com/CripterHack/distrito-cero/actions/runs/34939385744) | Importador temporal de recuperación, retirado | Commit en rama de feature |
| [34991261427](https://github.com/CripterHack/distrito-cero/actions/runs/34991261427) | Primera ejecución del benchmark | Captura del renderer |
| [35045749864](https://github.com/CripterHack/distrito-cero/actions/runs/35045749864) | master después de PR #16 | Manejo: pérdida gráfica y generación liberada |

No se eliminan esos runs ni se cambian sus resultados. Reejecutar un run viejo usa el commit original, no la corrección nueva. Validar el HEAD mediante su propia CI y comprobar después Pages. Las advertencias de acciones dirigidas a Node 20 son mantenimiento pendiente, no el error que detuvo este job.

## Límites y referencias

No se garantiza que el driver nunca reinicie la GPU. Se protegen las entradas de dibujo durante pérdida y tras dispose, no toda llamada GL posible dentro de una función larga. Continúan la recuperación explícita y la exportación de datos.

Sin cambios de assets, anatomía, armas, física, formato de partidas, dependencias de runtime o configuración de Pages. Revertir no necesita migración. La siguiente unidad visual sigue siendo palma/pulgar y contacto entre manos de #6.

[Contexto perdido en Khronos](https://wikis.khronos.org/webgl/HandlingContextLost). [Reejecuciones en GitHub](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/re-run-workflows-and-jobs).

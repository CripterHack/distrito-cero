# CONTACT-03 · Auditoría de coordinación de armas largas

## Resultado de esta unidad

Issue #27 implementa un auditor reutilizable, no una nueva pose. El `master` de partida es `fecf117385941dabd4e22f13c04d45d4032fb042`, producto 0.20.1. **La alineación de armas largas sigue pendiente.** [SPEC-003](../../specs/003-weapon-contact/spec.md), [plan ejecutado](../../specs/003-weapon-contact/plan-longarm-audit.md).

El montaje existente resuelve la culata contra una referencia articulada del hombro y proyecta el objeto dentro del alcance de ambas manos. La alineación ocular de `src/weapon-handling.js` sólo se aplica a `sidearm`. Trasladar el objeto largo hasta el ojo sin coordinar cabeza, torso, hombro y manos mejora una métrica y rompe otra. El auditor expone las dos restricciones juntas, sin modificar ese montaje.

## Referencias independientes

El ojo se obtiene de la región ocular de la malla mediante el helper vigente `sidearm_sight.js`, pero **sus miras de pistola no se reutilizan**. Cada mira larga se comprueba contra vértices de `EquipmentGeometry.build(item)`. SMG, rifle y escopeta usan caras superiores de miras abiertas. Sniper usa el eje del tubo y del disco frontal de su recurso gráfico. Estas son referencias del asset ficticio, no instrucciones de armamento real.

La culata se mide en la cara posterior visible de su caja (`z=-0.2385` en coordenadas del objeto), no en `mount.brace.stock`. El hombro se reconstruye desde la articulación derecha dibujada y el desplazamiento heredado `[0.010,-0.040,0.024]` orientado por yaw. **Es una referencia del rig, no toda la superficie de la ropa.** Por eso difiere ligeramente del error registrado por el `brace` conceptual anterior.

Las palmas se calculan con `SkinRig.palmPoint`. Las longitudes se comparan entre articulaciones transformadas con sus respectivas matrices, no transformando los dos extremos con una sola matriz rígida. La prueba negativa desplaza una mano y demuestra que el observador detecta el estiramiento.

## Captura y cobertura

`longarm_stage.js` crea una simulación de diagnóstico separada de la partida de la aplicación. Usa semilla 1337 y una cámara/tiempo preparados. El observador de `drawEquipment` delega al renderer original y conserva la paleta realmente usada, el montaje, el contador de dibujos y los parámetros de cada imagen. El helper de frames vigente exige un dibujo, finalización de comandos GPU y ningún error GL. No se sustituye la implementación del renderer o de la pose.

Por familia se capturan cuatro poses (`neutral`, `crouch`, `up`, `down`), una cámara frontal y siete puntos de un ciclo de levantar/bajar. Son **48 imágenes**. La matriz numérica tiene 72 combinaciones de cuatro familias, tres cuellos, dos agachados y tres elevaciones. El ciclo registra 60 pasos a 1/60 s por familia, con render cada diez pasos. La galería no es un vídeo de todos los fotogramas ni un benchmark físico.

## Línea base medida en el renderer

Primera ejecución headed: `20260919T170039Z-493e3f9cb85b`, Chromium 144 del laboratorio, Storage fixture, 24/24 checks, 48 capturas y cero errores/peticiones. Los parámetros completos están en cada ficha de la galería. Milímetros, redondeados a dos decimales:

| Familia | Ojo/eje neutral | Culata/referencia neutral | Culata tras traslado contrafactual al ojo | Intervalo ocular de la matriz numérica |
| --- | ---: | ---: | ---: | ---: |
| SMG | 238.64 | 6.18 | 242.46 | 209.76–249.45 |
| Rifle | 238.64 | 6.18 | 242.46 | 209.76–249.45 |
| Escopeta | 234.66 | 11.80 | 242.56 | 206.62–246.62 |
| Sniper | 205.53 | 6.18 | 209.63 | 189.14–214.33 |

El contrafactual sólo aplica una traslación rígida algebraica. No resuelve de nuevo brazos ni produce una captura corregida. Las coincidencias palmares de las poses neutrales están dentro del error numérico, pero eso no aprueba penetraciones de toda la mano, torso o axila.

## Cómo interpretar el resultado

Los checks de `longarms` evalúan **integridad de medición**, no exigen que el defecto actual persista ni simulan que esté resuelto. Un informe de proceso `passed` puede contener `screening.status=needs-coordination`. `artisticAcceptance` es siempre `false`.

El cribado diagnóstico marca ojo/eje >10 mm, culata/referencia >30 mm, palma/ancla >12 mm, variación de longitud >1e-6 m o mira a menos de 50 mm por delante del ojo. Son criterios de inspección explícitos, no una aprobación anatómica universal ni un cambio silencioso de los umbrales de las suites anteriores. Datos incompletos/no finitos son fallos del auditor, no un resultado visual válido.

## Reproducción

```sh
node --test tests/longarm-contact.test.cjs
python3 tests/longarm_gallery.test.py
python3 tests/qa_selection.test.py
xvfb-run -a python3 -m tools.qa.run --suite longarms --headed --timeout 600
# Navegador del sistema, cuando esté disponible:
xvfb-run -a python3 -m tools.qa.run --suite longarms --browser /usr/bin/chromium --headed
```

Abrir `evidence/v020/longarms/report.html` dentro del directorio nuevo de artefactos. Los PNG tienen huella propia y todos los informes identifican el HTML `4a78bcca34cd40b2c406b0642362f30a6b71303d8a4a6ace659e0ba4afc9918d`. Mantener las imágenes junto al HTML. La galería no necesita dependencias remotas y escapa sus etiquetas.

## Verificación y límites de esta revisión

Trece pruebas Node del auditor, cuatro Python de galería y doce de selección. Se observaron fallos antes de implementar los contratos, incluido un caso de contacto no finito descubierto en revisión. El primer intento headless falló por WebGL2 no disponible, antes de producir checks. El modo headed/Xvfb sí pudo ejecutar el renderer, sin cambios de producto ni relajación de criterios. La CI del HEAD exacto y la integración se registran en el PR de #27, no se infieren de este documento.

La copia local procede del artefacto Pages 10579658107 del SHA canónico. Git remoto no pudo resolver DNS. Su commit local es un snapshot de ejecución, no historia remota. No se publica esa historia. Ningún cambio en `src/`, HTML, assets, rig, guardados, licencia, permisos o versión. El auditor y Playwright son herramientas de desarrollo, no dependencias del juego.

## Siguiente unidad, sin repetir este diagnóstico

Reutilizar este auditor para reproducir un caso acotado de rifle neutral y resolver conjuntamente la relación cabeza/hombro/objeto. Antes de tocar producción, fijar el contrato de las referencias que pueden moverse, límites de rotación/alcance y continuidad. Mantener la forma de la cara y la longitud de los brazos. Comparar antes/después con las mismas cámaras y revisar superficies del hombro además de la referencia del rig. Ampliar a las otras familias sólo después de conservar palmas, recarga y movimiento en el caso de referencia.

#5 conserva sus gates artísticos y #7 el recorrido íntegro. #6 sigue abierta. Reversión: revertir únicamente el PR del auditor, sin migración o cambio de partidas.

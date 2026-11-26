# Atlas facial nativo · candidata v0.20.23

Continuación de [UV-REBAKE](UV-REBAKE.md) y del
[plan de integración](../../specs/002-character-benchmark/plan-native-face-atlas.md).
La cara canónica recibe las cartas reparadas y el color cervical horneado.
El shader deja de buscar pigmento en una fila del atlas antiguo y reconstruye
una base tangente ortonormal para leer normales en cartas rotadas o reflejadas.
La fuerza original .30 se incorpora al horneado una sola vez.

## Geometría y materiales

Las 29.016 esquinas y 9.672 triángulos de face conservan todos los bytes de
posición, normal, articulaciones y pesos. Sólo cambian sus UV uint16; no
queda ningún triángulo UV colapsado después de cuantizarlas. Las otras partes,
49 huesos y topología se conservan. El metadato `lodClusterUV` codifica las
celdas UV originales, que también intervienen en la simplificación existente.
Así LOD1/2 mantienen exactamente sus 6.229/3.645 triángulos y atributos
geométricos; las coordenadas nuevas se promedian dentro del mismo grupo e isla
conectada por aristas posición+UV, sin mezclar cartas separadas. Dejarlas sin
promediar produjo parches angulares de color; la comparación dirigida detectó
esa regresión y motivó la corrección.

Los mapas WebP sin pérdida están embebidos en el HTML: color 1024², normal
512² y rugosidad 256². Se filtra color en espacio lineal y normales como
vectores normalizados. Una cuarta imagen de autoría hornea cobertura blanca
con la misma geometría y UV: sólo los texeles de cobertura completa alimentan
la extensión de bordes, compartida por los tres mapas. Así se evita propagar
el fondo y sus bordes parcialmente cubiertos, sin decidir por el pigmento.
La máscara no se incorpora al runtime. Los tres mapas ocuparían **7.340.028 bytes** en RGBA8
con mipmaps completos, frente a aproximadamente 1,75 MiB anteriores. Esta
estimación excluye otros recursos y memoria del controlador; no mide FPS.

El pigmento usa las posiciones originales de reposo, verificadas contra el
GLB neutral y sus huellas. En el horneado cervical 2048², los 6.420 centroides
superiores conservan RGB exacto respecto al atlas portable anterior, antes de
la reducción a 1024² para runtime, que remuestrea esos valores. La mezcla usa sRGB exacto,
mientras el shader anterior aproximaba la conversión mediante `pow(2.2)`;
no se promete igualdad píxel a píxel con ese renderer en la transición.
El detalle de rugosidad y poros cervicales sigue calculándose en runtime.

## Procedencia y reproducción

Se mantienen MakeHuman HM08 / Aksel Skin y sus
[atribuciones](../../assets/ATTRIBUTION-v09.md). Los modelos
[Higgsfield](HIGGSFIELD-ASSETS.md) siguen siendo candidatos separados.
No se han sustituido fuentes anatómicas ni GLB históricos.

[source.json](../../assets/native-face-atlas/source.json) conserva UV nuevas,
hashes de mapas, receta y toolchain. La
[semilla original](../../assets/native-face-uv-source.json) permite restaurar
exactamente la fuente anterior sin duplicar toda la geometría. El hash de la
receta es de JSON canónico; se identifica como `recipeCanonicalSha256`.

```sh
python3 tools/prepare_native_face_atlas.py --check --authored assets/native-face-atlas
python3 tests/native_face_atlas.test.py
node --test tests/crowd-atlas-lod.test.cjs
python3 tests/native_tangent_frame.test.py
python3 tools/export_current_human.py --output artifacts/native-export-new
node tools/qa/audit_uv.cjs artifacts/native-export-new/dc-human-0.20.23-neutral.glb
python3 build.py --check
```

La reproducción compacta requiere NumPy/Pillow de `requirements-dev.txt`,
exclusivamente en autoría. El relleno inicial usa también SciPy; el replay no
necesita SciPy ni Blender. `--check` compara sin escribir. Para un nuevo
horneado completo, restaurar primero `src/hero-asset.js` de `1142029` en un
directorio de staging junto a `character-fit.js`, o utilizar `restore_source`
con la semilla. El GLB baseline y su manifiesto deben corresponder a esa
fuente. El modo cervical rechaza el asset ya migrado como fuente antigua.

El exportador actual lee los mapas canónicos embebidos mediante staging,
convierte V/verde una vez y exporta normalScale 1. Su ruta v1 conserva el
contrato histórico .30. Las herramientas de Blender, tangentes y validación
no se incorporan al juego.

## Alcance de QA y reversión

La regresión WebGL utiliza la función real del shader y 14 cartas analíticas;
comprueba orientación, intensidad, reflejos y derivadas singulares. El visor
de cuello usa el renderer de producción, cámaras y reloj preparados; incluye
LOD1/2 forzados para inspección del material, sin atribuirles selección por
distancia ni FPS. Los informes declaran resolución, backend y guardas.

Esta integración no acredita anatomía AAA, calidad artística definitiva ni
rendimiento en dispositivos físicos. Revisar los bordes de cartas y mipmaps
en hardware real y mantener la aceptación artística separada de las pruebas.
La reversión debe retirar juntos UV, mapas, metadata LOD y shader y reconstruir
el HTML; revertir sólo las texturas rompería su correspondencia. Las partidas
y sus esquemas no requieren migración.

## Revisión visual retenida

Las 28 parejas finales tienen escenarios, cámaras y geometría comparables.
La primera candidata mostró parches angulares en LOD1/2 y un punto oscuro
en la nuca. Se corrigieron promediando UV dentro de cada isla y usando
cobertura explícita para excluir el borde parcialmente horneado. La revisión
final, también con distancia física de 9/16/43 m y zoom controlado, confirma
la corrección en las vistas observadas. La pared del estudio se retiró sólo
en ese diagnóstico para evitar oclusión; no se modificó el shader para aprobarlo.

En la nuca a 43 m, el píxel observado pasó de RGB (160,153,137) en la base a
(161,152,135) en la candidata final. La primera versión de relleno aún dejaba
un residuo: sus capturas se conservan separadas. No se cambió ningún umbral
de aceptación para ocultarlo. Los huecos grandes de prenda/nuca de LOD2 ya
existían en la base y siguen pendientes, junto con la aprobación artística.

Los grupos LOD retenidos cuya UV media queda fuera de su isla están a menos
de 2,994/6,263 píxeles de ella en el atlas 2048², dentro del margen de 16.
Ninguno cae en otra carta y la superficie más cercana pertenece a su propia
isla. Es evidencia específica de este recurso, no garantía de otros atlas.

| Vista | Base | Candidata |
| :--- | :--- | :--- |
| Frontal, LOD0 | [Imagen](../../qa/native-face-atlas-20261125/before-front.png) | [Imagen](../../qa/native-face-atlas-20261125/after-front.png) |
| Perfil, LOD2 forzado a 0,85 m | [Imagen](../../qa/native-face-atlas-20261125/before-profile-lod2-forced.png) | [Imagen](../../qa/native-face-atlas-20261125/after-profile-lod2-forced.png) |

## Verificación local de la candidata

[Resumen con hashes](../../qa/native-face-atlas-20261125/summary.json).
Node completo: **695/695**. Python: exportador **19/19**, replay/atlas **14/14**,
shader WebGL **6/6**, Blender **5/5**, release **12/12**, checkout **1/1**,
equipos **1/1** y workflow **9/9**. Thenar y garment `--check` conservan el
SHA del nuevo canon. Build reproducible y enlaces documentales comprobados.

Benchmark nativo: **36/36 checks y 30 capturas por versión**. Primeros planos:
**32/32 checks y 28 capturas por versión**. Recuperación gráfica: **25/25**.
Los informes no registran errores JS/shader ni peticiones externas. El GLB
actual tiene cero UV colapsadas; su derivado con tangentes conserva el informe
completo de Khronos con cero errores/advertencias, incluidas sus notas
informativas. Estas cifras locales no se atribuyen a una CI todavía pendiente.

## Comprobación heredada detectada por CI

El run de autoría `45559958452` sobre `d85a1f8` falló en dos aserciones de
`human-tangents-integration.cjs`: aún exigían 984 UV degeneradas y 26.064
esquinas válidas del atlas v1. El resultado real era 0 y 29.016. Las otras
tres pruebas de integración aprobaron; la generación posterior del workflow
no se ejecutó por ese fallo. Se conserva el run fallido como evidencia.

El contrato se separa explícitamente por versión de material: v1 mantiene
sus cifras históricas y v2 exige cero fallback, 29.016 esquinas válidas y
normalScale 1. No se calculan los valores esperados a partir del resultado
ni se modifican las tolerancias de tangentes. La misma suite aprueba **5/5 con v2** y **5/5 con el export histórico**.
El trigger de CI incluye ahora el propio archivo de integración. El arreglo
del gate conserva el hash del HTML y la evidencia de runtime de la candidata.

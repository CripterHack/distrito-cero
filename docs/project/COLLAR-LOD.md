# Cobertura cervical de la chaqueta · v0.20.25 · refs #5

La chaqueta LOD2 usaba una reducción de celda de 60 mm que mezclaba superficies
cercanas y contraía las curvas del torso. Aparecían islas adicionales de piel
junto al escote. El cuello LOD2 conserva la corrección de costura de #64;
este cambio afecta a la política de detalle de la prenda.

## Decisión

LOD2 de `jacket` reutiliza la entrada y la key de LOD1. El recurso GPU tiene un
único propietario; personajes LOD1 y LOD2 añaden instancias al mismo lote, cada
uno con su pose y apariencia. No se genera ni registra otra copia de la malla.
Se conservan el reductor, la geometría de las demás partes, LOD0/1, umbrales e
histéresis de distancia, modos de calidad, fuentes, rig, mapas y partidas.

Esta unidad evita la degradación adicional de la chaqueta al pasar a LOD2.
No convierte la fuente o LOD1 en una prenda sin intersecciones. Tampoco cambia
las proporciones para taparlas ni certifica calidad AAA.

## Diagnóstico y alternativas

El source tiene un torso de 15.642 triángulos y un escote abierto separado de
384. La reducción anterior mezclaba doce grupos entre ambos componentes; el
escote quedaba en cinco triángulos. En un vértice representativo, la media lo
movía 43,63 mm hacia otra superficie; en los rayos problemáticos, el cuello
cambiaba ~0,1 mm mientras la chaqueta se alejaba 34,69/54,39 mm.

Se ensayaron alternativas sin modificar el runtime. Separar componentes y
preservar la frontera real mejora los dos píxeles conocidos, pero aún pierde
37/289 anclas de piel cubiertas tanto en LOD0 como en LOD1. Esas dos imágenes
por sí solas habrían dado un falso éxito. La prueba por anclas es direccional;
no mide volumen de intersección ni área visible exacta.

| Alternativa de jacket LOD2 | Triángulos | Alcance medido |
| :--- | ---: | :--- |
| Reducción anterior | 811 | Defecto reproducido |
| Conectividad local y frontera | 980 | Cobertura insuficiente |
| Error a planos tangentes ≤6 mm | 2.901 | Límite numérico, sin aceptación visual |
| Error ≤3 mm | 4.295 | Límite numérico, sin aceptación visual |
| Error ≤1 mm | 7.226 | Límite numérico, sin aceptación visual |
| Reutilizar LOD1 | 2.992 | Malla y recurso existentes |

Los prototipos adaptativos tardaron ~159/164/188 ms en este entorno y requieren
otro algoritmo y buffer. El de 6 mm sólo ahorra 91 triángulos frente a LOD1;
los demás lo exceden. Un límite respecto a planos tangentes no es distancia
Hausdorff ni garantiza separación tras DQ. Los experimentos se conservaron
como evidencia y no se incorporaron al producto.

## Presupuesto

Se añaden **2.181 triángulos por instancia LOD2** respecto a la chaqueta anterior.
El cuerpo LOD2 pasa de 5.965 a 8.146; con el peinado neutro de 960 triángulos,
el total pasa de 6.925 a 9.106 (+31,5 %). LOD0/1 conservan sus recuentos. Son recuentos del LOD normal; los primeros
planos de QA fuerzan sólo el cuerpo y conservan el groom de la fixture.

Se elimina el VBO de chaqueta LOD2 de **155.712 bytes**, su buffer de instancias,
un VAO y una llamada de reducción durante la construcción. El VBO compartido
LOD1 ya existía (574.464 bytes). Los bytes de VBO no son memoria total de GPU.
El coste por frame depende de personajes y hardware; no se atribuyen FPS ni
una mejora universal de rendimiento a compartir recursos.

## Verificación y reproducción

El plan exige referencias congeladas de cuatro perfiles por tres poses, con
LOD0/1 anteriores al candidato. La cohorte usa centros de triángulos originales
de piel en la banda cervical de reposo, con puntos y normales deformados por el
shader real de cada condición. Registrar el conjunto completo cubierto por
LOD0, su deuda hacia LOD1 y el subconjunto cubierto por ambos. No elegir anclas
según los resultados del candidato ni aceptar cohortes vacías.

Además de preservar el subconjunto de referencia, revisar la profundidad de la
piel LOD2 para no aceptar una prenda correcta frente a una piel desplazada.
Las capturas incluyen primeros planos y cuerpo completo; la regresión de nuca
se conserva separadamente. Se verifican actores con LOD mezclados, slots,
recursos compartidos y recuperación WebGL. Las poses son muestras preparadas,
no una partida continua ni aprobación de hardware físico.

La referencia preliminar de v0.20.24 completó 42 capturas válidas, con 44
fallos geométricos reproducidos. Los subconjuntos de cobertura LOD0/1 varían
por perfil/pose (283–370 anclas); no se reutiliza sólo el conjunto neutro.
Se reforzó el productor con un hash independiente de la piel en las 42 vistas,
para impedir que modificarla pueda satisfacer el criterio de la chaqueta.
La referencia preliminar y el productor original se conservaron por separado.

Suite Node completa **707/707** y pruebas dirigidas **34/34**, incluidos siete casos de política/instancing y
recursos. El RED inicial dio dos fallos y dos controles; un replay aislado de
los siete casos contra `2b72a688` da cuatro fallos y tres controles. Build,
release **12/12**, checkout **1/1** y workflow **9/9** aprobados. Benchmark general **36/36** (30 capturas), recuperación WebGL **25/25** y
regresión de nuca **36 controles/33 criterios geométricos**, 16 vistas, aprobados
sobre el HTML final. Exportación de equipos **1/1**, checks de autoría de tenar,
prenda y atlas sin cambios. Exportación humana actual con tangentes: integración
**5/5** y validador **cero errores/cero advertencias**, informe sin truncar.
El contrato del productor pasa **18/18** pruebas. La referencia final conserva
42 capturas válidas (130 guardas) y reproduce 44 fallos geométricos. La candidata
completa **42 capturas, 173/173 guardas y 110/110 criterios geométricos**; la
comparación separada pasa **304/304** controles. Las 24 imágenes LOD0/1 son
idénticas; la geometría de piel es idéntica en las 42 vistas. Se conservan las
3.755 combinaciones ancla/condición cubiertas por LOD0 y LOD1, procedentes de
611 anclas únicas. En los dos rayos originales la chaqueta vuelve a quedar
delante de la piel LOD2: 26,453 mm en nuca y 43,772 mm en perfil.

El conjunto más amplio cubierto por LOD0 contiene 4.596 combinaciones. Sus
pérdidas pasan de 1.365 a 841: se recuperan las 714 pérdidas del subconjunto
LOD0/1, pero **190 combinaciones fuera de él pierden cobertura** que la chaqueta
LOD2 anterior sí daba. El balance mejora en 524 combinaciones, sin mejorar cada
ancla. Es una concesión explícita de reutilizar LOD1, cuya deuda frente a la
fuente permanece; no se oculta escogiendo sólo el subconjunto aprobado.

[Galería y resumen verificable](../../qa/collar-lod-v02025/README.md).
Los informes completos, buffers GPU y 84 PNG originales se conservan en el
paquete de revisión. La CI del nuevo commit sigue siendo un gate separado.

### Residuos registrados

Las sondas sobre la piel realmente reducida conservan **492 resultados sin
impacto de 3.755 combinaciones**, entre 38 y 43 por condición: son desconocidos,
no pruebas de separación. Hay cinco márgenes direccionales negativos de
−0,007 a −0,196 mm. Cuatro pasan de positivo a negativo frente a la chaqueta
anterior y uno tenía resultado desconocido. Por tanto no se afirma que toda
intersección restante sea anterior al cambio.

La auditoría independiente conserva IDs, posiciones y rayos de cámara para
esos cinco casos. No se observaron nuevos puntos de piel visibles en sus pares
recortados: los puntos están ocluidos por prenda u otra superficie de piel en
esas cámaras. Los perfiles y cuerpos completos revisados tampoco muestran
nuevas aperturas. Esta observación acotada no prueba ausencia de colisiones
desde otros ángulos. Permanecen el borde central escalonado propio de LOD1,
las limitaciones faciales de LOD2 y la deuda de cobertura entre fuente y LOD1.

```sh
python3 build.py --check
node --test tests/crowd-garment-lod.test.cjs
python3 tests/collar_lod_qa.test.py
python3 tools/qa/render_collar_lod.py --html index.html --output artifacts/collar-review --label candidate
```

Instalar NumPy y Playwright desde `requirements-dev.txt`, más Chromium de
Playwright o indicar `--browser /ruta/chromium`. Para antes/después, capturar
primero el HTML de `2b72a688` en una salida fresca y usar su informe mediante
`--reference`. La baseline puede completar capturas y retornar 1 por los
criterios geométricos fallidos; no declararla candidata aceptada. Conservar
los mismos inputs/casos/productor. El runtime sigue sin dependencias externas.

HTML SHA256: `81c9f68654e0e14eddb9cfa73f6408038120d87943bb438c7d713adf64859003`.
Source SHA256: `2473fa894a6359a0bd56895018c3da7de15ea65c9e411200cf6481eca63d4984`.
Productor SHA256: `e468485e276f220517b3f0a9150e66492725a0a560a1ea21d01ae016a3ed2531`.
Las capturas previas al commit registran el HEAD base `2b72a688`; los hashes
de entrada identifican el HTML y productor modificados realmente evaluados.

## Dependencias y reversión

[Plan](../../specs/002-character-benchmark/plan-collar-lod.md). Base `2b72a688`
del PR #64, cuya CI aprobó tres workflows y nueve jobs. Depende también del
atlas de #63. La rama nace de master actualizado y añade los prerrequisitos
por fast-forward; el PR apunta a master para ejecutar los gates existentes.
No se ha integrado ni desplegado.

Revertir esta unidad y su versión/build restaura la chaqueta LOD2 anterior.
No migra geometría fuente, rig, mapas ni partidas. No cerrar #5/#6/#7 por esta
corrección; las fuentes, el arte global y el hardware conservan sus criterios.

# Continuidad de la nuca en LOD2 · v0.20.24 · refs #5

La reducción facial de v0.20.23 separaba diez posiciones de autoría coincidentes
a ambos lados de la costura UV posterior. Aunque posición, normal, IDs y pesos
eran idénticos, sus celdas UV producían centroides separados hasta **5,464 mm**.
La abertura tenía 22 bordes en LOD2; LOD0 y LOD1 no la tenían. Con el culling
habitual desactivado se veía la superficie interior a través de ella.

## Cambio acotado

`CrowdGeometry.reduce` incorpora `weldUVSeams`, activado sólo para `face`.
Después de formar los grupos existentes, une los que comparten un vértice con
los catorce atributos geométricos y de rig idénticos bit a bit. Agrega cada grupo
una sola vez y remapea los índices antes del recorte habitual. Las UV se siguen
calculando por isla conectada, sin mezclar cartas del atlas. Diferencias de
normal, orden de joints, IDs de peso cero o pesos impiden esa unión.

La ruta sin opción conserva sus resultados anteriores. En el personaje real,
LOD1 mantiene todos sus bytes y LOD2 cambia sólo 57 esquinas en la nuca; el
desplazamiento máximo respecto al LOD anterior es 4,098 mm. Las fuentes LOD0,
atlas, shaders, rig, animaciones, simulación y partidas no cambian.

| Medida de face | LOD1 | LOD2 |
| :--- | ---: | ---: |
| Triángulos antes y después | 6.229 | 3.645 |
| Bytes del buffer antes y después | 1.195.968 | 699.840 |
| Bordes posteriores antes → después | 0 → 0 | 22 → 0 |
| Triángulos UV degenerados después | 0 | 0 |

La auditoría topológica global conserva 187 aristas no manifold previas; las
aristas de borde globales pasan de 120 a 98. Esta corrección local no convierte
toda la malla en una superficie manifold ni aprueba la anatomía.

## Evidencia del renderer

[Comparación seleccionada y mediciones versionadas](../../qa/lod-seam-v02024/README.md).
La corrida final aprueba **53/53 controles de captura** y **37/37 criterios
geométricos**; el comparador valida **91/91 comprobaciones de procedencia**.
Los 32 PNG son idénticos a los ya revisados antes de reforzar el control de
referencias. Se conservaron ambas corridas; no se sustituyó evidencia histórica.

`tools/qa/render_lod_seam.py` reutiliza la matriz, el stage y el capturador
existentes. Lee el VBO y las posiciones `vWorld` mediante transform feedback
del vertex shader de producción. Conserva material, culling, cámara, reloj,
guardas de simulación/almacenamiento y cero peticiones externas.

Son seis vistas neutras —nuca y perfil en LOD0/1/2— más diez poses cervicales
controladas. Se fijó la región posterior en coordenadas de reposo antes de
comparar; los movimientos no permiten que los vértices escapen de la medición.
La baseline reproduce 13 criterios geométricos fallidos: doce muestras LOD2
con 22 bordes y un rayo que alcanza el interior. El candidato cierra esos
bordes, conserva exactamente las posiciones compartidas después de DQ y
mantiene las cuatro capturas LOD0/1 idénticas píxel por píxel.

El rayo posterior en (362,470) pasa de profundidad 0,907208 m, cara interior,
a **0,783594 m, cara exterior**, dentro de la envolvente LOD0 fijada por nueve
rayos de referencia [0,782396; 0,784371] m. Difiere sólo +0,162192 mm del rayo
central LOD0. Se revisaron visualmente nuca neutra y poses; no se declara una
prueba de animación continua, selección LOD por distancia ni hardware físico.

## Reproducción

Dependencias de desarrollo fijadas en `requirements-dev.txt`: NumPy y
Playwright; Chromium instalado por Playwright o `--browser /ruta/chromium`.
El HTML conserva cero dependencias externas de runtime.

```sh
node --test tests/crowd-seam-continuity.test.cjs tests/crowd-atlas-lod.test.cjs tests/cast.test.cjs tests/human-fidelity.test.cjs
python3 tests/lod_seam_qa.test.py
python3 build.py --check
python3 tools/qa/render_lod_seam.py --html index.html --output artifacts/lod-seam-review --label candidate
```

Para una comparación antes/después, extraer `index.html` de `a72060b`, capturar
primero esa baseline en otra salida fresca y pasar su `report.json` mediante
`--reference`. La baseline completa sus capturas pero retorna **1** por la
regresión geométrica esperada; no tratarla como candidata aceptada. Ambos
informes deben usar el mismo productor, matriz, stage y capturador. La referencia
se valida y sus bytes se verifican al terminar. Nueve pruebas del productor
cubren métricas, referencias vacías/inválidas, baseline RED y cambios de bytes
durante la captura; las regresiones nuevas fallaron antes del arreglo. Sin `--reference`, CI declara
la envolvente del LOD0 del propio build. Las salidas existentes no se pisan.

El job de personajes existente ejecuta el nuevo productor después del benchmark
y conserva sus archivos en el mismo artefacto. No se cambian runners, permisos,
timeouts ni tolerancias del benchmark anterior.

## Verificación complementaria

Suite Node completa **700/700**; selección dirigida **24/24**. Las cinco pruebas
nuevas reprodujeron primero cuatro fallos y una salvaguarda aprobada. Exportación
de equipos **1/1**, contorno tenar **8/8** y binding de prendas **5/5**; los dos
checks de autoría conservan exactamente el SHA de la fuente facial.

El benchmark nativo general aprueba **36/36**, con 30 capturas; recuperación
WebGL **25/25**, ambos sobre el mismo HTML. El primer intento del runner no
resolvió el Chromium local a través de la variable heredada; quedó registrado
como fallo de entorno antes de renderizar. La corrida fresca con `--browser /usr/bin/chromium` es la que aporta estos resultados.

Replay del atlas aprobado; exportador humano **19/19** e integración de
MikkTSpace **5/5**. El GLB original tiene cero errores y un aviso por no incluir
tangentes; el derivado tiene **cero errores y cero avisos**, sin truncamiento.
Su BIN LOD0 de 4.860.080 bytes es idéntico al export final de v0.20.23: catorce
mallas, 49 huesos, once clips, imágenes y materiales. Sólo varían los metadatos
de versión. Esto no prueba la deformación DQ de un visor glTF convencional.

Build determinista, release **12/12**, checkout LF/CRLF **1/1** y contratos del
workflow **9/9**. La CI del PR de esta unidad se registra por separado.

HTML: `50b5123b8dcbe27182e63eab5fe9d2647ddc73c5d080fb21e77adae5cb8f4de1`.
Fuente de build: `3299740ffe90fb6263c5f11a8c3dfbc41b0d7292c8193c65cf088a9991eea9e7`.

## Coste y límites

En este entorno Node 24.22.3, dos calentamientos y seis pares alternados con GC
explícito dieron medias de construcción LOD1 **71,20 → 88,18 ms** y LOD2
**39,32 → 65,53 ms**. Es coste inicial de CPU, no trabajo por frame ni FPS;
los buffers de salida conservan su tamaño. Validar impacto en hardware real.

Persiste la intersección cuello/chaqueta: la prenda existe, pero la piel pasa
por delante tras simplificar. El parche visible bajo el cuello en nuca/perfil
es ese defecto separado. También siguen pendientes revisión artística facial,
cabello, adaptación de los candidatos Higgsfield y rendimiento de dispositivos.
No cerrar #5/#6/#7 ni atribuir calidad AAA a esta unidad.

## Dependencia y reversión

Esta candidata depende del PR #63 en `a72060b`, con tres workflows y nueve jobs
aprobados. La rama nueva parte del master actualizado y añade ese prerrequisito
por fast-forward; el PR usa master para conservar los gates. Integrar #63 primero
reduce el diff sin reescribir historia. No se ha integrado ni desplegado.

Revertir esta unidad, incluida la versión, y reconstruir el HTML restaura la
reducción anterior. No exige migrar mapas, rig ni partidas. El atlas de #63
tiene su [propio contrato y reversión](NATIVE-FACE-ATLAS.md).

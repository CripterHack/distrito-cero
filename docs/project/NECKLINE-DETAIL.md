# Borde lateral del escote · v0.20.27 · refs #5

Un peatón con el cuerpo LOD2, visto en el estudio desde 0,85 m, mostraba piel a través del borde lateral de la chaqueta. En el ancla fuente 9216, la reducción de 27 mm colapsaba dos vértices de cada uno de los triángulos de chaqueta 9815 (torso) y 15887 (tira del escote). Al medir profundidad sobre el eje de cámara en el centro de cada píxel, la prenda anterior quedaba 37,94 mm detrás de la piel LOD2 en la vista posterior y 105,29 mm detrás de perfil. Con la corrección queda 20,80 mm delante en la vista posterior y 18,45 mm delante de perfil. Los dos resultados coinciden con los de la chaqueta fuente frente a la misma piel LOD2. En ambos rayos, la diferencia entre piel LOD0 y LOD2 era inferior a 0,2 mm.

La política aplicada a la chaqueta conserva por esquina las posiciones, normales, UV y datos de rig originales en las celdas de su inserción cervical. En reposo, los centros de esas celdas tienen altura ≥1,45 m y distan ≤0,112 m del eje vertical en (x=0, z=−0,01 m). La selección retiene 3.434 esquinas que corresponden a 637 filas distintas de atributos. Usar el centro de la celda permite compartir los vértices de transición entre caras y mantener el resto de la reducción habitual. LOD1 y LOD2 emplean el mismo buffer y lote de instancias. El asset fuente y las otras partes conservan sus huellas.

## Elección y presupuesto

En las doce combinaciones de perfil y pose se ensayó proteger sólo las celdas de la tira independiente. Ese candidato recuperaba los rayos conocidos pero perdía siete coberturas comunes a la fuente y a LOD1. Con radio de 0,10 m en las celdas de la inserción aún quedaban seis pérdidas respecto a la fuente. La banda seleccionada cubre también la primera hilera del torso. El análisis de aristas confirma que reaparecen las 128 aristas de abertura de la fuente. Las otras 16 aristas abiertas del resultado ya estaban en la malla intermedia anterior.

La primera ronda con 0,110 m recuperó los 85 rayos preseleccionados. Al proyectar los márgenes negativos se encontró otro cambio en el perfil ligero con el cuello girado a la derecha. En la cámara posterior, en (293,536), la prenda quedaba 0,110 mm detrás de la piel y la prenda fuente quedaba 0,028 mm delante de la misma piel. El triángulo 8621 cruzaba el límite de reducción en una esquina cuya celda está a 0,111893 m del eje. Aumentar el radio a 0,112 m conserva esa celda y su simétrica, 118 esquinas y 36 triángulos más respecto a la primera ronda. El test de la cara 8621 falló antes de ese ajuste. La captura corregida en (293,536) devuelve el margen fuente de +0,028305 mm. Al sustituir únicamente la chaqueta por la de LOD0 y conservar todo el cuerpo LOD2, el PNG da exactamente el mismo RGB [123,138,129] en ese píxel. El cuerpo completo LOD0 da [87,122,120]. El centro de píxel de perfil (465,527) conserva la abertura que pertenece a la fuente. [Control de la chaqueta en el renderer](../../qa/neckline-detail-v02027/transition-raster.json).

| Recurso por instancia o malla | v0.20.26 | v0.20.27 |
| --- | ---: | ---: |
| Triángulos de chaqueta LOD1/2 | 2.992 | 3.965 |
| Triángulos del cuerpo LOD1 | 15.829 | 16.802 |
| Triángulos del cuerpo LOD2 | 8.146 | 9.119 |
| Cuerpo y pelo neutro LOD2 | 9.106 | 10.079 |
| Bytes de geometría en el único VBO intermedio | 574.464 | 761.280 |

El incremento es de 973 triángulos por instancia intermedia o lejana y de 186.816 bytes en el VBO compartido. Para un peatón lejano con pelo neutro supone un 10,69 % más de triángulos. En Node 24.22.3 se cronometró sólo el reductor de chaqueta después de dos calentamientos, con seis muestras alternas por política. La mediana fue 63 ms para la política anterior (50–233 ms) y 134 ms para la candidata (69–294 ms), durante otras pruebas simultáneas. Esta construcción se ejecuta al crear los recursos del renderer. La evaluación del tiempo por fotograma requiere hardware físico.

## Referencia y pruebas

La prueba inicial falló porque faltaba el triángulo 9815 en LOD1. Los tests de integración comprueban las tres caras completas y la abertura, el hash del reductor anterior al omitir la opción, los hashes de todas las otras partes, los presupuestos, el lote compartido, la selección por distancia y la liberación de recursos. Las muestras de laboratorio usan el renderer WebGL nativo y el mismo shader que en juego. El comparador externo aprobó 361/361 comprobaciones. Dentro de las doce condiciones, las pérdidas de cobertura frente a la prenda fuente bajaron de 841 a cero sobre 4.596 anclas cubiertas, y las cuatro coberturas adicionales desaparecieron. Los 85 rayos preseleccionados recuperaron la tela por delante de la piel LOD2 con al menos 9,33 mm de separación sobre el eje de cámara.

La separación medida en dirección normal tiene una contrapartida. Sobre las mismas 3.755 anclas anteriores, los márgenes negativos frente a la piel LOD2 pasan de 5 a 20, con 492 sondas indeterminadas en ambas versiones. Sobre las 4.596 anclas cubiertas en la candidata, hay 22 márgenes negativos y 495 indeterminados. El peor margen mide −0,4965 mm. Los 22 también son negativos con la chaqueta fuente y la misma piel LOD2. En el centro inferior de la nuca sigue viéndose una franja estrecha de piel presente en la fuente.

[Resultados, imágenes y limitaciones de la verificación del escote](../../qa/neckline-detail-v02027/README.md). Los informes identifican por SHA-256 el HTML cargado. Se tomaron las capturas antes de crear el commit de la candidata, por lo que el campo de commit registra la base del árbol de trabajo. El registro del [PR #67](../../qa/collar-street-v02025/README.md) conserva el diagnóstico anterior. La pertenencia de un ancla a una superficie cubierta es una medida direccional. La separación completa de todas las superficies y la aceptación artística siguen pendientes.

En la cámara de calle a 1280 × 720, los seis pares de capturas usaron el mismo peatón y la selección de LOD de la partida. Los dos controles LOD0 a 6,10 m coincidieron píxel a píxel. En calidad equilibrada, las capturas a 42,15 m (LOD1) y 50,12 m (LOD2) también coincidieron. En calidad eco cambiaron 28 píxeles RGB a 24,25 m (LOD1) en una región de 10 × 8 píxeles alrededor del cuello del peatón. A 31,20 m (LOD2) ambas imágenes coincidieron. La cámara forzada de 0,85 m muestra el detalle recuperado a una escala mayor. [Informe de calle, cámaras y huellas de los HTML](../../qa/neckline-detail-v02027/street.json).

Para repetir la comparación con v0.20.26, extraer el HTML del arreglo de puerta y usar un directorio de salida nuevo.

```sh
mkdir -p artifacts
git show fd6ed02:index.html > artifacts/v02026.html
DC_QA_BROWSER=/usr/bin/chromium python3 tools/qa/capture_collar_street.py \
  --compare-neckline-detail --before artifacts/v02026.html --after index.html \
  --output artifacts/neckline-street-review
```

[Plan](../../specs/002-character-benchmark/plan-neckline-detail.md). Retirar el cambio de política y reconstruir el juego recupera la chaqueta anterior.

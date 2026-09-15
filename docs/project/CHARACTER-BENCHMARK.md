# Benchmark de personajes · primera unidad técnica de #5

## Propósito y estado

Referencia reproducible sobre el renderer real, no remodelación ni aprobación automática de la anatomía. Esta unidad implementa cámaras, luces, perfiles, poses, medidas y una galería portable. **#5 permanece abierto** hasta revisar la referencia artística y completar los requisitos de autoría/poses que correspondan. #6 no se cierra por tener muñecas matemáticamente próximas a un objetivo.

No cambia `src/`, `build.py`, `index.html`, modelos, partidas o Pages. Los scripts de preparación se cargan sólo en las pruebas. El modo de juego distribuido no descarga esta herramienta.

## Cobertura explícita

`tests/benchmarks/characters.json` define cuatro perfiles (neutral, ligero, robusto y extremo), cuatro cámaras (frente, perfil, tres cuartos y posterior), tres luces y doce poses. La selección `smoke` contiene **30 capturas y 36 comprobaciones**, cubriendo cada eje al menos una vez y los once estilos de cabello. **No es el producto cartesiano completo.**

`full` produce **586 capturas**: 4 perfiles × 12 poses × 3 luces × 4 cámaras, más diez variantes de cabello adicionales. Esta matriz no multiplica los once peinados por cada pose. Son fotogramas preparados, no 586 sesiones ni una verificación temporal de todas las transiciones.

Reposo, marcha, carrera, frenada, giro, agachado, fase aérea y cuello usan la escena de estudio existente. Apuntado, recarga, conducción y entrada utilizan el fondo de ciudad y los métodos reales de equipo/asiento/acceso. El renderer no se reemplaza para dibujar un arma dentro de un estudio que originalmente la omite.

## Comandos

Dependencias sólo de desarrollo: Python, Node y Playwright 1.57.0 con Chromium. En Linux sin escritorio, usar Xvfb.

```sh
python3 tests/character_matrix.test.py
node --test tests/character-stage.test.cjs
xvfb-run -a python3 -m tools.qa.run --suite characters --headed --timeout 900
# Matriz completa bajo un directorio nuevo, fuera del árbol histórico:
DC_QA_HEADLESS=0 xvfb-run -a python3 tests/character_benchmark.py --matrix full --output artifacts/character-full
```

El runner permite `--browser` para un Chromium instalado. El script directo usa `DC_QA_BROWSER`. No se deben reutilizar carpetas de salida ni modificar archivos bajo qa histórico. El workflow `Character reference benchmark` ejecuta smoke en cambios pertinentes y ofrece full por ejecución manual.

## Salidas

El artefacto contiene `report.html`, PNG sin retoque, `art-review.json` y JSON con métricas y checks. Bajo el runner, la galería está en `evidence/v019/characters/report.html`; el resumen del runner contiene commit y run ID. El reporte hijo identifica HTML, matriz y script mediante SHA-256. Su commit puede ser null en la copia de QA sin .git; el commit efectivo está en el manifiesto padre.

Cada imagen registra cámara, luz, perfil, estilo, tiempo, calidad, viewport, buffer real, GPU declarada por WebGL, matrices finitas y errores. Los PNG tienen 720×720; el render interno del perfil balanced puede ser menor y su dimensión se informa por separado. El tiempo de captura no se presenta como frame time del juego.

Las medidas distinguen **pivotes del rig** y **puntos de la superficie canónica**. La banda cervical selecciona vértices originales entre 1.490 y 1.510 m, luego aplica complexión, grosor y ajuste cervical. La pieza face incluye cuello inferior. Ni la distancia entre pivotes ni la caja de esa pieza se etiquetan como medidas clínicas del cuerpo.

Los presupuestos de cada LOD suman por separado cuerpo y geometría de cabello reales. No son mediciones de VRAM o FPS. En el modelo neutral actual, la referencia observada es 89,433 / 19,894 / 6,917 triángulos con corto clásico.

## Separación de estado

Se prepara una simulación independiente, manteniendo intactos el estado serializable de la sesión inicial y el fixture de almacenamiento. El reloj de animación se controla después del arranque y de cargar mapas. El fixture registra callbacks RAF pendientes para cancelarlos de forma determinista, incluso al comparar contra v0.19 anterior al lifecycle nuevo. No desactiva RAF antes del arranque.

Esta suite no verifica persistencia nativa; la suite HTTP `native` cubre ese contrato por separado. No es un playthrough ni una prueba de GPU física.

## Fallos encontrados durante el desarrollo del benchmark

Los primeros tests fallaron porque no existían matriz/medidas; las regresiones de LOD fallaron antes de implementar el cálculo. Un primer arranque anulaba RAF demasiado pronto e impedía iniciar el juego. Otra captura dejaba ejecutar un callback pendiente del HTML original, detectado por el check de no mutación. Se corrigieron los fixtures, sin relajar el check ni modificar gameplay.

El Chromium local sin ventana no proporcionó WebGL2 con su configuración inicial. Se aisló con un canvas mínimo y se ejecutó Chromium con Xvfb y ANGLE/SwiftShader explícito. Un fallo de arranque ahora informa el mensaje del juego en vez de esperar todo el timeout. No se presenta como un fallo del producto corregido.

## Hallazgos visuales y siguiente corrección

En las primeras capturas del HTML original v0.19, `neutral--aim--neutral--front` muestra una deformación amplia en el frente superior de la chaqueta al cruzar el brazo de apoyo. La proximidad de palmas/muñecas pasa, pero **la imagen no aprueba el contacto corporal ni la prenda**. Hay que reproducirlo sobre el HEAD probado y localizar pesos/topología/postura antes de alterar agarres.

La silueta de hombros y la unión superior de la prenda permanecen muy uniformes. Varios peinados largos necesitan revisión en perfil y movimiento. Estos son hallazgos de presentación, no mediciones anatómicas universales ni cambios ya implementados.

La aceptación artística requiere un revisor identificado, decisión y evidencia del hash exacto. `accept_review` valida ese registro y rechaza una aprobación vacía. El archivo generado siempre empieza en pending. No fabricar una aprobación del usuario ni una revisión independiente.

## Pendientes

Revisión artística del benchmark completo, secuencias continuas para transiciones, referencias ampliadas de manos/calzado y validación de recursos editables/licencias. El alcance técnico de este PR no incluye nuevos assets, correctivos de pose, material neutro alternativo, motion capture ni medición en hardware físico.

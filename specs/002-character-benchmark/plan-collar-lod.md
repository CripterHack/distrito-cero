# Contacto de cuello y chaqueta en LOD2 · CHAR-01/02 · refs #5

Estado: implementación y verificación local completas; pendiente de CI/revisión.
Base candidata v0.20.24, PR #64 `2b72a688`.
Sus tres workflows y nueve jobs están aprobados. Nueva rama desde master remoto
`f9454df`, con ese prerrequisito incorporado por fast-forward; no se han integrado
ni desplegado #63/#64. El PR de esta unidad tendrá master como destino para
conservar los gates, declarando ambas dependencias.

## Problema observable

Después de cerrar la costura posterior, persisten parches aislados de piel a
través de la chaqueta en LOD2. El diagnóstico anterior demuestra que ambas
superficies existen, pero su orden de profundidad se invierte. Reproducir sobre
v0.20.24 antes de editar. Los rayos de referencia son (267,547) en nuca y
(447,548) en perfil, con la cámara canónica del primer plano de cuello.
La fuente LOD0 ya tiene exposición central del cuello: no tratarla como una
prenda perfecta ni hacer desaparecer el escote para aprobar una métrica.

## Contrato

- Dada la superficie original del cuello y su prenda, al construir LOD2 se
  deben conservar los detalles topológicos del escote necesarios para evitar
  nuevas islas de piel fuera de la abertura de autoría.
- Fijar la causa de reducción y un caso RED antes de modificarla; evaluar
  conectividad, fronteras reales y colapso de componentes próximos. No inflar
  la prenda arbitrariamente, desplazar el cuerpo ni cambiar materiales/culling.
- Conservar los mapas, fuentes de autoría, rig de 49 huesos, poses, simulación,
  partidas y LOD0/1. La regresión cervical de #64 permanece obligatoria.
- La reducción geométrica existente se conserva. LOD2 de jacket reutiliza la
  entrada/key/malla de LOD1, con un solo propietario GPU e instancing compartido.
  No generar ni registrar una segunda copia de ese buffer. Las demás partes
  mantienen sus LOD, y la selección por distancia/calidad permanece intacta.
- Comprobar actores simultáneos LOD1/2, slots de pose/identidad independientes,
  triángulos contados una vez por actor y reconstrucción tras pérdida WebGL.
  Medir triángulos, buffers y coste inicial; no inventar caras ni ampliar prenda.

## Verificación y límites

Comparar ambas superficies reales después del shader y DQ nativos, con hashes,
matriz/stage/cámaras compartidos y guardas de simulación, almacenamiento, errores
y red. Combinar profundidad y topología de regiones de reposo con inspección
visual; una pareja de píxeles no aprueba el cuello completo. Incluir perfiles
y poses cervicales preparados. No confundirlos con animación continua, selección
LOD por distancia, playtest ni rendimiento en hardware físico.

Ejecutar regresiones dirigidas, suite Node completa, build/release/checkout,
exportación mínima, benchmark y recuperación WebGL. Incorporar el gate al job
existente sólo con alcance y coste medidos. Actualizar documentación y handoff;
conservar evidencia anterior. La aceptación artística global y los candidatos
Higgsfield siguen separados. Revertir la unidad y reconstruir revierte el cambio;
no hay migración de partidas.

## Decisión y alternativas medidas

La chaqueta fuente tiene dos componentes: torso (15.642 triángulos) y escote
(384). La reducción de 60 mm mezcla doce grupos entre ambos y contrae curvas
con residuales de planos de hasta 26,97 mm. Conectividad local y fronteras
preservadas mejoran los dos rayos conocidos, pero aún pierden 37/289 anclas de
piel cubiertas tanto en LOD0 como LOD1. No se acepta esa variante.

Un prototipo de refinamiento adaptativo con errores de plano de 6/3/1 mm requiere
2.901/4.295/7.226 triángulos y ~159/164/188 ms de construcción. El límite de
plano no garantiza cobertura ni distancia Hausdorff. LOD1 ya tiene 2.992
triángulos; el candidato de 6 mm ahorra sólo 91 y agrega otro algoritmo/buffer.

Se conserva la malla existente de LOD1 para jacket en LOD2: +2.181 triángulos
por instancia lejana respecto a 811; elimina el buffer anterior de 155.712 bytes
más su construcción, sin añadir un solver. La verificación GPU decide si esta
política satisface la regresión; la elección no equivale a aceptar el arte ni
el rendimiento físico. Los prototipos quedan sólo como evidencia, fuera del
runtime. La cobertura fuente y la deuda LOD1 se informan por separado; no se
promete reparar intersecciones previas de la fuente o de LOD1 en esta unidad.

## Resultado de la unidad

[Contrato y resultados](../../docs/project/COLLAR-LOD.md): Node 707/707,
contrato QA 18/18, benchmark 36/36, recuperación 25/25 y regresión de nuca
aprobados. Comparación de collar: 42 vistas, 173 guardas, 110 criterios
geométricos y 304 comprobaciones comparativas aprobadas. LOD0/1 y piel intactos.

La cobertura direccional de referencia se conserva; no equivale a separación
global. Se registran 492 sondas desconocidas y cinco márgenes negativos menores
de 0,2 mm (cuatro nuevos, uno antes desconocido), sin puntos nuevos visibles en
las cámaras inspeccionadas. El rendimiento físico y la aceptación artística
siguen pendientes. La CI se vincula al commit exacto en el PR de revisión.
La pérdida total de cobertura fuente baja de 1.365 a 841 combinaciones, pero
190 fuera del subconjunto común LOD0/1 pierden cobertura antes disponible.
Este intercambio se conserva en la evidencia y la siguiente revisión.

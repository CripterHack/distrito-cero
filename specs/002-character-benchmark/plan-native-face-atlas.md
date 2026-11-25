# Atlas facial nativo y transición cervical · CHAR-05/06 · refs #5

Continuación de la receta portable del PR #63. Se adapta el recurso canónico
al atlas sin triángulos UV colapsados, conservando la geometría, el rig de 49
huesos, las partidas y el HTML autónomo. La integración se conserva sólo tras
pruebas de materiales, exportación y comparación en el renderer de producción.

## Contrato

- Hornear la mezcla cervical existente sobre posiciones de reposo originales,
  verificadas contra el exportador. Conservar el color de la cara superior.
  La antigua fila UV .095 deja de ser una coordenada válida de pigmento en el
  atlas nuevo; el shader lee el color ya mezclado.
- Reproyectar normales con fuerza .30 una sola vez; el nuevo mapa utiliza
  fuerza 1. En runtime, convertir la base tangente derivada a una base
  ortonormal con orientación y reflexión explícitas, y fallback finito para
  derivadas singulares. Verificarlo con normales analíticas en WebGL real.
- Cuantizar sólo las UV de face al formato nativo uint16. Conservar todos los
  demás bytes de geometría y pesos. Las UV cuantizadas deben seguir siendo
  invertibles en cada triángulo.
- Mantener los grupos originales de simplificación LOD mediante procedencia
  de las celdas UV originales. Conservar posiciones, normales, pesos y
  triángulos LOD1/2; promediar las nuevas UV sólo dentro de cada grupo e isla
  conectada por aristas posición+UV. No interpolar entre islas separadas.
- Mapas embebidos WebP sin pérdida de 1024² (color), 512² (normal) y 256²
  (rugosidad). Reducir color en espacio lineal y normales como vectores.
  Hornear una máscara explícita de cobertura blanca y extender sólo texeles
  completamente cubiertos sobre el fondo/bordes antes de reducir. Conservar
  pigmento negro legítimo; el color no decide qué texel tiene cobertura.
  No añadir solicitudes ni dependencias de runtime. Registrar coste de memoria.
- El exportador actual consume los mapas canónicos embebidos, convierte V y
  verde y usa fuerza normal 1. Las recetas y fuentes históricas se conservan.
- Registrar insumos, hashes y receta reproducible; rechazar fuentes alteradas,
  datos inválidos o sobrescrituras de históricos. `--check` no muta salidas.

## Verificación y reversión

Reproducir regresiones antes de cambiar código: base tangente con UV sesgadas,
exportación que lee mapas antiguos y normalScale .30, cambio de geometría LOD
por el atlas. Tras corregir, ejecutar suites dirigidas, Node completo, build,
release y exportación. Comparar poses y luces del benchmark nativo, revisar
primeros planos cervicales y recuperación de contexto. Conservar informes y
limitaciones; las capturas preparadas no acreditan FPS físicos ni calidad AAA.

La versión de producto cambia; los esquemas de partida permanecen intactos.
La reversión debe retirar conjuntamente UV, mapas, metadatos, shader y versión,
y reconstruir el HTML. No revertir sólo un mapa ni reescribir evidencia previa.

# Continuidad cervical en LOD · CHAR-01/02 · refs #5

Estado: implementado y verificado localmente; integración pendiente. Unidad dependiente del atlas de PR #63, cuya CI en
`a72060b` aprobó los tres workflows y nueve jobs. La rama de esta unidad parte
de master actualizado e incorpora ese prerrequisito por fast-forward. El PR
declara la dependencia de #63 y enlaza la comparación desde `a72060b`; mantiene
master como destino para ejecutar los gates existentes. Integrar primero #63
reduce automáticamente su diff a esta unidad, sin reescribir commits.

## Defecto reproducido

La simplificación de face conserva celdas UV diferentes a ambos lados de una
costura. Diez posiciones de autoría coincidentes, con normales e influencias
idénticas, terminan en centroides separados hasta 5,464 mm en LOD2. La región
cervical posterior tiene cero aristas abiertas en LOD0/1 y 22 en LOD2.
Desactivar culling no lo repara: puede mostrar la superficie interior a través
de la abertura. La exposición de piel sobre la chaqueta es otro defecto y
requiere un diagnóstico de superficies independiente.

## Contrato y aceptación

- Dado un vértice coincidente en posición, normal, IDs y pesos (incluido su
  orden), si sólo difieren sus UV, el LOD de face debe mantener una única
  posición e influencias de salida. Verificar reposo y deformación cervical.
- Añadir `weldUVSeams` opcional a la reducción. Conservar los clusters
  existentes, unir sólo los que comparten ese vértice exacto y remapear índices
  antes de aplicar el recorte existente. Mantener las UV separadas por isla.
- Activar la opción únicamente para face. La ruta sin opción conserva su
  salida histórica; normales o influencias distintas no autorizan la unión.
- Exigir 22→0 aristas abiertas nuevas en la región posterior fijada por el
  diagnóstico, cero UV colapsadas, valores finitos y pesos normalizados. No
  añadir caras de relleno ni cambiar shader, exposición o culling para ocultarla.
- LOD0, fuentes canónicas, mapas, rig de 49 huesos, poses y partidas permanecen
  intactos. Registrar triángulos, buffers y coste de construcción de LOD.

## Verificación

Primero conservar el caso RED. Después probar la equivalencia histórica sin
opción, separación de UV, controles negativos y malla real con movimientos y
perfiles. Comparar nuca y perfiles de LOD0/1/2 con el mismo renderer, luces,
cámaras y reloj preparados. Conservar guardas de simulación, almacenamiento,
errores y red. Un primer plano de LOD forzado no acredita selección por
distancia ni rendimiento de hardware físico.

Ejecutar suite Node, build, release, exportación de equipos y pruebas gráficas
afectadas. Publicar versión y HTML coherentes, documentación, evidencia y PR.
La aprobación artística del conjunto y el cruce de prenda se registran aparte.
Revertir opción/activación y reconstruir el HTML revierte esta unidad; no hay
migración de assets ni de partidas.

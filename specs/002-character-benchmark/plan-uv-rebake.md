# Reparametrización y reproyección portable · CHAR-05/06 · refs #5

Estado: derivado técnico implementado; integración y arte pendientes. Continuación del PR #63.
El atlas canónico contiene 984 triángulos UV degenerados; el diagnóstico
anterior no los repara. Esta unidad produce un derivado de autoría con cartas
invertibles y texturas reproyectadas antes de plantear una migración nativa.

## Contrato

La referencia es el humano exportado actual con tangentes explícitas. En los
984 triángulos colapsados ese derivado ya define un fallback documentado.
No se presenta ese fallback como la única base correcta ni como el sombreado DQ.

Blender 4.3.2 genera cartas nuevas únicamente para face y reproyecta color,
ORM y normales. El color/ORM se hornean como emisión sin luces. El shader
fuente usa los T/N/W explícitos para evitar que Blender invente otra base sobre
las UV colapsadas. El mapa normal de destino incorpora la fuerza .30 de origen
y se usa con fuerza 1. Se conserva un registro de estos cambios de material.

El empaquetador consume UV por esquina, conserva exactamente posición, normal,
articulaciones y pesos por esquina, y añade mapas/atributos al binario original.
No reexporta el esqueleto desde Blender. Nodos, skins, escenas y once clips
se conservan; sólo face recibe un nuevo material. Nuevas tangentes MikkTSpace
y validación oficial se calculan para el derivado, nunca se heredan del origen.

## Aceptación

- Rechazar hash de entrada distinto, receta incompleta, UV no finitas o
  colapsadas, formato no soportado y destinos que sobrescriban fuentes.
- Preservar bytes originales y cada atributo no UV/tangente por esquina.
- Auditor UV sin cartas colapsadas y validador completo sin errores/advertencias
  después de regenerar tangentes; no alterar severidades o descartar informes.
- Comparación portable antes/después con la misma cámara, luces y pose, en
  reposo y giro cervical. Mapas de normales visualizados separadamente.
- Guardar hashes, herramientas, imágenes y límites. Cero errores numéricos
  no equivale a aceptación artística.

## Separación del runtime y reversión

El renderer nativo usa mezcla cervical, coordenada fija .095 para pigmento y
una base cotangente derivada en pantalla. Copiar este atlas al runtime sin
adaptar esos contratos cambiaría el aspecto. Por ello esta unidad deja
src, HTML, versión, partidas, canon e históricos intactos.

Blender, Three.js y las herramientas de baking/validación son de autoría.
El visor local no forma parte del HTML ni realiza peticiones externas.
Sus capturas no son evidencia de FPS físicos, renderer nativo o CCD.

Revertir herramientas/tests/documentación retira la unidad sin migración.
Integrar en el runtime requiere otra unidad con el benchmark nativo, la
adaptación del shader y la revisión de materiales.

## Evidencia de implementación

Repack: seis casos RED → seis GREEN. Node completo: 686/686. Blender: 2/2,
con error angular de 0.303° y control negativo de signo verde. Visor: cuatro
fallos de aceptación reproducidos → 4/4 métodos aprobados; conserva errores de
consola/shader y hashes finales de entradas. Build, release12 y exportación
equipos1 aprobados. El resultado y los límites de la comparación están en
[UV-REBAKE](../../docs/project/UV-REBAKE.md); las cifras locales no se atribuyen
a un run remoto de CI.

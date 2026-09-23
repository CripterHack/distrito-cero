# CHAR-06 · Tangentes portables

Base c49ed085. Ejecución secuencial mediante executing-plans, revisión propia.

## Contrato y decisión

La exportación actual pasa Khronos pero omite TANGENT en face, único material
con normalTexture. Es reproducible localmente: 0 errores y una advertencia
MESH_PRIMITIVE_GENERATED_TANGENT_SPACE. No suprimir el aviso ni retirar el mapa.

Crear una variante derivada en un directorio nuevo, conservando el GLB de entrada.
Usar mikktspace 1.1.1, dependencia de autoría MIT, no parte del runtime. Expandir
índices a esquinas para MikkTSpace, convertir handedness glTF con w *= -1 y volver
a indexar por (índice original, cuatro componentes de tangente). Separar costuras
sin promediar bases incompatibles. Copiar todos los atributos de cada esquina,
incluidos JOINTS_0/WEIGHTS_0, y conservar íntegro el prefijo binario de entrada.
Los demás meshes, nodos, clips, materiales e imágenes no cambian.

No alterar los mapas/UV ni la fuente
humana. Entradas no soportadas (sparse, morph, UV transformado, datos no finitos,
índices/rangos inválidos) deben rechazar antes de crear salida. El comando no es
un importador universal de glTF. Sólo admite el contrato del exportador actual.

## Pasos verificables

1. Escribir tests sin dependencia de red del adaptador y observar fallo por
   implementación ausente. Cubrir copia byte a byte, costura reflejada, índices,
   rango, valores no finitos y generador inválido sin mutación.
2. Implementar tools/export_human_tangents.cjs con API pura addTangents y CLI
   INPUT_DIR OUTPUT_DIR MIKKTSPACE_MODULE_DIR. Preservar hashes de procedencia,
   artefactos previos y rechazo de destinos versionados/directorios existentes.
3. Ejecutar tests de integración con MikkTSpace real y el GLB real. Verificar cada
   esquina y sus atributos antes/después, y Khronos completo sin filtros.
4. Integrar el paso en human-export.yml, manteniendo permisos contents: read,
   versiones fijadas y reportes completos. El artefacto conserva original y derivado.
5. Actualizar STATE/HANDOFF/CURRENT-HUMAN-EXPORT, publicar PR desde master sin
   workflow auxiliar, revisar diff, CI del HEAD exacto y artefactos antes del merge.

## Revisión y límites

Especial atención a espejo de UV, signo W, vértices compartidos, alineación de
buffers, atributos normalizados y preservación de muestras de animación.
Khronos verde no equivale a equivalencia DQ/LBS o aprobación artística global.
El prefijo binario conservado puede dejar accessors viejos no usados, explícitos
en el informe. No se ocultan avisos informativos ni degenerados históricos.

Dependencias recuperadas por workflow auxiliar de lectura porque DNS local no
resuelve GitHub/npm. Se comprueban SRI del registro y SHA-256. El helper no se
integra en master. Reversión: retirar derivador/tests y paso del workflow, sin
cambiar partidas, HTML ni recursos históricos. #5/#6/#7 mantienen sus criterios.

Fuentes: glTF 2.0, sección Geometry de Khronos, y README de
https://github.com/donmccurdy/mikktspace-wasm (convención de signo y esquinas).

## Hallazgo y decisión tras prueba real

El GLB tiene 984 triángulos con determinante UV exactamente cero. En 2,761 de
sus esquinas MikkTSpace devuelve el eje X por defecto, no perpendicular a N.
No se incrementó el umbral de ortogonalidad. Para las 2,952 esquinas de esos
triángulos sin parametrización invertible se construye una base ortonormal
determinista proyectando el eje menos paralelo a N, con handedness +1. Se
cuentan ambas magnitudes en el manifiesto. Los otros 26,064 resultados se
conservan exactamente como MikkTSpace con conversión W. Los mapas UV no quedan
reparados por este fallback y no se declara equivalencia al detalle nativo.

Tres nuevas regresiones observaron RED antes de implementar esa política.
Nueve tests de adaptador y cinco de integración real aprobaron. La variante
local conserva los 4,088,108 bytes previos y añade 366,312 bytes, con 612
duplicaciones de vértice para bases distintas. Khronos: 0 errores, 0 advertencias
y 20 mensajes informativos conservados. No son veinte defectos nuevos: incluyen
accessors históricos sin uso y degenerados previos fuera del mesh modificado.

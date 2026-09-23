# Tangentes explícitas para la exportación portable

Refs #5 / CHAR-06. Base `c49ed085fe3270c42b284867575c5abc2251fa69`, producto 0.20.3.
[Contrato de exportación](CURRENT-HUMAN-EXPORT.md), [plan](../../specs/002-character-benchmark/plan-portable-tangents.md).

## Decisión y alcance

La salida original de PR #37 conserva su GLB y su reporte oficial de cero errores
con una advertencia de tangentes generadas por el visor. Se entrega además una
variante `*-tangents.glb` en un subdirectorio nuevo, con procedencia y validación
propias. No se reemplazan recursos históricos ni el renderer nativo.

El adaptador usa `mikktspace@1.1.1` como herramienta de autoría MIT. Expande
índices a esquinas, genera tangentes y convierte W para glTF según el paquete.
Reindexa por índice original y base tangente exacta. Los vértices compartidos con
bases distintas se separan; cada esquina conserva exactamente sus posiciones,
normales, UV, índices de articulación y pesos. Los buffers originales permanecen
como prefijo idéntico. Nodos, skins, once clips, mapas y materiales se conservan.
Los accessors originales que dejan de usarse no se borran ni se ocultan al validador.

## UV degeneradas, no una reparación invisible

El material face contiene 984 triángulos con determinante UV exactamente cero.
En la prueba inicial, Mikk devolvió un eje por defecto no perpendicular a la normal
en 2,761 esquinas y la exportación fue rechazada. No se relajó la ortogonalidad.

Únicamente para las 2,952 esquinas de esos triángulos sin base UV invertible se
proyecta el eje menos paralelo a la normal y se normaliza, con W final +1. El
manifiesto identifica la política y cuenta las excepciones. Las otras 26,064
esquinas conservan exactamente el resultado del paquete, salvo el signo W.
**No son UV reparadas ni una garantía de detalle de normal map equivalente.**
La revisión visual portable y la deuda de parametrización siguen pendientes.

## Reproducción

```sh
npm install --prefix artifacts/gltf-tools --ignore-scripts --no-audit --no-fund --no-package-lock --save-exact gltf-validator@2.0.0-dev.3.10 mikktspace@1.1.1
python3 tools/export_current_human.py --output artifacts/human-export
node tools/qa/validate_glb.cjs artifacts/human-export artifacts/gltf-tools/node_modules/gltf-validator
DC_MIKKTSPACE_MODULE=artifacts/gltf-tools/node_modules/mikktspace DC_TANGENT_INPUT=artifacts/human-export node --test tests/human-tangents-integration.cjs
node tools/export_human_tangents.cjs artifacts/human-export artifacts/human-export/tangents artifacts/gltf-tools/node_modules/mikktspace
node tools/qa/validate_glb.cjs artifacts/human-export/tangents artifacts/gltf-tools/node_modules/gltf-validator
```

El directorio de salida debe ser nuevo. Se rechazan destinos versionados, hashes
incorrectos, dependencias de otra versión y layouts no soportados. No es un
importador glTF universal: sparse, morph, transformaciones de UV y entradas no
finitas se rechazan. Los tests de integración requieren la dependencia real y se
ejecutan explícitamente en human-export, sin skips. El core ejecuta los nueve
contratos del adaptador sin instalar librerías de autoría.

## Evidencia local y verificación remota

531/531 Node y 14/14 Python del exportador aprobados, sin omitidos. Nueve tests del
adaptador y cinco de integración con el paquete y GLB reales. Se cotejan todos los
atributos de cada esquina, W, norma, ortogonalidad, reproducción y no mutación.
Se observaron RED de implementación ausente, UV degeneradas y política sin declarar.

GLB local original SHA-256 `aa92936d122d1a331f9b88b3727061aa6a653d03a3eb73b880e14b178020abb8`.
Derivado `542080dfa0e77a164c444d9da0f86cb455b40cfb643910911bcd12ef6e09471e`.
Khronos original: 0 errores, 1 advertencia, 14 informativos. Derivado: 0 errores,
0 advertencias, 20 informativos, reporte íntegro. Incluye degenerados históricos
y accessors sin uso; cero advertencias no significa geometría perfecta.
Se preservan 4,088,108 bytes binarios y se añaden 366,312. Face pasa de 4,893 a
5,505 vértices por 612 separaciones de bases, sin cambiar sus 9,672 triángulos.

El workflow conserva original y derivado con sus dos validaciones. La CI del PR
requiere cero errores y advertencias del derivado sin cambiar severidades. Sus
resultados y hashes remotos se registran por HEAD; los hashes locales no prometen
igualdad entre toolchains. Permisos contents: read, sin commits, refs o Pages.

## Continuidad y reversión

No cambia src, HTML, versión, guardados, munición, anatomía o licencia propia.
DQ nativo y skinning lineal portable siguen teniendo límites. Revertir esta unidad
retira adaptador, tests y pasos adicionales, no requiere migrar partidas.
#5 sigue con aprobación artística/procedencia global, #6 con revisión de acciones,
vídeo y coste por actor/LOD y #7 con recorrido/playtest/hardware.

Fuentes técnicas: [glTF 2.0](https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html),
[MikkTSpace WASM](https://github.com/donmccurdy/mikktspace-wasm).

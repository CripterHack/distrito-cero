# Recursos de Distrito Cero

Este directorio conserva insumos de autoría, bases geométricas, exportaciones GLB y referencias de QA de varias versiones. **El juego vigente es v0.20.5**, no la versión indicada en el nombre de cada recurso.

El índice rector está en [docs/project/ASSETS.md](../docs/project/ASSETS.md). La geometría humana del runtime está embebida en `src/hero-asset.js`, junto a materiales y generación de peinados en sus módulos. `dc019-equipment.glb` es el kit de equipamiento de esta base. Los GLB humanos anteriores son referencias/exportaciones históricas, no un exportador de todas las funciones del creador actual.

Para construir el juego: `python3 build.py`. Para reconstruir el kit actual: `python3 tools/export_contact.py`. No ejecutar una receta de otra versión sobre las fuentes actuales sin verificar su contrato y su insumo.

Preservar `anatomy-source/`, los baselines y las atribuciones hasta demostrar que una migración puede reproducir los assets sin ellos. El HTML no solicita esos archivos por red. No se distribuyen fuentes tipográficas. La política de licencia global pendiente está en [LICENSING](../docs/project/LICENSING.md).

La nueva superficie palma/pulgar está en el recurso canónico y su receta `tools/refine_thenar.py`. Los GLB humanos anteriores no se presentan como una exportación de v0.20. El kit `dc019-equipment.glb` se regeneró en v0.20.2 por la culata del rifle y se actualiza en v0.20.3 por las culatas de SMG, escopeta y sniper. El rifle y las demás familias conservan su geometría, al igual que el modelo humano.

## Extensión 0.20.3

El kit actual conserva 13 equipos y 9,888 triángulos. Se revisan sólo las culatas cosméticas de SMG, escopeta y sniper. Rifle y demás familias conservan sus geometrías. [Contrato de autoría](../docs/adr/0004-longarm-family-docks.md). Las exportaciones anteriores mantienen su carácter histórico.

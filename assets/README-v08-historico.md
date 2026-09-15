# Recursos v0.8 · Presencia

## Archivos actuales
`dc08-hero-native.glb`: geometría nativa de v0.8, 17 huesos y cinco clips de estudio procedurales. `dc08-coupe-native.glb`: kit de geometría del coche ya presente en Horizonte, exportado nuevamente. Los coches del juego incluyen además piezas procedurales y estado de daño.

Regenerar con `python tools/export_presence_glb.py`. Los materiales portables del GLB aproximan los shaders del juego. Parpadeo, objetivos de manos en acceso, variaciones de NPC y secuencias de extracción están en el runtime y no son clips del GLB.

`hero-native-report.json` detalla cada componente construido por `tools/build_hero_v08.py`. La malla, párpados y ropa revisados son originales y procedurales. No hay escaneo, textura fotográfica, MakeHuman importado ni nuevo GLB remoto integrado en esta entrega.

## Historial
Los `dc05-*`, `higgsfield-body.json`, la referencia pequeña y `source/` son insumos históricos. No representan la geometría revisada del protagonista v0.8. La receta original de v0.5 tenía escenas de autoría en Higgsfield: protagonista `bea56607-3eea-4526-abc9-b546a4717f10` y coupé `b423a0c7-1fe4-4a56-a0bd-4cd654a18258`. Esta versión utiliza el código y los buffers nativos documentados, no una nueva exportación del servicio.

La consulta de recursos externos durante esta iteración no produjo bytes utilizables. Nada se integra a partir de una transferencia truncada ni se presenta como fotogrametría. El juego no necesita conectarse al servicio de autoría.

Los shaders y utilidades de modelado son parte del código local. No se distribuyen archivos de fuentes tipográficas ni librerías externas de runtime.

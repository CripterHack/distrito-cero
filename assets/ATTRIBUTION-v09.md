# Procedencia de los recursos de v0.9

## Cabeza anatómica

**MakeHuman Community, HM08 basemesh y target adulto. CC0.** Se reutiliza únicamente un subconjunto de la cabeza, no un humano completo desnudo. Los recursos artísticos son datos, no una biblioteca de runtime. La cabecera del OBJ declara la liberación CC0 en septiembre de 2020 y reconoce a Data Collection AB, Joel Palmius y Jonas Hauquier.

Fuentes oficiales consultadas el 11 de septiembre de 2026:

* https://static.makehumancommunity.org/makehuman/faq/are_makehuman_files_free.html
* https://raw.githubusercontent.com/makehumancommunity/makehuman/master/makehuman/data/3dobjs/base.obj
* https://raw.githubusercontent.com/makehumancommunity/makehuman/master/makehuman/data/targets/macrodetails/caucasian-male-young.target

Huellas de la descarga original:

* Base: `8e761e6624b8f54536409135d1636da63b32486a90d4897f84e121d144f6fb4c`.
* Target: `70e228ba7164737dae664454394536fc5935fa48d333c1a97d77e2dc6eacc5f5`.

Modificaciones: aplicación del target, selección de caras sobre el corte del cuello, conversión a escala métrica, simetría soldada, unión inferior de cuello, asignación de pesos al esqueleto nativo, nuevas UV cilíndricas y cuantización de coordenadas. El rostro no representa a una persona real identificada ni procede de un escaneo realizado para este juego.

## Piel

**Aksel Skin, autor Mindfront, CC0**, según el catálogo oficial del paquete `skins02`.

* https://static.makehumancommunity.org/assets/assetpacks/skins02.html
* https://files.makehumancommunity.org/asset_packs/skins02/skins02_cc0.zip

Archivos originales seleccionados: `Aksel_Skin_diffuse.png`, `Aksel_Skin_NRM.png` y `Aksel_Skin_SPEC.png`.

Modificaciones: reproyección de UV hacia el atlas cilíndrico del juego, conversión de orientación de normales, derivación de rugosidad desde el mapa especular, reducción de tamaño, compresión WebP y reparación local de píxeles de desoclusión del horneado. Una zona orbital defectuosa se corrige con simetría de la zona limpia y borde difuminado. No se presenta como una captura fotográfica nueva, una textura generada por Higgsfield o una calibración física exacta de piel.

## Transporte y reproducción

La descarga y primer horneado se ejecutaron en el sandbox de Higgsfield. El archivo recibido se conserva intacto en `assets/anatomy-source/compact.bin`, de 40,130 bytes.

SHA-256: `4bdcd196342f4ec13e3f616deffa7176ca59cee8fabc891d7339f9161c6ecccf`.

Cabecera: cuatro longitudes `uint32` little-endian. Luego una malla delta-comprimida con LZMA y tres imágenes WebP. Las longitudes son 16768, 19442, 3744 y 160. La malla contiene 2174 vértices y 2106 quads de una mitad simétrica, con posiciones `int16` en pasos de 0.1 mm y deltas de índices. Los scripts de construcción decodifican estos insumos sin conectarse a internet. LZMA y las herramientas de horneado no se distribuyen dentro del runtime.

El horneado a partir del OBJ completo fue una operación de autoría remota. La construcción offline reproducible parte de este insumo versionado, no afirma regenerar desde cero la reproyección del paquete original de 73 MB. Los originales reducidos no se sobrescriben al reparar el mapa.

## Resto del personaje

Chaqueta, pantalones, manos, ojos, cabello, calzado, esqueleto y animación conservan modelado/código procedural original de Distrito Cero con los cambios documentados. No se han añadido assets de pago, paquetes con permisos no verificados ni archivos de fuentes tipográficas.

CC0 no impone atribución obligatoria. Se conserva esta información voluntariamente para mantener trazabilidad y no atribuir autoría falsa. La licencia de los recursos de terceros no cambia automáticamente la del resto del proyecto.

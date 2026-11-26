# CHAR-01/02 · escote de la chaqueta a media y larga distancia

El informe del PR #67 identifica dos rayos que atraviesan la piel LOD2 junto al borde lateral. El triángulo fuente 9216 permite reproducirlos en las vistas de nuca y de perfil. La fuente viste ese punto. El modelo reducido pierde las dos caras de prenda que debían taparlo.

1. Comparar cada superficie por separado, fijando la piel LOD2 y las cámaras anteriores. Exigir la conservación de las dos caras de prenda, con todos sus atributos por esquina, antes de tocar la selección de LOD.
2. Proteger celdas completas de la abertura y la unión con el torso. Las caras que conectan con las celdas reducidas deben seguir compartiendo sus vértices. Mantener la malla de chaqueta compartida por los dos niveles de detalle.
3. Comparar las 611 anclas fuente y las doce condiciones de perfil/pose. Conservar todas las coberturas que proporciona la prenda fuente y todas sus aberturas muestreadas. Repetir los rayos de #65 y #67, incluir una cámara de calle con selección de LOD por distancia y revisar las imágenes del modelo.
4. Medir el coste de geometría y comprobar el aislamiento de recursos y actores. Los controles de LOD0 y de todas las partes distintas de la chaqueta se conservan.

La reversión del cambio de política y su build recupera los buffers de v0.20.26. La simulación y el formato de guardado usan sus esquemas vigentes. [Contrato y reproducción](../../docs/project/NECKLINE-DETAIL.md).

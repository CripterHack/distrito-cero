# Constitución corporal · v0.10

## Objetivo
Continuar sobre la fuente verificable de v0.9. Conservar la cabeza anatómica y sus tres mapas, la campaña, el territorio y la ocupación. Mejorar las proporciones de todo el cuerpo vestido, manos, calzado y respuesta del esqueleto. No sustituir el juego por una escena de muestra ni calificarlo como AAA terminado.

## Decisiones
La fuente de la iteración interrumpida sólo está disponible como imágenes. Se reconstruye el incremento sobre v0.9, en una copia aislada, sin sustituir los originales. La anatomía de manos y prendas de este incremento será de autoría paramétrica local. Se mantienen las atribuciones de la cabeza HM08. No se incorpora una transferencia remota no verificada.

La alternativa de cambiar de motor o utilizar un personaje de red se descarta para preservar el HTML sin dependencias. Tampoco se sigue añadiendo volumen a las primitivas rígidas. Se crea una mano continua con uniones interdigitales, pulgar opuesto y tres articulaciones por dedo, sobre un esqueleto compartido ampliado. Los primeros 17 índices permanecen estables.

## Unidades y pruebas
1. Registrar baseline, crear tests fallidos de esqueleto, dedos, apoyos, paleta y geometría.
2. Revisar clavículas, hombros, codo, muñeca, cadera y rodilla. Especificación compartida entre autoría y runtime para impedir desalineación.
3. Hornear prendas continuas con menor volumen excesivo, perfiles de pecho/espalda diferenciados, transición axilar, cintura, muslo, pantorrilla y tobillo. Nuevos zapatos con suela plana y horma, no elipsoides.
4. Construir manos conectadas y pesos con flexión individual de falanges. Estados relajado, carrera, carga y conducción. Actualizar dedos después del contacto IK de muñecas.
5. Paleta GPU de tamaño derivado del esqueleto, mismo resultado en color, sombra y NPC. Mantener límites de actores y geometría compartida.
6. Exportar GLB con esqueleto actualizado y clips de estudio. Validar rangos, pesos, normales, poses y reconstrucción determinista.
7. Revisar capturas reales frontal, perfil, carrera, agachado, mano abierta/cerrada, reparto, conductor y extracción. Reejecutar regresiones, almacenamiento y sectores. Entregar archivos, comparación y límites.

## No incluido
Mocap, mano fotogramétrica, contacto físico individual por dedo, musculatura volumétrica, tela física, física de ragdoll, nuevas misiones o cambios de captura policial. La mejora se juzga con capturas del renderer, no con recuentos de polígonos ni ilustraciones.

## Cierre verificable

Las siete unidades se implementaron y pasaron sus pruebas definidas. La geometría final, la revisión de capturas y los límites están en `VERIFICACION.md`. Los estados de máxima flexión mantienen limitaciones visuales explícitas, no se consideran contacto físico completo.

# Distrito Cero v0.5 · Superficies y movimiento

Base verificada: v0.4, 96 pruebas de lógica, 9 de septiembre de 2026.
Autorización: continuar implementando y puliendo los modelos con Higgsfield, conservando cero dependencias de runtime.

## Alcance del incremento

1. Modelar y descargar recursos originales mediante Higgsfield/Blender: carrocería con pasos de rueda y normales suaves, parabrisas curvo, detalles mecánicos; personaje vestido con proporciones, pesos y superficies deformables.
2. Convertir glTF en la construcción, no usar librerías remotas ni descargas durante el juego. Conservar procedencia, geometría fuente, transformaciones y materiales. Validar buffers, índices, normales, pesos y presupuesto.
3. Integrar deformación del personaje por pesos en GPU y esqueleto independiente del render, reutilizando velocidad real, postura, salto, agarre y estados existentes. Mantener fallback procedural, sin confundirlo con mocap o rig de nivel AAA.
4. Mejorar el shader de materiales con BRDF microfacet GGX, Fresnel, energía difusa/especular, rugosidad diferenciada, detalles finos y reducción de aliasing. Material de pintura, piel, tejido, caucho, corteza y follaje. No prometer trazado de rayos o fotografías.
5. Sustituir copas esféricas por troncos/ramas y grupos de hojas con viento limitado, manteniendo el pivote de caída y las reglas de interacción. Compartir geometría y limitar detalle por distancia.
6. Revisión visual real del juego en reposo, andar, llevar objetos, coche limpio y dañado, árbol intacto y caído. Regresión de policía, guardados y controles. Mostrar límites y recuentos de pruebas realmente ejecutadas.

## Límites

Campaña y física no se reescriben. No despliegues ni suscripciones. La sesión no va a entregar fotogrametría, mocap ni un mundo íntegramente hiperrealista. No se incorpora un asset sin descargarlo, convertirlo y verificar su presencia en el renderer. No se garantiza rendimiento a partir de SwiftShader.

## Resolución de la implementación

Los puntos 1 y 2 se adaptaron por una limitación de transferencia: las escenas de Higgsfield quedaron comprometidas, pero no se descargaron al runtime sus GLB nuevos. Se implementaron reconstrucciones nativas de las mismas recetas y se documentó la diferencia de topología. No se presentaron como importaciones directas.

Implementados los puntos 3 a 6, con estas precisiones: 17 huesos y pesos en GPU, GGX aproximado sin iluminación basada en cubemap, microdetalle procedural sin texturas fotográficas, dos LOD de follaje y revisión por fotogramas reales más renderer continuo. Se añadió el encuadre de primer plano a modo foto.

Se exportaron adicionalmente dos GLB nativos para edición. El del personaje contiene cinco clips procedurales de estudio. La evolución a escaneo de materiales, malla humana de producción, rig facial, mocap con retargeting y contactos sobre terreno arbitrario sigue pendiente. No se considera terminado el plan integral de versiones posteriores.

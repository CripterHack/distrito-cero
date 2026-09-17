# Unidad #21: referencia ocular del avatar al apuntar

Base: `687ead2`, v0.20.0. Unidad parcial de #6 / CONTACT-03 para pistola y revólver ficticios del juego.

Dos pruebas sobre la base reproducen 51.39 mm de error en neutral y 103.12 mm en cuello corto/elevación negativa. La cámara, el ojo articulado y el objeto usan referencias distintas.

## Plan

1. Referencias de arte comprobadas contra la malla real del avatar y los objetos.
2. Usar la paleta de cabeza ya evaluada, sin deformar cara/cuello ni otro cálculo de pose.
3. Alinear el montaje rígido transversalmente al eje visual, con mezcla acotada en apuntado, equipamiento, recarga y retroceso. El alcance bilateral tiene prioridad.
4. Conservar contactos relativos, longitudes de huesos, reglas y esquemas de guardado.
5. Validar neutral (<3 mm) y matriz moderada (<10 mm): cuello [-1,0,1], agachado [0,1], elevación [-.30,0,.30]. Capturas comparables y continuidad a 1/60.
6. Regresión completa, versión 0.20.1 y documentos. Revisar PR y exigir CI verde antes del merge autorizado. Verificar master y Pages antes de cerrar #21.

## Límites

Referencias exclusivamente visuales del juego. No óptica física, cambio de rig, primera persona, alineación de objetos largos o simulación biomecánica. #5/#6/#7 siguen abiertos. No alargar brazos o mover palmas en relación al objeto para ocultar el defecto.

## Hallazgos de implementación

La primera mezcla desactivaba la alineación al disparar y hacía bajar 44.53 mm la boca del objeto. Se reemplazó por proyección sobre el marco sin retroceso y rotación del impulso alrededor del agarre, con test específico.

La base de equipamiento ya movía el montaje 63.85 mm por paso de 1/60. El nuevo gate separa movimiento total heredado (<75 mm), corrección nueva (<15 mm) y recarga (<30 mm). No se alteran pruebas antiguas ni se oculta esa diferencia. El correctivo se aplica antes del límite de alcance.

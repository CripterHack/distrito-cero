# Contorno de la unión entre palma y pulgar

Unidad parcial del issue #6 sobre master `ef905ece47bc8901c28c381ef081486e72fa8730`. Conserva los contactos de manos, las animaciones y el correctivo de Actions de #17. No cierra #5, #6 o #7.

## Defecto y evaluación

Las pruebas digitales anteriores elegían vértices por su influencia de huesos. La zona donde se mezclan palma y pulgar quedaba parcialmente fuera. El nuevo helper usa una banda geométrica fija, con 806 puntos izquierdos y 803 derechos, sin filtrar por peso: modificar un peso no puede hacer desaparecer el defecto de la prueba.

Dos regresiones iniciales reprodujeron una penetración aproximada máxima de 3.113 mm bajo el apoyo delantero del fusil y de 3.596 mm en una pieza extraíble sostenida. La referencia se midió sobre la piel DQ del modelo y proxies independientes de las piezas, no sólo en pivotes.

Un intento de ampliar la influencia del pulgar resolvía el contacto, pero introducía pliegues y movimientos de la superficie de hasta unos 22 mm en las poses inspeccionadas. Se descartó. No se incorpora ese cambio de pesos ni un nuevo pivote.

## Cambio de autoría

La almohadilla volar procedural estaba demasiado llena en la zona compartida con los apoyos. Se reduce suavemente hasta 4 mm en su profundidad transversal, en ambas manos. La corrección se desvanece antes de muñeca, dorso, uñas y dedos distales. No cambia las coordenadas verticales o longitudinales, los UV, los pesos, los huesos, los contactos ni la topología. La mano no se desplaza como un bloque para salir del objeto.

Las normales usan la inversa transpuesta del mismo mapa suave que mueve los puntos. Su determinante analítico es positivo (>0.538), y la cuantización conserva los vértices únicos. El cambio está horneado en el recurso. No añade cálculo de piel, búsqueda, caché o colisiones por fotograma, ni dependencias del juego.

Sólo cambia la parte `skin` del recurso humano y sus metadatos. Los demás materiales, prendas, rostro texturizado, uñas, cabello y equipamiento conservan sus buffers. Dentro de `skin`, únicamente las filas de la semilla dispersa pueden variar, en posición y normal.

## Reproducción y protección del recurso

`assets/thenar-contour-source.json` conserva las filas originales en un bloque comprimido acotado. Se comprueban rig, conteo, duplicados, procedencia y cambios ajenos; no se sobrescribe silenciosamente una edición posterior. No se guarda otra copia completa del modelo.

```sh
python3 tools/refine_thenar.py --check
python3 tests/thenar_contour.test.py
python3 tools/rebind_garment.py --check
node --test tests/thenar-surface.test.cjs
python3 build.py
python3 -m tools.qa.run --suite thenar
```

Omitir `--check` regenera el correctivo desde sus filas originales, no lo aplica acumulativamente. Se mantiene la reconstrucción de prendas. Los GLB humanos de versiones anteriores siguen siendo exportaciones históricas; esta unidad actualiza el recurso canónico y el HTML, no reescribe aquellos archivos.

## Pruebas y alcance

Nueve tests Node cubren superficie completa de la banda, tres apoyos delanteros, seis piezas sostenidas, ambas manos en armas cortas, otras poses, transformaciones y desplazamiento <=4 mm tras el skinning. Ocho tests Python protegen autoría, normales, semilla, costuras, simetría e idempotencia.

La suite gráfica tiene quince comprobaciones y once capturas. Sus medidas usan las matrices del renderer que dibujó el personaje. La comparación con el HTML anterior conserva cinco fallos de contacto esperados. El umbral nuevo es 1 mm; no se relajan los existentes de dedos, pulgares o manos.

Las imágenes emplean cámara y reloj preparados. No son una prueba de FPS ni una partida completa. El almacenamiento gráfico es fixture; las pruebas HTTP nativas se ejecutan aparte. Consultar el PR/Actions del commit exacto para sus resultados, no repetir cifras históricas como actuales.

## Límites

Es un pulido localizado de contorno, no una mano nueva o una aprobación hiperrealista. No hay autocolisión completa, simulación muscular ni control de todos los pliegues en agarres extremos. La cohorte no cubre cada triángulo de la mano. Ojo/mira, fases intermedias y otras zonas mixtas mantienen sus requisitos propios.

No cambia munición, física, salud, esquema de partidas, configuración de Pages o dependencias. La reversión sólo requiere devolver recurso, generador y build al commit anterior, sin migrar datos.

## Preservación del apoyo palmar

La regresión original de superficie neutral detectó que el primer correctivo de contorno alejaba la piel del ancla medida. Se añadió un área central preservada con transición suave. El test original de 2 mm permanece intacto y vuelve a pasar junto al criterio nuevo de 1 mm de penetración. No se movió el ancla ni se relajaron tolerancias.

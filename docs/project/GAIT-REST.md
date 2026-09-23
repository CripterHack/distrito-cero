# Frenado de marcha lenta · v0.20.4

Refs #6. Base `a7c13a82e27d1bd7728570de3eb6e0b6306163a6`, que integra PR #38.
Corrección de presentación nativa, no cambio de física, anatomía o guardados.

## Fallo reproducido

La grabación de subida, recarga, agachado, marcha lenta y bajada de las cuatro
familias largas mostró un hundimiento del personaje al terminar el movimiento.
La posición física y la altura de cámara permanecían estables: el descenso venía
de la raíz del rig, no de teletransporte, culata o cámara.

En `NaturalMotion.gait`, la frecuencia de paso ya se atenúa por `weight` al
aproximarse al reposo. La amplitud `speed / hz * duty`, limitada a 0.86 m,
conservaba entonces una excursión demasiado grande. `foot` atenuaba inclinación
y elevación, pero no el desplazamiento longitudinal. El ajuste de suelo del rig
intentaba alcanzar esos pies y bajaba la raíz.

Tres pruebas fallaron antes del cambio: un pie a 0.03 m/s retenía z=0.43 m,
el barrido de fase rebasaba el apoyo aceptado y la secuencia nativa registraba
`rootY=-0.5735982762684599` en el fotograma 97, a 15 capturas/s.

## Corrección acotada

Se multiplica z del pie por la envolvente de marcha existente. Para velocidades
con peso completo, desde 0.65 m/s, el cálculo original no cambia. No se cambian
cadencia, frecuencia de simulación, velocidad física, colocación de cámara,
longitudes óseas, clamps del rig o tolerancias de contactos. La corrección usa
una multiplicación por pie, sin búsquedas, estado persistente o dependencias.

Cinco regresiones cubren fase/velocidad cerca de reposo, altura de raíz, secuencia
nativa al detenerse, trayectorias anteriores a velocidad normal y lectura pura.
536 pruebas Node completas aprobaron, cero fallidas/omitidas/canceladas/todo.
Los tres tests iniciales tienen RED conservado. La CI del HEAD final y los
resultados gráficos se registran en el PR, no se heredan de v0.20.3.

## Comparación de movimiento

El protocolo usa la simulación y el renderer del juego, semilla 1337 y estado
inicial aislado. Ejecuta 60 pasos de simulación/s y codifica 15 fotogramas/s:
120 fotogramas por equipo, ocho segundos, sin interpolar imágenes. Aim hasta
6.5 s, recarga nativa a 1.4 s, agachado 4.5–5.15 s y avance lento 5.35–6.15 s.
La cámara sigue la posición real. Cada fotograma verifica palmas/segmentos,
ausencia de disparos involuntarios y preservación de partida/Storage activos.
Es una escena preparada con GPU software, no un playtest humano o medida de FPS.

El registro baseline guarda huellas de sus 480 imágenes codificadas y conserva
36 PNG originales para cotejo. Las películas contienen los 480 fotogramas. La
revisión visual por hojas de contacto es parcial: 17 fotogramas por arma, no
la afirmación de revisar manualmente todos los fotogramas. El muestreo de
superficies es una vez por segundo, no una validación continua de colisiones.

## Lo que no se resuelve

El mismo baseline detecta penetración muestreada de culata/chaqueta de 15.77 a
20.41 mm en guardia/recarga. Es un pendiente distinto de #6: no se cambia el
montaje o la geometría para aprobar esta corrección de raíz. Dos ensayos de
traslación de objeto fallaron y fueron retirados antes de este cambio.
No se declara aprobación global de animación, anatomía, todos los navegadores,
GPU física o autocolisión. #5 y #7 conservan sus gates propios.

## Reproducción y reversión

```sh
node --test tests/gait-rest-transition.test.cjs
node --test tests/*.test.cjs
python3 build.py --check
python3 tests/release_build.test.py
```

Revertir la modificación de `src/character-motion.js` junto con la identidad de
versión, HTML y build-info asociados. Ninguna migración o borrado de partidas.
Las fuentes, logs y videos de antes/después se entregan con su procedencia.
[Estado](STATE.md), [handoff](HANDOFF.md), [QA](QA.md).

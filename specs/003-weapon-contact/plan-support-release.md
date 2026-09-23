# CONTACT · Continuidad al liberar y recuperar apoyo

Base `bfa26cd629afbc5a4295d8afdbbf833cddd587c2`, v0.20.4. Continuación de #6.

## Problema y contrato

La marcha nativa reproduce dos discontinuidades distintas del hundimiento ya
corregido en #39. El pie que deja su ancla salta a la trayectoria procedural y
la raíz deja de exigir alcance en cuanto ese pie abandona el suelo. En el
siguiente contacto, el alcance vuelve a aplicarse de golpe. Casos medidos a
60 muestras/s: +109.59 mm al despegar y -84.91 mm al apoyar.

Conservar física, velocidad, cámara, huesos y longitudes, inputs y partidas.
Mantener los apoyos plantados y las trayectorias de pie a envolvente completa.
La presentación debe transportar suavemente el desfase del último apoyo hacia
la trayectoria de balanceo y exigir alcance también durante el balanceo.
No usar un filtro de cámara/raíz que esconda pies inalcanzables.

## Unidad acotada y pruebas

1. Reproducir ambos bordes con el rig real y la secuencia de simulación nativa.
2. Escribir pruebas RED para continuidad de raíz, liberación de ancla y alcance.
3. Conservar un residual transitorio por pie dentro de MotionTracker y hacerlo
   desaparecer durante el balanceo. No guardarlo en la simulación ni serializarlo.
4. Compartir ese objetivo entre alcance de raíz e IK del pie. No cambiar clamps.
5. Comprobar apoyo, pose sentada/aire, reinicio, idempotencia y traslación/rotación.
6. Ejecutar Node/Python/build, comparar movimiento del renderer canónico y revisar
   Actions del HEAD exacto antes de integrar. Verificar master/Pages aparte.

Alternativas descartadas: suavizar sólo rootY deja extremidades inalcanzables;
retirar anclas pierde el apoyo fijo; cambiar velocidad/dimensiones altera gameplay.
Revisión propia, no independiente. No cierra penetración de culata ni #5/#7.


## Decisiones durante ejecución

El residual por sí solo elimina el teletransporte del pie pero no la recuperación
rápida de la raíz. Aplicar alcance sólo al objetivo instantáneo tampoco anticipa
el descenso del siguiente talón. Las variantes intermedias fallaron el test de
30 mm por paso y no se publican como solución.

Decisión: extraer groundTargets como único muestreador compartido por tracker y
rig. Añadir anticipación del techo de alcance del próximo talón a lo largo del
balanceo y suavizado únicamente ascendente, limitado por min al techo exacto.
Esto conserva las anclas, la longitud de piernas y la física. Tiene coste de
unos pocos muestreos de la curva de pie por actor, sin búsquedas o solver nuevo.
No equivale a una medición de coste por LOD/GPU física.

El objetivo de anticipación usa la raíz antes del término de vuelo procedural.
Tomarlo después introducía una discontinuidad de carrera y la regresión de los
bordes lo rechazó. El criterio no fue relajado.

Validación de lógica completada: 543/543 Node, 7/7 regresiones nuevas, sin skips.
La evidencia gráfica canónica y la nueva CI se registran en SUPPORT-RELEASE y el
PR de la unidad. No heredar la aprobación remota de #39.

# Continuidad del apoyo dinámico · v0.20.5

Unidad acotada de #6, base `bfa26cd629afbc5a4295d8afdbbf833cddd587c2`.
[Plan](../../specs/003-weapon-contact/plan-support-release.md), [estado](STATE.md),
[handoff](HANDOFF.md). No vuelve a implementar el ajuste de marcha lenta de #39.

## Causa y corrección

El tracker fija la posición horizontal del pie durante apoyo. Al despegar,
la implementación anterior descartaba esa ancla y saltaba directamente a la
curva procedural. Además, el límite de alcance de la raíz sólo se aplicaba
mientras el pie estaba en contacto. Liberarlo podía subir la raíz de golpe y
el siguiente talón podía hacerla bajar otra vez. La reproducción nativa a
60 muestras/s midió +109.59 mm al despegar y -84.91 mm al apoyar. Una liberación
sintética con desfase de ancla produjo 97.46 mm de desplazamiento discontinuo.

`MotionTracker` conserva un residual horizontal y angular del último apoyo.
Desaparece con una curva quintica de velocidad/aceleración nulas en sus extremos,
sin mover el ancla mientras está plantada. El progreso de retirada no retrocede.
El siguiente contacto, teletransporte, aire, asiento o acceso descartan ese estado.

`SkinRig.groundTargets` centraliza los objetivos que consumen el tracker y la
pose. Exige alcance de ambos pies, también durante el balanceo, y anticipa el
techo de alcance del siguiente talón. El tracker suaviza sólo la recuperación
ascendente y la limita con `min` al techo geométrico. La pose vuelve a comprobar
ese techo antes del IK. No se alargan piernas para compensar un filtro.

Son cambios de presentación dentro del sistema existente. No cambian velocidad,
posición física, inputs, cámara, munición, guardados, rig, mallas o geometría de
equipo. La memoria extra vive en el tracker acotado por actor, nunca en partidas.
Las curvas nominales de pie y el arreglo de envolvente de #39 permanecen.

## Regresiones y verificación local

Tres nuevos requisitos reprodujeron RED antes de modificar producción. Las
variantes intermedias que sólo transportaban el ancla o limitaban el objetivo
instantáneo seguían fallando la continuidad vertical. Se conservaron esos fallos.
La anticipación calculada después del término de vuelo produjo otra discontinuidad
de carrera; el test de borde la rechazó y el origen de anticipación se corrigió.
No se cambiaron umbrales ni se retiraron tests para obtener GREEN.

La suite final ejecutó **543 tests Node, todos aprobados**, cero skips, canceladas
o todo. Incluye siete nuevas regresiones: ambos bordes de apoyo, liberación de
ancla desplazada, doce marchas/frenadas nativas, residual monótono y retirada,
reinicios, transformación del mundo, pureza y longitudes. Los 89 tests Python del
core vigente también aprobaron, junto con autoría, build y exportación del equipo.
El GLB del equipo permanece idéntico. Los tests de checkout usan sus repositorios
temporales internos, no fabrican la historia del proyecto.

El barrido numérico final mantuvo un máximo de 19.04 mm por paso a 60 muestras/s
en las doce secuencias de aceleración/parada. A 30 y 15 muestras/s, los máximos
fueron 36.80 y 72.67 mm por muestra. No son el mismo intervalo temporal y no se
presentan como una aceptación universal de 30 mm para cualquier frecuencia.
El límite del test nativo es 30 mm por paso a 60 Hz.

## Evidencia gráfica y procedencia

La comparación utiliza los HTML canónicos anterior y nuevo, sin sustituir
módulos de producción en memoria. Simulación a 60 Hz, renderer a 30 muestras/s,
semilla 1337, rifle, escena aislada y la misma cámara relativa a la trayectoria
física. Son dos recorridos de aceleración/frenado por versión. Storage fixture,
Chromium/Xvfb/SwiftShader: no es persistencia HTTP ni rendimiento de GPU física.
Las cuatro secuencias completaron 282 capturas y frames codificados en vídeo,
con todos sus hashes verificados. Se revisaron visualmente 52 frames seleccionados,
no cada uno. La posición física, velocidad, fase, reloj y cámara coinciden
exactamente entre ambas versiones. No hubo excepciones, errores GL ni solicitudes
externas en los informes. Las palmas y segmentos conservan sus criterios.

| Secuencia a 30 muestras/s | Máximo salto de raíz antes | Después | Error máximo de alcance después |
| :--- | ---: | ---: | ---: |
| Liberación, throttle 0.6 | 95.74 mm | 29.71 mm | 0 mm numérico |
| Contacto, throttle 1 | 147.33 mm | 36.80 mm | 0 mm numérico |

El segundo recorrido tenía hasta 63.60 mm de objetivo de pie fuera de alcance.
Se conserva ese hallazgo en el informe anterior. Estas cifras no son precisión
física ni una revisión exhaustiva de anatomía. La nueva CI del HEAD exacto se
registra por separado en el PR.

Base HTML SHA-256:
`dde3ddf57f9387db14c634bb6fd34806add814b3f5e2d71f9fcaf7bec1aa4e21`.
Nuevo HTML:
`4307c76139bc4f4b8178a16792ecb6c490bd1b0633d98a4a4a86336036cf3641`,
8,869,123 bytes. Fuente:
`c24ebe1d3d15e9fd80f649c7ec70e9d0f5b57ab2eab618d9259f7ba203dd2e92`.

El snapshot local proviene de Pages 10754299290 con digest verificado, no de un
checkout Git: GitHub no resolvió DNS desde el laboratorio. El workflow y atributos
omitidos por Pages se recuperaron y cotejaron por blob. No se publica historia
local sintética. Un eventual helper de reconstrucción almacena sólo blobs desde
un padre remoto real y se excluye del árbol de producto y de sus permisos normales.
Una primera ejecución Node completa fue interrumpida por el presupuesto de llamada;
sólo la repetición completa de 543 tests cuenta como aprobación.

## Reproducción, coste y límites

```sh
node --test tests/support-release.test.cjs
node --test tests/*.test.cjs
python3 build.py --check
python3 tests/release_build.test.py
python3 tools/export_contact.py
python3 tests/contact_exports.test.py
```

El muestreo añade trabajo constante por actor y memoria transitoria acotada por
el tracker existente, no búsqueda por fotograma ni otro solver. Falta una medición
física de coste por actor/LOD. Ejecutar los workflows de WebGL, HTTP, benchmark y
exportación actuales antes de integrar y verificar master/Pages por separado.

No corrige la penetración de culata/prenda durante guardia o recarga, ni acredita
colisión completa, todos los cambios de dirección, anatomías o frecuencias.
La revisión es propia, no independiente. #5/#6/#7 conservan sus criterios pendientes.
Revertir fuentes y HTML/version/build-info asociados, sin migrar o borrar partidas.


## Fallo del helper conservado

La primera reconstrucción auxiliar, run 35881784473, falló antes de aplicar el
parche porque checkout era superficial y HEAD^ no existía. No se almacenaron
blobs ni se ejecutó Node en ese intento. La revisión recupera la historia real,
comprueba ascendencia y conserva todas las verificaciones de bytes y de Node.
El workflow auxiliar y su permiso de almacenamiento de objetos no se integran.

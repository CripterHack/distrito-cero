# Cruces medidos de equipamiento

## SMG ↔ revólver desde recarga · árbol 0.20.18

[Plan](../../specs/003-weapon-contact/plan-smg-revolver-reload.md). Base integrada
#54, d50a60665638f43076b85739205d59c8ab2c1741. Se retira sólo la exclusión de
recarga activa/visible, preservando el rechazo de un tercer objeto mostrado.
Se reutilizan captura de cuerpo/dedos/pieza, retorno de 0.90 s, arco de 0.12 m
y caché canónica, sin modificar gameplay, munición, rig o geometría.

Nueve regresiones fallaron en el snapshot base: siete de ruta y dos de caché.
Los tests existentes ahora cubren ambos sentidos desde siete fases, selector
congelado, retorno/reselección, acciones prioritarias, movimiento y restore.
No se descartan los anteriores casos de tres selecciones lógicas. El revólver
se observa por su cuerpo, no por una pieza articulada ausente del renderer.

La cobertura dirigida es 192 selecciones y 456 poses de culata. Conservar
criterios de paso preparado <30 mm, contactos <12 mm y penetración muestreada
máxima de 2 mm. La aceptación numérica no certifica toda la malla, colisión
continua ni manipulación física del equipo.

Sight conserva los 84 checks y catorce secuencias de #54 y añade diez checks,
dos recargas, al mismo catálogo y tercer job: total 94 =40 +26 +28. Se mantienen
61 estados por secuencia, capturas, cinco guardas por partición y límites
1800 s/productor, 40 min/job, sin nuevo runner. Resultados concretos, revisión
propia, CI y merge se registran en el PR vinculado desde
[issue #6](https://github.com/CripterHack/distrito-cero/issues/6).

Las secciones siguientes conservan evidencia histórica de sus versiones,
no son una ampliación pendiente de esta unidad ni pruebas de su HTML.

## SMG ↔ revólver libre · árbol 0.20.17

[Plan](../../specs/003-weapon-contact/plan-smg-revolver-free.md). Base integrada
#53, 6ba8b86c6e18b160588caf75ecdb24c7e64f078f. La única ampliación es el cambio
libre SMG/revólver. CaptureSwitch reutiliza la pose/pieza mostradas, 0.90 s
cosméticos y el montaje existente. Recargas activas, piezas retornando y
tercer objeto mostrado siguen excluidos en esta pareja. Las acciones reales
no esperan al montaje y la caché canónica permanece acotada a cuatro perfiles.

Siete fallos dirigidos observados en la base: ambas direcciones, selector,
prioridad/presencia de captura, marcha y dos comparaciones de caché. Dos
expectativas de QA fallaron antes de añadir la cobertura. El primer ajuste de
0.08 m no cumplió el criterio de chaqueta en SMG→revólver a guardia baja,
frame 27, distancia −0.004067746185254382 m. Se midió el arco de 0.12 m con
las cajas verificadas de la propia geometría SMG, sin relajar −2 mm.

Los bucles existentes agregan ocho casos libres a los 128 anteriores, cuatro
configuraciones en cada dirección. Se conservan pruebas de selector congelado,
reversión, locomoción, longitudes, prioridad y restore. La caché fría/inicializada
se comprueba en procesos distintos, sin precalentar las suites normales.

El productor gráfico conserva los 76 checks y doce casos de #53. Añade ocho
checks y dos casos libres al job existente sight-revolver-reload (18), cuyo
nombre histórico se mantiene por compatibilidad. Los otros grupos siguen en
40 y 26. Catorce secuencias de 61 estados, cinco guardas comunes bloqueantes,
1800 s/productor, 40 min/job y mismo número de jobs. Más casos no demuestra
menor coste total. La CI/revisión/merge reales se registran en el PR vinculado
desde [issue #6](https://github.com/CripterHack/distrito-cero/issues/6).


## Rifle ↔ revólver desde recarga · árbol 0.20.16

[Plan vigente](../../specs/003-weapon-contact/plan-rifle-revolver-reload.md).
#52 integró el cambio libre sobre la caché de #51. Ahora se elimina únicamente
la exclusión de recarga/pieza retornando, manteniendo excluido un tercer modelo
mostrado. Captura/montaje/retorno de 0.90 s y arco de 0.12 m existentes,
sin otro solver, caché, tracker, reloj, rig o geometría.

Siete regresiones extendidas fallaron antes de habilitarlo, luego 20/20
pruebas dirigidas aprobaron. Los mismos bucles cubren 128 casos dirigidos
(cuatro parejas × cuatro configuraciones × ocho estados), 304 poses de
culata, selector congelado, reselección durante retorno, prioridad y restore.
Caché fría/inicializada comparada en procesos independientes para ambas
parejas de rifle/arma corta, libre/recarga. No se precalienta QA.

Máximos palmares dirigidos por paso preparado de 60 Hz para rifle→revólver
26.652 mm y revólver→rifle 18.765 mm. Mínimo combinado muestreado −0.353 mm,
conservando −2 mm. Los puntos del revólver se observan sobre su cuerpo
realmente dibujado, no sobre un cargador que no renderiza.

El mismo productor sight añade dos secuencias de recarga. Se conservan los
66 checks anteriores y se añaden diez en un job disjunto: total 76, doce
secuencias de 61 estados y cinco guardas comunes bloqueantes contadas una vez.
No se elevan 1800 s/productor o 40 min/job. Presupuesto agregado mayor.

Los resultados completos de renderer, CI, revisión y merge se registran en
[issue #6](https://github.com/CripterHack/distrito-cero/issues/6) y el PR vinculado.
No atribuir evidencia histórica a este HTML. Las acciones reales siguen
inmediatas, sin cambiar munición, reglas, disponibilidad o partidas. No se
acredita continuidad de todos los cortes prioritarios, toda la malla/CCD,
FPS físicos ni una animación mecánica certificada del cilindro del revólver.

## Registro del cambio libre · PR #52

Integrado en d25baffca0f22e60a001f8f7f6e81ac8877cb9eb, producto 0.20.15.
El primer arco de 0.08 m falló a −4.068 mm contra chaqueta. Se reutilizó
0.12 m sin relajar el criterio. Verify del PR y push aprobaron seis jobs,
277 WebGL, 80 HTTP y 36 benchmark por conjunto. [Cierre y límites](https://github.com/CripterHack/distrito-cero/pull/52).
Su siguiente diagnóstico de recarga motivó esta unidad, no una repetición
del cambio libre ni de los arreglos de caché o scheduling anteriores.

## Registro histórico de rifle ↔ pistola · PR #49

La siguiente descripción corresponde al alcance y evidencia original de #49,
no a nueva cobertura ni a una candidata pendiente. #50 particionó su QA y
#51 corrigió la caché. Las cifras históricas no se suman a pruebas actuales.

**Base integrada:** `613c16495d79e009587c56593ebe9c5a48591406`, PR #48.
[Plan](../../specs/003-weapon-contact/plan-cross-family-handoff.md),
[SPEC-003](../../specs/003-weapon-contact/spec.md), CONTACT-04/05 e issue #6.

## Causas reproducidas y alcance

captureSwitch sólo admitía dos armas con dock o dos sidearms. Rifle ↔ pistola
perdía la pose anterior al seleccionar, tanto libre como durante recarga. Al
permitir esa pareja apareció un segundo corte: actor condicionaba la coordinación
al arma lógica nueva, por lo que tronco/cabeza abandonaban la pose de rifle. Los
ángulos de dedos se mezclaban, pero no amount, usado también por el giro lateral
del pulgar. La igualdad inicial de las 49 matrices descubrió esa discontinuidad.

Se admite sólo esta pareja, en ambos sentidos, reutilizando la captura de UI,
el montaje y 0.90 s de presentación. actor toma la coordinación de la pose
mostrada y grip mezcla amount junto a los ángulos ya interpolados. No se añade
un solver, un modelo simultáneo, un reloj o un tracker alternativo.

La prueba de superficies rechazó el primer arco: chaqueta a −8.024 mm en una
pose de salida de recarga. No se amplió la tolerancia de −2 mm. El mismo arco
frontal, con valor cero en ambos extremos, gana 4 cm sólo para esta pareja
(0.12 m frente a 0.08 m). Una reversión rápida conserva el arco capturado; otras
parejas no se habilitan ni se ajustan sin pruebas propias.

La simulación selecciona/cancela de inmediato. El renderer devuelve el cargador
antiguo a su asiento antes del reemplazo único y deja libre la mano de apoyo.
Es una devolución cosmética, no una animación mecánica certificada de reinserción.
Disparo y nueva recarga prevalecen; no se retrasan para ocultar discontinuidades.
No se cambian disponibilidad, munición, geometría, huesos, anclas o partidas.

## Regresiones y evidencia local dirigida

Las cuatro pruebas iniciales fallaron contra la base auténtica antes de tocar
runtime. La ampliación a todas las matrices produjo otros tres fallos por el
pulgar. La nueva prueba de culata falló con la primera implementación. Estos
fallos y sus correcciones se conservan como pasos distintos; no afirmar que
los siete tests finales fallaron íntegramente contra la base.

Siete tests vigentes: dos direcciones × cuatro configuraciones × ocho estados
(libre y siete fases de recarga), 64 casos con 72 pasos de 1/60 s. Además,
selector congelado, reversión, restore, prioridad de acciones, marcha con
MotionTracker y exclusiones. Criterios: salto inicial <1e-5 m, matrices iniciales
<1e-5, paso palmar y de pieza <30 mm, targets <12 mm, longitudes invariantes,
munición constante y cargador asentado antes de mostrar el siguiente modelo.

En la ejecución dirigida local, máximo palmar 26.550 mm rifle → pistola y
28.240 mm pistola → rifle. La culata se muestrea sólo cuando el renderer muestra
un rifle: 152 poses, mínimo −0.353 mm en las superficies de cara/chaqueta
seleccionadas, dentro del límite −2 mm. Esos valores no prueban separación
positiva universal, toda la malla o detección continua de colisiones.

## Renderer y CI

Se conserva el bucle/cámara de sight y sus 40 checks. Se agregan rifle → pistola
y su inversa, libres y a 46% de recarga: 18 comprobaciones, total contractual
58. Cada secuencia usa la tecla real y observa antes, frame cero y 60 pasos
preparados, nueve PNG y hashes por secuencia. crossFamilyCases guarda palmas,
matrices iniciales, transformación de pieza, munición, draw único y superficies
de culata del modelo realmente mostrado, no del seleccionado lógicamente.

Los intentos locales completos Node anteriores terminaron por límite de
proceso, sin resumen final: no se contabilizan como aprobados. La nueva corrida
completa y las suites de navegador/Python deben registrarse por separado en el
PR del HEAD exacto. No reutilizar evidencia anterior como aceptación nueva.
Los presupuestos de CI y tolerancias del producto no cambian.

## Límites y reversión

Otros cruces, herramientas/pesados, suavidad de acciones prioritarias y todas
las anatomías/giros siguen pendientes en #6. #5 conserva arte/materiales/UV y
procedencia; #7 playtests humanos, recorrido y hardware. Software GPU no acredita
FPS físicos, coste por actor o estándar AAA. No se generan assets nuevos.
Revertir fuentes, tests, docs, identidad y build juntos, sin migrar partidas.

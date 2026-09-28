# Cruces medidos de equipamiento

## Rifle ↔ revólver libre · candidata 0.20.15

Base integrada #51 `17f6086`, caché canónica de dedos corregida. Se habilitan
ambos sentidos libres mediante el montaje existente. Sin nuevo solver, tracker,
reloj, modelo simultáneo o geometría. [Plan](../../specs/003-weapon-contact/plan-rifle-revolver-free.md).

El selector conserva su vista congelada y la reversión libre se prueba antes
y después del reemplazo de modelo. Una acción real siempre prevalece. Recarga
activa, estado visual que devuelve una pieza y un tercer modelo mostrado no
se admiten por analogía. La captura es cosmética, nunca estado persistente.

Las pruebas extendidas reprodujeron saltos palmares iniciales de 572.577 mm
y 195.796 mm en las configuraciones dirigidas de la base, más fallos de
selector, marcha y presencia del handoff. Arco 0.08 m rechazado a −4.068 mm
contra chaqueta. Con 0.12 m: diez tests aprobados, 72 casos dirigidos (64
rifle/pistola existentes y ocho rifle/revólver libres), 228 poses de culata.
Mínimo combinado muestreado −0.353 mm, no separación positiva universal.
Máximos palmares nuevos: 26.652 y 16.570 mm por paso preparado de 60 Hz.

El mismo productor sight añade dos secuencias de teclas: 40 base + 26 cruces,
66 checks. Conserva los ocho casos anteriores, cinco guards compartidos y
61 estados por intercambio, incluidos frame cero y capturas. Los resultados
completos de renderer y CI se registran en el PR, no se anticipan aquí.

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

# Transición visual entre equipos · v0.20.8

Unidad acotada de #6, [SPEC-003](../../specs/003-weapon-contact/spec.md).
Base `be26fa05612e3318ad764ca09ddd5f8ef7f6ad3f`, PR #43 integrado y verificado.
No repite guardia/recarga ni preparación inicial. Revisión propia, no independiente.

## Problema y contrato

El cambio lógico de equipo era inmediato, pero también reiniciaba la pose visual.
La reproducción anterior registró saltos palmares de hasta 240.29 mm al seleccionar
otra familia. La nueva regresión de navegador usa las teclas de selección originales,
observa la paleta realmente dibujada y conserva el fallo de la versión anterior.

La selección lógica, el origen de disparo, la disponibilidad, cancelación, munición
y serialización conservan su ruta. Sólo se suaviza la presentación entre rifle,
SMG, escopeta y sniper disponibles, fuera de una recarga activa. El cambio entre
otros equipos y la salida de una recarga conservan la ruta inmediata anterior.

## Diseño dentro del montaje existente

`WeaponHandling.captureSwitch` conserva el montaje visual anterior en coordenadas
del actor antes de cambiar la selección. `present` llama al mismo `mount` con esa
memoria transitoria, mientras que `Equipment.mount` sigue calculando el montaje
lógico sin interpolación para trazas, disparos y demás reglas. El renderer usa
`present`. No se añade un segundo solver ni se interpola una matriz ósea a costa
de acortar o estirar huesos.

La memoria dura 0.40 segundos de simulación y utiliza una curva quíntica acotada.
Incluye origen, orientación, preparación de torso/mirada y objetivos de manos.
Las lecturas del renderer no avanzan el reloj ni modifican el estado persistente.
Un cambio sucesivo captura la pose visible actual, no la primera pose de la serie.
Pausa conserva el instante y restauración no conserva esa memoria cosmética.

El objeto describe un arco exterior máximo de 80 mm. La mano dominante conserva
su agarre. **La mano de apoyo se abre y se separa temporalmente del objeto**, luego
regresa al apoyo final. Su referencia durante ese arco es un objetivo de alcance,
no un contacto físico con la empuñadura. El informe digital expone `free-reach`
con peso de contacto cero. Ambos brazos mantienen sus longitudes y el IK existente.

Sólo se dibuja un equipo: el anterior en la primera mitad, el nuevo en la segunda,
con la entrega situada fuera del torso. No es una animación completa de funda ni
un objeto físico transportado. El HUD distingue selección lógica de transición
visual con «CAMBIANDO EQUIPO». Un disparo o recarga real tiene prioridad inmediata:
retira visualmente la entrega y muestra el montaje del equipo que ejecuta la acción.
Ese corte por acción está deliberadamente fuera del contrato de suavidad cosmética.
No se retrasa el disparo ni se muestra el arma anterior usando munición de la nueva.

## Alternativas rechazadas

Conservar rígidamente ambas manos y añadir el arco antes de proyectar al alcance
funcionaba en neutral, pero la proyección anulaba el desplazamiento exterior y
reintroducía penetraciones en variantes. Se observaron casos de 2.282, 2.846 y
6.783 mm al intentar ajustes verticales. No se conservaron esos perfiles ni se
relajó el límite de 2 mm. La corrección separa el agarre dominante del objetivo
libre de apoyo y aplica la separación del objeto después del ajuste de alcance.

Las capturas del primer prototipo y sus checks neutrales son exploración, no QA
del release final. Los logs distinguen RED, variantes rechazadas y ejecución final.

## Cobertura y reproducción

`tests/equipment-handoff.test.cjs` cubre los doce cambios ordenados entre cuatro
familias, retarget durante entrega, prioridad de acciones, restauración, caminos
no soportados y lecturas puras. Comprueba el instante inicial y pasos a 60 Hz,
retirada finita y coincidencia exacta con el montaje anterior al terminar. El
criterio de continuidad palmar permanece en menos de 30 mm por paso.

Se revisan superficies muestreadas con los observadores existentes y se añaden
160 muestras de cuello, agachado e inclinación para cuatro cambios representativos.
El criterio es profundidad no mayor de 2 mm, no separación positiva universal.
La mano libre no se computa falsamente como contacto digital rígido con el prop.

`tests/equipment_handoff_browser.py` ejecuta cuatro cambios mediante las teclas
originales y una interrupción de disparo. Usa el renderer canónico, no sustituciones
de módulos en memoria. Conserva identidad HTML, observaciones de 31 instantes por
cambio, capturas y hashes, además de alcance, datos, trigger y estado del HUD.
Reutiliza `longarm_stage.js`, que restaura la simulación original después de usar
la escena de prueba. La suite `handoff` agrega 16 controles al runner y a CI.

```sh
node --test tests/equipment-handoff.test.cjs
node --test tests/*.test.cjs
python3 build.py --check
python3 tests/release_build.test.py
python3 tests/qa_selection.test.py
xvfb-run -a python3 -m tools.qa.run --suite handoff --headed --output artifacts/handoff-check
```

La CI del HEAD y su revisión se registran en el PR, no se deducen de este documento.
Master y Pages requieren comprobación propia posterior al merge. Los resultados
locales identifican un árbol modificado hasta publicarse el commit correspondiente.
No se reescriben manifiestos o huellas de las ejecuciones anteriores.

## Límites y continuidad

No resuelve todas las entradas desde recarga, cambios a equipos sin dock, giros
extremos o variaciones completas de apariencia/locomoción. El disparo inmediato
puede interrumpir la curva. Las superficies son selecciones de piel/chaqueta contra
dos volúmenes del objeto mostrado, no colisión de toda la malla ni CCD. Los puntos
intermedios de la mano abierta requieren revisión artística más amplia.

Escena y reloj preparados, Storage fixture y GPU software no son una partida
completa, persistencia HTTP, FPS físicos o prueba con participantes. #5 conserva
aceptación artística/procedencia/materiales/UV y #7 recorrido/playtest/hardware.
#6 mantiene combinaciones no cubiertas y coste por actor/LOD, sin duplicar matrices.
No se cambian modelos, anclas originales, datos, licencia o permisos del repositorio.

Revertir fuentes, tests y build/version asociados no migra ni borra partidas.
[Handoff](HANDOFF.md), [estado](STATE.md), [QA](QA.md), [ramas](BRANCH-CLEANUP.md).

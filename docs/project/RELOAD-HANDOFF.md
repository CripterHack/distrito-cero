# Salida visual de recarga al cambiar equipo · v0.20.9

Unidad acotada de #6 y [SPEC-003](../../specs/003-weapon-contact/spec.md).
Base `3d6722e4e20b706c6a821b1866cf62c1f133784f`, PR #44 integrado, 0.20.8.
El PR de esta unidad registra resultados finales, integración y publicación.

## Defecto y contrato

El cambio libre entre familias ya tenía transición. `captureSwitch` excluía una
recarga activa. La cancelación retiraba inmediatamente tanto el estado lógico como
la pose anterior, aunque la mano izquierda estuviera sosteniendo una pieza extraída.
La nueva reproducción del HTML 0.20.8 con teclado real y recarga al 46% mostró
saltos iniciales de palma izquierda de 394.054 mm (rifle a SMG) y 149.989 mm
(escopeta a sniper). Son desplazamientos entre instantes, no FPS o velocidades.

La selección, cancelación de recarga, disponibilidad, munición, trigger y datos
siguen siendo inmediatos. La ampliación es **sólo de presentación** entre las
cuatro familias con dock. No modifica recargas normales, equipos sin dock,
geometría, anclas originales, longitudes de huesos, física o cámara.

## Implementación en el montaje existente

`captureSwitch` acepta ahora una recarga activa y conserva la pose y transformación
local de la pieza visible. La memoria sigue dentro de handling, excluida de las
partidas. No hay un segundo IK ni un reloj del renderer.

El montaje compartido mezcla torso, palmas y agarres desde esa instantánea. La
pieza del objeto anterior vuelve a su asiento con curva quíntica durante la
primera mitad, antes de reemplazar el único objeto dibujado. Su transformación
inicial es exactamente la capturada. No se genera una segunda pieza ni un evento
de reposición de munición. Durante el traslado la mano de apoyo sigue siendo un
objetivo libre, no un contacto digital rígido falso.

La salida de recarga dispone de **0.60 segundos de simulación**, frente a los 0.40
que conserva el cambio libre. El recorrido desde una pieza extraída es más largo.
El primer ensayo de 0.40 s conservó el instante inicial, pero llegó a 31.796 mm por
paso de palma y fue rechazado. Se amplió únicamente el tiempo cosmético, manteniendo
el límite de 30 mm por paso a 60 Hz y la disponibilidad inmediata del equipo.
Un cambio sucesivo conserva la duración y pose de la entrega activa.

Un disparo o nueva recarga reales siguen interrumpiendo inmediatamente la
presentación y mostrando el montaje lógico que ejecuta la acción. Una restauración
no recupera memorias de presentación. No se añade una animación de funda ni una
simulación física de la pieza libre o del gesto de reinsertarla.

## Regresiones y evidencia

Las cuatro regresiones por familia observaron RED en la fuente original antes
del cambio. La cobertura final recorre doce cambios ordenados, siete fases
(0, 8, 28, 46, 65, 86 y 97%) y 48 pasos a 60 Hz por caso. Comprueba continuidad,
superficies muestreadas, primer transform de pieza, asiento antes del reemplazo,
fin de memoria, cancelación inmediata, munición y pureza del serializador.
Una quinta regresión cubre reselección rápida, acciones prioritarias y restore.
El antiguo test de ruta inmediata se conserva para indisponibilidad y no-dock;
su cláusula de recarga queda reemplazada explícitamente por este contrato.

La suite gráfica **existente** `handoff` conserva sus 16 checks y añade seis:
dos cambios desde recarga mediante las teclas originales, 43 observaciones
renderizadas por caso y 18 capturas adicionales. Compara las palmas y tres puntos
de la pieza visible antes/después, cancelación, munición, alcance y superficie.
No etiqueta esos dos casos como cobertura visual completa de las 84 combinaciones.

El presupuesto de cada suite WebGL de CI pasa de 600 a 900 segundos por las 86
observaciones adicionales. No cambia el límite del job, los criterios de aceptación,
las suites HTTP o el manejo de fallos. No se usa continue-on-error.

```sh
node --test tests/reload-handoff.test.cjs tests/equipment-handoff.test.cjs
node --test tests/*.test.cjs
python3 build.py --check
python3 tests/release_build.test.py
python3 tests/qa_selection.test.py
xvfb-run -a python3 -m tools.qa.run --suite handoff --headed --timeout 900 --output artifacts/reload-handoff-check
```

La repetición completa local terminó con **576/576 Node** y **101 Python
vigentes** (92 del core y nueve de matriz), sin tests omitidos. Autoría, build,
exportación y enlaces en 76 documentos aprobaron. Son resultados de esta
candidata, no una reutilización del resultado anterior de master.

El primer runner gráfico `20260924T073706Z-9925f4c28e4c` agotó sus 900 segundos:
exitCode 124, 16 checks aprobados de los 22 esperados. Ocurrió mientras también
se ejecutaba la suite Node completa. Ese run permanece **fallido**, con capturas
y registro parcial. La repetición se ejecuta por separado con presupuesto local
de 1800 s, sin retirar los casos antiguos ni alterar sus aserciones. Sus resultados
finales se registran en el PR, separados del helper de reconstrucción y de CI.

HTML canónico 0.20.9: 8,875,066 bytes, SHA-256
`5743fc63568d2a4da7635f5b1708542ff0fa681accae660113237561ba7961fd`.
Fuente `7a7f316ecbbb8c4d364a9e0a33acba26bf847bb66b0835ba5271522e61f204b9`.

Los informes conservan el SHA del HTML y el checkout base con modificaciones
cuando proceda, sin reescribir procedencia. Una prueba local de baseline fue
interrumpida al detectar que seguía activa mientras se editaba la fuente y no
cuenta como evidencia del baseline limpio. Una ejecución dirigida de 30 s también
se interrumpió y se repitió completa. El primer fetch del bundle usó un nombre de
ref inexistente y después se recuperó el ref realmente enumerado, sin crear historia.

## Límites y continuación

Las superficies son las mismas selecciones de cara/cuello y chaqueta frente a dos
volúmenes, no CCD, colisión de toda la malla ni separación positiva universal.
Las observaciones se hacen con escena/tiempo preparados y GPU software. No son
playtests humanos, rendimiento de GPU física ni aprobación artística del gesto.
La salida hacia equipos sin dock y las interrupciones por una acción real conservan
su ruta inmediata, sin afirmar que sean suaves. Acciones combinadas, locomoción,
anatomías y coste por actor/LOD mantienen sus criterios generales de #6.

#5 conserva arte/procedencia/materiales/UV y #7 escena/recorrido/playtests/hardware.
No cerrar esos requisitos por esta corrección. [STATE](STATE.md) y
[HANDOFF](HANDOFF.md) son los puntos de continuidad. Revisión propia, no independiente.
Revertir los cambios de fuente, pruebas, versión y build no requiere migraciones
ni borrado de partidas. Las ramas de trabajo se retiran sólo tras verificación.

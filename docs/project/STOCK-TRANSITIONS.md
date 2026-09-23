# Culata y prenda durante guardia y recarga · v0.20.6

Seguimiento de #6 y [SPEC-003](../../specs/003-weapon-contact/spec.md).
Base remota `02e3a140baa8994a02fbcb5943b9a4c8258915df`, publicada como 0.20.5.
El parche de la preparación local anterior se aplica en esta continuación mediante
una rama nueva. El PR registra su CI, revisión e integración definitivas.
Los apartados históricos siguientes conservan las ejecuciones originales del parche;
no deben interpretarse como ejecuciones nuevas de esta publicación.

## Defecto, causa y cambio acotado

El apuntado neutral aceptado no evitaba el cruce de la culata con la prenda al
bajar el arma o recargar. Al desaparecer la coordinación ocular, el montaje
interpolaba hacia un origen genérico dentro del torso. Las palmas seguían llegando
a sus anclas, por lo que medir sólo manos u ojos no detectaba esa penetración.

Se reutiliza la referencia triangular de chaqueta del montaje existente. El centro
posterior de la culata se mantiene delante de esa superficie durante guardia y
recarga. El recorrido hacia el apuntado describe un arco exterior que se anula en
ambos extremos. El margen frontal aumenta suavemente para inclinaciones hacia
abajo. Los valores se aplican a presentación de equipo ficticio, no a ingeniería
real. No se cambia geometría, vértices, longitudes, pivotes palmares o referencias
QA para hacer pasar las distancias.

Torso y objeto comparten una envolvente derivada del mismo `handling.ready`:
`carryReady = 1 - sqrt(1 - ready)` y `carryWeight = carryReady²`. No añade un reloj,
filtro persistente o estado guardado. Conserva el ritmo de disponibilidad del
equipamiento y evita que la preparación visual salte hacia el torso más rápido
que las manos. Con ready=1 y coordinación=1, el punto final de apuntado no cambia.

El cambio vive en `weapon-handling.js`, dentro del montaje ya existente. La
proyección al alcance de ambos brazos continúa vigente. Las familias sin `dock`
siguen su rama original. El origen del equipo y su trayectoria visual sí cambian,
por lo que no se presenta como identidad geométrica universal de la boca del arma.
La transferencia de munición y el serializador no se modifican.

## Regresiones y fallos conservados

Ocho requisitos iniciales fallaron con la fuente original. La repetición completa
inicial produjo 543 aprobadas y ocho fallidas. Tras ampliar cobertura se reprodujo
RED nuevamente: diez de las once regresiones fallaron sobre el código original.

Una primera trayectoria pasó casos neutrales pero falló recuperación inclinada.
La ampliación de cuello/agachado/pitch detectó esos cruces y motivó el arco exterior.
Otro prototipo introdujo cinco regresiones de continuidad al equipar, con pasos
palmares de hasta 61.5 mm frente al límite vigente de 30 mm. Se rechazó. Torso y
montaje terminaron usando la misma envolvente, sin modificar ese límite. Las 33
pruebas previas afectadas volvieron a aprobar, y la suite final produjo
**554/554 Node**, cero fallidas/omitidas/canceladas/todo.

Las once regresiones cubren guardia y recarga por familia, 192 combinaciones
inclinadas de cuello/agachado, pureza y transformaciones, y flujo real de recarga
con conservación de munición. Las entradas, temporizadores y continuidad palmar
se ejecutan a 60 Hz. En la secuencia nativa de 2,880 pasos la superficie se muestrea
cada seis pasos, a 10 Hz. No es detección continua de colisiones entre muestras.

El test longarms conserva sus 24 comprobaciones y añade clearance a la aceptación
de sus siete capturas de subida/bajada por familia. Ya no basta con que el
observador de superficie devuelva números finitos.

## Evidencia local identificable

La entrega adjunta conserva logs RED/GREEN, repetición Python y reportes gráficos.
Antes y después utilizan los HTML canónicos construidos, no módulos sustituidos
en memoria. La comparación de rifle conserva 16 capturas por versión. Las otras
tres familias añaden 48 capturas de la candidata: **80 imágenes en total**, no vídeos.
Las escenas, cámara y tiempo están preparados; se avanzan los temporizadores de
recarga reales. Chromium/SwiftShader, Storage fixture y revisión propia.

El informe de captura valida también errores del navegador, GL, peticiones y
pureza del juego activo. `passed` en el informe anterior significa integridad de
captura, no ausencia de la penetración original. Ver las distancias, la decisión
de clearance y los hashes de cada PNG. El alcance gráfico no acredita FPS físicos
ni persistencia HTTP. No se volvió a ejecutar la matriz artística de 586 imágenes.

El primer chequeo Python de identidad falló porque README/índice/STATE todavía
indicaban 0.20.5. Se conservaron el fallo y su posterior repetición después de
sincronizar la documentación. No se retiró ni cambió esa prueba.

HTML anterior SHA-256:
`4307c76139bc4f4b8178a16792ecb6c490bd1b0633d98a4a4a86336036cf3641`.
HTML de la candidata, 8,870,022 bytes:
`ff8db64a6c9f10549fb346320725efc97539813f6da83852bcbc279d7680b86f`.
Fuente:
`08dc02e50fbdce141e2cbbc0d55c2b089b5d437c84c8f340383a4c3a2a54c493`.

## Cierre de verificación local

La repetición Python final aprobó **98 pruebas**: 89 del conjunto central y nueve
de la matriz de personajes. El primer fallo de identidad está conservado junto
al log `release-final.log` de la repetición aprobada. El build inmutable, la
exportación de equipo y los enlaces locales de 73 documentos aprobaron.

El runner portable `20260923T195509Z-cd4a5d344a98` terminó con exitCode=0:
**141 comprobaciones**, distribuidas entre longarms (24), handling (51), thumbs
(15), fingers (15) y characters (36). Todos los informes identifican el HTML
candidato, sin errores o solicitudes externas. Se cotejaron los 48 hashes de
capturas longarms y los 30 del benchmark, además de los 80 de la comparación.

El campo `commit` de ese runner conserva `5f7cdc2`, el padre Git disponible en el
laboratorio. **Es una ejecución de un árbol local modificado**, no la CI ni los
bytes de ese commit. El HTML, el manifiesto de archivos y el parche identifican
exactamente la candidata. El contexto documental del master remoto se verificó
por sus blobs antes de generar el diff. No se fabrica un commit remoto.

Se revisaron las 64 vistas candidatas en cuatro hojas de contacto, más el detalle
de una recarga y la comparación del rifle. La inspección en miniaturas no equivale
a examinar cada vértice/píxel a resolución completa ni a aprobar arte del conjunto.
No se ejecutaron en esta sesión nuevas suites de persistencia HTTP o exportación
humana para la candidata. Esos workflows y la CI del nuevo PR siguen siendo puertas
de integración, separadas de la CI del master publicado.

## Reproducción y límites pendientes

```sh
node --test tests/stock-transition-clearance.test.cjs
node --test tests/*.test.cjs
python3 build.py --check
python3 tests/release_build.test.py
python3 tools/export_contact.py
python3 tests/contact_exports.test.py
xvfb-run -a python3 -m tools.qa.run --suite longarms --suite handling --headed
```

El equipo está preparado (ready=1) antes de iniciar guardia/recarga en los casos de
aceptación. **Persisten posibles cruces durante el desenvainado inicial**, que se
debe abordar en otra unidad conservando continuidad y alcance. No extrapolar esta
corrección a cualquier giro, constitución, movimiento o combinación de acciones.

El observador conserva la selección original: cara/cuello y vértices de chaqueta
con altura de bind >=1.30, frente a dos cuboides cosméticos verificados. No representa
toda la prenda ni colisión triángulo-triángulo, no evalúa todos los segmentos del
arma y no constituye aprobación artística. #6 continúa pendiente a nivel global.
#5 y #7 mantienen sus requisitos propios de arte/procedencia/playtest/hardware.

La sesión que preparó el parche sólo disponía de lectura de GitHub. Esta continuación
sí utiliza escritura y reconstruye los objetos exactos desde el master actual.
La reconstrucción 35916388833 verificó el build y 554 Node, sin modificar referencias
de producto. Su ZIP tiene SHA-256
`1c91dcb407c5ae380679585e94e81c3f9b5d5dcd409c03bc787dbd060175f446`.
El bundle incluido permite verificar y aplicar los once archivos contra el commit
02e3a14 auténtico. Los seis objetos de producto coinciden con el parche entregado.
Los cambios adicionales a HANDOFF/STATE y esta página distinguen pasado y publicación.

Una repetición local nueva volvió a observar diez regresiones fallidas con la fuente
original y 554 Node aprobados con la candidata. La prueba adicional del desenvainado
confirma el límite pendiente: hasta 23.70 mm de cruce muestreado al décimo paso,
ready aproximado 0.8401. Ese diagnóstico numérico no es una corrección publicada.

Exigir la CI del HEAD del PR, exportación humana y benchmark aplicables, además de
revisión de artefactos antes del merge. Master/Pages se verifican por separado.
La herramienta auxiliar no entra en el árbol ni historial del producto y debe
retirarse al terminar. Revertir fuentes, pruebas y build/version asociados no
migra ni borra partidas. [Handoff](HANDOFF.md).

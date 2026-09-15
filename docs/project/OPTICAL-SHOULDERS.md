# Continuidad de hombros y codos al usar binoculares

Unidad de #6 / CONTACT-03, CONTACT-05 y CONTACT-06. Base revisada: `ac3cf5b3ef78e42f50eee173a8200b9e3d2e4286`. No cierra todos los criterios del issue.

## Defecto localizado

Al revisar el ciclo completo de los hombros después de corregir las mangas, los binoculares revelaron una inversión rápida del plano de flexión del codo. Era especialmente visible al terminar de levantar el instrumento estando agachado: las manos llegaban a su sitio mientras los codos se colocaban por encima de las muñecas y la prenda cambiaba bruscamente de forma.

La causa era la referencia de flexión (`pole`) compartida con armas largas. El solver proyecta esa dirección sobre el plano perpendicular a hombro-muñeca. En la postura óptica compacta, ambas direcciones se aproximaban al antiparalelismo, por lo que una variación pequeña de la mano cambiaba mucho la dirección del codo. No era un nuevo error de los pesos de mangas.

## Corrección

El perfil óptico define sus propias referencias de codo, adelantadas y moderadamente descendentes. Las demás familias conservan exactamente sus referencias anteriores. Las anclas de palma, posiciones del instrumento, forma de los dedos, solver analítico y longitudes de los huesos no cambian.

La interpolación de subida y bajada de los binoculares utiliza una tasa de 6 en lugar de 12. Alcanza aproximadamente el 95% de la postura en medio segundo, frente a aproximadamente un cuarto de segundo anterior. Las armas de fuego mantienen la tasa 12. Se conserva el zoom, inventario y todas las reglas de munición y recarga. Cambia la presentación óptica, no su potencia ni su funcionamiento de observación.

La corrección del plano se valida con incrementos uniformes de pose, independientemente de la velocidad de interpolación. No se oculta la inversión limitándose a hacer más lenta una trayectoria defectuosa.

## Regresiones y alcance medido

Ocho pruebas Node cubren recorrido uniforme, subida/bajada con el controlador real a pasos de 1/60, posición final de codos, longitudes, orientación palmar, lecturas deterministas, familias no ópticas, condicionamiento del plano y superficie real de hombro/axila. Seis fallan con las fuentes anteriores; las ocho pasan tras la corrección.

En las muestras documentadas del modelo actual:

| Medida | Resultado corregido |
| :--- | :--- |
| Máximo paso del codo en barrido óptico agachado de 1/180 | 0.002960 m |
| Máximo paso del codo en subida/bajada óptica a 1/60 | 0.034807 m |
| Mínimo seno entre referencia y eje hombro-muñeca en la cuadrícula revisada | 0.788376 |
| Máximo paso de la superficie superior de la prenda | 0.022980 m |

La muestra de superficie revisa 284 posiciones canónicas por pose. La regresión anterior detecta un salto de 0.104956 m al comenzar a bajar el instrumento en un caso de pie. Estas medidas describen muestras concretas; no prueban ausencia de intersecciones en todas las animaciones. La tolerancia de movimiento entre pasos no debe confundirse con la tolerancia de contacto palma-empuñadura.

`tests/optical_shoulder.py` añade 14 comprobaciones del renderer de producción, 13 capturas de fases ópticas y recarga de fusil, y conserva la separación entre almacenamiento fixture y nativo. Utiliza el controlador real de equipo, tiempo y estado de escena preparados. No es un playthrough ni un benchmark de FPS físicos.

## Reproducción

```sh
python3 build.py
node --test tests/shoulder-motion.test.cjs
node --test tests/*.test.cjs
python3 -m tools.qa.run --suite optical --headed
python3 -m tools.qa.run --suite handling --suite recovery --headed
python3 -m tools.qa.run --suite native --origin http --headed
```

La suite optical forma parte del contrato fixture y nunca satisface la persistencia HTTP. El benchmark de personajes y los tests de autoría de mangas permanecen intactos. Los artefactos nuevos van a `artifacts/`, no reemplazan evidencia histórica.

## Verificación visual e integridad

Se compararon 21 fotogramas locales antes/después con cámaras equivalentes, incluyendo perfil/frontal/tres cuartos, grados de elevación y fusil sin cambios. Esas comparaciones usan la base visual v0.19 con los mismos assets actuales; no contienen la capa posterior de recuperación. La prueba remota y la CI utilizan el HTML actual con recuperación. Mantener identificados ambos orígenes, sin atribuir las capturas locales al hash de la CI.

Asset humano sin modificar: `a4f5a6522f0012290bd2fca8d573ca5243388474f72fb026cf5766924e3c8b7d`. HTML actualizado: `fe47dfa3ef9b2bff6d415b6f6fb0b64e0d0b0c0df7193b135c59e4fc3fe7b93b`, 8,851,747 bytes. Sólo dos módulos del runtime cambian: `weapon-handling.js` y `equipment-simulation.js`. No hay nuevos recursos, huesos, librerías o formatos de guardado.

## Límites y opciones descartadas

Un ensayo local con una referencia que variaba por fase no conservó el margen de condicionamiento y la continuidad de la bajada. Se descartó antes de publicar, sin relajar las tolerancias. Una falta de `xauth` del entorno remoto se resolvió iniciando Xvfb directamente; no se modificó el juego para resolver esa infraestructura.

Los codos ahora recorren una solución estable, pero el aspecto de hombros, axilas, dedos y cuerpo sigue siendo estilizado. No hay autocolisión general de tejidos ni una simulación biomecánica completa. Los contactos de falanges, la alineación ojo-mira y otras familias necesitan unidades posteriores. Las poses extremas no revisadas pueden seguir mostrando intersecciones. Las exportaciones humanas GLB anteriores son históricas.

Reversión: revertir los dos módulos y reconstruir el HTML. No requiere migrar partidas. No cambiar la configuración de Pages.

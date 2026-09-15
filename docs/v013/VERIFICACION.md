# Distrito Cero v0.13 · Movimiento orgánico · Verificación

14 de septiembre de 2026. Continuación del código de **v0.12**, sin sustituir la campaña, el creador, el catálogo o la expansión regional.

## Identidad de los archivos

HTML: **8,706,553 bytes**. SHA-256 `2cfc9ae5cc85087d8d21ded739a10c955cce37b831f029467e314b25acdefbc3`.

GLB: **3,752,348 bytes**. SHA-256 `79de0cbacc0f77d724e16681e0c417bc3b703f279b77e9bce6a575860c158c30`.

El informe `qa/v013/release-report.json` coteja estos bytes con las pruebas y las capturas finales. La comparación gráfica usa el HTML original v0.12, no un sustituto reconstruido para hacer parecer mayor la mejora.

## Resultados ejecutados

| Grupo | Comprobaciones satisfactorias |
| :--- | ---: |
| Lógica Node: núcleo, rig, apoyos, ocupación, mundo, identidad y catálogo | 227 |
| Creador nuevo y regresión DQ/inspección/búsqueda | 30 |
| Partidas/editor anteriores, fallos de escritura e interfaces móviles | 64 |
| Campaña, conducción, controles y guardado anteriores | 52 |
| Bucle de simulación/render original con teclado real | 16 |
| Geometría corporal, cabeza y continuidad anteriores | 20 |
| Pulido de prendas y normales compartidas de manos | 5 |
| Estructura, materiales y nueve clips del GLB | 1 |

**227 pruebas de lógica, 162 comprobaciones de navegador y 26 de geometría/exportación.** Son aserciones, no 162 sesiones independientes ni una certificación artística. No se suman resultados históricos. Los cuatro grupos finales de navegador no registraron excepciones JavaScript, errores WebGL detectados ni solicitudes HTTP/HTTPS. Las imágenes embebidas no son descargas externas.

## Cambios y cobertura

### Locomoción y postura

La cadencia se calcula a partir de distancia y velocidad reales. Peatones que quedan bloqueados no continúan avanzando su fase de marcha por un simple reloj fijo. La solución analítica de las piernas se aplica después del torso, compensa su posición y limita la altura de pelvis al alcance de los segmentos. Los codos se flexionan más al correr, los brazos alternan respecto de las piernas y existen compensaciones suaves de respiración, aceleración y giro.

Las pruebas recorren velocidades, fases y estados de crouch, comprueban cotas de suela sobre suelo plano y transformaciones finitas. Los bordes de despegue y contacto se prueban a ambos lados del límite del ciclo para evitar un salto de ángulo. El estudio de 240 pasos de marcha recta comprueba que el error del tobillo respecto de su apoyo conservado es menor de 12 mm. Ese umbral no demuestra colisión de cada vértice de la suela ni equivalencia biomecánica con marcha capturada.

`MotionTracker` limita su memoria a 144 actores, no altera sus entradas ni los datos serializables, es idempotente al repetir una muestra y se reinicia ante teletransporte, saltos de tiempo o cambio de simulación. No conserva apoyos mundiales durante el estudio en el sitio, asientos, acciones de acceso o vuelo. Los giros extremos liberan apoyos para no torcer indefinidamente el tobillo.

### Manos y ocupantes

Los patrones de dedos distinguen conducción, carga, alcance y reposo. No son un contacto físico individual de falanges. Se identificó que los objetivos anteriores del volante estaban fuera del alcance de la cadena del brazo. Se comparte una referencia de cabina entre el volante dibujado y ambos tipos de ocupante. Las muñecas se prueban en dirección neutra y dos extremos de giro, con error inferior a 8 mm respecto de su objetivo; los dedos se recalculan después de IK.

La secuencia existente de extracción y entrada se mantiene. La suite continua usa F real, espera al cierre, conduce, frena, sale, camina y cruza una frontera de sector. No se sustituye RAF, renderer, cámara ni simulación. Sus posiciones iniciales se preparan para repetir el escenario.

### Superficies

El pulido geométrico conserva **85,209 triángulos**, 49 huesos y trece grupos de material. Cambia 2,389 vértices únicos de chaqueta y 635 de pantalón, con desplazamientos máximos cuantizados de aproximadamente 4.55 mm y 1.34 mm. El cuello de la prenda, cierre, puños y puntos de contacto se preservan mediante máscaras. Se comprueban orientación de triángulos, normales unitarias y pesos.

Las manos conservan posiciones, UV y pesos. Se corrigieron discontinuidades de normales de sombreado entre vértices coincidentes, encontradas al revisar la imagen y medidas hasta unos 26 grados antes de la corrección. No se anuncia una nueva topología de mano. Rostro, uñas, cuero cabelludo y mapas existentes permanecen. Tela y piel reciben microdetalle filtrado ligado a la superficie. Los párpados cierran sobre los ojos sin comprimir su geometría; la mirada cambia por intervalos cortos, no por oscilación continua.

LOD observados: **85,209 / 17,557 / 6,188 triángulos**. La geometría se comparte entre actores. La capacidad de la paleta no equivale a una promesa de esa cantidad de personas a 60 FPS.

### Creador y datos

Se prueban enfoque de pies, cámara lenta del estudio, posturas de asiento y alcance, retorno a reposo y ausencia de cambios en la sesión real. Comparación, cancelación y aplicación conservan el borrador. Los tests de catálogo repiten historias independientes, renombrado, copias, importación, exportación, búsqueda y orden, escritura rechazada, sesión volátil y conflictos de revisión.

No se cambia el esquema ni la clave de partidas. Los doce espacios siguen sujetos a cuota y permisos. La persistencia probada se realiza con un fixture explícito en memoria; no se afirma guardado nativo después de cerrar y reabrir un archivo local.

## Correcciones encontradas durante esta iteración

1. El caso inicial de apoyo mostraba tobillos fuera del alcance de las piernas. Se añadió prueba fallida y se sustituyó por resolución posterior al torso con altura de pelvis acotada.
2. La continuidad angular entre recuperación, contacto y despegue falló al revisar ambos lados del ciclo. Se igualaron sus valores de borde y se repitieron las pruebas.
3. La primera integración del editor no arrancó por una variable `target` declarada dos veces. La sintaxis de todo el JavaScript distribuido quedó cubierta por una nueva prueba, se separó el nombre de objetivo de pose y se repitió la batería completa.
4. Las normales de la piel tenían discrepancias en puntos cuantizados compartidos. La nueva prueba falló antes de unificarlas y pasa después, preservando posiciones y pesos.
5. Un test de cadencia temprano pidió movimiento a 0.01 m/s, por debajo de la zona muerta explícita de 0.02 m/s. Se corrigió el caso a 0.1 m/s, sin eliminar la prueba de reposo.

Los ensayos iniciales fallidos no se cuentan como pases. La API del contenedor devolvió una demora al iniciar el plan de capturas, pero se comprobó el proceso existente antes de continuarlo; no se lanzaron copias adicionales a ciegas.

## Imágenes y animación

Las capturas y el vídeo proceden del renderer WebGL del juego. Las posiciones y cámaras de estudio son preparadas. Los cuadros comparativos sólo recortan por igual y añaden rótulos, sin retocar al personaje.

El clip se compone de **180 fotogramas** a 20 FPS de reproducción, con marcha, carrera y flexión de dedos. El tiempo de captura de cada fotograma puede exceder ese intervalo. Está rotulado como **tiempo de animación controlado**, no rendimiento en tiempo real ni mocap. No utiliza generación de imágenes ni interpolación de vídeo.

## Exportación y reproducción

El GLB actual contiene trece mallas, 49 huesos, tres mapas PNG y nueve estudios procedurales. Incluye traslaciones locales por hueso, además de sus rotaciones, para conservar la respiración y las soluciones de pose. Se comprobaron buffers, índices, pesos, normales, tiempo creciente, cuaterniones unitarios y cierre de los clips. `trimesh` lo leyó de forma independiente. No se ejecutó el validador oficial de Khronos ni una comparación visual en todos los editores externos.

La geometría, HTML y GLB se reconstruyen desde los insumos incluidos. `tools/audit_organic_release.py` exige huellas idénticas antes/después y que todos los informes actuales correspondan a este HTML. Los constructores antiguos se conservan identificados como históricos y no se utilizan para v0.13.

## Entorno y límites

Chromium 144.0.7559.96, Linux, Xvfb y ANGLE SwiftShader. Las suites de estado aparcan renderer entre fotogramas reales; las cuatro suites usan HTML inyectado y almacenamiento en memoria por las restricciones de navegación del laboratorio. La prueba continua conserva el bucle original a 680 × 440. No se deduce rendimiento de GPU física de estas mediciones.

No se probaron Safari, Firefox, teléfonos físicos, sesiones de horas, almacenamiento de nube o recuperación del contexto WebGL. No se anunció un benchmark de FPS.

**El resultado sigue estilizado y no iguala la referencia hiperrealista.** La mejora principal de esta versión es movimiento y continuidad, no un personaje escaneado nuevo. Persisten límites visibles en rostro, cabello, manos, silueta corporal y algunas poses extremas. No hay mocap, ropa física, simulación muscular, apoyo sobre cada objeto móvil, ragdoll nuevo o contacto exacto dedo/objeto. La anatomía de NPCs continúa compartiendo una familia base.

# Distrito Cero v0.12 · Continuidad anatómica · Verificación

14 de septiembre de 2026. Continuación comprobada de **Identidad v0.11**, sin reconstruir la campaña o sustituir el catálogo de partidas.

## Archivos exactos

HTML autónomo: **8,696,067 bytes**. SHA-256:

`9dda7ab5ccffca783ae70d6703141a5fbf3ad0673fcbacdcf76aa53b348af2dc`

GLB del personaje neutral: **3,099,692 bytes**. SHA-256:

`f4cf902480d25ae5b12a6e484a37470a75ec2b8519ee9a76411b4550583818f6`

`qa/v012/release-report.json` contiene las huellas de fuentes y los informes de pruebas. Los cuatro informes finales de navegador y las nueve capturas actuales corresponden al mismo HTML. Las dos capturas anteriores se obtuvieron del HTML original v0.11 y se identifican como tales.

## Ejecuciones finales

| Grupo | Comprobaciones satisfactorias | Fallos finales |
| :--- | ---: | ---: |
| Lógica Node, incluidos DQ, identidad y catálogo | 207 | 0 |
| Creador nuevo, DQ en GPU, comparación, cuello y búsqueda | 23 | 0 |
| Catálogo/editor heredados, fallos e interfaces móviles | 64 | 0 |
| Campaña y controles heredados | 52 | 0 |
| Bucle normal con extracción, conducción y cruce de sectores | 16 | 0 |
| Geometría corporal | 7 | 0 |
| Cabeza, mapas y conexión cervical | 6 | 0 |
| Anatomía cervical, uñas, pesos, normales y presupuesto | 7 | 0 |
| Exportación GLB | 1 | 0 |

Total: **207 pruebas de lógica, 155 comprobaciones de navegador y 21 pruebas de geometría/exportación**. No son 155 sesiones independientes ni cobertura exhaustiva de todas las combinaciones del mundo abierto. No se suman informes históricos ni intentos incompletos.

En las cuatro ejecuciones finales de navegador no se registraron excepciones JavaScript, errores WebGL detectados ni peticiones HTTP/HTTPS externas. Los datos de imágenes embebidos no son descargas de red.

## Qué cambió y cómo se comprobó

### Anatomía visible

La nueva base del cuello llega hasta 1.447 m y se abre hacia el tórax. Las influencias inferiores se anclan al pecho, pasan al cuello y finalmente a la cabeza. La topología y los mapas faciales anteriores se conservan, salvo la corrección del contorno cervical inferior. La abertura de la chaqueta no es un cilindro tapado. La unión suavizada de torso y mangas modifica hombros y axilas, junto a pliegues de menor amplitud.

La palma y la muñeca tienen menos volumen, y las uñas siguen la superficie dorsal real mediante una intersección geométrica, no una estimación basada sólo en el radio nominal de un dedo. Se verifican continuidad de manos, pesos que suman 255 en el formato cuantizado, normales unitarias, huesos dentro de rango y un presupuesto de menos de 100,000 triángulos para detalle alto. La separación de uñas se muestrea respecto de la superficie en reposo, no es una garantía de ausencia de intersección para cada pose.

Se detectó durante la revisión un pico lateral cervical heredado del recorte de la cabeza, con semiancho de 80.6 mm entre 1.515 y 1.541 m. La prueba falló antes de suavizar ese contorno y pasa después, conservando la mandíbula superior. Registro: `cervical-spike-red.txt` y `geometry-final.txt`.

### Deformación

Las matrices originales de los 49 huesos permanecen intactas como contrato de simulación/IK. Una paleta adicional de cuaterniones duales se calcula por actor y se utiliza en color, sombras y reflejos. La prueba CPU verifica reposo, transformaciones rígidas incluso cercanas a 180°, mezcla de signos opuestos, torsión sin colapso radial y límites de escritura de cada fila. El navegador comprueba la carga de la paleta y la deformación real en varias poses.

La piel de manos y cuello recibe detalle de altura/rugosidad procedural ligado a la superficie. No se añadieron escaneos, mapas fotográficos de manos, simulación muscular ni física de tejidos. DQ reduce artefactos de mezcla de rotaciones, pero puede abultar zonas y no elimina todos los cruces entre superficies.

### Creador y guardados

Los perfiles antiguos sin `neck` se cargan con cero. Valores fuera de rango se rechazan antes de escribir. El borrador, la comparación inicial, la iluminación de estudio y los enfoques de inspección no cambian el mundo real. Se verifica que aplicar desde comparación guarda el borrador y que cancelar conserva la apariencia anterior.

La búsqueda admite tildes y mayúsculas y consulta nombres de historia/personaje. Ordenar por nombre o progreso no modifica las cadenas de almacenamiento. El respaldo completo no desaparece al filtrar todos los resultados. Se vuelven a ejecutar los casos heredados de nombres iguales, ID independiente, carga, renombrado, copia, borrado, importación/exportación, rechazo de datos, cuota, sesión sin guardado y conflicto de revisión.

Los doce espacios son el límite de diseño sujeto a la cuota, no una garantía de capacidad máxima. El catálogo sigue siendo local, sin sincronización en nube ni bloqueo distribuido.

## Campaña y ejecución real

El bucle continuo no reemplaza RAF, simulación, cámara ni renderer. Usa teclado del navegador para iniciar extracción de un conductor, completar acceso, conducir, frenar, salir, caminar, cruzar una frontera de sector y utilizar el atlas. Las posiciones iniciales se preparan para repetir el escenario. No equivale a una partida completa ni a una prueba de horas.

Las suites por estados aparcan el renderer entre fotogramas WebGL dibujados explícitamente. Conservan las reglas del juego y las entradas DOM. La campaña coloca al jugador cerca de objetivos para probar las transiciones del desenlace público. Las interfaces se emulan en 390 × 844 y 844 × 390. Los controles nuevos de inspección se ejercitaron en escritorio, además de mantener accesible el editor completo en esos tamaños móviles.

Los hashes de núcleo, mundo, policía, simulación, daño, ocupación, mundo procedural, audio, app base, rig y mapas coinciden con v0.11. Lista en `behavior-unchanged.json`. La igualdad binaria no sustituye las pruebas de integración.

## Evidencia visual

Se inspeccionaron cuello/hombros, mano abierta, flexión, cuerpo completo, carrera, agachado, conductor, extracción y reparto. Las imágenes son del juego, no renders de Blender ni imágenes generadas. Las comparaciones v0.11/v0.12 usan idéntica cámara, luz, pose, viewport, escala de píxel y calidad. Su composición sólo recorta por igual y añade rótulos.

Los planos de estudio finales se capturaron a calidad alta y escala 1.5, dando imágenes de 966 × 912. Los encuadres del mundo usan 1000 × 700, y el bucle continuo 680 × 440 en calidad económica. No se interpretan estas capturas como un benchmark.

## Recursos

| Recurso | Valor |
| :--- | ---: |
| Triángulos de detalle alto | 85,209 |
| Triángulos de detalle medio | 17,527 |
| Triángulos de detalle lejano | 6,178 |
| Huesos / grupos de material | 49 / 13 |
| Textura DQ adicional | 98 × 128 RGBA32F |
| Memoria de esa textura DQ exclusivamente | 200,704 bytes |
| Paleta matricial conservada | 401,408 bytes |

La memoria de estas dos texturas no incluye el resto de VRAM o memoria del juego. La capacidad de 128 filas no promete 128 personas a 60 FPS. Los recursos de geometría y texturas se comparten con tres niveles de detalle.

El GLB se leyó también con `trimesh`: 13 mallas, 85,209 triángulos, límites métricos finitos. Siete estudios procedurales y tres mapas embebidos. No se ejecutó el validador oficial de Khronos ni una prueba visual en todos los editores. Un visor glTF lineal puede deformar distinto del juego con DQ. Apariencia personalizada, mirada, parpadeo, materiales procedurales y secuencias de acceso a vehículos no se exportan como efectos completos al GLB.

## Incidencias y límites

La prueba inicial de uñas encontró puntos 0.371 mm dentro de la mano. El ajuste sobre triángulos sustituyó la fórmula nominal, y se reconstruyó el modelo antes de repetir todas las comprobaciones finales. La prueba de cuello añadió otra corrección geométrica identificada visualmente. Se conservan los registros de fallos previos.

Una prueba temprana del nuevo agarre dependía de una espera fija de 120 ms y falló bajo carga del renderer por software. Se cambió a esperar el estado de la pose antes de dibujar, sin modificar la animación para satisfacer la prueba. El estado previo al dibujo fue `grip: 0.82, gl: 0` y la suite final pasó completa. Otra ejecución de biblioteca fue interrumpida por el límite de un lanzador, luego se repitió por separado. No se cuentan los intentos incompletos.

Se intentó verificar almacenamiento nativo con un contexto real y `file://`, pero el entorno devolvió `ERR_BLOCKED_BY_ADMINISTRATOR`. No se sortearon esas restricciones y no se afirma haber comprobado persistencia al cerrar/reabrir el navegador. Las pruebas finales utilizan almacenamiento aislado en memoria e inyección del HTML. El juego distribuido sí utiliza el almacenamiento nativo, no ese fixture.

Entorno: Chromium, Linux, Xvfb, ANGLE SwiftShader. No se probaron Safari, Firefox, GPU física, teléfonos físicos, sesiones prolongadas, pérdida de contexto WebGL ni despliegue público. No se promete un FPS.

**El resultado continúa estilizado y no iguala la referencia hiperrealista.** La mejora comprobada es de contorno y continuidad de superficies, deformación y herramientas de inspección. Siguen pendientes materiales más ricos, rostros/cuerpos realmente diversos, expresiones, cabello de mayor fidelidad, contactos individuales de dedos, ropa física y animación más natural. No se presentan las pruebas de lógica como certificación de calidad artística.

## Reproducción

`python tools/audit_continuity_release.py` reconstruye geometría, HTML y GLB, verifica sus hashes idénticos, ejecuta lógica y geometría y coteja el hash de todas las pruebas y capturas actuales. `rebuild.json` conserva antes/después. Comandos de las suites en `README.md` y guía. Las dependencias de autoría/pruebas no son requisitos del HTML. No se distribuyen fuentes tipográficas.

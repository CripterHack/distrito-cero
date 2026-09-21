# #29 · Rechazo de penetración antes de corregir la pose

**Estado: control de rechazo implementado, rifle pendiente, PR #30 no integrable.** Continúa [plan-rifle-coordination](plan-rifle-coordination.md) y [SPEC-003](spec.md). El producto sigue en 0.20.1. Este documento no aprueba otro contrato de apoyo ni una nueva geometría del rifle.

## Hallazgo que cambia la siguiente decisión

El punto heredado del hombro no representa la superficie de la chaqueta. En el rifle neutral canónico el centro de culata está a 6.18 mm de esa referencia, pero un vértice real de chaqueta penetra 15.53 mm en el volumen de la pieza posterior. La desalineación ocular continúa en 238.6433 mm. No basta optimizar las dos distancias anteriores.

Se ensayó un apoyo sobre un triángulo pectoral real, con deslizamiento dentro de la cara posterior del objeto y rotaciones moderadas. La variante C bajó el error ocular a 1.8818 mm, pero una inspección de la superficie deformada encontró 31.2559 mm de penetración en cara/cuello y 16.3883 mm en chaqueta. Su prueba Node `complete native reload keeps the thumb tip trajectory continuous` también falló: salto de 0.04155005748616606 m en el primer paso de recarga. Ese nombre de test no convierte la prueba Node en una prueba HTTP.

**C se rechazó y se restauraron íntegramente las fuentes de producción.** No se publicó ese perfil ni el contrato experimental de triángulo único. Las recetas A/B anteriores siguen descartadas. No se realizó una búsqueda exhaustiva ni se demostró que una solución de pose con la geometría actual sea imposible.

## Control implementado

`tools/qa/stock_clearance.js` es una lectura QA de rifle, no otro solver ni una nueva matriz de escenarios. Verifica los doce triángulos completos de cada uno de los dos volúmenes gráficos de la culata contra `EquipmentGeometry.build`. No confía en `mount.brace` ni sólo en que existan sus esquinas.

El conjunto fijo contiene 4,863 vértices únicos de cara/cuello y 2,993 de chaqueta superior. Se selecciona en bind, con `y >= 1.30` sólo para chaqueta. Los vértices coincidentes con influencias de piel diferentes se conservan. Se aplican forma, ajuste cervical, DQ, escala, raíz y yaw sobre la paleta suministrada. No se recalcula otra pose como sustituto de evidencia ausente. El marco del objeto debe ser rígido y finito.

El informe conserva el peor vértice de cada superficie, su índice y posiciones bind/mundo/objeto. Distancia negativa significa interior del volumen gráfico. El control rechaza penetraciones mayores de 2 mm. **Superarlo no acredita contacto, anatomía ni colisión completa.** No es una prueba de todos los triángulos, mangas inferiores o todas las piezas del arsenal.

`longarm_stage.js` incorpora esta lectura a las doce imágenes de rifle que ya existían. El productor gráfico valida la integridad del nuevo campo, no exige que un defecto conocido desaparezca. La galería muestra la penetración antes de los parámetros plegados. La aceptación pendiente en `rifle-coordination.test.cjs` conserva todos sus umbrales originales y añade ausencia de penetración. El primer requisito ocular sigue fallando, sin skip o exclusión de CI.

## Evidencia de esta continuación

| Comprobación local | Resultado |
| --- | --- |
| Nuevo helper Node | 10/10, con controles negativos observados |
| Node completo | 495 tests, 494 aprobados, uno fallido por el requisito ocular original |
| Python vigente | 83 aprobados, incluidos dos nuevos tests de galería |
| Autoría, build inmutable y exportación | Aprobados, HTML/GLB/recurso humano conservan sus hashes |
| Suite longarms | 24/24 de integridad, 48 PNG con hashes cotejados, cero errores/peticiones |

Run local `20260921T175615Z-a8b5616788c5`, Chromium 144, Xvfb y SwiftShader, 208.945 s. Su commit es `null`: la copia procede del artefacto Pages canónico, no de un checkout Git. No se fabrica historia para rellenarlo. La galería con el resumen nuevo se generó también a partir del mismo JSON conservado, sin alterar mediciones o capturas.

Se reprodujo además C en una página aislada: original y variante desde dos cámaras, cuatro PNG con hashes y los mismos parámetros. **Es una reproducción con módulos reemplazados en memoria, no QA canónica ni código aceptado.** La revisión visual confirmó el rechazo. Las fuentes y el replay rechazados se conservan en el paquete de investigación de la conversación, no en el runtime.

El primer intento del runner usó un destino fuera de `artifacts/` y fue rechazado por configuración antes de ejecutar la suite. Se corrigió únicamente la ruta. Un probe gráfico temprano perdió el contexto; su repetición serial quedó registrada por separado. El primer test de traslado de la cabeza miraba un mínimo ubicado en el cuello y tenía una expectativa incorrecta. Se corrigió el fixture para trasladar la paleta suministrada, sin cambiar producto o tolerancias. Estos fallos no se presentan como aprobaciones.

La CI anterior `35626695314`, HEAD `f2dc994`, terminó fallida por el test ocular. Sus jobs WebGL y HTTP terminaron success. La revisión nueva requiere su propia CI y no hereda esos resultados. Consultar el PR #30 para HEAD, árbol, run y revisión actuales.

## Invariantes y siguiente acción

HTML SHA-256 `4a78bcca34cd40b2c406b0642362f30a6b71303d8a4a6ace659e0ba4afc9918d`, 8,862,957 bytes. No cambian `src/`, modelos, miras, longitudes, guardados, munición, versión, licencia, permisos o workflows. No hay merge ni despliegue nuevo en esta unidad. El coste nuevo pertenece a QA, no al fotograma del juego.

Antes de otro ajuste ciego de cabeza/hombros, resolver conjuntamente el espacio libre entre cara, culata y chaqueta. La siguiente decisión propuesta es permitir una revisión cosmética acotada del rifle, con referencias verificadas contra la nueva geometría, preservando la anatomía y las reglas. Esa geometría **no está implementada ni aprobada aquí**. La alternativa es demostrar una pose natural que satisfaga las superficies actuales. En ambos casos conservar comparaciones y los criterios de ojo, palmas, longitudes, recarga y continuidad. No sustituir el fallo por una tolerancia mayor.

#29 y #6 permanecen abiertas. #5 mantiene revisión artística y #7 sus gates de recorrido/playtest/hardware. Reversión de esta unidad: retirar sólo el helper, sus pruebas, integración QA y documentación. No requiere migración de partidas.
